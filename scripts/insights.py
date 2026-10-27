# %% [markdown]
# ## 1. Problem Statement
# Review when and where inverter-hours show negative performance-ratio gaps.
# This is an initial descriptive analysis of the simulated solar dataset.

# %%
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TABLES = PROJECT_ROOT / "output/tables"
SQL_RESULTS = PROJECT_ROOT / "output/sql_results"
FIGURES = PROJECT_ROOT / "output/figures"
FIGURES.mkdir(parents=True, exist_ok=True)


# %% [markdown]
# ## 2. Summary Statistics
# Use the saved summary table so this report reads only compact output artifacts.

# %%
summary_statistics = pd.read_csv(TABLES / "summary_statistics.csv")
print("Summary statistics and missing-value counts")
print(summary_statistics.to_string(index=False))


# %% [markdown]
# ## 3. Charts
# Each chart uses saved tables and is exported as a PNG for the written report.

# %%
plt.style.use("seaborn-v0_8-whitegrid")

hourly = pd.read_csv(TABLES / "hourly_mean_pr.csv")
figure, axis = plt.subplots(figsize=(9, 5))
axis.plot(
    hourly["hour"],
    hourly["mean_daytime_pr"],
    marker="o",
    color="#287b72",
)
axis.set(
    title="Mean Daytime Performance Ratio by Hour of Day",
    xlabel="Hour of day",
    ylabel="Mean performance ratio (unitless)",
)
axis.set_xticks(range(0, 24, 2))
figure.tight_layout()
figure.savefig(FIGURES / "pr_by_hour_of_day.png", dpi=140)
plt.close(figure)


# %%
monthly = pd.read_csv(TABLES / "monthly_mean_pr_by_group.csv")
figure, axis = plt.subplots(figsize=(10, 5))
for group, color in [("Faulted", "#b44b40"), ("Non-faulted", "#376f9d")]:
    group_rows = monthly[monthly["inverter_group"] == group].sort_values("month")
    axis.plot(
        group_rows["month"],
        group_rows["mean_daytime_pr"],
        marker="o",
        label=group,
        color=color,
    )
axis.set(
    title="Monthly Mean Daytime PR: Faulted vs Non-faulted Inverters",
    xlabel="Month",
    ylabel="Mean performance ratio (unitless)",
)
axis.tick_params(axis="x", rotation=45)
axis.legend(frameon=False)
figure.tight_layout()
figure.savefig(FIGURES / "monthly_mean_pr_by_group.png", dpi=140)
plt.close(figure)


# %%
fault_day = pd.read_csv(TABLES / "fault_day_pr_101_202_303.csv")
fault_day["DATE_TIME"] = pd.to_datetime(fault_day["DATE_TIME"])
figure, axes = plt.subplots(3, 1, figsize=(9, 9), sharex=True, sharey=True)
fault_dates = {
    101: "2025-03-15",
    202: "2025-06-20",
    303: "2025-09-10",
}
for axis, (inverter_id, fault_date) in zip(axes, fault_dates.items()):
    rows = fault_day[fault_day["INVERTER_ID"] == inverter_id].sort_values("DATE_TIME")
    axis.plot(
        rows["DATE_TIME"].dt.hour,
        rows["PERFORMANCE_RATIO"],
        marker="o",
        color="#bc7138",
    )
    axis.set_title(f"Inverter {inverter_id}, {fault_date}")
    axis.set_ylabel("Performance ratio (unitless)")
    axis.set_xticks(range(0, 24, 2))
axes[-1].set_xlabel("Hour of day")
figure.suptitle("Performance Ratio on Simulated Fault Days", y=1.01)
figure.tight_layout()
figure.savefig(FIGURES / "fault_day_pr_101_202_303.png", dpi=140, bbox_inches="tight")
plt.close(figure)


# %%
scatter = pd.read_csv(TABLES / "scatter_sample_100k.csv.gz")
figure, axis = plt.subplots(figsize=(8, 6))
axis.scatter(
    scatter["IRRADIANCE"],
    scatter["AC_POWER"],
    s=4,
    alpha=0.16,
    color="#287b72",
    rasterized=True,
)
axis.axhline(
    60,
    color="#b44b40",
    linewidth=1.2,
    linestyle="--",
    label="60 kW rated AC clip",
)
axis.set(
    title="Irradiance and AC Power",
    xlabel="Plane-of-array irradiance (W/m²)",
    ylabel="AC power (kW)",
)
axis.legend(frameon=False)
figure.tight_layout()
figure.savefig(FIGURES / "irradiance_vs_ac_power.png", dpi=140)
plt.close(figure)


# %% [markdown]
# ## 4. Cautious Inference
# Compare weighted mean daytime PR across faulted and non-faulted inverter-hours.
# A module-temperature correlation needs paired compact observations, not aggregate summaries.

# %%
monthly["weighted_pr"] = monthly["mean_daytime_pr"] * monthly["daytime_rows"]
group_totals = monthly.groupby("inverter_group").agg(
    weighted_pr=("weighted_pr", "sum"),
    daytime_rows=("daytime_rows", "sum"),
)
group_totals["weighted_mean_daytime_pr"] = (
    group_totals["weighted_pr"] / group_totals["daytime_rows"]
)
print("Weighted mean daytime PR by inverter group")
print(group_totals[["daytime_rows", "weighted_mean_daytime_pr"]].to_string())

# Existing compact output tables do not retain paired module-temperature and PR values.
temperature_sample = TABLES / "module_temperature_pr_sample.csv"
if temperature_sample.exists():
    temperature_pr = pd.read_csv(temperature_sample)
    correlation = temperature_pr["module_temperature_c"].corr(
        temperature_pr["performance_ratio"]
    )
    print(f"Module-temperature and PR correlation: {correlation:.4f}")
else:
    print(
        "Module-temperature and PR correlation: not calculated. "
        "No paired module_temperature_c and performance_ratio sample is available "
        "in output/tables/ or output/sql_results/."
    )


# %% [markdown]
# ## 5. Conclusion and Limitations
# These compact outputs support descriptive checks of hourly and monthly patterns.
# The fault scenarios are injected into simulated data, so results check the analysis
# workflow and do not establish real-world causes or equipment behavior.

# %%
flagged = pd.read_csv(TABLES / "flagged_blocks_by_severity.csv")
print("Flagged three-hour blocks by severity")
print(flagged.to_string(index=False))
print(
    "Conclusion: the saved summaries and charts describe patterns in the modeled "
    "dataset only. Faults are injected scenarios, nighttime PR is undefined, and "
    "the compact inputs do not support a module-temperature correlation."
)
