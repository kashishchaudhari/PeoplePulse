import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from recruitment import demo_applications, funnel, source_metrics, bottleneck_summary

class TestRecruitment(unittest.TestCase):
    def test_reproducible(self):
        self.assertTrue(demo_applications(100).equals(demo_applications(100)))
    def test_funnel_monotonic(self):
        f=funnel(demo_applications(300))
        self.assertEqual(int(f.iloc[0].Candidates),300)
        self.assertTrue(all(a>=b for a,b in zip(f.Candidates,f.Candidates[1:])))
    def test_sourcing_totals(self):
        df=demo_applications(280)
        s=source_metrics(df)
        self.assertEqual(int(s.Applicants.sum()),len(df))
        self.assertEqual(int(s.Hires.sum()),int(df.Hired.sum()))
    def test_summary(self):
        self.assertIn('synthetic',bottleneck_summary(demo_applications(100)).lower())

if __name__=='__main__':unittest.main()
