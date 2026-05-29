# Week 4 — Python Foundations & First Data Pull

**Phase 1 — Foundations &nbsp;|&nbsp; Milestone 2 (first pull)**

---

## This Week's Focus

Learn just enough Python to pull your first dataset and save it locally.

**Topics:**

- Variables, data types, conditionals, loops
- Functions and reusability
- Lists and dictionaries
- Reading/writing files in Python
- Installing packages and importing modules
- HTTP request basics or file loading basics
- Save raw data locally as CSV or JSON

---

## Resources

**Primary:** [Python Official Getting Started Guide](https://python.org/about/gettingstarted)

**Optional:** [Learnpython.org](https://learnpython.org) — interactive exercises for beginners

---

## Task

Build `scripts/ingest.py` that:

1. Pulls or loads the first raw dataset
2. Saves it into `/data/raw` with a clear, descriptive filename

---

## Deliverable

`scripts/ingest.py` + first raw data file committed to `/data/raw`.

**Milestone 2 — First Data Pull** — submit this week.

**Estimated time:** 5 hours

## Learner Support

### Starter Script / Template

Start with a small `scripts/ingest.py` skeleton like this:

```python
from pathlib import Path

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

def main():
    source_name = "<your_source_name>"
    output_file = RAW_DIR / "<your_file_name>.csv"

    # Replace this block with your actual load or request logic
    raw_text = "<raw content goes here>"

    output_file.write_text(raw_text, encoding="utf-8")
    print(f"Saved raw data for {source_name} to {output_file}")

if __name__ == "__main__":
    main()
```

### How To Adapt This To Your Project

- Replace the placeholder load logic with either an API call, file read, or manual file-save flow.
- Use a descriptive filename that makes sense when you collect future raw pulls.
- Keep the script focused on landing raw data only. Cleaning comes later.

### Sample AI Prompts

- "Help me turn this ingestion idea into a simple `scripts/ingest.py` flow that only saves raw data."
- "I am getting this Python error: `<paste error>`. Explain the likely cause and the smallest fix."
- "Review this script and tell me whether it mixes raw ingestion with cleaning or transformation."

### Definition of Done

- `scripts/ingest.py` exists and runs.
- A raw file is saved into `/data/raw`.
- The filename is clear enough that another person can recognize the source.
- Your repo now has both the script and one real raw data sample.

### Common Mistakes

- Doing cleaning steps inside the ingestion script.
- Saving the file outside `/data/raw`.
- Using a vague filename like `data.csv`.
- Writing code that only works once and cannot be repeated.

### If You’re Stuck After 2 Hours

- First prove you can save any file into `/data/raw`, then connect the real source.
- Print intermediate values so you can see whether the script reached the save step.
- If the source is difficult, document the blocker and ask whether a manual raw save is acceptable for now.
