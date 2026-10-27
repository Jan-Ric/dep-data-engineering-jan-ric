from pathlib import Path
from datetime import datetime
import requests
import json

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data/raw"
OUTPUT_FILE = RAW_DIR / "open_meteo_raw.json"
API_URL = "https://archive-api.open-meteo.com/v1/archive"
START_DATE = "2025-01-01"
END_DATE = "2025-12-31"
EXPECTED_HOURS = int(
    (datetime(2026, 1, 1) - datetime(2025, 1, 1)).total_seconds() / 3600
)
WEATHER_FIELDS = [
    "temperature_2m",
    "wind_speed_10m",
    "global_tilted_irradiance",
]
REQUEST_TIMEOUT_SECONDS = 30  # seconds
REQUEST_PARAMS = {
    "latitude": 13.9155,
    "longitude": 120.6498,
    "start_date": START_DATE,
    "end_date": END_DATE,
    "hourly": ",".join(WEATHER_FIELDS),
    "models": "ecmwf_ifs",
    "timezone": "Asia/Singapore",
    "wind_speed_unit": "ms",
    "tilt": 11,
    "azimuth": 0,
}
REQUEST_HEADERS = {"Accept": "application/json"}

def fetch_data():
    response = requests.get(
        API_URL,
        params=REQUEST_PARAMS,
        headers=REQUEST_HEADERS,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()

def validate_payload(payload):
    for field in WEATHER_FIELDS:
        values = payload["hourly"][field]
        assert len(values) == EXPECTED_HOURS, (
            f"{field} has {len(values)} rows, expected {EXPECTED_HOURS}"
        )
        null_count = sum(value is None for value in values)
        assert null_count == 0, f"{field} contains {null_count} null readings"

def main():
    payload = fetch_data()
    validate_payload(payload)

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(payload, indent=4), encoding="utf-8")
    print(f"Saved raw extract to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()