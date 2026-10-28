## Key Findings

The fleet-median PR-gap rule flagged **35 rolling three-hour blocks** across **13 of 830 inverters (1.57%)**. The severity mix was **16 Watch (45.71%)**, **15 Alert (42.86%)**, and **4 Critical (11.43%)**. These are overlapping eligible time windows, not confirmed failures.

The validation table contains **15 injected windows**. All **12 designed Watch, Alert, and Critical faults were detected with matching target tiers**: Watch 4/4, Alert 4/4, and Critical 4/4. The **three hard cases were missed as expected**: two had mean PR gaps below 0.05, and the Alert-sized case had only two hours of data, shorter than the three-hour rule. The 12/12 designed result is a controlled synthetic test, not evidence of real-world accuracy.

The false-alarm check found **zero flagged blocks on non-faulted inverters**. Zero is expected in this simulation because all non-faulted inverters share the same weather and simulated PR. This confirms the rule does not misfire on identical simulated peers and says nothing about noisy real data.

The pooled mean hourly PR was **0.92925**. It describes modeled valid daytime rows and is not the detector's same-hour peer gap or a diagnosis. Formula F uses synthetic temperature offsets, and some values exceed the README's earlier 2 to 15 C suggestion to reach the intended Critical gap in the model.

For O&M, treat Watch as remote review and monitoring, Alert as remote reset plus a planned site visit, and Critical as urgent review with telemetry confirmation. Validate on real plant data with confirmed fault labels, weather variation, and inverter variation before using these thresholds operationally.
