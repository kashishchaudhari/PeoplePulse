"""PeoplePulse: recruiter-friendly HR reporting demo with fictional data."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

import pandas as pd
import plotly.express as px
import streamlit as st
from generate_demo import generate
from portal import audit, connection, initialize, load_csv, report, summary

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB = DATA_DIR / "peoplepulse.db"

st.set_page_config(page_title="PeoplePulse | Workforce Intelligence", page_icon="📊", layout="wide", initial_sidebar_state="expanded")
st.markdown("""<style>
.block-container {padding-top: 1.6rem; padding-bottom: 2.5rem; max-width: 1420px;}
h1 {font-weight: 800; letter-spacing: -0.04em;}
[data-testid='stMetric'] {background: white; border: 1px solid #e5eaf0; padding: 14px 18px; border-radius: 13px;}
[data-testid='stMetricLabel'] {font-weight: 600;}
[data-testid='stMetricValue'] {color: #12364a;}
.subhead {color: #64748b; margin-top:-6px; font-size: 0.97rem;}
.notice {background:#e9f6f3; border-left: 4px solid #2c9c8e; padding: 10px 14px; border-radius: 6px;}
</style>""", unsafe_allow_html=True)

initialize(DB)
# The initial demo is immediately viewable without uploading files, and is labeled fictional.
if summary(DB)["employees"] == 0:
    load_csv(DB, generate(DATA_DIR / "demo_employees.csv", count=450, seed=42))

with st.sidebar:
    st.title("PeoplePulse")
    st.caption("WORKFORCE INTELLIGENCE")
    st.divider()
    role = st.selectbox("Demo access level", ["analyst", "manager", "admin"], help="UI-only simulation, not production authentication")
    actor = st.text_input("Report audit label", "portfolio_viewer", max_chars=50)
    st.divider()
    st.subheader("Dataset")
    uploaded = st.file_uploader("Import IBM HR Analytics CSV", type=["csv"], help="Use the IBM fictional attrition CSV from Kaggle")
    if uploaded and st.button("Import CSV", use_container_width=True):
        try:
            p = DATA_DIR / "uploaded.csv"
            p.write_bytes(uploaded.getvalue())
            imported = load_csv(DB, p)
            st.success(f"Imported {imported:,} fictional employee records.")
            st.rerun()
        except (ValueError, TypeError, KeyError) as e:
            st.error(f"Dataset validation failed: {e}")
    if st.button("Reset to synthetic sample", use_container_width=True):
        load_csv(DB, generate(DATA_DIR / "demo_employees.csv", count=450, seed=42))
        st.rerun()
    st.caption("Sample records are synthetic; Kaggle IBM records are also fictional. No real employee data required.")
    st.divider()
    st.caption("Portfolio prototype · Python · SQL · SQLite · Streamlit · uv")

with connection(DB) as con:
    departments = [r[0] for r in con.execute("SELECT DISTINCT Department FROM employees ORDER BY Department")]
    role_options = [r[0] for r in con.execute("SELECT DISTINCT JobRole FROM employees ORDER BY JobRole")]

st.title("Workforce intelligence, made useful.")
st.markdown('<p class="subhead">A practical HR analytics workspace for exploring workforce health and generating consistent reporting.</p>', unsafe_allow_html=True)
st.caption("DEMO ENVIRONMENT  •  FICTIONAL EMPLOYEE DATA  •  NOT CONNECTED TO ORACLE HCM")

f1,f2 = st.columns([1,1])
with f1:
    selected_depts = st.multiselect("Department", departments, default=departments)
with f2:
    selected_roles = st.multiselect("Job role", role_options, default=role_options)

# Parameterized filtering limits queries to known fields and role values; no dynamic SQL identifiers.
clauses=[]
params=[]
if not selected_depts or not selected_roles:
    st.warning("Choose at least one department and one job role to display analytics.")
    st.stop()
clauses.append("Department IN (" + ",".join("?" * len(selected_depts)) + ")")
params.extend(selected_depts)
clauses.append("JobRole IN (" + ",".join("?" * len(selected_roles)) + ")")
params.extend(selected_roles)
where = " WHERE " + " AND ".join(clauses)
with connection(DB) as con:
    # Only selected columns; no employee-level records are displayed in the UI.
    data = pd.read_sql_query("""SELECT Department, JobRole, Attrition, Gender, Age, MonthlyIncome,
               JobSatisfaction, PerformanceRating, YearsAtCompany, OverTime
               FROM employees""" + where, con, params=params)
if data.empty:
    st.info("No matching workforce records. Try broader filters.")
    st.stop()

n = len(data)
attrition = int((data.Attrition == "Yes").sum())
retention = 100.0 * (n - attrition)/n
rate = attrition/n*100
mean_tenure = data.YearsAtCompany.mean()
headcount, rate_card, retention_card, tenure_card = st.columns(4)
headcount.metric("Employees in view", f"{n:,}")
rate_card.metric("Attrition rate", f"{rate:.1f}%")
retention_card.metric("Non-attrition share", f"{retention:.1f}%")
tenure_card.metric("Average tenure", f"{mean_tenure:.1f} years")

tab_overview,tab_attrition,tab_workforce,tab_reports = st.tabs(["📊 Executive overview", "📉 Attrition insights", "👥 Workforce profile", "📁 Report center"])

COLORS = ["#137C85", "#48A9A6", "#A7D9D5", "#2D5E79", "#87AFC4", "#D9B26D"]

def bar(df, x, y, title, horizontal=False, color=None):
    if horizontal:
        fig = px.bar(df, x=x, y=y, orientation="h", color=color, color_discrete_sequence=COLORS)
    else:
        fig = px.bar(df, x=x, y=y, color=color, color_discrete_sequence=COLORS)
    fig.update_layout(title=title, margin=dict(l=10,r=10,t=52,b=12),height=330,
                      plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)", legend_title_text="")
    fig.update_traces(marker_line_width=0)
    st.plotly_chart(fig, use_container_width=True)

with tab_overview:
    left, right = st.columns(2)
    counts = data.groupby("Department").size().rename("Employees").reset_index().sort_values("Employees",ascending=False)
    with left:
        bar(counts, "Department", "Employees", "Headcount by department")
    with right:
        trend = data.groupby("YearsAtCompany").size().rename("Employees").reset_index()
        bar(trend, "YearsAtCompany", "Employees", "Employee tenure distribution")
    st.markdown('<div class="notice"><strong>Reading the dashboard:</strong> Figures reflect the active department and job-role filters. Attrition indicates fictional dataset outcomes, not a forecast.</div>',unsafe_allow_html=True)

with tab_attrition:
    left, right = st.columns(2)
    a = data.assign(Attrited=data.Attrition.eq("Yes").astype(int)).groupby("Department").agg(Employees=("Attrited","size"),Departures=("Attrited","sum")).reset_index()
    a["Attrition %"] = (100*a.Departures/a.Employees).round(1)
    with left:
        bar(a,"Department","Attrition %","Attrition rate by department")
    with right:
        ot = data.assign(Attrited=data.Attrition.eq("Yes").astype(int)).groupby("OverTime").agg(Employees=("Attrited","size"),Departures=("Attrited","sum")).reset_index()
        ot["Attrition %"] = (100*ot.Departures/ot.Employees).round(1)
        bar(ot,"OverTime","Attrition %","Attrition vs. overtime")
    st.dataframe(a, use_container_width=True, hide_index=True)
    st.caption("Observational summaries only. Overtime and attrition may be associated but this analysis does not establish causation.")

with tab_workforce:
    l,r = st.columns(2)
    by_role = data.groupby("JobRole").size().rename("Employees").reset_index().sort_values("Employees")
    with l:
        bar(by_role,"Employees","JobRole","Roles by employee count",horizontal=True)
    with r:
        sat = data.groupby("Department")["JobSatisfaction"].mean().round(2).rename("Avg satisfaction (1-4)").reset_index()
        bar(sat,"Department","Avg satisfaction (1-4)","Job satisfaction by department")
    st.markdown("#### Department workforce snapshot")
    snapshot = data.groupby("Department").agg(Headcount=("Age","size"),Avg_Age=("Age","mean"),Avg_Tenure=("YearsAtCompany","mean"),Avg_Satisfaction=("JobSatisfaction","mean")).round(1).reset_index()
    st.dataframe(snapshot,hide_index=True,use_container_width=True)

with tab_reports:
    st.markdown("#### SQL report library")
    st.caption("Saved predefined queries • CSV export • local audit trail • example access restrictions")
    reports = {
        "Headcount by department":"headcount",
        "Attrition by department":"attrition",
        "Performance by department":"performance",
        "Compensation overview (manager/admin)":"compensation",
        "Workforce roles & satisfaction":"workforce"
    }
    selected_report_label = st.selectbox("Select report",list(reports))
    if st.button("Generate SQL report", type="primary"):
        try:
            rows = report(DB,reports[selected_report_label],role,actor.strip() or "portfolio_viewer")
            st.session_state["report_result"] = pd.DataFrame(rows)
            st.session_state["report_name"] = reports[selected_report_label]
        except PermissionError as e:
            st.error(str(e))
    if "report_result" in st.session_state:
        st.caption(f"Last generated report: {st.session_state['report_name']} • Unfiltered, database-wide aggregation")
        st.dataframe(st.session_state["report_result"],use_container_width=True,hide_index=True)
        st.download_button("Download report CSV",st.session_state["report_result"].to_csv(index=False),"peoplepulse_report.csv","text/csv")
    if role == "admin":
        with st.expander("View report audit trail (admin demo)"):
            st.dataframe(pd.DataFrame(audit(DB,role)),use_container_width=True,hide_index=True)
    st.info("Demo roles are selectable by visitors and are NOT authentication. Reporting uses aggregate SQL; this app must not be used with real employee data or sensitive records.")

st.divider()
st.caption("PeoplePulse · Independent HR reporting portfolio project · Kaggle IBM HR Analytics dataset or deterministic synthetic data · Not production HR software")
