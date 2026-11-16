import unittest
import numpy as np
import pandas as pd
from research.strategy_rules import decorrelate,risk_on,choose_training_winner
from execution import simulate


class HypothesesTests(unittest.TestCase):
    def test_correlated_stocks_are_replaced_by_independent_candidate(self):
        rng=np.random.default_rng(42);x=rng.normal(size=126);z=rng.normal(size=126)
        returns=pd.DataFrame({1:x,2:x,3:z})
        selected=decorrelate(pd.Series({1:3.,2:2.,3:1.}),returns)
        self.assertEqual(list(selected.index),[1,3])
    def test_missing_overlap_is_not_assumed_uncorrelated(self):
        returns=pd.DataFrame({1:np.arange(126,dtype=float),2:[np.nan]*50+list(range(76))})
        self.assertEqual(list(decorrelate(pd.Series({1:2.,2:1.}),returns).index),[1])
    def test_market_filter_uses_only_prior_closes(self):
        days=pd.bdate_range('2020-01-01',periods=205);wig=pd.Series(np.arange(205)+100.,index=days)
        t=days[199];original=risk_on(wig,t)
        wig.loc[days[200]:]=0
        self.assertEqual(risk_on(wig,t),original)
        self.assertFalse(risk_on(wig,days[100]))
    def test_training_winner_cannot_see_test_year(self):
        r=pd.DataFrame([dict(year=y,variant=v,ret=value) for y,v,value in [(2011,'a',.1),(2011,'b',.2),(2012,'a',.1),(2012,'b',.2),(2013,'a',5),(2013,'b',-1)]])
        self.assertEqual(choose_training_winner(r,2013),'b')
        r.loc[r.year==2013,'ret']=[-100,100]
        self.assertEqual(choose_training_winner(r,2013),'b')
    def test_risk_off_liquidates_on_next_open_and_stays_cash_until_review(self):
        d=pd.bdate_range('2020-01-01',periods=8)
        c=pd.DataFrame({1:[10.]*8},index=d);o=c.copy();o.at[d[3],1]=12
        div=pd.DataFrame(columns=['ex_date']);events=pd.DataFrame(columns=['date'])
        scores=lambda t,value:pd.Series({1:1.}) if t==d[0] else pd.Series(dtype=float)
        result=simulate(c,o,c*10,c*0+1,div,events,d[1],d[-1],scores,3,6,0.,300.,2)
        buys=[x for x in result.ledger if x['action']=='buy'];sells=[x for x in result.ledger if x['action']=='sell']
        self.assertEqual(len(buys),1);self.assertEqual(len(sells),1);self.assertEqual(sells[0]['date'],d[3])
        self.assertEqual(result.positions,{});self.assertEqual(result.cash,320.)

if __name__=='__main__':unittest.main()
