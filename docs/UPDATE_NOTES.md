# Project Update Notes

## 1. Overview

The project downloads hourly Open-Meteo weather, transforms it into modeled inverter-hour records, runs SQLite questions, builds compact summary tables and KPIs, compares segments and cohorts, and writes figures and plain-language interpretation. The inverter telemetry and fault events are simulated, so the results are descriptive rather than equipment diagnoses.

This documentation update adds a copy-ready README draft and consolidates the milestone notes. It clarifies the Path B decision, corrects the detection summary to the current recorded result of 1 of 3 injected windows, links to existing outputs, and records the one incomplete analysis criterion. No code, thresholds, processed data, or numeric output was changed in this batch.

## 2. Criteria Checklist

### M3: Clean Dataset

| Pass criterion | Status | Evidence |
| --- | --- | --- |
| Obtain and preserve hourly weather source data | Met | `scripts/ingest.py`; `data/raw/open_meteo_raw.json` is retained locally. |
| Clean weather columns and parse timestamps | Met | `scripts/transform.py`; `data/processed/open_meteo_cleaned.csv`. |
| Create detailed inverter-hour computation outputs and SQL-ready metrics | Met | `scripts/transform.py`; `data/processed/` contains the outputs, with the largest files generated locally. |
| Document schemas, grain, key, formulas, sources, and cleaning decisions | Met | `docs/schema.md`, `docs/methodology.md`, `docs/cleaning_log.md`. |
| Validate required values, types, ranges, keys, row counts, and nighttime PR nulls | Met | `scripts/transform.py`; `docs/cleaning_log.md`. |
| Do not impute undefined or missing values | Met | `scripts/transform.py`; nighttime PR remains null at zero irradiance. |
| Demonstrate repeatability for current local inputs | Met for recorded run | `docs/progress.md` records two matching transform runs; hashes are in `docs/pipeline_baseline_hashes.txt`. |

### M4: Initial Insights

| Pass criterion | Status | Evidence |
| --- | --- | --- |
| Answer the three beginner SQL analysis questions and save results | Met | `sql/`, `scripts/run_sql.py`, `output/sql_results/`. |
| Produce compact descriptive tables and fixed-seed sample | Met | `scripts/build_insight_tables.py`, `output/tables/`. |
| Produce four initial charts and written interpretation | Met | `scripts/insights.py`, `docs/insights.md`, `output/figures/`. |
| Provide notebook-style, reproducible exploration | Met by script-format alternative | `scripts/insights.py` is divided into VS Code `# %%` cells, with `docs/insights.md` and `output/figures/`. The project requirement is plain scripts and no notebooks, so no `.ipynb` is used. |
| Compare paired module temperature and PR observations | Not fully met | The allowed compact analysis inputs do not contain paired module-temperature and PR observations. `scripts/insights.py` and `docs/insights.md` report this limitation rather than an unsupported correlation. |

### M5: Path B

| Pass criterion | Status | Evidence |
| --- | --- | --- |
| Define and calculate the requested KPIs | Met | `scripts/kpis.py`, `docs/kpi_definitions.md`, `output/tables/kpi_summary.csv`. |
| Segment by season/hour and irradiance and compare cohorts | Met | `scripts/segmentation.py`, `docs/segmentation.md`, segment/cohort tables and figures in `output/`. |
| Explain results for the intended audience | Met | `docs/stakeholder_brief.md`. |
| Select a justified non-predictive path | Met | Path B: injected faults use a fixed rule and Phase 2 has no real failure labels. See the Path Choice section below. |
| Provide an ordered pipeline and repeatable run instructions | Met | `scripts/run_pipeline.py`; `docs/README_draft.md`; Batch 9 run evidence in `docs/progress.md`. |

## 3. Removed or Archived

| Item | Why it is outside M3-M5 | Replacement or disposition |
| --- | --- | --- |
| Dashboard website and publishing workflow | A dashboard deployment is beyond the beginner data and descriptive-analysis milestones. | Supporting material remains under `archive/dashboard/` and `archive/.github/workflows/`; analysis tables and figures remain under `output/`. |
| Legacy query collection | Superseded by focused SQLite questions for the current study. | Current queries are under `sql/`. |
| Empty Jupyter notebook placeholder | A notebook runtime conflicts with the requested plain-script workflow; no executed analysis depended on it. | `scripts/insights.py` in `# %%` cell format, `docs/insights.md`, and `output/figures/`. |
| Unreconciled legacy daily summary | No verified generator or reconciliation supported it. | Documented monthly and compact analysis outputs. |
| External fault JSON as active configuration | A separate configuration file added indirection for three fixed demonstration windows. | The source of truth is the `FAULT_WINDOWS` list in `scripts/transform.py`; consumers import it. The archival JSON is retained under `archive/config/`. |

Raw source files in `data/raw/` are not removed by this project workflow and were not touched in this batch.

## 4. Added

- `docs/README_draft.md`: copy-ready stranger-facing project guide; the root README was deliberately not edited in this batch.
- `docs/UPDATE_NOTES.md`: this consolidated milestone checklist, walkthrough, and study record.
- `scripts/run_sql.py` and focused SQL query files; `--sample` supports a small checked-in input.
- `scripts/build_insight_tables.py`, `scripts/insights.py`, `scripts/kpis.py`, `scripts/segmentation.py`, and `scripts/run_pipeline.py` for repeatable analysis.
- Compact SQL results, tables, and charts under `output/`.
- M3-M5 explanations under `docs/`, including schema, methods, cleaning, insights, KPI definitions, segmentation, stakeholder brief, and baseline hashes.

## 5. Simplified

The examples below compare the earlier tracked transform with the simplified form. The changes explain implementation organization; they do not authorize changing model outputs or detector thresholds.

**Duplicate AC and PR calculation merged.** The earlier transform had one feature-calculation path and another inverter-metrics path that computed AC and PR again after fault assignment. The current transform computes inverter metrics once after applying the selected fault offset, then derives the SQL-ready columns from those metrics.

Earlier calculation shape:

```python
df_features["ac_power_kw"] = (df_features["dc_power_kw"] * eta_inv).clip(upper=p_ac_rated)
df_features["performance_ratio"] = df_features["ac_power_kw"] / (irradiation_kwh_m2 * dc_inv_kwp)
```

The later calculation applies the fault-adjusted efficiency before calculating AC and PR for the modeled inverter rows, avoiding a separate competing result path.

**Dummy-key merge replaced by a cross join.** Earlier code added a constant key to both tables, joined on it, then removed the key:

```python
df_features = df_features.assign(key=1)
inverter_ids = inverter_ids.assign(key=1)
df_metrics = df_features.merge(inverter_ids, on="key").drop(columns="key")
```

The current code states the intended all-pairs relation directly:

```python
df_metrics = df_features.merge(inverter_ids, how="cross")
```

**JSON fault config replaced by an inline fault list.** Earlier code opened `config/fault_windows.json` and loaded `json.load(file)["fault_windows"]`. The active configuration is now `FAULT_WINDOWS` in `scripts/transform.py`, so a beginner can see the three fixed examples beside other project constants. Shared consumers import that list rather than copying the dates.

**Constants moved to the top.** Earlier formulas assigned plant, module, inverter, and thermal constants inside calculation functions. The current transform puts these assumptions near the top of the file so the formula functions use one visible definition.

**Validation made explicit.** The current transform validates expected schemas and row counts, missing values, numeric and datetime types, unique inverter-hour keys, physical ranges, allowed fault offsets, and daytime/nighttime PR behavior.

**Fault windows shared by import.** Table building, segmentation, and insights use `from transform import FAULT_WINDOWS`, reducing duplicated fault dates.

**Pipeline runner added.** `scripts/run_pipeline.py` runs ingestion, transformation, SQL, table building, KPI, segmentation, and insights in order, while supporting `skip-ingest` and `skip-transform`.

## 6. File-by-File Walkthrough

1. `scripts/ingest.py` requests historical hourly weather and validates coverage before saving the source response.
2. `data/raw/` holds the retained API input. Preserve it as the reproducible source for transformation; do not delete it.
3. `scripts/transform.py` cleans weather, calculates modeled module and inverter values, applies fixed demonstration fault windows, validates outputs, and writes processed files.
4. `data/processed/` contains cleaned weather and compact checked-in samples; the detailed computation and full SQL-ready metrics files are generated locally. The main metrics grain is one row per inverter per hour, keyed by inverter ID and timestamp.
5. `scripts/run_sql.py` loads the SQL-ready CSV to local SQLite in 100,000-row chunks, runs queries from `sql/`, and saves results under `output/sql_results/`.
6. `output/sql_results/` contains the lowest-PR, month/hour gap, and rolling flagged-block query outputs.
7. `scripts/build_insight_tables.py` reads large CSV inputs in chunks and creates compact summary, sample, and fault-validation tables.
8. `output/tables/` stores those tables, including `kpi_summary.csv`, cohort summaries, segment summaries, and inverter detail files.
9. `scripts/kpis.py` validates compact inputs, calculates the KPI summary, and writes `output/tables/kpi_summary.csv`.
10. `scripts/segmentation.py` builds season/hour and irradiance summaries, compares faulted and non-faulted cohorts, and writes tables and charts.
11. `scripts/insights.py` reads compact outputs, prints summaries, and generates the initial descriptive charts. Its VS Code `# %%` sections can run individually or as a script.
12. `output/figures/` stores the initial insight and segmentation charts.
13. `docs/` explains schemas, formulas, cleaning choices, results, KPI definitions, segmentation, stakeholders, and hashes.
14. `scripts/run_pipeline.py` calls all stages in dependency order and supports reuse of existing raw or processed inputs with skip options.

## 7. Concepts to Study

- **Grain:** what one row represents; here, an inverter at one hour.
- **Composite key:** a unique record identified by inverter ID plus timestamp.
- **Cross join:** pairing every weather-hour row with each modeled inverter.
- **Missing-value strategy:** preserve undefined nighttime PR as null; do not invent a value through imputation.
- **Validation:** executable checks for schema, row count, types, value ranges, and unique keys.
- **Reproducibility and hashing:** rerun the same transformation and compare SHA-256 output hashes for unchanged inputs and environment.
- **Descriptive statistics:** summaries of the modeled data, not predictions or diagnoses.
- **Rolling windows:** evaluate each overlapping set of three consecutive hourly records.
- **PR gap against a fleet median:** at each timestamp, compare the inverter PR with the median valid fleet PR at that time; this differs from `1 - PR`.
- **Segmentation and cohorts:** compare defined time/irradiance groups and faulted versus non-faulted records.
- **KPI framework:** define formula, units, source, interpretation, and limits for each measure.
- **Correlation versus causation:** a pattern does not establish that one variable caused another.
- **Limits of simulated data:** fixed injected faults and modeled telemetry cannot establish real operating performance.

## 8. How to Run and Verify

Use the platform-specific setup and full pipeline commands in `docs/README_draft.md`. Windows uses `python`; Mac/Linux uses `python3`. Install pinned packages with `python -m pip install -r requirements.txt` after activating the virtual environment. Ingestion needs network access. The SQL runner can use `--sample` to exercise the small checked-in sample.

For a full pipeline run that reuses the retained raw JSON, run `python scripts/run_pipeline.py skip-ingest`; to reuse processed files as well, use `python scripts/run_pipeline.py skip-ingest skip-transform` only if the runner permits both flags in the current version. Individual scripts can be run in data-flow order when debugging.

The progress record documents that the full-data SQL, table, KPI, segmentation, insight, and pipeline steps completed, and that two transform runs matched on the saved processed-output hashes. `docs/pipeline_baseline_hashes.txt` stores hashes for recorded SQL/table outputs and the two large processed baselines. This documentation batch did not rerun project scripts because code and numeric outputs were explicitly out of scope.

## 9. Assumptions and Open Questions

- `n_module` is a float from `63,300,000 / 830 / 315`, approximately 242.1113. It is not rounded to 242; no numeric model output was changed to match an earlier approximate note.
- Detector `pr_gap` is peer-relative: median valid PR across inverters at an hour minus that inverter's PR. It is distinct from the fleet mean shortfall `1 - pooled mean PR`.
- The saved fault validation detects 1 of 3 windows: inverter 202 crosses the 0.05 threshold as Watch; inverters 101 and 303 do not. Fault degradation begins only above 45 C internal temperature, so weaker injected changes may yield a small PR effect. This is a fixed-rule simulation result, not a general detection-performance estimate.
- M4 is delivered with `scripts/insights.py` in cell format plus its report and figures, not with a notebook file, to honor the scripts-only project constraint.
- Path B is selected because injected faults follow a fixed rule and Phase 2 has no real failure labels. No predictive model is trained.
- A module-temperature/PR paired correlation remains not fully met because permitted compact inputs do not contain paired observations. Do not infer this statistic from separate aggregates.
- `docs/status.md` is a file inventory snapshot, not a current code review. `docs/progress.md` is the chronological work log. `docs/pipeline_baseline_hashes.txt` records expected hashes from prior validation runs.
- The root `README.md` is not changed in this batch. The copy-ready content is in `docs/README_draft.md` for the owner to copy.
- A duplicate SQL name (`01_lowest_average_pr.sql` and `01_lowest_avg_pr.sql`), archived non-snake-case names such as `README.md`, and empty directories are retained. The filename/empty-directory audit is not fully met and should be handled separately if repository policy permits.

## M5 Path Choice

Path B means keeping this phase descriptive and not training a predictive model. The injected faults are generated by a fixed rule, so a model could only reproduce that rule. Phase 2 does not have real, verified failure labels for supervised learning. Prediction should wait until representative operational labels and a meaningful target are available.| Former empty `notebooks/insights.ipynb` | Removed from the repository to keep the project script-only and ensure no `.ipynb` files remain | `scripts/insights.py` in VS Code `# %%` sections, `docs/insights.md`, and `output/figures/` |
# Project Update Notes

## 1. Overview

This update aligns the repository to the beginner M3 Clean Dataset and M4 Initial Insights scope. The pipeline uses plain Python scripts, pandas, SQLite, and matplotlib. It loads hourly Open-Meteo weather, builds an hourly inverter dataset, validates it, answers initial SQL questions, and publishes compact tables and figures. The inverter telemetry and fault events are simulated, so findings are descriptive and educational.

## 2. Criteria Checklist

| Milestone criterion | Status | Evidence |
| --- | --- | --- |
| M3: Obtain hourly weather input and preserve the source file | Met | `scripts/ingest.py`; `data/raw/open_meteo_raw.json` is local and is not modified by transform |
| M3: Clean and rename weather columns and parse timestamps | Met | `scripts/transform.py`; `data/processed/open_meteo_cleaned.csv` |
| M3: Produce the detailed modeled inverter-hour computation data | Met | `scripts/transform.py`; `data/processed/open_meteo_computation.csv` |
| M3: Produce a SQL-ready analysis file with documented grain and composite key | Met | `data/processed/processed_inv_metrics.csv`; `docs/schema.md` |
| M3: Document expected schemas, formulas, sources, and cleaning decisions | Met | `docs/schema.md`, `docs/methodology.md`, `docs/cleaning_log.md` |
| M3: Validate completeness, physical ranges, null behavior, output schemas, and duplicate keys | Met | `scripts/transform.py`; `docs/cleaning_log.md` |
| M3: Avoid imputation and preserve undefined nighttime PR as null | Met | `scripts/transform.py`; `docs/cleaning_log.md` |
| M3: Reproduce processed outputs consistently | Met for current local inputs | Two consecutive transform runs produced matching hashes for all five processed outputs; hashes are listed in Section 8 |
| M3/M4: Answer initial analysis questions with beginner SQL and save compact results | Met | `sql/01_lowest_avg_pr.sql`, `sql/02_pr_gap_by_month_hour.sql`, `sql/03_flagged_3h_blocks.sql`, `scripts/run_sql.py`, `output/sql_results/` |
| M4: Create compact descriptive tables and an auditable fixed-seed sample | Met | `scripts/build_insight_tables.py`; `output/tables/` |
| M4: Provide four initial charts and written interpretation | Met | `scripts/insights.py`, `docs/insights.md`, `output/figures/` |
| M4: Provide a runnable notebook-style exploration | Met by the documented script alternative | The criterion is satisfied by `scripts/insights.py` in VS Code `# %%` cell format, together with `docs/insights.md` and `output/figures/`. This choice is explicit: the project is implemented and run as plain scripts, not as a Jupyter notebook. |
| M4: Compare module temperature with PR using paired observations | Not fully met | The compact allowed tables do not contain paired module-temperature and PR observations. `scripts/insights.py` and `docs/insights.md` state this limitation rather than report an invalid correlation. |

## 3. Removed or Archived

| Item | Reason | Replacement or disposition |
| --- | --- | --- |
| Dashboard-specific site and publishing workflow | Outside the M3/M4 beginner analysis scope | Supporting source artifacts retained under `archive/`; analysis tables are kept under `output/tables/` |
| `archive/project_queries.sql` legacy queries | Superseded by focused SQLite-compatible questions | `sql/01_lowest_avg_pr.sql`, `sql/02_pr_gap_by_month_hour.sql`, `sql/03_flagged_3h_blocks.sql` |
| `archive/notebooks/` empty notebook and placeholder | Avoid shipping `.ipynb` while retaining the documented script workflow | `scripts/insights.py` in VS Code `# %%` sections, `docs/insights.md`, and `output/figures/` |
| Legacy daily summary with unreconciled values | No verified generator or reconciliation | Use the regenerated monthly summary and documented compact M4 tables |

Raw files in `data/raw/` were retained. No raw file is deleted by the transform.

## 4. Added

- `scripts/run_sql.py` and the three beginner SQL queries.
- `scripts/build_insight_tables.py` for chunked table generation from existing processed CSVs.
- `scripts/insights.py` for repeatable summary printing and chart generation without a notebook runtime.
- `output/tables/` compact tables, including the fixed-seed 100,000-row gzip scatter sample.
- `output/sql_results/` query results and `output/figures/` four PNG charts.
- `docs/schema.md`, `docs/methodology.md`, `docs/cleaning_log.md`, `docs/insights.md`, and this update record.

## 5. Simplified

The current transformation uses a single modeled inverter table and derives the SQL-ready table from it, avoiding a separate duplicate AC/PR calculation path.

Before, a generated key was used to match each weather row with each inverter:

```python
weather["key"] = 1
inverters["key"] = 1
metrics = weather.merge(inverters, on="key")
```

After, pandas expresses the intended all-pairs relationship directly:

```python
metrics = weather.merge(inverters, how="cross")
```

Before, fault windows were loaded through a separate JSON config. After, the three deterministic educational scenarios are an inline `FAULT_WINDOWS` list near the transform constants, keeping this small beginner pipeline self-contained.

Plant, module, inverter, and thermal assumptions are defined once near the top of `scripts/transform.py` and reused in the calculations.

Validation was added or made explicit for expected column order, hourly and expanded row counts, datetime and integer types, required missing values, the composite key, the 0 to 60 kW AC range, valid fault offsets, nighttime-null and daytime-non-null PR, and basic weather and PR ranges.

## 6. File-by-File Walkthrough

1. `scripts/ingest.py` requests the historical Open-Meteo hourly weather and validates coverage before saving.
2. `data/raw/open_meteo_raw.json` is the retained source response. Keep raw inputs unchanged so the transformation can be repeated.
3. `scripts/transform.py` renames and cleans weather fields, derives modeled module/inverter metrics, applies the inline test fault windows, validates results, and writes processed outputs.
4. `data/processed/` contains cleaned weather, detailed computation data, the five-column SQL-ready inverter-hour file, a small sample, and monthly aggregates. The main table grain is one row per inverter per hour; its composite key is `INVERTER_ID` plus `DATE_TIME`.
5. `sql/` contains three SQLite questions: lowest mean daytime PR, PR gap by month/hour, and qualifying rolling three-hour blocks with severity tiers.
6. `scripts/run_sql.py` loads the large SQL-ready CSV to a gitignored local SQLite database in chunks and writes query results.
7. `scripts/build_insight_tables.py` streams the processed CSVs in chunks and writes compact hourly, monthly, fault-day, severity, sample, and summary-statistic tables.
8. `output/tables/` stores those compact tables. The scatter sample contains exactly 100,000 rows and is gzip-compressed to stay below the size limit.
9. `scripts/insights.py` reads compact outputs, prints summary and inference results, and creates the four charts. Its VS Code `# %%` sections can run as one Python script or cell by cell.
10. `output/figures/` contains the hourly PR, monthly group PR, fault-day PR, and irradiance versus AC power charts.
11. `docs/insights.md` provides chart interpretation, cautious inference, and limitations for the GitHub-facing M4 deliverable.

## 7. Concepts to Study

- CSV ingestion, column renaming, timestamp parsing, and data types.
- Data grain, composite keys, group-by aggregation, and null counts.
- Why ratios with zero denominators are undefined and should not be imputed as zero.
- Pandas cross joins, chunked CSV reads, and deterministic random sampling.
- SQL aggregation, date/time grouping, self-joins, and severity classification.
- Descriptive statistics, weighted means, scatter plots, and correlation limitations.
- Reproducibility checks using SHA-256 hashes and validation assertions.
- The difference between simulated test events and observed operational evidence.

## 8. How to Run and Verify

Install dependencies and run these commands from the repository root:

```powershell
python -m pip install -r requirements.txt
python scripts/ingest.py
python scripts/transform.py
python scripts/run_sql.py
python scripts/build_insight_tables.py
python scripts/insights.py
```

The ingestion command requires network access. The transform consumes the retained raw JSON after ingestion. The SQL and insight scripts run from the generated processed data. The transform is intentionally not required to run for each chart-only edit.

Two consecutive transform executions completed successfully and yielded identical SHA-256 hashes for each processed output:

| File | SHA-256 |
| --- | --- |
| `data/processed/open_meteo_cleaned.csv` | `DF7A74403AF20F611D6BAAEC110EE53A5589E27590609E359F4DF4F1CCD912C1` |
| `data/processed/open_meteo_computation.csv` | `7459EC2BE9E90B2B530788273729C3EDD8013EDA8ACE9216B70EB885665AA73D` |
| `data/processed/processed_inv_metrics.csv` | `674086F246EA9032FCEA4520FE3997304B23C87F8655730383A2C11A778DD045` |
| `data/processed/sample_processed_inv_metrics.csv` | `B8C35033900DB02D64F8A63AB72DAC5DA41CADC2D3426EA21A815D21B20F242F` |
| `data/processed/monthly_inv_summary.csv` | `DC22AE0910D3147C01FA0C4B7B9D7B13B903455B11CBF1114B025C82A2C5F7E4` |

The large computation and metrics hashes match the previously recorded baseline hashes. These results establish repeatability for the current local raw input and Python environment, not for every API response or platform.

## 9. Assumptions and Open Questions

- `n_module` is a float in code, not the integer 242. The configured calculation evaluates to approximately 242.1113 modules per inverter. No rounding is applied. The earlier requested approximate note of 242.4 does not equal the implemented constants and formula; numeric model outputs were not changed to force that value.
- The inverter temperature and three fault windows are synthetic demonstrations. They are not measurements of actual faults.
- Open-Meteo data is model/reanalysis data, not an on-site sensor record.
- The project uses the plain Python `scripts/insights.py` file in VS Code `# %%` cell format instead of a `.ipynb`. This deliberate choice preserves the script-based workflow; the written report and committed figures provide the M4 deliverable.
- No compact input currently provides paired module temperature and PR values for a valid correlation. A future paired sample can support that check without loading the full computation file interactively.
- A single public README and compact outputs support basic review, but no live dashboard or forecasting model is included in this M3/M4 scope.

The dependency file covers all third-party imports used by active scripts: `requests`, `pandas`, and `matplotlib`. `sqlite3` is part of Python's standard library. The only other third-party import found is `duckdb` in the archived `archive/scripts/publish_artifacts.py`, which is outside the active beginner workflow. No Jupyter, `nbformat`, or `ipykernel` dependency is declared. `.gitignore` excludes raw JSON, local databases, large regenerable files, Python caches, and `.ipynb` files while allowing the intended small review artifacts.

The final audit found no tracked file over 50 MB, no machine-specific absolute paths in project text, and no remaining `.ipynb` file in the repository. The paired module-temperature and PR correlation is the only criterion not fully met because no allowed compact input contains those paired observations.
- The requested README run-command update is also not fully met: the historical README is restored from `main`, but workspace edit attempts failed to replace its existing Getting Started section. Its original problem statement is preserved. The commands are available in this section and were executed as part of verification where applicable.

## M5 Path Choice

Path B is selected because the available project data has no predictive target worth modeling. The demonstrated fault events are injected by a fixed rule (Formula F), so a predictive model would only relearn that rule rather than discover an independently observed failure pattern. Phase 2 also has no real inverter-failure labels for supervised learning. The next analysis should remain descriptive and non-predictive until representative operational failure labels are available.
