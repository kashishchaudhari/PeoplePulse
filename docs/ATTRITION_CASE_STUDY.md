# PeoplePulse: Attrition Investigation

**Source:** Synthetic 450-record demo  
**Population:** 450 fictional records  
**Design:** Cross-sectional exploratory analysis; not a randomized experiment or historical time series.

## Business question
Which segments have elevated observed attrition, and which hypotheses should an HR team examine with real, authorized data?

## Dataset and KPI definitions
- Dataset: Synthetic 450-record demo.
- Attrition rate = number with Attrition=Yes / number of employee records in group.
- Overall observed attrition: **15.3%** (69 / 450).
- Employee tenure is the dataset's YearsAtCompany field, not a monthly event series.
- Wilson 95% binomial intervals express sampling uncertainty; fictional data is not representative of real employers.

## Finding 1: departments
Human Resources has the highest observed department attrition rate (22.0%; n=41).

| Department             |   Employees |   Departures |   Attrition rate (%) |   CI lower (%) |   CI upper (%) |
|:-----------------------|------------:|-------------:|---------------------:|---------------:|---------------:|
| Human Resources        |          41 |            9 |                 22   |           12   |           36.7 |
| Research & Development |         281 |           40 |                 14.2 |           10.6 |           18.8 |
| Sales                  |         128 |           20 |                 15.6 |           10.3 |           22.9 |

## Finding 2: overtime association
Overtime=Yes: 15.2% (n=231); Overtime=No: 15.5% (n=219); observed difference -0.4 percentage points.

- Unadjusted chi-square p-value: 0.9125 (chi-square; unadjusted and exploratory).
- These group-level findings cannot establish that overtime causes departures. Department, job level, tenure and other covariates can confound the relationship.

## Quality checks
8 of 8 checks passed.

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
