# Week 7 — Storage Design & Data Modeling

**Phase 3 — Data Processing &nbsp;|&nbsp; Milestone 3 prep**

---

## This Week's Focus

Before cleaning anything, design how your data should be structured.

**Topics:**

- Files vs databases vs warehouse-style tables
- Entities, records, measures, dimensions
- Fact vs dimension tables (light intro)
- Primary keys and foreign keys
- Grain of a table
- Naming conventions and schema readability
- Choose storage approach for raw and processed layers

---

## Resources

**Primary:** [Fundamentals of Data Engineering](https://redpanda.com/guides/fundamentals-of-data-engineering) — modeling/storage sections

**Optional:** [Database Technology Overview](https://halvorsen.blog/documents/database/database.php)

---

## Task

Write a simple schema plan for the processed dataset:

- What are the key tables or files?
- What is the grain (one row = one what)?
- What are the identifiers (primary keys)?
- What are the expected columns?

---

## Deliverable

Schema draft in the README or a separate design note.

**Estimated time:** 4–5 hours

## Learner Support

### Starter Script / Template

Use a short schema note like this:

```md
## Processed Data Plan

### Main Table or File
- Name: <processed_table_name>
- Grain: one row = one <entity/event/time period>
- Primary key: <your_primary_key>

### Important Columns
| Column | Meaning | Expected Type |
|--------|---------|---------------|
| <column_1> | <meaning> | <type> |
| <column_2> | <meaning> | <type> |

### Related Tables or Files
- <table_name>: joins on <join_key>
```

### How To Adapt This To Your Project

- Define the grain before listing columns.
- If you have more than one file, explain how they relate.
- Keep names readable and consistent with the data you actually have.

### Definition of Done

- Your schema note names the main processed file or table.
- One row clearly means one specific thing.
- Key identifiers are named.
- Expected columns are listed well enough to guide Week 9 and Week 10.

### Common Mistakes

- Describing the data source without defining the processed output.
- Mixing multiple grains into one table.
- Using vague IDs that do not uniquely identify a row.
- Listing columns without explaining what they represent.

### If You’re Stuck After 2 Hours

- Start with one main table first, even if your project may later grow to more.
- Write the grain as a sentence beginning with "one row =".
- Compare your schema note against the Week 1 problem statement and remove anything that does not support it.
