# Injected Fault Window Design

## Why the list changed

The first three windows were too weak to test all detector and dashboard severity cases. Only the +8 C window on a cool hour crossed the 0.05 gap threshold; the other two were below it, and the set did not exercise Alert or Critical. This change replaces only the fault-window list in `scripts/transform.py`. Formula F, its beta value of 0.01, the 45 C temperature threshold, the PR calculation, weather inputs, detector logic, and severity boundaries remain unchanged.

## Selection method

Candidate hours were simulated from `data/processed/open_meteo_cleaned.csv` using the exact transformation equations: the Faiman module-temperature calculation, derived DC capacity and floating module count, temperature-adjusted DC power, nominal inverter efficiency, Formula F efficiency adjustment, the 60 kW AC clip, and PR from AC divided by irradiance and inverter DC capacity. Predicted `pr_gap` is the mean baseline PR minus faulted PR across each complete window. The listed internal temperatures are baseline values, one per hour.

The first 12 three-hour windows cover all 12 months and use 12 distinct inverter IDs. The three added hard windows use new inverter IDs 150, 250, and 350 in January, February, and March. Every hour in all 15 windows has 300 to 700 W/m2 irradiance. All modeled baseline and faulted AC outputs are below 60 kW, so clipping does not hide the modeled loss. No windows overlap on an inverter. The tier labels on the original 12 windows identify their intended detector severity; the added labels identify two below-threshold expected misses and one too-short expected miss.

| Inverter | Date | Hours | Irradiance per hour (W/m2) | Baseline internal temperature per hour (C) | Trial delta_t (C) | Predicted mean pr_gap | Target tier |
|---:|---|---|---|---|---:|---:|---|
| 101 | 2025-01-22 | 14:00-16:00 | 626.2, 468.1, 396.4 | 39.03, 36.64, 34.99 | 16.14 | 0.07497 | Watch |
| 118 | 2025-02-21 | 14:00-16:00 | 660.4, 583.0, 330.2 | 39.13, 37.83, 33.53 | 16.21 | 0.07498 | Watch |
| 202 | 2025-03-11 | 15:00-17:00 | 673.8, 496.8, 309.0 | 42.72, 39.53, 36.57 | 13.53 | 0.07496 | Watch |
| 303 | 2025-04-17 | 15:00-17:00 | 693.4, 521.1, 302.5 | 43.90, 40.96, 36.39 | 12.77 | 0.07500 | Watch |
| 404 | 2025-05-19 | 08:00-10:00 | 337.3, 509.2, 649.3 | 36.07, 39.17, 41.50 | 22.29 | 0.15000 | Alert |
| 505 | 2025-06-25 | 08:00-10:00 | 309.7, 502.7, 695.4 | 35.47, 43.36, 49.57 | 18.81 | 0.15001 | Alert |
| 606 | 2025-07-08 | 14:00-16:00 | 472.8, 643.4, 393.0 | 35.86, 37.86, 34.72 | 24.85 | 0.15002 | Alert |
| 707 | 2025-08-21 | 14:00-16:00 | 508.3, 586.5, 370.0 | 41.33, 42.49, 37.44 | 20.89 | 0.15001 | Alert |
| 808 | 2025-09-29 | 08:00-10:00 | 336.1, 534.1, 543.5 | 34.69, 41.41, 41.89 | 35.98 | 0.28002 | Critical |
| 123 | 2025-10-09 | 14:00-16:00 | 616.5, 531.0, 352.4 | 41.36, 39.76, 34.95 | 36.52 | 0.27999 | Critical |
| 456 | 2025-11-18 | 14:00-16:00 | 594.4, 563.2, 350.6 | 40.02, 38.36, 35.03 | 37.28 | 0.28004 | Critical |
| 789 | 2025-12-24 | 14:00-16:00 | 608.7, 524.8, 364.4 | 40.19, 39.49, 36.29 | 36.53 | 0.27999 | Critical |
| 150 | 2025-01-01 | 09:00-11:00 | 310.8, 531.3, 632.2 | 33.60, 36.81, 38.04 | 11.53 | 0.02499 | Below Watch (expected miss) |
| 250 | 2025-02-04 | 14:00-16:00 | 478.1, 453.5, 353.0 | 37.82, 36.47, 34.21 | 12.57 | 0.03497 | Below Watch (expected miss) |
| 350 | 2025-03-04 | 15:00-16:00 | 693.6, 547.5 | 40.30, 37.98 | 22.06 | 0.14997 | Too short (expected miss) |

The hard windows show where the detector stops: a three-hour mean PR gap below 0.05 is not flagged, and a large gap lasting only two hours does not meet the three-consecutive-hour rule. The predicted gaps for inverters 150 and 250 are below Watch; inverter 350 exceeds the gap threshold but is intentionally shorter than the required duration.

## Limits

These faults are planted by a fixed rule in a modeled dataset. This test checks whether the unchanged detector can see the planted cases and where it stops; it says nothing about real inverters, real fault prevalence, or field diagnostic accuracy. The internal-temperature value is a modeled proxy, not measured inverter telemetry. The large delta_t values used in the Critical simulations produce modeled faulted internal temperatures above the datasheet's +60 C operating limit; these are simulation stress values, not realistic temperatures.
