"""Synthetic recruitment case study. Candidate records are fabricated and entirely separate from IBM HR data."""
from __future__ import annotations
from datetime import date, timedelta
import random
import statistics
import pandas as pd

STAGES = ('Applied','Screen','Interview','Offer','Hired')
CHANNELS = ('LinkedIn','Referral','Job board','Career site')

def demo_applications(n=900,seed=2026)->pd.DataFrame:
    rng=random.Random(seed)
    result=[]
    for i in range(n):
        channel=rng.choices(CHANNELS,weights=(40,20,25,15))[0]
        role=rng.choice(('Data Analyst','Business Analyst','HR Analyst','Operations Analyst'))
        department=rng.choice(('People','Operations','Finance'))
        applied=date(2026,1,1)+timedelta(days=rng.randrange(240))
        # Probabilities deliberately differ by channel to provide synthetic analytical examples.
        screen_prob={'LinkedIn':.56,'Referral':.77,'Job board':.47,'Career site':.60}[channel]
        screen=rng.random()<screen_prob
        interview=screen and rng.random()<.48
        offer=interview and rng.random()<.34
        hired=offer and rng.random()<.72
        stage='Hired' if hired else 'Offer' if offer else 'Interview' if interview else 'Screen' if screen else 'Applied'
        days_to_hire=rng.randint(17,72) if hired else None
        result.append({'CandidateID':f'SYN-{i+1:05d}','Source':channel,'Role':role,'Department':department,
                       'AppliedDate':applied.isoformat(),'LastStage':stage,'Hired':hired,
                       'DaysToHire':days_to_hire})
    return pd.DataFrame(result)

def funnel(df:pd.DataFrame)->pd.DataFrame:
    """Cumulative stage counts; each stage denominator is prior stage, applied is all."""
    if df.empty:
        return pd.DataFrame(columns=['Stage','Candidates','Conversion from prior (%)','Overall conversion (%)'])
    stages=df.LastStage.map({s:i for i,s in enumerate(STAGES)})
    if stages.isna().any(): raise ValueError('Invalid stage name')
    total=len(df)
    rows=[]
    previous=total
    for i,stage in enumerate(STAGES):
        count=int((stages>=i).sum())
        rows.append({'Stage':stage,'Candidates':count,
                     'Conversion from prior (%)':round(100*count/previous,1) if previous else 0,
                     'Overall conversion (%)':round(100*count/total,1)})
        previous=count
    return pd.DataFrame(rows)

def source_metrics(df:pd.DataFrame)->pd.DataFrame:
    if df.empty: return pd.DataFrame(columns=['Source','Applicants','Hires','Hire conversion (%)','Median time to hire (days)'])
    records=[]
    for source,g in df.groupby('Source'):
        hired=g[g.Hired]
        records.append({'Source':source,'Applicants':len(g),'Hires':len(hired),
                        'Hire conversion (%)':round(100*len(hired)/len(g),1),
                        'Median time to hire (days)':round(float(hired.DaysToHire.median()),1) if len(hired) else None})
    return pd.DataFrame(records).sort_values('Applicants',ascending=False)

def bottleneck_summary(df:pd.DataFrame)->str:
    f=funnel(df)
    if len(f)<2:return 'Not enough data to identify a funnel bottleneck.'
    candidate=f.iloc[1:].sort_values('Conversion from prior (%)').iloc[0]
    return (f"Largest stage-to-stage drop: entry to {candidate['Stage']} "
            f"({candidate['Conversion from prior (%)']:.1f}% of preceding-stage candidates advance). "
            "This is a synthetic workflow; no actual recruitment outcomes are represented.")
