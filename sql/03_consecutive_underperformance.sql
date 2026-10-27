-- Question: Which inverters have three consecutive daytime hours with PR gaps >= 0.05, and at what severity?
-- Logic: Require three actual consecutive timestamps, each with irradiance > 200 W/m^2 and 1 - PR >= 0.05.
-- Severity uses the three-hour mean gap: Watch [0.05, 0.10), Alert [0.10, 0.20), Critical [0.20, infinity).
-- Expected output: Compact counts per inverter and severity; this avoids publishing a huge block-level result.
WITH eligible_hours AS (
    SELECT
        INVERTER_ID,
        DATE_TIME,
        PERFORMANCE_RATIO,
        IRRADIANCE,
        1.0 - PERFORMANCE_RATIO AS pr_gap,
        LAG(DATE_TIME, 1) OVER (
            PARTITION BY INVERTER_ID ORDER BY DATE_TIME
        ) AS previous_time,
        LAG(DATE_TIME, 2) OVER (
            PARTITION BY INVERTER_ID ORDER BY DATE_TIME
        ) AS two_hours_previous_time,
        LAG(1.0 - PERFORMANCE_RATIO, 1) OVER (
            PARTITION BY INVERTER_ID ORDER BY DATE_TIME
        ) AS previous_gap,
        LAG(1.0 - PERFORMANCE_RATIO, 2) OVER (
            PARTITION BY INVERTER_ID ORDER BY DATE_TIME
        ) AS two_hours_previous_gap,
        LAG(IRRADIANCE, 1) OVER (
            PARTITION BY INVERTER_ID ORDER BY DATE_TIME
        ) AS previous_irradiance,
        LAG(IRRADIANCE, 2) OVER (
            PARTITION BY INVERTER_ID ORDER BY DATE_TIME
        ) AS two_hours_previous_irradiance
    FROM processed_inv_metrics
    WHERE PERFORMANCE_RATIO IS NOT NULL
), three_hour_blocks AS (
    SELECT
        INVERTER_ID,
        DATE_TIME AS block_end,
        (pr_gap + previous_gap + two_hours_previous_gap) / 3.0 AS mean_pr_gap
    FROM eligible_hours
    WHERE pr_gap >= 0.05
      AND previous_gap >= 0.05
      AND two_hours_previous_gap >= 0.05
      AND IRRADIANCE > 200
      AND previous_irradiance > 200
      AND two_hours_previous_irradiance > 200
      AND datetime(previous_time) = datetime(DATE_TIME, '-1 hour')
      AND datetime(two_hours_previous_time) = datetime(DATE_TIME, '-2 hours')
), classified_blocks AS (
    SELECT
        INVERTER_ID,
        block_end,
        mean_pr_gap,
        CASE
            WHEN mean_pr_gap < 0.10 THEN 'Watch'
            WHEN mean_pr_gap < 0.20 THEN 'Alert'
            ELSE 'Critical'
        END AS severity
    FROM three_hour_blocks
)
SELECT
    INVERTER_ID,
    severity,
    COUNT(*) AS qualifying_three_hour_blocks,
    MIN(mean_pr_gap) AS minimum_mean_pr_gap,
    MAX(mean_pr_gap) AS maximum_mean_pr_gap
FROM classified_blocks
GROUP BY INVERTER_ID, severity
ORDER BY INVERTER_ID, severity;
