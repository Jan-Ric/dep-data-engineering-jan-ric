# Week 17 — Regression Modeling (Path A) / Advanced Segmentation (Path B)

**Phase 5 — Predictive / Alt Track &nbsp;|&nbsp; Milestone 5**

> ⚡ Follow the section for your chosen path.

---

## Path A — Regression Modeling

### This Week's Focus

Build a baseline regression model if your project has a numeric outcome worth predicting.

**Topics:**

- Regression problem setup: target and features
- Train/test split concept
- Fit a simple linear regression model
- Evaluate using RMSE and R²
- Read coefficients at a basic level
- Recognize underfitting/overfitting intuitively
- Use regression only if it supports the project question

**Resources:**

**Primary:** [Regression Analysis](https://sta210-s22.github.io/website) — targeted sections

**Optional:** [Data Science for Beginners — Microsoft](https://github.com/microsoft/Data-Science-For-Beginners)

**Task:** Build a simple regression baseline if the project has a numeric outcome worth predicting. Otherwise create a forecast-style baseline with justification.

**Deliverable:** Baseline regression notebook section + evaluation metrics.

---

## Path B — Advanced Segmentation & Cohort Analysis

### Focus

Segment your data by 2–3 dimensions and build comparison views.

**Topics:**

- Segmenting data by 2–3 dimensions
- Comparison views showing differences between groups
- Cohort thinking and time-based grouping
- Visual storytelling across segments
- Drawing careful conclusions from group differences

**Resources:**

**Primary:** [StatQuest](https://youtube.com/@statquest)

**Optional:** [OpenIntro Statistics](https://openintro.org/book/os)

**Task:** Segment project data by 2–3 dimensions and build comparison views showing meaningful differences between groups.

**Deliverable:** Segmentation analysis notebook section.

---

**Estimated time:** 4–5 hours

## Learner Support

### Starter Script / Template

**Path A — Regression baseline**

```md
## Baseline Regression
- Target column: <your_target_column>
- Feature columns: <feature_1>, <feature_2>, <feature_3>
- Train/test split: <your_split_choice>
- Metrics to report: RMSE, R^2
- Plain-language summary: <what the baseline tells you>
```

**Path B — Segmentation analysis**

```md
## Segmentation Plan
| Segment Dimension | Why It Matters | Comparison Metric |
|------------------|----------------|-------------------|
| <segment_1> | <reason> | <metric> |
| <segment_2> | <reason> | <metric> |
```

### How To Adapt This To Your Project

- Choose Path A only if predicting a numeric outcome supports the original question.
- Choose Path B if group comparison and descriptive insights are a better fit.
- Keep the baseline simple enough to explain clearly.

### Definition of Done

- You completed the section for the correct path.
- Path A names a target, features, and evaluation metrics.
- Path B compares meaningful segments tied to the project question.
- A reviewer can see why this week’s work moves you toward Milestone 5.

### Common Mistakes

- Forcing regression when the project is not truly predictive.
- Using features that leak the answer.
- Creating segments that do not matter to the audience.
- Reporting results without explaining what they mean.

### If You’re Stuck After 2 Hours

- Re-read your Week 1 question and ask whether it needs prediction or comparison.
- Start with a tiny baseline instead of an ambitious model.
- If Path B fits better, switch early instead of wrestling the wrong method.
