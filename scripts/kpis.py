from pathlib import Path

import pandas as pd

from transform import FAULT_WINDOWS


# Paths are relative to the project root; all input tables are compact outputs.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
TABLES_DIR = PROJECT_ROOT / "output" / "tables"
SUMMARY_STATS_PATH = TABLES_DIR / "summary_statistics.csv"
SEVERITY_PATH = TABLES_DIR / "flagged_blocks_by_severity.csv"
FLAGGED_INVERTERS_PATH = PROJECT_ROOT / "output" / "sql_results" / "03_flagged_3h_blocks.csv"
SCATTER_SAMPLE_PATH = TABLES_DIR / "scatter_sample_100k.csv"
FAULT_VALIDATION_PATH = TABLES_DIR / "fault_detection_validation.csv"
FALSE_ALARM_PATH = TABLES_DIR / "false_alarm_check.csv"
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
        ["inverter_id", "target_tier", "detected", "tier_matches_target"],
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

    designed_validation = fault_validation[
        fault_validation["target_tier"].isin(severity_labels)
    ]
    detected_flags = fault_validation["detected"].astype(str).str.lower().eq("true")
    designed_detected = detected_flags.loc[designed_validation.index]
    detected_count = int(designed_detected.sum())
    injected_window_count = len(designed_validation)
    assert injected_window_count > 0, "Expected designed fault windows"
    detection_rate = detected_count / injected_window_count * 100.0
    faulted_inverters = {fault["inverter_id"] for fault in FAULT_WINDOWS}
    non_faulted_inverter_count = FLEET_INVERTER_COUNT - len(faulted_inverters)
    non_faulted_flags = flagged_inverters[
        ~flagged_inverters["inverter_id"].isin(faulted_inverters)
    ]
    flagged_blocks_on_non_faulted = len(non_faulted_flags)
    non_faulted_inverters_flagged = int(
        non_faulted_flags["inverter_id"].nunique()
    )
    false_alarm_note = (
        "Zero false alarms are expected here because non-faulted inverters share "
        "the same weather and simulated PR; this checks identical peers only, "
        "not noisy real data."
    )
    pd.DataFrame(
        [
            {
                "faulted_inverters": len(faulted_inverters),
                "non_faulted_inverters": non_faulted_inverter_count,
                "flagged_blocks_on_non_faulted": flagged_blocks_on_non_faulted,
                "non_faulted_inverters_flagged": non_faulted_inverters_flagged,
                "note": false_alarm_note,
            }
        ]
    ).to_csv(FALSE_ALARM_PATH, index=False)
    tier_detection = []
    for tier in severity_labels:
        tier_rows = fault_validation[fault_validation["target_tier"] == tier]
        tier_detection.append(
            f"{tier}: {int(detected_flags.loc[tier_rows.index].sum())}/{len(tier_rows)}"
        )
    hard_rows = fault_validation[
        fault_validation["target_tier"].str.contains("expected miss", case=False)
    ]
    hard_misses = int((~detected_flags.loc[hard_rows.index]).sum())
    tier_detection.append(f"Hard cases (expected misses): {hard_misses}/{len(hard_rows)}")
    detection_by_tier = "; ".join(tier_detection)

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
            "Definition and formula": "Detected designed Watch, Alert, and Critical windows / designed windows * 100; excludes hard cases labeled expected misses.",
            "Source": "output/tables/fault_detection_validation.csv",
            "How to read it": "Checks the 12 designed tier-positive synthetic windows against the fixed rolling rule.",
            "Limitation": "This controlled test is not a real-world accuracy estimate.",
        },
        {
            "KPI": "False alarm blocks",
            "Value": flagged_blocks_on_non_faulted,
            "Unit": "blocks on non-faulted inverters",
            "Definition and formula": "Count of saved flagged rolling blocks whose inverter ID is absent from FAULT_WINDOWS.",
            "Source": "output/tables/false_alarm_check.csv and output/sql_results/03_flagged_3h_blocks.csv",
            "How to read it": "Zero is expected because all non-faulted inverters share identical modeled weather and PR.",
            "Limitation": "Confirms the rule does not misfire on identical simulated peers; it says nothing about noisy real data.",
        },
        {
            "KPI": "Detection by target",
            "Value": detection_by_tier,
            "Unit": "detected / injected windows",
            "Definition and formula": "Detected windows / injected windows by target tier; hard windows are expected misses.",
            "Source": "output/tables/fault_detection_validation.csv",
            "How to read it": "Separates the 12 designed tier tests from the three hard cases that demonstrate rule limits.",
            "Limitation": "Synthetic checks do not establish real-world detection accuracy.",
        },
    ]

    kpi_summary = pd.DataFrame(kpi_rows)
    assert len(kpi_summary) == 9, "Expected exactly nine KPI rows"
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    kpi_summary.to_csv(OUTPUT_PATH, index=False)
    output_size = OUTPUT_PATH.stat().st_size
    assert output_size < MAX_OUTPUT_BYTES, "kpi_summary.csv must be under 1 MB"
    print(f"Saved {len(kpi_summary)} KPIs to {OUTPUT_PATH.relative_to(PROJECT_ROOT)}")
    print(f"Saved false-alarm check to {FALSE_ALARM_PATH.relative_to(PROJECT_ROOT)}")
    print(f"Output size: {output_size:,} bytes")


if __name__ == "__main__":
    main()