"""
Title: PV Generation Threshold Analysis (East/West Combined & Mean-Hourly GSA)

Description:
------------
This script analyzes photovoltaic (PV) generation data to determine the number 
of hours per month where generation exceeds 50%, 65%, and 80% of the monthly 
maximum mean-hourly generation.

It compares:
1. Combined East/West-oriented PV systems (scaled).
2. Mean-hourly Global Solar Atlas (GSA) data.

Outputs:
    • CSV files:
        - combined_EW_hours_above_multi_thresholds.csv
        - mean_hourly_hours_above_multi_thresholds.csv
    • A line plot (hours_above_threshold_lines.png)
    • Printed summaries of total hours above each threshold
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# === File Paths ===
CSV_FILE = "mean_east_west_gsa_solar_data_scaled.csv"
GSA_FILE = "mean_hourly_gsa_data.csv"

# === Load Data ===
df_gsa = pd.read_csv(GSA_FILE)
df_ew = pd.read_csv(CSV_FILE)

# === Month Order (Consistent Sorting) ===
MONTH_ORDER = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]
for df in [df_gsa, df_ew]:
    df["Month"] = pd.Categorical(df["Month"], categories=MONTH_ORDER, ordered=True)

# === Identify Hour Columns ===
HOUR_COLS = [c for c in df_ew.columns if c.startswith("Hour")]

# === Threshold Levels ===
THRESHOLDS = [0.5, 0.65, 0.8]

# === Precompute Monthly Maximum Generation (from GSA) ===
monthly_max_gsa = df_gsa.groupby("Month")["Generation"].max()

# -------------------------------------------------------------------------
# Helper Function: Calculate Hours Above Threshold
# -------------------------------------------------------------------------
def calc_hours_above_threshold(df_subset, max_gen, levels, hour_cols):
    """Calculate hours and percentages above threshold for a given subset."""
    combined_hours = df_subset[hour_cols].sum()
    total_hours = len(hour_cols)
    results = []
    for level in levels:
        threshold = max_gen * level
        hours_above = (combined_hours > threshold).sum()
        perc_above = hours_above / total_hours * 100
        results.append((level, threshold, hours_above, perc_above))
    return results

# -------------------------------------------------------------------------
# Process East/West Combined Data
# -------------------------------------------------------------------------
ew_records = []
for (tilt, month), subset in df_ew[
    df_ew["Orientation"].isin(["East", "West"])
].groupby(["Tilt", "Month"]):
    max_gen = monthly_max_gsa.get(month)
    if pd.isna(max_gen):
        continue
    for level, threshold, hours_above, perc_above in calc_hours_above_threshold(
        subset, max_gen, THRESHOLDS, HOUR_COLS
    ):
        ew_records.append({
            "Tilt": tilt,
            "Month": month,
            "Threshold_Level": f"{int(level * 100)}%",
            "Threshold_Value": threshold,
            "Hours_Above_Threshold": hours_above,
            "Percentage_Above_Threshold": perc_above
        })

df_ew_result = pd.DataFrame(ew_records)
df_ew_result.to_csv("combined_EW_hours_above_multi_thresholds.csv", index=False)

# -------------------------------------------------------------------------
# Process Mean-Hourly GSA Data
# -------------------------------------------------------------------------
mean_records = []
for month, subset in df_gsa.groupby("Month"):
    max_gen = monthly_max_gsa.get(month)
    if pd.isna(max_gen):
        continue
    for level in THRESHOLDS:
        threshold = max_gen * level
        hours_above = (subset["Generation"] > threshold).sum()
        perc_above = hours_above / 24 * 100  # 24 hourly samples
        mean_records.append({
            "Month": month,
            "Threshold_Level": f"{int(level * 100)}%",
            "Threshold_Value": threshold,
            "Hours_Above_Threshold": hours_above,
            "Percentage_Above_Threshold": perc_above
        })

df_mean_result = pd.DataFrame(mean_records)
df_mean_result.to_csv("mean_hourly_hours_above_multi_thresholds.csv", index=False)

# -------------------------------------------------------------------------
# Totals per Threshold
# -------------------------------------------------------------------------
def print_totals(df, label):
    print(f"\nTotal hours above thresholds ({label}):")
    for level in THRESHOLDS:
        lvl_str = f"{int(level * 100)}%"
        total = df.loc[df["Threshold_Level"] == lvl_str, "Hours_Above_Threshold"].sum()
        print(f"  > {lvl_str}: {total} hours")

print_totals(df_ew_result, "East/West combined")
print_totals(df_mean_result, "Mean-hourly GSA")

# -------------------------------------------------------------------------
# Visualization: Hours Above Threshold per Month
# -------------------------------------------------------------------------
combined_df = pd.concat([
    df_mean_result.assign(Source="Mean-Hourly GSA"),
    df_ew_result.assign(Source="East/West Combined")
])

combined_df["Month"] = pd.Categorical(combined_df["Month"], categories=MONTH_ORDER, ordered=True)
combined_df = combined_df.sort_values("Month")

# --- Plot Style ---
sns.set_theme(style="whitegrid")
fig, ax = plt.subplots(figsize=(14, 7))

# --- Base Colors ---
COLORS = {"Mean-Hourly GSA": "#4E79A7", "East/West Combined": "#F28E2B"}

# --- Line Styles for Thresholds ---
STYLES = {"50%": "dotted", "65%": "dashdot", "80%": "solid"}

for (source, color), (level, style) in [
    ((src, COLORS[src]), (th, STYLES[th])) 
    for src in COLORS for th in STYLES
]:
    subset = combined_df[
        (combined_df["Source"] == source) &
        (combined_df["Threshold_Level"] == level)
    ]
    if not subset.empty:
        ax.plot(
            subset["Month"],
            subset["Hours_Above_Threshold"],
            color=color,
            linestyle=style,
            marker="o",
            linewidth=2.5,
            label=f"{source} – {level}"
        )

# --- Axis & Legend ---
ax.set_xlabel("Month", fontsize=12)
ax.set_ylabel("Hours Above Threshold", fontsize=12)
ax.tick_params(axis="x", rotation=45)
ax.legend(title="Dataset & Threshold", fontsize=10, title_fontsize=11, ncol=2)
ax.set_ylim(0, None)

plt.tight_layout()
plt.savefig("hours_above_threshold_lines.png", dpi=300)
plt.show()
