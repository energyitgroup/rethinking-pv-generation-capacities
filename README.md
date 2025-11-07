# Rethinking PV Generation Capacities
This repository is supporting the Solar World Conference Paper "Rethinking PV Generation Capacities", presented at the Solar World Congress 2025, Fortaleza, Brasil. 
It contains Python scripts for retrieving, processing, and analyzing photovoltaic (PV) generation data, including measured PV data and modeled data from the Global Solar Atlas (GSA).
The scripts support system orientation comparison, threshold-based analysis, and visualization of diurnal and monthly PV generation patterns.
## Repository Overview

The scripts in this repository form a workflow from data retrieval → aggregation → comparison → visualization.
They are designed for reproducible solar energy performance analysis, especially focusing on east/west orientation, monthly trends, and GSA data validation.Script Flow

### 1. api_utrecht.py
**Purpose:**  
Fetch and generate hourly PV production data for all PV units in Utrecht using the Global Solar Atlas (GSA) API and system metadata.

**Input:**  
- `metadata.csv` – Contains PV system metadata (ID, azimuth, tilt, DC capacity).

**Output:**  
- `gsa_data.csv` – Hourly PV generation (Wh) for each system.

---

### 2. get_gsa_moved.py
**Purpose:**  
Fetch monthly-hourly PV generation data from the GSA API for east- (90°) and west-facing (270°) systems with specified tilt and capacity.

**Features:**
- Fixed tilt angle and DC capacity  
- Converts GSA output to Wh scaled to system capacity  
- Saves long-format CSV of monthly hourly data

**Output:**  
- `mean_east_west_gsa_solar_data_scaled.csv` – Hourly generation for East/West systems

---

### 3. east_west_gsa.py
**Purpose:**  
Compare the GSA reference system (Utrecht) with East/West-oriented systems, both raw and scaled, and visualize differences.

**Input Files:**
- `mean_hourly_gsa_data.csv`  
- `mean_east_west_gsa_solar_data.csv`  
- `mean_east_west_gsa_solar_data_scaled.csv`

**Output:**
- `mean_east_west_gsa_comparison.png` – 2x2 comparison grid showing:
  - Reference generation  
  - East/West system generation  
  - Scaled generation  
  - Hourly deviations  

---

### 4. exceeds_threshold.py
**Purpose:**  
Calculate how often the systems exceed defined PV generation thresholds (50%, 65%, 80% of peak).

**Inputs:**
- `mean_east_west_gsa_solar_data_scaled.csv`  
- `mean_hourly_gsa_data.csv`

**Outputs:**
- `combined_EW_hours_above_multi_thresholds.csv`  
- `mean_hourly_hours_above_multi_thresholds.csv`  
- `hours_above_threshold_lines.png` – Visual summary of hours exceeding thresholds

---

### 5. mean_minute_per_id.py
**Purpose:**  
Aggregate measured PV power data to compute mean hourly values per month across multiple years for each system.

**Steps:**
1. Load `filtered_pv_power_measurements_ac.csv`  
2. Convert timestamps to datetime format  
3. Extract Year, Month, Hour  
4. Resample to hourly averages  
5. Group by Month and Hour to obtain mean profiles per system  
6. Save aggregated data

**Input:**  
- `filtered_pv_power_measurements_ac.csv`

**Output:**  
- `mean_hourly_per_month_per_id.csv`

---

### 6. six_grid_graphs.py
**Purpose:**  
Visualize PV generation profiles for various orientation and tilt combinations using six subplot grids.

**Process:**
1. Load and parse `grid_graphs.csv`  
2. Assign consistent color/line style for paired months (Jan–Dec, Feb–Nov, etc.)  
3. Plot six subplots (different orientation/tilt cases)  
4. Save figure

**Input:**  
- `grid_graphs.csv`

**Output:**  
- `six_grid_graphs.png`

---

### 7. violin_plot.py
**Purpose:**  
Compare measured PV generation and GSA-modeled estimations using a violin plot to show hourly difference distributions.

**Process:**
1. Load measured and GSA data:
   - `mean_hourly_per_month_per_id_final.csv`  
   - `gsa_solar_data.csv`
2. Calculate hourly absolute differences per system  
3. Generate violin plots:
   - Gray violins = distribution of hourly differences  
   - Orange line = mean  
   - Blue line = median  
4. Save figure

**Output:**  
- `seaborn_violinplot_absdiff_per_hour_corrected.png`

---
