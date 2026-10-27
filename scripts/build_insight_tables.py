from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
METRICS_FILE = PROJECT_ROOT / "data/processed/processed_inv_metrics.csv"
COMPUTATION_FILE = PROJECT_ROOT / "data/processed/open_meteo_computation.csv"
SQL_RESULTS_DIRECTORY = PROJECT_ROOT / "output/sql_results"
TABLE_DIRECTORY = PROJECT_ROOT / "output/tables"
CHUNK_SIZE = 100_000
SAMPLE_SIZE = 100_000
CANDIDATES_PER_CHUNK = 2_000
RANDOM_SEED = 42
MAX_OUTPUT_BYTES = 2 * 1024 * 1024
FAULT_DAYS = {
    101: "2025-03-15",
    202: "2025-06-20",
    303: "2025-09-10",
}
METRICS_COLUMNS = [
    "INVERTER_ID",
    "DATE_TIME",
    "AC_POWER",
    "IRRADIANCE",
    "PERFORMANCE_RATIO",
]
METRICS_STATS_COLUMNS = ["AC_POWER", "IRRADIANCE", "PERFORMANCE_RATIO"]
COMPUTATION_STATS_COLUMNS = [
    "dc_power_kw",
    "ac_power_kw",
    "irradiation_w_m2",
    "performance_ratio",
]


def summarize_dataset(
    dataset_name: str,
    stat_parts: list[pd.DataFrame],
    missing_counts: pd.Series,
) -> pd.DataFrame:
    numeric_values = pd.concat(stat_parts, ignore_index=True)
    summary = numeric_values.describe().transpose().reset_index(names="column")
    summary["dataset"] = dataset_name
    summary["missing_values"] = summary["column"].map(missing_counts)
    return summary[
        [
            "dataset",
            "column",
            "count",
            "mean",
            "std",
            "min",
            "25%",
            "50%",
            "75%",
            "max",
            "missing_values",
        ]
    ]


def main() -> None:
    TABLE_DIRECTORY.mkdir(parents=True, exist_ok=True)

    hourly_parts = []
    monthly_parts = []
    fault_day_parts = []
    scatter_candidates = []
    metrics_stats_parts = []
    metrics_missing = pd.Series(0, index=METRICS_COLUMNS, dtype="int64")

    for chunk_number, chunk in enumerate(
        pd.read_csv(
            METRICS_FILE,
            chunksize=CHUNK_SIZE,
            dtype={"INVERTER_ID": "int16"},
        ),
        start=1,
    ):
        metrics_missing = metrics_missing.add(chunk.isna().sum(), fill_value=0)
        metrics_stats_parts.append(chunk[METRICS_STATS_COLUMNS].copy())

        chunk["hour"] = chunk["DATE_TIME"].str.slice(11, 13).astype("int8")
        chunk["month"] = chunk["DATE_TIME"].str.slice(0, 7)
        chunk["inverter_group"] = chunk["INVERTER_ID"].isin(FAULT_DAYS)
        chunk["inverter_group"] = chunk["inverter_group"].map(
            {True: "Faulted", False: "Non-faulted"}
        )
        daytime = chunk[chunk["PERFORMANCE_RATIO"].notna()]

        hourly_parts.append(
            daytime.groupby("hour", as_index=False).agg(
                pr_sum=("PERFORMANCE_RATIO", "sum"),
                daytime_rows=("PERFORMANCE_RATIO", "count"),
            )
        )
        monthly_parts.append(
            daytime.groupby(["month", "inverter_group"], as_index=False).agg(
                pr_sum=("PERFORMANCE_RATIO", "sum"),
                daytime_rows=("PERFORMANCE_RATIO", "count"),
            )
        )

        for inverter_id, fault_day in FAULT_DAYS.items():
            fault_rows = chunk[
                (chunk["INVERTER_ID"] == inverter_id)
                & chunk["DATE_TIME"].str.startswith(fault_day)
            ][METRICS_COLUMNS]
            if not fault_rows.empty:
                fault_day_parts.append(fault_rows)

        # Sample each chunk with a fixed seed so rows are spread across the year.
        scatter_candidates.append(
            chunk[["IRRADIANCE", "AC_POWER"]].sample(
                n=min(CANDIDATES_PER_CHUNK, len(chunk)),
                random_state=RANDOM_SEED + chunk_number,
            )
        )
        print(f"Processed metrics chunk {chunk_number}: {len(chunk):,} rows")

    hourly_totals = pd.concat(hourly_parts, ignore_index=True).groupby(
        "hour", as_index=False
    ).agg(pr_sum=("pr_sum", "sum"), daytime_rows=("daytime_rows", "sum"))
    hourly_totals["mean_daytime_pr"] = (
        hourly_totals["pr_sum"] / hourly_totals["daytime_rows"]
    )
    hourly = hourly_totals[["hour", "daytime_rows", "mean_daytime_pr"]]
    hourly.to_csv(TABLE_DIRECTORY / "hourly_mean_pr.csv", index=False)

    monthly_totals = pd.concat(monthly_parts, ignore_index=True).groupby(
        ["month", "inverter_group"], as_index=False
    ).agg(pr_sum=("pr_sum", "sum"), daytime_rows=("daytime_rows", "sum"))
    monthly_totals["mean_daytime_pr"] = (
        monthly_totals["pr_sum"] / monthly_totals["daytime_rows"]
    )
    monthly = monthly_totals[
        ["month", "inverter_group", "daytime_rows", "mean_daytime_pr"]
    ]
    monthly.to_csv(TABLE_DIRECTORY / "monthly_mean_pr_by_group.csv", index=False)

    fault_day_metrics = pd.concat(fault_day_parts, ignore_index=True)
    fault_day_metrics.to_csv(
        TABLE_DIRECTORY / "fault_day_pr_101_202_303.csv", index=False
    )

    candidates = pd.concat(scatter_candidates, ignore_index=True)
    if len(candidates) < SAMPLE_SIZE:
        raise ValueError(
            f"Expected at least {SAMPLE_SIZE:,} scatter candidates, got {len(candidates):,}."
        )
    scatter_sample = candidates.sample(n=SAMPLE_SIZE, random_state=RANDOM_SEED)
    scatter_path = TABLE_DIRECTORY / "scatter_sample_100k.csv.gz"
    scatter_sample.to_csv(scatter_path, index=False, compression="gzip")

    metrics_summary = summarize_dataset(
        "processed_inv_metrics", metrics_stats_parts, metrics_missing
    )
    del metrics_stats_parts

    computation_stats_parts = []
    computation_columns = None
    computation_missing = None
    fault_day_computation_parts = []
    for chunk_number, chunk in enumerate(
        pd.read_csv(
            COMPUTATION_FILE,
            chunksize=CHUNK_SIZE,
            dtype={"inverter_id": "int16"},
        ),
        start=1,
    ):
        if computation_columns is None:
            computation_columns = list(chunk.columns)
            computation_missing = pd.Series(
                0, index=computation_columns, dtype="int64"
            )
        computation_missing = computation_missing.add(
            chunk.isna().sum(), fill_value=0
        )
        computation_stats_parts.append(chunk[COMPUTATION_STATS_COLUMNS].copy())

        for inverter_id, fault_day in FAULT_DAYS.items():
            fault_rows = chunk[
                (chunk["inverter_id"] == inverter_id)
                & chunk["date_time"].str.startswith(fault_day)
            ][["inverter_id", "date_time", "performance_ratio"]]
            if not fault_rows.empty:
                fault_day_computation_parts.append(fault_rows)
        print(f"Processed computation chunk {chunk_number}: {len(chunk):,} rows")

    fault_day_computation = pd.concat(fault_day_computation_parts, ignore_index=True)
    fault_day_computation = fault_day_computation.rename(
        columns={
            "inverter_id": "INVERTER_ID",
            "date_time": "DATE_TIME",
            "performance_ratio": "PERFORMANCE_RATIO",
        }
    )
    fault_day_computation.to_csv(
        TABLE_DIRECTORY / "fault_day_pr_101_202_303.csv", index=False
    )

    flagged_source = SQL_RESULTS_DIRECTORY / "03_flagged_3h_blocks.csv"
    flagged = pd.read_csv(flagged_source)
    flagged_counts = flagged.groupby("severity_tier", as_index=False).agg(
        qualifying_3h_blocks=("qualifying_3h_blocks", "sum")
    )
    flagged_counts.to_csv(
        TABLE_DIRECTORY / "flagged_blocks_by_severity.csv", index=False
    )

    computation_summary = summarize_dataset(
        "open_meteo_computation", computation_stats_parts, computation_missing
    )
    summary = pd.concat([metrics_summary, computation_summary], ignore_index=True)
    summary.to_csv(TABLE_DIRECTORY / "summary_statistics.csv", index=False)

    output_files = [
        TABLE_DIRECTORY / "hourly_mean_pr.csv",
        TABLE_DIRECTORY / "monthly_mean_pr_by_group.csv",
        TABLE_DIRECTORY / "fault_day_pr_101_202_303.csv",
        TABLE_DIRECTORY / "flagged_blocks_by_severity.csv",
        scatter_path,
        TABLE_DIRECTORY / "summary_statistics.csv",
    ]
    for output_file in output_files:
        size_bytes = output_file.stat().st_size
        if size_bytes >= MAX_OUTPUT_BYTES:
            raise ValueError(f"{output_file.name} is {size_bytes:,} bytes, above 2 MB.")
        print(f"Saved {output_file.relative_to(PROJECT_ROOT)} ({size_bytes:,} bytes)")


if __name__ == "__main__":
    main()
