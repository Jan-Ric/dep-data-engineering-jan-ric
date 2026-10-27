# Project Status Inventory

Inventory checked on 2026-10-27. This records file and directory presence, not a code review or rerun of project scripts.

## Milestone Items

| item | exists (yes/no) | notes |
| --- | --- | --- |
| `scripts/ingest.py` | yes | Open-Meteo ingestion script. |
| `scripts/transform.py` | yes | Data cleaning, computation, validation, and output script. |
| `scripts/run_sql.py` | yes | SQLite query runner. |
| `sql/` (3 queries) | yes | Three milestone queries exist: `01_lowest_average_pr.sql`, `02_pr_gap_by_month_hour.sql`, and `03_consecutive_underperformance.sql`. Two additional SQL files also remain. |
| `docs/schema.md` | yes | Dataset schema and lineage documentation. |
| `docs/methodology.md` | yes | Method and formula documentation. |
| `docs/cleaning_log.md` | yes | Cleaning and validation decisions. |
| `output/sql_results/` | yes | Contains three CSV query results. |
| `scripts/build_insight_tables.py` | yes | Builds compact insight tables. |
| `output/tables/` | yes | Contains summary, ranking, fault, sample, and detail tables. |
| `scripts/insights.py` | yes | Builds and reports initial descriptive insights. |
| `docs/insights.md` | yes | Initial insights report. |
| `output/figures/` (count PNGs) | yes | 4 PNG files; `.gitkeep` is not counted. |
| `scripts/kpis.py` | no | Not present. |
| `docs/kpi_definitions.md` | no | Not present. |
| `scripts/segmentation.py` | no | Not present. |
| `docs/segmentation.md` | no | Not present. |
| `docs/stakeholder_brief.md` | no | Not present. |
| `scripts/run_pipeline.py` | no | Not present. |
| `docs/UPDATE_NOTES.md` | yes | Update notes exist. |
| `requirements.txt` | yes | Dependency list exists. |
| `.gitignore` | yes | Ignore rules exist. |

## Directory Inventory

- `scripts/`: `ingest.py`, `transform.py`, `run_sql.py`, `build_insight_tables.py`, and `insights.py` (plus local `__pycache__/`).
- `sql/`: `01_lowest_average_pr.sql`, `01_lowest_avg_pr.sql`, `02_pr_gap_by_month_hour.sql`, `03_consecutive_underperformance.sql`, and `03_flagged_3h_blocks.sql`.
- `docs/`: `audit.md`, `cleaning_log.md`, `insights.md`, `methodology.md`, `progress.md`, `schema.md`, `UPDATE_NOTES.md`, and this `status.md`.
- `data/`: `processed/`, `raw/`, and `samples/`. `processed/` contains `.gitkeep`, `monthly_inv_summary.csv`, `open_meteo_cleaned.csv`, `open_meteo_computation.csv`, `processed_inv_metrics.csv`, `sample_processed_inv_metrics.csv`, and `sql_cache.sqlite`. `raw/` contains `.gitkeep`, `open_meteo.json`, and `open_meteo_raw.json`. `samples/` contains `processed_inv_metrics_sample.csv`.
- `output/`: `figures/`, `sql_results/`, and `tables/`. `figures/` has four PNGs and `.gitkeep`; `sql_results/` has `01_lowest_avg_pr.csv`, `02_pr_gap_by_month_hour.csv`, and `03_flagged_3h_blocks.csv`. `tables/` has `alert_blocks.csv`, `baseline_daily.csv`, `fault_day_pr_101_202_303.csv`, `fault_detection_validation.csv`, `flagged_blocks_by_severity.csv`, `hourly_mean_pr.csv`, `inverter_ranking.csv`, `monthly_mean_pr_by_group.csv`, `scatter_sample_100k.csv.gz`, `summary_statistics.csv`, and `inverter_detail/`.
- `archive/`: `project_queries.sql`, plus `config/`, `dashboard/`, `data/`, `notebooks/`, `scripts/`, and `workflows/`. Archived items include `config/fault_windows.json`, dashboard files, `data/daily_inv_summary.csv`, `notebooks/.gitkeep`, `scripts/publish_artifacts.py`, and `workflows/pages.yml`.
- Root `notebooks/`: missing.
- Root `dashboard/`: missing; archived copy is under `archive/dashboard/`.
- Root `config/`: missing; archived copy is under `archive/config/`.
- Root `.github/`: missing, therefore `.github/workflows/` is missing; the old workflow is at `archive/workflows/pages.yml`.

## Additional Checks

- Leftover `.ipynb` files: none found in the project tree.
- `dashboard/`: absent at the root; preserved as `archive/dashboard/`.
- `config/`: absent at the root; preserved as `archive/config/`.
- `.github/workflows/`: absent; preserved workflow is `archive/workflows/pages.yml`.
- `scripts/publish_artifacts.py`: absent at the root; preserved as `archive/scripts/publish_artifacts.py`.
- Files over 5 MB (decimal bytes and binary MiB):

| file | size |
| --- | ---: |
| `data/processed/open_meteo_computation.csv` | 1,134,076,743 bytes (1,081.54 MiB) |
| `data/processed/sql_cache.sqlite` | 561,135,616 bytes (535.14 MiB) |
| `data/processed/processed_inv_metrics.csv` | 374,281,220 bytes (356.94 MiB) |
| `archive/data/daily_inv_summary.csv` | 22,480,241 bytes (21.44 MiB) |
| `venv/Lib/site-packages/_duckdb.cp314-win_amd64.pyd` | 37,380,608 bytes (35.65 MiB) |
| `venv/Lib/site-packages/numpy.libs/libscipy_openblas64_-ed4f167a5330424524f45258e7ca2c8d.dll` | 20,589,056 bytes (19.64 MiB) |
| `venv/Lib/site-packages/PIL/_avif.cp314-win_amd64.pyd` | 7,890,432 bytes (7.52 MiB) |

## Recorded Baseline Hashes

Both baseline SHA-256 values were already recorded in `docs/progress.md`; they are repeated here without re-hashing or changing the large outputs.

| file | recorded SHA-256 |
| --- | --- |
| `data/processed/processed_inv_metrics.csv` | `674086f246ea9032fcea4520fe3997304b23c87f8655730383a2c11a778dd045` |
| `data/processed/open_meteo_computation.csv` | `7459ec2be9e90b2b530788273729c3edd8013eda8ace9216b70eb885665aa73d` |

## Batches Needed

1. Batch 1: M3 docs
2. Batch 2: M3 SQL
3. Batch 3: cleanup and code review
4. Batch 4: M4 tables
5. Batch 5: M4 insights
6. Batch 6: M5 KPIs
7. Batch 7: M5 segmentation
8. Batch 8: M5 brief
9. Batch 9: M5 pipeline
10. Batch 10: final polish