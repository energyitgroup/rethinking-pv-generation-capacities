"""
Title: Fetch and Save GSA Solar PV Data

Description:
------------
This script retrieves hourly PV generation data from the Global Solar Atlas (GSA) API
for a list of PV systems defined in 'metadata.csv'. It calculates monthly hourly output
based on system azimuth, tilt, and estimated DC capacity, and saves the results to a CSV.

Features:
---------
- Converts azimuth and tilt from metadata to numeric values.
- Scales PV output to the system's DC capacity.
- Saves combined monthly-hourly data for all PV systems.
- Maps month indices to English month names.

Inputs:
-------
- 'metadata.csv': Metadata including ID, azimuth, tilt, estimated DC capacity.

Outputs:
--------
- 'gsa_data.csv': Monthly hourly PV generation (Wh) per system.

Dependencies:
-------------
- pandas
- requests
- urllib.parse
- json
"""

import requests
import urllib.parse
import json
import pandas as pd
import matplotlib.pyplot as plt
from deep_translator import GoogleTranslator


ausrichtungen = {
  "Nord": 0,
  "Nord-Ost": 45,
  "Ost": 90,
  "Süd-Ost": 135,
  "Süd": 180,
  "Süd-West": 225,
  "West": 270,
  "Nord-West": 315,
  "Ost-West": 360,      # ?????
}

neigungen = {
    "< 20 Grad": 10,
    "20 - 40 Grad": 30,
    "40 - 60 Grad": 50,
    "> 60 Grad": 70,
    "Fassadenintegriert": 90,
    "Nachgeführt": 0
}

months = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December"
}

def fetch_solar_data(azimuth, tilt, cap):
    url = "https://api.globalsolaratlas.info/data/pvcalc"

    params = {
        "loc": "48.35007,10.901184",  # lat,lon
        "gmtOffset": 0                # Germany/Austria (UTC+1 standard time)
    }

    payload = {
        "type": "rooftopSmall",
        "systemSize": {
            "type": "capacity",
            "value": cap / 1000  # 1 kWp
        },
        "orientation": {
            "azimuth": azimuth,  # Facing south
            "tilt": tilt       # 36° tilt
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, params=params, json=payload, headers=headers)
    full_data = response.json()
    data = full_data['monthly-hourly']['data']['PVOUT_specific']
    return data

def fetch_query(query):
    base_url = "http://127.0.0.1:8000/api/database"
    encoded_query = urllib.parse.quote(query)
    url = f"{base_url}?query={encoded_query}"

    response = requests.get(url)

    if not response.ok:
        raise Exception(f"HTTP-Fehler: {response.status_code}")

    return response.json()

metadata_df = pd.read_csv('metadata.csv', sep=';')
print(metadata_df.head())
all_combined_data = []

for index, row in metadata_df.iterrows():
    #print(row)
    id_value = row['ID']
    # lat = row['lat']
    # lon = row['lon']
    azimuth = row.get('azimuth', 180)
    tilt = row.get('tilt', 30)
    cap = row.get('estimated_dc_capacity', 1)

    print(f"Processing ID: {id_value}, lat: {52.092876}, lon: {5.104480}, azimuth: {azimuth}, tilt: {tilt}")
    try:
        solar_data = fetch_solar_data(azimuth, tilt, cap)
        print(solar_data)
        updated_data = [[round(float(output / 1000 * cap), 2) for output in month] for month in solar_data]
        for month_idx, month_data in enumerate(updated_data):
            all_combined_data.append({
                "ID": id_value,
                "Azimuth": azimuth,
                "Tilt": tilt,
                "Month": months[month_idx + 1],
                **{f"Hour {hour_idx + 1}": value for hour_idx, value in enumerate(month_data)}
            })

        
    except Exception as e:
        print(f"Fehler für ID {id_value}: {e}")

# Save all combined data to a CSV file with column names as the first row
all_combined_df = pd.DataFrame(all_combined_data)
all_combined_df.to_csv('gsa_data.csv', index=False)
print('GSA solar data saved to gsa_data.csv')
