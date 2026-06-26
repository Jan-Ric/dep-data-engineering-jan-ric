# Luzon Grid Stress Analysis: Quantifying Dry-Season Power Continuity Risk for the Proposed Pax Silica Data Center Complex in New Clark City, Pampanga

## Problem Statement

I want to answer: "Do historical yellow and red alert events in the Luzon grid from 2019-2024 reveal dry-season power continuity patterns that present a risk to large-load infrastructure such as the proposed Pax Silica data center complex in New Clark City, Pampanga, which projects a 5 GW electricity requirement?"

## Audience

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

NGCP is the system operator and declares yellow and red alerts directly. They publish public advisories per alert event with declaration timestamps. This is the closest to a pre-labeled alert log. The gap is format inconsistency — advisories are narrative PDFs and web posts, not structured CSVs — requiring scraping and parsing. However, for 2019-2024, the alert timestamps are traceable here even when IEMOP dispatch data has gaps.
2. **[DOE Daily Power Situation Reports](https://www.doe.gov.ph)**

DOE publishes daily power situation reports during grid stress periods that explicitly label yellow and red alert declarations per grid with dates and durations. These are PDFs but follow a consistent enough template that a Python PDF parser (pdfplumber or camelot) can extract structured tables. Coverage is strongest during high-stress dry seasons — exactly your target period.
3. **Philippine News Agency / Official Press Releases**

PNA and DOE press releases archive alert declarations with dates and affected grids. Lower structured data value but useful as a cross-validation layer and gap-filler for specific missing months. Not suitable as a primary source but reliable as a secondary timestamp validator.

4. **[IEMOP Daily Operations Reports](https://www.iemop.ph/the-market/daily-operations-reports/)**

IEMOP publishes Daily Operations Reports that summarize grid conditions including reserve margin status per dispatch interval. These are more readable than raw RTD data and may contain alert classifications explicitly. Check this before attempting to derive alerts from raw RTD reserve figures — it may save significant pipeline complexity.

 
## Possible Final Dashboard

**Primary Visual:** Year-over-year heat map of monthly alert-hours

- X-axis: Year (2019, 2020, 2021, 2022, 2023, 2024) - 5-year span
- Y-axis: Month (January through December, top to bottom)
- Cell Value: Total alert-hours per month-year combination
- Legend: Sequential color scale from white (0 alert-hours) to dark red (maximum alert-hours recorded), with labeled intervals at 0, 25%, 50%, 75%, and 100% of the observed maximum

**Alert Tracks:** Two heat map layers — yellow alert-hours and red alert-hours — displayed separately via a toggle button, defaulting to red alert-hours on load since it is the primary Tier III risk signal

**Dry-Season Highlight:** December to May rows visually banded with a light background shade or left-border accent to surface seasonal stress patterns without obscuring cell color values
Tier III Threshold Line: Reference marker at 1.577 cumulative annual red alert-hours overlaid as a horizontal dashed line on a companion bar chart

- X-axis: Year (2019 to 2024)
- Y-axis: Cumulative red alert-hours per year
- Legend: Two series — "Cumulative Red Alert-Hours" (solid bar) and "Tier III Maximum Allowable Downtime — 1.577 hrs/year" (dashed red line)

**Risk Rating Panel:** Plain-language siting risk rating of Low, Moderate, or High per year derived from KPI 4, displayed as a color-coded summary card row (green / amber / red) pinned above the heat map and visible without scrolling

**Scope Label:** Annotated header stating "Luzon Grid | 2019–2024 | Reference: Proposed Pax Silica Complex, New Clark City, Pampanga"

**Public Data Access:** Downloadable aggregated dataset button on the dashboard exposing a clean CSV containing month, year, alert type, and total alert-hours per cell — derived from raw IEMOP WESM records, with no raw proprietary dispatch data included — hosted on the same GitHub Pages deployment and linked from the repository README for public transparency and reproducibility
