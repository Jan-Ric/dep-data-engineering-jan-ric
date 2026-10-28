# Stakeholder Brief: Which Inverters Need Attention?

For O&M engineers and the plant supervisor. Based on modeled 2025 data for Calatagan Solar Farm (830 inverters).

## Bottom line

Our rule flagged 1 inverter out of 830 and caught 1 of 3 planted test faults. It gives crews a short list to check, not a wall of alarms, but it can miss small faults.

## Why it matters

Inverters last 5 to 10 years, while panels last 25 to 30, and inverters are hard to repair. Crews need to know when and where to look. A rule that flags everything gets ignored: an earlier version compared each inverter with a perfect score of 1.0 and flagged about 2 million blocks. Comparing each inverter with the other inverters at the same hour cut that to 1.

## How the rule works

Performance ratio (PR) compares actual AC output with what sunlight and installed capacity should produce. For each daytime hour, we subtract an inverter's PR from the fleet median PR. If that gap averages 0.05 or more over three hours in a row, and sunlight stays above 200 W/m² in each hour, the inverter is flagged.

## What we found

- **Fleet level:** average PR was 0.929, about 7 points below 1.0. This is a fleet-wide level, not a fault signal.
- **Flagged:** 1 block, inverter 202, Watch level. That is 0.12% of the fleet.
- **Test faults:** 1 of 3 detected. Inverter 202 (June 20) had a gap of 0.062 and was caught. Inverters 101 (gap 0.011) and 303 (gap 0.014) were missed.
- **Power cap:** 2.16% of sampled hours hit the 60 kW limit. This is expected behavior, not a fault.

![Flagged blocks by severity and fault cohort](../output/figures/flagged_blocks_by_severity_cohort.png)

**Why two were missed:** in our model, efficiency only drops once internal temperature passes 45°C, so a fault on a cooler hour barely changes output. This comes from how the test was built, and it also shows that small faults can stay hidden.

## What to do with a flag

| Level    | Gap          | Suggested action                                               |
| -------- | ------------ | -------------------------------------------------------------- |
| Watch    | 0.05 to 0.10 | Check remotely, log it, monitor for 24 hours                   |
| Alert    | 0.10 to 0.20 | Try a remote reset, then schedule a site visit within 72 hours |
| Critical | above 0.20   | Likely hardware fault, dispatch immediately                    |

These thresholds are demonstration values, not validated maintenance limits. Confirm a flag against equipment data before acting.

## Limits

Weather and output are modeled, faults are planted, and there is no real inverter data. Three test windows cannot show real-world detection rates.

## Next steps

Test the rule on real telemetry with confirmed faults, try larger and more varied test faults, then estimate remaining inverter life and revenue impact.
