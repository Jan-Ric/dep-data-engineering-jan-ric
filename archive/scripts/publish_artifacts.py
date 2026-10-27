from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import duckdb
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
METRICS_FILE = PROJECT_ROOT / "data/processed/processed_inv_metrics.csv"
FAULT_CONFIG_FILE = PROJECT_ROOT / "config/fault_windows.json"
ARTIFACT_DIR = PROJECT_ROOT / "dashboard/data"
EXISTING_DAILY_SUMMARY = PROJECT_ROOT / "data/processed/daily_inv_summary.csv"
SQL_FILE = PROJECT_ROOT / "project_queries.sql"
SCRIPT_VERSION = "1.0.0"
BASELINE_GAP_THRESHOLD = 0.05
IRRADIANCE_THRESHOLD_W_M2 = 200.0
BLOCK_HOURS = 3
SQL_PREVIEW_ROWS = 100
CONTROL_INVERTERS = [1, 415, 830]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def get_git_sha() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=PROJECT_ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, lineterminator="\n", float_format="%.10g")


def read_sql_statements() -> list[str]:
    sql_text = SQL_FILE.read_text(encoding="utf-8")
    sql_text = re.sub(r"/\*.*?\*/", "", sql_text, flags=re.DOTALL)
    sql_text = re.sub(r"--[^\n]*", "", sql_text)
    return [statement.strip() for statement in sql_text.split(";") if statement.strip()]


def create_views(connection: duckdb.DuckDBPyConnection) -> None:
    metrics_path = str(METRICS_FILE).replace("\\", "/").replace("'", "''")
    connection.execute(
        f"""CREATE VIEW processed_inv_metrics AS
        SELECT * FROM read_csv_auto('{metrics_path}', header=true)"""
    )
    connection.execute(
        """CREATE VIEW hourly_baseline AS
        SELECT DATE_TIME,
               median(PERFORMANCE_RATIO) AS baseline_pr,
               median(AC_POWER) AS baseline_ac_power,
               median(IRRADIANCE) AS irradiance_w_m2
        FROM processed_inv_metrics
        WHERE PERFORMANCE_RATIO IS NOT NULL
        GROUP BY DATE_TIME"""
    )
    connection.execute(
        f"""CREATE VIEW hourly_gaps AS
        SELECT metrics.INVERTER_ID,
               metrics.DATE_TIME,
               metrics.AC_POWER,
               metrics.IRRADIANCE,
               metrics.PERFORMANCE_RATIO,
               baseline.baseline_pr,
               baseline.baseline_ac_power,
               baseline.baseline_pr - metrics.PERFORMANCE_RATIO AS baseline_gap
        FROM processed_inv_metrics AS metrics
        JOIN hourly_baseline AS baseline USING (DATE_TIME)
        WHERE metrics.PERFORMANCE_RATIO IS NOT NULL"""
    )
    connection.execute(
        f"""CREATE VIEW relative_blocks AS
        SELECT INVERTER_ID,
               CAST(DATE_TIME AS DATE) AS DATE,
               FLOOR(EXTRACT(HOUR FROM DATE_TIME) / {BLOCK_HOURS}) AS block_number,
               MIN(DATE_TIME) AS block_start,
               MAX(DATE_TIME) AS block_end,
               AVG(PERFORMANCE_RATIO) AS mean_performance_ratio,
               AVG(baseline_pr) AS mean_baseline_pr,
               AVG(baseline_gap) AS mean_baseline_gap,
               MIN(IRRADIANCE) AS min_irradiance_w_m2,
               COUNT(*) AS observed_hours
        FROM hourly_gaps
        GROUP BY INVERTER_ID, CAST(DATE_TIME AS DATE),
                 FLOOR(EXTRACT(HOUR FROM DATE_TIME) / {BLOCK_HOURS})
        HAVING COUNT(*) = {BLOCK_HOURS}
           AND MIN(IRRADIANCE) > {IRRADIANCE_THRESHOLD_W_M2}
           AND AVG(baseline_gap) >= {BASELINE_GAP_THRESHOLD}"""
    )
    connection.execute(
        """CREATE VIEW relative_alert_blocks AS
        SELECT *,
               CASE
                   WHEN mean_baseline_gap < 0.10 THEN 'Watch'
                   WHEN mean_baseline_gap < 0.20 THEN 'Alert'
                   ELSE 'Critical'
               END AS severity
        FROM relative_blocks"""
    )


def query_dataframe(connection: duckdb.DuckDBPyConnection, query: str) -> pd.DataFrame:
    return connection.execute(query).fetchdf()


def generate_artifacts(output_dir: Path, sample_output: Path) -> dict[str, object]:
    with FAULT_CONFIG_FILE.open(encoding="utf-8") as file:
        fault_config = json.load(file)
    fault_windows = fault_config["fault_windows"]

    connection = duckdb.connect()
    connection.execute("SET threads TO 1")
    create_views(connection)

    eligible = int(connection.execute(
        "SELECT COUNT(*) FROM processed_inv_metrics WHERE PERFORMANCE_RATIO IS NOT NULL"
    ).fetchone()[0])
    total_rows = int(connection.execute("SELECT COUNT(*) FROM processed_inv_metrics").fetchone()[0])
    date_bounds = connection.execute(
        "SELECT MIN(DATE_TIME), MAX(DATE_TIME) FROM processed_inv_metrics"
    ).fetchone()
    inverter_count = int(connection.execute(
        "SELECT COUNT(DISTINCT INVERTER_ID) FROM processed_inv_metrics"
    ).fetchone()[0])

    baseline_daily = query_dataframe(
        connection,
        f"""WITH daily AS (
            SELECT CAST(DATE_TIME AS DATE) AS DATE,
                   AVG(baseline_pr) AS fleet_median_pr,
                   SUM(CASE WHEN baseline_pr <= 1 - {BASELINE_GAP_THRESHOLD}
                                 AND irradiance_w_m2 > {IRRADIANCE_THRESHOLD_W_M2}
                            THEN 1 ELSE 0 END) AS baseline_absolute_flagged_hours,
                   SUM(baseline_ac_power) AS baseline_ac_energy_kwh,
                   AVG(irradiance_w_m2) AS mean_irradiance_w_m2
            FROM hourly_baseline
            GROUP BY CAST(DATE_TIME AS DATE)
        )
        SELECT * FROM daily ORDER BY DATE""",
    )
    write_csv(baseline_daily, output_dir / "baseline_daily.csv")

    ranking = query_dataframe(
        connection,
        f"""WITH metrics AS (
            SELECT INVERTER_ID,
                   AVG(PERFORMANCE_RATIO) AS mean_performance_ratio,
                   SUM(CASE WHEN baseline_gap >= {BASELINE_GAP_THRESHOLD}
                                  AND IRRADIANCE > {IRRADIANCE_THRESHOLD_W_M2}
                            THEN 1 ELSE 0 END) AS baseline_relative_flagged_hours,
                   SUM(CASE WHEN 1 - PERFORMANCE_RATIO >= {BASELINE_GAP_THRESHOLD}
                                  AND IRRADIANCE > {IRRADIANCE_THRESHOLD_W_M2}
                            THEN 1 ELSE 0 END) AS absolute_flagged_hours,
                   SUM(AC_POWER) AS total_ac_energy_kwh
            FROM hourly_gaps
            GROUP BY INVERTER_ID
        ), blocks AS (
            SELECT INVERTER_ID,
                   COUNT(*) AS alert_block_count,
                   MAX(mean_baseline_gap) AS max_block_gap,
                   MAX(CASE severity
                       WHEN 'Critical' THEN 3 WHEN 'Alert' THEN 2 WHEN 'Watch' THEN 1 ELSE 0
                   END) AS max_severity_rank
            FROM relative_alert_blocks
            GROUP BY INVERTER_ID
        )
        SELECT metrics.INVERTER_ID,
               metrics.mean_performance_ratio,
               metrics.baseline_relative_flagged_hours,
               metrics.absolute_flagged_hours,
               COALESCE(blocks.alert_block_count, 0) AS alert_block_count,
               COALESCE(blocks.max_block_gap, 0) AS max_block_gap,
               CASE COALESCE(blocks.max_severity_rank, 0)
                   WHEN 3 THEN 'Critical' WHEN 2 THEN 'Alert' WHEN 1 THEN 'Watch' ELSE 'Normal'
               END AS max_severity,
               metrics.total_ac_energy_kwh
        FROM metrics
        LEFT JOIN blocks USING (INVERTER_ID)
        ORDER BY metrics.INVERTER_ID""",
    )
    ranking["rank"] = ranking["mean_performance_ratio"].rank(
        ascending=True, method="min"
    ).astype("int64")
    ranking = ranking.sort_values(["rank", "INVERTER_ID"])
    write_csv(ranking, output_dir / "inverter_ranking.csv")

    alert_blocks = query_dataframe(
        connection,
        """SELECT INVERTER_ID, DATE, block_number, block_start, block_end,
                  mean_performance_ratio, mean_baseline_pr, mean_baseline_gap,
                  min_irradiance_w_m2, severity
           FROM relative_alert_blocks
           ORDER BY DATE, block_start, INVERTER_ID""",
    )
    write_csv(alert_blocks, output_dir / "alert_blocks.csv")

    detail_ids = sorted({int(fault["inverter_id"]) for fault in fault_windows})
    for inverter_id in detail_ids:
        detail = query_dataframe(
            connection,
            f"""SELECT INVERTER_ID, DATE_TIME, PERFORMANCE_RATIO,
                      baseline_pr, baseline_gap, AC_POWER, IRRADIANCE
               FROM hourly_gaps
               WHERE INVERTER_ID = {inverter_id} AND IRRADIANCE > 0
               ORDER BY DATE_TIME""",
        )
        write_csv(detail, output_dir / "inverter_detail" / f"{inverter_id}.csv")

    sample_ids = sorted({int(fault["inverter_id"]) for fault in fault_windows} | set(CONTROL_INVERTERS))
    sample_conditions = []
    for fault in fault_windows:
        fault_date = pd.Timestamp(fault["start"]).date()
        sample_conditions.append(
            f"(CAST(DATE_TIME AS DATE) BETWEEN DATE '{fault_date - pd.Timedelta(days=1)}' "
            f"AND DATE '{fault_date + pd.Timedelta(days=1)}')"
        )
    sample_filter = " OR ".join(sample_conditions)
    sample = query_dataframe(
        connection,
        f"""SELECT INVERTER_ID, DATE_TIME, AC_POWER, IRRADIANCE, PERFORMANCE_RATIO
            FROM processed_inv_metrics
            WHERE INVERTER_ID IN ({', '.join(map(str, sample_ids))})
              AND ({sample_filter})
            ORDER BY DATE_TIME, INVERTER_ID""",
    )
    write_csv(sample, sample_output)

    sql_results: dict[str, dict[str, object]] = {}
    sql_names = [
        "absolute_hourly_ranking",
        "absolute_fixed_3h_blocks",
        "absolute_fixed_3h_severity",
    ]
    statements = read_sql_statements()
    if len(statements) != len(sql_names):
        raise ValueError(f"Expected {len(sql_names)} SQL statements, found {len(statements)}")
    for name, statement in zip(sql_names, statements, strict=True):
        result_count = int(connection.execute(
            f"SELECT COUNT(*) FROM ({statement}) AS query_result"
        ).fetchone()[0])
        preview_limit = result_count if name == "absolute_hourly_ranking" else SQL_PREVIEW_ROWS
        result = query_dataframe(
            connection,
            f"SELECT * FROM ({statement}) AS query_result LIMIT {preview_limit}",
        )
        preview_name = f"{name}.csv" if name == "absolute_hourly_ranking" else f"{name}_top{SQL_PREVIEW_ROWS}.csv"
        write_csv(result, output_dir / preview_name)
        sql_results[name] = {
            "result_rows": result_count,
            "published_preview_rows": len(result),
            "preview_file": preview_name,
        }

    validation = query_dataframe(
        connection,
        """SELECT INVERTER_ID, DATE, block_start, block_end,
                  mean_baseline_gap, severity
           FROM relative_alert_blocks
           ORDER BY DATE, block_start, INVERTER_ID""",
    )
    detected_keys: set[tuple[int, str]] = set()
    for row in validation.itertuples(index=False):
        for fault in fault_windows:
            if int(row.INVERTER_ID) != int(fault["inverter_id"]):
                continue
            if str(row.block_start) <= fault["end"] and str(row.block_end) >= fault["start"]:
                detected_keys.add((int(row.INVERTER_ID), str(row.DATE)))
    validation_rows = []
    for fault in fault_windows:
        inverter_id = int(fault["inverter_id"])
        fault_date = fault["start"][:10]
        detected = (inverter_id, fault_date) in detected_keys
        validation_rows.append({
            "INVERTER_ID": inverter_id,
            "fault_start": fault["start"],
            "fault_end": fault["end"],
            "injected_hours": 1 + int(
                (pd.Timestamp(fault["end"]) - pd.Timestamp(fault["start"])).total_seconds() // 3600
            ),
            "detected_by_fixed_3h_rule": detected,
            "detection_recall": 1.0 if detected else 0.0,
        })
    write_csv(pd.DataFrame(validation_rows), output_dir / "fault_detection_validation.csv")

    false_positive_count = int(connection.execute(
        """SELECT COUNT(DISTINCT INVERTER_ID)
           FROM relative_alert_blocks
           WHERE INVERTER_ID NOT IN (101, 202, 303)"""
    ).fetchone()[0])
    detected_fault_windows = sum(
        1 for row in validation_rows if row["detected_by_fixed_3h_rule"]
    )
    non_fault_inverter_count = inverter_count - len({
        int(fault["inverter_id"]) for fault in fault_windows
    })
    absolute_flags = int(connection.execute(
        f"""SELECT COUNT(*) FROM hourly_gaps
             WHERE 1 - PERFORMANCE_RATIO >= {BASELINE_GAP_THRESHOLD}
               AND IRRADIANCE > {IRRADIANCE_THRESHOLD_W_M2}"""
    ).fetchone()[0])
    relative_flags = int(connection.execute(
        f"""SELECT COUNT(*) FROM hourly_gaps
             WHERE baseline_gap >= {BASELINE_GAP_THRESHOLD}
               AND IRRADIANCE > {IRRADIANCE_THRESHOLD_W_M2}"""
    ).fetchone()[0])
    fleet_mean_pr = float(connection.execute(
        "SELECT AVG(PERFORMANCE_RATIO) FROM hourly_gaps"
    ).fetchone()[0])
    baseline_absolute_flags = int(connection.execute(
        f"""SELECT COUNT(*) FROM hourly_baseline
             WHERE baseline_pr <= 1 - {BASELINE_GAP_THRESHOLD}
               AND irradiance_w_m2 > {IRRADIANCE_THRESHOLD_W_M2}"""
    ).fetchone()[0])

    reconciliation = reconcile_daily_summary(connection)
    metadata = {
        "project": "Solar Power Plant Inverter Analysis",
        "artifact_version": SCRIPT_VERSION,
        "git_sha": get_git_sha(),
        "weather_source": "Open-Meteo Historical API, ECMWF IFS reanalysis",
        "location": {
            "name": "Calatagan Solar Farm, Philippines",
            "latitude": 13.9155,
            "longitude": 120.6498,
            "timezone": "Asia/Singapore",
            "tilt_degrees": 11,
            "azimuth_degrees": 0,
        },
        "date_range": {
            "start": str(date_bounds[0]),
            "end": str(date_bounds[1]),
        },
        "input": {
            "path": "data/processed/processed_inv_metrics.csv",
            "sha256": sha256_file(METRICS_FILE),
            "bytes": METRICS_FILE.stat().st_size,
        },
        "row_counts": {
            "inverter_hour_rows": total_rows,
            "daytime_rows_with_defined_pr": eligible,
            "inverters": inverter_count,
        },
        "kpis": {
            "fleet_mean_performance_ratio": fleet_mean_pr,
            "absolute_flagged_daytime_hours": absolute_flags,
            "baseline_absolute_flagged_hours": baseline_absolute_flags,
            "baseline_relative_flagged_hours": relative_flags,
            "baseline_relative_alert_blocks": len(alert_blocks),
            "non_fault_inverters_with_alert_blocks": false_positive_count,
            "non_fault_inverter_count": non_fault_inverter_count,
            "non_fault_inverter_false_positive_rate": (
                false_positive_count / non_fault_inverter_count
                if non_fault_inverter_count
                else 0.0
            ),
            "injected_fault_windows_detected": detected_fault_windows,
            "injected_fault_windows_total": len(fault_windows),
            "injected_fault_window_detection_recall": (
                detected_fault_windows / len(fault_windows)
                if fault_windows
                else 0.0
            ),
        },
        "thresholds": {
            "baseline_relative_gap": BASELINE_GAP_THRESHOLD,
            "absolute_pr_gap": BASELINE_GAP_THRESHOLD,
            "irradiance_w_m2_minimum": IRRADIANCE_THRESHOLD_W_M2,
            "fixed_block_hours": BLOCK_HOURS,
            "severity": {"Watch": [0.05, 0.10], "Alert": [0.10, 0.20], "Critical": [0.20, None]},
        },
        "fault_windows": fault_windows,
        "simulation_note": "All inverter metrics are modeled. Faults for inverter IDs 101, 202, and 303 are injected test scenarios, not observed faults.",
        "nighttime_note": "PR is null when irradiance is zero; these rows are excluded from PR analysis, not treated as zero.",
        "sql_query_result_rows": sql_results,
        "daily_summary_reconciliation": reconciliation,
        "reproducibility": {
            "seed": None,
            "randomness_used": False,
            "formula_source": "scripts/transform.py",
            "fault_config": "config/fault_windows.json",
        },
    }
    (output_dir / "fleet_summary.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    connection.close()
    return metadata


def reconcile_daily_summary(connection: duckdb.DuckDBPyConnection) -> dict[str, object]:
    if not EXISTING_DAILY_SUMMARY.exists():
        return {"existing_file_found": False, "matching": None}
    path = str(EXISTING_DAILY_SUMMARY).replace("\\", "/").replace("'", "''")
    connection.execute(
        f"""CREATE VIEW existing_daily_summary AS
        SELECT * FROM read_csv_auto('{path}', header=true)"""
    )
    connection.execute(
        """CREATE VIEW regenerated_daily_summary AS
        SELECT INVERTER_ID, CAST(DATE_TIME AS DATE) AS DATE,
               AVG(PERFORMANCE_RATIO) AS avg_performance_ratio,
               MIN(PERFORMANCE_RATIO) AS min_performance_ratio,
               SUM(CASE WHEN 1 - PERFORMANCE_RATIO >= 0.05 AND IRRADIANCE > 200
                        THEN 1 ELSE 0 END) AS flagged_hours_count,
               SUM(AC_POWER) AS total_ac_energy_kwh
        FROM processed_inv_metrics
        GROUP BY INVERTER_ID, CAST(DATE_TIME AS DATE)"""
    )
    counts = connection.execute(
        """SELECT
            (SELECT COUNT(*) FROM existing_daily_summary),
            (SELECT COUNT(*) FROM regenerated_daily_summary),
            (SELECT COUNT(*) FROM existing_daily_summary AS o
             FULL OUTER JOIN regenerated_daily_summary AS n USING (INVERTER_ID, DATE)
             WHERE o.INVERTER_ID IS NULL OR n.INVERTER_ID IS NULL)"""
    ).fetchone()
    old_rows = int(counts[0])
    regenerated_rows = int(counts[1])
    unmatched = connection.execute(
        """SELECT
            COUNT(*) FILTER (WHERE ABS(o.avg_performance_ratio - n.avg_performance_ratio) > 1e-8),
            COUNT(*) FILTER (WHERE ABS(o.min_performance_ratio - n.min_performance_ratio) > 1e-8),
            COUNT(*) FILTER (WHERE o.flagged_hours_count != n.flagged_hours_count),
            COUNT(*) FILTER (WHERE ABS(o.total_ac_energy_kwh - n.total_ac_energy_kwh) > 1e-6),
            MAX(ABS(o.avg_performance_ratio - n.avg_performance_ratio)),
            MAX(ABS(o.total_ac_energy_kwh - n.total_ac_energy_kwh))
        FROM existing_daily_summary AS o
        FULL OUTER JOIN regenerated_daily_summary AS n USING (INVERTER_ID, DATE)"""
    ).fetchone()
    key_mismatches = old_rows != regenerated_rows or counts[2] > 0
    return {
        "existing_file_found": True,
        "existing_rows": old_rows,
        "regenerated_rows": regenerated_rows,
        "key_mismatches": key_mismatches,
        "rows_differing_by_column": {
            "avg_performance_ratio": int(unmatched[0]),
            "min_performance_ratio": int(unmatched[1]),
            "flagged_hours_count": int(unmatched[2]),
            "total_ac_energy_kwh": int(unmatched[3]),
        },
        "maximum_absolute_difference": {
            "avg_performance_ratio": float(unmatched[4] or 0),
            "total_ac_energy_kwh": float(unmatched[5] or 0),
        },
        "matching": not key_mismatches and not any(unmatched[:4]),
        "logic": "Per-inverter/day aggregates from processed_inv_metrics.csv; absolute PR gap >= 0.05 and irradiance > 200 W/m^2 for flagged hours.",
    }


def artifact_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file())


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate compact static-dashboard data artifacts.")
    parser.add_argument("--check", action="store_true", help="Regenerate in a temporary folder and fail if committed artifacts differ.")
    args = parser.parse_args()
    if not METRICS_FILE.exists():
        parser.error(f"Missing input CSV: {METRICS_FILE}. Run scripts/transform.py first.")

    if args.check:
        with tempfile.TemporaryDirectory(prefix="solar-artifacts-") as temp_dir:
            generated_dir = Path(temp_dir)
            generated_sample = generated_dir / "processed_inv_metrics_sample.csv"
            generate_artifacts(generated_dir, generated_sample)
            expected = {
                path.relative_to(generated_dir): path
                for path in artifact_files(generated_dir)
                if path != generated_sample
            }
            actual = {path.relative_to(ARTIFACT_DIR): path for path in artifact_files(ARTIFACT_DIR)} if ARTIFACT_DIR.exists() else {}
            differences = sorted(
                str(path) for path in expected.keys() | actual.keys()
                if path not in expected or path not in actual
                or (
                    json.loads(expected[path].read_text(encoding="utf-8"))
                    | {"git_sha": None}
                    != json.loads(actual[path].read_text(encoding="utf-8"))
                    | {"git_sha": None}
                    if path.name == "fleet_summary.json"
                    else expected[path].read_bytes() != actual[path].read_bytes()
                )
            )
            sample_path = PROJECT_ROOT / "data/samples/processed_inv_metrics_sample.csv"
            sample_differs = not sample_path.exists() or sample_path.read_bytes() != generated_sample.read_bytes()
            if differences:
                print("Dashboard artifacts differ:")
                print("\n".join(differences))
            if sample_differs:
                print("Sample artifact differs: data/samples/processed_inv_metrics_sample.csv")
            if differences or sample_differs:
                return 1
            print(f"Dashboard artifacts and sample are current ({len(expected)} dashboard files).")
            return 0

    sample_target = PROJECT_ROOT / "data/samples/processed_inv_metrics_sample.csv"
    sample_target.parent.mkdir(parents=True, exist_ok=True)
    metadata = generate_artifacts(ARTIFACT_DIR, sample_target)
    print(f"Published artifacts to {ARTIFACT_DIR}")
    print(f"Input rows: {metadata['row_counts']['inverter_hour_rows']:,}; alert blocks: {metadata['kpis']['baseline_relative_alert_blocks']:,}")
    print(f"Daily summary matches existing CSV: {metadata['daily_summary_reconciliation'].get('matching')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
