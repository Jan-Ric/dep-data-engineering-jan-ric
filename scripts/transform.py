from pathlib import Path
import json
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = PROJECT_ROOT / "data/raw/open_meteo_raw.json"
WEATHER_FILE = PROJECT_ROOT / "data/processed/open_meteo_cleaned.csv"
COMPUTATION_FILE = PROJECT_ROOT / "data/processed/open_meteo_computation.csv"
MAIN_INV_FILE = PROJECT_ROOT / "data/processed/processed_inv_metrics.csv"
DAILY_SUMMARY_FILE = PROJECT_ROOT / "data/processed/daily_inv_summary.csv"


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


def solar_inv_engr_features(df_features) -> pd.DataFrame:
    # Formula A: Plant Sizing Constants & Derivations
    dc_plant = 63_300_000  # Total plant DC Capacity (Wp)
    p_stc = 315            # Module rated power at STC (Wp)
    n_inv = 830            # Number of inverters
    
    df_features["n_module"] = (dc_plant / n_inv) / p_stc
    df_features["dc_inv_cap"] = dc_plant / n_inv  # Watts

    # Formula B: Module Temperature Constants & Faiman Model
    t_amb = df_features["ambient_temperature_c"]
    ws = df_features["wind_speed_10m_ms"]
    g_poa = df_features["irradiation_w_m2"]
    u_0 = 25.0
    u_1 = 6.84

    df_features["module_temperature_c"] = t_amb + (g_poa / (u_0 + u_1 * ws))

    # Formula E: Baseline internal temperature proxy
    module_temperature_rise = df_features["module_temperature_c"] - t_amb
    df_features["internal_temperature_c"] = t_amb + module_temperature_rise

    # Formula C: Module DC Power Calculation (Output in kW)
    gamma_p = -0.41  # Temperature coefficient of Pmax (%/°C)
    p_stc_total = p_stc * df_features["n_module"]
    
    df_features["dc_power_kw"] = (
        p_stc_total 
        * (g_poa / 1000.0) 
        * (1 + (gamma_p / 100.0) * (df_features["module_temperature_c"] - 25))
    ) / 1000.0  # Convert W to kW

    # Formula D: Inverter AC Output Calculation (Output in kW)
    eta_inv = 0.983     # Euro-eta inverter efficiency
    p_ac_rated = 60.0   # Rated AC output power (kW)

    df_features["ac_power_kw"] = (df_features["dc_power_kw"] * eta_inv).clip(upper=p_ac_rated)

    # 📊 Key Formula: Performance Ratio (PR) Calculation
    # Convert irradiance from W/m² to kWh/m² and DC capacity from W to kWp
    irradiation_kwh_m2 = g_poa / 1000.0
    dc_inv_kwp = df_features["dc_inv_cap"] / 1000.0

    df_features["performance_ratio"] = df_features["ac_power_kw"] / (irradiation_kwh_m2 * dc_inv_kwp)

    return df_features


def create_inverter_metrics(df_features) -> pd.DataFrame:
    n_inv = 830
    eta_inv = 0.983
    beta = 0.01
    t_threshold = 45.0

    inverter_ids = pd.DataFrame({"inverter_id": range(1, n_inv + 1)})
    df_features = df_features.assign(key=1)
    inverter_ids = inverter_ids.assign(key=1)
    df_metrics = df_features.merge(inverter_ids, on="key").drop(columns="key")

    # Formula F: Apply faults only to selected inverter and time windows
    df_metrics["delta_t_fault"] = 0.0
    fault_windows = [
        (101, "2025-03-15 10:00:00", "2025-03-15 12:00:00", 4.0),
        (202, "2025-06-20 10:00:00", "2025-06-20 12:00:00", 8.0),
        (303, "2025-09-10 10:00:00", "2025-09-10 12:00:00", 12.0),
    ]

    for inverter_id, start_time, end_time, delta_t_fault in fault_windows:
        fault_mask = (
            (df_metrics["inverter_id"] == inverter_id)
            & (df_metrics["date_time"] >= pd.Timestamp(start_time))
            & (df_metrics["date_time"] <= pd.Timestamp(end_time))
        )
        df_metrics.loc[fault_mask, "delta_t_fault"] = delta_t_fault

    df_metrics["internal_temperature_fault_c"] = (
        df_metrics["internal_temperature_c"] + df_metrics["delta_t_fault"]
    )
    df_metrics["inverter_efficiency"] = eta_inv * (
        1
        - beta
        * (df_metrics["internal_temperature_fault_c"] - t_threshold).clip(lower=0)
    )

    df_metrics["ac_power_kw"] = (
        df_metrics["dc_power_kw"] * df_metrics["inverter_efficiency"]
    ).clip(upper=60.0)

    irradiation_kwh_m2 = df_metrics["irradiation_w_m2"] / 1000.0
    dc_inv_kwp = df_metrics["dc_inv_cap"] / 1000.0
    df_metrics["performance_ratio"] = df_metrics["ac_power_kw"] / (
        irradiation_kwh_m2 * dc_inv_kwp
    )

    return df_metrics


def create_query_dataset(df_metrics) -> pd.DataFrame:
    return df_metrics.rename(
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


def create_daily_summary(df_metrics) -> pd.DataFrame:
    all_metrics = df_metrics.copy()
    all_metrics["date"] = all_metrics["date_time"].dt.date

    daytime_metrics = df_metrics[df_metrics["irradiation_w_m2"] > 0].copy()
    daytime_metrics["date"] = daytime_metrics["date_time"].dt.date
    daytime_metrics["underperforming"] = (
        (1 - daytime_metrics["performance_ratio"] >= 0.05)
        & (daytime_metrics["irradiation_w_m2"] > 200)
    )

    summary = (
        daytime_metrics.groupby(["inverter_id", "date"], as_index=False)
        .agg(
            avg_performance_ratio=("performance_ratio", "mean"),
            min_performance_ratio=("performance_ratio", "min"),
            flagged_hours_count=("underperforming", "sum"),
        )
    )
    energy = (
        all_metrics.groupby(["inverter_id", "date"], as_index=False)
        .agg(total_ac_energy_kwh=("ac_power_kw", "sum"))
    )
    return (
        summary.merge(energy, on=["inverter_id", "date"])
        .rename(columns={"inverter_id": "INVERTER_ID", "date": "DATE"})
    )


def main() -> None:
    # 1. Load raw data and perform basic data exploration
    df_raw = load_raw_data()

    # 2. Feature Engineering: Compute all inverter parameters and PR
    df_features = solar_inv_engr_features(df_raw)
    df_metrics = create_inverter_metrics(df_features)

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
    assert df_metrics["delta_t_fault"].isin([0.0, 4.0, 8.0, 12.0]).all(), "Unexpected fault offset found"
    
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

    daily_summary = create_daily_summary(df_metrics)
    daily_summary.to_csv(DAILY_SUMMARY_FILE, index=False)
    print(f"Saved daily summary to {DAILY_SUMMARY_FILE}")


if __name__ == "__main__":
    main()