from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent/'src'))
import pandas as pd
import streamlit as st
from portal import initialize, load_csv, summary, report, audit, REPORTS
from generate_demo import generate

st.set_page_config(page_title='HR Reporting Portal',layout='wide',page_icon='📊')
st.title('HR Reporting Portal')
st.caption('Portfolio demonstration | IBM HR Analytics Kaggle dataset or clearly labeled synthetic demo | Not Oracle HCM')
root=Path(__file__).parent
DB=root/'data'/'hr_portal.db'
DB.parent.mkdir(exist_ok=True)
initialize(DB)
with st.sidebar:
    st.header('Data & access')
    uploaded=st.file_uploader('Load original IBM HR CSV',type=['csv'])
    if uploaded and st.button('Import Kaggle CSV'):
        path=root/'data'/'uploaded.csv';path.write_bytes(uploaded.getvalue())
        try: st.success(f'Imported {load_csv(DB,path):,} records')
        except (ValueError,TypeError) as exc:st.error(str(exc))
    if st.button('Use synthetic demo data'):
        path=generate(root/'data'/'demo_employees.csv')
        st.success(f'Loaded {load_csv(DB,path)} synthetic rows')
    role=st.selectbox('Demonstration role',['analyst','manager','admin'])
    actor=st.text_input('Audit user label','portfolio_user')
    report_name=st.selectbox('Report',list(REPORTS))

s=summary(DB)
a,b,c=st.columns(3)
a.metric('Employees',f"{s['employees']:,}")
b.metric('Attrition rate',f"{100*s['leavers']/s['employees']:.1f}%" if s['employees'] else '—')
c.metric('Departments',s['departments'])
if st.button('Run report',type='primary'):
    try:
        rows=report(DB,report_name,role,actor)
        df=pd.DataFrame(rows)
        st.dataframe(df,use_container_width=True,hide_index=True)
        if not df.empty:
            st.bar_chart(df.set_index(df.columns[0]).iloc[:,0])
            st.download_button('Download report CSV',df.to_csv(index=False),'hr_report.csv','text/csv')
    except (ValueError,PermissionError) as exc:st.error(str(exc))
if role=='admin':
    with st.expander('Audit trail'):
        st.dataframe(pd.DataFrame(audit(DB,role)),hide_index=True,use_container_width=True)
st.info('Demo roles are simulated through a UI selector. Production authentication, row-level database security, and privacy compliance are not implemented.')
