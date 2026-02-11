# Earthquake_insights

A utility that downloads recent earthquake event data from the USGS FDSN event API, loads it into a pandas DataFrame, and stores it in a MySQL database for analysis.

## Contents

- `streamlit_dashboard.py` — **Interactive Streamlit dashboard** that executes all 30 SQL queries directly from the MySQL database and displays results with export options

- `earthquake_trend_analyzer.py` — Main script that:
  - Fetches earthquake events (magnitude ≥ 3) from the last 5 years
  - Creates a pandas DataFrame
  - **Automatically creates the MySQL database if missing**
  - Creates the `earthquakes` table
  - Inserts all records into MySQL
  - Verifies the import with statistics

- `earthquake_analysis.sql` — Comprehensive SQL queries (30 total) for earthquake analysis across multiple categories

- `MYSQL_SETUP.md` — Detailed MySQL installation and configuration guide

## Requirements

- Python 3.8+
- `requests` — for API calls
- `pandas` — for DataFrame operations
- `mysql-connector-python` — for MySQL connection
- `streamlit` — for interactive dashboard
- `plotly` — for visualizations

Install all packages:

```powershell
python -m pip install -r requirements.txt
```

Or install individually:

```powershell
pip install streamlit pandas mysql-connector-python requests plotly
```

## Quick Start

### 1. Install MySQL

**Option A: Windows with Chocolatey**
```powershell
choco install mysql
```

**Option B: Docker (Recommended)**
```powershell
docker run --name earthquake-mysql -e MYSQL_ROOT_PASSWORD=root -p 3306:3306 -d mysql:8.0
```

### 2. Set MySQL Credentials (PowerShell)

```powershell
$env:MYSQL_USER = "root"
$env:MYSQL_PASSWORD = "your_password"
$env:MYSQL_HOST = "localhost"
$env:MYSQL_PORT = "3306"
$env:MYSQL_DATABASE = "earthquake_db"
```

### 3. Load Data into MySQL

```powershell
python earthquake_trend_analyzer.py
```

**The script will:**
- ✓ Connect to MySQL
- ✓ Auto-create the database (if missing)
- ✓ Create the `earthquakes` table
- ✓ Fetch 5 years of earthquake data from USGS API
- ✓ Insert all records into MySQL
- ✓ Display verification statistics

### 4. Run the Streamlit Dashboard

#### Quick Start Command (Windows PowerShell)

```powershell
cd "D:\earthquick'\earthquake_insights"
.\env\Scripts\python.exe -m streamlit run streamlit_dashboard.py
```

#### What to Expect

After running the command, you should see:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://<your-ip>:8501
```

The dashboard will automatically open in your default browser. If not, manually navigate to:
- **Local Access:** `http://localhost:8501`
- **Network Access:** `http://<your-machine-ip>:8501` (for access from other devices)

#### Streamlit Dashboard Features

**Dashboard Interface:**
- **Left Sidebar:** Interactive dropdown menu with all 30 earthquake analysis queries
- **Query Selection:** Select any query from the dropdown
- **Execute Button:** Click "Execute Query" to run the selected query
- **Results Display:** Query results shown in a formatted table
- **CSV Export:** Download results as CSV file directly from the dashboard

**30 Available Queries:**
1. Top 10 Strongest Earthquakes
2. Top 10 Deepest Earthquakes
3. Most Recent Earthquakes (Last 30 Days)
4. Earthquakes by Magnitude Range (5.0-6.0)
5. Earthquakes by Depth Category (Shallow, Intermediate, Deep)
6. Average Magnitude by Region
7. Earthquake Count by Year
8. Magnitude vs Depth Correlation
9. Earthquakes in Specific Latitude Range
10. Earthquakes in Specific Longitude Range
... and 20 more analytical queries covering magnitude trends, regional analysis, temporal patterns, and seismic activity statistics.

#### Troubleshooting

**Issue: Browser doesn't open automatically**
- Manually navigate to `http://localhost:8501`

**Issue: "Address already in use" error**
```powershell
# Kill the process using port 8501
netstat -ano | findstr :8501
taskkill /PID <PID> /F
```

**Issue: "Query error: MySQL Connection not available"**
1. Verify MySQL is running: `mysql -u root -p`
2. Check credentials match your environment variables
3. Verify database was created: `SHOW DATABASES;`
4. The dashboard auto-reconnects on the next query attempt

**Issue: Environment variables not set**
```powershell
# Set them in PowerShell before running Streamlit:
$env:MYSQL_USER = "root"
$env:MYSQL_PASSWORD = "your_password"
$env:MYSQL_HOST = "localhost"
$env:MYSQL_DATABASE = "earthquake_db"

# Then run:
.\env\Scripts\python.exe -m streamlit run streamlit_dashboard.py
```

**Issue: Slow dashboard response**
- First query execution loads data from MySQL database
- Subsequent queries may be faster
- Large datasets may take 5-10 seconds to execute
- No caching is used to ensure fresh data on each query

### 5. Verify in MySQL Workbench

```sql
USE earthquake_db;
SELECT COUNT(*) FROM earthquakes;
SELECT * FROM earthquakes LIMIT 5;
```

## Data Structure

The `earthquakes` table contains these fields:

| Field | Type | Description |
|-------|------|-------------|
| `id` | VARCHAR(50) | Unique event identifier (Primary Key) |
| `time` | DATETIME | Event occurrence time |
| `updated` | DATETIME | Last update timestamp |
| `latitude` | DOUBLE | Event latitude |
| `longitude` | DOUBLE | Event longitude |
| `depth_km` | DOUBLE | Event depth in kilometers |
| `magnitude` | DOUBLE | Event magnitude |
| `magType` | VARCHAR(10) | Magnitude type (e.g., mb, ml, mw) |
| `place` | TEXT | Event location description |
| `status` | VARCHAR(20) | Event status (reviewed/automatic) |
| `tsunami` | INT | 1 if tsunami triggered, 0 otherwise |
| `alert` | VARCHAR(10) | Alert level (green/yellow/orange/red) |
| `type` | VARCHAR(20) | Event type |
| `types` | VARCHAR(100) | List of associated types |
| `rms` | DOUBLE | RMS (Root Mean Square) error |
| `gap` | DOUBLE | Azimuthal gap in degrees |
| `nst` | INT | Number of seismic stations used |
| `net` | VARCHAR(10) | Reporting network code |

## 30 Earthquake Analysis Queries

All 30 queries are available in the **interactive Streamlit dashboard** (`streamlit_dashboard.py`). Each query result is displayed in an expandable section with a download button to export data as CSV.

### Running the Dashboard

```powershell
python -m streamlit run streamlit_dashboard.py
```

The dashboard connects directly to your MySQL `earthquake_db` database and executes queries on demand.

### Query Categories:

**Magnitude & Depth Analysis (Queries 1-5)**
- 1. Top 10 strongest earthquakes
- 2. Top 10 deepest earthquakes
- 3. Shallow earthquakes (< 50km) with high magnitude (> 7.5)
- 4. Average depth by region
- 5. Average magnitude by magnitude type

**Time Analysis (Queries 6-10)**
- 6. Year with most earthquakes
- 7. Month with highest earthquake count
- 8. Day of week with most earthquakes
- 9. Count of earthquakes per hour of day
- 10. Most active reporting network

**Event Quality & Status (Queries 14-18)**
- 14. Reviewed vs automatic earthquakes
- 15. Count by earthquake type
- 16. Number of earthquakes by data type
- 17. Average RMS and gap by region
- 18. Events with high station coverage (nst > 50)

**Tsunamis & Alerts (Queries 19-20)**
- 19. Tsunamis triggered per year
- 20. Count earthquakes by alert level

**Seismic Patterns & Trends (Queries 21-24)**
- 21. Top 5 countries by average magnitude (last 10 years)
- 22. Countries with both shallow and deep earthquakes in same month
- 23. Year-over-year growth rate in total earthquakes
- 24. Top 3 most seismically active regions (frequency + magnitude)

**Depth & Location Analysis (Queries 25-30)**
- 25. Average depth near equator (±5° latitude)
- 26. Shallow-to-deep earthquake ratios by country
- 27. Average magnitude: tsunami vs non-tsunami
- 28. Lowest reliability events (highest error margins)
- 29. Consecutive earthquakes within 50km and 1 hour
- 30. Regions with highest frequency of deep-focus earthquakes (> 300km)

### Accessing Individual Queries

To run a specific query directly in MySQL:

```sql
-- Example: Top 10 strongest earthquakes
SELECT id, place, magnitude, time, depth_km 
FROM earthquakes 
ORDER BY magnitude DESC 
LIMIT 10;
```

See `earthquake_analysis.sql` for all 30 SQL queries.

## Troubleshooting

### Streamlit Dashboard Issues

**Error: ModuleNotFoundError: No module named 'streamlit'**
```powershell
# Make sure to use the project's virtual environment
.\env\Scripts\python.exe -m pip install streamlit plotly mysql-connector-python
```

**Dashboard won't open in browser**
- The Streamlit server is running, but the browser didn't open automatically
- Copy the Local URL printed in the terminal (e.g., http://localhost:8501) and paste it into your browser manually
- Alternatively, run with explicit host/port:
  ```powershell
  .\env\Scripts\python.exe -m streamlit run streamlit_dashboard.py --server.port 8502
  ```

**Database connection fails in dashboard**
- Ensure MySQL is running and your environment variables are set:
  ```powershell
  $env:MYSQL_HOST = "localhost"
  $env:MYSQL_USER = "root"
  $env:MYSQL_PASSWORD = "your_password"
  $env:MYSQL_DATABASE = "earthquake_db"
  ```
- Or edit the dashboard code to hardcode credentials (not recommended for production)

### MySQL Connection Issues

**Error: Access denied (wrong username/password)**
```powershell
# Verify MySQL is running
mysql -u root -p

# Set correct credentials
$env:MYSQL_USER = "root"
$env:MYSQL_PASSWORD = "correct_password"
```

**Error: Cannot connect to MySQL server**
```powershell
# Check if MySQL service is running
Get-Service | grep MySQL

# Or start it manually
net start MySQL80
```

### Data Loading Issues

**Error: Syntax or Unicode encoding**
- Already handled: the script uses ASCII-safe text for messages
- Run with: `python earthquake_trend_analyzer.py`

**Test your MySQL setup before loading data:**

```powershell
$env:MYSQL_USER = "root"
$env:MYSQL_PASSWORD = "your_password"
python -c "import mysql.connector; conn = mysql.connector.connect(host='localhost', user=os.getenv('MYSQL_USER'), password=os.getenv('MYSQL_PASSWORD')); print('OK')"
```

## Configuration

### Modify Query Parameters

Edit `earthquake_trend_analyzer.py`:

```python
params = {
    "format": "geojson",
    "starttime": start_date,
    "endtime": end_date,
    "minmagnitude": 3  # Change minimum magnitude here
}
```

### Change Time Range

Modify the year range:

```python
start_year = datetime.now().year - 10  # Last 10 years instead of 5
end_year = datetime.now().year
```

## Export Data to CSV

After loading data into MySQL, export with:

```sql
SELECT * FROM earthquakes 
INTO OUTFILE '/tmp/earthquakes.csv'
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n';
```

Or use Python:

```python
import pandas as pd
df = pd.read_sql("SELECT * FROM earthquakes", conn)
df.to_csv('earthquakes_export.csv', index=False)
```

## Notes

- **Streamlit Dashboard:** Interactive interface for exploring all 30 analysis queries with live results and CSV export
- **API Rate Limiting:** `earthquake_trend_analyzer.py` paginates queries by month to avoid hitting USGS API limits
- **Performance:** First data load may take 5-10 minutes to fetch 5 years of data from USGS
- **Data Volume:** Typically ~5,000-10,000 records per year for magnitude ≥ 3 events
- **Updates:** Run `earthquake_trend_analyzer.py` multiple times; duplicate IDs will update existing records with latest data
- **Query Performance:** Streamlit dashboard caches MySQL connections for optimal performance

## Data Source

All earthquake data comes from the [USGS Earthquake Hazards Program](https://earthquake.usgs.gov/fdsnws/event/1/).

## Workflow Summary

1. **Data Ingestion:** `earthquake_trend_analyzer.py` fetches data from USGS API → MySQL
2. **Interactive Analysis:** `streamlit_dashboard.py` displays all 30 SQL queries with results
3. **SQL Queries:** `earthquake_analysis.sql` contains all analysis queries
4. **Export:** Download results as CSV directly from the dashboard

## Additional Resources

- `streamlit_dashboard.py` — Run the interactive dashboard
- `earthquake_analysis.sql` — View all 30 SQL queries
- `earthquake_trend_analyzer.py` — Load latest earthquake data from USGS
- `README.md` — This file with setup instructions