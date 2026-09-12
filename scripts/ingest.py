from pathlib import Path
from datetime import datetime
import requests
import json

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data/raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

def fetch_data():
    url = "https://archive-api.open-meteo.com/v1/archive"
    
    # Parameters cleanly separated as a dictionary
    params = {
        "latitude": 13.9155,
        "longitude": 120.6498,
        "start_date": "2025-01-01",
        "end_date": "2025-12-31",
        "hourly": "temperature_2m,wind_speed_10m,global_tilted_irradiance",
        "models": "ecmwf_ifs",
        "timezone": "Asia/Singapore",
        "wind_speed_unit": "ms",
        "tilt": 11,
        "azimuth": 0
    }
    headers = {"Accept": "application/json"}

    response = requests.get(url, params=params, headers=headers, timeout=30)
    response.raise_for_status() # Fails fast if the API is down
    return response.json()

def main():
    source_name = "open_meteo"
    payload = fetch_data()
    expected_hours = int(
        (datetime(2026, 1, 1) - datetime(2025, 1, 1)).total_seconds() / 3600
    )
    weather_fields = ["temperature_2m", "wind_speed_10m", "global_tilted_irradiance"]
    # Fail before saving because this pipeline has no fallback for gappy API responses.
    for field in weather_fields:
        values = payload["hourly"][field]
        assert len(values) == expected_hours, (
            f"{field} has {len(values)} rows, expected {expected_hours}"
        )
        null_count = sum(value is None for value in values)
        assert null_count == 0, f"{field} contains {null_count} null readings"
    output_file = RAW_DIR / f"{source_name}_raw.json"
    
    # Save as properly formatted JSON
    output_file.write_text(json.dumps(payload, indent=4), encoding="utf-8")
    print(f"Saved raw extract to {output_file}")

if __name__ == "__main__":
    main()