USE earthquake_db;

SELECT id, place, magnitude, time
FROM earthquakes
ORDER BY magnitude DESC
LIMIT 10;
-- 2. Top 10 deepest earthquakes
SELECT id, place, depth_km, time
FROM earthquakes
ORDER BY depth_km DESC
LIMIT 10;

-- 3. Shallow earthquakes < 50 km and mag > 7.5
SELECT id, place, magnitude, depth_km, time
FROM earthquakes
WHERE depth_km < 50 AND magnitude > 7.5;

-- 4. Average depth per continent (requires mapping place → continent)
-- Example: using LIKE for rough grouping
SELECT 
  CASE
    WHEN place LIKE '%Asia%' THEN 'Asia'
    WHEN place LIKE '%Africa%' THEN 'Africa'
    WHEN place LIKE '%Europe%' THEN 'Europe'
    WHEN place LIKE '%America%' THEN 'America'
    WHEN place LIKE '%Pacific%' THEN 'Oceania'
    ELSE 'Other'
  END AS continent,
  AVG(depth_km) AS avg_depth
FROM earthquakes
GROUP BY continent;

-- 5. Average magnitude per magnitude type
SELECT magType, ROUND(AVG(magnitude),2) AS avg_mag
FROM earthquakes
GROUP BY magType;

-- 6. Year with most earthquakes
SELECT YEAR(time) AS year, COUNT(*) AS total
FROM earthquakes
GROUP BY year
ORDER BY total DESC
LIMIT 1;

-- 7. Month with highest number of earthquakes
SELECT MONTH(time) AS month, COUNT(*) AS total
FROM earthquakes
GROUP BY month
ORDER BY total DESC
LIMIT 1;

-- 8. Day of week with most earthquakes
SELECT DAYNAME(time) AS day_of_week, COUNT(*) AS total
FROM earthquakes
GROUP BY day_of_week
ORDER BY total DESC;

-- 9. Count of earthquakes per hour of day
SELECT HOUR(time) AS hour, COUNT(*) AS total
FROM earthquakes
GROUP BY hour
ORDER BY hour;

-- 10. Most active reporting network
SELECT net, COUNT(*) AS total
FROM earthquakes
GROUP BY net
ORDER BY total DESC
LIMIT 1;

-- 14. Count of reviewed vs automatic earthquakes
SELECT status, COUNT(*) AS total
FROM earthquakes
GROUP BY status;

-- 15. Count by earthquake type
SELECT type, COUNT(*) AS total
FROM earthquakes
GROUP BY type;

-- 16. Number of earthquakes by data type (types)
SELECT types, COUNT(*) AS total
FROM earthquakes
GROUP BY types;

-- 17. Average RMS and gap per continent
SELECT place, AVG(rms) AS avg_rms, AVG(gap) AS avg_gap
FROM earthquakes
GROUP BY place;

-- 18. Events with high station coverage (nst > 50)
SELECT id, place, nst, time
FROM earthquakes
WHERE nst > 50;

-- 19. Number of tsunamis triggered per year
SELECT YEAR(time) AS year, COUNT(*) AS tsunami_count
FROM earthquakes
WHERE tsunami = 1
GROUP BY year;

-- 20. Count earthquakes by alert levels
SELECT alert, COUNT(*) AS total
FROM earthquakes
GROUP BY alert;

-- 21. Top 5 countries with highest average magnitude (last 10 years)
SELECT SUBSTRING_INDEX(place, ',', -1) AS country,
       ROUND(AVG(magnitude),2) AS avg_mag
FROM earthquakes
WHERE YEAR(time) >= YEAR(CURDATE()) - 10
GROUP BY country
ORDER BY avg_mag DESC
LIMIT 5;

-- 22. Countries with both shallow and deep earthquakes in same month
SELECT country, YEAR(time) AS year, MONTH(time) AS month
FROM (
  SELECT SUBSTRING_INDEX(place, ',', -1) AS country, time, depth_km
  FROM earthquakes
) t
GROUP BY country, year, month
HAVING MIN(depth_km) < 70 AND MAX(depth_km) > 300;

-- 23. Year-over-year growth rate in total earthquakes
SELECT year, total,
       ROUND(((total - LAG(total) OVER (ORDER BY year)) / LAG(total) OVER (ORDER BY year)) * 100,2) AS growth_rate
FROM (
  SELECT YEAR(time) AS year, COUNT(*) AS total
  FROM earthquakes
  GROUP BY year
) sub;

-- 24. Top 3 most seismically active regions (frequency + avg magnitude)
SELECT SUBSTRING_INDEX(place, ',', -1) AS region,
       COUNT(*) AS freq,
       ROUND(AVG(magnitude),2) AS avg_mag,
       (COUNT(*) * AVG(magnitude)) AS score
FROM earthquakes
GROUP BY region
ORDER BY score DESC
LIMIT 3;

-- 25. Average depth of earthquakes within ±5° latitude of equator per country
SELECT SUBSTRING_INDEX(place, ',', -1) AS country,
       AVG(depth_km) AS avg_depth
FROM earthquakes
WHERE latitude BETWEEN -5 AND 5
GROUP BY country;

-- 26. Countries with highest ratio of shallow to deep earthquakes
SELECT country,
       SUM(CASE WHEN depth_km < 70 THEN 1 ELSE 0 END) /
       SUM(CASE WHEN depth_km >= 300 THEN 1 ELSE 0 END) AS shallow_deep_ratio
FROM (
  SELECT SUBSTRING_INDEX(place, ',', -1) AS country, depth_km
  FROM earthquakes
) t
GROUP BY country
ORDER BY shallow_deep_ratio DESC;

-- 27. Avg magnitude difference between tsunami vs non-tsunami
SELECT 
  ROUND(AVG(CASE WHEN tsunami=1 THEN magnitude END),2) -
  ROUND(AVG(CASE WHEN tsunami=0 THEN magnitude END),2) AS mag_diff
FROM earthquakes;

-- 28. Events with lowest reliability (highest rms + gap)
SELECT id, place, rms, gap, (rms + gap) AS error_score
FROM earthquakes
ORDER BY error_score DESC
LIMIT 10;

-- 29. Pairs of consecutive earthquakes within 50 km & 1 hour
USE earthquake_db;

-- 29. Pairs of consecutive earthquakes within 50 km & 1 hour
SELECT 
    e1.id AS eq1_id,
    e1.place AS eq1_place,
    e1.time AS eq1_time,
    e2.id AS eq2_id,
    e2.place AS eq2_place,
    e2.time AS eq2_time,
    TIMESTAMPDIFF(MINUTE, e1.time, e2.time) AS minutes_diff,
    (6371 * ACOS(
        COS(RADIANS(e1.latitude)) * COS(RADIANS(e2.latitude)) *
        COS(RADIANS(e2.longitude) - RADIANS(e1.longitude)) +
        SIN(RADIANS(e1.latitude)) * SIN(RADIANS(e2.latitude))
    )) AS distance_km
FROM earthquakes e1
JOIN earthquakes e2 
    ON e2.time > e1.time
   AND TIMESTAMPDIFF(MINUTE, e1.time, e2.time) <= 60
WHERE (6371 * ACOS(
        COS(RADIANS(e1.latitude)) * COS(RADIANS(e2.latitude)) *
        COS(RADIANS(e2.longitude) - RADIANS(e1.longitude)) +
        SIN(RADIANS(e1.latitude)) * SIN(RADIANS(e2.latitude))
    )) <= 50
ORDER BY e1.time, e2.time;

-- 30. Regions with highest frequency of deep-focus earthquakes (>300 km)
SELECT SUBSTRING_INDEX(place, ',', -1) AS region,
       COUNT(*) AS deep_quakes
FROM earthquakes
WHERE depth_km > 300
GROUP BY region
ORDER BY deep_quakes DESC
LIMIT 5;