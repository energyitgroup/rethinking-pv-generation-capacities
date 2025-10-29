"""
Script Name: violin_plot.py

Description:
    This script compares measured PV generation data with modeled GSA solar estimations
    and visualizes the hourly differences using a violin plot.

    The process:
      1. Load two CSV files:
         - 'mean_hourly_per_month_per_id_final.csv' → Measured or aggregated PV data
         - 'gsa_solar_data.csv' → Modeled solar estimation data (GSA)
      2. For each hour (1–24) and each system ID:
         - Extract mean measured and GSA-estimated values
         - Compute the absolute difference (ignoring near-zero values)
      3. Store all hourly differences in a combined DataFrame.
      4. Generate a violin plot (via Seaborn) showing the distribution of hourly differences:
         - Gray violins represent distribution per hour.
         - Overlayed lines show hourly mean (orange) and median (blue).
      5. Save the resulting visualization as 'seaborn_violinplot_absdiff_per_hour_corrected.png'.

    Inputs:
        - mean_hourly_per_month_per_id_final.csv
        - gsa_solar_data.csv

    Output:
        - seaborn_violinplot_absdiff_per_hour_corrected.png (hourly difference distribution plot)

Usage:
    python violin_plot.py
"""
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# --- Set Seaborn theme for consistent styling ---
sns.set_theme(style="whitegrid", context="talk")

# --- Load input CSVs ---
df_mean = pd.read_csv("mean_hourly_per_month_per_id.csv")
df_gsa = pd.read_csv("gsa_data.csv")

# --- Collect differences for each hour and system ID ---
data_list = []

ids = df_gsa["ID"].unique()

for hour in range(1, 25):  # Loop through hours 1–24
    hour_diffs = []  # Temporary storage to check valid data presence

    for id_ in ids:
        # Extract measured and modeled values for this hour and ID
        mean_vals = df_mean.loc[df_mean["Hour"] == hour, f"{id_}"].values
        gsa_vals = df_gsa.loc[df_gsa["ID"] == id_, f"Hour {hour}"].values

        # Skip if data is missing
        if len(mean_vals) == 0 or len(gsa_vals) == 0:
            continue

        # Compute and filter small differences
        diffs = np.subtract(mean_vals, gsa_vals)
        diffs = diffs[np.abs(diffs) > 0.01]

        # Store differences
        if len(diffs) > 0:
            for d in diffs:
                data_list.append({"Hour": hour, "Difference": d, "ID": id_})
            hour_diffs.extend(diffs)

    # Skip empty hours (no valid data)
    if len(hour_diffs) == 0:
        print(f"No valid data for hour {hour}, skipping.")

# --- Create DataFrame for plotting ---
plot_df = pd.DataFrame(data_list)
valid_hours = sorted(plot_df["Hour"].unique())
print(f"Using {len(valid_hours)} valid hours: {valid_hours}")

# --- Compute mean and median per hour ---
hour_stats = plot_df.groupby("Hour")["Difference"].agg(["mean", "median"]).reset_index()

# --- Create violin plot ---
plt.figure(figsize=(14, 6))
ax = sns.violinplot(
    data=plot_df,
    x="Hour",
    y="Difference",
    inner=None,
    color="lightgray",
    linewidth=1,
    scale="width"
)

# --- Overlay scatter points (individual values) ---
sns.stripplot(
    data=plot_df,
    x="Hour",
    y="Difference",
    color="#1F1F1F",
    size=2,
    alpha=0.7,
    ax=ax
)

# --- Prepare x-position mapping for connecting mean & median lines ---
xticks = dict(zip(valid_hours, range(len(valid_hours))))
x_positions = [xticks[h] for h in hour_stats["Hour"]]

# --- Draw connected mean and median lines ---
ax.plot(x_positions, hour_stats["mean"], color="#FF8A37", linewidth=2, label="Average")
ax.plot(x_positions, hour_stats["median"], color="#537EFF", linewidth=2, label="Median")

# --- Style and labels ---
ax.set_xticks(range(len(valid_hours)))
ax.set_xticklabels(valid_hours)
ax.set_xlabel("Hour of the Day", fontsize=13)
ax.set_ylabel("Difference (Wh)", fontsize=13)
ax.legend()
ax.grid(axis="y", linestyle="--", alpha=0.6)

plt.tight_layout()
plt.savefig("seaborn_violinplot_absdiff_per_hour.png", dpi=300)
plt.show()