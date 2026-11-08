"""Generate a transparent Markdown case study from the selected local dataset."""
import argparse
from pathlib import Path
import pandas as pd
from analytics import attrition_narrative, grouped_attrition, overtime_analysis, quality_report, workforce_metrics
from portal import connection


def build_case_study(df: pd.DataFrame, source: str) -> str:
    m=workforce_metrics(df)
    n=attrition_narrative(df)
    o=overtime_analysis(df)
    table=grouped_attrition(df,'Department').to_markdown(index=False) if not df.empty else 'No data'
    qa=quality_report(df)
    p='Not reported (expected cell count too small)'
    if o['available'] and o['chi_square_p'] is not None:
        p=f"{o['chi_square_p']:.4g} (chi-square; unadjusted and exploratory)"
    return f'''# PeoplePulse: Attrition Investigation

**Source:** {source}  
**Population:** {m['employees']:,} fictional records  
**Design:** Cross-sectional exploratory analysis; not a randomized experiment or historical time series.

## Business question
Which segments have elevated observed attrition, and which hypotheses should an HR team examine with real, authorized data?

## Dataset and KPI definitions
- Dataset: {source}.
- Attrition rate = number with Attrition=Yes / number of employee records in group.
- Overall observed attrition: **{m['attrition_rate']:.1f}%** ({m['departures']:,} / {m['employees']:,}).
- Employee tenure is the dataset's YearsAtCompany field, not a monthly event series.
- Wilson 95% binomial intervals express sampling uncertainty; fictional data is not representative of real employers.

## Finding 1: departments
{n['department']}

{table}

## Finding 2: overtime association
{n['overtime']}

- Unadjusted chi-square p-value: {p}.
- These group-level findings cannot establish that overtime causes departures. Department, job level, tenure and other covariates can confound the relationship.

## Quality checks
{int((qa['Result']=='PASS').sum())} of {len(qa)} checks passed.

## Recommendations for an HR stakeholder
1. Validate whether the same patterns occur in authorized, longitudinal organizational data.
2. Compare rates alongside group sizes and uncertainty; do not rank small groups solely on point estimates.
3. Investigate workload, job level, manager context and tenure before designing interventions.
4. Define an evaluation plan (baseline, time window, outcome and comparison group) before claiming business impact.

## Important limitations
- Fictional data; patterns **do not imply** real-world prevalence.
- Cross-sectional snapshot, not a time series, so no genuine monthly attrition trends.
- Exploratory group comparisons are not adjusted causal estimates; multiple-comparison caution applies.
- No cost-of-turnover assumptions or ROI claims are made.
- Demo application roles are not production security controls.
'''

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--db',default='data/peoplepulse.db')
    parser.add_argument('--source',default='Synthetic demo (fictional)')
    parser.add_argument('--output',default='docs/ATTRITION_CASE_STUDY.md')
    args=parser.parse_args()
    with connection(args.db) as con:
        frame=pd.read_sql_query('SELECT * FROM employees',con)
    dest=Path(args.output);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(build_case_study(frame,args.source),encoding='utf-8')
    print(f'Wrote {dest}')
