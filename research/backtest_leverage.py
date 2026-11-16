"""Synthetic 2x daily-reset funds on mWIG40 and WIG20; protocol in round3_plan.md (last addendum)."""
import sys,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'research'))
import numpy as np,pandas as pd
import sim as m
from paths import data_path
from strategy_rules import risk_on
from backtest_hypotheses import BASE
from backtest_round2 import TREND
from backtest_round3 import bootstrap
OUT=ROOT/'results/experiments3'
DIV={'MWIG40.INDX':.025,'WIG20.INDX':.027}
FIRST={'MWIG40.INDX':2011,'WIG20.INDX':2003}
COMMISSION=.0039

def index_returns(ticker):
 i=pd.read_parquet(data_path('idx.parquet'));i['date']=pd.to_datetime(i.date)
 s=i[i.ref_ticker==ticker].set_index('date').close;s=s[~s.index.duplicated()]
 return s.reindex(m.C.index.union(s.index)).ffill().reindex(m.C.index).pct_change()

def synthetic(r,ticker,cost):
 return 2*(r+DIV[ticker]/252)-cost/252

def calibrate():
 """One-dimensional fit of c so that 2xWIG20 matches ETFBW20LV cumulative return."""
 meta=pd.read_csv(data_path('etf_metadata.csv')).set_index('code');px=pd.read_parquet(data_path('etf_px.parquet'));px.date=pd.to_datetime(px.date)
 real=px[px.instrument_id==int(meta.instrument_id['ETFBW20LV'])].set_index('date').adj_close;real=real[~real.index.duplicated()]
 r=index_returns('WIG20.INDX');days=real.index.intersection(r.index)[1:]
 target=real.reindex(real.index).loc[days[0]:days[-1]];target=target.iloc[-1]/real.loc[:days[0]].iloc[-1]-1
 lo,hi=0.,.2
 for _ in range(60):
  c=(lo+hi)/2;cum=(1+synthetic(r.loc[days],'WIG20.INDX',c)).prod()-1
  lo,hi=(c,hi) if cum>target else (lo,c)
 return c,target

def window_value(rets,y,ma200,start=20000.):
 s,e=m.window(y);days=m.C.index[(m.C.index>=s)&(m.C.index<=e)];reviews=set(days[::21]);v=start;invested=False;cash=start;
 value=start
 for d in days:
  t=m.C.index[m.C.index.get_loc(d)-1]
  if d in reviews:
   want=risk_on(m.WIG,t) if ma200 else True
   if want and not invested:value=value/(1+COMMISSION);invested=True
   elif not want and invested:value=value*(1-COMMISSION);invested=False
  if invested:value*=1+rets.at[d]
 return value/start-1

def stats_row(g,base,extra):
 row=dict(extra,n=len(g),mean=g.ret.mean(),median=g.ret.median(),worst=g.ret.min(),best=g.ret.max(),losses=int((g.ret<0).sum()))
 for key,ref in {'podium':BASE,'podium_ma200':TREND}.items():
  b=base[(base.variant==ref)&(base.commission==COMMISSION)].set_index('year').ret.reindex(g.year).values
  d=g.ret.values-b;lo,hi=bootstrap(d)
  row.update({f'{key}_mean':b.mean(),f'{key}_worst':b.min(),f'diff_vs_{key}':d.mean(),f'ci90_lo_{key}':lo,f'ci90_hi_{key}':hi,f'wins_vs_{key}':int((d>0).sum())})
 return row

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 c0,target=calibrate();print('calibrated c=%.4f target cum=%.3f'%(c0,target),flush=True)
 base=pd.read_csv(ROOT/'results/experiments2/combined_years.csv')
 # out-of-sample check on ETFBM40LV
 meta=pd.read_csv(data_path('etf_metadata.csv')).set_index('code');px=pd.read_parquet(data_path('etf_px.parquet'));px.date=pd.to_datetime(px.date)
 real=px[px.instrument_id==int(meta.instrument_id['ETFBM40LV'])].set_index('date').adj_close;real=real[~real.index.duplicated()]
 r40=index_returns('MWIG40.INDX');days=real.index.intersection(r40.index)[1:]
 real_cum=real.iloc[-1]/real.iloc[0]-1;syn_cum=(1+synthetic(r40.loc[days],'MWIG40.INDX',c0)).prod()-1
 rr=real.pct_change().loc[days];corr=rr.corr(synthetic(r40.loc[days],'MWIG40.INDX',c0))
 val=dict(calibrated_cost=c0,etfbw20lv_cumulative=target,etfbm40lv_real_cumulative=real_cum,etfbm40lv_synthetic_cumulative=syn_cum,etfbm40lv_days=len(days),etfbm40lv_daily_corr=corr)
 rows=[]
 for ticker,label in [('MWIG40.INDX','mwig40'),('WIG20.INDX','wig20')]:
  r=index_returns(ticker)
  for cost in [.03,c0,.10]:
   rets=synthetic(r,ticker,cost)
   for ma in [False,True]:
    for y in range(FIRST[ticker],2026):
     rows.append(dict(index=label,cost=cost,variant=f'lev_{"ma200" if ma else "hold"}',year=y,ret=window_value(rets,y,ma)))
 res=pd.DataFrame(rows);res.to_csv(OUT/'leverage_years.csv',index=False)
 summary=[]
 for (idx,cost,v),g in res.groupby(['index','cost','variant']):
  summary.append(stats_row(g,base,dict(index=idx,cost=cost,variant=v)))
 pd.DataFrame(summary).to_csv(OUT/'leverage_stats.csv',index=False)
 (OUT/'leverage_validation.json').write_text(json.dumps(val,indent=1)+'\n')
 print(json.dumps(val,indent=1))

if __name__=='__main__':main()
