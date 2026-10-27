# Stakeholder Brief: Inverter PR Review

## Question

When do inverter records show sustained shortfalls, and how should O&M respond?

## What we did

We summarized modeled hourly inverter data using performance ratio (PR), which compares AC output with expected output from sunlight and installed capacity. We applied a fixed rule to rolling three-hour periods and checked it against three simulated fault windows.

## What we found

- Mean valid PR was **0.9293**, or about **0.0707 (7.07 percentage points)** below the normalized reference of 1.0; this is not a comparison with a known healthy fleet.
- The saved results contain **2,017,730 flagged three-hour blocks**: **1,337,958 Watch (66.31%)**, **629,972 Alert (31.22%)**, and **49,800 Critical (2.47%)**. A rolling block advances by one hour, so overlapping blocks can describe the same extended period rather than separate incidents.
- An estimated **2.1640%** of sampled inverter-hour rows reached the modeled 60 kW AC output cap. This clipping is expected in the model and is not, on its own, evidence of a fault.
- The fixed rule detected **0 of 3** simulated fault windows. This small test does not measure real-world detection performance, but it shows that this rule did not catch the examples it was designed to check.

![Flagged blocks by severity and fault cohort](../output/figures/flagged_blocks_by_severity_cohort.png)

## What to do

Treat Watch, Alert, and Critical as review priorities, not confirmed diagnoses. A flag means the average PR gap (distance below 1.0) met a demonstration threshold over three consecutive hours with irradiance above 200 W/m². For Watch, remotely check, log, and monitor for 24 hours. For Alert, attempt a remote reset and schedule a site visit within 72 hours. For Critical, the README suggests likely hardware fault and immediate dispatch. Verify flags against equipment readings before acting.

## Limits

Faults were injected for testing, and weather and inverter output are model-based. The project has no real inverter telemetry, so these results cannot confirm equipment condition or establish validated maintenance limits. Flagged blocks overlap, and the available severity summary cannot identify the share of inverters with at least one flag.

## Next steps

Phase 2 is future work: explore remaining-life and PR estimates using historical data, weather forecasts, temperature change, and inverter age. Phase 3 is also future work: research how verified energy shortfalls could relate to gross revenue. Neither phase is delivered or validated by these descriptive results.

PDF export in VS Code: Install the “Markdown PDF” extension, open this file, and run “Markdown PDF: Export (pdf)” from the Command Palette.
Alternative: Open Markdown Preview with `Ctrl+Shift+V`, then print the preview to PDF using your system print dialog.