from pathlib import Path

import pandas as pd


# Paths are relative to the project root; all input tables are compact outputs.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
TABLES_DIR = PROJECT_ROOT / "output" / "tables"
SUMMARY_STATS_PATH = TABLES_DIR / "summary_statistics.csv"
SEVERITY_PATH = TABLES_DIR / "flagged_blocks_by_severity.csv"
FLAGGED_INVERTERS_PATH = PROJECT_ROOT / "output" / "sql_results" / "03_flagged_3h_blocks.csv"
SCATTER_SAMPLE_PATH = TABLES_DIR / "scatter_sample_100k.csv"
FAULT_VALIDATION_PATH = TABLES_DIR / "fault_detection_validation.csv"
OUTPUT_PATH = TABLES_DIR / "kpi_summary.csv"

# Project assumptions and thresholds.
FLEET_INVERTER_COUNT = 830  # inverters
RATED_AC_POWER_KW = 60.0  # kW
MAX_OUTPUT_BYTES = 1_000_000  # bytes


def require_columns(table, required_columns, source_name):
    missing_columns = [
        column for column in required_columns if column not in table.columns
    ]
    assert not missing_columns, (
        f"{source_name} is missing required columns: {missing_columns}"
    )


def main():
    print("Loading compact KPI source tables")
    summary_stats = pd.read_csv(SUMMARY_STATS_PATH)
    severity_counts = pd.read_csv(SEVERITY_PATH)
    flagged_inverters = pd.read_csv(FLAGGED_INVERTERS_PATH)
    clipping_sample = pd.read_csv(SCATTER_SAMPLE_PATH)
    fault_validation = pd.read_csv(FAULT_VALIDATION_PATH)

    require_columns(
        summary_stats,
        ["dataset", "column", "count", "mean"],
        "summary_statistics.csv",
    )
    require_columns(
        severity_counts,
        ["severity_tier", "qualifying_3h_blocks"],
        "flagged_blocks_by_severity.csv",
    )
    require_columns(clipping_sample, ["AC_POWER"], "scatter_sample_100k.csv")
    require_columns(
        fault_validation,
        ["detected"],
        "fault_detection_validation.csv",
    )
    require_columns(
        flagged_inverters,
        ["inverter_id", "block_start", "block_end", "mean_pr_gap", "severity_tier"],
        "03_flagged_3h_blocks.csv",
    )

    pr_rows = summary_stats.loc[
        (summary_stats["dataset"] == "processed_inv_metrics")
        & (summary_stats["column"] == "PERFORMANCE_RATIO")
    ]
    assert len(pr_rows) == 1, "Expected one processed PERFORMANCE_RATIO summary row"
    mean_pr = float(pr_rows.iloc[0]["mean"])
    valid_pr_rows = int(pr_rows.iloc[0]["count"])
    assert valid_pr_rows > 0, "Expected valid daytime PR rows"
    fleet_mean_pr_shortfall = 1.0 - mean_pr

    total_flagged_blocks = int(severity_counts["qualifying_3h_blocks"].sum())
    assert total_flagged_blocks > 0, "Expected at least one qualifying 3-hour block"
    flagged_inverter_count = int(flagged_inverters["inverter_id"].nunique())
    flagged_inverter_share = flagged_inverter_count / FLEET_INVERTER_COUNT * 100.0
    severity_labels = ["Watch", "Alert", "Critical"]
    severity_parts = []
    for severity_label in severity_labels:
        tier_rows = severity_counts.loc[
            severity_counts["severity_tier"] == severity_label
        ]
        tier_count = int(tier_rows["qualifying_3h_blocks"].sum())
        tier_share = tier_count / total_flagged_blocks * 100.0
        severity_parts.append(
            f"{severity_label}: {tier_count:,} ({tier_share:.2f}%)"
        )
    severity_value = "; ".join(severity_parts)

    assert len(clipping_sample) > 0, "Expected at least one clipping sample row"
    clipping_count = int(
        (clipping_sample["AC_POWER"] >= RATED_AC_POWER_KW).sum()
    )
    clipping_share = clipping_count / len(clipping_sample) * 100.0

    detected_count = int(fault_validation["detected"].astype(bool).sum())
    injected_window_count = len(fault_validation)
    assert injected_window_count > 0, "Expected at least one injected fault window"
    detection_rate = detected_count / injected_window_count * 100.0

    kpi_rows = [
        {
            "KPI": "Performance Ratio (hourly, per inverter)",
            "Value": mean_pr,
            "Unit": "unitless ratio",
            "Definition and formula": "Mean valid hourly PR across processed inverter-hour rows; PR = AC_POWER / (irradiance_kWh_m2 * installed_DC_kWp).",
            "Source": "output/tables/summary_statistics.csv",
            "How to read it": "Pooled daytime mean; compare with the normalized reference of 1.0.",
            "Limitation": "Aggregate mean does not show individual inverter-hour variation; inputs are modeled.",
        },
        {
            "KPI": "fleet_mean_pr_shortfall_from_1",
            "Value": fleet_mean_pr_shortfall,
            "Unit": "unitless ratio",
            "Definition and formula": "1 - pooled mean valid hourly PR; distinct from per-timestamp fleet-median pr_gap.",
            "Source": "Derived from output/tables/summary_statistics.csv",
            "How to read it": "Distance below the normalized PR reference of 1.0; this is not the detector's pr_gap.",
            "Limitation": "Not a comparison to a healthy-fleet baseline and not proof of a fault.",
        },
        {
            "KPI": "Flagged 3-hour block count",
            "Value": total_flagged_blocks,
            "Unit": "blocks",
            "Definition and formula": "Sum of saved severity-tier block counts; see sql/03_flagged_3h_blocks.sql.",
            "Source": "output/tables/flagged_blocks_by_severity.csv",
            "How to read it": "Rolling qualifying windows; overlapping blocks count separately.",
            "Limitation": "Fixed-rule flags on simulated data are not confirmed failures.",
        },
        {
            "KPI": "Flagged inverter share",
            "Value": f"{flagged_inverter_share:.2f}% ({flagged_inverter_count}/{FLEET_INVERTER_COUNT})",
            "Unit": "% of fleet",
            "Definition and formula": "Inverters with at least one qualifying block / 830 * 100.",
            "Source": "Distinct inverter IDs in output/sql_results/03_flagged_3h_blocks.csv; fleet size from README.md.",
            "How to read it": "Share of the fleet with at least one qualifying rolling block.",
            "Limitation": "Flags are based on simulated data and a fixed demonstration rule, not confirmed failures.",
        },
        {
            "KPI": "Severity distribution (Watch, Alert, Critical)",
            "Value": severity_value,
            "Unit": "blocks and % of flagged blocks",
            "Definition and formula": "Count and share per tier; tier count / total flagged blocks * 100.",
            "Source": "output/tables/flagged_blocks_by_severity.csv",
            "How to read it": "Shows the tier mix of saved qualifying blocks.",
            "Limitation": "Overlapping blocks count separately; exactly 0.20 is Alert in the saved SQL query.",
        },
        {
            "KPI": "Clipping hours share (sample estimate)",
            "Value": f"{clipping_share:.4f}%",
            "Unit": "% of sampled inverter-hour rows",
            "Definition and formula": "Rows with AC_POWER >= 60 kW / sampled inverter-hour rows * 100.",
            "Source": "output/tables/scatter_sample_100k.csv",
            "How to read it": "Estimated frequency of records at the modeled 60 kW AC cap.",
            "Limitation": "Fixed-seed sample estimate, not the exact fleet-wide share; sample has no timestamps.",
        },
        {
            "KPI": "Fault detection rate",
            "Value": f"{detection_rate:.2f}% ({detected_count}/{injected_window_count})",
            "Unit": "% of injected windows",
            "Definition and formula": "Detected injected windows / total injected windows * 100.",
            "Source": "output/tables/fault_detection_validation.csv",
            "How to read it": "Checks the rolling three-hour fleet-median-gap rule against the three synthetic windows.",
            "Limitation": "Only three synthetic windows; not a real-world performance estimate.",
        },
    ]

    kpi_summary = pd.DataFrame(kpi_rows)
    assert len(kpi_summary) == 7, "Expected exactly seven KPI rows"
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    kpi_summary.to_csv(OUTPUT_PATH, index=False)
    output_size = OUTPUT_PATH.stat().st_size
    assert output_size < MAX_OUTPUT_BYTES, "kpi_summary.csv must be under 1 MB"
    print(f"Saved {len(kpi_summary)} KPIs to {OUTPUT_PATH.relative_to(PROJECT_ROOT)}")
    print(f"Output size: {output_size:,} bytes")


if __name__ == "__main__":
    main()