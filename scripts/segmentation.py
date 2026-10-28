from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from transform import FAULT_WINDOWS


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = PROJECT_ROOT / "data/processed/processed_inv_metrics.csv"
TABLES = PROJECT_ROOT / "output/tables"
FIGURES = PROJECT_ROOT / "output/figures"
FLAGGED_SOURCE = PROJECT_ROOT / "output/sql_results/03_flagged_3h_blocks.csv"
CHUNK_SIZE = 100_000  # inverter-hour rows per read
FIGURE_DPI = 140  # dots per inch
FAULT_IDS = {fault["inverter_id"] for fault in FAULT_WINDOWS}
FAULT_WINDOW_BY_INVERTER = {
    fault["inverter_id"]: (fault["start"], fault["end"])
    for fault in FAULT_WINDOWS
}
FAULT_START = min(fault["start"] for fault in FAULT_WINDOWS)
FAULT_END = max(fault["end"] for fault in FAULT_WINDOWS)
SEVERITY_ORDER = ["Watch", "Alert", "Critical"]


def create_season_hour_chart(segment_pr_by_season_hour):
    figure, axis = plt.subplots(figsize=(9, 5))
    for season in ["Dry", "Wet"]:
        rows = segment_pr_by_season_hour[
            segment_pr_by_season_hour["season"] == season
        ]
        axis.plot(
            rows["hour_band"],
            rows["mean_pr"],
            marker="o",
            label=season,
            color="#287b72" if season == "Dry" else "#bc7138",
        )
    axis.set(
        title="Mean Performance Ratio by Season and Hour Band",
        xlabel="Hour band (local time, h)",
        ylabel="Mean performance ratio (unitless)",
    )
    axis.legend(frameon=False)
    figure.tight_layout()
    figure.savefig(FIGURES / "mean_pr_by_season_hour_band.png", dpi=FIGURE_DPI)
    plt.close(figure)


def create_irradiance_chart(segment_pr_by_irradiance_band):
    figure, axis = plt.subplots(figsize=(8, 5))
    axis.bar(
        segment_pr_by_irradiance_band["irradiance_band"],
        segment_pr_by_irradiance_band["mean_pr"],
        color="#287b72",
    )
    axis.set(
        title="Mean Performance Ratio by Irradiance Band",
        xlabel="Plane-of-array irradiance band (W/m²)",
        ylabel="Mean performance ratio (unitless)",
    )
    figure.tight_layout()
    figure.savefig(FIGURES / "mean_pr_by_irradiance_band.png", dpi=FIGURE_DPI)
    plt.close(figure)


def create_severity_chart(cohort_flags_by_severity):
    figure, axis = plt.subplots(figsize=(9, 5))
    pivot = cohort_flags_by_severity.pivot(
        index="cohort", columns="severity", values="flagged_blocks"
    ).fillna(0)
    pivot = pivot.reindex(columns=SEVERITY_ORDER, fill_value=0)
    pivot.plot(kind="bar", ax=axis, color=["#bc7138", "#b44b40", "#7b3737"])
    axis.set(
        title="Qualifying Three-Hour Blocks by Severity and Fault Cohort",
        xlabel="Inverter cohort",
        ylabel="Flagged rolling three-hour blocks (blocks)",
    )
    axis.legend(title="Severity", frameon=False)
    axis.tick_params(axis="x", rotation=0)
    figure.tight_layout()
    figure.savefig(FIGURES / "flagged_blocks_by_severity_cohort.png", dpi=FIGURE_DPI)
    plt.close(figure)


def main():
    plt.style.use("seaborn-v0_8-whitegrid")
    assert INPUT_CSV.exists(), f"Processed metrics file is missing: {INPUT_CSV}"
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)

    segment_parts = []
    irradiance_parts = []
    fault_window_parts = []
    overall_cohort_parts = []
    rows_read = 0

    for chunk in pd.read_csv(
        INPUT_CSV,
        usecols=["INVERTER_ID", "DATE_TIME", "IRRADIANCE", "PERFORMANCE_RATIO"],
        parse_dates=["DATE_TIME"],
        chunksize=CHUNK_SIZE,
    ):
        rows_read += len(chunk)
        chunk["month"] = chunk["DATE_TIME"].dt.month
        chunk["hour"] = chunk["DATE_TIME"].dt.hour
        chunk["season"] = chunk["month"].isin([12, 1, 2, 3, 4, 5]).map(
            {True: "Dry", False: "Wet"}
        )
        chunk["hour_band"] = pd.cut(
            chunk["hour"],
            bins=[5, 9, 14, 18],
            labels=["Morning 06-09", "Midday 10-14", "Afternoon 15-18"],
        )
        chunk["irradiance_band"] = pd.cut(
            chunk["IRRADIANCE"],
            bins=[-0.001, 200, 600, float("inf")],
            labels=["0-200", "200-600", ">600"],
            include_lowest=True,
        )

        valid_pr = chunk[chunk["PERFORMANCE_RATIO"].notna()]
        valid_pr = valid_pr.copy()
        cohort_names = {inverter_id: f"Faulted {inverter_id}" for inverter_id in FAULT_IDS}
        valid_pr["cohort"] = valid_pr["INVERTER_ID"].map(cohort_names).fillna(
            "Non-faulted"
        )
        overall_cohort_parts.append(
            valid_pr.groupby("cohort")["PERFORMANCE_RATIO"]
            .agg(["sum", "count"])
            .reset_index()
        )
        season_groups = valid_pr.dropna(subset=["hour_band"]).groupby(
            ["season", "hour_band"], observed=True
        )["PERFORMANCE_RATIO"].agg(["sum", "count"]).reset_index()
        segment_parts.append(season_groups)
        irradiance_groups = valid_pr.groupby("irradiance_band", observed=True)[
            "PERFORMANCE_RATIO"
        ].agg(["sum", "count"]).reset_index()
        irradiance_parts.append(irradiance_groups)

        current_chunk = chunk[
            ["INVERTER_ID", "DATE_TIME", "IRRADIANCE", "PERFORMANCE_RATIO"]
        ].copy()
        fault_window = current_chunk[
            current_chunk["INVERTER_ID"].isin(FAULT_IDS)
            & current_chunk["DATE_TIME"].between(FAULT_START, FAULT_END)
        ].copy()
        for inverter_id, (fault_start, fault_end) in FAULT_WINDOW_BY_INVERTER.items():
            rows = fault_window[
                fault_window["INVERTER_ID"].eq(inverter_id)
                & fault_window["DATE_TIME"].between(fault_start, fault_end)
            ][["INVERTER_ID", "DATE_TIME", "PERFORMANCE_RATIO"]]
            if not rows.empty:
                fault_window_parts.append(rows)

        if len(segment_parts) % 10 == 0:
            print(f"Processed {rows_read:,} inverter-hour rows")

    season_summary = pd.concat(segment_parts, ignore_index=True).groupby(
        ["season", "hour_band"], observed=True
    )[["sum", "count"]].sum().reset_index()
    season_summary["mean_pr"] = season_summary["sum"] / season_summary["count"]
    season_summary["hour_band"] = season_summary["hour_band"].astype(str)
    season_summary["inverter_hour_rows"] = season_summary["count"]
    season_summary = season_summary[
        ["season", "hour_band", "inverter_hour_rows", "mean_pr"]
    ].sort_values(["season", "hour_band"])
    season_summary.to_csv(TABLES / "segment_pr_by_season_hour.csv", index=False)

    irradiance_summary = pd.concat(irradiance_parts, ignore_index=True).groupby(
        "irradiance_band", observed=True
    )[["sum", "count"]].sum().reset_index()
    irradiance_summary["mean_pr"] = (
        irradiance_summary["sum"] / irradiance_summary["count"]
    )
    irradiance_summary["irradiance_band"] = irradiance_summary[
        "irradiance_band"
    ].astype(str)
    irradiance_summary["inverter_hour_rows"] = irradiance_summary["count"]
    irradiance_summary = irradiance_summary[
        ["irradiance_band", "inverter_hour_rows", "mean_pr"]
    ]
    irradiance_summary.to_csv(
        TABLES / "segment_pr_by_irradiance_band.csv", index=False
    )

    fault_windows = pd.concat(fault_window_parts, ignore_index=True)
    fault_windows["DATE_TIME"] = pd.to_datetime(fault_windows["DATE_TIME"])
    fault_windows["cohort"] = fault_windows["INVERTER_ID"].map(
        lambda value: f"Faulted {value}"
    )
    normal_rows = pd.read_csv(
        INPUT_CSV,
        usecols=["INVERTER_ID", "DATE_TIME", "PERFORMANCE_RATIO"],
        parse_dates=["DATE_TIME"],
        chunksize=CHUNK_SIZE,
    )
    fault_time_index = set(fault_windows["DATE_TIME"])
    normal_parts = []
    for chunk in normal_rows:
        normal = chunk[
            ~chunk["INVERTER_ID"].isin(FAULT_IDS)
            & chunk["DATE_TIME"].isin(fault_time_index)
            & chunk["PERFORMANCE_RATIO"].notna()
        ]
        if not normal.empty:
            normal_parts.append(
                normal.groupby("DATE_TIME")["PERFORMANCE_RATIO"]
                .agg(["sum", "count"])
                .reset_index()
            )
    normal_by_time = pd.concat(normal_parts, ignore_index=True).groupby(
        "DATE_TIME"
    )[["sum", "count"]].sum()
    overall_cohort_summary = pd.concat(overall_cohort_parts, ignore_index=True).groupby(
        "cohort"
    )[["sum", "count"]].sum()
    cohort_parts = []
    overall_faulted = overall_cohort_summary.loc[
        [f"Faulted {inverter_id}" for inverter_id in sorted(FAULT_IDS)]
    ].sum()
    overall_cohorts = [
        ("All faulted inverters", overall_faulted),
        ("Non-faulted", overall_cohort_summary.loc["Non-faulted"]),
    ]
    for overall_label, rows in overall_cohorts:
        cohort_parts.append(
            {
                "fault_cohort": overall_label,
                "comparison_group": "All valid PR rows",
                "valid_pr_rows": int(rows["count"]),
                "mean_pr": rows["sum"] / rows["count"],
            }
        )
    for inverter_id in sorted(FAULT_IDS):
        rows = fault_windows[fault_windows["INVERTER_ID"] == inverter_id]
        fault_mean = rows["PERFORMANCE_RATIO"].mean()
        fault_count = rows["PERFORMANCE_RATIO"].count()
        times = rows["DATE_TIME"]
        normal_sum = normal_by_time.loc[normal_by_time.index.isin(times), "sum"].sum()
        normal_count = normal_by_time.loc[normal_by_time.index.isin(times), "count"].sum()
        cohort_parts.extend(
            [
                {
                    "fault_cohort": f"Faulted {inverter_id}",
                    "comparison_group": "Fault window",
                    "valid_pr_rows": fault_count,
                    "mean_pr": fault_mean,
                },
                {
                    "fault_cohort": f"Faulted {inverter_id}",
                    "comparison_group": "Non-faulted peers, same hours",
                    "valid_pr_rows": normal_count,
                    "mean_pr": normal_sum / normal_count if normal_count else float("nan"),
                },
            ]
        )
    cohort_comparison = pd.DataFrame(cohort_parts)
    cohort_comparison.to_csv(TABLES / "cohort_fault_vs_normal.csv", index=False)

    flagged_blocks = pd.read_csv(FLAGGED_SOURCE)
    cohort_names = {inverter_id: f"Faulted {inverter_id}" for inverter_id in FAULT_IDS}
    flagged_blocks["cohort"] = flagged_blocks["inverter_id"].map(
        cohort_names
    ).fillna("Non-faulted")
    flag_summary = flagged_blocks.groupby(
        ["cohort", "severity_tier"]
    ).size().rename("flagged_blocks").reset_index().rename(
        columns={"severity_tier": "severity"}
    )
    all_cohorts = ["Non-faulted"] + [f"Faulted {value}" for value in sorted(FAULT_IDS)]
    complete_index = pd.MultiIndex.from_product(
        [all_cohorts, SEVERITY_ORDER], names=["cohort", "severity"]
    )
    flag_summary = (
        flag_summary.set_index(["cohort", "severity"])
        .reindex(complete_index, fill_value=0)
        .reset_index()
    )
    flag_summary.to_csv(TABLES / "cohort_flags_by_severity.csv", index=False)

    create_season_hour_chart(season_summary)
    create_irradiance_chart(irradiance_summary)
    create_severity_chart(flag_summary)
    print(f"Processed {rows_read:,} inverter-hour rows")
    print("Saved four segmentation tables and three charts")


if __name__ == "__main__":
    main()