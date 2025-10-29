"""
===========================================================
Script: east_west_gsa.py

Description:
------------
This script compares simulated photovoltaic (PV) generation data 
from three datasets:
    1. GSA reference system data (`mean_hourly_gsa_data.csv`)
    2. East-West PV system data (`mean_east_west_gsa_solar_data.csv`)
    3. Scaled East-West PV system data (`mean_east_west_gsa_solar_data_scaled.csv`)

It produces a 2x2 grid of plots showing:
    - (1,1): GSA reference generation by hour and month
    - (1,2): East-West system generation by hour and month
    - (2,1): Scaled East-West system generation
    - (2,2): Hourly deviation between scaled and GSA generation

The script also calculates:
    - The scaling factor between datasets
    - Total monthly and annual generation sums for each source

Finally, it saves the resulting figure as:
    `mean_east_west_gsa_comparison.png`

"""

import pandas as pd
import matplotlib.pyplot as plt

# === Load Data ===
df = pd.read_csv('mean_east_west_gsa_solar_data.csv')
df_scaled = pd.read_csv('mean_east_west_gsa_solar_data_scaled.csv')
df_gsa = pd.read_csv('mean_hourly_gsa_data.csv')

# === Prepare Data ===
df_gsa_wide = df_gsa.pivot(index='Month', columns='Hour', values='Generation').reset_index()

hour_cols = [c for c in df.columns if c.startswith('Hour ')]
hour_cols_scaled = [c for c in df_scaled.columns if c.startswith('Hour ')]
hour_cols_gsa = [c for c in df_gsa.columns if c.startswith('Hour ')]
hours = list(range(1, 25))

month_order = pd.date_range('2024-01-01', periods=12, freq='MS').strftime('%B').tolist()

# === Define Colors and Styles ===
colors = plt.cm.tab10.colors[:6]
paired_months = [
    ("January", "December"),
    ("February", "November"),
    ("March", "October"),
    ("April", "September"),
    ("May", "August"),
    ("June", "July")
]

color_map = {m: colors[i] for i, pair in enumerate(paired_months) for m in pair}
line_style_map = {m: "-" if i == 0 else ":" for pair in paired_months for i, m in enumerate(pair)}

# === Plot Setup ===
fig, axes = plt.subplots(2, 2, figsize=(42, 25), sharey=True)
for row in axes:
    for ax in row:
        ax.set_xlabel("Hour of Day", fontsize=28)
        ax.title.set_fontsize(30)
        ax.grid(axis='y', linestyle='--', alpha=0.6)
        ax.set_xticks(range(0, 25, 2))
        ax.tick_params(axis='x', labelsize=24)
        ax.tick_params(axis='y', labelsize=24)

# === Helper Function for Month Sorting ===
def month_sort_key(month):
    return pd.to_datetime(month, format='%B').month

# === Plot 1: Simulated Reference PV System (GSA Data) ===
for month, month_data in df_gsa.groupby('Month'):
    axes[0, 0].plot(
        month_data['Hour'], month_data['Generation'],
        label=f'Month {month}',
        color=color_map.get(month, 'gray'),
        linestyle=line_style_map.get(month, '-'),
        linewidth=3.5
    )
axes[0, 0].set_title('Simulated Reference PV System', fontsize=30)
axes[0, 0].set_ylabel('Generation (Wh)', fontsize=28)

# === Plot 2: East-West PV Systems ===
for month, month_data in df.groupby('Month'):
    sum_per_hour = month_data[hour_cols].sum()
    axes[0, 1].plot(
        hours, sum_per_hour.values,
        label=month,
        color=color_map.get(month, 'gray'),
        linestyle=line_style_map.get(month, '-'),
        linewidth=3.5
    )
axes[0, 1].set_title('East-West PV Systems', fontsize=30)

# === Compute Scaling Factor (GSA vs East-West) ===
gsa_sum_max = df_gsa.groupby('Month')['Generation'].max().max()
east_west_sum_max = df[hour_cols].sum().max()
scaling_factor = gsa_sum_max / east_west_sum_max if east_west_sum_max else 1

print(f'Scaling factor: {scaling_factor}\nGSA sum max: {gsa_sum_max}\nEast + West sum max: {east_west_sum_max}')

# === Plot 3: Scaled East-West PV Systems ===
for month, month_data in df_scaled.groupby('Month'):
    sum_per_hour = month_data[hour_cols_scaled].sum()
    axes[1, 0].plot(
        hours, sum_per_hour.values,
        label=month,
        color=color_map.get(month, 'gray'),
        linestyle=line_style_map.get(month, '-'),
        linewidth=3.5
    )
axes[1, 0].set_title('Scaled East-West PV Systems', fontsize=30)
axes[1, 0].set_xlabel('Hour of Day', fontsize=28)
axes[1, 0].set_ylabel('Generation (Wh)', fontsize=28)

# === Plot 4: Deviation (Scaled – Mean) ===
common_months = df_gsa_wide['Month'].isin(df_scaled['Month']).replace(False, None)
for month in df_gsa_wide.loc[common_months, 'Month']:
    gsa_row = df_gsa_wide.loc[df_gsa_wide['Month'] == month, list(range(1, 25))].values.flatten()
    scaled_sum = df_scaled.loc[df_scaled['Month'] == month, hour_cols_scaled].sum().values
    diff = scaled_sum - gsa_row
    print(f"Difference for month {month}: {diff}")
    axes[1, 1].plot(
        hours, diff,
        label=month,
        color=color_map.get(month, 'gray'),
        linestyle=line_style_map.get(month, '-'),
        linewidth=3.5
    )
axes[1, 1].set_title('Deviation in Hourly Generation (Scaled – Mean)', fontsize=30)
axes[1, 1].set_xlabel('Hour of Day')

# === Shared Legend ===
handles, labels = axes[0, 0].get_legend_handles_labels()
clean_labels = [lbl.replace("Month ", "") for lbl in labels]
label_to_handle = dict(zip(clean_labels, handles))

sorted_labels = [m for m in month_order if m in label_to_handle]
sorted_handles = [label_to_handle[m] for m in sorted_labels]

fig.legend(
    sorted_handles, sorted_labels,
    loc='lower center',
    bbox_to_anchor=(0.5, -0.02),
    fontsize=28,
    ncol=6,
    frameon=False,
    labelspacing=1.5,
    handlelength=3.0,
    handletextpad=0.8
)

plt.tight_layout(rect=[0, 0.07, 1, 1])
plt.savefig('mean_east_west_gsa_comparison.png', dpi=300, bbox_inches='tight')

# === Summaries ===
def total_generation(df, hour_cols):
    return df.groupby('Month')[hour_cols].sum().sum().sum()

gsa_total_sum = df_gsa['Generation'].sum()
east_west_total_sum = total_generation(df, hour_cols)
scaled_csv_total_sum = total_generation(df_scaled, hour_cols_scaled)

print(f"Total original GSA generation data: {gsa_total_sum}")
print(f"Total scaled east+west generation data: {east_west_total_sum}")
print(f"Total generation from scaled CSV data: {scaled_csv_total_sum}")
