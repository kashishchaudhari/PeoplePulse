import sys
import unittest
from pathlib import Path
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from analytics import grouped_attrition, overtime_analysis, quality_report, workforce_metrics, attrition_narrative
from case_study import build_case_study

class TestAnalytics(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame([
            {'EmployeeNumber':i,'Attrition':'Yes' if i%4==0 else 'No',
             'Department':'A' if i<=12 else 'B','OverTime':'Yes' if i%2==0 else 'No',
             'JobRole':'Analyst','JobSatisfaction':3,'YearsAtCompany':2,'JobLevel':2,
             'MonthlyIncome':4200} for i in range(1,25)
        ])
    def test_metrics(self):
        self.assertEqual(workforce_metrics(self.df)['employees'],24)
        self.assertEqual(workforce_metrics(self.df)['departures'],6)
    def test_group_rates_have_denominators(self):
        t=grouped_attrition(self.df,'Department')
        self.assertEqual(int(t.Employees.sum()),24)
        self.assertTrue((t['CI upper (%)'] >= t['Attrition rate (%)']).all())
    def test_group_whitelist(self):
        with self.assertRaises(ValueError): grouped_attrition(self.df,'EmployeeNumber')
    def test_tiny_group_suppression(self):
        self.assertTrue(grouped_attrition(self.df,'Department',minimum_group_size=20).empty)
    def test_overtime_analysis(self):
        t=overtime_analysis(self.df)
        self.assertEqual(t['yes_n'],12)
        self.assertEqual(t['no_n'],12)
    def test_quality(self):
        self.assertTrue((quality_report(self.df).Result=='PASS').all())
    def test_case_study(self):
        text=build_case_study(self.df,'Test fixture')
        self.assertIn('Test fixture',text)
        self.assertIn('causal',text)

if __name__ == '__main__': unittest.main()
