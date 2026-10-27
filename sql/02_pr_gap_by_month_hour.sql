/*
Question: How does the average performance ratio gap vary by month and hour?
Logic: Group positive-irradiance rows by calendar month and clock hour, then
       report the average PR and its gap from 1. Null nighttime PR is excluded.
Expected output: One row per month and hour with contributing inverter-hour
                 count, average PR, and average PR gap, chronologically ordered.
*/
SELECT
    strftime('%Y-%m', DATE_TIME) AS month,
    strftime('%H', DATE_TIME) AS hour,
    COUNT(PERFORMANCE_RATIO) AS daytime_inverter_hours,
    AVG(PERFORMANCE_RATIO) AS avg_performance_ratio,
    1.0 - AVG(PERFORMANCE_RATIO) AS avg_pr_gap
FROM processed_inv_metrics
WHERE IRRADIANCE > 0
GROUP BY month, hour
ORDER BY month ASC, hour ASC;
