# Dashboard Layout Plan

## Audience

- **Primary:** O&M engineer, reviewing flagged inverter-hours and deciding which records need follow-up.
- **Secondary:** Plant supervisor, scanning fleet-level status and the limits of the analysis.

## Question

“When and where are those inverters that have negative performance ratio gaps in a solar power plant?”

## Text Wireframe

```text
+------------------------------------------------------------------+
| Solar inverter PR monitoring                  Limits | Data links |
+------------------------------------------------------------------+
| Flagged blocks | Flagged inverter share | Detection rate | Mean PR|
+------------------------------------------------------------------+
| Fleet status by severity: Watch | Alert | Critical                 |
+------------------------------------------------------------------+
| When and where: flagged blocks table                              |
| Inverter | Date | Start | End | Mean gap | Tier                    |
+------------------------------------------------------------------+
| Inverter ranking: top 10 by lowest mean PR or largest gap          |
+------------------------------------------------------------------+
| Investigation: fault-day PR series for validation inverters        |
+------------------------------------------------------------------+
| Detection check: injected test window | Mean gap | Detected | Tier  |
+------------------------------------------------------------------+
| What to do: Watch | Alert | Critical                               |
+------------------------------------------------------------------+
| Limits and links                                                    |
+------------------------------------------------------------------+
```

## Panels

| panel | question it answers | KPI or table | source file | display type |
| --- | --- | --- | --- | --- |
| 1. Headline and KPI cards | What is the overall scale of flags, flagged fleet share, test detection, and mean PR? | Flagged 3-hour blocks; flagged inverter share; fault detection rate; pooled mean PR | `output/tables/kpi_summary.csv` | Four text-and-number KPI cards |
| 2. Fleet status by severity | How many saved blocks are Watch, Alert, or Critical? | Severity-tier block counts | `output/tables/flagged_blocks_by_severity.csv` | Three labeled counts; include tier names so meaning is not carried by color |
| 3. When and where | Which inverter was flagged, and when did its block occur? | Inverter, date, start time, end time, mean gap, tier | `output/sql_results/03_flagged_3h_blocks.csv` provides the saved inverter, tier, and gap aggregate. The matching detected window in `output/tables/fault_detection_validation.csv` supplies date and times. | Accessible table; show up to 50 rows ordered by largest mean gap, with an explicit note that overlapping rolling blocks count separately |
| 4. Inverter ranking | Which inverters have the lowest mean PR or largest saved gap? | Top 10 rows in the existing mean-PR ranking | `output/tables/inverter_ranking.csv` | Accessible ranked table |
| 5. Investigation | What does hourly PR look like on each validation inverter's fault day? | Hourly PR series for validation inverters 101, 202, and 303 | `output/tables/fault_day_pr_101_202_303.csv` | Line chart with one selectable inverter series; retain a table alternative |
| 6. Detection check | Which planted test windows did the rule detect? | Fault-window validation rows | `output/tables/fault_detection_validation.csv` | Table with detected status written as text |
| 7. What to do | What follow-up is suggested for each demonstration tier? | Watch: remote check, log, monitor for 24 hours. Alert: attempt remote reset and schedule a site visit within 72 hours. Critical: likely hardware fault, dispatch immediately. | `README.md` and `docs/stakeholder_brief.md` | Three action rows with tier labels and text |
| 8. Limits and links | What should readers not infer, and where can they inspect methods and definitions? | Modeled data, simulated faults, demonstration thresholds, and links to KPI definitions, segmentation, stakeholder brief, and source tables | `docs/kpi_definitions.md`, `docs/segmentation.md`, `docs/stakeholder_brief.md`, and the listed CSV sources | Plain-language note and relative links |

Panel 3 uses only saved compact analysis tables. Dates and times are shown from a detected validation window matched by inverter ID; no event times are inferred from the 7-million-row processed file.