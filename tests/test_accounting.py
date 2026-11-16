import unittest
import numpy as np
import pandas as pd
from corporate import split_prices, stable_ranking
from execution import simulate
from orders import quantity, price_limit, confirmed_limit


class AccountingTests(unittest.TestCase):
    def setUp(self):
        self.d=pd.bdate_range('2026-01-02',periods=6)
        self.c=pd.DataFrame({1:[100.]*6,2:[100.]*6},index=self.d)
        self.v=self.c*10
        self.f=self.c*0+1
        self.div=pd.DataFrame(columns=['instrument_id','ex_date','unadjusted_value','currency'])
        self.events=pd.DataFrame(columns=['instrument_id','date','action','price','source'])
    def run_model(self,c=None,o=None,score=None,n=1,step=1,capital=1000):
        c=self.c if c is None else c
        return simulate(c,c.copy() if o is None else o,self.v,self.f,self.div,self.events,
                        self.d[1],self.d[-1],score or (lambda t,value:pd.Series({1:1.})),n,1,0.,capital,step)
    def test_split_preserves_raw_portfolio_value_and_signal(self):
        self.c.loc[self.d[3]:,1]=10
        self.f.at[self.d[3],1]=10
        result=self.run_model()
        self.assertEqual(result.value,1000)
        self.assertEqual(result.positions[1],100)
        event=pd.DataFrame([dict(instrument_id=1,ex_date=self.d[3],ratio=10)])
        adj=self.c.copy();adj.loc[:self.d[2],1]=10
        signal,factor,blocked,checks=split_prices(self.c,adj,event)
        self.assertEqual(signal[1].nunique(),1)
        self.assertTrue(checks.accepted.all())
    def test_reverse_split(self):
        self.c.loc[self.d[3]:,1]=1000;self.f.at[self.d[3],1]=.1
        result=self.run_model();self.assertEqual(result.value,1000);self.assertEqual(result.positions[1],1)
    def test_purchase_uses_open_not_same_day_close(self):
        op=self.c.copy();op.at[self.d[1],1]=80
        result=self.run_model(o=op)
        self.assertEqual(result.positions[1],12);self.assertEqual(result.cash,40);self.assertEqual(result.value,1240)
    def test_missing_open_does_not_create_sale(self):
        op=self.c.copy();op.loc[self.d[2]:,1]=np.nan
        def scores(t,value):return pd.Series({1:1.}) if t==self.d[0] else pd.Series({2:1.})
        result=self.run_model(o=op,score=scores)
        self.assertIn(1,result.positions)
        self.assertFalse(any(x['action']=='sell' for x in result.ledger))
    def test_delisting_settlement_is_explicit(self):
        self.events=pd.DataFrame([dict(instrument_id=1,date=self.d[3],action='delist',price=90,source='test')])
        result=self.run_model();self.assertEqual(result.cash,900);self.assertNotIn(1,result.positions)
        self.assertEqual(result.trades,2)
    def test_suspension_prevents_sale_and_marks_freeze(self):
        self.events=pd.DataFrame([dict(instrument_id=1,date=self.d[2],action='suspend',price=np.nan,source='test')])
        self.c.loc[self.d[2]:,1]=20
        result=self.run_model();self.assertEqual(result.value,1000)
    def test_dividend_is_not_spendable_at_review(self):
        self.div=pd.DataFrame([dict(instrument_id=1,ex_date=self.d[2],unadjusted_value=10,currency='PLN')])
        def scores(t,value):return pd.Series({1:1.}) if t==self.d[0] else pd.Series({2:1.})
        result=self.run_model(score=scores)
        self.assertEqual(result.dividends,100);self.assertEqual(result.positions[2],10);self.assertEqual(result.value,1100)
    def test_whole_shares_and_commission_budget(self):
        q=quantity(2000,1091,.0039)
        self.assertEqual(q,1);self.assertLessEqual(q*1091*1.0039,2000)
    def test_bad_split_is_flagged_without_future_dependence(self):
        event=pd.DataFrame([dict(instrument_id=1,ex_date=self.d[3],ratio=10)])
        _,_,blocked,check=split_prices(self.c,self.c,event)
        self.assertFalse(check.accepted.any());self.assertFalse(blocked.loc[self.d[:3],1].any());self.assertTrue(blocked.loc[self.d[3]:,1].all())
        truncated=split_prices(self.c.iloc[:3],self.c.iloc[:3],event)
        pd.testing.assert_frame_equal(truncated[0],self.c.iloc[:3])
    def test_split_adjustment_does_not_rewrite_past(self):
        event=pd.DataFrame([dict(instrument_id=1,ex_date=self.d[3],ratio=10)])
        a=self.c.copy();c=self.c.copy();c.loc[self.d[3]:,1]=10
        full=split_prices(c,a,event)[0];short=split_prices(c.iloc[:3],a.iloc[:3],event)[0]
        pd.testing.assert_frame_equal(full.iloc[:3],short)
    def test_no_fill_when_daily_volume_is_zero(self):
        self.v[1]=0;result=self.run_model();self.assertEqual(result.trades,0);self.assertEqual(result.cash,1000)
    def test_ranking_ties_are_stable(self):
        self.assertEqual(list(stable_ranking(pd.Series({2:1.,1:1.})).index),[1,2])
    def test_tick_boundary_and_unknown_grid(self):
        self.assertEqual(price_limit(99,markup=.015,step=.5),100.5)
        ticks=pd.DataFrame([dict(isin_code='X',valid_from=pd.Timestamp('2026-01-01'),valid_to=pd.Timestamp('2026-12-31'),lower=100,upper=200,tick=.5,source='test')])
        self.assertEqual(confirmed_limit('X',99,.015,self.d[0],ticks),100.5)
        with self.assertRaises(ValueError):confirmed_limit('Y',99,.015,self.d[0],ticks)

if __name__=='__main__':unittest.main()
