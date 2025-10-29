"""
Script Name: six_grid_graphs.py

Description:
    This script visualizes hourly PV generation data for different
    combinations of orientation and tilt using 'grid_graphs.csv' as input.

    The process:
      1. Load and parse the input CSV.
      2. Assign colors and line styles to month pairs for visual consistency.
      3. Create six subplots showing generation profiles for selected
         combinations of orientation and tilt.
      4. Plot monthly curves (January–December) for each case.
      5. Save the final figure as 'six_grid_graphs.png'.

Input:
    - grid_graphs.csv

Output:
    - six_grid_graphs.png

Usage:
    python six_grid_graphs.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import ast
from deep_translator import GoogleTranslator

# Load and preprocess data
df = pd.read_csv("grid_graphs.csv")
df["daten"] = df["daten"].apply(ast.literal_eval)

# Define color and style scheme for opposite month pairs
colors = plt.cm.tab10.colors[:6]
paired_months = [
    ("January", "December"),
    ("February", "November"),
    ("March", "October"),
    ("April", "September"),
    ("May", "August"),
    ("June", "July")
]

color_map = {}
line_style_map = {}
for i, (m1, m2) in enumerate(paired_months):
    color_map[m1] = color_map[m2] = colors[i]
    line_style_map[m1] = "-"
    line_style_map[m2] = ":"

# Orientation and tilt labels
orientations = {0: "Nord", 1: "Ost", 2: "Süd", 3: "West"}
tilts = {1: "20 - 40 Grad", 3: "> 60 Grad"}

months = {
    0: "January", 1: "February", 2: "March", 3: "April",
    4: "May", 5: "June", 6: "July", 7: "August",
    8: "September", 9: "October", 10: "November", 11: "December"
}

# Define combinations of orientation and tilt
plot_combinations = [
    {"orientation": "Süd", "tilt": "20 - 40 Grad"},
    {"orientation": "Ost", "tilt": "20 - 40 Grad"},
    {"orientation": "West", "tilt": "20 - 40 Grad"},
    {"orientation": "Nord", "tilt": "> 60 Grad"},
    {"orientation": "Ost", "tilt": "> 60 Grad"},
    {"orientation": "West", "tilt": "> 60 Grad"},
]

# Create subplot grid
fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(42, 15), sharex=True, sharey=True)
axes = axes.flatten()

# Common axis formatting
for i, ax in enumerate(axes):
    ax.grid(axis="y", linestyle="--", alpha=0.6)
    ax.tick_params(axis="both", which="major", labelsize=14)
    ax.set_xticks(range(0, 25, 2))
    ax.set_xlabel("Hour of Day" if i >= 3 else "", fontsize=14)
    ax.set_ylabel("Generation (kWh)" if i % 3 == 0 else "", fontsize=14)

# Translator (German → English)
translator = GoogleTranslator(source="de", target="en")

# Plot data
for i, combo in enumerate(plot_combinations):
    tilt = combo["tilt"]
    orientation = combo["orientation"]
    filtered = df[(df["ausrichtung"] == orientation) & (df["neigung"] == tilt)]

    if filtered.empty:
        print(f"No data available for {orientation} / {tilt}.")
        continue

    for row in filtered["daten"]:
        for month_index, values in enumerate(row):
            month_name = months[month_index]
            axes[i].plot(
                range(1, 25),
                values,
                label=month_name,
                color=color_map[month_name],
                linestyle=line_style_map[month_name],
                linewidth=2,
            )

    eng_orientation = translator.translate(orientation)
    eng_tilt = translator.translate(tilt)
    axes[i].set_title(f"{eng_orientation}: {eng_tilt}", fontsize=16)
    axes[i].grid(axis="y", linestyle="--", alpha=0.6)

# Layout and legend
plt.tight_layout(pad=2.0, w_pad=1.5, h_pad=4.0, rect=[0, 0.09, 1, 1])
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, fontsize=12, loc="lower center", ncol=6)

# Save figure
fig.set_size_inches(15, 8)
plt.savefig("six_grid_graphs.png", dpi=300, bbox_inches="tight")
plt.show()
