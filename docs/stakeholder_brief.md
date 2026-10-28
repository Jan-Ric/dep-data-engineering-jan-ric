# Stakeholder Brief: Which Inverters Need Attention?

**Bottom line:** The fixed peer-relative rule flagged 35 rolling three-hour blocks across 13 of 830 inverters (1.57%). It detected the 12 designed Watch, Alert, and Critical test windows with matching tiers, while missing all three hard cases as expected. The 12/12 result checks deterministic synthetic scenarios; it is not evidence of real-world accuracy.

For O&M engineers and the plant supervisor reviewing modeled 2025 results for Calatagan Solar Farm. This is a rule demonstration, not live monitoring or diagnosis; metrics come from generated tables.

## How the rule works

Performance ratio (PR) compares modeled AC output with irradiance and installed DC capacity. For each hour, the detector subtracts an inverter's PR from the same-hour fleet median. A block is flagged when three consecutive hourly timestamps each have irradiance above 200 W/m2 and valid PR, and their mean `pr_gap` is at least 0.05. Watch is 0.05 to below 0.10, Alert is 0.10 through 0.20, and Critical is above 0.20. Overlapping blocks count separately.

## What the outputs show

The saved severity distribution is 16 Watch blocks (45.71%), 15 Alert blocks (42.86%), and 4 Critical blocks (11.43%). The blocks occur on 13 inverters, or 1.57% of the 830-inverter fleet. These are rolling windows, not independent confirmed failures.

The validation contains 15 injected windows. All four Watch, four Alert, and four Critical designed cases were detected with matching tiers. The three hard cases were missed as expected: two mean gaps are below 0.05; the third has a 0.14997 gap but lasts two hours. The 12 designed faults were detected in a deterministic test, not a real-world accuracy study.

The false-alarm table reports zero flagged blocks on 815 inverters without an injected window. This is expected because they share the same weather and simulated PR. It confirms the rule does not misfire on identical inverters, but says nothing about noisy real data. Pooled mean PR is 0.92925; it is not a detector gap.

![Flagged blocks by severity and target cohort](../output/figures/flagged_blocks_by_severity_cohort.png)

## Suggested O&M follow-up

| Level | Gap | Suggested action |
| --- | --- | --- |
| Watch | 0.05 to below 0.10 | Check remotely, log the signal, and monitor for 24 hours. |
| Alert | 0.10 through 0.20 | Attempt a remote reset and schedule a site visit within 72 hours. |
| Critical | Above 0.20 | Prioritize immediate dispatch and verify against equipment telemetry. |

These are demonstration thresholds, not validated limits. Formula F uses synthetic temperature offsets; some delta_t values exceed the README's earlier 2 to 15 C suggestion to reach Critical in the model. Verify real flags against plant telemetry before acting.

## Next steps

Test on real telemetry with confirmed fault labels and weather/inverter variation before judging operational accuracy or considering maintenance thresholds, remaining life, or revenue impact.
