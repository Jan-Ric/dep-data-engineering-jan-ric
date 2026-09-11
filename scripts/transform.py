from pathlib import Path
import json
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = PROJECT_ROOT / "data/raw/open_meteo_raw.json"
OUTPUT_FILE = PROJECT_ROOT / "data/processed/open_meteo_cleaned.csv"
COMPUTATION_FILE = PROJECT_ROOT / "data/processed/open_meteo_computation.csv"


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
    p_stc = 314            # Module rated power at STC (Wp)
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


def main() -> None:
    # 1. Load raw data and perform basic data exploration
    df_raw = load_raw_data()

    # 2. Feature Engineering: Compute all inverter parameters and PR
    df_features = solar_inv_engr_features(df_raw)

    # 3. Data Profiling
    print("First five rows:")
    print(df_features.head())
    print("\nDataFrame info:")
    df_features.info()
    print("\nDescriptive statistics:")
    print(df_features.describe())
    print("\nRows by date:")
    print(df_features["date_time"].dt.date.value_counts().sort_index().head())
    print("\nMissing values:")
    print(df_features.isnull().sum())

    # 4. Validation Profile: Check for anomalies and outliers in the data
    # Check physical limits of raw weather data
    assert df_features["irradiation_w_m2"].min() >= 0, "Unexpected negative irradiance value found"
    assert df_features["ambient_temperature_c"].min() >= 10, "Low Ambient temperature - Out of range"
    assert df_features["ambient_temperature_c"].max() <= 50, "High Ambient temperature - Out of range"
    
    # Check calculated Performance Ratio (irradiance > 0 only)
    daytime_data = df_features[df_features["irradiation_w_m2"] > 0]
    assert daytime_data["performance_ratio"].min() >= 0, "Unexpected Zero or Near-zero PR - Out of range"
    assert daytime_data["performance_ratio"].max() <= 1.5, "Too high PR - Out of range"

    print("Validation done: All checks passed successfully.")
    
    # 5. Save the outputs
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Save base cleaned dataset
    df_raw.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved cleaned dataset to {OUTPUT_FILE}")
    
    # Save inverter performance computation dataset
    df_features.to_csv(COMPUTATION_FILE, index=False)
    print(f"Saved computed dataset to {COMPUTATION_FILE}")


if __name__ == "__main__":
    main()