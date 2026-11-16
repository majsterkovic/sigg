import sys,unittest
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'research'))
from etf_rules import mask_policy_history,etf_choice
from execution import simulate

class EtfResearchTests(unittest.TestCase):
 def test_old_wigtech_cannot_supply_bond_momentum(self):
  idx=pd.bdate_range('2023-10-01','2024-05-01')
  original=pd.DataFrame({1:100.,2:200.},index=idx)
  x=mask_policy_history(original,1)
  self.assertTrue(x.loc[:'2024-01-01',1].isna().all())
  self.assertEqual(original.iloc[0,0],100.)
  mom=x/x.shift(63)-1
  self.assertTrue(mom.loc[:'2024-03-28',1].isna().all())
  self.assertEqual(mom.loc['2024-04-15',1],0.)
  pd.testing.assert_series_equal(x[2],original[2])
 def test_missing_or_illiquid_cash_is_not_a_fallback(self):
  mom=pd.Series({1:-.1,2:.01});eligible=pd.Series({1:True,2:False})
  self.assertTrue(etf_choice(mom,eligible,[1],2,'positive_cash').empty)
  eligible[2]=True;mom[2]=float('nan')
  self.assertTrue(etf_choice(mom,eligible,[1],2,'positive_cash').empty)
 def test_regime_switch_invests_full_single_slot_next_open(self):
  dates=pd.bdate_range('2024-04-01',periods=4)
  close=pd.DataFrame({1:100.,2:50.},index=dates)
  opening=close.copy();opening.loc[dates[2],2]=60.
  def scores(t,value):
   return etf_choice(pd.Series({1:.2,2:.01}),pd.Series({1:True,2:True}),[1],2,'wig_cash',risk_on=t==dates[0])
  emptydiv=pd.DataFrame(columns=['ex_date']);emptyevents=pd.DataFrame(columns=['date'])
  z=simulate(close,opening,close*0+10000,close*0+1,emptydiv,emptyevents,dates[1],dates[2],scores,1,1,0,20000,1)
  self.assertEqual(z.positions,{2:333})
  self.assertEqual(z.cash,20.)
  self.assertEqual([a['action'] for a in z.ledger],['buy','sell','buy'])
 def test_positive_equity_wins_and_ties_are_deterministic(self):
  m=pd.Series({3:.2,1:.2,2:.5});ok=pd.Series({1:True,2:True,3:True})
  self.assertEqual(etf_choice(m,ok,[3,1],2,'positive_cash').index.tolist(),[1,3])

if __name__=='__main__':unittest.main()
