# HR Reporting Portal

An **HR analytics reporting portfolio project** built with **Python, SQL (SQLite), pandas, and Streamlit**. Supports department headcount, attrition, performance, compensation summaries and workforce KPIs with data-quality checks, demo role authorization, CSV exports, and audit logging.

> **Integrity note:** This is an independent portfolio prototype, **not** an Oracle HCM, OTBI, or BI Publisher implementation. The app does not connect to those systems. No measured 45% time savings, production compliance certification, or deployment to HR staff is claimed.

## Data: Kaggle

**Primary source:** [IBM HR Analytics Employee Attrition & Performance](https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset), a fictional employee dataset originally created for HR analytics demonstrations. Contains **1,470 rows and 35 columns**, including department, attrition, job role, satisfaction, compensation and tenure. Dataset license and usage terms are on its Kaggle page. Do not upload private employee data.

Download using Kaggle CLI (requires a Kaggle account/credentials):

```bash
pip install kaggle
kaggle datasets download -d pavansubhasht/ibm-hr-analytics-attrition-dataset -p data --unzip
```

Use the app sidebar to upload `WA_Fn-UseC_-HR-Employee-Attrition.csv`. The repository **does not redistribute Kaggle data**. A separate deterministic synthetic-data option is provided so the project runs without a Kaggle download; it is explicitly labeled demo data.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run app.py
```

Select **Use synthetic demo data** or upload the original Kaggle CSV. Choose an example role, then a report and click **Run report**.

## Reports

| Report | Output | Access |
|---|---|---|
| Headcount | Department counts, average tenure | Analyst+ |
| Attrition | Department attrition counts and rates | Analyst+ |
| Performance | Performance-rating counts by department | Analyst+ |
| Compensation | Average salary by department, no individual salary | Manager/admin |
| Workforce | Job role counts, tenure and job satisfaction | Analyst+ |

## Approach

1. **Ingest** Kaggle CSV and validate required columns, employee identifiers and attrition labels.
2. **Model** typed records in SQLite; use grouped SQL for dashboard-ready aggregates.
3. **Report** predefined, parameter-free SQL templates; no arbitrary SQL execution.
4. **Audit** successful report requests with timestamp, actor label, role and row count.
5. **Export** aggregated results to CSV for scheduled-report workflows.
6. **Test** data import, aggregation, permissions and auditing using standard-library unittest.

```bash
python -m unittest discover -s tests -v
```

## Privacy/security limitations

- Input dataset is **fictional**; no real employee PII required.
- Reports aggregate by department/job role, and display no employee IDs or names.
- The Streamlit role selector is a **demonstration**, not real authentication or production RBAC.
- Audit records are stored locally, with no tamper-evident retention guarantees.
- Real deployment would require SSO, database-enforced row-level security, encryption, secure audit storage, privacy review, and small-group suppression to limit inference risk.

## Oracle enterprise integration roadmap (not implemented)

- Connect authorized Oracle HCM subject areas using OTBI analyses.
- Rebuild aggregated HR queries as BI Publisher data models and scheduled delivery jobs.
- Use HCM role permissions and secure delivery controls rather than UI role switching.
- Compare manual and automated report turnaround times with measured before/after tests before claiming a percentage improvement.

## Next steps

Add real SSO, database-enforced RLS, BI Publisher/OTBI screenshots from an appropriately licensed Oracle training environment, scheduled report delivery, and documented baseline metrics. Avoid representing these roadmap items as completed.
