import sys,unittest
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'research'))
from execution import simulate

class CloneColumnTests(unittest.TestCase):
 def frames(self,ids):
  idx=pd.bdate_range('2020-01-01',periods=30)
  price=pd.Series([100.+i for i in range(30)],index=idx)
  return [pd.DataFrame({k:v for k in ids},index=idx) for v in (price,price.shift(1).bfill(),pd.Series(1e6,index=idx))],idx
 def test_three_clones_match_single_full_slot_up_to_rounding(self):
  (c,o,v),idx=self.frames([1]);(c3,o3,v3),_=self.frames([1,2,3])
  f=pd.DataFrame(1.,index=idx,columns=[1]);f3=pd.DataFrame(1.,index=idx,columns=[1,2,3])
  empty=pd.DataFrame(columns=['instrument_id','ex_date','unadjusted_value','currency']);ev=pd.DataFrame(columns=['instrument_id','date','action'])
  s,e=idx[2],idx[-1]
  one=simulate(c,o,v,f,empty,ev,s,e,lambda t,x:pd.Series({1:1.}) if t==idx[1] else None,1,1,.0039,20000,21)
  three=simulate(c3,o3,v3,f3,empty,ev,s,e,lambda t,x:pd.Series({1:1.,2:1.,3:1.}) if t==idx[1] else None,3,6,.0039,20000,21)
  self.assertEqual(three.trades,3)
  self.assertAlmostEqual(one.value/20000,three.value/20000,delta=.01)
if __name__=='__main__':unittest.main()
