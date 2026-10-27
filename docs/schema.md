# Data Schema

## File Lineage

```text
Open-Meteo Historical API JSON
  -> data/raw/open_meteo_raw.json
  -> data/processed/open_meteo_cleaned.csv (8,760 hourly weather rows)
  -> data/processed/open_meteo_computation.csv (7,270,800 inverter-hour rows)
  -> data/processed/processed_inv_metrics.csv (7,270,800 SQL-ready rows)
  -> sql/*.sql -> output/sql_results/*.csv
  -> notebooks/insights.ipynb -> output/figures/*.png
```

The raw JSON is an hourly Open-Meteo extract. `open_meteo_cleaned.csv` keeps the four weather columns after renaming and timestamp conversion. The computation file adds modeled plant/inverter fields and fault-test values. The SQL-ready file is a five-column view of the computation table. Large generated files are local and ignored by Git; run the transform to recreate them.

## Grain and Identifiers

- `processed_inv_metrics`: one row per inverter per hour.
- Composite key: (`INVERTER_ID`, `DATE_TIME`).
- `open_meteo_cleaned.csv`: one row per weather hour; `date_time` is unique.
- `open_meteo_computation.csv`: one row per inverter per hour; 830 inverter IDs are paired with every weather hour.

## Files and Expected Columns

### `data/processed/open_meteo_cleaned.csv`

| Column | Type | Meaning |
| --- | --- | --- |
| `date_time` | datetime | Local hourly timestamp, Asia/Singapore (UTC+8) |
| `ambient_temperature_c` | decimal | Open-Meteo `temperature_2m`, degrees Celsius |
| `wind_speed_10m_ms` | decimal | Open-Meteo `wind_speed_10m`, metres per second |
| `irradiation_w_m2` | decimal | Open-Meteo global tilted irradiance, W/m² |

### `data/processed/open_meteo_computation.csv`

| Column | Type | Meaning |
| --- | --- | --- |
| `date_time` | datetime | Hourly timestamp |
| `ambient_temperature_c` | decimal | Ambient temperature, °C |
| `wind_speed_10m_ms` | decimal | Wind speed, m/s |
| `irradiation_w_m2` | decimal | Plane-of-array irradiance, W/m² |
| `n_module` | decimal | Derived modules per inverter; remains a float |
| `dc_inv_cap` | decimal | Plant-derived DC capacity per inverter, W |
| `module_temperature_c` | decimal | Faiman-model module temperature, °C |
| `internal_temperature_c` | decimal | Simulated baseline internal-temperature proxy, °C |
| `dc_power_kw` | decimal | Modeled DC power, kW |
| `ac_power_kw` | decimal | Modeled AC power after efficiency and 60 kW cap |
| `performance_ratio` | decimal or null | KPI; null when irradiance is zero |
| `inverter_id` | integer | Simulated identifier from 1 through 830 |
| `delta_t_fault` | decimal | Injected temperature offset, °C; zero except test windows |
| `internal_temperature_fault_c` | decimal | Baseline proxy plus injected offset, °C |
| `inverter_efficiency` | decimal | Simulated efficiency after temperature degradation |

### `data/processed/processed_inv_metrics.csv`

| Column | Type | Meaning |
| --- | --- | --- |
| `INVERTER_ID` | integer | Simulated inverter identifier |
| `DATE_TIME` | timestamp | Hourly timestamp |
| `AC_POWER` | decimal | Modeled AC power, kW; at 1-hour resolution numerically equals kWh for the interval |
| `IRRADIANCE` | decimal | Plane-of-array irradiance, W/m² |
| `PERFORMANCE_RATIO` | decimal or null | `AC / (irradiance_kWh_m2 * installed_DC_kWp)` |

### Other useful outputs

- `data/processed/sample_processed_inv_metrics.csv`: first 1,000 rows from the SQL-ready file.
- `data/processed/monthly_inv_summary.csv`: one row per inverter per month, with mean/minimum daytime PR, daytime-hour count, and total modeled AC energy.
- `output/sql_results/*.csv`: compact query results from the full locally regenerated SQL-ready table.
- `output/tables/*.csv`: small retained analysis tables used for review and notebook comparisons.
