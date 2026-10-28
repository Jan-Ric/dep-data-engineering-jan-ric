import csv
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TABLES_DIR = PROJECT_ROOT / "output" / "tables"
OUTPUT_PATH = PROJECT_ROOT / "docs" / "data" / "dashboard_data.json"
REQUIRED_KEYS = (
    "kpis",
    "severity_counts",
    "flagged_blocks",
    "ranking",
    "detection_validation",
    "inverter_detail",
    "hourly_mean_pr",
)


def load_csv(filename):
    path = TABLES_DIR / filename
    with path.open("r", newline="", encoding="utf-8-sig") as input_file:
        return list(csv.DictReader(input_file))


def build_severity_counts(rows):
    counts = {"Watch": 0, "Alert": 0, "Critical": 0}
    for row in rows:
        tier = row["severity_tier"]
        if tier in counts:
            counts[tier] = int(row["qualifying_3h_blocks"])
    return counts


def build_inverter_detail(rows, validation_rows):
    inverter_ids = {row["inverter_id"] for row in validation_rows}
    detail = {inverter_id: [] for inverter_id in sorted(inverter_ids, key=int)}
    for row in rows:
        inverter_id = row["INVERTER_ID"]
        if inverter_id in detail:
            pr_value = row["PERFORMANCE_RATIO"]
            detail[inverter_id].append(
                {
                    "date_time": row["DATE_TIME"],
                    "performance_ratio": float(pr_value) if pr_value else None,
                }
            )
    return detail


def main():
    kpis = load_csv("kpi_summary.csv")
    severity_rows = load_csv("flagged_blocks_by_severity.csv")
    detailed_block_rows = load_csv("alert_blocks.csv")
    ranking = load_csv("inverter_ranking.csv")[:10]
    detection_validation = load_csv("fault_detection_validation.csv")
    fault_day_rows = load_csv("fault_day_pr_101_202_303.csv")
    hourly_mean_pr = load_csv("hourly_mean_pr.csv")

    # This saved table has no rows; do not rebuild block details from the large input.
    flagged_blocks = []
    if detailed_block_rows:
        flagged_blocks = detailed_block_rows

    dashboard_data = {
        "kpis": kpis,
        "severity_counts": build_severity_counts(severity_rows),
        "flagged_blocks": flagged_blocks,
        "ranking": ranking,
        "detection_validation": detection_validation,
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