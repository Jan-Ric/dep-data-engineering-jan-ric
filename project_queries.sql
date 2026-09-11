-- Phase 1 Goal: Identifying which inverter/s are underperforming from Historical Weather API and AC Yield (Anomaly Detection)               

/*
Question 1: Which of the following inverters has the most total underperforming hours?

NOTE: This query counts the total number of underperforming hours for each inverter based on the performance ratio and irradiance conditions.
*/

SELECT INVERTER_ID, 
    COUNT(PERFORMANCE_RATIO) AS total_underperform_hrs
FROM processed_inv_metrics
WHERE 1 - PERFORMANCE_RATIO >= 0.05 AND IRRADIANCE > 200
GROUP BY INVERTER_ID
ORDER BY total_underperform_hrs DESC;

/* 
Question 2: Which are the inverters that are underperforming with greater than 200 W/m² irradiance for 3-hour blocks?

NOTE: I used to average first the ac yield and irradiance then calculate performance ratio for each inverter in 3-hour blocks and 
        then filter the inverters that are underperforming with greater than 200 W/m² irradiance.
*/

SELECT 
    INVERTER_ID,
    AVG(PERFORMANCE_RATIO) AS performance_ratio,
    DATE(DATE_TIME) AS date_only,
    FLOOR(EXTRACT(HOUR FROM DATE_TIME) / 3) AS three_hour_block
FROM processed_inv_metrics
GROUP BY INVERTER_ID, DATE(DATE_TIME), FLOOR(EXTRACT(HOUR FROM DATE_TIME) / 3)
HAVING 1 - AVG(PERFORMANCE_RATIO) >= 0.05 AND AVG(IRRADIANCE) > 200 -- IRRADIANCE remains in W/m² for this threshold
ORDER by performance_ratio ASC;

/* 
Question 3: How are the underperforming inverters classified based on their severity?

NOTE: I used the aggregated 3-hour block data from the previous query to classify the underperforming inverters based on their severity.
*/
SELECT 
    INVERTER_ID,
    AVG(PERFORMANCE_RATIO) AS performance_ratio,
    1 - AVG(PERFORMANCE_RATIO) AS severity_gap,
    DATE(DATE_TIME) AS date_only,
    FLOOR(EXTRACT(HOUR FROM DATE_TIME) / 3) AS three_hour_block,
    CASE 
        WHEN 1 - AVG(PERFORMANCE_RATIO) >= 0.05 AND 1 - AVG(PERFORMANCE_RATIO) < 0.10 THEN 'Watch'
        WHEN 1 - AVG(PERFORMANCE_RATIO) >= 0.10 AND 1 - AVG(PERFORMANCE_RATIO) < 0.20 THEN 'Alert'
        WHEN 1 - AVG(PERFORMANCE_RATIO) >= 0.20 THEN 'Critical'
    ELSE 'Normal'
END AS severity_label
FROM processed_inv_metrics
GROUP BY INVERTER_ID, DATE(DATE_TIME), FLOOR(EXTRACT(HOUR FROM DATE_TIME) / 3)
HAVING 1 - AVG(PERFORMANCE_RATIO) >= 0.05 AND AVG(IRRADIANCE) > 200 -- IRRADIANCE remains in W/m² for this threshold
ORDER by severity_gap DESC;

