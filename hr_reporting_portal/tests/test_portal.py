import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from generate_demo import generate
from portal import load_csv,report,summary,audit

class TestPortal(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.db=Path(self.tmp.name)/'test.db';csv=generate(Path(self.tmp.name)/'demo.csv',50)
        self.assertEqual(load_csv(self.db,csv),50)
    def tearDown(self):self.tmp.cleanup()
    def test_import(self):self.assertEqual(summary(self.db)['employees'],50)
    def test_reports(self):self.assertEqual(sum(x['headcount'] for x in report(self.db,'headcount')),50)
    def test_role_gate(self):
        with self.assertRaises(PermissionError):report(self.db,'compensation','analyst')
        self.assertGreater(len(report(self.db,'compensation','manager')),0)
    def test_audit(self):
        report(self.db,'attrition',actor='testuser')
        self.assertEqual(audit(self.db)[0]['actor'],'testuser')
        with self.assertRaises(PermissionError):audit(self.db,'analyst')
    def test_unknown_report(self):
        with self.assertRaises(ValueError):report(self.db,'DROP TABLE employees')
if __name__=='__main__':unittest.main()
