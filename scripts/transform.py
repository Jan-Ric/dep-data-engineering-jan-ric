from pathlib import Path
import json
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = PROJECT_ROOT / "data/raw/open_meteo_raw.json"
WEATHER_FILE = PROJECT_ROOT / "data/processed/open_meteo_cleaned.csv"
COMPUTATION_FILE = PROJECT_ROOT / "data/processed/open_meteo_computation.csv"
MAIN_INV_FILE = PROJECT_ROOT / "data/processed/processed_inv_metrics.csv"
SAMPLE_FILE = PROJECT_ROOT / "data/processed/sample_processed_inv_metrics.csv"
MONTHLY_SUMMARY_FILE = PROJECT_ROOT / "data/processed/monthly_inv_summary.csv"

DC_PLANT_WP = 63_300_000  # watts peak
INVERTER_COUNT = 830  # inverters
MODULE_RATED_POWER_WP = 315  # watts peak per module
FAIMAN_U0 = 25.0  # W/(m^2 * degree C)
FAIMAN_U1 = 6.84  # W/(m^2 * degree C per m/s)
MODULE_TEMPERATURE_COEFFICIENT_PERCENT = -0.41  # percent per degree C
INVERTER_EFFICIENCY = 0.983  # unitless Euro efficiency
INVERTER_RATED_AC_KW = 60.0  # kW
FAULT_DEGRADATION_PER_C = 0.01  # fractional efficiency loss per degree C
FAULT_TEMPERATURE_THRESHOLD_C = 45.0  # degrees C

FAULT_WINDOWS = [
    {
        "inverter_id": 101,
        "start": "2025-03-15 10:00:00",
        "end": "2025-03-15 12:00:00",
        "delta_t_fault_c": 4.0,
    },
    {
        "inverter_id": 202,
        "start": "2025-06-20 10:00:00",
        "end": "2025-06-20 12:00:00",
        "delta_t_fault_c": 8.0,
    },
    {
        "inverter_id": 303,
        "start": "2025-09-10 10:00:00",
        "end": "2025-09-10 12:00:00",
        "delta_t_fault_c": 12.0,
    },
]

WEATHER_COLUMNS = [
    "date_time",
    "ambient_temperature_c",
    "wind_speed_10m_ms",
    "irradiation_w_m2",
]
COMPUTATION_COLUMNS = WEATHER_COLUMNS + [
    "n_module",
    "dc_inv_cap",
    "module_temperature_c",
    "internal_temperature_c",
    "dc_power_kw",
    "ac_power_kw",
    "performance_ratio",
    "inverter_id",
    "delta_t_fault",
    "internal_temperature_fault_c",
    "inverter_efficiency",
]
METRICS_COLUMNS = [
    "INVERTER_ID",
    "DATE_TIME",
    "AC_POWER",
    "IRRADIANCE",
    "PERFORMANCE_RATIO",
]


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


def validate_missing_values(df_raw: pd.DataFrame, df_metrics: pd.DataFrame) -> None:
    assert list(df_raw.columns) == WEATHER_COLUMNS, (
        f"Unexpected cleaned weather columns: {list(df_raw.columns)}"
    )
    assert list(df_metrics.columns) == COMPUTATION_COLUMNS, (
        f"Unexpected computation columns: {list(df_metrics.columns)}"
    )
    assert len(df_raw) == 8760, f"Expected 8760 hourly weather rows, got {len(df_raw)}"
    expected_rows = INVERTER_COUNT * len(df_raw)
    assert len(df_metrics) == expected_rows, (
        f"Expected {expected_rows} inverter-hour rows, got {len(df_metrics)}"
    )
    assert pd.api.types.is_datetime64_any_dtype(df_metrics["date_time"]), (
        "date_time must have a datetime dtype"
    )
    assert pd.api.types.is_integer_dtype(df_metrics["inverter_id"]), (
        "inverter_id must have an integer dtype"
    )

    raw_required_columns = [
        "date_time",
        "ambient_temperature_c",
        "wind_speed_10m_ms",
        "irradiation_w_m2",
    ]
    raw_missing = df_raw[raw_required_columns].isna().sum()
    unexpected_raw_missing = raw_missing[raw_missing > 0]
    assert unexpected_raw_missing.empty, (
        "Missing required weather values: "
        f"{unexpected_raw_missing.to_dict()}"
    )

    calculated_columns = [
        "n_module",
        "dc_inv_cap",
        "module_temperature_c",
        "internal_temperature_c",
        "dc_power_kw",
        "ac_power_kw",
        "inverter_id",
        "delta_t_fault",
        "internal_temperature_fault_c",
        "inverter_efficiency",
    ]
    calculated_missing = df_metrics[calculated_columns].isna().sum()
    unexpected_calculated_missing = calculated_missing[calculated_missing > 0]
    assert unexpected_calculated_missing.empty, (
        "Missing calculated values: "
        f"{unexpected_calculated_missing.to_dict()}"
    )

    assert df_metrics["ac_power_kw"].between(
        0, INVERTER_RATED_AC_KW
    ).all(), "ac_power_kw must be between 0 and 60 kW"
    allowed_fault_offsets = {0.0} | {
        float(fault["delta_t_fault_c"]) for fault in FAULT_WINDOWS
    }
    assert set(df_metrics["delta_t_fault"].unique()).issubset(allowed_fault_offsets), (
        f"Unexpected fault offset found: {sorted(df_metrics['delta_t_fault'].unique())}"
    )

    daytime_data = df_metrics[df_metrics["irradiation_w_m2"] > 0]
    nighttime_data = df_metrics[df_metrics["irradiation_w_m2"] == 0]
    assert daytime_data["performance_ratio"].notna().all(), (
        "Performance ratio is missing for a daylight row"
    )
    assert nighttime_data["performance_ratio"].isna().all(), (
        "Performance ratio must be undefined when irradiance is zero"
    )

    print(
        "Cleaning decisions: no values imputed; "
        f"{len(nighttime_data)} nighttime rows have intentionally undefined "
        "performance_ratio values; all other required values are present."
    )


def add_weather_features(df_weather: pd.DataFrame) -> pd.DataFrame:
    df_features = df_weather.copy()
    df_features["n_module"] = (
        DC_PLANT_WP / INVERTER_COUNT
    ) / MODULE_RATED_POWER_WP
    df_features["dc_inv_cap"] = DC_PLANT_WP / INVERTER_COUNT

    ambient_temperature = df_features["ambient_temperature_c"]
    wind_speed = df_features["wind_speed_10m_ms"]
    irradiance = df_features["irradiation_w_m2"]
    df_features["module_temperature_c"] = ambient_temperature + (
        irradiance / (FAIMAN_U0 + FAIMAN_U1 * wind_speed)
    )
    module_temperature_rise = (
        df_features["module_temperature_c"] - ambient_temperature
    )
    df_features["internal_temperature_c"] = (
        ambient_temperature + module_temperature_rise
    )

    module_stc_power = MODULE_RATED_POWER_WP * df_features["n_module"]
    df_features["dc_power_kw"] = (
        module_stc_power
        * (irradiance / 1000.0)
        * (
            1
            + (MODULE_TEMPERATURE_COEFFICIENT_PERCENT / 100.0)
            * (df_features["module_temperature_c"] - 25)
        )
    ) / 1000.0
    return df_features


def create_inverter_metrics(df_features) -> pd.DataFrame:
    inverter_ids = pd.DataFrame({"inverter_id": range(1, INVERTER_COUNT + 1)})
    # A cross join pairs every weather hour with every inverter.
    df_metrics = df_features.merge(inverter_ids, how="cross")

    # Formula F: Apply faults only to selected inverter and time windows
    df_metrics["delta_t_fault"] = 0.0
    for fault in FAULT_WINDOWS:
        inverter_id = fault["inverter_id"]
        start_time = fault["start"]
        end_time = fault["end"]
        delta_t_fault = fault["delta_t_fault_c"]
        fault_mask = (
            (df_metrics["inverter_id"] == inverter_id)
            & (df_metrics["date_time"] >= pd.Timestamp(start_time))
            & (df_metrics["date_time"] <= pd.Timestamp(end_time))
        )
        df_metrics.loc[fault_mask, "delta_t_fault"] = delta_t_fault

    df_metrics["internal_temperature_fault_c"] = (
        df_metrics["internal_temperature_c"] + df_metrics["delta_t_fault"]
    )
    df_metrics["inverter_efficiency"] = INVERTER_EFFICIENCY * (
        1
        - FAULT_DEGRADATION_PER_C
        * (
            df_metrics["internal_temperature_fault_c"]
            - FAULT_TEMPERATURE_THRESHOLD_C
        ).clip(lower=0)
    )

    df_metrics["ac_power_kw"] = (
        df_metrics["dc_power_kw"] * df_metrics["inverter_efficiency"]
    ).clip(upper=INVERTER_RATED_AC_KW)

    irradiation_kwh_m2 = df_metrics["irradiation_w_m2"] / 1000.0
    dc_inv_kwp = df_metrics["dc_inv_cap"] / 1000.0
    df_metrics["performance_ratio"] = df_metrics["ac_power_kw"] / (
        irradiation_kwh_m2 * dc_inv_kwp
    )

    return df_metrics[COMPUTATION_COLUMNS]


def create_query_dataset(df_metrics) -> pd.DataFrame:
    query_dataset = df_metrics.rename(
        columns={
            "inverter_id": "INVERTER_ID",
            "date_time": "DATE_TIME",
            "ac_power_kw": "AC_POWER",
            "irradiation_w_m2": "IRRADIANCE",
            "performance_ratio": "PERFORMANCE_RATIO",
        }
    )[
        [
            "INVERTER_ID",
            "DATE_TIME",
            "AC_POWER",
            "IRRADIANCE",
            "PERFORMANCE_RATIO",
        ]
    ]
    assert list(query_dataset.columns) == METRICS_COLUMNS, (
        f"Unexpected SQL-ready columns: {list(query_dataset.columns)}"
    )
    return query_dataset


def main() -> None:
    # 1. Load raw data and perform basic data exploration
    df_raw = load_raw_data()

    # 2. Feature Engineering: Compute all inverter parameters and PR
    df_features = add_weather_features(df_raw)
    df_metrics = create_inverter_metrics(df_features)

    validate_missing_values(df_raw, df_metrics)

    # 3. Data Profiling
    print("First five rows:")
    print(df_metrics.head())
    print("\nDataFrame info:")
    df_metrics.info()
    print("\nDescriptive statistics:")
    print(df_metrics.describe())
    print("\nRows by date:")
    print(df_metrics["date_time"].dt.date.value_counts().sort_index().head())
    print("\nMissing values:")
    print(df_metrics.isnull().sum())

    # 4. Validation Profile: Check for anomalies and outliers in the data
    # Check physical limits of raw weather data
    assert df_metrics["irradiation_w_m2"].min() >= 0, "Unexpected negative irradiance value found"
    assert df_metrics["ambient_temperature_c"].min() >= 10, "Low Ambient temperature - Out of range"
    assert df_metrics["ambient_temperature_c"].max() <= 50, "High Ambient temperature - Out of range"
    assert df_metrics[["inverter_id", "date_time"]].duplicated().sum() == 0, "Duplicate inverter timestamp found"
    # Check calculated Performance Ratio (irradiance > 0 only)
    daytime_data = df_metrics[df_metrics["irradiation_w_m2"] > 0]
    assert daytime_data["performance_ratio"].notna().all(), "Missing daytime performance ratio found"
    assert daytime_data["performance_ratio"].min() >= 0, "Unexpected Zero or Near-zero PR - Out of range"
    assert daytime_data["performance_ratio"].max() <= 1.5, "Too high PR - Out of range"

    print("Validation done: All checks passed successfully.")
    
    # 5. Save the outputs
    WEATHER_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Save base cleaned dataset
    df_raw.to_csv(WEATHER_FILE, index=False)
    print(f"\nSaved cleaned dataset to {WEATHER_FILE}")
    
    # Save inverter performance computation dataset
    df_metrics.to_csv(COMPUTATION_FILE, index=False)
    print(f"Saved computed dataset to {COMPUTATION_FILE}")

    query_dataset = create_query_dataset(df_metrics)
    query_dataset.to_csv(MAIN_INV_FILE, index=False)
    print(f"Saved query dataset to {MAIN_INV_FILE}")

    query_dataset.head(1000).to_csv(SAMPLE_FILE, index=False)
    print(f"Saved 1,000-row sample to {SAMPLE_FILE}")

    monthly_summary = query_dataset.assign(
        MONTH=pd.to_datetime(query_dataset["DATE_TIME"]).dt.to_period("M").astype(str)
    ).groupby(["INVERTER_ID", "MONTH"], as_index=False).agg(
        mean_performance_ratio=("PERFORMANCE_RATIO", "mean"),
        min_performance_ratio=("PERFORMANCE_RATIO", "min"),
        daytime_hours=("PERFORMANCE_RATIO", "count"),
        total_ac_energy_kwh=("AC_POWER", "sum"),
    )
    expected_monthly_columns = [
        "INVERTER_ID",
        "MONTH",
        "mean_performance_ratio",
        "min_performance_ratio",
        "daytime_hours",
        "total_ac_energy_kwh",
    ]
    assert list(monthly_summary.columns) == expected_monthly_columns, (
        f"Unexpected monthly summary columns: {list(monthly_summary.columns)}"
    )
    monthly_summary.to_csv(MONTHLY_SUMMARY_FILE, index=False)
    print(f"Saved monthly inverter summary to {MONTHLY_SUMMARY_FILE}")


if __name__ == "__main__":
    main()