import streamlit as st
import pandas as pd
import mysql.connector
import os

st.set_page_config(page_title="Earthquake Insights - 30 Queries", layout="wide")
st.title("[USGS] Earthquake Analysis - 30 SQL Queries")

# MySQL connection setup
@st.cache_resource
def get_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", "My$QL102511"),
            database=os.getenv("MYSQL_DATABASE", "earthquake_db")
        )
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def run_query(conn, query: str) -> pd.DataFrame:
    try:
        return pd.read_sql(query, conn)
    except Exception as e:
        st.error(f"Query error: {e}")
        return pd.DataFrame()

conn = get_connection()
if conn is None:
    st.error("Failed to connect to MySQL. Check environment variables.")
    st.stop()

st.sidebar.info("All 30 earthquake analysis queries from the database")

# Define all 30 queries
queries = {
    "Magnitude & Depth Analysis": {
        "1. Top 10 Strongest Earthquakes": """
SELECT id, place, magnitude, time, depth_km 
FROM earthquakes 
ORDER BY magnitude DESC 
LIMIT 10;
        """,
        "2. Top 10 Deepest Earthquakes": """
SELECT id, place, depth_km, magnitude, time 
FROM earthquakes 
ORDER BY depth_km DESC 
LIMIT 10;
        """,
        "3. Shallow < 50km & Magnitude > 7.5": """
SELECT id, place, magnitude, depth_km, time 
FROM earthquakes 
WHERE depth_km < 50 AND magnitude > 7.5
ORDER BY magnitude DESC;
        """,
        "4. Average Depth by Region": """
SELECT 
  SUBSTRING_INDEX(place, ',', -1) AS region,
  ROUND(AVG(depth_km), 2) AS avg_depth,
  COUNT(*) AS event_count
FROM earthquakes
GROUP BY region
ORDER BY avg_depth DESC
LIMIT 20;
        """,
        "5. Average Magnitude by Type": """
SELECT magType, ROUND(AVG(magnitude), 2) AS avg_mag, COUNT(*) AS count
FROM earthquakes
WHERE magType IS NOT NULL
GROUP BY magType
ORDER BY avg_mag DESC;
        """,
    },
    "Time Analysis": {
        "6. Year with Most Earthquakes": """
SELECT YEAR(time) AS year, COUNT(*) AS total
FROM earthquakes
GROUP BY year
ORDER BY total DESC
LIMIT 1;
        """,
        "7. Month with Highest Count": """
SELECT MONTH(time) AS month, COUNT(*) AS total
FROM earthquakes
GROUP BY month
ORDER BY total DESC
LIMIT 1;
        """,
        "8. Day of Week with Most Earthquakes": """
SELECT DAYNAME(time) AS day_of_week, COUNT(*) AS total
FROM earthquakes
GROUP BY day_of_week
ORDER BY total DESC;
        """,
        "9. Count by Hour of Day": """
SELECT HOUR(time) AS hour, COUNT(*) AS total
FROM earthquakes
GROUP BY hour
ORDER BY hour;
        """,
        "10. Most Active Reporting Network": """
SELECT net, COUNT(*) AS total
FROM earthquakes
WHERE net IS NOT NULL
GROUP BY net
ORDER BY total DESC
LIMIT 10;
        """,
    },
    "Event Quality & Status": {
        "14. Reviewed vs Automatic Earthquakes": """
SELECT status, COUNT(*) AS total
FROM earthquakes
WHERE status IS NOT NULL
GROUP BY status;
        """,
        "15. Count by Earthquake Type": """
SELECT type, COUNT(*) AS total
FROM earthquakes
WHERE type IS NOT NULL
GROUP BY type
ORDER BY total DESC;
        """,
        "16. Number of Earthquakes by Data Type": """
SELECT types, COUNT(*) AS total
FROM earthquakes
WHERE types IS NOT NULL
GROUP BY types
ORDER BY total DESC
LIMIT 15;
        """,
        "17. Average RMS and Gap by Region": """
SELECT 
  SUBSTRING_INDEX(place, ',', -1) AS region,
  ROUND(AVG(rms), 4) AS avg_rms,
  ROUND(AVG(gap), 2) AS avg_gap,
  COUNT(*) AS count
FROM earthquakes
GROUP BY region
HAVING count > 10
ORDER BY avg_rms DESC
LIMIT 15;
        """,
        "18. High Station Coverage Events (nst > 50)": """
SELECT id, place, nst, magnitude, time 
FROM earthquakes 
WHERE nst > 50
ORDER BY nst DESC
LIMIT 20;
        """,
    },
    "Tsunamis & Alerts": {
        "19. Tsunamis Triggered per Year": """
SELECT YEAR(time) AS year, COUNT(*) AS tsunami_count
FROM earthquakes
WHERE tsunami = 1
GROUP BY year
ORDER BY year DESC;
        """,
        "20. Count by Alert Level": """
SELECT alert, COUNT(*) AS total
FROM earthquakes
WHERE alert IS NOT NULL
GROUP BY alert
ORDER BY total DESC;
        """,
    },
    "Seismic Patterns & Trends": {
        "21. Top 5 Countries by Avg Magnitude (10 years)": """
SELECT 
  SUBSTRING_INDEX(place, ',', -1) AS country,
  ROUND(AVG(magnitude), 2) AS avg_mag,
  COUNT(*) AS count
FROM earthquakes
WHERE YEAR(time) >= YEAR(CURDATE()) - 10
GROUP BY country
ORDER BY avg_mag DESC
LIMIT 5;
        """,
        "22. Countries with Shallow & Deep in Same Month": """
SELECT 
  SUBSTRING_INDEX(place, ',', -1) AS country,
  YEAR(time) AS year,
  MONTH(time) AS month,
  COUNT(*) AS total_events
FROM earthquakes
GROUP BY country, year, month
HAVING MIN(depth_km) < 70 AND MAX(depth_km) > 300
LIMIT 20;
        """,
        "23. Year-over-Year Growth Rate": """
SELECT 
  year,
  total,
  ROUND(((total - LAG(total) OVER (ORDER BY year)) / LAG(total) OVER (ORDER BY year)) * 100, 2) AS growth_rate_pct
FROM (
  SELECT YEAR(time) AS year, COUNT(*) AS total
  FROM earthquakes
  GROUP BY year
) sub
ORDER BY year;
        """,
        "24. Top 3 Most Seismically Active Regions": """
SELECT 
  SUBSTRING_INDEX(place, ',', -1) AS region,
  COUNT(*) AS frequency,
  ROUND(AVG(magnitude), 2) AS avg_mag,
  ROUND(COUNT(*) * AVG(magnitude), 2) AS activity_score
FROM earthquakes
GROUP BY region
ORDER BY activity_score DESC
LIMIT 3;
        """,
    },
    "Depth & Location Analysis": {
        "25. Avg Depth Near Equator (±5°)": """
SELECT 
  SUBSTRING_INDEX(place, ',', -1) AS country,
  ROUND(AVG(depth_km), 2) AS avg_depth,
  COUNT(*) AS count
FROM earthquakes
WHERE latitude BETWEEN -5 AND 5
GROUP BY country
ORDER BY avg_depth DESC
LIMIT 15;
        """,
        "26. Shallow to Deep Earthquake Ratio": """
SELECT 
  SUBSTRING_INDEX(place, ',', -1) AS country,
  SUM(CASE WHEN depth_km < 70 THEN 1 ELSE 0 END) AS shallow_count,
  SUM(CASE WHEN depth_km >= 300 THEN 1 ELSE 0 END) AS deep_count,
  ROUND(SUM(CASE WHEN depth_km < 70 THEN 1 ELSE 0 END) / 
        NULLIF(SUM(CASE WHEN depth_km >= 300 THEN 1 ELSE 0 END), 0), 2) AS shallow_deep_ratio
FROM earthquakes
GROUP BY country
HAVING deep_count > 0
ORDER BY shallow_deep_ratio DESC
LIMIT 15;
        """,
        "27. Avg Magnitude: Tsunami vs Non-Tsunami": """
SELECT 
  CASE WHEN tsunami = 1 THEN 'With Tsunami' ELSE 'No Tsunami' END AS category,
  ROUND(AVG(magnitude), 2) AS avg_magnitude,
  COUNT(*) AS count
FROM earthquakes
GROUP BY tsunami;
        """,
        "28. Lowest Reliability Events (Highest Error)": """
SELECT 
  id,
  place,
  magnitude,
  ROUND(rms, 4) AS rms,
  ROUND(gap, 2) AS gap,
  ROUND(rms + gap, 2) AS error_score,
  time
FROM earthquakes
WHERE rms IS NOT NULL AND gap IS NOT NULL
ORDER BY error_score DESC
LIMIT 15;
        """,
        "29. Consecutive Earthquakes (50km & 1hr)": """
SELECT 
  e1.id AS eq1_id,
  e1.place AS eq1_place,
  e1.magnitude AS eq1_mag,
  e2.id AS eq2_id,
  e2.place AS eq2_place,
  e2.magnitude AS eq2_mag,
  TIMESTAMPDIFF(MINUTE, e1.time, e2.time) AS minutes_diff,
  ROUND(6371 * ACOS(
    COS(RADIANS(e1.latitude)) * COS(RADIANS(e2.latitude)) *
    COS(RADIANS(e2.longitude) - RADIANS(e1.longitude)) +
    SIN(RADIANS(e1.latitude)) * SIN(RADIANS(e2.latitude))
  ), 2) AS distance_km
FROM earthquakes e1
JOIN earthquakes e2 
  ON e2.time > e1.time
  AND TIMESTAMPDIFF(MINUTE, e1.time, e2.time) BETWEEN 1 AND 60
WHERE 6371 * ACOS(
  COS(RADIANS(e1.latitude)) * COS(RADIANS(e2.latitude)) *
  COS(RADIANS(e2.longitude) - RADIANS(e1.longitude)) +
  SIN(RADIANS(e1.latitude)) * SIN(RADIANS(e2.latitude))
) <= 50
ORDER BY e1.time DESC
LIMIT 20;
        """,
        "30. Deep-Focus Earthquakes (>300km)": """
SELECT 
  SUBSTRING_INDEX(place, ',', -1) AS region,
  COUNT(*) AS deep_quakes,
  ROUND(AVG(magnitude), 2) AS avg_magnitude,
  ROUND(AVG(depth_km), 2) AS avg_depth
FROM earthquakes
WHERE depth_km > 300
GROUP BY region
ORDER BY deep_quakes DESC
LIMIT 15;
        """,
    },
}

# Display queries by category
for category, queries_dict in queries.items():
    st.header(category)
    for query_name, query in queries_dict.items():
        with st.expander(query_name):
            df_result = run_query(conn, query)
            if not df_result.empty:
                st.dataframe(df_result, use_container_width=True)
                csv = df_result.to_csv(index=False)
                st.download_button(
                    f"Download {query_name.split('.')[0]}",
                    csv,
                    file_name=f"{query_name.split('.')[0].replace(' ', '_')}.csv"
                )
            else:
                st.warning("No results for this query")

st.divider()
st.success("Dashboard complete. All 30 queries executed from MySQL earthquake_db database.")
