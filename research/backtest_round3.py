"""Round 3: S&P 500 ETF on GPW (Yahoo series) and gold proxy; protocol in round3_plan.md."""
import sys,json,hashlib
from functools import lru_cache
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'research'))
import numpy as np
import pandas as pd
import sim as m
from paths import data_path
from execution import simulate
from baskets import basket_mask
from strategy_rules import risk_on
from backtest_hypotheses import BASE
from backtest_round2 import TREND

OUT=ROOT/'results/experiments3'
SP=22857                      # instrument_id of ETFSP500 (DB has XETRA bars only)
CLONES=[SP,SP+100000,SP+200000]  # identical columns: lets the engine fill three slots with one fund
YEARS=range(2010,2026)
COSTS=[.0039,.006]
FLOORS=[300000,50000]

def load_sp500(calendar):
 bars=pd.read_parquet(data_path('yf_war_etf.parquet'));bars=bars[bars.code=='ETFSP500'].set_index('date')
 bars=bars[~bars.index.duplicated()].reindex(calendar)
 divs=pd.read_parquet(data_path('yf_war_etf_dividends.parquet'));divs=divs[divs.code=='ETFSP500']
 return bars,divs

def add_clones(frame,series):
 return pd.concat([frame,pd.DataFrame({k:series for k in CLONES},index=frame.index)],axis=1)

def window_start_close(calendar,s):
 return calendar[calendar.get_loc(s)-1]

def bootstrap(diff,seed=20261116,draws=100000):
 rng=np.random.default_rng(seed);d=np.asarray(diff,float)
 means=d[rng.integers(0,len(d),(draws,len(d)))].mean(axis=1)
 return np.percentile(means,[5,95])

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 calendar=m.C.index
 bars,divs=load_sp500(calendar)
 close=bars.Close.where(bars.Close>0);opening=bars.Open.where(bars.Open>0);vol=bars.Volume.fillna(0)
 traded=close.notna()&(vol>0)
 turnover=(close*vol).where(traded).rolling(63,min_periods=40).median()
 C=add_clones(m.C,close);O=add_clones(m.O,opening);V=add_clones(m.V,vol)
 factors=pd.concat([m.SPLIT_FACTORS,pd.DataFrame(1.0,index=m.SPLIT_FACTORS.index,columns=CLONES)],axis=1)
 sp_div=pd.concat([pd.DataFrame(dict(instrument_id=k,ex_date=pd.to_datetime(divs.ex_date),unadjusted_value=divs.value,currency='PLN')) for k in CLONES])
 div=pd.concat([m.DIVIDENDS,sp_div],ignore_index=True)
 events=m.EVENTS.iloc[:0]
 def eligible(t,floor):return bool(traded.loc[t] and turnover.loc[t]>=floor)
 @lru_cache(maxsize=None)
 def stock_scores(t):
  if not risk_on(m.WIG,t):return pd.Series(dtype=float)
  u=m.universe(t,300000)&basket_mask('liquidity-21-140',t)
  x=m.SIG['combo'].loc[t][u].dropna()
  return x if len(x)>=5 else None
 @lru_cache(maxsize=None)
 def stock_half(y,cost):
  s,e=m.window(y)
  return simulate(m.C,m.O,m.V,m.SPLIT_FACTORS,m.DIVIDENDS,m.EVENTS,s,e,lambda t,value:stock_scores(t),3,6,cost,10000,21)
 rows=[]
 for cost in COSTS:
  for floor in FLOORS:
   for y in YEARS:
    s,e=m.window(y);t0=window_start_close(calendar,s)
    def hold(t,value,capital_unused=None):
     if t!=t0:return None
     return pd.Series({SP:1.}) if eligible(t,floor) else pd.Series(dtype=float)
    def switch(t,value):
     if risk_on(m.WIG,t):return stock_scores(t)
     return pd.Series({k:1. for k in CLONES}) if eligible(t,floor) else pd.Series(dtype=float)
    z_hold=simulate(C,O,V,factors,div,events,s,e,hold,1,1,cost,20000,21)
    z_half=simulate(C,O,V,factors,div,events,s,e,hold,1,1,cost,10000,21);other=stock_half(y,cost)
    z_sw=simulate(C,O,V,factors,div,events,s,e,switch,3,6,cost,20000,21)
    ok=eligible(t0,floor)
    for name,ret,trades,idle in [('hold_sp500',z_hold.value/20000-1,z_hold.trades,z_hold.trades==0),('mix50_sp500',(z_half.value+other.value)/20000-1,z_half.trades+other.trades,z_half.trades==0),('wig_sp500',z_sw.value/20000-1,z_sw.trades,False)]:
     rows.append(dict(variant=name,year=y,commission=cost,min_to=floor,ret=ret,trades=trades,sp_idle_at_start=bool(not ok),sp_actions=sum(a['action']=='buy' and a['instrument_id'] in CLONES for a in (z_sw.ledger if name=='wig_sp500' else z_hold.ledger))))
   print('SP500',cost,floor,flush=True)
 r=pd.DataFrame(rows);r.to_csv(OUT/'sp500_years.csv',index=False)
 base=pd.read_csv(ROOT/'results/experiments2/combined_years.csv')
 refs={'podium':BASE,'podium_ma200':TREND}
 summary=[]
 for (cost,floor,v),g in r.groupby(['commission','min_to','variant']):
  for label,sub in [('2010-2025',g),('floor_met_at_start',g[~g.sp_idle_at_start])]:
   if not len(sub):continue
   row=dict(commission=cost,min_to=floor,variant=v,sample=label,n=len(sub),mean=sub.ret.mean(),median=sub.ret.median(),worst=sub.ret.min(),best=sub.ret.max(),losses=int((sub.ret<0).sum()),idle_windows=int(sub.sp_idle_at_start.sum()))
   for key,ref in refs.items():
    b=base[(base.variant==ref)&(base.commission==cost)].set_index('year').ret.reindex(sub.year).values
    d=sub.ret.values-b;lo,hi=bootstrap(d)
    row.update({f'{key}_mean':b.mean(),f'diff_vs_{key}':d.mean(),f'ci90_lo_{key}':lo,f'ci90_hi_{key}':hi,f'wins_vs_{key}':int((d>0).sum())})
   summary.append(row)
 pd.DataFrame(summary).to_csv(OUT/'sp500_stats.csv',index=False)
 # Gold proxy (descriptive only).
 gp=pd.read_parquet(data_path('yf_gold_proxy.parquet'));gold=(gp.GOLD_USD*gp.USDPLN).dropna()
 podium=base[(base.variant==BASE)&(base.commission==.0039)].set_index('year').ret
 g_rows=[]
 for y in range(2003,2026):
  s,e=m.window(y);t0=window_start_close(calendar,s)
  g_rows.append(dict(year=y,gold_pln=gold.asof(e)/gold.asof(t0)-1,podium=podium[y],wig_above_ma200=bool(risk_on(m.WIG,t0)),wig=m.WIG.asof(e)/m.WIG.asof(t0)-1))
 gr=pd.DataFrame(g_rows);gr.to_csv(OUT/'gold_proxy_years.csv',index=False)
 worst=gr.nsmallest(5,'podium')
 gsum=dict(n=len(gr),mean=gr.gold_pln.mean(),median=gr.gold_pln.median(),worst=gr.gold_pln.min(),corr_podium=gr.gold_pln.corr(gr.podium),corr_wig=gr.gold_pln.corr(gr.wig),gold_mean_worst5_podium=worst.gold_pln.mean(),podium_mean_worst5=worst.podium.mean(),gold_mean_below_ma200=gr[~gr.wig_above_ma200].gold_pln.mean(),n_below_ma200=int((~gr.wig_above_ma200).sum()))
 (OUT/'gold_proxy_stats.json').write_text(json.dumps(gsum,indent=1)+'\n')
 files=['research/round3_plan.md','research/fetch_yf_etf.py','research/backtest_round3.py','execution.py','corporate.py','bt.py','baskets.py']
 meta=dict(outcomes=len(r),years='2010-2025',code_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files},input_sha256={p:hashlib.sha256(data_path(p).read_bytes()).hexdigest() for p in ['yf_war_etf.parquet','yf_war_etf_dividends.parquet','yf_gold_proxy.parquet','C.parquet','O.parquet','V.parquet']})
 (OUT/'manifest.json').write_text(json.dumps(meta,indent=2)+'\n')

GOLD=900001
GOLD_IDS=[GOLD,GOLD+100000,GOLD+200000]

def gold_main():
 calendar=m.C.index
 gp=pd.read_parquet(data_path('yf_gold_proxy.parquet'));pln=(gp.GOLD_USD*gp.USDPLN).dropna()
 pln=pln[~pln.index.duplicated()]
 close=pln.reindex(calendar.union(pln.index)).ffill().reindex(calendar)
 opening=close.shift(1)   # decision-time price: previous close, no look-ahead
 def with_gold(frame,series):return pd.concat([frame,pd.DataFrame({k:series for k in GOLD_IDS},index=frame.index)],axis=1)
 C=with_gold(m.C,close);O=with_gold(m.O,opening);V=with_gold(m.V,pd.Series(1e9,index=calendar))
 factors=pd.concat([m.SPLIT_FACTORS,pd.DataFrame(1.0,index=m.SPLIT_FACTORS.index,columns=GOLD_IDS)],axis=1)
 empty=m.DIVIDENDS.iloc[:0];events=m.EVENTS.iloc[:0]
 @lru_cache(maxsize=None)
 def stock_scores(t):
  if not risk_on(m.WIG,t):return pd.Series(dtype=float)
  u=m.universe(t,300000)&basket_mask('liquidity-21-140',t)
  x=m.SIG['combo'].loc[t][u].dropna()
  return x if len(x)>=5 else None
 @lru_cache(maxsize=None)
 def stock_half(y,cost):
  s,e=m.window(y)
  return simulate(m.C,m.O,m.V,m.SPLIT_FACTORS,m.DIVIDENDS,m.EVENTS,s,e,lambda t,value:stock_scores(t),3,6,cost,10000,21)
 rows=[]
 for cost in COSTS:
  for y in range(2003,2026):
   s,e=m.window(y);t0=window_start_close(calendar,s)
   hold=lambda t,value:pd.Series({GOLD:1.}) if t==t0 else None
   switch=lambda t,value:stock_scores(t) if risk_on(m.WIG,t) else pd.Series({k:1. for k in GOLD_IDS})
   zh=simulate(C,O,V,factors,empty,events,s,e,hold,1,1,cost,20000,21)
   zm=simulate(C,O,V,factors,empty,events,s,e,hold,1,1,cost,10000,21);other=stock_half(y,cost)
   zs=simulate(C,O,V,factors,empty,events,s,e,switch,3,6,cost,20000,21)
   for name,ret,trades in [('hold_gold',zh.value/20000-1,zh.trades),('mix50_gold',(zm.value+other.value)/20000-1,zm.trades+other.trades),('wig_gold',zs.value/20000-1,zs.trades)]:
    rows.append(dict(variant=name,year=y,commission=cost,ret=ret,trades=trades))
 r=pd.DataFrame(rows);r.to_csv(OUT/'gold_proxy_strategy_years.csv',index=False)
 base=pd.read_csv(ROOT/'results/experiments2/combined_years.csv');summary=[]
 for (cost,v),g in r.groupby(['commission','variant']):
  row=dict(commission=cost,variant=v,n=len(g),mean=g.ret.mean(),median=g.ret.median(),worst=g.ret.min(),best=g.ret.max(),losses=int((g.ret<0).sum()))
  for key,ref in {'podium':BASE,'podium_ma200':TREND}.items():
   b=base[(base.variant==ref)&(base.commission==cost)].set_index('year').ret.reindex(g.year).values
   d=g.ret.values-b;lo,hi=bootstrap(d)
   row.update({f'{key}_mean':b.mean(),f'{key}_worst':b.min(),f'diff_vs_{key}':d.mean(),f'ci90_lo_{key}':lo,f'ci90_hi_{key}':hi,f'wins_vs_{key}':int((d>0).sum())})
  summary.append(row)
 pd.DataFrame(summary).to_csv(OUT/'gold_proxy_strategy_stats.csv',index=False)

if __name__=='__main__':
 main();gold_main()
