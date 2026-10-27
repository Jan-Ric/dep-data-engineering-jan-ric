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
