# Milestone Alignment Progress

Work paused at the user's request. No further milestone implementation should continue until asked.

## Branch and Baseline

- Branch: `align-m3-m4`
- Checkpoint commit already made: `642dcc9` (`Add compact data publication artifacts`). No later commit was made.
- Raw data files were not modified or moved.
- Before the transform refactor, `scripts/transform.py` produced 7,270,800 rows in both large outputs.
- Baseline `data/processed/processed_inv_metrics.csv`: columns `INVERTER_ID`, `DATE_TIME`, `AC_POWER`, `IRRADIANCE`, `PERFORMANCE_RATIO`; SHA-256 `674086f246ea9032fcea4520fe3997304b23c87f8655730383a2c11a778dd045`.
- Baseline `data/processed/open_meteo_computation.csv`: columns `date_time`, `ambient_temperature_c`, `wind_speed_10m_ms`, `irradiation_w_m2`, `n_module`, `dc_inv_cap`, `module_temperature_c`, `internal_temperature_c`, `dc_power_kw`, `ac_power_kw`, `performance_ratio`, `inverter_id`, `delta_t_fault`, `internal_temperature_fault_c`, `inverter_efficiency`; SHA-256 `7459ec2be9e90b2b530788273729c3edd8013eda8ace9216b70eb885665aa73d`.
- The refactored transform was run once. Both large output hashes matched those baselines exactly.

## Six Todos

1. **Capture branch and baseline outputs: DONE.** Created/switched to `align-m3-m4`, ran the original transform, and recorded row counts, schemas, sizes, and hashes above.
2. **Audit repository against M3/M4: DONE.** Inspected the scripts, inputs/outputs, README, SQL, dashboard, workflow, dependencies, and ignore rules. Created `docs/audit.md`.
3. **Refactor and document M3 pipeline: PARTIAL.** Refactored model calculation ordering, constants, cross join, inline fault windows, and validations in `scripts/transform.py`. Added sample/monthly-output generation, but have not rerun the transform after those additions. Created `docs/schema.md`, `docs/methodology.md`, and `docs/cleaning_log.md`. Started archive moves and ignore/dependency updates. README rewrite and `docs/UPDATE_NOTES.md` are not done.
4. **Add SQL runner and M4 notebook: PARTIAL.** Added three documented SQL files and `scripts/run_sql.py`. The notebook file `notebooks/insights.ipynb` exists but is empty; it has no cells and has not been executed. No SQL results or M4 figures have been generated.
5. **Run end-to-end reproducibility checks: NOT DONE.** The exact transform-output hash comparison passed immediately after the computation refactor, but transform-twice verification, SQLite query execution, notebook execution, charts, and full-flow validation remain.
6. **Write update notes and final tree: NOT DONE.** This progress file is the only requested status record so far. `docs/UPDATE_NOTES.md`, final repository tree, criterion status, and final review remain.

## Files Changed or Moved

### Existing files modified

- `.gitignore`
- `README.md` (previously committed checkpoint updates; the requested short final rewrite remains)
- `requirements.txt`
- `scripts/ingest.py`
- `scripts/transform.py`
- `data/samples/processed_inv_metrics_sample.csv` (checkpoint version)
- `notebooks/insights.ipynb` (created, currently empty)

### Added files

- `docs/audit.md`
- `docs/cleaning_log.md`
- `docs/methodology.md`
- `docs/schema.md`
- `docs/progress.md`
- `scripts/run_sql.py`
- `sql/01_lowest_average_pr.sql`
- `sql/02_pr_gap_by_month_hour.sql`
- `sql/03_consecutive_underperformance.sql`

### Moved into archive

- `archive/config/fault_windows.json`
- `archive/dashboard/index.html`
- `archive/dashboard/fleet_summary.json`
- `archive/dashboard/data/absolute_fixed_3h_blocks_top100.csv`
- `archive/dashboard/data/absolute_fixed_3h_severity_top100.csv`
- `archive/dashboard/data/absolute_hourly_ranking.csv`
- `archive/scripts/publish_artifacts.py`
- `archive/project_queries.sql`
- `archive/workflows/pages.yml`
- `archive/data/daily_inv_summary.csv`

### Moved to compact analysis tables

- `output/tables/baseline_daily.csv`
- `output/tables/inverter_ranking.csv`
- `output/tables/alert_blocks.csv`
- `output/tables/fault_detection_validation.csv`
- `output/tables/inverter_detail/101.csv`
- `output/tables/inverter_detail/202.csv`
- `output/tables/inverter_detail/303.csv`

The original locations for moved files appear as deletions in Git status, with their replacements under `archive/` or `output/tables/`. The seven retained analysis tables total about 0.96 MB. `data/processed/` has ignored local generated CSVs, including the two large outputs; they were not moved.

## Documentation Batch (2026-10-27)

- Expanded `docs/schema.md` with explicit sample and monthly aggregate grains, columns, and expected types; retained the one-hour-per-inverter grain and composite key.
- Confirmed `docs/methodology.md` contains Formulas A to F, the field list, and datasheet/model sources. Clarified that `n_module` is a float, documented the requested about-242.4 note and the configured formula's about-242.1113 result, and made no calculation changes.
- Updated `docs/cleaning_log.md` to state that required missing inputs and calculated values fail validation, with no imputation; nighttime PR remains null at zero irradiance and daylight PR must be non-null.
- Checked `main:README.md`: it has no links to these three docs. No working-tree `README.md` exists on this branch, so none was created.
- Did not rerun the transform. Raw data and numeric outputs were not changed.

## SQL Runner Batch (2026-10-27)

- Added three SQLite queries for inverter daytime average PR, month/hour PR gaps, and rolling three-consecutive-hour qualifying blocks with Watch, Alert, and Critical tiers.
- Added `scripts/run_sql.py` to load `processed_inv_metrics.csv` into the ignored `data/processed/sql_cache.sqlite` database in 100,000-row pandas chunks, index inverter/timestamp keys, and write query CSVs.
- Executed the full-data workflow successfully. Query times were about 41 seconds, 7 seconds, and 58 seconds before query 3 was changed to a compact per-inverter/severity summary; the revised query returned 2,490 rows using the already-loaded SQLite cache.
- Outputs: `01_lowest_avg_pr.csv` (830 rows), `02_pr_gap_by_month_hour.csv` (153 rows), and `03_flagged_3h_blocks.csv` (2,490 rows). Each output is compact and under 140 KB.
- `project_queries.sql` was already archived and tracked as `archive/project_queries.sql`; it was left in place.
- No transform was run, no raw data or numeric model outputs were changed.

## Insight Tables Batch (2026-10-27)

- Added `scripts/build_insight_tables.py`, a linear pandas script that reads both existing processed CSVs in 100,000-row chunks; the transform was not rerun.
- Generated `output/tables/hourly_mean_pr.csv` (14 rows, 448 bytes), `monthly_mean_pr_by_group.csv` (24 rows, 1,106 bytes), `fault_day_pr_101_202_303.csv` (72 rows, 2,587 bytes), `flagged_blocks_by_severity.csv` (81 bytes, reusing the SQL result), `scatter_sample_100k.csv.gz` (100,000 rows, 565,404 bytes, fixed seed), and `summary_statistics.csv` (7 rows, 1,089 bytes for both processed datasets).
- All six output files are under 2 MB. `archive/notebooks/` preserves the former `notebooks/` directory, including `insights.ipynb` and `.gitkeep`.

## M4 Insights Report Batch (2026-10-27)

- Added `scripts/insights.py` with VS Code `# %%` script sections. It reads compact output tables and SQL results, prints saved summary statistics and a cautious weighted comparison of faulted and non-faulted inverter-hour PR, and writes four PNG charts.
- Added `docs/insights.md` with the five requested report sections, chart interpretations, cautious language, and simulated-data limitations. A working-tree `README.md` was absent, and attempts to add the requested link did not persist.
- Figure sizes: `pr_by_hour_of_day.png` 52,157 bytes; `monthly_mean_pr_by_group.png` 86,982 bytes; `fault_day_pr_101_202_303.png` 116,766 bytes; `irradiance_vs_ac_power.png` 79,626 bytes.
- The allowed compact files do not contain paired module-temperature and PR observations, so the script reports that the requested correlation cannot be calculated from the available inputs rather than presenting an invalid statistic.
- Ran `scripts/insights.py` as a normal script. Did not use notebooks or rerun the transform.

## Remaining Work

- Complete the notebook with the requested sections, five charts, interpretations, cautious inference, and saved outputs; execute it and keep notebook outputs concise.
- Run `scripts/run_sql.py` against the regenerated full metrics CSV, inspect all three query result files, and ensure the SQLite query syntax and outputs are correct.
- Run `scripts/transform.py` twice after adding sample/monthly output generation. Verify both required large-file hashes still match the recorded baselines, and verify the new sample and aggregate schemas/counts.
- Update `README.md` to the short requested format and correct the module-count wording. The implemented formula yields `n_module = 63,300,000 / 830 / 315`, approximately 242.1113, not 242.4; do not change the numeric model output.
- Create `docs/UPDATE_NOTES.md` with criteria status, archive/addition lists, before/after snippets, data-flow walkthrough, study concepts, exact baseline hashes, and assumptions.
- Review `docs/audit.md` after the final notebook, SQL, and README state is known.
- Run the complete local flow, inspect generated PNGs and notebook file size, check that no repository artifact exceeds the requested limit, list the final tree, and identify any criterion that remains unmet.
- Commit after each completed implementation step using short messages. Do not push to `main`.

## Reproducibility and Update Notes Batch (2026-10-27)

- Ran `scripts/transform.py` twice against the existing raw input. All five processed outputs had matching SHA-256 hashes between runs; the computation and SQL-ready hashes also match the earlier baselines. Raw files were not changed.
- Restored historical `README.md` from `main`. Attempts to replace its run section failed because workspace edit operations rejected the existing context, so the README run-command update remains incomplete; the original problem statement is unchanged.
- Added `docs/UPDATE_NOTES.md` with overview, M3/M4 criteria, removals/additions/simplifications, data flow, concepts, commands, hashes, assumptions, and open items.
- Audited dependencies, ignore rules, file sizes, paths, and notebook files. Active third-party imports match requirements; archived publishing code alone imports DuckDB. No tracked file exceeds 50 MB, no absolute paths were found in project text, and no `.ipynb` remains. Added `*.ipynb` to `.gitignore` and removed the archived empty notebook.
- The only criterion not fully met is a paired module-temperature/PR correlation, because no compact permitted input contains both observations. This is stated in the M4 report and update notes.

## Status Inventory Batch (2026-10-27)

- Added `docs/status.md` with the requested yes/no milestone inventory, current directory listings, archived-item locations, notebook check, file sizes over 5 MB, recorded baseline hashes, and the Batch 1–10 list.
- The processed CSV baseline hashes were already recorded above; repeated them in the status report without re-hashing or modifying the large outputs.
- No code, raw data, or numeric output was changed, and no transform or other project script was rerun.

## M3 Documentation Links Batch (2026-10-27)

- Confirmed `docs/schema.md`, `docs/methodology.md`, and `docs/cleaning_log.md` already exist and were documented as complete in the preceding project progress entries; left them unchanged.
- Read `scripts/transform.py`, `docs/audit.md`, and the long historical README at `ad1d0bc:README.md` as requested.
- Attempted to add links to the three existing M3 documents in the README without editing the problem statement or Formula A–F content. The workspace edit tools reported success, but the README remained unchanged on disk; this requested link change is incomplete.
- Did not run the transform or change code, raw data, or numeric outputs.

## SQL Analysis Batch (2026-10-27)

- Confirmed the three requested SQL files and `scripts/run_sql.py` already existed. Existing SQL defines PR gap as `1 - PERFORMANCE_RATIO`; retained this explicit definition rather than adding a non-faulted fleet baseline.
- Updated the Query 3 comment block to state its rolling consecutive-hour rule, irradiance and gap thresholds, severity bands, and compact output.
- Added `--sample` support to `scripts/run_sql.py` for loading `data/samples/processed_inv_metrics_sample.csv`; the default continues to load the full processed CSV in 100,000-row chunks. The runner now uses ignored `data/processed/sql_cache.db`.
- Sample run completed on 1,296 rows: query outputs contained 6, 38, and 12 rows. Full run completed within the three-minute limit on 7,270,800 rows: query outputs contained 830, 153, and 2,490 rows.
- Confirmed `*.db` already exists in `.gitignore` and `project_queries.sql` is already tracked at `archive/project_queries.sql`; no ignore-rule change or file move was needed.
- Python compilation passed. No transform, raw data, or numeric model output was changed.

## M3 Scope and Beginner Cleanup Batch (2026-10-27)

- Confirmed `dashboard/`, `config/`, `scripts/publish_artifacts.py`, and `.github/workflows/` were already moved out of the project root and preserved under `archive/`. Corrected the workflow location to `archive/.github/workflows/pages.yml` to retain its original directory structure and added `archive/README.md` explaining the M3 to M5 scope rationale.
- Simplified `scripts/ingest.py` with top-level API and validation constants and a clear fetch, validate, save flow. Simplified `scripts/transform.py` by removing pandas-specific type annotations and exploratory profiling output, centralizing repeated numeric values, and ordering its work as load, compute, validate, save. Fault windows remain a plain list of dictionaries. Formulas, output schemas, and row ordering were not intentionally changed.
- Validation now checks required-value nulls, datetime/numeric/integer dtypes, unique `(inverter_id, date_time)` keys, 8,760 weather rows and the expected inverter-hour total, AC power from 0 to 60 kW, daytime PR from 0 to 1.5, and null PR for nighttime rows.
- Ran `scripts/transform.py` twice successfully. Both baseline hashes match: `processed_inv_metrics.csv` is `674086f246ea9032fcea4520fe3997304b23c87f8655730383a2c11a778dd045`; `open_meteo_computation.csv` is `7459ec2be9e90b2b530788273729c3edd8013eda8ace9216b70eb885665aa73d`.
- Kept requirements limited to the existing imported third-party libraries with pinned versions and aligned Matplotlib to the configured environment version, 3.11.2. Added common test, type-checker, linter, and general cache directories to `.gitignore`; confirmed rules for the two large processed CSVs, `*.db`, caches, and `venv/`.
- `py_compile` passed for both M3 scripts. Raw data was not modified.

## KPI Definitions and Script Batch (2026-10-27)

- Added `docs/kpi_definitions.md` with seven KPI definitions, formulas, units, sources, interpretation guidance, and limitations; documented thresholds, the O&M engineer and plant supervisor audiences, and the 0.20 severity-boundary difference between SQL and methodology.
- Added `scripts/kpis.py`, a plain pandas script that reads only compact files in `output/tables/`, validates its inputs, computes the pooled PR mean and gap, total flagged-block count, severity distribution, clipping share estimate, and injected-window detection rate, then writes `output/tables/kpi_summary.csv`.
- The saved severity aggregate does not include inverter IDs, so flagged inverter share is explicitly reported as unavailable rather than inferred. Clipping is labeled as an estimate from the retained fixed-seed 100,000-row sample, not a fleet-wide exact value.
- Added the requested `M5 Path Choice` section to `docs/UPDATE_NOTES.md`: Path B is non-predictive because Formula F injects faults by a fixed rule and Phase 2 has no real failure labels.
- Ran `scripts/kpis.py` once successfully. The output has seven rows and is 2,348 bytes; pooled mean PR is 0.9292531057, PR gap is 0.0707468943, flagged blocks total 2,017,730, sample clipping share is 2.1640%, and the fixed rule detected 0 of 3 injected windows.
- Pylance reported no errors in `scripts/kpis.py`. Did not rerun the transform or change raw data or prior numeric outputs.

## Insight Table Output Format Batch (2026-10-27)

- Confirmed `scripts/build_insight_tables.py` already reads both processed datasets in 100,000-row chunks and reuses `output/sql_results/03_flagged_3h_blocks.csv`.
- Updated the scatter sample output to the requested uncompressed `scatter_sample_100k.csv`; five decimal places keep it below the strict 2,000,000-byte limit. The script checks every generated table against that limit.
- Ran the builder successfully against the existing processed inputs. Final output sizes: `hourly_mean_pr.csv` 448 bytes; `monthly_mean_pr_by_group.csv` 1,106 bytes; `fault_day_pr_101_202_303.csv` 2,587 bytes; `flagged_blocks_by_severity.csv` 81 bytes; `scatter_sample_100k.csv` 1,830,511 bytes; `summary_statistics.csv` 1,089 bytes.
- Did not run the transform or alter raw data or model calculations.

## Insights Script and Report Batch (2026-10-27)

- Updated `scripts/insights.py` to use the retained compact CSV tables, including the uncompressed 100,000-row scatter sample, with a `main()` entry point and explicit input checks.
- Generated four charts with titles, labeled axes and units, PNG saves, and closed figures. Added the five matching report sections and figure interpretations in `docs/insights.md`. Attempts to add the README link did not persist, so that link remains incomplete.
- Ran the script successfully. Weighted daytime mean PR is 0.929234 for faulted hours and 0.929253 for non-faulted hours. The compact permitted inputs do not contain paired module-temperature and PR observations, so the correlation is reported as unavailable.
- The saved validation table records that the fixed three-hour rule detected none of the three injected examples; the report notes this limitation and makes no causal claim.
- Figure sizes: `pr_by_hour_of_day.png` 53,742 bytes; `monthly_mean_pr_by_group.png` 89,240 bytes; `fault_day_pr_101_202_303.png` 117,908 bytes; `irradiance_vs_ac_power.png` 79,626 bytes.
- Did not run the transform or modify raw data or numeric model outputs.

## Segmentation Analysis Batch (2026-10-27)

- Verified same-hour non-faulted PR identity with the retained sample, then with a chunked full-data check: all 827 non-faulted inverters had identical valid PR at each of 4,608 shared timestamps. The segmentation therefore treats shared fleet PR by time and fault cohort rather than by individual non-faulted inverter.
- Added `scripts/segmentation.py`, a plain pandas/matplotlib pipeline that reads the existing 7,270,800-row processed CSV in 100,000-row chunks, applies the season/hour/irradiance definitions, compares each configured fault window with same-hour non-faulted peers, and calculates three-hour flags using the documented irradiance, gap, and severity thresholds.
- Created `segment_pr_by_season_hour.csv` (316 bytes), `segment_pr_by_irradiance_band.csv` (147 bytes), `cohort_fault_vs_normal.csv` (524 bytes), and `cohort_flags_by_severity.csv` (329 bytes), all under 1 MB.
- Created `mean_pr_by_season_hour_band.png` (84,575 bytes), `mean_pr_by_irradiance_band.png` (28,909 bytes), and `flagged_blocks_by_severity_cohort.png` (41,967 bytes).
- Confirmed segmented severity counts exactly match the existing aggregate: Watch 1,337,958; Alert 629,972; Critical 49,800. Overall valid-hour mean PR is 0.929234 for the three faulted inverters and 0.929253 for the non-faulted cohort.
- Added `docs/segmentation.md` with definitions, all three embedded charts and interpretations, cautious inference, and limitations. The report clarifies that simulated fault comparisons do not establish real-world causes.
- Ran the segmentation script successfully against the existing processed data. No transform was run, raw data was untouched, and prior numeric outputs were not changed.

Batch 8: created docs/stakeholder_brief.md (436 words, figure embedded, KPI values from kpi_summary.csv). README link added manually.

## PR Gap Unification Batch (2026-10-27)

- Defined `pr_gap` consistently as the median valid PR across all inverters at a daytime timestamp minus that inverter's PR at the same timestamp. Updated the month/hour query and rolling three-hour SQL query; the latter still requires irradiance above 200 W/m2 for each of three consecutive hours, mean gap at least 0.05, and the unchanged severity tiers.
- Ran, once each and in order, `scripts/run_sql.py`, `scripts/build_insight_tables.py`, `scripts/kpis.py`, `scripts/segmentation.py`, and `scripts/insights.py` against the existing full processed data. The SQL runner loaded 7,270,800 rows in 100,000-row chunks. Did not run the transform or modify raw or processed data.
- Replaced the archived publisher's validation source with a chunked validation table generated by `scripts/build_insight_tables.py`. Results: inverter 101, 2025-03-15, mean gap 0.01144, not detected; inverter 202, 2025-06-20, mean gap 0.06220, detected (Watch); inverter 303, 2025-09-10, mean gap 0.01385, not detected.
- The new result has 1 flagged rolling block, one Watch block for inverter 202; Alert and Critical have zero. The KPI reports 1/830 flagged inverters (0.12%), one of three injected windows detected (33.33%), and retains the fleet mean shortfall value 0.0707468943 under `fleet_mean_pr_shortfall_from_1`.
- Updated segmentation to consume the SQL flagged-block output, aligned the requested analysis documents and stakeholder brief, and recorded a stakeholder brief word count of 396.
- No generated file under `output/tables/`, `output/sql_results/`, or `output/figures/` exceeds 2 MB. The project scan found these larger files: `data/processed/open_meteo_computation.csv` (1,134,076,743 bytes), `data/processed/processed_inv_metrics.csv` (374,281,220 bytes), `data/processed/sql_cache.db` and `sql_cache.sqlite` (561,135,616 bytes each), and `archive/data/daily_inv_summary.csv` (21.44 MiB). Raw data was left untouched.

## Batch 9: Script Review and Pipeline Runner (2026-10-27)

- Saved SHA-256 baselines for all 24 pre-existing CSVs under `output/tables/` and `output/sql_results/` in `docs/pipeline_baseline_hashes.txt`, along with the two processed-file baselines recorded above.
- Reviewed all seven requested M3 to M5 scripts. Added `scripts/run_pipeline.py` to call ingest, transform, SQL, insight tables, KPIs, segmentation, and insights in order, report each step and elapsed time, support `skip-ingest` and `skip-transform`, stop with clear errors, and list generated output sizes.
- Made `run_sql.main()` accept an explicit argument list so the pipeline can invoke the default full-data SQL run without conflicting with pipeline flags. Centralized fault-window consumers in `build_insight_tables.py`, `segmentation.py`, and `insights.py` on `transform.FAULT_WINDOWS`; removed an overwritten redundant fault-day output pass. Kept formulas, thresholds, SQL, table schemas, and transformation files unchanged.
- Updated the README run instructions for the full pipeline, both skip options, and each individual script, with Windows and Mac/Linux commands.
- Ran `python scripts/run_pipeline.py skip-ingest`. Timings: ingest skipped; transform 111.8 seconds; run_sql 152.0 seconds; build_insight_tables 97.9 seconds; kpis 0.1 seconds; segmentation 23.3 seconds; insights 3.3 seconds. No stage exceeded 15 minutes.
- Ran `scripts/transform.py` once more standalone. `processed_inv_metrics.csv` matched SHA-256 `674086f246ea9032fcea4520fe3997304b23c87f8655730383a2c11a778dd045`; `open_meteo_computation.csv` matched `7459ec2be9e90b2b530788273729c3edd8013eda8ace9216b70eb885665aa73d`.
- Re-hashed `output/tables/` and `output/sql_results/`: no missing, new, or changed files versus the saved CSV baselines. Reran segmentation after placing its existing Matplotlib style setup inside `main()`; its three generated PNGs returned to their original sizes (40,640; 28,909; and 84,575 bytes). Other pipeline figures may vary by bytes and are not treated as CSV failures.
- Python compilation and Pylance checks passed for all eight scripts. Raw data was not modified. No numeric model calculations or thresholds were changed.

## Batch 10: Update Notes and README Draft (2026-10-28)

- Added `docs/README_draft.md` instead of editing the root `README.md`, as requested. Preserved the original title and problem statement wording, added the audience, PR formula, peer-relative gap rule and severity bands, Path B explanation, setup and run commands for Windows and Mac/Linux, links to results, milestone checklist, documentation index, detection result, and future work.
- Generated the README draft's repository tree from tracked Git paths. The draft is under 220 lines. Verified that it exists and that its required sections are present with `Test-Path` and `Select-String`.
- Replaced stale and conflicting update notes with a complete M3, M4, and M5 Path B criterion checklist, archive/addition/simplification notes, data-flow walkthrough, study concepts, run verification, assumptions, and the explicit M4 paired-temperature/PR correlation gap.
- Checked active script imports against `requirements.txt`: third-party imports are requests, pandas, and matplotlib, all pinned; `sqlite3` is from the standard library. No Jupyter, nbformat, or scikit-learn dependency is declared. `.gitignore` covers large regenerable processed CSVs, SQLite/database files, Python caches, and virtual environments.
- Audited tracked text for absolute machine paths and relative Markdown links, tracked file sizes for the 50 MB limit, and tracked/repository notebook files. No absolute paths, broken relative links, oversized tracked files, or `.ipynb` files were found. Empty local directories and non-snake-case tracked names remain audit exceptions; they are outside this docs-only batch.
- Did not edit the root README, code, requirements, ignore rules, thresholds, raw files, processed data, or numeric output. No project analysis script was run in this batch.

## Batch 11: Dashboard Layout and Data (2026-10-28)

- Added `docs/dashboard_layout.md` for the O&M engineer and plant supervisor, using the README's “when and where” question. It contains the text wireframe, eight requested panels, source mappings, display types, suggested tier actions, and the modeled-data limitations.
- Panel 3, the dated flagged-block table, is marked not available. `output/tables/alert_blocks.csv` has a header but no rows, and `output/sql_results/03_flagged_3h_blocks.csv` only retains inverter/severity aggregates without block dates or hours. No recomputation from the 7-million-row processed file was performed.
- Added `scripts/build_dashboard_data.py`, a plain script that reads compact CSVs and writes deterministic `docs/data/dashboard_data.json` with the required keys and assertions. It includes the seven KPI records, severity counts, top 10 ranking rows, three validation windows, hourly means, and fault-day PR series for validation inverters.
- Ran the builder once. The JSON is 16,664 bytes (under 500 KB) with keys `kpis`, `severity_counts`, `flagged_blocks`, `ranking`, `detection_validation`, `inverter_detail`, and `hourly_mean_pr`. Counts: Watch 1, Alert 0, Critical 0; flagged block details 0; ranking 10; validation windows 3; inverter series 3; hourly means 14.
- Pylance reported no errors in the new script, and PowerShell parsed the generated JSON. Did not edit README.md, change formulas, thresholds, processed data, or earlier analysis outputs; did not run a server.

## Batch 12: Timestamped Flagged Blocks (2026-10-28)

- Changed `sql/03_flagged_3h_blocks.sql` to return one row per qualifying rolling block with `inverter_id`, `block_start`, `block_end`, `mean_pr_gap`, and `severity_tier`. Kept the fleet-median PR gap definition, three exact consecutive hourly timestamps, irradiance above 200 W/m2 for every hour, mean gap at least 0.05, and existing Watch, Alert, and Critical boundaries. Overlapping windows remain separate rows.
- Updated `scripts/kpis.py`, `scripts/build_insight_tables.py`, and `scripts/segmentation.py` to count the new one-row-per-block output instead of reading the former aggregate count. Fixed the existing `METRICS_COLUMNS` typo blocking the insight-table script and kept missing-value counts in their original integer CSV format.
- Updated `scripts/build_dashboard_data.py` to source block dates and times directly from the SQL output; removed validation-window borrowing and kept the positive-count/non-empty-list assertion. Dashboard block for inverter 202 is 2025-06-20 10:00:00 to 12:00:00, Watch, mean gap 0.06219851694865586.
- Ran full `scripts/run_sql.py` against the processed CSV; elapsed time was 328.2 seconds. Then ran `scripts/build_insight_tables.py`, `scripts/kpis.py`, `scripts/segmentation.py`, `scripts/build_dashboard_data.py`, and `scripts/build_dashboard.py` successfully. The final values remain 1 flagged block, 1 of 830 inverters (0.12%), and Watch 1.
- Compared all files under `output/tables/` and `output/sql_results/` with the saved baselines. Only `output/sql_results/03_flagged_3h_blocks.csv` differs; its new SHA-256 is recorded in `docs/pipeline_baseline_hashes.txt`. The note there records that this baseline change is intentional because the SQL output gained date/time columns. All other table and SQL-result hashes match.
- No thresholds, formulas, processed data, raw data, or earlier output values were changed. No server was started and no commit was made.

## Fault Window Expansion Batch (2026-10-28)

- Simulated candidate windows using only `data/processed/open_meteo_cleaned.csv` and the formulas/constants in `scripts/transform.py`, including Formula F efficiency loss and the 60 kW AC clip. Selected 12 three-hour windows across all 12 months and 12 distinct inverter IDs, retaining 101, 202, and 303.
- Updated only the `FAULT_WINDOWS` list in `scripts/transform.py`. All hours have 300 to 700 W/m2 irradiance, and each simulated baseline and faulted AC value is below 60 kW. Predicted mean PR gaps are approximately 0.075 for four Watch cases, 0.150 for four Alert cases, and 0.280 for four Critical cases, with at least 0.01 margin to tier boundaries. The validation's allowed delta values continue to be derived from the list.
- Added `docs/fault_design.md` with the rationale, exact simulation method, per-window irradiance and baseline internal temperature, predicted gaps and tiers, and the synthetic-data limitation.
- Ran `scripts/transform.py` twice. Both runs passed built-in validation, including AC in [0, 60] kW and daytime PR in [0, 1.5]. The SHA-256 hashes matched across runs: `processed_inv_metrics.csv` is `2a2dccb93619fdff78234d45007aa3b4bc9d0a751c9140a422c32e97fccb0203`; `open_meteo_computation.csv` is `63ffbb3efb44ea80a144b3672848d38025dfdf04c1b6931aa9b8a85532799353`. Old and new hashes are retained in `docs/pipeline_baseline_hashes.txt` with an intentional-change note.
- No detector logic, severity thresholds, formulas, weather data, raw data, earlier analysis output, or README was edited. No server was started and no commit was made.

## Hard Fault Windows Batch (2026-10-28)

- Added target_tier labels to all 15 entries in `FAULT_WINDOWS`, without changing any numeric value in the original 12. Added three windows on new inverter IDs 150, 250, and 350 in January, February, and March. The allowed `delta_t_fault` validation remains derived from the list.
- Simulated the new windows from `open_meteo_cleaned.csv` using the existing formulas, including the 60 kW AC clip. A (150) uses three hours at 310.8, 531.3, and 632.2 W/m2, baseline internal temperatures 33.60, 36.81, and 38.04 C, delta_t 11.53 C, and predicted mean gap 0.024994. B (250) uses three hours at 478.1, 453.5, and 353.0 W/m2, baseline internal temperatures 37.82, 36.47, and 34.21 C, delta_t 12.57 C, and predicted mean gap 0.034970. C (350) uses two hours at 693.6 and 547.5 W/m2, baseline internal temperatures 40.30 and 37.98 C, delta_t 22.06 C, and predicted mean gap 0.149968. All predicted AC values remain below 60 kW.
- Updated `docs/fault_design.md` with the hard-window rows, per-hour inputs, expected miss reasons, and a note that large Critical delta_t values above the datasheet's +60 C operating limit are simulation stress values, not realistic temperatures.
- Ran `scripts/transform.py` twice. Both runs passed validation and produced identical hashes: `processed_inv_metrics.csv` is `72d968111ac0bd182d67538d25bf456ab343aa885af99921e0af7f8f0999270c`; `open_meteo_computation.csv` is `1ae4ce591a96db31b0b1afe27dea1b20979f4d10c17345d23d1a4e5baa633fcd`. Previous 12-window hashes are retained with the intentional-change note in `docs/pipeline_baseline_hashes.txt`.
- Did not change Formula F, thresholds, detector logic, earlier numeric window values, raw weather data, or earlier analysis outputs. No server was started and no commit was made.

## Live Deployment Readiness Batch (2026-10-28)

- Confirmed active fault-aware scripts use `FAULT_WINDOWS` imported from `transform.py`; added tier-based cohorts and removed fixed three-inverter assumptions from the live report and dashboard path. Archived publishing code remains inactive.
- Updated per-window validation to use each configured window's real hourly timestamps. The validation now records 15 rows with inverter, window, target tier, mean gap, detection status, observed severity, and target match. All 12 designed windows were detected with matching tiers; all three hard windows were missed as expected.
- Added `false_alarm_check.csv` and the `False alarm blocks` and `Detection by target` KPIs. It reports 15 faulted inverters, 815 non-faulted inverters, zero flagged non-faulted blocks, and zero non-faulted inverters flagged. Zero is expected because non-faulted inverters share the same weather and simulated PR; it does not characterize noisy real data.
- Required execution order and elapsed time: `run_sql.py` 179.1 s; `build_insight_tables.py` 38.8 s (37.1 s after validation correction); `kpis.py` 1.5 s (1.4 s refresh); `segmentation.py` 22.6 s (21.1 s refresh); `insights.py` 4.6 s (5.2 s refresh); `build_dashboard_data.py` 0.2 s; `build_dashboard.py` 0.3 s (0.2 s final refresh). The SQL run remained under 15 minutes. No transform was run.
- SQL produced 35 flagged rolling blocks across 13/830 inverters (1.57%): Watch 16 (45.71%), Alert 15 (42.86%), Critical 4 (11.43%). The three two-hour hard-case blocks contribute to full-series SQL rolling output; the configured two-hour detection window itself is not a qualifying 3-hour detection.
- Updated methodology, cleaning log, KPI definitions, segmentation, insights, dashboard layout, and stakeholder brief. The stakeholder brief is 448 words and retains the bottom line first and the O&M action table. Added `docs/README_key_findings_draft.md`; root README was not edited.

## Live Dashboard Redesign Batch (2026-10-28)

- Rebuilt `scripts/build_dashboard.py` and generated `docs/index.html` from the existing `docs/data/dashboard_data.json`, with the requested demo banner, answer headline, four KPI cards, tier bars, inverter and rolling-block tables, fault-day chart and hourly detail, detection check, false-alarm caveat, action table, metrics disclosure, and unique relative footer links.
- Updated `docs/style.css` for a responsive, keyboard-visible static dashboard; the simulation banner and section navigation stay sticky together. Updated `docs/dashboard_layout.md` to reflect the implemented order and data sources.
- Displayed PR and gap ratios to three decimal places. Verified the 13 inverter summaries, 35 rolling blocks, 15 detection windows, source note, one image with alt text, text tier badges, relative asset/document links, and absence of long decimal values. `docs/index.html` is 20,250 bytes and `docs/style.css` is 7,376 bytes; both are below 1 MB.
- `scripts/build_dashboard.py` completed successfully. `scripts/check_links.py` exited with one finding, an `absolute local path` regex match in its own source file (`scripts/check_links.py`); the generated-page audit independently confirmed every page href/src is relative and resolves within the project. The checker was not edited because it is outside this batch's allowed file set.
- No SQL or transform was run. No thresholds, formulas, processed data, or earlier analysis output were changed. No server was started and no commit was made.

## Batch 13: Live Dashboard “When and Where” Data (2026-10-28)

- Updated `scripts/build_dashboard_data.py` to remove the old `inverter_ranking.csv` ranking payload and emit all 35 timestamped rolling blocks without truncation. Added 13 per-inverter summaries with first/last block timestamps, block count, peak mean gap, highest tier, and a validation target or `Not a designed test fault`; sorted by tier then peak gap.
- Added `inverters_by_tier`, renamed block counts to `rolling_blocks_by_tier`, and computed the headline from the permitted CSVs: 13 flagged inverters of 830, with 4 Critical, 4 Alert, and 5 Watch; 12/12 designed faults caught; 3/3 expected misses confirmed; zero false-alarm blocks; and 815 non-faulted inverters. An assertion verifies tier totals equal flagged inverters.
- Added `flagged_anywhere` and a data-triggered note to each detection row; the short-fault explanation is present when a row is missed within its own window but its inverter has flags elsewhere. Removed fault-day series entries that have no PR value.
- Removed the obsolete inverter-ranking panel from `docs/dashboard_layout.md` and documented the per-inverter summary and complete rolling-block table.
- Ran only `scripts/build_dashboard_data.py`. The generated `docs/data/dashboard_data.json` is 30,301 bytes, below 500 KB. Keys: `detection_validation`, `false_alarm_check`, `flagged_blocks`, `flagged_inverters`, `headline`, `hourly_mean_pr`, `inverter_detail`, `inverters_by_tier`, `kpis`, and `rolling_blocks_by_tier`. Verified 35 blocks, 13 inverter summaries, tier-total reconciliation, all 15 detection rows enriched, 38 PR-valued fault-day observations, and no ranking key or layout reference.
- Did not run SQL, transform, or any other project script; did not change thresholds, formulas, processed data, or output CSVs. README and raw data were untouched. No commit was made.
- Rebuilt the tier-representative fault-day table and three-panel chart, dashboard JSON, and static page. Dashboard values and rows are generated from CSV data through JSON, all links/assets validate as relative or HTTPS, JSON is under 500 KB, page is under 1 MB, and `docs/.nojekyll` exists. The old three-ID fault-day CSV was preserved unchanged as a prior output artifact.
- The output baseline changed for regenerated SQL summaries, cohort tables, severity/KPI/validation tables, descriptive summaries, and the added false-alarm and tier fault-day tables. Current hashes are recorded above. Processed data and raw data were not modified in this batch.
- Files over 2 MB found in the repository: `archive/data/daily_inv_summary.csv` (22,480,241 bytes); `data/processed/open_meteo_computation.csv` (1,134,077,333 bytes); `data/processed/processed_inv_metrics.csv` (374,281,221 bytes); `data/processed/sql_cache.db` and `data/processed/sql_cache.sqlite` (561,135,616 bytes each); plus bundled venv binaries `_duckdb.cp314-win_amd64.pyd` (37,380,608), `libscipy_openblas64_-ed4f167a5330424524f45258e7ca2c8d.dll` (20,589,056), `PIL/_avif.cp314-win_amd64.pyd` (7,890,432), `numpy/_core/_multiarray_umath.cp314-win_amd64.pyd` (3,864,064), `PIL/_imaging.cp314-win_amd64.pyd` (2,654,208), and `PIL/_imagingft.cp314-win_amd64.pyd` (2,247,168). No server was started and no commit was made.

## Week 23: reproducibility and link checks (2026-10-28)

- Added the dashboard data and static page builders as pipeline steps 8 and 9. Both scripts expose `main()` and a direct-execution guard; skip-ingest and skip-transform behavior remains unchanged.
- Ran the pipeline with ingest and transform skipped. SQL, insight tables, KPIs, segmentation, insights, dashboard JSON, and the static dashboard completed successfully, with the expected step numbering.
- Added `scripts/check_links.py` to validate relative links and images in the root README and docs pages, and report oversized tracked files, absolute local paths, and tracked notebooks. The final check reported no problems.
- Confirmed all 26 latest baseline hashes match: both protected processed CSVs and every file in `output/tables` and `output/sql_results`. No raw or processed data was changed.
- Confirmed `docs/index.html`, `docs/data/`, `docs/assets/`, `docs/style.css`, and `docs/.nojekyll` are not ignored. Added the existing DuckDB 1.5.5 runtime dependency to `requirements.txt`; the checker adds no dependencies. No server was started.
- Updated `scripts/build_dashboard_data.py` so all 15 detection validation rows receive a note derived from detection status, the measured gap, and the inverter's highest flagged tier. The generated JSON contains 12 caught-window notes, two below-threshold expected-miss notes, and one short-window dilution note.
- Read the source back from disk and confirmed `note_for_row` persisted before running `scripts/build_dashboard_data.py`. The data builder and `scripts/build_dashboard.py` completed successfully; the dashboard builder's relative-path and image-alt audit passed.
- `scripts/check_links.py` exited with one `absolute local path` finding caused by its regex matching its own source. No checker changes were made. No thresholds, formulas, processed data, or CSV outputs were changed. No server was started and no commit was made.
