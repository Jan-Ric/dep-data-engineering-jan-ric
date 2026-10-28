# Cleaning and Validation Log

| Issue | Decision | Reason | Where in code |
| --- | --- | --- | --- |
| API timestamps and source column names | Rename to project names, parse `date_time`, sort chronologically | Stable, typed hourly input for later calculations | `scripts/transform.py`, `load_raw_data` |
| Missing weather inputs | Do not impute; validation fails with an assertion if required fields contain nulls | No defensible fallback measurement is defined | `scripts/transform.py`, `validate_missing_values` |
| Missing calculated fields | Validation fails with an assertion if required calculated values contain nulls | Prevent incomplete inverter-hour records | `scripts/transform.py`, `validate_missing_values` |
| Zero irradiance at night | Keep `PERFORMANCE_RATIO` null because the denominator is zero; exclude these rows from PR analysis, not treat them as zero | Zero would misrepresent an undefined ratio as a measurement | `scripts/transform.py`, PR calculation and validation |
| Daytime PR is missing | Fail validation if any row with irradiance above zero has null PR | Daylight KPI must be computable | `scripts/transform.py`, `validate_missing_values` |
| Nighttime PR is non-null | Fail validation if zero-irradiance rows have a PR value | Enforce the division-by-zero decision | `scripts/transform.py`, `validate_missing_values` |
| Input coverage and expanded data size | Require 8,760 weather hours and exactly `830 * 8,760 = 7,270,800` inverter-hour rows | Catch incomplete API pulls and bad cross joins | `scripts/transform.py`, `validate_missing_values` |
| Duplicate inverter-hour key | Fail if (`inverter_id`, `date_time`) is duplicated | Enforce the dataset grain and composite key | `scripts/transform.py`, `main` |
| AC power range | Require 0 to 60 kW inclusive | Match nonnegative output and the rated AC cap | `scripts/transform.py`, `validate_missing_values` |
| Invalid fault offset | Allow zero and only offsets defined by `FAULT_WINDOWS` | Keep fault injections constrained to declared scenarios | `scripts/transform.py`, `validate_missing_values` |
| Output schema drift | Require exact column names and order for weather, computation, and query outputs | Preserve downstream CSV contracts | `scripts/transform.py`, schema constants and validation |
| Raw irradiance and ambient temperature limits | Fail if irradiance is negative or ambient temperature is outside 10–50°C | Basic physical range checks for this project | `scripts/transform.py`, `main` |
| Daytime PR range | Require PR between 0 and 1.5 | Basic guard against invalid calculation results | `scripts/transform.py`, `main` |
| Fleet-relative PR gap and detector | For each timestamp, compute `pr_gap = median valid PR across all inverters - that inverter's PR`. Flag rolling three-hour windows only when each hour has irradiance above 200 W/m², valid PR, and mean `pr_gap` at least 0.05; retain Watch [0.05, 0.10), Alert [0.10, 0.20], Critical > 0.20. | A common peer-relative definition avoids confusing detector gaps with pooled shortfall from PR 1.0; overlapping consecutive windows are counted independently. | `sql/02_pr_gap_by_month_hour.sql`, `sql/03_flagged_3h_blocks.sql` |

## Detection Result

The regenerated validation detects all 12 designed windows: Watch 4/4, Alert 4/4, and Critical 4/4, with all target tiers matching. The three hard windows are not detected as expected: two mean `pr_gap` values are below 0.05, while the third is only two hours long and fails the three-hour rule. The false-alarm check reports zero blocks on non-faulted inverters. That zero is expected because all non-faulted inverters share the same weather and simulated PR; it confirms the rule does not misfire on identical simulated peers and says nothing about noisy real data.

The raw JSON files are never removed or rewritten by the transformation. Ingestion only writes the dedicated `open_meteo_raw.json` output after validating the API payload.
