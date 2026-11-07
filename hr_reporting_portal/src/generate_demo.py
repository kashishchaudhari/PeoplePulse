"""Clearly labeled synthetic demo only, NOT the Kaggle dataset."""
import csv, random
from pathlib import Path
from portal import COLUMNS

def generate(out, count=250,seed=42):
    rng=random.Random(seed)
    departments=['Sales','Research & Development','Human Resources']
    roles={'Sales':['Sales Executive','Sales Representative'], 'Research & Development':['Research Scientist','Laboratory Technician','Research Director'], 'Human Resources':['Human Resources']}
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=COLUMNS);w.writeheader()
        for i in range(count):
            department=rng.choices(departments,[25,65,10])[0]
            tenure=rng.randint(0,22);total=tenure+rng.randint(0,12)
            d={'EmployeeNumber':1000+i,'Age':rng.randint(20,60),'Attrition':rng.choices(['Yes','No'],[18,82])[0],'BusinessTravel':'Travel_Rarely','Department':department,'DistanceFromHome':rng.randint(1,28),'Education':rng.randint(1,5),'EducationField':'Life Sciences','EnvironmentSatisfaction':rng.randint(1,4),'Gender':rng.choice(['Female','Male']),'JobInvolvement':rng.randint(1,4),'JobLevel':rng.randint(1,5),'JobRole':rng.choice(roles[department]),'JobSatisfaction':rng.randint(1,4),'MaritalStatus':'Single','MonthlyIncome':rng.randint(2500,16000),'NumCompaniesWorked':rng.randint(0,8),'OverTime':rng.choice(['Yes','No']),'PercentSalaryHike':rng.randint(11,25),'PerformanceRating':rng.choice([3,4]),'StockOptionLevel':rng.randint(0,3),'TotalWorkingYears':total,'TrainingTimesLastYear':rng.randint(0,6),'WorkLifeBalance':rng.randint(1,4),'YearsAtCompany':tenure,'YearsInCurrentRole':rng.randint(0,tenure),'YearsSinceLastPromotion':rng.randint(0,tenure),'YearsWithCurrManager':rng.randint(0,tenure)}
            w.writerow(d)
    return out
if __name__=='__main__':
    print(generate('data/demo_employees.csv'))
