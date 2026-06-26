# Luzon Grid Stress Analysis: Quantifying Dry-Season Power Continuity Risk for the Proposed Pax Silica Data Center Complex in New Clark City, Pampanga

## Problem Statement

I want to answer: "Do historical yellow and red alert events in the Luzon grid from 2019-2024 reveal dry-season power continuity patterns that present a risk to large-load infrastructure such as the proposed Pax Silica data center complex in New Clark City, Pampanga, which projects a 5 GW electricity requirement?"

## Audience

This project is for stakeholders evaluating the Pax Silica complex developed by the Bases Conversion and Development Authority (BCDA).

- **Who:** Foreign investors and infrastructure developers
- **Decision:** Evaluating Luzon, Philippines as a data center siting location, specifically the Pax Silica complex in New Clark City, Pampanga
- **Need:** Data-driven grid reliability baseline to inform investment commitment
- **Urgency:** Decision window ahead of the projected 2028 groundbreaking

## KPI or Key Metric

The main metric I want to track is **Monthly Alert-Hours by Severity**
1. **Yellow Alert-Hours per Month**

**What it measures:** Total hours the Luzon grid operated under yellow alert status within a calendar month

**Formula:** Σ (Yellow Alert End Timestamp − Yellow Alert Start Timestamp) for all yellow alert events within the month

**Unit:** Hours per month

2. **Red Alert-Hours per Month**

**What it measures:** Total hours the Luzon grid operated under red alert status within a calendar month

**Formula:** Σ (Red Alert End Timestamp − Red Alert Start Timestamp) for all red alert events within the month

**Unit:** Hours per month

3. **Cumulative Annual Red Alert-Hours**

**What it measures:** Running total of red alert-hours across all months within a calendar year, used as the primary Tier III compatibility check

**Formula:** Σ (Monthly Red Alert-Hours) across January to December of each year

**Unit:** Hours per year

**Benchmark:** ≤ ~1.6 hours per year (Tier III Data Center 99.982% uptime standard)

4. **Monthly Risk Rating**

What it measures: Plain-language siting risk signal derived from red alert-hours relative to the Tier III annual budget
**Formula:**

- **Low** → Monthly red alert-hours = 0
- **Moderate** → Monthly red alert-hours > 0 but cumulative annual total ≤ 1.6 hours
- **High** → Cumulative annual red alert-hours > 1.6 hours

**Unit:** Categorical (Low / Moderate / High)

**Output:** Primary decision signal on the dashboard for the investor audience


## Likely Data Source

I will explore the following public data sources:

**Note:** Currently evaluating the datasets available so most of the components are draft but the problem being solved is defined.

1. **[NGCP Grid Advisory Archives](https://www.ngcp.ph)**

2. **[DOE Daily Power Situation Reports](https://www.doe.gov.ph)**

3. **Philippine News Agency / Official Press Releases**

4. **[IEMOP Daily Operations Reports](https://www.iemop.ph/the-market/daily-operations-reports/)**

## Possible Final Dashboard

**Primary Visual:** Year-over-year heat map of monthly alert-hours

**Alert Tracks:** Two heat map layers: Yellow alert-hours and Red alert-hours _(default risk signal)_ which displayed separately via a toggle button.

**Dry-Season Highlight:** Visualize the December–May dry season using appropriate background shading to highlight stress patterns.

**Risk Rating Panel:** Plain-language siting risk rating of Low, Moderate, or High per year derived from KPI 4, displayed as a color-coded summary card row (green / amber / red) pinned above the heat map and visible without scrolling

**Scope Label:** Annotated header stating "Luzon Grid | 2019–2024 | Reference: Proposed Pax Silica Complex, New Clark City, Pampanga"

**Public Data Access:** Downloadable aggregated dataset option on the dashboard derived from raw public data records with no raw proprietary dispatch data included.
