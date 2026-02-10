# earthquake_insights

A utility that downloads recent earthquake event data from the USGS FDSN event API, loads it into a pandas DataFrame, and stores it in a MySQL database for analysis.

## Contents

- `earthquake_trend_analyzer.py` — Main script that:
  - Fetches earthquake events (magnitude ≥ 3) from the last 5 years
  - Creates a pandas DataFrame
  - **Automatically creates the MySQL database if missing**
  - Creates the `earthquakes` table
  - Inserts all records into MySQL
  - Verifies the import with statistics

- `earthquake_analysis_30_queries.sql` — Comprehensive SQL queries (30 total) for earthquake analysis across multiple categories

- `run_analysis_queries.py` — Python script to execute all 30 analysis queries and export results to CSV

- `test_mysql_connection.py` — Connection tester to verify MySQL setup before running the main script

- `MYSQL_SETUP.md` — Detailed MySQL installation and configuration guide

## Requirements

- Python 3.8+
- `requests` — for API calls
- `pandas` — for DataFrame operations
- `mysql-connector-python` — for MySQL connection

Install all packages:

```powershell
python -m pip install -r requirements.txt
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

### 3. Run the Script

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

### 4. Verify in MySQL Workbench

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

Run all analyses with:

```powershell
python run_analysis_queries.py
```

Or view the SQL file directly:

```powershell
cat earthquake_analysis_30_queries.sql
```

### Query Categories:

**1. Magnitude & Depth Analysis (Queries 1-5)**
- Top 10 strongest earthquakes
- Top 10 deepest earthquakes
- Shallow earthquakes (< 50km) with high magnitude (> 7.5)
- Average depth by region
- Average magnitude by magnitude type

**2. Time Analysis (Queries 6-10)**
- Year with most earthquakes
- Month with highest earthquake count
- Day of week distribution
- Hourly distribution
- Most active reporting network

**3. Event Quality (Queries 14-18)**
- Reviewed vs automatic earthquakes
- Earthquake type distribution
- Data quality metrics (RMS, gap)
- High station coverage events

**4. Tsunamis & Alerts (Queries 19-20)**
- Tsunamis triggered per year
- Distribution by alert level

**5. Seismic Patterns (Queries 21-24)**
- Top regions by average magnitude
- Mixed shallow/deep activity in same month
- Year-over-year growth trends
- Most seismically active regions

**6. Depth & Location Analysis (Queries 25-30)**
- Equatorial region analysis (±5° latitude)
- Shallow-to-deep earthquake ratios
- Tsunami magnitude comparison
- Data reliability assessment
- Consecutive earthquake pairs
- Deep-focus earthquakes (> 300km)

**Bonus:** Overall statistics, monthly trends, magnitude distribution

## Troubleshooting

### Connection Issues

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

**Error: Syntax or Unicode encoding**
- Already handled: the script uses ASCII-safe text for messages
- Run with: `python earthquake_trend_analyzer.py`

### Test Connection First

Before running the main script, test your setup:

```powershell
$env:MYSQL_USER = "root"
$env:MYSQL_PASSWORD = "your_password"
python test_mysql_connection.py
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

- **API Rate Limiting:** Queries are paginated by month to avoid hitting API limits
- **Performance:** First run may take 5-10 minutes to fetch 5 years of data
- **Storage:** Typically ~5,000-10,000 records per year for magnitude ≥ 3 events
- **Updates:** Run the script multiple times; duplicate IDs will update existing records

## Data Source

All earthquake data comes from the [USGS Earthquake Hazards Program](https://earthquake.usgs.gov/fdsnws/event/1/).

## Additional Resources

- See `MYSQL_SETUP.md` for detailed MySQL installation steps
- See `earthquake_analysis_30_queries.sql` for all SQL query details
- See `requirements.txt` for Python package versions