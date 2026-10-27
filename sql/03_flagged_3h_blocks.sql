/*
Question: Which inverters have three consecutive qualifying daytime hours?
Definition: At each timestamp, pr_gap is the median valid PR across all
    inverters with daytime rows minus that inverter's PR at that timestamp.
Logic: Join each inverter-hour to the next two exact hourly timestamps. Each
    hour must have irradiance above 200 W/m2 and a non-null PR. Require the
    three-hour mean pr_gap to be at least 0.05. Classify the mean as Watch
    [0.05, 0.10), Alert [0.10, 0.20], or Critical > 0.20.
Expected output: Compact one-row-per-inverter-and-severity summary with the
           count of qualifying rolling blocks and mean/maximum gap.
*/
WITH ranked_daytime_pr AS (
    SELECT
        DATE_TIME,
        PERFORMANCE_RATIO,
        ROW_NUMBER() OVER (
            PARTITION BY DATE_TIME ORDER BY PERFORMANCE_RATIO
        ) AS pr_rank,
        COUNT(*) OVER (PARTITION BY DATE_TIME) AS hour_count
    FROM processed_inv_metrics
    WHERE PERFORMANCE_RATIO IS NOT NULL
),
hourly_medians AS (
    SELECT DATE_TIME, AVG(PERFORMANCE_RATIO) AS median_pr
    FROM ranked_daytime_pr
    WHERE pr_rank IN ((hour_count + 1) / 2, (hour_count + 2) / 2)
    GROUP BY DATE_TIME
),
daytime_gaps AS (
    SELECT
        metrics.INVERTER_ID,
        metrics.DATE_TIME,
        metrics.IRRADIANCE,
        metrics.PERFORMANCE_RATIO,
        hourly_medians.median_pr - metrics.PERFORMANCE_RATIO AS pr_gap
    FROM processed_inv_metrics AS metrics
    JOIN hourly_medians USING (DATE_TIME)
    WHERE metrics.PERFORMANCE_RATIO IS NOT NULL
),
block_candidates AS (
    SELECT
        first_hour.INVERTER_ID,
        (
            first_hour.pr_gap + second_hour.pr_gap + third_hour.pr_gap
        ) / 3.0 AS mean_pr_gap
    FROM daytime_gaps AS first_hour
    JOIN daytime_gaps AS second_hour
        ON second_hour.INVERTER_ID = first_hour.INVERTER_ID
        AND second_hour.DATE_TIME = datetime(first_hour.DATE_TIME, '+1 hour')
    JOIN daytime_gaps AS third_hour
        ON third_hour.INVERTER_ID = first_hour.INVERTER_ID
        AND third_hour.DATE_TIME = datetime(first_hour.DATE_TIME, '+2 hours')
    WHERE first_hour.IRRADIANCE > 200
        AND second_hour.IRRADIANCE > 200
        AND third_hour.IRRADIANCE > 200
),
flagged_blocks AS (
    SELECT
        INVERTER_ID,
        mean_pr_gap,
        CASE
            WHEN mean_pr_gap < 0.10 THEN 'Watch'
            WHEN mean_pr_gap <= 0.20 THEN 'Alert'
            ELSE 'Critical'
        END AS severity_tier
    FROM block_candidates
    WHERE mean_pr_gap >= 0.05
)
SELECT
    INVERTER_ID,
    severity_tier,
    COUNT(*) AS qualifying_3h_blocks,
    AVG(mean_pr_gap) AS mean_pr_gap,
    MAX(mean_pr_gap) AS maximum_pr_gap
FROM flagged_blocks
GROUP BY INVERTER_ID, severity_tier
ORDER BY INVERTER_ID ASC, severity_tier ASC;