# Week 8 — SQL Fundamentals for Data Projects

**Phase 3 — Data Processing &nbsp;|&nbsp; Milestone 2/3 bridge**

---

## This Week's Focus

Use SQL to query your dataset and answer real business questions.

**Topics:**

- SELECT, FROM, WHERE, ORDER BY, LIMIT
- COUNT, SUM, AVG, MIN, MAX
- GROUP BY and HAVING
- Aliases and calculated columns
- INNER JOIN and LEFT JOIN
- Basic date filters and null checks
- Turn business questions into SQL questions

---

## Resources

**Primary:** [SQLBolt](https://sqlbolt.com) — interactive SQL practice

**Optional:** [W3Schools SQL Tutorial](https://w3schools.com/sql) — reference and examples

---

## Task

Load the working dataset into a local database and write at least 3 SQL queries that answer business questions from your problem statement.

---

## Deliverable

SQL script or notebook section with 3 answered business questions.

**Estimated time:** 5 hours

## Learner Support

### Starter Script / Template

Translate each project question into a SQL query frame:

```sql
-- Question 1: How does <your_kpi_name> change by <time_or_group>?
SELECT
    <time_or_group>,
    AVG(<your_metric_column>) AS avg_metric
FROM <your_table_name>
GROUP BY <time_or_group>
ORDER BY <time_or_group>;

-- Question 2: Which <category> has the highest <metric>?
SELECT
    <category_column>,
    SUM(<metric_column>) AS total_metric
FROM <your_table_name>
GROUP BY <category_column>
ORDER BY total_metric DESC;
```

### How To Adapt This To Your Project

- Write the business question in plain language before writing SQL.
- Use columns that already exist in your raw or working dataset.
- Keep the first three queries simple and directly tied to the problem statement.

### Definition of Done

- You have at least 3 SQL queries.
- Each query answers a real project question, not a random practice question.
- The results are understandable enough to discuss in plain language.
- Your SQL can be re-run by a reviewer.

### Common Mistakes

- Writing queries that explore the data but do not answer the project question.
- Using `SELECT *` instead of choosing useful columns.
- Forgetting `GROUP BY` when aggregating.
- Writing SQL without any note explaining what question it answers.

### If You’re Stuck After 2 Hours

- Start with one question that begins with "how many," "which group," or "how has it changed over time."
- Use a tiny sample table first if the full dataset feels overwhelming.
- Post one business question and your attempted query so others can help debug the logic.
