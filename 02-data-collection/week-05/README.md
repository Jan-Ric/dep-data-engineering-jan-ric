# Week 5 — API Fundamentals & Request Handling

**Phase 2 — Data Collection &nbsp;|&nbsp; Milestone 2**

---

## This Week's Focus

Learn how to talk to APIs in Python and pull your actual dataset.

**Topics:**

- HTTP methods (GET)
- Endpoints, query parameters, headers, auth basics
- JSON structure: dicts, lists, nested objects
- Response status codes and error handling
- Pagination, rate limits, retries, timeouts
- Convert JSON response into tabular structure

---

## Resources

**Primary:** [Python Requests Library](https://docs.python-requests.org)

**Optional:** [freeCodeCamp Web Scraping / API tutorial](https://freecodecamp.org/news/tag/web-scraping)

---

## Task

Extend `scripts/ingest.py` to:

1. Handle query parameters and errors
2. Support repeated calls (pagination or looping)
3. Save raw extracts consistently to `/data/raw/`

---

## Deliverable

More robust API ingestion script + sample raw pulls committed.

**Estimated time:** 5 hours

## Learner Support

### Starter Script / Template

Use this API-oriented skeleton and fill in the placeholders:

```python
from pathlib import Path
import requests

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

def fetch_data():
    url = "<your_api_url>"
    params = {"<param_name>": "<param_value>"}
    headers = {"Accept": "application/json"}

    response = requests.get(url, params=params, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()

def main():
    payload = fetch_data()
    output_file = RAW_DIR / "<your_source_name>_raw.json"
    output_file.write_text(str(payload), encoding="utf-8")
    print(f"Saved raw extract to {output_file}")

if __name__ == "__main__":
    main()
```

### How To Adapt This To Your Project

- Put your real endpoint, parameters, and headers into the request block.
- If the API returns many pages, loop through them and combine the results before saving.
- Keep the raw response intact so you can trace back to the source later.

### Definition of Done

- Your script successfully hits the real API.
- It handles bad responses with at least basic error visibility.
- Raw outputs are saved consistently into `/data/raw`.
- You can explain which parameters control the returned data.

### Common Mistakes

- Forgetting `timeout` and basic error handling.
- Saving only a transformed subset instead of the raw extract.
- Hardcoding values without documenting what they mean.
- Ignoring pagination when the source returns partial data.

### If You’re Stuck After 2 Hours

- Test the endpoint in the browser or docs first to confirm it works.
- Print the response status code and a small sample of the payload.
- Start with one page or one date range, then expand once the first request succeeds.
