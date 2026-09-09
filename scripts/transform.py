from pathlib import Path
import json

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = PROJECT_ROOT / "data/raw/open_meteo_raw.json"
OUTPUT_FILE = PROJECT_ROOT / "data/processed/open_meteo_cleaned.csv"


def load_raw_data() -> pd.DataFrame:
    with RAW_FILE.open(encoding="utf-8") as file:
        payload = json.load(file)

    hourly = payload["hourly"]
    df = pd.DataFrame(hourly)
    df = df.rename(
        columns={
            "time": "date_time",
            "temperature_2m": "ambient_temperature_c",
            "wind_speed_10m": "wind_speed_10m_ms",
            "global_tilted_irradiance": "irradiation_w_m2",
        }
    )
    df["date_time"] = pd.to_datetime(df["date_time"])
    return df.sort_values("date_time").reset_index(drop=True)


def main() -> None:
    df = load_raw_data()

    print("First five rows:")
    print(df.head())
    print("\nDataFrame info:")
    df.info()
    print("\nDescriptive statistics:")
    print(df.describe())
    print("\nRows by date:")
    print(df["date_time"].dt.date.value_counts().sort_index().head())
    print("\nMissing values:")
    print(df.isnull().sum())

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved cleaned dataset to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()