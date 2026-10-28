# Methodology and Sources

## Scope and KPI

Phase 1 asks: **When and where are those inverters that have negative performance ratio gaps in a solar power plant?** The primary audience is an Operations and Maintenance Engineer; the secondary audience is a Solar Energy Power Plant Supervisor.

The KPI is hourly Performance Ratio:

$$
PR = \dfrac{AC}{I \times DC}
$$

Here, AC is modeled AC energy for the one-hour interval (AC power in kW is numerically equal to kWh over one hour); I is plane-of-array irradiance converted from W/m² to kWh/m² using the one-hour interval; DC is the plant-derived installed DC capacity per inverter in kWp.

## Formula Flow

```text
A + B -> C -> F-adjusted D -> PR
B -> E -> F (test-only injected temperature fault)
```

### A. Plant sizing

$$
N_{module} = \dfrac{DC_{plant}/N_{inv}}{P_{STC}}
\qquad
DC_{inv} = \dfrac{DC_{plant}}{N_{inv}}
$$

The code uses 63,300,000 Wp plant DC capacity, 830 inverters, and a 315 Wp module rating. `n_module` is stored as a float, not rounded to the integer 242. The requested approximate note is about 242.4, but the configured formula evaluates to about 242.1113; `dc_inv_cap` is about 76,265.06 W per inverter. No rounding is applied, and the numeric model output is unchanged.

### B. Module temperature, Faiman model

$$
T_{module} = T_{amb} + \dfrac{G_{POA}}{u_0 + u_1 WS}
$$

The implementation uses $u_0=25.0$ W/(m²·°C) and $u_1=6.84$ W/(m²·°C per m/s). Inputs are ambient temperature, POA irradiance, and 10 m wind speed.

### C. DC power, PVWatts-style equation

$$
P_{dc} = P_{module,STC,total} \times \dfrac{G_{POA}}{1000}
\times \left[1 + \dfrac{\gamma_p}{100}(T_{module}-25)\right]
$$

The module temperature coefficient is −0.41%/°C. The result is converted from W to kW. The implementation uses the derived floating-point module count.

### D. AC power

$$
P_{AC} = \min(P_{dc} \times \eta_{inv}, 60\text{ kW})
$$

The normal inverter efficiency is 0.983 (Euro efficiency). In test fault windows, efficiency is adjusted by Formula F before AC output is calculated.

### E. Baseline internal-temperature proxy

$$
T_{internal} = T_{amb} + (T_{module}-T_{amb})
$$

This equals the modeled module temperature and is only a proxy. It is not measured inverter telemetry.

### F. Test-only injected fault

$$
T_{internal,fault} = T_{internal} + \Delta T_{fault}
$$

$$
\eta_{inv,degraded} = \eta_{inv}\left[1 - \beta\max(0,T_{internal,fault}-T_{threshold})\right]
$$

The demonstration uses $\beta=0.01$ and a 45°C threshold. The configured Formula F windows, imported by downstream scripts from `scripts/transform.py`, are:

| Inverter | Date | Hours | Irradiance per hour (W/m²) | Baseline internal temperature per hour (°C) | $\Delta T_{fault}$ (°C) | Predicted mean `pr_gap` | Target |
|---:|---|---|---|---|---:|---:|---|
| 101 | 2025-01-22 | 14:00–16:00 | 626.2, 468.1, 396.4 | 39.03, 36.64, 34.99 | 16.14 | 0.07497 | Watch |
| 118 | 2025-02-21 | 14:00–16:00 | 660.4, 583.0, 330.2 | 39.13, 37.83, 33.53 | 16.21 | 0.07498 | Watch |
| 202 | 2025-03-11 | 15:00–17:00 | 673.8, 496.8, 309.0 | 42.72, 39.53, 36.57 | 13.53 | 0.07496 | Watch |
| 303 | 2025-04-17 | 15:00–17:00 | 693.4, 521.1, 302.5 | 43.90, 40.96, 36.39 | 12.77 | 0.07500 | Watch |
| 404 | 2025-05-19 | 08:00–10:00 | 337.3, 509.2, 649.3 | 36.07, 39.17, 41.50 | 22.29 | 0.15000 | Alert |
| 505 | 2025-06-25 | 08:00–10:00 | 309.7, 502.7, 695.4 | 35.47, 43.36, 49.57 | 18.81 | 0.15001 | Alert |
| 606 | 2025-07-08 | 14:00–16:00 | 472.8, 643.4, 393.0 | 35.86, 37.86, 34.72 | 24.85 | 0.15002 | Alert |
| 707 | 2025-08-21 | 14:00–16:00 | 508.3, 586.5, 370.0 | 41.33, 42.49, 37.44 | 20.89 | 0.15001 | Alert |
| 808 | 2025-09-29 | 08:00–10:00 | 336.1, 534.1, 543.5 | 34.69, 41.41, 41.89 | 35.98 | 0.28002 | Critical |
| 123 | 2025-10-09 | 14:00–16:00 | 616.5, 531.0, 352.4 | 41.36, 39.76, 34.95 | 36.52 | 0.27999 | Critical |
| 456 | 2025-11-18 | 14:00–16:00 | 594.4, 563.2, 350.6 | 40.02, 38.36, 35.03 | 37.28 | 0.28004 | Critical |
| 789 | 2025-12-24 | 14:00–16:00 | 608.7, 524.8, 364.4 | 40.19, 39.49, 36.29 | 36.53 | 0.27999 | Critical |
| 150 | 2025-01-01 | 09:00–11:00 | 310.8, 531.3, 632.2 | 33.60, 36.81, 38.04 | 11.53 | 0.02499 | Below Watch (expected miss) |
| 250 | 2025-02-04 | 14:00–16:00 | 478.1, 453.5, 353.0 | 37.82, 36.47, 34.21 | 12.57 | 0.03497 | Below Watch (expected miss) |
| 350 | 2025-03-04 | 15:00–16:00 | 693.6, 547.5 | 40.30, 37.98 | 22.06 | 0.14997 | Too short (expected miss) |

The 12 positive tests span Watch, Alert, and Critical. The three hard windows deliberately test two sub-0.05 gaps and one two-hour run. The positive-test $\Delta T_{fault}$ values exceed the README's earlier 2 to 15°C suggestion for some tiers, especially the Critical cases, because larger stress values were required to reach the intended Critical gap in this model. These are synthetic test scenarios, not observed equipment faults; the severe offsets are not proposed as realistic field temperatures.

## Field List

- Weather input fields: timestamp, ambient temperature (°C), POA irradiance (W/m²), wind speed at 10 m (m/s).
- Derived fields: module count, plant-derived inverter DC capacity (W), module temperature (°C), internal-temperature proxy (°C), DC power (kW), AC power (kW), injected temperature delta (°C), faulted temperature proxy (°C), inverter efficiency, and PR.
- SQL-ready fields: `INVERTER_ID`, `DATE_TIME`, `AC_POWER`, `IRRADIANCE`, `PERFORMANCE_RATIO`.
- Daily yield and lifetime yield remain future fields; they are not generated by this Phase 1 pipeline.

## Data Sources

### Weather

Open-Meteo Historical Weather API, ECMWF IFS reanalysis, hourly for 2025-01-01 through 2025-12-31. Location: Calatagan Solar Farm, Philippines, latitude 13.9155, longitude 120.6498. The request uses 11° tilt, azimuth 0° (south), wind speed in m/s, and Asia/Singapore timezone (UTC+8, matching Asia/Manila offset).

API: <https://archive-api.open-meteo.com/v1/archive>

Open-Meteo values are model/reanalysis data, not readings from a physical weather sensor at the plant.

### Plant and equipment references

- Calatagan Solar PV Park plant profile: <https://www.sma.de/en/references/pv-power-plant-catalagan-philippines>
- SMA Sunny Tripower 60TL-10 specification: <https://files.sma.de/downloads/STP60-JP-10-DEN1818-V28web.pdf>
- Trina Solar Tallmax TSM-PC14 module specification: <https://static.trinasolar.com/sites/default/files/Tallmax%20PC14.pdf>

The simulation uses 63.3 MWp, 830 inverters, a 315 Wp module rating, 0.983 Euro efficiency, 60 kW rated AC output, and −0.41%/°C Pmax coefficient. Datasheet values are fixed assumptions, not live data.

### Model references

- Faiman module temperature model: <https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.temperature.faiman.html>
- NREL PVWatts Version 5 manual: <https://docs.nrel.gov/docs/fy14osti/62641.pdf>
- The AC calculation is the direct nominal-efficiency and rated-output clipping approximation documented above; it is not a full inverter efficiency curve.

## Demonstration Thresholds

- Absolute PR gap: $1-PR \ge 0.05$.
- Irradiance: greater than 200 W/m² for every hour in a qualifying three-hour block.
- Severity: Watch $[0.05,0.10)$, Alert $[0.10,0.20]$, Critical $> 0.20$.

These are educational demonstration assumptions. Since the baseline PR itself can be below 0.95, an absolute gap is not by itself evidence of inverter faults.
