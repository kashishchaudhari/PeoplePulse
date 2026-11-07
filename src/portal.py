"""Standalone HR reporting engine with SQLite, privacy views and audit logs."""
import csv
import hashlib
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

COLUMNS = ['Age','Attrition','BusinessTravel','Department','DistanceFromHome','Education','EducationField','EmployeeNumber','EnvironmentSatisfaction','Gender','JobInvolvement','JobLevel','JobRole','JobSatisfaction','MaritalStatus','MonthlyIncome','NumCompaniesWorked','OverTime','PercentSalaryHike','PerformanceRating','StockOptionLevel','TotalWorkingYears','TrainingTimesLastYear','WorkLifeBalance','YearsAtCompany','YearsInCurrentRole','YearsSinceLastPromotion','YearsWithCurrManager']
ALLOWED_ROLES={'analyst','manager','admin'}
REPORTS={
 'headcount': '''SELECT Department, COUNT(*) headcount, ROUND(AVG(YearsAtCompany),1) avg_tenure_years FROM employees GROUP BY Department ORDER BY headcount DESC''',
 'attrition': '''SELECT Department, COUNT(*) headcount, SUM(CASE WHEN Attrition='Yes' THEN 1 ELSE 0 END) attrition_count, ROUND(100.0*SUM(CASE WHEN Attrition='Yes' THEN 1 ELSE 0 END)/COUNT(*),1) attrition_pct FROM employees GROUP BY Department ORDER BY attrition_pct DESC''',
 'performance': '''SELECT Department, PerformanceRating, COUNT(*) employees FROM employees GROUP BY Department, PerformanceRating ORDER BY Department, PerformanceRating''',
 'compensation': '''SELECT Department, COUNT(*) employees, ROUND(AVG(MonthlyIncome),0) avg_monthly_income FROM employees GROUP BY Department''',
 'workforce': '''SELECT JobRole, COUNT(*) headcount, ROUND(AVG(YearsAtCompany),1) avg_tenure, ROUND(AVG(JobSatisfaction),2) avg_job_satisfaction FROM employees GROUP BY JobRole ORDER BY headcount DESC'''
}

@contextmanager
def connection(path):
    """Close SQLite handles on every exit, including on Windows and errors."""
    con = sqlite3.connect(str(path))
    con.row_factory = sqlite3.Row
    try:
        with con:
            yield con
    finally:
        con.close()

def initialize(path):
    with connection(path) as con:
        con.executescript('''CREATE TABLE IF NOT EXISTS employees (EmployeeNumber INTEGER PRIMARY KEY, Age INTEGER, Attrition TEXT, BusinessTravel TEXT, Department TEXT, DistanceFromHome INTEGER, Education INTEGER, EducationField TEXT, EnvironmentSatisfaction INTEGER, Gender TEXT, JobInvolvement INTEGER, JobLevel INTEGER, JobRole TEXT, JobSatisfaction INTEGER, MaritalStatus TEXT, MonthlyIncome INTEGER, NumCompaniesWorked INTEGER, OverTime TEXT, PercentSalaryHike INTEGER, PerformanceRating INTEGER, StockOptionLevel INTEGER, TotalWorkingYears INTEGER, TrainingTimesLastYear INTEGER, WorkLifeBalance INTEGER, YearsAtCompany INTEGER, YearsInCurrentRole INTEGER, YearsSinceLastPromotion INTEGER, YearsWithCurrManager INTEGER);
CREATE TABLE IF NOT EXISTS audit_log (id INTEGER PRIMARY KEY AUTOINCREMENT, event_ts TEXT NOT NULL, actor TEXT NOT NULL, role TEXT NOT NULL, action TEXT NOT NULL, report TEXT NOT NULL, row_count INTEGER NOT NULL);
CREATE INDEX IF NOT EXISTS idx_employee_department ON employees(Department);''')

def load_csv(db_path,csv_path):
    initialize(db_path)
    with open(csv_path,newline='',encoding='utf-8-sig') as f:
        reader=csv.DictReader(f)
        missing=set(COLUMNS)-set(reader.fieldnames or [])
        if missing:raise ValueError('Dataset missing columns: '+', '.join(sorted(missing)))
        rows=[]; seen=set()
        for row in reader:
            eid=int(row['EmployeeNumber'])
            if eid in seen:raise ValueError('Duplicate EmployeeNumber: '+str(eid))
            seen.add(eid)
            if row['Attrition'] not in ('Yes','No'): raise ValueError('Invalid Attrition value')
            item=[]
            for key in COLUMNS:
                value=row[key]
                if key not in ('Attrition','BusinessTravel','Department','EducationField','Gender','JobRole','MaritalStatus','OverTime'):
                    value=int(value)
                item.append(value)
            rows.append(item)
    with connection(db_path) as con:
        con.execute('DELETE FROM employees')
        con.executemany('INSERT INTO employees ('+','.join(COLUMNS)+') VALUES ('+','.join('?' for _ in COLUMNS)+')',rows)
    return len(rows)

def report(db_path, report_name, role='analyst', actor='demo'):
    if role not in ALLOWED_ROLES:raise PermissionError('Invalid role')
    if report_name not in REPORTS:raise ValueError('Unknown report')
    if report_name=='compensation' and role not in ('manager','admin'):
        raise PermissionError('Compensation summary requires manager or admin role')
    with connection(db_path) as con:
        out=[dict(r) for r in con.execute(REPORTS[report_name]).fetchall()]
        con.execute('INSERT INTO audit_log(event_ts,actor,role,action,report,row_count) VALUES (?,?,?,?,?,?)',
                   (datetime.now(timezone.utc).isoformat(),actor,role,'run',report_name,len(out)))
    return out

def audit(db_path,role='admin'):
    if role!='admin':raise PermissionError('Admin only')
    with connection(db_path) as con:return [dict(r) for r in con.execute('SELECT * FROM audit_log ORDER BY id DESC LIMIT 100')]

def summary(db_path):
    with connection(db_path) as con:
        return dict(con.execute('SELECT COUNT(*) employees, SUM(CASE WHEN Attrition="Yes" THEN 1 ELSE 0 END) leavers, COUNT(DISTINCT Department) departments FROM employees').fetchone())
