# Week 20 — Pipeline Integration (Both Paths)

**Phase 5 — Predictive / Alt Track &nbsp;|&nbsp; Milestone 5**

---

## This Week's Focus

Integrate all outputs into a clean, runnable pipeline so the project is ready to hand off to Phase 6.

**Topics:**

- Where modeling/advanced analysis sits in the project flow
- Inputs → transformation → model/analysis → output
- Save model results or prediction tables predictably
- Keep notebooks and scripts aligned
- Document assumptions and limits of the model or analysis
- `requirements.txt` and reproducibility checklist

---

## Resources

**Path A Primary:** [Data Engineering Zoomcamp](https://dezoomcamp.streamlit.app) — deployment/project demo sections

**Path B Primary:** [Data Engineering Zoomcamp](https://dezoomcamp.streamlit.app) — project demo sections

**Optional (both):** [Modern Data Engineering Playbook](https://thoughtworks.com/insights/blog/data-engineering/data-engineering-playbook)

---

## Task

Integrate all analysis or predictive outputs into the broader project flow:

1. Refactor the repo so scripts run in order with no manual steps
2. Perform a documentation pass across all notebooks and scripts
3. Update `requirements.txt`

---

## Deliverable

Connected analytics pipeline with reusable outputs.

**Milestone 5 — Public Repository / Predictive Component** — submit this week.

**Estimated time:** 4–5 hours

## Learner Support

### Starter Script / Template

Use a simple run-order outline for either path:

```md
## Project Flow
1. `python scripts/ingest.py`
2. `python scripts/transform.py`
3. `python <analysis_or_model_script>.py` or run `<notebook_name>.ipynb`
4. Save outputs to `/output` or `/data/processed`
```

Path A output checklist:

```md
- Saved model results or predictions
- Metrics documented
- Assumptions and limitations noted
```

Path B output checklist:

```md
- Segmentation outputs saved
- KPI definitions documented
- Stakeholder brief included
```

### How To Adapt This To Your Project

- Make the sequence match the real repo, not the ideal repo.
- Save outputs in predictable locations.
- Align scripts, notebooks, and README instructions so they tell the same story.

### Definition of Done

- The project has a clean runnable flow.
- Path-specific outputs are integrated into the broader pipeline.
- `requirements.txt` is updated.
- The repo now looks professional enough for Milestone 5 review.

### Common Mistakes

- Leaving results trapped in notebook cells with no saved outputs.
- Forgetting to document path-specific assumptions or limitations.
- Updating files but not the README run instructions.
- Treating integration as only a code task instead of a communication task too.

### If You’re Stuck After 2 Hours

- Write the real execution order on paper first, then make the repo match it.
- Save one stable output file before polishing everything else.
- Ask a peer to read your README and tell you where they would get confused.
