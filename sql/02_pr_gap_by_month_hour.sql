-- Question: In which months and hours do absolute PR gaps of at least 0.05 occur?
-- Logic: Treat 1 - PR as the gap from the ideal PR of 1.0; require irradiance > 200 W/m^2.
-- Expected output: Compact month/hour counts and mean PR gap, ordered chronologically.
SELECT
    SUBSTR(DATE_TIME, 1, 7) AS month,
    CAST(SUBSTR(DATE_TIME, 12, 2) AS INTEGER) AS hour_of_day,
    COUNT(*) AS flagged_inverter_hours,
    AVG(1.0 - PERFORMANCE_RATIO) AS mean_pr_gap
FROM processed_inv_metrics
WHERE PERFORMANCE_RATIO IS NOT NULL
  AND 1.0 - PERFORMANCE_RATIO >= 0.05
  AND IRRADIANCE > 200
GROUP BY month, hour_of_day
ORDER BY month, hour_of_day;
