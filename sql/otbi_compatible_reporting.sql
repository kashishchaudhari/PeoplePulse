-- Portable demonstration SQL, NOT Oracle OTBI / BI Publisher code.
-- To implement in Oracle HCM, use approved subject areas and authorized data models.
SELECT Department, COUNT(*) AS headcount,
       SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS attrition_count,
       ROUND(100.0 * SUM(CASE WHEN Attrition='Yes' THEN 1 ELSE 0 END)/COUNT(*),1) AS attrition_pct
FROM employees GROUP BY Department ORDER BY attrition_pct DESC;

SELECT Department, JobRole, COUNT(*) AS active_and_historical_records
FROM employees GROUP BY Department, JobRole ORDER BY Department, JobRole;
