"""Reproducible cross-sectional workforce analysis. Never interpret associations causally."""
from __future__ import annotations
import math
import pandas as pd
from scipy.stats import chi2_contingency
from statsmodels.stats.proportion import proportion_confint


def workforce_metrics(df: pd.DataFrame) -> dict:
    n = len(df)
    departures = int(df['Attrition'].eq('Yes').sum()) if n else 0
    return {'employees':n, 'departures':departures, 'attrition_rate':100 * departures/n if n else 0,
            'mean_tenure':float(df['YearsAtCompany'].mean()) if n else 0}


def grouped_attrition(df: pd.DataFrame, group: str, minimum_group_size: int = 5) -> pd.DataFrame:
    """Rates plus Wilson 95% intervals; suppress tiny groups from display."""
    if group not in ('Department','OverTime','JobRole','JobSatisfaction','YearsAtCompany','JobLevel'):
        raise ValueError('Unsupported grouping variable')
    if minimum_group_size < 1:
        raise ValueError('minimum_group_size must be >=1')
    output = []
    for value, subset in df.groupby(group, dropna=False):
        n = len(subset)
        if n < minimum_group_size:
            continue
        k = int(subset['Attrition'].eq('Yes').sum())
        lo, hi = proportion_confint(k,n,alpha=.05,method='wilson')
        output.append({group:value,'Employees':n,'Departures':k,'Attrition rate (%)':round(100*k/n,1),
                       'CI lower (%)':round(100*lo,1),'CI upper (%)':round(100*hi,1)})
    return pd.DataFrame(output)


def overtime_analysis(df: pd.DataFrame) -> dict:
    """2x2 observed comparison and chi-square association; not a causal estimate."""
    valid = df.loc[df['OverTime'].isin(('Yes','No')) & df['Attrition'].isin(('Yes','No'))]
    c = pd.crosstab(valid.OverTime, valid.Attrition).reindex(index=['No','Yes'],columns=['No','Yes'],fill_value=0)
    a,b = int(c.loc['Yes','Yes']),int(c.loc['Yes','No'])
    d,e = int(c.loc['No','Yes']),int(c.loc['No','No'])
    yes_n, no_n = a+b, d+e
    if not yes_n or not no_n:
        return {'available':False,'reason':'Both overtime groups must contain employees.'}
    yes_rate, no_rate = a/yes_n, d/no_n
    # Chi-square is not appropriate for small expected cell counts. Explicitly distinguish such cases.
    p_value = None
    if a and b and d and e:
        test = chi2_contingency(c.values, correction=False)
        if all(x >= 5 for x in test.expected_freq.ravel()):
            p_value = float(test.pvalue)
    return {'available':True,'yes_n':yes_n,'no_n':no_n,'yes_departures':a,'no_departures':d,
            'yes_rate_pct':100*yes_rate,'no_rate_pct':100*no_rate,
            'difference_pp':100*(yes_rate-no_rate),'risk_ratio':yes_rate/no_rate if no_rate else None,
            'chi_square_p':p_value}


def quality_report(df: pd.DataFrame) -> pd.DataFrame:
    checks = [
        ('Row count > 0',len(df)>0),
        ('Unique employee IDs',df.EmployeeNumber.is_unique),
        ('No missing employee IDs',df.EmployeeNumber.notna().all()),
        ('Valid attrition labels',df.Attrition.isin(['Yes','No']).all()),
        ('Valid overtime labels',df.OverTime.isin(['Yes','No']).all()),
        ('Nonnegative years at company',df.YearsAtCompany.ge(0).all()),
        ('Nonnegative monthly income',df.MonthlyIncome.ge(0).all()),
        ('Satisfaction between 1–4',df.JobSatisfaction.between(1,4).all()),
    ]
    return pd.DataFrame([{'Check':name,'Result':'PASS' if passed else 'FAIL'} for name,passed in checks])


def attrition_narrative(df: pd.DataFrame) -> dict:
    """Dataset-specific findings from actual records; no invented outcomes."""
    outcome = overtime_analysis(df)
    groups = grouped_attrition(df,'Department', minimum_group_size=5)
    if groups.empty:
        strongest='No department has a sufficient sample for comparison.'
    else:
        highest = groups.sort_values('Attrition rate (%)',ascending=False).iloc[0]
        strongest = f"{highest['Department']} has the highest observed department attrition rate ({highest['Attrition rate (%)']:.1f}%; n={int(highest['Employees'])})."
    if outcome['available']:
        comparison = f"Overtime=Yes: {outcome['yes_rate_pct']:.1f}% (n={outcome['yes_n']}); Overtime=No: {outcome['no_rate_pct']:.1f}% (n={outcome['no_n']}); observed difference {outcome['difference_pp']:+.1f} percentage points."
    else:
        comparison = outcome['reason']
    return {'department':strongest,'overtime':comparison,
            'caveat':'Observational fictional data: these associations are not causal, and do not generalize to real employees.'}
