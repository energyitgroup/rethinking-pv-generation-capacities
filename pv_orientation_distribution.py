"""
Script Name: pv_orientation_distribution.py

Description:
    This script analyzes the metadata of photovoltaic (PV) systems to determine 
    their distribution by **orientation**, **tilt angle**, and **estimated DC capacity**.

    Steps performed:
      1. Load the metadata CSV file ('metadata.csv'), which uses semicolon separators.
      2. Categorize each PV system into an orientation group based on azimuth:
            - North (315–45°)
            - East (45–135°)
            - South (135–225°)
            - West (225–315°)
      3. Count the number of systems in each orientation group and export results.
      4. Categorize each PV system into a tilt group based on tilt angle:
            - < 20°
            - 20–40°
            - 40–60°
            - > 60°
      5. Count the number of systems in each tilt group and export results.
      6. Calculate the mean estimated DC capacity across all PV systems.

    Input:
        - metadata.csv
          (Contains fields such as 'azimuth', 'tilt', and 'estimated_dc_capacity')

    Output:
        - pv_orientation_group_distribution.csv   → Count of PV systems per orientation
        - pv_tilt_group_distribution.csv           → Count of PV systems per tilt range
        - Printed summary statistics in console

Usage:
    python pv_orientation_distribution.py
"""

import pandas as pd

# Load the metadata CSV (semicolon separated)
df = pd.read_csv('metadata.csv', sep=';')

# Define orientation groups based on azimuth
def orientation_group(azimuth):
    azimuth = float(azimuth)
    if 135 <= azimuth <= 225:
        return 'South'
    elif 45 <= azimuth < 135:
        return 'East'
    elif 225 < azimuth <= 315:
        return 'West'
    else:
        return 'North'

df['Orientation'] = df['azimuth'].apply(orientation_group)

# Count the number of systems in each orientation group
orientation_counts = df['Orientation'].value_counts().sort_index()

print("Distribution of PV systems by orientation group:")
print(orientation_counts)

# Optionally, save to CSV
orientation_counts.to_csv('pv_orientation_group_distribution.csv', header=['Count'])

# Define tilt groups based on tilt
def tilt_group(tilt):
    azimuth = float(tilt)
    if tilt < 20:
        return '< 20 Grad'
    elif 20 <= tilt < 40:
        return '20 - 40 Grad'
    elif 40 < tilt <= 60:
        return '40 - 60 Grad'
    else:
        return '> 60 Grad'

df['Tilt_Group'] = df['tilt'].apply(tilt_group)

# Count the number of systems in each tilt group
tilt_counts = df['Tilt_Group'].value_counts().sort_index()

print("\nDistribution of PV systems by tilt group:")
print(tilt_counts)

# Optionally, save to CSV
tilt_counts.to_csv('pv_tilt_group_distribution.csv', header=['Count'])

# Calculate the sum of estimated_dc_capacity for all PV systems
total_dc_capacity = df['estimated_dc_capacity'].astype(float).mean()
print(f"\nTotal estimated DC capacity for all PV systems: {total_dc_capacity}")