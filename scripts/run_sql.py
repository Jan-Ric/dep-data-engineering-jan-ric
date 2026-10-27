from pathlib import Path
import sqlite3
import sys
import time

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = PROJECT_ROOT / "data/processed/processed_inv_metrics.csv"
SAMPLE_INPUT_FILE = PROJECT_ROOT / "data/samples/processed_inv_metrics_sample.csv"
DATABASE_FILE = PROJECT_ROOT / "data/processed/sql_cache.db"
QUERY_DIRECTORY = PROJECT_ROOT / "sql"
OUTPUT_DIRECTORY = PROJECT_ROOT / "output/sql_results"
CHUNK_SIZE = 100_000


def main(arguments=None) -> None:
    if arguments is None:
        arguments = sys.argv[1:]
    assert len(arguments) <= 1, "Usage: python scripts/run_sql.py [--sample]"
    assert len(arguments) == 0 or arguments[0] == "--sample", (
        "The only supported option is --sample"
    )
    input_file = SAMPLE_INPUT_FILE if arguments else INPUT_FILE
    assert input_file.exists(), f"Input file does not exist: {input_file}"

    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    DATABASE_FILE.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DATABASE_FILE) as connection:
        connection.execute("PRAGMA journal_mode = OFF")
        connection.execute("PRAGMA synchronous = OFF")
        connection.execute("DROP TABLE IF EXISTS processed_inv_metrics")

        for chunk_number, chunk in enumerate(
            pd.read_csv(input_file, chunksize=CHUNK_SIZE), start=1
        ):
            write_mode = "replace" if chunk_number == 1 else "append"
            chunk.to_sql(
                "processed_inv_metrics",
                connection,
                if_exists=write_mode,
                index=False,
            )
            print(f"Loaded chunk {chunk_number}: {len(chunk):,} rows")

        print(f"Loaded input: {input_file.relative_to(PROJECT_ROOT)}")

        connection.execute(
            "CREATE INDEX idx_metrics_inverter_datetime "
            "ON processed_inv_metrics (INVERTER_ID, DATE_TIME)"
        )

        query_files = [
            "01_lowest_avg_pr.sql",
            "02_pr_gap_by_month_hour.sql",
            "03_flagged_3h_blocks.sql",
        ]
        for query_file in query_files:
            query_path = QUERY_DIRECTORY / query_file
            output_path = OUTPUT_DIRECTORY / query_file.replace(".sql", ".csv")
            query = query_path.read_text(encoding="utf-8")
            started = time.perf_counter()
            result = pd.read_sql_query(query, connection)
            result.to_csv(output_path, index=False)
            elapsed = time.perf_counter() - started
            print(
                f"{query_file}: {len(result):,} rows in {elapsed:.1f} seconds; "
                f"saved {output_path.relative_to(PROJECT_ROOT)}"
            )


if __name__ == "__main__":
    main()
