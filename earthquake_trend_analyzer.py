import requests
import pandas as pd
from datetime import datetime

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
        # adding a comment to view in github to test the git feature

df = pd.DataFrame(all_records)

print("Rows:", df.shape[0])
print("Columns:", df.shape[1])
print(df.head())
