/*
Question: Which inverter has a flagged block of three consecutive daytime hours?
Logic: Join each inverter-hour to the next two exact hourly timestamps. Require
       irradiance above 200 W/m2 and non-null PR at all three hours. Classify
    the three-hour mean PR gap: Watch [0.05, 0.10), Alert [0.10, 0.20],
    Critical > 0.20.
Expected output: One row per qualifying rolling three-hour block, including
Expected output: Compact one-row-per-inverter-and-severity summary with the
                 number of qualifying rolling blocks and mean/maximum PR gap.
*/
WITH flagged_blocks AS (
    SELECT
    first_hour.INVERTER_ID,
    1.0 - (
        first_hour.PERFORMANCE_RATIO
        + second_hour.PERFORMANCE_RATIO
        + third_hour.PERFORMANCE_RATIO
    ) / 3.0 AS pr_gap,
    CASE
        WHEN 1.0 - (
            first_hour.PERFORMANCE_RATIO
            + second_hour.PERFORMANCE_RATIO
            + third_hour.PERFORMANCE_RATIO
        ) / 3.0 < 0.10 THEN 'Watch'
        WHEN 1.0 - (
            first_hour.PERFORMANCE_RATIO
            + second_hour.PERFORMANCE_RATIO
            + third_hour.PERFORMANCE_RATIO
        ) / 3.0 <= 0.20 THEN 'Alert'
        ELSE 'Critical'
    END AS severity_tier
FROM processed_inv_metrics AS first_hour
JOIN processed_inv_metrics AS second_hour
    ON second_hour.INVERTER_ID = first_hour.INVERTER_ID
    AND second_hour.DATE_TIME = datetime(first_hour.DATE_TIME, '+1 hour')
JOIN processed_inv_metrics AS third_hour
    ON third_hour.INVERTER_ID = first_hour.INVERTER_ID
    AND third_hour.DATE_TIME = datetime(first_hour.DATE_TIME, '+2 hours')
WHERE first_hour.IRRADIANCE > 200
    AND second_hour.IRRADIANCE > 200
    AND third_hour.IRRADIANCE > 200
    AND first_hour.PERFORMANCE_RATIO IS NOT NULL
    AND second_hour.PERFORMANCE_RATIO IS NOT NULL
    AND third_hour.PERFORMANCE_RATIO IS NOT NULL
    AND 1.0 - (
        first_hour.PERFORMANCE_RATIO
        + second_hour.PERFORMANCE_RATIO
        + third_hour.PERFORMANCE_RATIO
    ) / 3.0 >= 0.05
)
SELECT
    INVERTER_ID,
    severity_tier,
    COUNT(*) AS qualifying_3h_blocks,
    AVG(pr_gap) AS mean_pr_gap,
    MAX(pr_gap) AS maximum_pr_gap
FROM flagged_blocks
GROUP BY INVERTER_ID, severity_tier
ORDER BY INVERTER_ID ASC, severity_tier ASC;