# Week 14 — EDA & Visualization

**Phase 4 — Analysis & Insights &nbsp;|&nbsp; Milestone 4**

---

## This Week's Focus

Build charts that answer your project question — clear, labeled, and purposeful.

**Topics:**

- Choosing chart types: line, bar, scatter, histogram
- Matplotlib/Plotly basics
- Labeling titles, axes, and legends
- Comparing categories and trends over time
- Detecting anomalies and seasonality visually
- Build charts that answer the project question

---

## Resources

**Primary:** [Data Visualization & Business Intelligence playlist](https://youtube.com) — search "data visualization business intelligence playlist"

**Optional:** [TechTFQ](https://youtube.com/@TechTFQ) — targeted plotting tutorials

---

## Task

Create at least 3 clear charts tied to the project question and save them into `/output/figures/` or as notebook outputs.

---

## Deliverable

Three or more charts with readable titles and labels.

**Estimated time:** 5 hours

## Learner Support

### Starter Script / Template

Plan each chart before building it:

```md
| Chart | Question It Answers | Chart Type | Main Columns |
|------|----------------------|------------|--------------|
| 1 | <question_1> | <line/bar/scatter> | <x>, <y> |
| 2 | <question_2> | <line/bar/scatter> | <x>, <y> |
| 3 | <question_3> | <line/bar/scatter> | <x>, <y> |
```

Minimal plotting starter:

```python
import matplotlib.pyplot as plt

df.plot(x="<x_column>", y="<y_column>", kind="line", title="<chart title>")
plt.xlabel("<x label>")
plt.ylabel("<y label>")
plt.tight_layout()
```

### How To Adapt This To Your Project

- Choose chart types that match the question, not just the nicest-looking option.
- Make sure titles say what the viewer is seeing.
- Use labels a non-technical audience can understand.

### Definition of Done

- You have at least 3 charts.
- Every chart ties back to the project question.
- Titles, axes, and legends are readable.
- The charts are saved in the notebook or `/output/figures/`.

### Common Mistakes

- Making charts before deciding what question they answer.
- Using unclear titles like "Chart 1" or "Distribution".
- Putting too many series on one chart.
- Choosing decorative colors that reduce readability.

### If You’re Stuck After 2 Hours

- Start with one time trend, one category comparison, and one distribution view.
- Ask whether each chart would still make sense without you explaining it live.
- Rebuild messy charts using fewer variables.
