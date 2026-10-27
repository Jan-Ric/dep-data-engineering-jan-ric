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
