# Week 18 — Classification Modeling (Path A) / KPI Development (Path B)

**Phase 5 — Predictive / Alt Track &nbsp;|&nbsp; Milestone 5**

> ⚡ Follow the section for your chosen path.

---

## Path A — Classification Modeling

### This Week's Focus

Build a classification model if your project has a meaningful yes/no outcome.

**Topics:**

- Binary target definition
- Class labels and imbalance awareness
- Logistic regression basics
- Confusion matrix
- Accuracy vs precision vs recall vs F1 (intro level)
- Threshold thinking and business tradeoffs
- Decide whether classification is appropriate

**Resources:**

**Primary:** [Data Science for Beginners — Microsoft](https://github.com/microsoft/Data-Science-For-Beginners)

**Optional:** [Learning from Data](https://work.caltech.edu/telecourse) — small excerpts

**Task:** If the project supports a yes/no outcome, build a first classification model and explain which metric matters most.

**Deliverable:** Classification baseline + short metric interpretation.

---

## Path B — KPI Development & Metric Framework

### Focus

Define 3–5 KPIs that directly measure your problem statement.

**Topics:**

- Define 3–5 KPIs for the project
- Explain how each is calculated
- Show trend over time
- KPI vs vanity metric distinction
- Aligning KPIs to the original problem statement

**Resources:**

**Primary:** [Presentation and Storytelling](https://youtube.com) — search "presentation and storytelling data"

**Optional:** [Real World Data Science Use Cases](https://realworlddatascience.net)

**Task:** Define 3–5 KPIs for the project, explain how each is calculated, and show trend over time.

**Deliverable:** KPI notebook section + metric definitions.

---

**Estimated time:** 4–5 hours

## Learner Support

### Starter Script / Template

**Path A — Classification baseline**

```md
## Baseline Classification
- Target column: <your_binary_target>
- Positive class: <what counts as yes>
- Features: <feature_1>, <feature_2>, <feature_3>
- Metrics to report: accuracy, precision, recall, F1
- Most important metric for this project: <chosen_metric> because <reason>
```

**Path B — KPI framework**

```md
| KPI | Definition | Formula or Logic | Why It Matters |
|-----|------------|------------------|----------------|
| <your_kpi_name> | <plain definition> | <how to calculate> | <reason> |
| <your_kpi_name_2> | <plain definition> | <how to calculate> | <reason> |
```

### How To Adapt This To Your Project

- Path A should only be used if a meaningful yes/no target exists.
- Path B KPIs should trace directly back to the Week 1 problem statement.
- Keep definitions in plain language before adding technical detail.

### Definition of Done

- Path A includes a binary target and metric interpretation.
- Path B includes 3–5 KPIs with clear calculation logic.
- The work is understandable to someone outside your head.
- Your outputs can feed into later storytelling or deployment.

### Common Mistakes

- Turning a weak target into a forced classification problem.
- Reporting accuracy alone when class imbalance matters.
- Listing vanity metrics that do not support decision-making.
- Writing KPI names without defining how they are calculated.

### If You’re Stuck After 2 Hours

- For Path A, ask which mistake matters more: false positives or false negatives.
- For Path B, start with one KPI per audience decision.
- If the target or KPI still feels fuzzy, rewrite it in one plain sentence first.
