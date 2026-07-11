# Solar Power Plant Inverter Analysis: A 12-month AC output quantification of inverters with a negative performance ratio gap

---

## Problem Statement

### **Dilemmas:**

1. Difference in Life-Span - Solar Panels typically have 25-30 years while inverters only have 5-10 years which requires high maintenance
2. Inverters are hard and complex to repair - As Operations and Maintenance can't just simply repair or troubleshoot faulty inverters, these components are also more sensitive as they compose of major electronics circuits and parts.
3. Current solution is cure (based on historical data) rather than prevention (like predicting the remaining life-span of the inverters).

### **I want to answer (Phase 1):**

**"When and where are those inverters that have negative performance ratio gaps in a solar power plant?"**

**Scope:** My end goal is to provide insight into the project's business side as well as data-driven decisions for better grid management. For now, however, I will concentrate on Phase 1 only.

Furthermore, while the project aims to collect weather data in near real time, the **actual internal telemetry and performance metrics for inverter and solar module data are not directly available to fetch as a dataset**. But these can be derived indirectly, which is why there is a baseline (Calatagan Solar Farm - _not for commercial use_) and calculation to derive the parameters needed to compute the Performance Ratio (KPI).

_There will be three phases in my project:_

- **Phase 1. Identifying which inverter/s are underperforming from Historical Weather API and AC Yield (Anomaly Detection)**

- **Phase 2. Predictive Remaining Lifespan of Inverter from Historical and Weather Forecast API, Change in Temperature, Date after installation (Prediction Model - Supervised Learning)**

- **Phase 3. Translate to Business Aspect (Gross Revenue Impact - will further research about this if ever)**

---

## Audience

- **Primary Audience:** Operation and Maintenance Engineer

- **Secondary Audience:** Solar Energy Power Plant Supervisor

---

## KPI or Key Metric

### **Main Key Performance Indicator (KPI):** Performance Ratio (PR) of each inverter per 1-hour interval

---

### **Key Formula (this is what field 10, PERFORMANCE_RATIO, is calculated from):**

$$
PR = \dfrac{AC}{I \times DC}
$$

_where:_

- _**PR** = Performance Ratio (Unitless) — this is the final output, the number Phase 1 is trying to flag anomalies on_
- _**AC** = AC Energy Output (kWh) — comes from field 5, AC_POWER_
- _**I** = Irradiance (kWh/m²), based on a reference of 1 kW/m² — comes from field 12, IRRADIATION_
- _**DC** = Installed DC Capacity (kWp) — this doesn't change over time; it's calculated once in Formula A and reused for every inverter_

**Note:** PR is the last step in the pipeline. Everything before it (Formulas A–F below) exists just to build the fields this formula needs, since the raw data sources don't give us inverter/module readings directly. _(See Data Source Notes for what's pulled directly vs. what's calculated.)_

---

### **Preliminary Formulas:**

None of the fields below come straight from a data source — Open-Meteo only gives weather data, and there's no live inverter telemetry available (see Problem Statement). Formulas A–F are how the rest of the fields get built, using the weather data plus the fixed datasheet numbers as inputs. Each one below is written as: what goes in, what comes out, and what uses that output next.

### A. Plant Sizing Derivation — fixed values, calculated once

**In:** the plant's total DC capacity, number of inverters, and module rated power (all fixed numbers from the datasheets). **Out:** two constants — `N_module` (modules per inverter) and `DC_inv,plant-derived` (DC capacity per inverter) — calculated once and reused for every inverter and every hour, not recalculated per row. Checked against the plant's published panel count to make sure the math lines up. `N_module` is used in Formula C. `DC_inv,plant-derived` is used in the PR formula — this is a different number from the SMA nameplate DC rating (which only shows up in Formula E), so they shouldn't be mixed up.

### B. Module Temperature — Faiman Model (checked against the datasheet)

**In:** ambient temperature, irradiance, and wind speed — all from Open-Meteo. **Out:** `MODULE_TEMPERATURE`, used in Formulas C and E. This is the first calculation after pulling the raw weather data, and it's also where most of the hour-to-hour change comes from, since wind speed moves somewhat independently of temperature and irradiance. The formula's constants are standard published values, not something fitted to this project's data, and they were checked once against the module datasheet's NOCT rating to confirm they're reasonable.

### C. Module DC Power (adjusted for temperature)

**In:** module temperature (Formula B), irradiance, and modules per inverter (Formula A). **Out:** `DC_POWER`, calculated by scaling the module's rated power by irradiance and by how much heat reduces its output, then multiplying by the number of modules.

### D. Inverter AC Output

**In:** DC power (Formula C), plus the inverter's fixed efficiency and rated capacity from the datasheet. **Out:** `AC_POWER`. The output is capped at the inverter's rated 60 kW, so on high-irradiance hours some power gets "clipped" off — this is expected given the plant's 1.27 DC/AC ratio (from Formula A), not a sign of anything wrong.

### E. Ambient-envelope stress proxy

**In:** ambient temperature plus the heating effect from Formula B, compared against the inverter's rated operating limit of 60°C. **Out:** `THERMAL_STRESS_FLAG`, a simple yes/no check. Every number here comes straight from the datasheet, nothing is estimated.

### F. Fault Injection (used only for testing, not the real pipeline)

**In:** the baseline from Formula E, plus a manually chosen offset and severity level, applied only to specific inverters/time windows I pick for testing. **Out:** `DELTA_T_FAULT` (0 everywhere else) and a reduced efficiency value. This isn't part of the actual data pipeline — it's how I create fake, labeled "faults" (Watch 2–4°C / Alert 4–8°C / Critical 8–15°C) so I can check whether my Phase 1 anomaly detector actually catches them before trusting it on real data.

---

### **Inverter & Solar Output Performance and Operational Parameters | Weather Sensor Parameters**

_Format: FIELD (Unit) - Data Type -> Description_

### **_A. From simulation methodology — 830 SMA Sunny Tripower 60TL-10 inverters, Calatagan Solar Farm_**

1. DATE_TIME (1-hour timestamp) — TIMESTAMP
2. INVERTER*ID (Unitless) - INTEGER -> \_inverter identifier (830 unique inverters)*
3. MODULE*TEMPERATURE (°C) - DECIMAL -> \_from Faiman model (Formula B): T_ambient + G_POA / (u₀ + u₁ × WS); checked against Trina datasheet*
4. DC*POWER (kW) - DECIMAL -> \_from Formula C: P_STC × (G_POA/1000) × [1 + (γ_p/100) × (T_module − 25)] × 242 modules*
5. AC*POWER (kW) - DECIMAL -> \_from Formula D: min(DC_POWER × η_inv, 60 kW rated); instantaneous power, not accumulated energy*
6. DAILY*YIELD (kWh) - DECIMAL -> \_accumulated today, added up from AC_POWER*
7. TOTAL*YIELD (kWh) - DECIMAL -> \_lifetime total, same install date assumed for all inverters*
8. THERMAL*STRESS_FLAG (Boolean) - INTEGER -> \_from Formula E: flags when (ambient temp + module heating) gets close to the datasheet's +60°C limit*
9. DELTA*T_FAULT (°C) - DECIMAL -> \_injected fault offset (Formula F), only applied to selected inverter_id/time windows for testing; 0 everywhere else*
10. PERFORMANCE*RATIO (Unitless) - DECIMAL -> \_the KPI: AC_POWER / (IRRADIATION_kWh_m2 × DC_inv,plant-derived); see Field 12 and Formula A*

### **_B. From open-source weather API (Open-Meteo — ECMWF IFS, hourly, Jan–Dec 2025)_**

11. AMBIENT*TEMPERATURE (°C) - DECIMAL -> *`temperature_2m`, hourly reading\_
12. IRRADIATION (W/m² - GTI/POA) - DECIMAL -> _`global_tilted_irradiance`, preceding-hour mean; tilt 11°, azimuth 0° (south). Comes in as W/m²; converted to kWh/m² (`× 1h / 1000`) before it's used in the PR formula, since that's a straight unit conversion at hourly intervals, not something that needs to be added up over time._
13. WIND*SPEED (m/s) - DECIMAL -> *`wind_speed_10m`, hourly reading; needed for Formula B. This field wasn't in my original plan, but I added it once I found the module temperature formula needed wind speed as an input.\_

---

### **Threshold Intervention:**

**A. Flag Conditions**
| Condition | Threshold |
|---|---|
| PR Gap | > 0.05 (5 percentage points) |
| Duration | ≥ 3 consecutive 1-hour intervals |
| Irradiance | > 200 W/m² at time of gap |

**B. Severity Tiers**
| Severity | PR Gap | Suggested O&M Action |
|---|---|---|
| Watch | 0.05 – 0.10 | Remote checking only; log and monitor for the next 24 hours |
| Alert | 0.10 – 0.20 | Attempt a remote reset and schedule a site visit within 72 hours |
| Critical | > 0.20 | Likely a hardware fault that requires immediate dispatch |

**Technical Terminologies**

- **Plane of Array (POA)** - amount of solar energy striking the surface of a tilted solar panel.
- **Photovoltaic (PV)** - converts light to electricity.
- **Standard Test Conditions (STC)** - the reference conditions used to rate module power at manufacture: 1000 W/m² irradiance, 25°C cell temperature, AM1.5 solar spectrum. Not related to inverter operating temperature.
- **Fleet** - the full set of distributed inverters/modules being monitored across the plant.

---

## Data Source Notes

_There are two different kinds of data being pulled into this project, and they're handled differently: weather data changes every hour, so it gets pulled fresh for every hour in the pipeline; datasheet numbers (inverter specs, plant capacity) never change, so they're pulled once and reused everywhere instead of being fetched again and again. Pulling the datasheet numbers repeatedly would be pointless — same result every time — and it also creates a small risk: if that webpage ever got edited partway through the project, different parts of the pipeline could end up using different numbers without anyone noticing._

### Primary Source

**Weather/irradiance (Historical Weather API)**

- Name: Open-Meteo Historical Weather API (Hourly parameters)
- URL: https://archive-api.open-meteo.com/v1/archive?latitude=13.9155&longitude=120.6498&start_date=2025-01-01&end_date=2025-12-31&hourly=global_tilted_irradiance,temperature_2m,wind_speed_10m&models=ecmwf_ifs&timezone=Asia%2FSingapore&wind_speed_unit=ms&tilt=11&azimuth=0
- Format: JSON (one request returns the whole year's hourly data — no pagination needed)
- How it's pulled: a single historical batch download, not a live/streaming feed, since Phase 1 only needs the full 2025 year at once. This fills fields 11–13 (table B above).
- Coverage
  - Location: Calatagan Solar Farm, Calatagan, Batangas, Philippines
  - Latitude: 13.9155°
  - Longitude: 120.6498°
  - Timeframe: **January 1 to December 31, 2025** (a full year, so it isn't skewed toward the wet or dry season)
  - Azimuth: 0° (South), set in the URL
  - Tilt Angle: 11°
  - Wind Speed Unit: m/s, set via `wind_speed_unit=ms` in the URL (this matches the unit Formula B expects)
  - Timezone: `Asia/Singapore` (the closest option Open-Meteo offers; the plant is actually in Asia/Manila, but both are UTC+8, so the hourly timestamps still line up correctly)
  - Re-analysis Model Used: ECMWF IFS
- Why it fits the problem: Hourly is Open-Meteo's native resolution, which matches what this project needs. It provides `global_tilted_irradiance` (POA), ambient temperature, and wind speed, which map directly onto the IRRADIATION, AMBIENT_TEMPERATURE, and WIND_SPEED fields. No account or API key is needed, which keeps things simple for a first project. It also has a 7–16 day forecast option, which I can reuse later for Phase 2.
- Known limitations: This is model/reanalysis data, not a real physical sensor at the plant — so it's a reasonable stand-in, not a perfect match to what a sensor on-site would actually read.

**Note:** the tables below aren't pulled repeatedly like the weather data — they're one-time reference numbers I look up once and then reuse (see Formula A).

### Simulation Reference Sources (Component B — one-time reference data, not a time series)

|                             | Plant Profile                                                                                                                                                                                              | Inverter Datasheet                                                                                                                                                                                                                                                                                                                                        | Module Datasheet                                                                                                                                                                                                                                              |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Name**                    | Calatagan Solar PV Park, Philippines — plant profile                                                                                                                                                       | SMA Sunny Tripower 60TL-10 (STP 60-JP-10) Specifications                                                                                                                                                                                                                                                                                                  | Trina Solar Tallmax TSM-PC14 (Polycrystalline) Specifications                                                                                                                                                                                                 |
| **URL**                     | https://www.sma.de/en/references/pv-power-plant-catalagan-philippines                                                                                                                                      | [files.sma.de/downloads/STP60-JP-10-DEN1818-V28web.pdf](https://files.sma.de/downloads/STP60-JP-10-DEN1818-V28web.pdf)                                                                                                                                                                                                                                    | [static.trinasolar.com/.../Tallmax PC14.pdf](https://static.trinasolar.com/sites/default/files/Tallmax%20PC14.pdf)                                                                                                                                            |
| **Format**                  | HTML page (reference only — not a downloadable dataset)                                                                                                                                                    | PDF (reference only — not a downloadable dataset)                                                                                                                                                                                                                                                                                                         | PDF (reference only — not a downloadable dataset)                                                                                                                                                                                                             |
| **Coverage**                | - Single plant<br>- Capacity: 63.3 MW<br>- Inverters: 830 × SMA Sunny Tripower 60TL-10<br>- Solar panels: 200,928<br>- Module: Trina Tallmax TSM-PC14 (polycrystalline)                                    | - Type: STP 60-JP-10<br>- Rated DC power: 61,240 W / Max PV array power: 90,000 Wp (this is the nameplate rating — not the number used for PR, see Formula A)<br>- Max DC input voltage: 1000 V<br>- Rated AC power: 60,000 W<br>- Max efficiency: 98.8% / Euro-eta: 98.3%<br>- Cooling: active (fan) / Operating temp: −25°C to +60°C<br>- Weight: 75 kg | - Type: TSM-PC14, 72-cell multicrystalline<br>- Power range: 305–315 Wp<br>- Module efficiency: 15.7%–16.2%<br>- Temp. coefficient of Pmax: −0.41%/°C<br>- NOCT: 44°C ±2°C (800 W/m², 20°C, 1 m/s wind)<br>- Dimensions: 1956 × 992 × 40 mm / Weight: 22.5 kg |
| **Why it fits the problem** | - Gives a real basis for the plant sizing calculation<br>- Anchors the fault-injection simulation to a real plant's numbers, combined with real weather data, so the synthetic AC/DC values aren't made up | - Gives the inverter's real operating numbers (rated power, efficiency, thermal limits) used in the AC output and thermal-stress formulas                                                                                                                                                                                                                 | - Gives the module's real operating numbers (power rating, temperature coefficient, NOCT) used in the DC power and module-temperature formulas                                                                                                                |
| **Known limitations**       | - Reference/spec info only, no time-series data<br>- Only covers inverter performance + weather; inverter/module temperature comes from the simulated fault-injection instead of a real sensor             | - Reference/spec info only, no time-series data<br>- No published curve showing how efficiency drops with internal temperature for this model                                                                                                                                                                                                             | - Reference/spec info only, no time-series data                                                                                                                                                                                                               |

### Fallback Source

**A. Kaggle Static Solar Power Data (main fallback)**

- Name: Solar Power Generation Data (Kaggle)
- URL: https://www.kaggle.com/datasets/anikannal/solar-power-generation-data/
- Format: CSV (generation data + weather sensor data, 2 plants)
- How it's pulled: a one-time file download, no account or API key needed — so I can still build and test the pipeline offline even if I don't have internet access to an API.
- Coverage: 2 solar plants, 34-day period, 15-min interval, includes: DC_POWER, AC_POWER, DAILY_YIELD, TOTAL_YIELD, AMBIENT_TEMPERATURE, MODULE_TEMPERATURE, IRRADIATION
- Why it could still work: It's already cleaned, and it already has DC/AC power and temperature readings directly, so I could use it to test the PR/anomaly-detection logic even without running Formulas B–D. The native 15-minute readings would need to be resampled (grouped) into hourly readings to match this project's design.
- Known limitations: It's a static file with no way to get new data (no live updates); only covers 34 days, which is far short of the full year this project needs; needs resampling to hourly before it lines up with the rest of the pipeline. I still need to check `SOURCE_KEY.nunique()` to confirm how many inverters are actually in each plant before using it.

**B. Solcast Historical Weather API (not usable yet)**

- Name: Solcast Historical Weather API (Hourly parameters)
- URL: _Not available yet — this requires an API account, and mine isn't verified yet, so I don't have a working link to give here._
- Format: JSON
- Coverage (planned, once I get access): same location, same Jan–Dec 2025 timeframe, same tilt/azimuth/wind-speed-unit setup as the Open-Meteo pull above.
- Why it could still work: Similar hourly data to Open-Meteo, and it also offers a 7–16 day forecast, which could help with Phase 2 later.
- Known limitations: I can't use this yet since the account isn't verified. It also only supports 2 panel orientations per account, though that's not a problem here since this plant only has one orientation. I'm including it mainly as a note for later — it doesn't count as my real fallback yet since there's no working link.

**NOTE:** Fields to be added if Phase 2 and 3 are developed:

- Phase 2:
  - RUL_INV (Months and Days) - DATE -> Predicted Remaining Useful Life of each inverter.
  - PR_FORECAST (Unitless) - DECIMAL -> Predicted Performance Ratio of each inverter for 15 days
  - DELTA_THEMP (°C) - FLOAT -> Change in temperature of internal vs. ambient
  - AGE_INV (Years) - DATE -> The age or exact install date of each inverter
- Phase 3:
  - Power Purchase Agreement (Fixed 8.69 ₱/kWh) -> The fixed price at which the Solar Farm sells electricity to the grid. Main component for "Gross Revenue Impact" (will research further if pursued).

---

## Possible Final Dashboard

The dashboard should help the audience quickly see three components:

1. **Fleet Status Panel:**
   - Displays threshold intervention results, revealing which inverters are flagged (Watch/Alert/Critical) and which are not.
2. **Inverter Ranking Panel:**
   - Ranks all inverters by inefficiency (AC Output Power / DC Input Power).
3. **Invertigation Panel:**
   - Click on each inverter to show an hourly Actual vs. Predicted AC Energy Yield.

**Note:** This will also be updated if Phase 2 and Phase 3 are developed.

_PS: AI agents assisted with some formatting to make the markdown file cleaner and easier to read while preserving the template._
