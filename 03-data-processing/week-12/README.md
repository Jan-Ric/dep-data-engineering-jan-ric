# Week 12 — Pipeline Structuring & Local Orchestration

**Phase 3 — Data Processing &nbsp;|&nbsp; Milestone 3 complete / Milestone 4 prep**

---

## This Week's Focus

Refactor the repo so any reviewer can understand and run the full pipeline.

**Topics:**

- ETL vs ELT (simple explanation)
- Raw → processed → analysis/output directory structure
- Separate scripts for ingestion and transformation
- Parameterization basics
- Running the pipeline in the correct order
- `requirements.txt` and reproducibility checklist

---

## Resources

**Primary:** [Data Engineering Zoomcamp](https://dezoomcamp.streamlit.app)

**Optional:** [Modern Data Engineering Playbook](https://thoughtworks.com/insights/blog/data-engineering/data-engineering-playbook)

---

## Task

Refactor the repo so a reviewer can:

1. Run `ingest.py` first
2. Run `transform.py` second
3. Run analysis third

Add repo instructions (in README) for running the project end to end.

---

## Deliverable

Clear script flow + repo instructions for running the project.

**Milestone 3 — Clean Dataset** — submit this week.

**Estimated time:** 4–5 hours

## Learner Support

### Starter Script / Template

Document the run order clearly in your README:

```md
## How To Run

1. Install dependencies: `pip install -r requirements.txt`
2. Run ingestion: `python scripts/ingest.py`
3. Run transformation: `python scripts/transform.py`
4. Run analysis: `python <analysis_script_or_notebook_step>`
```

Simple pipeline flow:

```text
/data/raw -> scripts/transform.py -> /data/processed -> analysis output
```

### How To Adapt This To Your Project

- Keep each step in the order a reviewer would actually follow.
- Use the same filenames and commands that exist in the repo.
- If analysis still happens in a notebook, say exactly which notebook and which section to run.

### Definition of Done

- A reviewer can tell how to run the project from raw input to analysis output.
- The repo has a clear script flow.
- `requirements.txt` is present and relevant.
- Your processed dataset and run instructions support Milestone 3 submission.

### Common Mistakes

- Hiding critical steps in your head instead of writing them down.
- Referring to scripts or files that do not exist.
- Mixing setup instructions with analysis commentary.
- Leaving the pipeline order ambiguous.

### If You’re Stuck After 2 Hours

- Pretend a stranger will run the repo tomorrow and write the minimum steps they need.
- Test your own instructions from top to bottom.
- If the flow is messy, write the intended order first, then refactor the files to match it later.
