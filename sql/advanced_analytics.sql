-- PeoplePulse advanced SQL, SQLite-compatible, observational fictional HR data.
-- 1) CTE + window functions: department ranking and share of all employee records.
WITH department_counts AS (
  SELECT Department, COUNT(*) AS headcount,
         SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS departures
  FROM employees GROUP BY Department
), ranked AS (
 SELECT Department, headcount, departures,
        ROUND(100.0 * departures / NULLIF(headcount,0),1) AS attrition_pct,
        DENSE_RANK() OVER (ORDER BY headcount DESC) AS headcount_rank,
        ROUND(100.0 * headcount / NULLIF(SUM(headcount) OVER (),0),1) AS share_of_workforce_pct
 FROM department_counts
)
SELECT * FROM ranked ORDER BY headcount_rank, Department;

-- 2) Conditional aggregation with explicit denominators.
SELECT Department,
 COUNT(*) AS employees,
 SUM(CASE WHEN OverTime = 'Yes' THEN 1 ELSE 0 END) AS overtime_employees,
 SUM(CASE WHEN OverTime = 'Yes' AND Attrition = 'Yes' THEN 1 ELSE 0 END) AS overtime_departures,
 ROUND(100.0 * SUM(CASE WHEN OverTime = 'Yes' AND Attrition = 'Yes' THEN 1 ELSE 0 END)
 / NULLIF(SUM(CASE WHEN OverTime = 'Yes' THEN 1 ELSE 0 END),0),1) AS overtime_attrition_pct
FROM employees GROUP BY Department;

-- 3) Banding and average workforce tenure; bands are not historical periods.
WITH tenure_bands AS (
 SELECT CASE WHEN YearsAtCompany < 2 THEN '00-01 years'
             WHEN YearsAtCompany < 5 THEN '02-04 years'
             WHEN YearsAtCompany < 10 THEN '05-09 years'
             ELSE '10+ years' END AS tenure_band, Attrition
 FROM employees
)
SELECT tenure_band, COUNT(*) AS employees,
 SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS departures,
 ROUND(100.0 * SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*),1) AS attrition_pct
FROM tenure_bands GROUP BY tenure_band ORDER BY tenure_band;

-- 4) Quality assurance: out-of-range values and duplicated IDs.
SELECT COUNT(*) AS invalid_records FROM employees
WHERE Attrition NOT IN ('Yes','No') OR OverTime NOT IN ('Yes','No')
 OR YearsAtCompany < 0 OR MonthlyIncome < 0 OR JobSatisfaction NOT BETWEEN 1 AND 4;
