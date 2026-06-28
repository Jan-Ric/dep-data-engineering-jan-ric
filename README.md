# Solar Power Plant Inverter Analysis: A 12-month span AC output quantification of inverters with negative gap based on Actual Vs. Predictive Yield

## Problem Statement

**I want to answer:** "When and where are those inverters that have negative gaps in terms of their performance ratio in a Solar Power Plant?"

**NOTE (optional):** Will further upgrade or add feature if possible like explaining why is there a faulty inverter gap and providing a revenue impact for each interver AC output negative gap.

## Audience

**Primary Audience:** Operation and Maintenance Engineer
**Secondary Audience:** Solar Energy Power Plant Supervisor

## KPI or Key Metric

**Main Key Performance Indicator (KPI):** Performance Ratio (PR) of each inveter per 15-minute interval

**Key Formula:**
  _PR = AC Energy Output (kW) / Irradiance (kWh/m²)  × Installed DC Capacity (kWp)_
  
**Inverter Parameters - Unit**
1. DATE_TIME           — 15-minute timestamp
2. PLANT_ID            — plant identifier
3. SOURCE_KEY          — inverter identifier (34 unique inverters)
4. DC_POWER            — kWp (p - Peak)
5. AC_POWER            — kW
6. DAILY_YIELD         — kWh accumulated today
7. TOTAL_YIELD         — kWh lifetime
8. AMBIENT_TEMPERATURE — °C (from weather sensor file)
9. MODULE_TEMPERATURE  — °C
10. IRRADIATION         — W/m² (POA)

**Thershold Intervention:**

**A. Flag Conditions**
| Condition | Threshold 
|---|---|
| PR Gap | > 0.05 (5 percentage points) |
| Duration | ≥ 3 consecutive 15-min intervals |
| Irradiance | > 200 W/m² at time of gap |

**B. Severity Tiers**
| Severity | PR Gap | Suggested O&M Action |
|---|---|---|
|  Watch | 0.05 – 0.10 | Remote checking only to log and monitor for the next 24 hours |
|  Alert | 0.10 – 0.20 | Attempt a remote reset and schedule site visit within 72 hours |
|  Critical | > 0.20 | Likely a hardware fault that requires immediate dispatch |

**Technical Terminologies**
- Play of Array (POA) - amount of solar energy striking the surface of a tilted solar panel.  
- Photovoltaic (PV) - convert "light" to "electricity"
- Standard Temperature Condition (STC) - typical temperature condition of an operating inverter
- Fleet - Multiple Distributed Energy

## Likely Data Source

I will explore the following public data sources:

**Primary Data Source:** [NREL PVDAQ (PV Data Acquisition Database)](https://dx.doi.org/10.25984/1846021)

**Secondary Data Source:** [Kaggle — Solar Power Generation Data](https://www.kaggle.com/datasets/anikannal/solar-power-generation-data)

**NOTE:** Currently using the pre-cleaned dataset from Kaggle for simplification of completing a data pipeline, then will go for NREL PVDAQ dataset (unclean data) for more complex modelling and cleaning of data.

## Possible Final Dashboard
The dashboard should help the audience quickly see three components:
1. Fleet Status Data:
   - Displays threshold intervention results wherein it reveals which investors are flagged and not flagged.
3. Inverter Ranking Panel:
   - Ranked the all inverters in terms of their inefficiencies (AC Output Power/DC Input Power)
4. Invertigation Panel
   - Click on each inverter to show a 15-minute Actual VS. Predicted AC Energy Yield 
