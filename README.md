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
