# Company Activity Analytics Pipeline

This repository contains the data model, pipeline architecture, and optimization strategy for the New "Company Activity" Dashboard.


## ⚡ Optimization Strategy
To resolve the 3-hour latency issue, we have implemented a three-tier optimization strategy:

1. **Incremental Loading (Highest Impact):** - **Change:** Modified SQL and ADF logic to filter by `WHERE date >= CURRENT_DATE - 2`.
   - **Result:** Reduces data volume processed daily by 95%+, shifting from a full history scan to a delta-refresh.

2. **Clustered Columnstore Indexing:** - **Change:** Applied a Columnstore Index to the `date` and `company_id` columns in the SQL analytics table.
   - **Result:** Compresses data storage and accelerates `GROUP BY` and `SUM` operations for the dashboard queries.

3. **Table Partitioning:** - **Change:** Partitioned the `fact_events` table by `Month`.
   - **Result:** Allows the database engine to "prune" (skip) partitions that aren't needed for the daily run, preventing unnecessary I/O.
  

## ⚡ Risk: Identify 2–3 risks or flaws
1. **Problem:** No `WHERE` clause means the query cost grows linearly every day.  
   **Fix:** Implement an incremental filter to only process new data.

2. **Problem:** `date` is a reserved word in T-SQL/Postgres/Snowflake and can cause pipeline crashes.  
   **Fix:** Wrap the column name in quotes or brackets (e.g., `"date"` or `[date]`).

3. **Problem:** If a company has no events for a day, `SUM` returns `NULL`. This can break downstream visualizations or "Churn Risk" logic that expects a numeric `0`.  
   **Fix:** Use `COALESCE(SUM(events), 0)`.


## ⚡Investigation Steps

1. Check for Duplicates
   I would run a query to check for duplicate `company_id` and `date` keys in the staging table.  
   This often happens if an ADF "Copy Activity" retries after a partial failure without a "Cleanup" script.

2. Timezone Alignment
   Check if the API provides data in UTC while the CRM/Database uses Local Time.  
   A mismatch here shifts events by one day, causing totals to look "wrong."

3. JSON Schema Drift
   Inspect the raw JSON in Blob storage.  
   If the API provider changed the field name (e.g., from `events` to `event_count`), the pipeline might be landing `NULL`s.




## ⚡ Status Update: Company Activity Dashboard Performance

   What’s Changing
   We are moving the "Company Activity" pipeline to an incremental refresh model.  
   Starting tomorrow, the daily job will only process the most recent 48 hours of data.
   
   Benefits
   - Reduces the morning data lag from 3 hours down to under 15 minutes.
   
   Limitations
   - Historical records (older than 2 days) will be "frozen" during the week.  
   - A full historical reconciliation will run every Sunday at 2:00 AM.
   
   Watch Out For
   - If you are auditing data from previous months, please refer to the "Last Synced" timestamp on the dashboard.
