# Solar Power Plant Inverter Analysis: A 12-month AC output quantification of inverters with a negative performance ratio gap.

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

The inverter output and injected faults in this implementation are modeled for a descriptive study.

## Audience

- Primary: Operation and Maintenance Engineer
- Secondary: Solar Energy Power Plant Supervisor

See the [stakeholder brief](stakeholder_brief.md).

## KPI and Key Formula

The main KPI is hourly Performance Ratio (PR), a unitless measure for each inverter-hour. With one-hour intervals, AC power and AC energy are numerically equal; irradiance is converted to kWh/m2.

$$
PR = \frac{AC}{I \times DC}
$$

Here `AC` is AC output in kWh, `I` is irradiation in kWh/m2, and `DC` is installed DC capacity in kWp. At zero irradiance PR is undefined and retained as null, not imputed.

For detector and peer comparisons, `pr_gap` is the timestamp's median valid fleet PR minus the inverter's PR at that timestamp. A rolling block qualifies at mean gap >= 0.05 over three consecutive daytime hours, with irradiance > 200 W/m2 in each hour. Severity is Watch 0.05 to < 0.10, Alert 0.10 through 0.20, and Critical > 0.20.

## Path B: Descriptive, Not Predictive

No predictive model is appropriate for this dataset: injected faults follow a fixed rule, so a model would only learn that rule, and Phase 2 has no real inverter-failure labels for supervised learning. This study therefore selects Path B and remains descriptive.

## Repository Structure

Generated from the tracked repository paths; generated local raw and large processed files are intentionally not listed.

|-- archive/ (.github/workflows/pages.yml, README.md, config/fault_windows.json,
|   dashboard/{data/*.csv, fleet_summary.json, index.html},
|   data/daily_inv_summary.csv, notebooks/.gitkeep, project_queries.sql,
|   scripts/publish_artifacts.py)
|-- data/ (processed/{.gitkeep, monthly_inv_summary.csv, open_meteo_cleaned.csv,
|   sample_processed_inv_metrics.csv}, raw/.gitkeep,
|   samples/processed_inv_metrics_sample.csv)
|-- docs/ (audit.md, cleaning_log.md, insights.md, kpi_definitions.md,
|   methodology.md, pipeline_baseline_hashes.txt, progress.md, README_draft.md,
|   schema.md, segmentation.md, stakeholder_brief.md, status.md, UPDATE_NOTES.md)
|-- output/
|   |-- figures/ (.gitkeep and seven PNG charts)
|   |-- sql_results/ (01_lowest_avg_pr.csv, 02_pr_gap_by_month_hour.csv,
|   |   03_flagged_3h_blocks.csv)
|   `-- tables/ (analysis CSVs, scatter samples, inverter_detail/{101,202,303}.csv)
|-- scripts/ (build_insight_tables.py, ingest.py, insights.py, kpis.py,
|   run_pipeline.py, run_sql.py, segmentation.py, transform.py)
`-- sql/ (01_lowest_average_pr.sql, 01_lowest_avg_pr.sql,
	02_pr_gap_by_month_hour.sql, 03_consecutive_underperformance.sql,
	03_flagged_3h_blocks.sql)
	|-- 01_lowest_average_pr.sql
	|-- 01_lowest_avg_pr.sql
	|-- 02_pr_gap_by_month_hour.sql
	|-- 03_consecutive_underperformance.sql
	`-- 03_flagged_3h_blocks.sql
```

## Setup

From the repository root, create and activate a virtual environment using your platform's Python launcher, then install pinned dependencies:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

The ingestion step needs network access. The project uses Python, pandas, SQLite from the standard library, and matplotlib. It does not require notebooks.

## How to Run

Run the full pipeline from the repo root:

```powershell
python scripts/run_pipeline.py
python scripts/run_pipeline.py skip-ingest
python scripts/run_pipeline.py skip-transform
```

```bash
python3 scripts/run_pipeline.py
python3 scripts/run_pipeline.py skip-ingest
python3 scripts/run_pipeline.py skip-transform
```

`skip-ingest` reuses `data/raw/open_meteo_raw.json`; `skip-transform` reuses generated processed files. The pipeline calls each step in order and reports failures.

To run steps individually, replace `python` with `python3` on Mac/Linux:

```powershell
python scripts/ingest.py
python scripts/transform.py
python scripts/run_sql.py [--sample]
python scripts/build_insight_tables.py
python scripts/kpis.py
python scripts/segmentation.py
python scripts/insights.py
```

```bash
python3 scripts/ingest.py
python3 scripts/transform.py
python3 scripts/run_sql.py [--sample]
python3 scripts/build_insight_tables.py
python3 scripts/kpis.py
python3 scripts/segmentation.py
python3 scripts/insights.py
```

Large processed CSVs and the SQLite cache are local generated files. Use `--sample` with the SQL runner for the small checked-in sample.

## Outputs

- SQL query results: [lowest average PR](../output/sql_results/01_lowest_avg_pr.csv), [monthly/hourly PR gap](../output/sql_results/02_pr_gap_by_month_hour.csv), [flagged three-hour blocks](../output/sql_results/03_flagged_3h_blocks.csv).
- Compact tables: [KPI summary](../output/tables/kpi_summary.csv), [severity counts](../output/tables/flagged_blocks_by_severity.csv), [fault-window validation](../output/tables/fault_detection_validation.csv), [season/hour segments](../output/tables/segment_pr_by_season_hour.csv), [irradiance segments](../output/tables/segment_pr_by_irradiance_band.csv), [summary statistics](../output/tables/summary_statistics.csv), and other tables under `output/tables/`.
- Figures: [hourly PR](../output/figures/pr_by_hour_of_day.png), [monthly PR](../output/figures/monthly_mean_pr_by_group.png), [fault-window PR](../output/figures/fault_day_pr_101_202_303.png), [irradiance and AC power](../output/figures/irradiance_vs_ac_power.png), plus three segmentation figures under `output/figures/`.

## Milestones

- [x] M3: ingestion, cleaning, modeled dataset, SQL-ready file, schema/method/cleaning notes, validation, and repeatability evidence. See [schema](schema.md), [methodology](methodology.md), [cleaning log](cleaning_log.md), scripts, and baseline hashes.
- [x] M4: compact descriptive tables, four charts, written interpretation, and a script-based cell workflow. See [insights](insights.md), `scripts/insights.py` (`# %%` cells), and `output/figures/`. A paired module-temperature/PR correlation is not fully met because the allowed compact inputs do not contain paired observations.
- [x] M5 Path B: segmentation, KPIs, stakeholder brief, and a repeatable pipeline. See [segmentation](segmentation.md), [KPI definitions](kpi_definitions.md), [stakeholder brief](stakeholder_brief.md), and `scripts/`.

## Detection Result

The fixed rule detected 1 of 3 injected windows: inverter 202 on 2025-06-20 (mean peer-relative gap 0.06220, Watch). It did not detect inverter 101 (0.01144) or inverter 303 (0.01385). The weaker injections can stay below the 0.05 rule threshold because modeled degradation begins only above 45 C internal temperature; this outcome describes the simulation and is not real-world detection performance. See [KPI definitions](kpi_definitions.md).

## Documentation Index

- [Schema](schema.md): dataset grain, columns, and lineage.
- [Methodology](methodology.md): formulas and assumptions.
- [Cleaning log](cleaning_log.md): data quality and missing-value decisions.
- [Insights](insights.md): initial charts and interpretation.
- [KPI definitions](kpi_definitions.md): measures, formulas, and limits.
- [Segmentation](segmentation.md): cohort and segment analysis.
- [Stakeholder brief](stakeholder_brief.md): plain-language summary for O&M.
- [Update notes](UPDATE_NOTES.md): milestone evidence and study walkthrough.

## Future Work

- Phase 2: obtain representative, verified inverter-failure labels before considering prediction.
- Phase 3: investigate validated energy and revenue impacts with appropriate operational data.
- Dashboard: consider a compact review interface after the analysis and data definitions are stable.
- Larger fault test set: evaluate the fixed rule against more varied, independently defined test windows before making performance claims.