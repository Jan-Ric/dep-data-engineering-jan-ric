# Week 6 — Alternate Ingestion Paths (⚡ 3-Path Branching)

**Phase 2 — Data Collection &nbsp;|&nbsp; Milestone 2**

---

## This Week's Focus

Complete your ingestion method. Choose the path that fits your data source.

**Topics:**

- HTML structure, BeautifulSoup basics
- Extracting tables, links, and text
- Respect `robots.txt` / responsible scraping
- Cleaning strings during extraction
- When to use scraping vs manual download vs APIs
- Manual path: timestamped filenames + source URL log
- Timestamping raw files for reproducibility

---

## Resources

**Primary:** [Beautiful Soup Documentation](https://crummy.com/software/BeautifulSoup/bs4/doc)

**Optional:** [Real Python — Practical Intro to Web Scraping](https://realpython.com/python-web-scraping-practical-introduction)

---

## Task

Choose your ingestion path and complete it:

- **Path A — API:** Harden `ingest.py` with error handling and retries
- **Path B — Scraping:** Build a scraper that lands data in `/data/raw/`
- **Path C — Manual download:** Document timestamped raw save + source log

All three paths must produce the same output: a raw file in `/data/raw/` with a documented source URL and date.

---

## Deliverable

Alternative ingestion method documented and working.

**Milestone 2 — Data Ingestion Script** — submit this week.

**Estimated time:** 4–5 hours

## Learner Support

### Starter Script / Template

Pick the path that matches your source:

**Path A — API**

```python
# Add retries, pagination, or looping around your Week 5 request logic
```

**Path B — Scraping**

```python
from pathlib import Path
import requests
from bs4 import BeautifulSoup

html = requests.get("<your_page_url>", timeout=30).text
soup = BeautifulSoup(html, "html.parser")

# Replace with the table, links, or text you need
records = []

Path("data/raw").mkdir(parents=True, exist_ok=True)
Path("data/raw/<your_source_name>_raw.html").write_text(html, encoding="utf-8")
```

**Path C — Manual Download**

```md
Saved file: /data/raw/<your_source_name>_<YYYY-MM-DD>.csv
Source URL: <your_source_url>
Downloaded on: <download_date>
Notes: <why manual download was necessary>
```

### How To Adapt This To Your Project

- Choose the simplest path that reliably gets the data into `/data/raw`.
- Record the exact source URL and date even if the process is manual.
- Keep your output naming consistent so future pulls are easy to compare.

### Definition of Done

- One ingestion path is complete and documented.
- A real raw file exists in `/data/raw`.
- The source URL and access date are recorded somewhere in the repo.
- Your process is repeatable by you or a reviewer.

### Common Mistakes

- Mixing scraping and heavy cleaning into one opaque script.
- Forgetting to log the source URL for manual downloads.
- Saving files with no timestamp or no source clue in the name.
- Choosing scraping when a clean download or API already exists.

### If You’re Stuck After 2 Hours

- Switch to the simplest valid path instead of forcing the hardest one.
- Save one successful raw sample first, then improve the process.
- Share the source URL and describe which step is failing: access, extraction, or saving.
