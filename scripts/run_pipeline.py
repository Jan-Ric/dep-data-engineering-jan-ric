from pathlib import Path
import sys
import time

import build_insight_tables
import ingest
import insights
import kpis
import run_sql
import segmentation
import transform


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = PROJECT_ROOT / "data" / "raw" / "open_meteo_raw.json"
TRANSFORM_OUTPUTS = [
    PROJECT_ROOT / "data" / "processed" / "open_meteo_cleaned.csv",
    PROJECT_ROOT / "data" / "processed" / "open_meteo_computation.csv",
    PROJECT_ROOT / "data" / "processed" / "processed_inv_metrics.csv",
    PROJECT_ROOT / "data" / "processed" / "sample_processed_inv_metrics.csv",
    PROJECT_ROOT / "data" / "processed" / "monthly_inv_summary.csv",
]
OUTPUT_DIRECTORIES = [
    PROJECT_ROOT / "output" / "tables",
    PROJECT_ROOT / "output" / "sql_results",
    PROJECT_ROOT / "output" / "figures",
]
SQL_CACHE_FILE = PROJECT_ROOT / "data" / "processed" / "sql_cache.db"
STEPS = [
    ("ingest", ingest.main),
    ("transform", transform.main),
    ("run_sql", lambda: run_sql.main([])),
    ("build_insight_tables", build_insight_tables.main),
    ("kpis", kpis.main),
    ("segmentation", segmentation.main),
    ("insights", insights.main),
]


def main() -> int:
    skip_ingest = "skip-ingest" in sys.argv[1:]
    skip_transform = "skip-transform" in sys.argv[1:]

    if skip_ingest and not RAW_FILE.is_file():
        print(f"Cannot skip ingest: required raw file is missing: {RAW_FILE}")
        return 1
    if skip_transform:
        missing_outputs = [path for path in TRANSFORM_OUTPUTS if not path.is_file()]
        if missing_outputs:
            print("Cannot skip transform: required processed files are missing:")
            for path in missing_outputs:
                print(f"  {path}")
            return 1

    try:
        for step_number, (step_name, step_main) in enumerate(STEPS, start=1):
            print(f"Step {step_number} of {len(STEPS)}: {step_name}")
            should_skip = (
                step_name == "ingest" and skip_ingest
            ) or (step_name == "transform" and skip_transform)
            if should_skip:
                print(f"Skipped {step_name}")
                continue

            started = time.perf_counter()
            try:
                step_main()
            except Exception as error:
                print(f"Step {step_number} of {len(STEPS)} failed ({step_name}): {error}")
                return 1
            elapsed = time.perf_counter() - started
            print(f"Completed {step_name} in {elapsed:.1f} seconds")
    except Exception as error:
        print(f"Pipeline stopped: {error}")
        return 1

    generated_files = []
    generated_files.extend(path for path in TRANSFORM_OUTPUTS if path.is_file())
    if SQL_CACHE_FILE.is_file():
        generated_files.append(SQL_CACHE_FILE)
    for directory in OUTPUT_DIRECTORIES:
        if directory.is_dir():
            generated_files.extend(path for path in directory.rglob("*") if path.is_file())

    print("Generated output files:")
    for path in sorted(set(generated_files)):
        relative_path = path.relative_to(PROJECT_ROOT)
        print(f"{relative_path}: {path.stat().st_size:,} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())