# Week 9 — Pandas Fundamentals: Cleaning & Shaping Data

**Phase 3 — Data Processing &nbsp;|&nbsp; Milestone 3**

---

## This Week's Focus

Load your raw data into pandas and produce the first cleaned version.

**Topics:**

- Read CSV/Excel/JSON into pandas
- DataFrame structure: rows, columns, dtypes, index
- Selecting columns and filtering rows
- Basic profiling: `head()`, `info()`, `describe()`, `value_counts()`
- Rename columns and standardize names
- Save processed outputs

---

## Resources

**Primary:** [Python for Data Science](https://cognitiveclass.ai/courses/python-for-data-science) — cognitiveclass.ai

**Optional:** [Python Official Getting Started Guide](https://python.org/about/gettingstarted) — review

---

## Task

Create `scripts/transform.py` or notebook cells that:

1. Load the raw data
2. Inspect and profile it
3. Produce the first cleaned version in `/data/processed/`

---

## Deliverable

First cleaned dataset version committed to `/data/processed/`.

**Estimated time:** 5 hours

## Learner Support

### Starter Script / Template

Start `scripts/transform.py` with a basic load-profile-save flow:

```python
from pathlib import Path
import pandas as pd

RAW_FILE = Path("data/raw/<your_raw_file>.csv")
OUTPUT_FILE = Path("data/processed/<your_processed_file>.csv")

def main():
    df = pd.read_csv(RAW_FILE)
    print(df.head())
    print(df.info())

    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved cleaned dataset to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
```

### How To Adapt This To Your Project

- Load the real raw file from `/data/raw`.
- Start with simple column cleanup and basic profiling before deeper cleaning.
- Save the first processed version even if it is not perfect yet.

### Definition of Done

- `scripts/transform.py` or equivalent notebook flow exists.
- The raw file loads successfully.
- You inspected the structure with basic profiling.
- A first cleaned file is saved in `/data/processed`.

### Common Mistakes

- Jumping into complex cleaning before checking `info()` and `head()`.
- Overwriting the raw file instead of writing to `/data/processed`.
- Renaming columns inconsistently.
- Treating the first cleaned version as the final version.

### If You’re Stuck After 2 Hours

- Confirm the file path and file format first.
- Print the column names before writing any cleaning logic.
- Get one row-to-row save working before adding more transformations.
