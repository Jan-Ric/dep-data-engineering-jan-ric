# Week 13 — Descriptive Statistics for Project Understanding

**Phase 4 — Analysis & Insights &nbsp;|&nbsp; Milestone 4**

---

## This Week's Focus

Use statistics to understand the shape and character of your data before visualizing it.

**Topics:**

- Mean, median, mode
- Min, max, percentiles
- Variance and standard deviation
- Distribution shape and skew
- Outlier identification basics
- Which statistic fits which data type

---

## Resources

**Primary:** [StatQuest — Statistics Fundamentals](https://youtube.com/@statquest)

**Optional:** [OpenIntro Statistics](https://openintro.org/book/os) — selected sections

---

## Task

Generate descriptive statistics for the key measures in your project and explain in plain language what they say about the data.

---

## Deliverable

Summary-statistics section in notebook with markdown interpretation.

**Estimated time:** 4–5 hours

## Learner Support

### Starter Script / Template

Use a notebook section outline like this:

```md
## Summary Statistics

### Key Measure 1: <your_metric_column>
- Mean:
- Median:
- Min / Max:
- Possible interpretation:

### Key Measure 2: <your_second_metric>
- Mean:
- Median:
- Min / Max:
- Possible interpretation:
```

Optional pandas starter:

```python
df[["<metric_1>", "<metric_2>"]].describe()
```

### How To Adapt This To Your Project

- Focus on measures that connect directly to the project question.
- Interpret each statistic in plain language, not just technical language.
- If a statistic is not useful for your data type, skip it and explain a better one.

### Definition of Done

- Your notebook has a summary-statistics section.
- The statistics cover the most important project measures.
- Each set of numbers has a short written interpretation.
- The section helps prepare you for better charts in Week 14.

### Common Mistakes

- Dumping `describe()` output without explanation.
- Reporting too many statistics that do not matter.
- Ignoring outliers or skew when they are obvious.
- Choosing columns that do not support the problem statement.

### If You’re Stuck After 2 Hours

- Start with one numeric column and one grouping variable.
- Write what surprised you before worrying about perfect statistical language.
- Compare mean and median to see whether the distribution may be skewed.
