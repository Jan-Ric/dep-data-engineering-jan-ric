# Initial Insights

## 1. Problem Statement

This analysis asks when inverter-hours fall below the fleet's same-hour PR median. At each timestamp, `pr_gap` is the median valid PR across all inverters minus that inverter's PR. A flag is a rolling set of three consecutive hours, each with valid PR and irradiance above 200 W/m², whose mean `pr_gap` is at least 0.05. The analysis uses compact outputs from modeled 2025 hourly data, not equipment causes.

## 2. Summary Statistics

The saved summary statistics describe 7,270,800 inverter-hour records. Mean AC power is about 15.38 kW and mean plane-of-array irradiance is about 223.1 W/m². Mean PR is about 0.929 across 3,824,640 valid rows; 3,446,160 PR values are null because irradiance is zero at night.

The PR values are unitless, and the null nighttime values are expected because PR has no defined irradiance denominator at zero irradiance. Full descriptive statistics and missing-value counts are in [summary_statistics.csv](../output/tables/summary_statistics.csv).

## 3. Charts

### Mean PR by Hour of Day

![Mean daytime performance ratio by hour of day](../output/figures/pr_by_hour_of_day.png)

Mean daytime PR is higher in the early and later daylight hours and lower around midday. This is a pattern in the modeled hourly summaries; the chart does not identify why it occurs.

### Monthly Mean PR: Faulted and Non-faulted Inverters

![Monthly mean PR by inverter group](../output/figures/monthly_mean_pr_by_group.png)

The monthly faulted and non-faulted group averages are very close across the year. Only three of 830 modeled inverters have injected fault windows, so the monthly group means dilute those few hours and should not be read as a sensitive fault detector.

### PR on the Three Fault Days

![Performance ratio on fault days for inverters 101, 202, and 303](../output/figures/fault_day_pr_101_202_303.png)

The traces show hourly PR for inverter 101 on March 15, inverter 202 on June 20, and inverter 303 on September 10, 2025. The plots provide context around the configured 10:00–12:00 injected windows; the saved validation table reports a detection for inverter 202 only.

### Irradiance and AC Power

![Irradiance and AC power scatter with the 60 kW clip](../output/figures/irradiance_vs_ac_power.png)

AC power generally rises with plane-of-array irradiance, and the horizontal reference line marks the modeled 60 kW rated AC clip. The chart uses the retained fixed-seed sample of 100,000 rows and shows the broad relationship rather than every inverter-hour.

## 4. Cautious Inference

Weighting monthly means by daytime-row counts gives a faulted-hour mean PR of 0.929234 and a non-faulted-hour mean PR of 0.929253. These values are nearly equal, which is consistent with the injected windows making up a small share of all inverter-hours; it does not show that the fixed three-hour detector successfully found the injected examples.

The requested simple correlation between module temperature and PR could not be calculated: the permitted compact tables contain no paired observations of both variables. A correlation cannot be recovered from separate or aggregate summaries. Faults are injected into simulated data, so this analysis checks the detector against test scenarios and does not show real-world causes; no causal claim is made.

## 5. Conclusion and Limitations

The charts describe hourly and monthly PR patterns, PR values around three configured fault windows, and the relationship between irradiance and modeled AC power. The rolling rule flagged one block and detected inverter 202's window; its mean `pr_gap` was 0.06220 (Watch). It did not detect inverter 101's window (0.01144) or inverter 303's window (0.01385).

## Detection Result

The weaker +4°C and +12°C injections may fall below 0.05 because the degradation term starts only above 45°C internal temperature, so the simulated PR effect can be small; here the +4°C example stayed below threshold while the +12°C example crossed it. This reflects the simulation design, not a failure of the method.

These are modeled results based on hourly reanalysis weather and synthetic fault injections, not field measurements of inverter faults. Nighttime PR is undefined because its irradiance denominator is zero. The available compact files do not contain paired module-temperature and PR values, so that correlation remains unmeasured; further conclusions would require paired observations and real plant telemetry.
