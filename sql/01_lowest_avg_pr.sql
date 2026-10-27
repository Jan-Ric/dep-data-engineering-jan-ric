/*
Question: Which inverters have the lowest average daytime performance ratio?
Logic: Average PERFORMANCE_RATIO per inverter for rows with positive irradiance;
       null nighttime ratios are naturally excluded by AVG.
Expected output: One row per inverter with daytime hour count, average PR, and
                 corresponding average PR gap, ordered from lowest average PR.
*/
SELECT
    INVERTER_ID,
    COUNT(PERFORMANCE_RATIO) AS daytime_hours,
    AVG(PERFORMANCE_RATIO) AS avg_performance_ratio,
    1.0 - AVG(PERFORMANCE_RATIO) AS avg_pr_gap
FROM processed_inv_metrics
WHERE IRRADIANCE > 0
GROUP BY INVERTER_ID
ORDER BY avg_performance_ratio ASC, INVERTER_ID ASC;