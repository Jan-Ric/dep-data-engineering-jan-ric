| Former empty `notebooks/insights.ipynb` | Removed from the repository to keep the project script-only and ensure no `.ipynb` files remain | `scripts/insights.py` in VS Code `# %%` sections, `docs/insights.md`, and `output/figures/` |
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
