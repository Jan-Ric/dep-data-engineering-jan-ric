# Stakeholder Brief: Inverter PR Review

## Question

When do inverter records show sustained shortfalls, and how should O&M respond?

## What we did

We summarized modeled hourly inverter data using performance ratio (PR), which compares AC output with expected output from sunlight and installed capacity. At each daytime timestamp, `pr_gap` is the median valid PR across all inverters minus that inverter's PR. The detector checks rolling sets of three consecutive hours; each must have irradiance above 200 W/m² and valid PR, and their mean `pr_gap` must be at least 0.05.

## What we found

- Mean valid PR was **0.9293**. The separate KPI `fleet_mean_pr_shortfall_from_1` was **0.0707 (7.07 percentage points)** below 1.0; it is not the detector's `pr_gap` or a healthy-fleet comparison.
- There was **1 flagged rolling block**, for inverter 202: **Watch 1 (100%)**, Alert 0, Critical 0. **1 of 830 inverters (0.12%)** had a qualifying block. Overlapping windows count separately.
- **2.1640%** of sampled inverter-hour rows reached the modeled 60 kW AC cap. This expected model cap is not, by itself, evidence of a fault.
- The detector found **1 of 3 simulated windows (33.33%)**: inverter 202 on June 20, 2025. It did not detect inverter 101 on March 15 or inverter 303 on September 10.

![Flagged blocks by severity and fault cohort](../output/figures/flagged_blocks_by_severity_cohort.png)

## Detection result

Window mean gaps were **0.01144** for inverter 101 (not detected), **0.06220** for inverter 202 (detected, Watch), and **0.01385** for inverter 303 (not detected). Severity is Watch from 0.05 to below 0.10, Alert from 0.10 through 0.20, and Critical above 0.20.

The weaker +4°C and +12°C injections may fall below 0.05 because simulated degradation starts only above 45°C internal temperature, so its PR effect can be small. Here +4°C stayed below threshold while +12°C crossed it. This reflects the simulation design, not a failure of the method.

## What to do

Treat tiers as review priorities, not diagnoses. Verify flags against equipment telemetry and operating context before maintenance action. These demonstration thresholds are not validated maintenance limits.

## Limits

Weather and inverter output are modeled, faults are injected, and no real inverter telemetry is included. This three-window check cannot confirm equipment condition or estimate real-world detection performance.

## Next steps

Future work could test the rule with verified operational labels and assess whether validated energy shortfalls relate to revenue. Remaining-life estimates and revenue analysis are outside this descriptive study.