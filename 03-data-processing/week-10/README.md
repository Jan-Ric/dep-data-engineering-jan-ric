# Week 10 — Advanced Transformation & Joins

**Phase 3 — Data Processing &nbsp;|&nbsp; Milestone 3**

---

## This Week's Focus

Combine, reshape, and enrich your data into one coherent analysis-ready table.

**Topics:**

- Handling missing values: fill, drop, flag
- Removing duplicates
- Type conversion: numeric, date, categorical
- `merge()`, `concat()`, `groupby()`, `agg()`
- Derived columns and feature engineering basics
- Time-based grouping (month, quarter, year)
- Produce one analysis-ready table

---

## Resources

**Primary:** [Data Engineering Zoomcamp](https://dezoomcamp.streamlit.app) — ETL/transformation sections

**Optional:** [Data Engineering Cookbook](https://github.com/andkret/Cookbook) — examples only

---

## Task

Transform multiple raw sources into one coherent processed dataset with a documented cleaning flow.

---

## Deliverable

Processed dataset + transformation logic documented.

**Estimated time:** 5 hours

## Learner Support

### Starter Script / Template

Extend your transform flow with explicit cleaning steps:

```python
df = df.drop_duplicates()
df["<date_column>"] = pd.to_datetime(df["<date_column>"], errors="coerce")
df["<numeric_column>"] = pd.to_numeric(df["<numeric_column>"], errors="coerce")
df["<category_column>"] = df["<category_column>"].fillna("unknown")

# Example join
other_df = pd.read_csv("data/raw/<other_file>.csv")
merged_df = df.merge(other_df, on="<join_key>", how="left")
```

### How To Adapt This To Your Project

- Only keep transformation steps that improve analysis-readiness for your question.
- If you join multiple files, explain why the join key is valid.
- Keep derived columns readable and easy to trace back to the source fields.

### Definition of Done

- Missing values, duplicates, and types are handled intentionally.
- If there are multiple sources, they are combined into one coherent processed output.
- The transformation logic is documented well enough to repeat.
- The saved processed file is closer to analysis-ready than last week’s version.

### Common Mistakes

- Filling nulls without explaining why.
- Joining files on a weak or inconsistent key.
- Creating derived columns with unclear names.
- Making many changes without saving an updated processed output.

### If You’re Stuck After 2 Hours

- Clean one issue at a time: duplicates, then types, then joins.
- Compare row counts before and after each major transformation.
- Write comments or markdown notes explaining each cleaning decision as you go.
