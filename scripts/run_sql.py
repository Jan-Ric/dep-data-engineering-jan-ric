import csv
import sqlite3
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
METRICS_FILE = PROJECT_ROOT / "data/processed/processed_inv_metrics.csv"
SQL_DIR = PROJECT_ROOT / "sql"
OUTPUT_DIR = PROJECT_ROOT / "output/sql_results"
BATCH_SIZE = 50_000


def load_metrics(connection: sqlite3.Connection) -> None:
    connection.execute(
        """CREATE TABLE processed_inv_metrics (
            INVERTER_ID INTEGER NOT NULL,
            DATE_TIME TEXT NOT NULL,
            AC_POWER REAL NOT NULL,
            IRRADIANCE REAL NOT NULL,
            PERFORMANCE_RATIO REAL
        )"""
    )
    insert_sql = """INSERT INTO processed_inv_metrics VALUES (?, ?, ?, ?, ?)"""
    with METRICS_FILE.open(encoding="utf-8", newline="") as file:
        rows = csv.DictReader(file)
        batch = []
        for row in rows:
            batch.append((
                int(row["INVERTER_ID"]),
                row["DATE_TIME"],
                float(row["AC_POWER"]),
                float(row["IRRADIANCE"]),
                float(row["PERFORMANCE_RATIO"]) if row["PERFORMANCE_RATIO"] else None,
            ))
            if len(batch) >= BATCH_SIZE:
                connection.executemany(insert_sql, batch)
                batch.clear()
        if batch:
            connection.executemany(insert_sql, batch)
    connection.commit()


def save_query_results(connection: sqlite3.Connection) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for sql_file in sorted(SQL_DIR.glob("*.sql")):
        query = sql_file.read_text(encoding="utf-8")
        cursor = connection.execute(query)
        output_file = OUTPUT_DIR / f"{sql_file.stem}.csv"
        with output_file.open("w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file, lineterminator="\n")
            writer.writerow([column[0] for column in cursor.description])
            writer.writerows(cursor)
        print(f"Saved {output_file.relative_to(PROJECT_ROOT)}")


def main() -> None:
    if not METRICS_FILE.exists():
        raise FileNotFoundError(
            f"Missing {METRICS_FILE.relative_to(PROJECT_ROOT)}; run scripts/transform.py first."
        )
    with tempfile.TemporaryDirectory(prefix="solar-sql-") as temporary_directory:
        database_file = Path(temporary_directory) / "metrics.db"
        connection = sqlite3.connect(database_file)
        connection.execute("PRAGMA journal_mode = OFF")
        connection.execute("PRAGMA synchronous = OFF")
        print("Loading processed inverter metrics into a temporary SQLite database...")
        load_metrics(connection)
        print("Running the three documented queries...")
        save_query_results(connection)
        connection.close()
    print("SQLite work is complete; temporary database removed.")


if __name__ == "__main__":
    main()
