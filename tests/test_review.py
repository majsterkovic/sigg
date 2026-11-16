"""Operational review tests use synthetic data, with no DB or private snapshot."""
import importlib.util
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch
import pandas as pd


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.day=pd.Timestamp('2026-11-13');self.ids=list(range(1,16))
        self.isins=[f'PL{i:010d}' for i in self.ids]
        meta=pd.DataFrame(dict(instrument_id=self.ids,isin=self.isins,ref_ticker=[f'T{i}.WAR' for i in self.ids]))
        meta.to_parquet(self.root/'ins.parquet')
        (self.root/'game.txt').write_text(' '.join(self.isins))
        pd.DataFrame({'date':['2026-11-13','2026-11-16','2026-11-17']}).to_csv(self.root/'sessions.csv',index=False)
        prices=pd.DataFrame(10.,index=[self.day],columns=self.ids)
        scores=pd.DataFrame([list(range(15,0,-1))],index=[self.day],columns=self.ids,dtype=float)
        bt=types.ModuleType('bt')
        for name,value in dict(C=prices,V=prices,P=prices,SIG={k:scores for k in ['hi52','mom3','combo']},med_to=prices*100000,
                               universe=lambda t,floor:pd.Series(True,index=self.ids),data_path=lambda name:self.root/name).items():setattr(bt,name,value)
        baskets=types.ModuleType('baskets');baskets.basket_mask=lambda name,t:pd.Series(True,index=self.ids);baskets.size_rank=lambda t:pd.Series(range(21,36),index=self.ids)
        spec=importlib.util.spec_from_file_location('review_picks',Path(__file__).parents[1]/'picks.py');self.module=importlib.util.module_from_spec(spec)
        with patch.dict('sys.modules',{'bt':bt,'baskets':baskets}):spec.loader.exec_module(self.module)
        self.args=self.module.parser().parse_args(['--as-of','2026-11-13','--trade-date','2026-11-16','--strategy','podium','--instruments',str(self.root/'game.txt'),'--sessions',str(self.root/'sessions.csv')])
    def tearDown(self):self.tmp.cleanup()
    def test_initial_list_filters_game_and_budgets(self):
        rank,orders,summary=self.module.build(self.args)
        self.assertEqual(list(orders[orders.role=='buy'].instrument_id),[1,2,3]);self.assertLessEqual(summary['podium']['estimated_buy_cost'],20000)
        self.assertFalse(summary['podium']['limits_confirmed'])
    def test_hold_buffer_and_use_actual_free_cash(self):
        held=pd.DataFrame([dict(strategy='podium',instrument_id=5,shares=100),dict(strategy='podium',instrument_id=14,shares=100)])
        held.to_csv(self.root/'held.csv',index=False);self.args.holdings=str(self.root/'held.csv');self.args.cash=500
        _,orders,summary=self.module.build(self.args)
        self.assertEqual(list(orders[orders.action=='keep'].instrument_id),[5]);self.assertEqual(list(orders[orders.action=='sell'].instrument_id),[14])
        self.assertEqual(len(orders[orders.action=='buy']),2);self.assertTrue(summary['podium']['conditional_on_sales'])
        self.assertLessEqual(summary['podium']['estimated_buy_cost'],500+1000*(1-.0039))
    def test_full_portfolio_has_no_new_orders(self):
        pd.DataFrame([dict(strategy='podium',instrument_id=k,shares=10) for k in [1,2,3]]).to_csv(self.root/'held.csv',index=False)
        self.args.holdings=str(self.root/'held.csv');self.args.cash=500
        _,orders,summary=self.module.build(self.args)
        self.assertEqual(set(orders.action),{'keep'});self.assertEqual(summary['podium']['estimated_buy_cost'],0)
    def test_suspended_position_stays_in_portfolio(self):
        before=self.module.C.copy();before.index=[self.day-pd.Timedelta(days=1)]
        self.module.C=pd.concat([before,self.module.C]);self.module.C.at[self.day,14]=float('nan')
        pd.DataFrame([dict(instrument_id=14,date='2026-11-13',action='suspend',price=float('nan'),source='test')]).to_csv(self.root/'events.csv',index=False)
        pd.DataFrame([dict(strategy='podium',instrument_id=14,shares=10)]).to_csv(self.root/'held.csv',index=False)
        self.args.events=str(self.root/'events.csv');self.args.holdings=str(self.root/'held.csv');self.args.cash=500
        _,orders,_=self.module.build(self.args)
        self.assertEqual(list(orders[orders.action=='keep'].instrument_id),[14])
        self.assertNotIn(14,orders[orders.action=='sell'].instrument_id.tolist())
    def test_intervening_session_rejected(self):
        self.args.trade_date='2026-11-17'
        with self.assertRaises(ValueError):self.module.build(self.args)
    def test_empty_universe_leaves_cash(self):
        self.module.universe=lambda t,floor:pd.Series(False,index=self.ids)
        rank,orders,summary=self.module.build(self.args)
        self.assertTrue(orders.empty);self.assertEqual(summary['podium']['status'],'insufficient_universe');self.assertEqual(summary['podium']['estimated_cash_left'],20000)
    def test_missing_held_quote_never_proposes_sale(self):
        pd.DataFrame([dict(strategy='podium',instrument_id=5,shares=100)]).to_csv(self.root/'held.csv',index=False)
        self.args.holdings=str(self.root/'held.csv');self.args.cash=500;self.module.C.at[self.day,5]=float('nan')
        with self.assertRaises(ValueError):self.module.build(self.args)

if __name__=='__main__':unittest.main()
