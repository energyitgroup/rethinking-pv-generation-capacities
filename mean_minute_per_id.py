"""
Script Name: mean_minute_per_id.py

Description:
    This script processes photovoltaic (PV) power measurement data to compute
    the mean hourly values for each month across multiple years.

    Steps performed:
      1. Load the input CSV file ('filtered_pv_power_measurements_ac.csv').
      2. Convert the 'DateTime' column to a proper datetime format.
      3. Extract temporal features (Year, Month, Hour) from the timestamp.
      4. Resample data to hourly means to smooth out intra-hour variations.
      5. Group by Month and Hour to calculate the mean hourly value for each ID
         across all years (representing typical monthly diurnal patterns).
      6. Save the aggregated results to a new CSV file
         ('mean_hourly_per_month_per_id.csv').

    Input:
        - filtered_pv_power_measurements_ac.csv
          (Contains timestamped PV power measurements for multiple IDs)

    Output:
        - mean_hourly_per_month_per_id.csv
          (Contains the mean hourly PV power per month and per ID)

    Example Output Columns:
        Month, Hour, ID_1, ID_2, ID_3, ...

Usage:
    python mean_minute_per_id.py
"""

import pandas as pd

# Load the CSV file
csv_file = 'filtered_pv_power_measurements_ac.csv'
df = pd.read_csv(csv_file)

df['DateTime'] = pd.to_datetime(df['DateTime'])
#df = df.set_index('DateTime')
df['Year'] = df['DateTime'].dt.year
df['Month'] = df['DateTime'].dt.month
# Use hour only (not minute)
df['Hour'] = df['DateTime'].dt.hour

print(df.head())

# Identify ID columns (all except metadata columns)
id_columns = [col for col in df.columns if col not in ['DateTime', 'Month', 'Hour', 'Year']]

# Resample to hourly means
hourly_df = df.resample('1h', on='DateTime')[id_columns].mean().reset_index()

# Add Month and Hour columns
hourly_df['Month'] = hourly_df['DateTime'].dt.month
hourly_df['Hour'] = hourly_df['DateTime'].dt.hour

# Group by Month and Hour, take mean across all years for each ID
result_df = hourly_df.groupby(['Month', 'Hour'])[id_columns].mean().reset_index()

# Save to new CSV with 'Month' and 'Hour' as the first columns
cols = ['Month', 'Hour'] + id_columns
result_df = result_df[cols]
result_df.to_csv('mean_hourly_per_month_per_id.csv', index=False)
print('Mean hourly value for each ID and month saved to mean_hourly_per_month_per_id.csv')
