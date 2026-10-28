import csv
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TABLES_DIR = PROJECT_ROOT / "output" / "tables"
SQL_RESULTS_DIR = PROJECT_ROOT / "output" / "sql_results"
OUTPUT_PATH = PROJECT_ROOT / "docs" / "data" / "dashboard_data.json"
REQUIRED_KEYS = (
    "kpis",
    "headline",
    "rolling_blocks_by_tier",
    "inverters_by_tier",
    "flagged_blocks",
    "flagged_inverters",
    "detection_validation",
    "false_alarm_check",
    "inverter_detail",
    "hourly_mean_pr",
)


def load_csv(filename):
    path = TABLES_DIR / filename
    with path.open("r", newline="", encoding="utf-8-sig") as input_file:
        return list(csv.DictReader(input_file))


def load_sql_csv(filename):
    path = SQL_RESULTS_DIR / filename
    with path.open("r", newline="", encoding="utf-8-sig") as input_file:
        return list(csv.DictReader(input_file))


def build_flagged_blocks(rows):
    flagged_blocks = []
    for row in rows:
        block_start = row["block_start"]
        block_end = row["block_end"]
        date, start_time = block_start.split(" ", maxsplit=1)
        _, end_time = block_end.split(" ", maxsplit=1)
        flagged_blocks.append(
            {
                "inverter_id": row["inverter_id"],
                "date": date,
                "start_time": start_time,
                "end_time": end_time,
                "block_start": block_start,
                "block_end": block_end,
                "mean_gap": row["mean_pr_gap"],
                "severity_tier": row["severity_tier"],
            }
        )
    flagged_blocks.sort(key=lambda item: float(item["mean_gap"]), reverse=True)
    return flagged_blocks


def build_rolling_blocks_by_tier(rows):
    counts = {"Watch": 0, "Alert": 0, "Critical": 0}
    for row in rows:
        tier = row["severity_tier"]
        if tier in counts:
            counts[tier] = int(row["qualifying_3h_blocks"])
    return counts


def build_flagged_inverters(rows, validation_rows):
    validation_by_inverter = {
        row["inverter_id"]: row["target_tier"] for row in validation_rows
    }
    summaries = {}
    tier_rank = {"Watch": 1, "Alert": 2, "Critical": 3}

    for row in rows:
        inverter_id = row["inverter_id"]
        tier = row["severity_tier"]
        if inverter_id not in summaries:
            summaries[inverter_id] = {
                "inverter_id": inverter_id,
                "first_block_start": row["block_start"],
                "last_block_end": row["block_end"],
                "rolling_block_count": 0,
                "peak_mean_gap": 0.0,
                "highest_tier": tier,
            }

        summary = summaries[inverter_id]
        summary["first_block_start"] = min(summary["first_block_start"], row["block_start"])
        summary["last_block_end"] = max(summary["last_block_end"], row["block_end"])
        summary["rolling_block_count"] += 1
        summary["peak_mean_gap"] = max(summary["peak_mean_gap"], float(row["mean_pr_gap"]))
        if tier_rank.get(tier, 0) > tier_rank.get(summary["highest_tier"], 0):
            summary["highest_tier"] = tier

    flagged_inverters = list(summaries.values())
    for summary in flagged_inverters:
        summary["test_target"] = validation_by_inverter.get(
            summary["inverter_id"], "Not a designed test fault"
        )

    flagged_inverters.sort(
        key=lambda item: (
            -tier_rank.get(item["highest_tier"], 0),
            -item["peak_mean_gap"],
        )
    )
    return flagged_inverters


def build_inverters_by_tier(flagged_inverters):
    counts = {"Watch": 0, "Alert": 0, "Critical": 0}
    for inverter in flagged_inverters:
        tier = inverter["highest_tier"]
        if tier in counts:
            counts[tier] += 1
    return counts


def build_headline(flagged_inverters, detection_rows, false_alarm_row):
    flagged_by_tier = build_inverters_by_tier(flagged_inverters)
    designed_faults = [
        row for row in detection_rows if "expected miss" not in row["target_tier"].lower()
    ]
    expected_misses = [
        row for row in detection_rows if "expected miss" in row["target_tier"].lower()
    ]
    caught = sum(row["detected"] == "True" for row in designed_faults)
    misses_confirmed = sum(row["detected"] == "False" for row in expected_misses)
    non_faulted_inverters = int(false_alarm_row["non_faulted_inverters"])
    faulted_inverters = int(false_alarm_row["faulted_inverters"])

    assert sum(flagged_by_tier.values()) == len(flagged_inverters)
    return {
        "flagged_inverters": len(flagged_inverters),
        "fleet_size": faulted_inverters + non_faulted_inverters,
        "critical_inverters": flagged_by_tier["Critical"],
        "alert_inverters": flagged_by_tier["Alert"],
        "watch_inverters": flagged_by_tier["Watch"],
        "designed_faults_caught": f"{caught}/{len(designed_faults)}",
        "expected_misses_confirmed": f"{misses_confirmed}/{len(expected_misses)}",
        "false_alarm_blocks": int(false_alarm_row["flagged_blocks_on_non_faulted"]),
        "non_faulted_inverters": non_faulted_inverters,
    }


def note_for_row(row, flagged_tier):
    gap = float(row["mean_pr_gap"])
    if row["detected"] == "True":
        return f"Caught in its own window at the {row['severity_tier']} level."
    if flagged_tier is None:
        return (
            f"Gap of {gap:.3f} is below the 0.05 threshold, "
            "so no flag is expected."
        )

    if gap < 0.05:
        tier_by_gap = "Below Watch"
    elif gap < 0.10:
        tier_by_gap = "Watch"
    elif gap <= 0.20:
        tier_by_gap = "Alert"
    else:
        tier_by_gap = "Critical"
    return (
        "The fault window is too short for the 3-hour rule. "
        f"Its gap of {gap:.3f} would be {tier_by_gap}, but neighboring normal "
        f"hours dilute the 3-hour average, so the flag appears as {flagged_tier}."
    )


def build_detection_validation(rows, flagged_inverters):
    flagged_ids = {row["inverter_id"] for row in flagged_inverters}
    flagged_tiers = {
        row["inverter_id"]: row["highest_tier"] for row in flagged_inverters
    }
    validation_rows = []
    for row in rows:
        flagged_anywhere = row["inverter_id"] in flagged_ids
        note = note_for_row(row, flagged_tiers.get(row["inverter_id"]))
        validation_rows.append(
            {**row, "flagged_anywhere": flagged_anywhere, "note": note}
        )
    return validation_rows


def build_inverter_detail(rows, validation_rows):
    inverter_ids = {row["INVERTER_ID"] for row in rows}
    detail = {inverter_id: [] for inverter_id in sorted(inverter_ids, key=int)}
    for row in rows:
        inverter_id = row["INVERTER_ID"]
        if inverter_id in detail:
            pr_value = row["PERFORMANCE_RATIO"]
            if not pr_value:
                continue
            detail[inverter_id].append(
                {
                    "date_time": row["DATE_TIME"],
                    "performance_ratio": float(pr_value),
                }
            )
    return detail


def main():
    kpis = load_csv("kpi_summary.csv")
    severity_rows = load_csv("flagged_blocks_by_severity.csv")
    flagged_block_rows = load_sql_csv("03_flagged_3h_blocks.csv")
    detection_validation = load_csv("fault_detection_validation.csv")
    fault_day_rows = load_csv("fault_day_pr_by_tier.csv")
    false_alarm_check = load_csv("false_alarm_check.csv")
    hourly_mean_pr = load_csv("hourly_mean_pr.csv")
    false_alarm_row = false_alarm_check[0]

    flagged_blocks = build_flagged_blocks(flagged_block_rows)
    flagged_inverters = build_flagged_inverters(flagged_block_rows, detection_validation)
    inverters_by_tier = build_inverters_by_tier(flagged_inverters)
    detection_validation = build_detection_validation(detection_validation, flagged_inverters)
    flagged_count = int(
        next(row["Value"] for row in kpis if row["KPI"] == "Flagged 3-hour block count")
    )
    assert flagged_count == 0 or len(flagged_blocks) > 0, (
        "The KPI reports flagged blocks, but the saved SQL result contains none."
    )

    dashboard_data = {
        "kpis": kpis,
        "headline": build_headline(flagged_inverters, load_csv("fault_detection_validation.csv"), false_alarm_row),
        "rolling_blocks_by_tier": build_rolling_blocks_by_tier(severity_rows),
        "inverters_by_tier": inverters_by_tier,
        "flagged_blocks": flagged_blocks,
        "flagged_inverters": flagged_inverters,
        "detection_validation": detection_validation,
        "false_alarm_check": false_alarm_check,
        "inverter_detail": build_inverter_detail(fault_day_rows, detection_validation),
        "hourly_mean_pr": hourly_mean_pr,
    }
    assert all(key in dashboard_data for key in REQUIRED_KEYS)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8", newline="\n") as output_file:
        json.dump(dashboard_data, output_file, ensure_ascii=True, indent=2, sort_keys=True)
        output_file.write("\n")


if __name__ == "__main__":
    main()