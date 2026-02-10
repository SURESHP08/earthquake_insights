import requests
import pandas as pd
from datetime import datetime
import mysql.connector
from mysql.connector import Error
import os

url = "https://earthquake.usgs.gov/fdsnws/event/1/query"

all_records = []
start_year = datetime.now().year - 5   # last 5 years
end_year = datetime.now().year

for year in range(start_year, end_year + 1):
    for month in range(1, 13):
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year+1}-01-01"
        else:
            end_date = f"{year}-{month+1:02d}-01"

        params = {
            "format": "geojson",
            "starttime": start_date,
            "endtime": end_date,
            "minmagnitude": 3
        }

        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"⚠️ Failed for {start_date}: {response.text[:200]}")
            continue

        try:
            data = response.json()
        except Exception as e:
            print(f"⚠️ JSON error for {start_date}: {e}")
            continue

        for f in data["features"]:
            p = f["properties"]
            g = f["geometry"]["coordinates"]
            all_records.append({
                "id": f.get("id"),
                "time": pd.to_datetime(p.get("time"), unit="ms"),
                "updated": pd.to_datetime(p.get("updated"), unit="ms"),
                "latitude": g[1] if g else None,
                "longitude": g[0] if g else None,
                "depth_km": g[2] if g else None,
                "magnitude": p.get("mag"),
                "magType": p.get("magType"),
                "place": p.get("place"),
                "status": p.get("status"),
                "tsunami": p.get("tsunami"),
                "alert": p.get("alert"),
                "type": p.get("type"),
                "types": p.get("types"),
                "rms": p.get("rms"),
                "gap": p.get("gap"),
                "nst": p.get("nst"),
                "net": p.get("net"),
            })

df = pd.DataFrame(all_records)

print("Rows:", df.shape[0])
print("Columns:", df.shape[1])
print(df.head())

# Connect to MySQL
print("\n" + "="*70)
print("[*] CONNECTING TO MYSQL DATABASE...")
print("="*70)

try:
    host = os.getenv("MYSQL_HOST", "localhost")
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", "My$QL102511")
    database = os.getenv("MYSQL_DATABASE", "earthquake_db")
    
    print(f"Host: {host}")
    print(f"User: {user}")
    print(f"Database: {database}\n")
    
    # Step 1: Connect to MySQL without specifying database
    print("[*] Step 1: Connecting to MySQL server...")
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password
    )
    cursor = conn.cursor()
    print("[OK] Connected to MySQL server!")
    
    # Step 2: Create database if it doesn't exist
    print("[*] Step 2: Creating database if it doesn't exist...")
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    conn.commit()
    print(f"[OK] Database '{database}' is ready!")
    
    # Step 3: Close and reconnect to the specific database
    cursor.close()
    conn.close()
    
    print("[*] Step 3: Connecting to the specific database...")
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    cursor = conn.cursor()
    print(f"[OK] Connected to database '{database}'!\n")
    
except Error as err:
    if err.errno == 1045:
        print(f"[ERROR] Access denied: wrong username/password")
        print(f"\n[FIX] Set correct credentials via PowerShell:")
        print(f"   $env:MYSQL_USER = 'root'")
        print(f"   $env:MYSQL_PASSWORD = 'your_actual_password'")
        exit(1)
    elif err.errno == 2003:
        print(f"[ERROR] Cannot connect to MySQL server on '{host}'")
        print(f"\n[FIX] Make sure MySQL is running:")
        print(f"   1. Check Windows Services (MySQL80)")
        print(f"   2. Or try: mysql -u {user} -p")
        exit(1)
    else:
        print(f"[ERROR] MySQL Error ({err.errno}): {err}")
        exit(1)

try:
    # Create table
    create_table = """
    CREATE TABLE IF NOT EXISTS earthquakes (
        id VARCHAR(50) PRIMARY KEY,
        time DATETIME,
        updated DATETIME,
        latitude DOUBLE,
        longitude DOUBLE,
        depth_km DOUBLE,
        magnitude DOUBLE,
        magType VARCHAR(10),
        place TEXT,
        status VARCHAR(20),
        tsunami INT,
        alert VARCHAR(10),
        type VARCHAR(20),
        types VARCHAR(100),
        rms DOUBLE,
        gap DOUBLE,
        nst INT,
        net VARCHAR(10)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    cursor.execute(create_table)
    conn.commit()
    print("[OK] Table 'earthquakes' is ready\n")
    
except Error as err:
    print(f"[ERROR] Error creating table: {err}")
    exit(1)

try:
    # Insert records
    print(f"[*] Inserting {len(df)} records into database...")
    insert_query = """
    INSERT INTO earthquakes (
        id, time, updated, latitude, longitude, depth_km, magnitude, magType,
        place, status, tsunami, alert, type, types, rms, gap, nst, net
    ) VALUES (
        %(id)s, %(time)s, %(updated)s, %(latitude)s, %(longitude)s, %(depth_km)s, %(magnitude)s, %(magType)s,
        %(place)s, %(status)s, %(tsunami)s, %(alert)s, %(type)s, %(types)s, %(rms)s, %(gap)s, %(nst)s, %(net)s
    )
    ON DUPLICATE KEY UPDATE
        time=VALUES(time),
        updated=VALUES(updated),
        latitude=VALUES(latitude),
        longitude=VALUES(longitude),
        depth_km=VALUES(depth_km),
        magnitude=VALUES(magnitude),
        magType=VALUES(magType),
        place=VALUES(place),
        status=VALUES(status),
        tsunami=VALUES(tsunami),
        alert=VALUES(alert),
        type=VALUES(type),
        types=VALUES(types),
        rms=VALUES(rms),
        gap=VALUES(gap),
        nst=VALUES(nst),
        net=VALUES(net);
    """
    
    for idx, (_, row) in enumerate(df.iterrows(), 1):
        try:
            cursor.execute(insert_query, row.to_dict())
            if idx % 100 == 0:
                conn.commit()
                print(f"  [OK] Committed {idx} records...")
        except Error as e:
            print(f"[WARN] Error inserting row {idx}: {e}")
            continue
    
    conn.commit()
    print(f"[OK] All {len(df)} records inserted!\n")
    
except Error as err:
    print(f"[ERROR] Error during insert: {err}")
    exit(1)

try:
    # Verify
    cursor.execute("SELECT COUNT(*) FROM earthquakes")
    total = cursor.fetchone()[0]
    print("[OK] VERIFICATION:")
    print(f"  Total records in 'earthquakes': {total}\n")
    
    cursor.execute("""
    SELECT 
        COUNT(*) as total,
        MIN(magnitude) as min_mag,
        MAX(magnitude) as max_mag,
        ROUND(AVG(magnitude), 2) as avg_mag
    FROM earthquakes;
    """)
    stats = cursor.fetchone()
    print(f"  Magnitude Statistics:")
    print(f"    Min: {stats[1]:.2f}, Max: {stats[2]:.2f}, Avg: {stats[3]:.2f}")
    
except Error as err:
    print(f"[WARN] Verification error: {err}")

finally:
    cursor.close()
    conn.close()
    print("\n[OK] Connection closed")
    print("="*70)


