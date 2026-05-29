# Week 11 — Data Quality, Validation & Reproducibility

**Phase 3 — Data Processing &nbsp;|&nbsp; Milestone 3**

---

## This Week's Focus

Make your cleaning pipeline reliable — the same input should always produce the same output.

**Topics:**

- What counts as a data quality issue
- Nulls, duplicates, invalid categories, impossible values
- Range checks and uniqueness checks
- Lightweight validation rules in code
- Logging assumptions and cleaning decisions
- Re-runability: transform script produces same output every time

---

## Resources

**Primary:** [DE Design Patterns](https://dedp.online)

**Optional:** [Modern Data Engineering Playbook](https://thoughtworks.com/insights/blog/data-engineering/data-engineering-playbook)

---

## Task

Add validation checks to the transformation flow and document every major cleaning decision in the README or notebook markdown.

---

## Deliverable

Validation notes + cleaner, reproducible transform flow.

**Estimated time:** 4–5 hours

## Learner Support

### Starter Script / Template

Add a few lightweight checks near the end of `transform.py`:

```python
assert df["<primary_key>"].isna().sum() == 0, "Primary key has nulls"
assert df["<primary_key>"].nunique() == len(df), "Primary key is not unique"
assert df["<numeric_column>"].min() >= 0, "Unexpected negative value found"

print("Validation checks passed")
```

Use a short cleaning log in your README or notebook:

```md
- Filled missing `<category_column>` with `unknown` because blank values still represent real records.
- Dropped rows missing `<primary_key>` because they cannot be linked reliably.
- Converted `<date_column>` to datetime for time-based analysis.
```

### How To Adapt This To Your Project

- Pick checks that reflect your actual risks: nulls, duplicates, impossible values, bad categories, or broken dates.
- Keep the validation small but meaningful.
- Log why you made each important cleaning decision.

### Definition of Done

- The transform flow includes validation checks.
- Major cleaning decisions are documented.
- Running the transform repeatedly gives the same output from the same input.
- A reviewer can see how you are protecting data quality.

### Common Mistakes

- Adding checks that do not match any real project risk.
- Making cleaning decisions without recording the reasoning.
- Using validation only in notebook cells that are easy to skip.
- Confusing reproducibility with perfection.

### If You’re Stuck After 2 Hours

- Start with three checks only: null key, duplicate key, and invalid numeric range.
- Re-run the script twice and compare the output file manually.
- If a check fails, inspect a few bad rows instead of guessing the cause.
