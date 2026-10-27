# Segmentation Analysis

## Inverter-Hour PR Identity Check

A chunked comparison of the full processed dataset found identical valid PR values across non-faulted inverters for every shared hour: 827 non-faulted inverters, 4,608 valid timestamps, and zero timestamps with differing PR. Therefore, the fleet-level segmentation is by time and fault cohort, not by individual non-faulted inverter. The fault cohort comparisons remain separate because injected faults alter the modeled inverter-hour PR.

## Definitions

- **Season:** Dry is December through May; Wet is June through November.
- **Hour band:** Morning is 06:00–09:00, midday is 10:00–14:00, and afternoon is 15:00–18:00. Other hours are excluded from this table; PR is null for modeled nighttime rows.
- **Irradiance band:** 0–200, above 200 through 600, and above 600 W/m². Bands use the row's plane-of-array irradiance. PR means use valid, non-null PR rows.
- **Cohort:** Faulted inverters are 101, 202, and 303; all other 827 inverters form the non-faulted cohort. Overall cohort means use all valid PR rows. Each fault-window comparison uses its configured three-hour window and non-faulted rows at the same timestamps.
- **Flagged blocks:** Rolling sets of three consecutive hourly records, each with irradiance above 200 W/m² and non-null PR. A qualifying block has a three-hour mean PR gap of at least 0.05, where gap is `1 - mean PR`. Severity is Watch for gaps from 0.05 to below 0.10, Alert from 0.10 through 0.20, and Critical above 0.20. Counts include overlapping rolling windows.

## Mean PR by Season and Hour Band

![Mean performance ratio by season and hour band](../output/figures/mean_pr_by_season_hour_band.png)

Mean PR is higher in the morning than midday in both seasons, and the midday mean is the lowest of the three hour bands. Wet-season means are modestly above dry-season means in each band; this is a descriptive difference in the modeled year, not evidence that season caused the change.

## Mean PR by Irradiance Band

![Mean performance ratio by irradiance band](../output/figures/mean_pr_by_irradiance_band.png)

The saved means decline from 0.968 in the 0–200 W/m² band to 0.937 in the 200–600 band and 0.886 above 600 W/m². The lowest-irradiance band includes valid PR values and should not be read as nighttime performance, since nighttime PR is undefined and excluded.

## Flagged Blocks by Severity and Fault Cohort

![Flagged blocks by severity per fault cohort](../output/figures/flagged_blocks_by_severity_cohort.png)

The three fault cohorts each have roughly 1,610 Watch blocks, 759–761 Alert blocks, and 60 Critical blocks, while the much larger non-faulted cohort contributes most blocks in absolute terms. Counts are rolling windows rather than unique events, and the cohort totals reconcile to the existing fleet severity aggregate.

## Cautious Inference

Across all valid PR rows, the three faulted inverters have mean PR 0.929234 and the non-faulted cohort has mean PR 0.929253. Within the injected windows, inverters 101 and 202 have lower mean PR than their non-faulted same-hour peers, while inverter 303 is also lower but by a smaller amount; these comparisons are consistent with the deliberately simulated faults, but do not establish a real-world fault signature or causal effect.

## Limitations

These are descriptive summaries of modeled weather and simulated fault windows, not real equipment measurements or maintenance thresholds. The overall faulted cohort contains only three inverters, each window contains three valid hourly PR rows, and its peer comparison has thousands of rows; the observations therefore have different cohort sizes. Seasonal comparisons cover one modeled calendar year, irradiance bands have different row counts, and overlapping flagged blocks are not independent events. The threshold tiers are demonstration rules and should not be used as validated operational limits.