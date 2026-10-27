-- Question: Which inverters have the lowest average daytime performance ratio?
-- Logic: Exclude nighttime null PR rows and summarize by inverter.
-- Expected output: One row per inverter, ordered from lowest to highest mean PR.
SELECT
    INVERTER_ID,
    AVG(PERFORMANCE_RATIO) AS mean_daytime_performance_ratio,
    COUNT(PERFORMANCE_RATIO) AS daytime_hours
FROM processed_inv_metrics
WHERE PERFORMANCE_RATIO IS NOT NULL
GROUP BY INVERTER_ID
ORDER BY mean_daytime_performance_ratio ASC, INVERTER_ID ASC;
