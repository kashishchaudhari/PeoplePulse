# PeoplePulse · Workforce Intelligence

Interactive HR analytics and SQL reporting portfolio prototype built with **Python, SQL, SQLite, pandas, Plotly, Streamlit, and uv**.

> **Live dashboard:** After deploying to Streamlit Community Cloud, paste the public URL here.
>
> **Demo only:** Uses deterministic synthetic employee records out of the box, or IBM's fictional HR dataset from Kaggle. No real employee data. Not connected to Oracle HCM, OTBI, or BI Publisher.

## What you'll see

- **Executive overview:** employee count, attrition %, non-attrition %, average tenure, headcount by department, tenure distribution.
- **Attrition insights:** department attrition rates, overtime comparison, metrics table.
- **Workforce profile:** job-role distribution, department satisfaction, workforce snapshot.
- **Report center:** five SQL report templates, CSV exports, local audit records, and illustrative role restrictions on compensation.
- **Global filters:** department and job role, applied to interactive analytics. Report-center SQL exports are explicitly database-wide (not filtered).
- **Zero-setup demo data:** 450 deterministic, fictional employees loaded at first launch. You can upload the [IBM HR Analytics Employee Attrition & Performance dataset on Kaggle](https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset).

## Tech stack

| Layer | Tools |
| --- | --- |
| Interactive UI | Streamlit, Plotly |
| Transformation | Python, pandas |
| Reporting | SQL, SQLite |
| Environment and dependencies | uv (`pyproject.toml`) |
| Testing | Python `unittest` |
| Deployment | Streamlit Community Cloud |

## Run locally with uv

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/).
2. Clone the repository and enter its root directory.
3. Run:

```bash
uv sync
uv run streamlit run app.py
```

`uv sync` creates a virtual environment and resolves dependencies from `pyproject.toml`. On first successful resolution it creates `uv.lock`; commit that lockfile to GitHub for reproducible deployments. This source package **does not include a pre-generated lockfile**, because dependency registry access was unavailable in the build environment.

Test the backend:

```bash
uv run python -m unittest discover -s tests -v
```

Alternatively, Streamlit Community Cloud can install the included `requirements.txt` without uv.

## Deploy on Streamlit Community Cloud

1. Commit `app.py`, `src/`, `sql/`, `requirements.txt`, `pyproject.toml`, `.streamlit/config.toml`, and the other project files to the repository root.
2. Visit https://share.streamlit.io and sign in using GitHub.
3. Select `kashishchaudhari/PeoplePulse`, branch `main`, main file `app.py`.
4. Deploy. The dashboard will automatically seed synthetic data on its first launch.
5. Copy the live URL into this README and GitHub's **About → Website** field.

**Hosted persistence:** Streamlit Community Cloud's filesystem should be treated as ephemeral. Data uploads and the SQLite reporting audit may reset on rebuild or restart. Only fictional datasets should be uploaded.

## File structure

```text
app.py                 # Interactive executive dashboard and SQL report center
src/portal.py          # SQLite schema, ingestion, reporting and audit functions
src/generate_demo.py   # Reproducible synthetic fictional dataset
sql/                   # Sample SQL reports
pyproject.toml         # uv dependencies and project metadata
.python-version        # Preferred local interpreter (Python 3.11)
requirements.txt       # Streamlit Community Cloud installer compatibility
tests/test_portal.py   # Five backend tests
.streamlit/config.toml # Theme
```

## Data and responsible usage

The Kaggle IBM HR dataset contains fictional employee records. The synthetic sample is generated locally and should not be interpreted as realistic workforce prevalence, demographic distributions or causal findings. The dashboard uses a demo role dropdown—not real user authentication. Compensation access gating is illustrative only. This is **not production HR software** and should not handle sensitive personal information.

Oracle HCM / OTBI and BI Publisher are **roadmap integrations**, not implemented. No time-saving claims have been measured.

## Roadmap

- Real SSO and permission enforcement at database level
- Privacy-preserving suppression of small groups
- Scheduled reporting and durable audit storage
- Power BI / Tableau and authorized Oracle HCM integrations
- Reproducible benchmark of manual vs automated reporting effort
