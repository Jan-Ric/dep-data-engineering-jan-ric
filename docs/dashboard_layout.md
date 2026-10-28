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
| Flagged blocks | Flagged inverter share | Detection rate | False alarms | Detection by target | Mean PR |
+------------------------------------------------------------------+
| Fleet status by severity: Watch | Alert | Critical                 |
+------------------------------------------------------------------+
| When and where: flagged blocks table                              |
| Inverter | Date | Start | End | Mean gap | Tier                    |
+------------------------------------------------------------------+
| Inverter ranking: top 10 by lowest mean PR or largest gap          |
+------------------------------------------------------------------+
| Investigation: three representative tier fault-day panels           |
+------------------------------------------------------------------+
| Detection check: all injected windows | Target | Mean gap | Detected | Tier match |
| False-alarm check: non-faulted inverter flags                         |
+------------------------------------------------------------------+
| What to do: Watch | Alert | Critical                               |
+------------------------------------------------------------------+
| Limits and links                                                    |
+------------------------------------------------------------------+
```

## Panels

| panel | question it answers | KPI or table | source file | display type |
| --- | --- | --- | --- | --- |
| 1. Headline and KPI cards | What is the overall scale of flags, flagged fleet share, test detection, false alarms, and mean PR? | Flagged 3-hour blocks; flagged inverter share; fault detection rate; false alarm blocks; detection by target; pooled mean PR | `output/tables/kpi_summary.csv` | CSV-backed KPI cards |
| 2. Fleet status by severity | How many saved blocks are Watch, Alert, or Critical? | Severity-tier block counts | `output/tables/flagged_blocks_by_severity.csv` | Three labeled counts; include tier names so meaning is not carried by color |
| 3. When and where | Which inverter was flagged, and when did its block occur? | Inverter, date, start time, end time, mean gap, tier | `output/sql_results/03_flagged_3h_blocks.csv` provides the saved inverter, tier, and gap aggregate. The matching detected window in `output/tables/fault_detection_validation.csv` supplies date and times. | Accessible table; show up to 50 rows ordered by largest mean gap, with an explicit note that overlapping rolling blocks count separately |
| 4. Inverter ranking | Which inverters have the lowest mean PR or largest saved gap? | Top 10 rows in the existing mean-PR ranking | `output/tables/inverter_ranking.csv` | Accessible ranked table |
| 5. Investigation | What does hourly PR look like in each designed tier? | One representative Watch, Alert, and Critical fault day | `output/tables/fault_day_pr_by_tier.csv` | Three small labeled panels and an accessible table alternative |
| 6. Detection check | Which designed windows were detected, and were hard cases missed as expected? | All 15 fault-window validation rows, including target tier and target-match status | `output/tables/fault_detection_validation.csv` | Table with detected and target-match status written as text |
| 7. False-alarm check | Did any non-faulted inverter get flagged? | Counts on the 815 non-faulted inverters | `output/tables/false_alarm_check.csv` | Plain-language check with explicit identical-simulation limitation |
| 8. What to do | What follow-up is suggested for each demonstration tier? | Watch: remote check, log, monitor for 24 hours. Alert: attempt remote reset and schedule a site visit within 72 hours. Critical: likely hardware fault, dispatch immediately. | `docs/stakeholder_brief.md` | Three action rows with tier labels and text |
| 9. Limits and links | What should readers not infer, and where can they inspect methods and definitions? | Modeled data, simulated faults, demonstration thresholds, and links to KPI definitions, segmentation, stakeholder brief, and source tables | `docs/kpi_definitions.md`, `docs/segmentation.md`, `docs/stakeholder_brief.md`, and the listed CSV sources | Plain-language note and relative links |

Panel 3 uses timestamped rows from `output/sql_results/03_flagged_3h_blocks.csv`; no dates or times are borrowed from validation windows. KPI values, detection rows, and false-alarm counts flow from generated CSVs through `docs/data/dashboard_data.json`; the HTML generator does not type result values by hand. Zero false alarms are expected because non-faulted inverters share identical simulated weather and PR, and do not test noisy real data.