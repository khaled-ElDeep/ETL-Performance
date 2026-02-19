
## 1. Data Model (Gold Layer)
**Grain:** One row per `company_id` per `date`.

| Column | Type | Description |
| :--- | :--- | :--- |
| date | DATE | Snapshot date (Primary Key Part 1) |
| company_id | INT | Unique Identifier (Primary Key Part 2) |
| company_name | VARCHAR | From CRM |
| active_users | INT | Daily unique users from API |
| rolling_7d_au | FLOAT | 7-day moving average of active users |
| is_churn_risk | BOOLEAN | Logic: `rolling_7d_au == 0` |

---

## 2. SQL Transformation (Incremental)
```sql
WITH daily_metrics AS (
    SELECT 
        company_id, 
        date, 
        SUM(COALESCE(events, 0)) AS total_events,
        AVG(active_users) OVER (
            PARTITION BY company_id 
            ORDER BY date 
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS rolling_7d_users
    FROM stg_usage
    WHERE date >= DATEADD(day, -2, GETDATE()) -- Incremental Filter
)
SELECT 
    m.*, 
    c.name, 
    CASE WHEN m.rolling_7d_users = 0 THEN 1 ELSE 0 END AS is_churn_risk
FROM daily_metrics m
LEFT JOIN stg_crm c ON m.company_id = c.company_id;