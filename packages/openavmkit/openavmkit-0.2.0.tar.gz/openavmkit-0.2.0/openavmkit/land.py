import os
import pickle
import warnings
import numpy as np
import pandas as pd
import geopandas as gpd
from geopandas import GeoDataFrame
from pygam import LinearGAM, s, te
from scipy.optimize import curve_fit
from pygam.callbacks import CallBack

from IPython.display import display
from openavmkit.data import (
    _get_sales,
    get_hydrated_sales_from_sup,
    SalesUniversePair,
    get_train_test_keys,
    get_sale_field,
)
from openavmkit.modeling import SingleModelResults, plot_value_surface, simple_ols
from openavmkit.quality_control import check_land_values
from openavmkit.utilities.data import (
    div_series_z_safe,
    add_sqft_fields,
)
from openavmkit.utilities.plotting import plot_histogram_df
from openavmkit.utilities.settings import get_model_group_ids

from openavmkit.utilities.stats import calc_correlations, calc_cod, calc_r2, calc_mse_r2_adj_r2


def run_land_analysis(sup: SalesUniversePair, settings: dict, verbose: bool = False):
    df_sales = get_hydrated_sales_from_sup(sup)
    model_group_ids = get_model_group_ids(settings)
    for model_group in model_group_ids:
        _run_land_analysis(df_sales, sup.universe, settings, model_group, verbose)


def convolve_land_analysis(
    sup: SalesUniversePair, settings: dict, verbose: bool = False
):
    df_sales = get_hydrated_sales_from_sup(sup)
    model_group_ids = get_model_group_ids(settings)
    for model_group in model_group_ids:
        _convolve_land_analysis(df_sales, sup.universe, settings, model_group, verbose)


def finalize_land_values(
    df_in: pd.DataFrame,
    settings: dict,
    verbose: bool = False,
) -> pd.DataFrame:
    model_group_ids = get_model_group_ids(settings)
    df_all_values: pd.DataFrame | None = None
    for model_group in model_group_ids:
        df_values = df_in[df_in["model_group"].eq(model_group)].copy()
        outpath = f"out/models/{model_group}/_cache/land_analysis.pickle"
        if os.path.exists(outpath):
            df_finalize = pd.read_pickle(outpath)
            df_finalize = _finalize_land_values(
                df_in, df_finalize, model_group, settings, verbose
            )
            df_values = df_values.merge(
                df_finalize[
                    [
                        "key",
                        "model_market_value",
                        "model_impr_value",
                        "model_land_value",
                    ]
                ],
                on="key",
                how="left",
            )
            df_values = add_sqft_fields(df_values)
            if df_all_values is None:
                df_all_values = df_values
            else:
                df_all_values = pd.concat([df_all_values, df_values], ignore_index=True)
    df_all_values.reset_index(inplace=True, drop=True)
    new_fields = [field for field in df_all_values.columns.values if field != "key"]
    df_return = df_in.copy()
    df_return = df_return[[col for col in df_return if col not in new_fields]]
    df_return = df_return.merge(df_all_values, on="key", how="left")

    os.makedirs(f"out/models/", exist_ok=True)
    gdf = gpd.GeoDataFrame(df_return, geometry="geometry")
    gdf.to_parquet(f"out/models/predictions.parquet")

    return gdf


def _finalize_land_values(
    df_orig: pd.DataFrame,
    df_in: pd.DataFrame,
    model_group: str,
    settings: dict,
    verbose: bool = False,
):
    df = df_in.copy()

    # Derive the final land values
    df["model_land_value"] = df["model_market_value"] * df["model_land_alloc"]
    df["model_impr_value"] = df["model_market_value"] - df["model_land_value"]

    # Apply basic sanity check / error correction to land values
    df = check_land_values(df, model_group)

    df["model_land_value_land_sqft"] = div_series_z_safe(
        df["model_land_value"], df["land_area_sqft"]
    )
    df["model_market_value_land_sqft"] = div_series_z_safe(
        df["model_market_value"], df["land_area_sqft"]
    )
    df["model_market_value_impr_sqft"] = div_series_z_safe(
        df["model_market_value"], df["bldg_area_finished_sqft"]
    )

    # Find variables correlated with land value

    df_subset = df_orig[df_orig["model_group"].eq(model_group)]
    df_sales = _get_sales(df_subset, settings)
    df_sales = df_sales.merge(
        df[
            [
                "key_sale",
                "key",
                "model_market_value",
                "model_land_value",
                "model_land_value_land_sqft",
            ]
        ],
        on="key",
        how="left",
    )
    df_sales["model_market_value_impr_sqft"] = div_series_z_safe(
        df_sales["model_market_value"], df_sales["bldg_area_finished_sqft"]
    )
    df_sales["model_market_value_land_sqft"] = div_series_z_safe(
        df_sales["model_market_value"], df_sales["land_area_sqft"]
    )

    ind_vars = (
        settings.get("modeling", {})
        .get("models", {})
        .get("main", {})
        .get("default", {})
        .get("ind_vars", [])
    )
    ind_vars = ind_vars + [
        "assr_market_value",
        "assr_land_value",
        "model_market_value",
        "model_market_value_land_sqft",
        "model_market_value_impr_sqft",
    ]

    print("LAND VALUE")
    X_corr = df_sales[["model_land_value"] + ind_vars]
    corrs = calc_correlations(X_corr)
    print("INITIAL")
    display(corrs["initial"])
    print("")
    print("FINAL)")
    display(corrs["final"])
    print("")
    print("LAND VALUE PER SQFT")
    X_corr = df_sales[["model_land_value_land_sqft"] + ind_vars]
    corrs = calc_correlations(X_corr)
    print("INITIAL")
    display(corrs["initial"])
    print("")
    print("FINAL)")
    display(corrs["final"])

    # Super tiny slivers of land will have insane $/sqft values
    df["model_market_value_land_sqft"] = div_series_z_safe(
        df["model_market_value"], df["land_area_sqft"]
    )
    df["model_market_value_impr_sqft"] = div_series_z_safe(
        df["model_market_value"], df["bldg_area_finished_sqft"]
    )
    df_not_tiny = df[df["land_area_sqft"].gt(5000)]

    plot_value_surface(
        "Land value per sqft",
        df_not_tiny["model_land_value_land_sqft"],
        gdf=df,
        cmap="viridis",
        norm="log",
    )

    plot_value_surface(
        "Market value per land sqft",
        df_not_tiny["model_market_value_land_sqft"],
        gdf=df,
        cmap="viridis",
        norm="log",
    )

    outpath = f"out/models/{model_group}/_images/"
    os.makedirs(outpath, exist_ok=True)

    return df


def _run_land_analysis(
    df_sales: pd.DataFrame,
    df_universe: pd.DataFrame,
    settings: dict,
    model_group: str,
    verbose: bool = False,
):
    instructions = settings.get("modeling", {}).get("instructions", {})
    allocation = instructions.get("allocation", {})

    sale_field = get_sale_field(settings, df_sales)

    results_map = {"main": {}, "hedonic": {}, "vacant": {}}
    sales_map = {"main": {}, "hedonic": {}, "vacant": {}}

    land_fields = []
    land_results: dict[str:SingleModelResults] = {}
    land_sales: dict[str:SingleModelResults] = {}

    # STEP 1: Gather results from the main, hedonic, and vacant models
    for key in ["main", "hedonic", "vacant"]:
        short_key = key[0]
        if key == "main":
            models = instructions.get("main", {}).get("run", [])
            skip = instructions.get("main", {}).get("skip", [])
            if model_group in skip:
                if "all" in skip[model_group]:
                    print(f"Skipping model group: {model_group}")
                    return
            if "ensemble" not in models:
                models.append("ensemble")
        else:
            models = allocation.get(key, [])
        
        path = key
        if key == "hedonic":
            path = "hedonic_land"

        outpath = f"out/models/{model_group}/{key}"

        if verbose:
            print(f"key = {key}")
        if len(models) > 0:
            for model in models:
                if verbose:
                    print(f"----> model = {model}")

                filepath = f"{outpath}/{model}"
                if os.path.exists(filepath):
                    fpred_univ = f"{filepath}/pred_universe.parquet"
                    fpred_sales = f"{filepath}/pred_sales.parquet"
                    if not os.path.exists(fpred_univ):
                        fpred_univ = f"{filepath}/pred_{model}_universe.parquet"
                        fpred_sales = f"{filepath}/pred_{model}_sales.parquet"
                    if os.path.exists(fpred_univ):
                        df_u = pd.read_parquet(fpred_univ)[["key", "prediction"]]
                        results_map[key][model] = df_u
                        df_s = pd.read_parquet(fpred_sales)
                        if "key_x" in df_s:
                            df_s = df_s.rename(columns={"key_x":"key"})
                        df_s = df_s[["key", "key_sale", "prediction"]]
                        sales_map[key][model] = df_s
                        print(f"--------> stashing {model}")

                fpred_results = f"{filepath}/pred_universe.pkl"
                fpred_sales = f"{filepath}/pred_sales.pkl"
                if os.path.exists(fpred_results):
                    if key != "main":
                        with open(fpred_results, "rb") as file:
                            results = pickle.load(file)
                            land_results[f"{short_key}_{model}"] = results
                            land_fields.append(f"{short_key}_{model}")
                        with open(fpred_sales, "rb") as file:
                            results = pickle.load(file)
                            land_sales[f"{short_key}_{model}"] = results

    df_all_alloc = results_map["main"]["ensemble"].copy()
    df_all_alloc_sales = sales_map["main"]["ensemble"].copy()
    df_all_land_values = df_all_alloc.copy()
    df_all_land_values = df_all_land_values[["key"]].merge(
        df_universe, on="key", how="left"
    )
    df_all_land_sales = df_all_alloc_sales.copy()
    print(df_all_land_sales.columns)
    df_all_land_sales = df_all_land_sales[["key_sale"]].merge(
        df_sales, on="key_sale", how="left"
    )

    all_alloc_names = []

    bins = 400

    # STEP 2: Calculate land allocations for each model

    data_compare = {
        "type": [],
        "model": [],
        "count": [],
        "r2": [],
        "alloc_median": [],
    }

    for key in ["hedonic", "vacant"]:
        short_key = key[0]
        df_alloc = results_map["main"]["ensemble"].copy()
        alloc_names = []
        entries = results_map[key]

        for model in entries:

            pred_main = results_map["main"].get(model)
            pred_sales = sales_map["main"].get(model)

            if pred_main is None:
                warnings.warn(
                    f"No main model found for model: {model}, using ensemble instead"
                )
                pred_main = results_map["main"].get("ensemble")
                pred_sales = sales_map["main"].get("ensemble")

            pred_land = (
                results_map[key]
                .get(model)
                .rename(columns={"prediction": "prediction_land"})
            )
            pred_sales = (
                sales_map[key]
                .get(model)
                .rename(columns={"prediction": "prediction_land"})
            )
            df = pred_main.merge(pred_land, on="key", how="left")
            dfs = pred_sales.merge(pred_sales, on="key_sale", how="left")
            alloc_name = f"{short_key}_{model}"
            df.loc[:, alloc_name] = df["prediction_land"] / df["prediction"]
            dfs.loc[:, alloc_name] = dfs["prediction_land"] / df["prediction"]

            df_alloc = df_alloc.merge(df[["key", alloc_name]], on="key", how="left")
            df_all_alloc = df_all_alloc.merge(
                df[["key", alloc_name]], on="key", how="left"
            )
            df_all_alloc_sales = df_all_alloc_sales.merge(
                df[["key_sale", alloc_name]], on="key_sale", how="left"
            )

            df2 = df.copy().rename(columns={"prediction_land": alloc_name})
            df2s = dfs.copy().rename(columns={"prediction_land": alloc_name})

            df_all_land_values = df_all_land_values.merge(
                df2[["key", alloc_name]], on="key", how="left"
            )
            df_all_land_sales = df_all_land_sales.merge(
                df2s[["key_sale", alloc_name]], on="key_sale", how="left"
            )

            alloc_names.append(alloc_name)
            all_alloc_names.append(alloc_name)

            total_count = len(df)
            data_compare["type"].append(key)
            data_compare["model"].append(model)
            data_compare["count"].append(total_count)

            mse, r2, _ = calc_mse_r2_adj_r2(df2s[alloc_name], df2s[sale_field], 1)

            # data_compare["pct_neg"].append(
            #     np.round(100 * len(df[df["prediction_land"].lt(0)]) / total_count) / 100
            # )
            # data_compare["pct_over"].append(
            #     np.round(100 * len(df[df[alloc_name].gt(1)]) / total_count) / 100
            # )

            data_compare["r2"].append(r2)
            data_compare["mse"].append(mse)
            data_compare["alloc_median"].append(
                np.round(100 * df[alloc_name].median()) / 100
            )

        df_compare = pd.DataFrame(data_compare)

        print("MODEL COMPARISON")
        display(df_compare)
        print("")

        df_alloc["allocation_ensemble"] = df_alloc[alloc_names].median(axis=1)

        plot_histogram_df(
            df=df_alloc,
            fields=alloc_names,
            xlabel="% of value attributable to land",
            ylabel="Number of parcels",
            title=f"({model_group}) Land allocation -- {key}",
            bins=bins,
            x_lim=(0.0, 1.0),
        )
        plot_histogram_df(
            df=df_alloc,
            fields=["allocation_ensemble"],
            xlabel="% of value attributable to land",
            ylabel="Number of parcels",
            title=f"({model_group}) Land allocation -- {key}, ensemble",
            bins=bins,
            x_lim=(0.0, 1.0),
        )

    plot_histogram_df(
        df=df_all_alloc,
        fields=all_alloc_names,
        xlabel="% of value attributable to land",
        ylabel="Number of parcels",
        title=f"({model_group}) Land allocation -- all",
        bins=bins,
        x_lim=(0.0, 1.0),
    )

    df_all_alloc["allocation_ensemble"] = df_all_alloc[all_alloc_names].median(axis=1)
    plot_histogram_df(
        df=df_all_alloc,
        fields=["allocation_ensemble"],
        xlabel="% of value attributable to land",
        ylabel="Number of parcels",
        title=f"({model_group}) Land allocation -- all, ensemble",
        bins=bins,
        x_lim=(0.0, 1.0),
    )

    # STEP 3: Optimize the ensemble allocation

    print(f"Putting it all together...")

    curr_ensemble = all_alloc_names
    best_score = float("inf")

    scores = {}

    for alloc_name in all_alloc_names:
        alloc = df_all_alloc[alloc_name]
        pct_neg = (alloc.lt(0)).sum() / len(alloc)
        pct_over = (alloc.gt(1)).sum() / len(alloc)
        score = pct_neg + (pct_over * 2.0)
        scores[alloc_name] = score

    print(f"Scores =\n{scores}")

    best_ensemble = None

    # Don't ensemble on assessor models:
    curr_ensemble = [col for col in curr_ensemble if "assessor" not in col]

    while len(curr_ensemble) > 0:
        alloc_ensemble = df_all_alloc[curr_ensemble].median(axis=1)
        pct_neg = (alloc_ensemble.lt(0)).sum() / len(alloc_ensemble)
        pct_over = (alloc_ensemble.gt(1)).sum() / len(alloc_ensemble)

        score = pct_neg + pct_over

        if score < best_score:
            best_score = score
            best_ensemble = curr_ensemble.copy()

        worst_score = -float("inf")
        worst_alloc = None
        for alloc_name in curr_ensemble:
            alloc_score = scores[alloc_name]
            if alloc_score > worst_score:
                worst_score = alloc_score
                worst_alloc = alloc_name

        if worst_alloc is not None:
            curr_ensemble.remove(worst_alloc)

        print(
            f"Ensemble score: {score:4.6f} (n:{pct_neg:4.2%} o:{pct_over:4.2%}), worst_score: {worst_score:4.2f}, eliminated: {worst_alloc}, best: {best_ensemble}"
        )

    if best_ensemble is None:
        print("No valid ensemble found, bailing...")
        return

    print(f"BEST ENSEMBLE = {best_ensemble}")
    print("LAND ENSEMBLE SCORE:")
    alloc_ensemble = df_all_alloc[best_ensemble].median(axis=1)
    pct_neg = (alloc_ensemble.lt(0)).sum() / len(alloc_ensemble)
    pct_over = (alloc_ensemble.gt(1)).sum() / len(alloc_ensemble)
    print(f"--> % neg : {pct_neg:4.2%}")
    print(f"--> % over: {pct_over:4.2%}")
    print(f"--> median: {alloc_ensemble.median():4.2%}")

    drop_alloc_names = [name for name in all_alloc_names if name not in best_ensemble]
    df_all_alloc = df_all_alloc.drop(columns=drop_alloc_names)

    plot_histogram_df(
        df=df_all_alloc,
        fields=best_ensemble,
        xlabel="% of value attributable to land",
        ylabel="Number of parcels",
        title=f"({model_group} Land allocation -- best ensemble (components)",
        bins=bins,
        x_lim=(0.0, 1.0),
    )

    df_all_alloc["allocation_ensemble"] = df_all_alloc[best_ensemble].median(axis=1)
    plot_histogram_df(
        df=df_all_alloc,
        fields=["allocation_ensemble"],
        xlabel="% of value attributable to land",
        ylabel="Number of parcels",
        title=f"{model_group} Land allocation -- best ensemble",
        bins=bins,
        x_lim=(0.0, 1.0),
    )

    # STEP 4: Finalize the results
    df_finalize = df_all_alloc.drop(columns=best_ensemble)
    df_finalize = df_finalize.rename(
        columns={
            "allocation_ensemble": "model_land_alloc",
            "prediction": "model_market_value",
        }
    )
    df_finalize = df_finalize.merge(
        df_universe[
            [
                "key",
                "geometry",
                "latitude",
                "longitude",
                "land_area_sqft",
                "bldg_area_finished_sqft",
            ]
        ],
        on="key",
        how="left",
    )

    df_finalize["model_land_value"] = (
        df_finalize["model_market_value"] * df_finalize["model_land_alloc"]
    )

    df_finalize = add_sqft_fields(df_finalize)

    outpath = f"out/models/{model_group}/land_analysis.csv"
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    df_finalize.to_csv(outpath)

    gdf = GeoDataFrame(df_finalize, geometry="geometry", crs=df_universe.crs)
    gdf.to_parquet(f"out/models/{model_group}/land_analysis.parquet")


def _convolve_land_analysis(
    df_sales: pd.DataFrame,
    df_universe: pd.DataFrame,
    settings: dict,
    model_group: str,
    verbose: bool = False,
):
    instructions = settings.get("modeling", {}).get("instructions", {})
    allocation = instructions.get("allocation", {})

    results_map = {"main": {}, "hedonic": {}, "vacant": {}}

    land_fields = []
    land_results: dict[str:SingleModelResults] = {}

    train_keys, test_keys = get_train_test_keys(df_sales, settings)

    vacant_sales = (
        df_sales[df_sales["valid_for_land_ratio_study"].eq(True)]["key_sale"]
        .unique()
        .tolist()
    )
    df_vacant_sale = df_sales[
        df_sales["key_sale"].isin(vacant_sales)
        & df_sales["model_group"].eq(model_group)
    ].copy()

    # STEP 1: Gather results from the main, hedonic, and vacant models
    for key in ["main", "hedonic", "vacant"]:
        short_key = key[0]
        if key == "main":
            models = instructions.get("main", {}).get("run", [])
            skip = instructions.get("main", {}).get("skip", [])
            if model_group in skip:
                if "all" in skip[model_group]:
                    print(f"Skipping model group: {model_group}")
                    return
            if "ensemble" not in models:
                models.append("ensemble")
        else:
            models = allocation.get(key, [])
        outpath = f"out/models/{model_group}/{key}"

        if verbose:
            print(f"key = {key}")
        if len(models) > 0:
            for model in models:

                filepath = f"{outpath}/{model}"
                if os.path.exists(filepath):
                    fpred_univ = f"{filepath}/pred_universe.parquet"
                    if not os.path.exists(fpred_univ):
                        fpred_univ = f"{filepath}/pred_{model}_universe.parquet"

                    if os.path.exists(fpred_univ):
                        df_univ = pd.read_parquet(fpred_univ)[["key", "prediction"]]
                        results_map[key][model] = df_univ

                fpred_results = f"{filepath}/pred_universe.pkl"
                if os.path.exists(fpred_results):
                    if key != "main":
                        with open(fpred_results, "rb") as file:
                            results = pickle.load(file)
                            land_results[f"{short_key}_{model}"] = results
                            land_fields.append(f"{short_key}_{model}")

    sale_field = get_sale_field(settings)

    data_results = {
        "model": [],
        "r2_ols": [],
        "r2_y=x": [],
        "slope": [],
        "med_ratio": [],
        "cod": [],
    }

    data_results_test = {
        "model": [],
        "r2_ols": [],
        "r2_y=x": [],
        "slope": [],
        "med_ratio": [],
        "cod": [],
    }

    # STEP 2: Calculate smoothed values for each surface
    for full_or_test in ["full", "test"]:
        for key in ["hedonic", "vacant"]:
            entries = results_map[key]
            for model in entries:

                dfv = df_vacant_sale.copy()

                pred_main = None

                if pred_main is None:
                    pred_main = results_map["main"].get("ensemble")

                pred_land = (
                    results_map[key]
                    .get(model)
                    .rename(columns={"prediction": "prediction_land"})
                )
                df = pred_main.merge(pred_land, on="key", how="left")
                df = df.merge(
                    df_universe[
                        ["key", "latitude", "longitude", "land_area_sqft"]
                    ],
                    on="key",
                    how="left",
                )

                # Clamp land predictions to be non-negative and not exceed the main prediction
                df.loc[df["prediction_land"].lt(0), "prediction_land"] = 0.0
                df["prediction_land"] = df["prediction_land"].astype("Float64")
                df.loc[
                    df["prediction_land"].gt(df["prediction"]),
                    "prediction_land",
                ] = df["prediction"].astype("Float64")

                # Calculate land area per square foot of land
                df["prediction_land_sqft"] = div_series_z_safe(
                    df["prediction_land"], df["land_area_sqft"]
                )

                # Calculate the sale price per square foot of land
                sale_field_land_sqft = f"{sale_field}_land_sqft"
                dfv[sale_field_land_sqft] = div_series_z_safe(
                    dfv[sale_field], dfv["land_area_sqft"]
                )

                df["prediction_land_smooth"] = df["prediction_land"]

                df["prediction_land_smooth_sqft"] = div_series_z_safe(
                    df["prediction_land_smooth"], df["land_area_sqft"]
                )

                dfv = dfv.merge(
                    df[
                        [
                            "key",
                            "prediction_land_smooth",
                            "prediction_land_smooth_sqft",
                        ]
                    ],
                    on="key",
                    how="left",
                )
                dfv = dfv[
                    ~dfv["prediction_land_smooth"].isna()
                    & ~dfv["prediction_land_smooth_sqft"].isna()
                    & ~dfv[sale_field_land_sqft].isna()
                ]

                if full_or_test == "test":
                    dfv = dfv[dfv["key_sale"].isin(test_keys)]
                if len(dfv) == 0:
                    continue

                dfv["sales_ratio"] = div_series_z_safe(
                    dfv["prediction_land_smooth"], dfv[sale_field]
                )

                median_ratio = dfv["sales_ratio"].median()
                cod = calc_cod(dfv["sales_ratio"].values)

                results = simple_ols(
                    dfv, "prediction_land_smooth", "sale_price", intercept=True
                )

                slope = results["slope"]
                r2 = results["r2"]

                y_true = dfv["sale_price"].values
                y_pred = dfv["prediction_land_smooth"].values

                ss_res = np.sum((y_true - y_pred) ** 2)
                ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
                r2_yx = 1 - (ss_res / ss_tot)

                if full_or_test == "full":
                    data_results["model"].append(
                        f"{key}_{model}"
                    )
                    data_results["slope"].append(f"{slope:.2f}")
                    data_results["r2_ols"].append(f"{r2:.2f}")
                    data_results["r2_y=x"].append(f"{r2_yx:.2f}")
                    data_results["med_ratio"].append(f"{median_ratio:.2f}")
                    data_results["cod"].append(f"{cod:.1f}")
                else:
                    data_results_test["model"].append(
                        f"{key}_{model}"
                    )
                    data_results_test["slope"].append(f"{slope:.2f}")
                    data_results_test["r2_ols"].append(f"{r2:.2f}")
                    data_results_test["r2_y=x"].append(f"{r2_yx:.2f}")
                    data_results_test["med_ratio"].append(f"{median_ratio:.2f}")
                    data_results_test["cod"].append(f"{cod:.1f}")

    df_results = pd.DataFrame(data_results)

    df_results["r2_"] = np.floor(df_results["r2_y=x"].astype("float").fillna(0.0) * 10)
    df_results["slope_"] = np.abs(1.0 - df_results["slope"].astype("float").fillna(0.0))

    df_results = df_results.sort_values(by=["r2_", "slope_"], ascending=False)
    df_results = df_results.drop(columns=["r2_", "slope_"])
    df_results = df_results.reset_index(drop=True)

    count = len(df_vacant_sale)
    print("=" * 80)
    print(f"FULL LAND RESULTS, MODEL GROUP : {model_group}, count: {count}")
    print("=" * 80)
    print(df_results.to_string())
    print("")

    df_results_test = pd.DataFrame(data_results_test)
    if len(df_results_test) > 0:
        df_results_test["r2_"] = np.floor(
            df_results_test["r2_y=x"].astype("float").fillna(0.0) * 10
        )
        df_results_test["slope_"] = np.abs(
            1.0 - df_results_test["slope"].astype("float").fillna(0.0)
        )
        df_results_test = df_results_test.sort_values(
            by=["r2_", "slope_"], ascending=False
        )
        df_results_test = df_results_test.drop(columns=["r2_", "slope_"])
        df_results_test = df_results_test.reset_index(drop=True)
        # df_results_test = df_results_test[df_results_test["model"].astype(str).str.contains("assessor") | (df_results_test.index < 10)]

        count = len(df_vacant_sale[df_vacant_sale["key_sale"].isin(test_keys)])
        print("=" * 80)
        print(f"TEST LAND RESULTS, MODEL GROUP : {model_group}, count: {count}")
        print("=" * 80)
        print(df_results_test.to_string())
        print("")



class LandSLICEModel:

    """
    SLICE stands for "Smooth Location w/ Increasing-Concavity Equation."
    """

    def __init__(
        self,
        alpha: float,
        beta: float,
        gam_L: LinearGAM,
        med_size: float,
        size_field: str
    ):
        self.alpha = alpha
        self.beta = beta
        self.gam_L = gam_L
        self.med_size = med_size
        self.size_field = size_field


    def predict_size_factor(size_value: float):
        return self.alpha * (size_value / self.med_size)**self.beta

    def predict(
        self,
        df: pd.DataFrame,
        location_factor: str = "location_factor",
        size_factor: str = "size_factor",
        prediction: str = "land_value"
    ):
        for field in ["latitude", "longitude", self.size_field]:
            if field not in df:
                raise ValueError(f"Required field {field} is missing from dataframe!")

        # Get location factor from Lat & Lon
        df[location_factor] = np.exp(
            self.gam_L.predict(df[["latitude", "longitude"]])
        )

        # Get size factor from power curve
        df[size_factor] = self.alpha * (np.asarray(df[self.size_field]) / self.med_size)**self.beta

        # Prediction is simply location premium times size factor
        df[prediction] = df[location_factor] * df[size_factor]
        return df


def fit_land_SLICE_model(
    df_in : pd.DataFrame,
    size_field: str = "land_area_sqft",
    value_field: str = "land_value",
    verbose: bool = False
)->LandSLICEModel:
    """
    Fits land values using SLICE: "Smooth Location with Increasing-Concavity Equation"
    
    This model takes already-existing raw per-parcel land values and separates the contribution of land size and locational premium.
    It also enforces three constraints: 
    1. Locational premium must change smoothly over space
    2. Land value in any fixed location must increase monotonically with land size
    3. The marginal value of each additional unit of land size must decrease monotonically
    
    The output is an object that encodes the final fitted land values, the locational premiums, and the local land factors. Fitted land
    values are derived by simply multiplying locational premium times local land factor.
    
    Parameters
    ----------
    df_in : pd.DataFrame
        Input data
    size_field : str
        The name of your land size field
    value_field : str
        The name of your land value field
    verbose : bool
        Whether to print verbose output
    """
    
    
    class Progress(CallBack):
        def on_loop_end(self, diff):
            # self.iter is automatically tracked inside Callback
            print(f"iter {self.iter:>3d}   dev.change={diff:9.3e}")
    
    if verbose:
        print("Fitting land SLICE model...")


    df = df_in[[value_field, size_field, "latitude", "longitude"]].copy()
    med_land_size = float(np.median(df[size_field]))

    # Y = Size-detrended location factor
    df["Y"] = div_series_z_safe(
        df[value_field],
        np.sqrt(
            df[size_field] / med_land_size
        )
    )

    if verbose:
        print("-->fitting thin-plate spline for location factor...")
        
    # Fit a thin-plate spline for location factor L(lat, lon)
    basis = te(0, 1, n_splines=40, spline_order=3)
    gam_L : LinearGAM = LinearGAM(
        basis,
        max_iter=40,
        callbacks=[Progress()],
        verbose=verbose
    )
    gam_L.fit(
        df[['latitude', 'longitude']].values,
        np.log(df['Y']).values
    )

    if verbose:
        print("-->estimating initial location factor...")
    # L_hat = Initial estimated location factor (mostly depends on latitude/longitude)
    df['L_hat'] = np.exp(gam_L.predict(df[['latitude', 'longitude']].values))

    # Z = Location-detrended land values (mostly depends on size)
    df["Z"] = df[value_field] / df["L_hat"]

    # Define a power law curve function
    def power_curve(s, alpha, beta):
        return alpha * (s / med_land_size)**beta

    # Solve for location-detrended-land-value and observed size to fit the power law curve
    # - with bounds: alpha>0 (always positive), 0<beta<1 (monotonic-up & concave)
    # - this enforces that land increases in value with size, but with diminishing returns to marginal size
    if verbose:
        print("-->fitting power law curve for size factor...")
    popt, _ = curve_fit(
        f=power_curve,
        p0=[np.median(df["Z"]),0.5],
        xdata=df[size_field].values,
        ydata=df["Z"].values,
        bounds=([0, 1e-6], [np.inf, 0.999])
    )

    # Coefficients for the power law curve:
    alpha_hat, beta_hat = popt

    # Function to call the power law curve with memorized coefficients and a given size
    def F_hat(s):
        return power_curve(np.asarray(s), alpha_hat, beta_hat)

    if verbose:
        print("-->tightening up values with one more iteration...")

    # Tighten up our values with an extra iteration
    df["Y2"] = df[value_field] / F_hat(df[size_field])
    gam_L2 : LinearGAM = gam_L.fit(df[["latitude", "longitude"]], np.log(df["Y2"]))   # refit L

    if verbose:
        print("-->estimating final location factor...")

    # L_hat = Final estimated location factor
    df["L_hat"] = np.exp( gam_L2.predict(df[["latitude", "longitude"]]))

    # could refit L_hat once more here if desired
    return LandSLICEModel(
        alpha_hat,
        beta_hat,
        gam_L2,
        med_land_size,
        size_field
    )
