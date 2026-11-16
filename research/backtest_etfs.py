"""Real GPW ETF history; does not splice WIGtech into bond returns."""
import sys,json,hashlib
from functools import lru_cache
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
import pandas as pd
import sim as m
from paths import data_path
from corporate import split_prices
from execution import simulate
from baskets import basket_mask
from strategy_rules import risk_on
from etf_rules import mask_policy_history,etf_choice,CASH_START

OUT=ROOT/'results/experiments2'
EQUITY_CODES=['ETFBW20TR','ETFBM40TR','ETFBS80TR','ETFBSPXPL','ETFBNDXPL']

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 meta=pd.read_csv(data_path('etf_metadata.csv'));px=pd.read_parquet(data_path('etf_px.parquet'));px.date=pd.to_datetime(px.date)
 ids=meta.set_index('code').instrument_id;cash_id=int(ids.ETFBCASH);equities=[int(ids[k]) for k in EQUITY_CODES]
 tested=equities+[cash_id,int(ids.ETFBTBSP)]
 calendar=m.C.index
 frames={name:px.pivot(index='date',columns='instrument_id',values=col).reindex(calendar).astype(float) for name,col in [('C','close'),('A','adj_close'),('O','open'),('V','volume')]}
 raw=frames['C'];rawV=frames['V']
 # Inventory derived summaries only; no raw vendor bars enter the repository.
 inv=[]
 for row in meta.itertuples():
  k=row.instrument_id;g=px[px.instrument_id==k]
  available=k in raw
  valid=(raw[k]>0)&(rawV[k]>0) if available else None
  turnover=(raw[k]*rawV[k]).where(valid).tail(63).median() if available else np.nan
  status='WAR_PLN' if available else ('foreign_primary' if pd.notna(row.code) else 'no_WAR_mapping')
  inv.append(dict(instrument_id=k,isin=row.isin,code=row.code,name=row.name,ref_ticker=row.ref_ticker,currency=row.currency,status=status,in_game=True,first_bar=g.date.min() if len(g) else pd.NaT,last_bar=g.date.max() if len(g) else pd.NaT,bars=len(g),median_turnover63=turnover,passes300k=bool(turnover>=300000),tested=k in tested,policy_start=CASH_START if k==cash_id else pd.NaT))
 pd.DataFrame(inv).to_csv(OUT/'etf_inventory.csv',index=False)
 for name in frames:frames[name]=mask_policy_history(frames[name][tested],cash_id)
 C,A,O,V=[frames[x] for x in ['C','A','O','V']]
 C=C.where(C>0);A=A.where(A>0)
 splits=pd.read_parquet(data_path('etf_split.parquet'));_,factors,blocked,checks=split_prices(C,A,splits)
 checks.to_csv(OUT/'etf_split_checks.csv',index=False)
 div=pd.read_parquet(data_path('etf_dividend.parquet'));div=div[div.instrument_id.isin(tested)].copy();div.ex_date=pd.to_datetime(div.ex_date)
 # All ETF selection uses t-1; missing current bar blocks entry.
 traded=C.notna()&(V>0)
 turnover=(C*V).where(traded).rolling(63,min_periods=40).median()
 count=A.notna().rolling(64,min_periods=1).sum()
 mom=A/A.shift(63)-1
 events=m.EVENTS.iloc[:0]
 rows=[];trade_rows=[]
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
 variants=[('hold_'+code,code,range(2022,2026)) for code in EQUITY_CODES+['ETFBTBSP']]
 variants += [('hold_ETFBCASH','ETFBCASH',range(2024,2026)),('mom3','mom3',range(2022,2026)),('positive','positive',range(2022,2026)),('positive_cash','positive_cash',range(2024,2026)),('wig_cash','wig_cash',range(2024,2026)),('mix50','mix50',range(2024,2026))]
 for cost in [.0039,.006]:
  for floor in [300000,50000]:
   for variant,rule,years in variants:
    for y in years:
     s,e=m.window(y);t0=calendar[calendar.get_loc(s)-1];capital=10000 if rule=='mix50' else 20000
     def scores(t,value):
      eligible=traded.loc[t]&(turnover.loc[t]>=floor)&~blocked.loc[t]
      if variant.startswith('hold_'):
       k=int(ids[rule])
       if t!=t0:return None
       return pd.Series({k:1.}) if eligible[k] else pd.Series(dtype=float)
      eligible=eligible&(count.loc[t]>=64)
      return etf_choice(mom.loc[t],eligible,equities,cash_id,'positive_cash' if rule=='mix50' else rule,risk_on(m.WIG,t))
     z=simulate(C,O,V,factors,div,events,s,e,scores,1,1,cost,capital,21)
     other=stock_half(y,cost) if rule=='mix50' else None
     actions=[a['action'] for a in z.ledger]
     row=dict(variant=variant,year=y,commission=cost,min_to=floor,ret=(z.value+(other.value if other else 0))/20000-1,trades=z.trades+(other.trades if other else 0),fees=z.fees+(other.fees if other else 0),ending_cash=z.cash+(other.cash if other else 0),bcash_buys=sum(a['action']=='buy' and a['instrument_id']==cash_id for a in z.ledger),etf_trades=z.trades,stale_marks=actions.count('stale_mark'),unfilled_sells=actions.count('unfilled_sell'),unfilled_buys=actions.count('unfilled_buy'))
     rows.append(row)
     for a in z.ledger:
      if a['action'] in ['buy','sell']:
       trade_rows.append(dict(variant=variant,year=y,commission=cost,min_to=floor,action=a['action'],date=a['date'],code=meta.set_index('instrument_id').at[a['instrument_id'],'code']))
    print('ETF',cost,floor,variant,flush=True)
 r=pd.DataFrame(rows);r.to_csv(OUT/'etf_years.csv',index=False);pd.DataFrame(trade_rows).to_csv(OUT/'etf_trade_choices.csv',index=False)
 summaries=[]
 for (cost,floor,v),g in r.groupby(['commission','min_to','variant']):
  for period,sub in [('2022-2025',g[g.year>=2022]),('2024-2025',g[g.year>=2024])]:
   # Never mislabel a two-year sample as four years.
   if period=='2022-2025' and len(sub)!=4:continue
   summaries.append(dict(commission=cost,min_to=floor,variant=v,period=period,n=len(sub),mean=sub.ret.mean(),median=sub.ret.median(),worst=sub.ret.min(),best=sub.ret.max(),loss=int(sum(sub.ret<0)),p40=(sub.ret>.4).mean(),trades=sub.trades.mean(),fees=sub.fees.mean(),bcash_buys=sub.bcash_buys.sum(),idle_windows=int(sum(sub.trades==0))))
 pd.DataFrame(summaries).to_csv(OUT/'etf_stats.csv',index=False)
 files=['research/round2_plan.md','research/load_etfs.py','research/backtest_etfs.py','research/etf_rules.py','execution.py','corporate.py','bt.py','baskets.py']
 metadata=dict(outcomes=len(r),gpw_series=20,inventory_isins=32,tested_isins=7,data_through=str(px.date.max().date()),bcash_policy_start=str(CASH_START.date()),source='private read-only marketdata; EODHD WAR listing, primary currency PLN; not independently reconciled',code_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files},input_sha256={p:hashlib.sha256(data_path(p).read_bytes()).hexdigest() for p in ['etf_metadata.csv','etf_px.parquet','etf_split.parquet','etf_dividend.parquet','C.parquet','O.parquet','V.parquet','A.parquet','idx.parquet','splits.parquet','dividends.parquet']})
 (OUT/'etf_manifest.json').write_text(json.dumps(metadata,indent=2)+'\n')
 print('Saved',len(r),'outcomes',flush=True)

if __name__=='__main__':main()
