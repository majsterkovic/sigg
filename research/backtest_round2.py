"""Finite sensitivity grid from round2_plan.md; preserves the first series."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import hashlib,json
from functools import lru_cache
import numpy as np
import pandas as pd
import sim as m
from baskets import basket_mask
from corporate import stable_ranking
from execution import simulate
from strategy_rules import risk_on,choose_training_winner
from backtest_hypotheses import BASE,uncertainty,stats

OUT=ROOT/'results/experiments2'
TREND='combo|liquidity-21-140|trend'
CONFIGS=[(BASE,3,21,0,'combo'),(TREND,3,21,200,'combo')]
for n in [1,5]:
 for ma in [0,200]:CONFIGS.append((f'n{n}_ma{ma}',n,21,ma,'combo'))
for step in [10,42]:
 for ma in [0,200]:CONFIGS.append((f'step{step}_ma{ma}',3,step,ma,'combo'))
for ma in [100,300]:CONFIGS.append((f'ma{ma}',3,21,ma,'combo'))
for sig in ['combo6','combo_skip1']:CONFIGS.append((sig,3,21,200,sig))
SIGNALS=dict(m.SIG)
SIGNALS['combo6']=m.SIG['hi52'].rank(axis=1,pct=True)+(m.P/m.P.shift(126)-1).rank(axis=1,pct=True)
SIGNALS['combo_skip1']=m.SIG['hi52'].rank(axis=1,pct=True)+(m.P.shift(21)/m.P.shift(84)-1).rank(axis=1,pct=True)

@lru_cache(maxsize=None)
def ranked(t,ma,sig,n):
 if ma and not risk_on(m.WIG,t,ma):return pd.Series(dtype=float)
 u=m.universe(t,300000)&basket_mask('liquidity-21-140',t)
 x=stable_ranking(SIGNALS[sig].loc[t][u])
 return x if len(x)>=max(5,n) else None

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 rows=[]
 for cost in [.0039,.006]:
  for v,n,step,ma,sig in CONFIGS:
   for y in range(2003,2026):
    s,e=m.window(y)
    z=simulate(m.C,m.O,m.V,m.SPLIT_FACTORS,m.DIVIDENDS,m.EVENTS,s,e,lambda t,value:ranked(t,ma,sig,n),n,2*n,cost,20000,step)
    actions=[a['action'] for a in z.ledger]
    rows.append(dict(variant=v,year=y,commission=cost,n_positions=n,step=step,ma=ma,signal=sig,ret=z.value/20000-1,trades=z.trades,fees=z.fees,ending_cash=z.cash,stale_marks=actions.count('stale_mark'),unfilled_sells=actions.count('unfilled_sell')))
   print(cost,v,flush=True)
 r=pd.DataFrame(rows);r.to_csv(OUT/'stock_years.csv',index=False)
 first=pd.read_csv(ROOT/'results/experiments/years.csv')
 checks=r[r.variant.isin([BASE,TREND])].merge(first,on=['variant','year','commission'],suffixes=('_new','_old'))
 err=float((checks.ret_new-checks.ret_old).abs().max())
 assert len(checks)==92 and err<1e-10,(len(checks),err)
 combined=pd.concat([first,r[~r.variant.isin([BASE,TREND])]],ignore_index=True)
 combined.to_csv(OUT/'combined_years.csv',index=False)
 summaries=[]
 for (cost,v),g in r.groupby(['commission','variant']):
  for label,sub in [('all',g),('late',g[g.year>=2013])]:summaries.append(dict(commission=cost,variant=v,period=label,**stats(sub)))
 pd.DataFrame(summaries).to_csv(OUT/'stock_stats.csv',index=False)
 core=combined[combined.commission==.0039]
 for name,sub in [('all',core),('late',core[core.year>=2013])]:uncertainty(sub).to_csv(OUT/f'combined_paired_{name}.csv',index=False)
 wf=[]
 for cost,g in combined.groupby('commission'):
  for y in range(2013,2026):
   choice=choose_training_winner(core,y)
   ret=g[(g.year==y)&(g.variant==choice)].ret.iloc[0]
   base=g[(g.year==y)&(g.variant==BASE)].ret.iloc[0]
   wf.append(dict(commission=cost,year=y,selected=choice,ret=ret,baseline=base,gain=ret-base,training_last_year=y-1))
 pd.DataFrame(wf).to_csv(OUT/'combined_walk_forward.csv',index=False)
 files=['research/round2_plan.md','research/backtest_round2.py','research/strategy_rules.py','research/backtest_hypotheses.py','execution.py','bt.py','corporate.py','baskets.py','data/market_events.csv']
 meta=dict(configurations=14,new_configurations=12,simulations=len(r),combined_unique_configurations=core.variant.nunique(),baseline_max_error=err,seed=20261116,draws=100000,code_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files},input_sha256={p:hashlib.sha256(m.data_path(p).read_bytes()).hexdigest() for p in ['A.parquet','C.parquet','O.parquet','V.parquet','idx.parquet','splits.parquet','dividends.parquet']})
 (OUT/'stock_manifest.json').write_text(json.dumps(meta,indent=2)+'\n')

if __name__=='__main__':main()
