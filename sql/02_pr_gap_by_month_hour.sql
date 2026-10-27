/*
Question: How does the average performance ratio gap vary by month and hour?
Definition: At each timestamp, pr_gap is the median valid PR across all
       inverters with daytime rows minus that inverter's PR at that timestamp.
Logic: Compute the timestamp median, then summarize per-inverter gaps by
       calendar month and clock hour. Null nighttime PR is excluded.
Expected output: One row per month and hour with contributing inverter-hour
                 count, average PR, and average fleet-median PR gap, ordered.
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
        metrics.DATE_TIME,
        metrics.PERFORMANCE_RATIO,
        hourly_medians.median_pr - metrics.PERFORMANCE_RATIO AS pr_gap
    FROM processed_inv_metrics AS metrics
    JOIN hourly_medians USING (DATE_TIME)
    WHERE metrics.PERFORMANCE_RATIO IS NOT NULL
)
SELECT
    strftime('%Y-%m', DATE_TIME) AS month,
    strftime('%H', DATE_TIME) AS hour,
    COUNT(PERFORMANCE_RATIO) AS daytime_inverter_hours,
    AVG(PERFORMANCE_RATIO) AS avg_performance_ratio,
    AVG(pr_gap) AS avg_pr_gap
FROM daytime_gaps
GROUP BY month, hour
ORDER BY month ASC, hour ASC;
