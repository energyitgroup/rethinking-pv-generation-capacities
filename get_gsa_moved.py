"""
Title: Fetch East/West GSA Solar PV Data

Description:
------------
This script fetches monthly-hourly PV generation data from the Global Solar Atlas (GSA) API
for east- and west-facing PV systems with a specified tilt and capacity. The output is saved
as a CSV file.

Features:
---------
- Fetches data for East (90°) and West (270°) orientations.
- Uses a fixed tilt angle and DC capacity.
- Converts GSA output to Wh scaled to system capacity.
- Saves data in long-format CSV with monthly hourly values.

Outputs:
--------
- 'mean_east_west_gsa_solar_data_scaled.csv': Monthly hourly generation for East/West PV systems.

Dependencies:
-------------
- pandas
- requests
"""

import requests
import pandas as pd

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
        "loc": "48.35007,10.901184",
        "gmtOffset": 0
    }
    payload = {
        "type": "rooftopSmall",
        "systemSize": {
            "type": "capacity",
            "value": cap / 1000  # in kW
        },
        "orientation": {
            "azimuth": azimuth,
            "tilt": tilt
        }
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, params=params, json=payload, headers=headers)
    full_data = response.json()
    data = full_data['monthly-hourly']['data']['PVOUT_specific']
    return data

all_combined_data = []

for orientation, azimuth in [("East", 90), ("West", 270)]:
    tilt = 55
    cap = 1140.75 * 1.5  # in W
    print(f"Processing {orientation}: azimuth={azimuth}, tilt={tilt}, cap={cap}")
    try:
        solar_data = fetch_solar_data(azimuth, tilt, cap)
        updated_data = [[round(float(output / 1000 * cap), 2) for output in month] for month in solar_data]
        for month_idx, month_data in enumerate(updated_data):
            all_combined_data.append({
                "Orientation": orientation,
                "Azimuth": azimuth,
                "Tilt": tilt,
                "Month": months[month_idx + 1],
                **{f"Hour {hour_idx + 1}": value for hour_idx, value in enumerate(month_data)}
            })
    except Exception as e:
        print(f"Fehler für {orientation}: {e}")

all_combined_df = pd.DataFrame(all_combined_data)
all_combined_df.to_csv('mean_east_west_gsa_solar_data_scaled.csv', index=False)
print('East/West GSA solar data saved to mean_east_west_gsa_solar_data_scaled.csv')
