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
FIGURES = PROJECT_ROOT / "output/figures"
FIGURE_DPI = 140  # dots per inch
AC_CLIP_KW = 60.0  # rated AC power in kilowatts
FAULT_DATES = {
    101: "2025-03-15",
    202: "2025-06-20",
    303: "2025-09-10",
}


# %% [markdown]
# ## 2. Summary Statistics
# Use the saved summary table so this report reads only compact output artifacts.

# %%
def print_summary_statistics(summary_statistics):
    print("Summary statistics and missing-value counts")
    print(summary_statistics.to_string(index=False))


# %% [markdown]
# ## 3. Charts
# Each chart uses saved tables and is exported as a PNG for the written report.

# %%
def create_hourly_chart(hourly):
    figure, axis = plt.subplots(figsize=(9, 5))
    axis.plot(
        hourly["hour"],
        hourly["mean_daytime_pr"],
        marker="o",
        color="#287b72",
    )
    axis.set(
        title="Mean Daytime Performance Ratio by Hour of Day",
        xlabel="Hour of day (local time, h)",
        ylabel="Mean performance ratio (unitless)",
    )
    axis.set_xticks(range(0, 24, 2))
    figure.tight_layout()
    figure.savefig(FIGURES / "pr_by_hour_of_day.png", dpi=FIGURE_DPI)
    plt.close(figure)


# %%
def create_monthly_chart(monthly):
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
        xlabel="Calendar month (YYYY-MM)",
        ylabel="Mean performance ratio (unitless)",
    )
    axis.tick_params(axis="x", rotation=45)
    axis.legend(frameon=False)
    figure.tight_layout()
    figure.savefig(FIGURES / "monthly_mean_pr_by_group.png", dpi=FIGURE_DPI)
    plt.close(figure)


# %%
def create_fault_day_chart(fault_day):
    fault_day["DATE_TIME"] = pd.to_datetime(fault_day["DATE_TIME"])
    figure, axes = plt.subplots(3, 1, figsize=(9, 9), sharex=True, sharey=True)
    for axis, (inverter_id, fault_date) in zip(axes, FAULT_DATES.items()):
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
    axes[-1].set_xlabel("Hour of day (local time, h)")
    figure.suptitle("Performance Ratio on Simulated Fault Days", y=1.01)
    figure.tight_layout()
    figure.savefig(
        FIGURES / "fault_day_pr_101_202_303.png",
        dpi=FIGURE_DPI,
        bbox_inches="tight",
    )
    plt.close(figure)


# %%
def create_irradiance_chart(scatter):
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
        AC_CLIP_KW,
        color="#b44b40",
        linewidth=1.2,
        linestyle="--",
        label=f"{AC_CLIP_KW:g} kW rated AC clip",
    )
    axis.set(
        title="Irradiance and AC Power",
        xlabel="Plane-of-array irradiance (W/m²)",
        ylabel="AC power (kW)",
    )
    axis.legend(frameon=False)
    figure.tight_layout()
    figure.savefig(FIGURES / "irradiance_vs_ac_power.png", dpi=FIGURE_DPI)
    plt.close(figure)


# %% [markdown]
# ## 4. Cautious Inference
# Compare weighted mean daytime PR across faulted and non-faulted inverter-hours.
# A temperature correlation requires paired module-temperature and PR observations.

# %%
def print_cautious_inference(monthly):
    monthly = monthly.copy()
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

    temperature_sample = TABLES / "module_temperature_pr_sample.csv"
    if temperature_sample.exists():
        temperature_pr = pd.read_csv(temperature_sample)
        required_columns = {"module_temperature_c", "performance_ratio"}
        assert required_columns.issubset(temperature_pr.columns), (
            "Temperature sample must include module_temperature_c and performance_ratio"
        )
        correlation = temperature_pr["module_temperature_c"].corr(
            temperature_pr["performance_ratio"]
        )
        print(f"Module-temperature and PR correlation: {correlation:.4f}")
    else:
        print(
            "Module-temperature and PR correlation: unavailable. The retained "
            "compact tables contain no paired temperature and PR observations."
        )


# %% [markdown]
# ## 5. Conclusion and Limitations
# These compact outputs support descriptive checks of hourly and monthly patterns.
# Faults are injected into simulated data, so this checks the detector, not real causes.

# %%
def print_conclusion(flagged):
    print("Flagged three-hour blocks by severity")
    print(flagged.to_string(index=False))
    print(
        "Conclusion: these compact outputs describe the modeled dataset only. "
        "Faults are injected to check the detector, nighttime PR is undefined, "
        "and the available tables do not support a temperature correlation. "
        "No real-world or causal claim is made."
    )


# %%
def main():
    plt.style.use("seaborn-v0_8-whitegrid")
    FIGURES.mkdir(parents=True, exist_ok=True)

    summary_statistics = pd.read_csv(TABLES / "summary_statistics.csv")
    hourly = pd.read_csv(TABLES / "hourly_mean_pr.csv")
    monthly = pd.read_csv(TABLES / "monthly_mean_pr_by_group.csv")
    fault_day = pd.read_csv(TABLES / "fault_day_pr_101_202_303.csv")
    scatter = pd.read_csv(TABLES / "scatter_sample_100k.csv")
    flagged = pd.read_csv(TABLES / "flagged_blocks_by_severity.csv")

    assert len(hourly) > 0, "Hourly PR table must not be empty"
    assert set(FAULT_DATES).issubset(set(fault_day["INVERTER_ID"])), (
        "Fault-day table must include inverters 101, 202, and 303"
    )
    assert len(scatter) == 100_000, "Scatter sample must contain 100,000 rows"

    print_summary_statistics(summary_statistics)
    create_hourly_chart(hourly)
    create_monthly_chart(monthly)
    create_fault_day_chart(fault_day)
    create_irradiance_chart(scatter)
    print_cautious_inference(monthly)
    print_conclusion(flagged)
    print(f"Saved four charts to {FIGURES}")


if __name__ == "__main__":
    main()
