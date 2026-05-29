# Week 22 — Dashboard Build & GitHub Pages Setup

**Phase 6 — Packaging & Deployment &nbsp;|&nbsp; Milestone 6**

---

## This Week's Focus

Build the dashboard and configure deployment to GitHub Pages.

**Topics:**

- Plotly/HTML/report generation basics
- Static vs interactive output tradeoffs
- Connect processed data to charts
- Consistent labels, filters, and color usage
- Export HTML or app output
- Validate story matches README and notebook
- GitHub Pages deployment setup

---

## Resources

**Primary:** [Data Engineering Zoomcamp — deployment sections](https://dezoomcamp.streamlit.app)

**Primary:** [GitHub Pages Official Docs](https://pages.github.com) — ⚡ primary deployment reference

**Optional:** [AlexTheAnalyst — Create a Portfolio Website](https://youtube.com) — search "create portfolio website alextheanalyst" — portfolio framing only

---

## Task

1. Build the dashboard/report and generate a shareable output file
2. Set up GitHub Pages in repo settings
3. Verify the deployment target is configured correctly

---

## Deliverable

Working dashboard/report artifact + deployment target configured.

**Estimated time:** 5 hours

## Learner Support

### Starter Script / Template

Use a small output checklist while building:

```md
- Input data: `/data/processed/<your_processed_file>.csv`
- Output artifact: `dashboard/index.html` or `/output/<your_report_file>.html`
- Main sections included: overview, trends, segmentation, insights
- Deployment target: GitHub Pages
```

If you are exporting HTML, keep the output path predictable:

```python
output_file = "dashboard/index.html"
```

### How To Adapt This To Your Project

- Build the simplest version that already tells the story well.
- Save the artifact in a location your deployment setup can use consistently.
- Make sure dashboard wording matches the README and notebook language.

### Definition of Done

- A dashboard or report artifact is generated locally.
- The deployment target is configured for GitHub Pages.
- The output file path is clear and repeatable.
- The built artifact reflects the KPIs and charts planned last week.

### Common Mistakes

- Saving the output to an inconsistent or hidden path.
- Building visuals that do not match the processed dataset.
- Setting up Pages without verifying what file actually gets published.
- Waiting until the end to test whether the artifact renders correctly.

### If You’re Stuck After 2 Hours

- Export a single-page HTML first, then improve styling later.
- Confirm where your deployment expects `index.html`.
- Open the local output in a browser and fix obvious layout or data issues before publishing.
