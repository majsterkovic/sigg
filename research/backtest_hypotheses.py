"""Run the fixed 12-configuration experiment in strategy_plan.md."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import argparse
import hashlib
import json
from functools import lru_cache
import numpy as np
import pandas as pd
import sim as market
from execution import simulate
from baskets import basket_mask
from corporate import stable_ranking
from strategy_rules import decorrelate,risk_on,choose_training_winner

BASE='combo|liquidity-21-140|base'
VARIANTS=[(signal,basket,rule) for signal in ['combo','mom3'] for basket in ['liquidity-21-140','main-proxy'] for rule in ['base','corr','trend']]
RETURNS=market.A.pct_change(fill_method=None).replace([np.inf,-np.inf],np.nan)

@lru_cache(maxsize=None)
def ranking(signal,basket,rule,t):
    if rule=='trend' and not risk_on(market.WIG,t):return pd.Series(dtype=float)
    u=market.universe(t,300000)&basket_mask(basket,t)
    x=stable_ranking(market.SIG[signal].loc[t][u])
    if len(x)<5:return None
    if rule=='corr':x=decorrelate(x,RETURNS.loc[:t].tail(126))
    return x


def run(commission):
    rows=[]
    for signal,basket,rule in VARIANTS:
        variant='|'.join([signal,basket,rule])
        for year in range(2003,2026):
            s,e=market.window(year)
            def scores(t,value):return ranking(signal,basket,rule,t)
            result=simulate(market.C,market.O,market.V,market.SPLIT_FACTORS,market.DIVIDENDS,market.EVENTS,
                            s,e,scores,3,6,commission,20000,21)
            actions=[x['action'] for x in result.ledger]
            rows.append(dict(variant=variant,signal=signal,basket=basket,rule=rule,year=year,
                commission=commission,ret=result.value/20000-1,trades=result.trades,fees=result.fees,
                ending_cash=result.cash,dividends=result.dividends,positions=len(result.positions),
                stale_marks=actions.count('stale_mark'),unfilled_sells=actions.count('unfilled_sell'),unfilled_buys=actions.count('unfilled_buy')))
        print(commission,variant,flush=True)
    return pd.DataFrame(rows)


def stats(g):
    x=g.ret
    return dict(n=len(x),mean=x.mean(),median=x.median(),worst=x.min(),best=x.max(),loss=(x<0).mean(),
                p20=(x>.2).mean(),p40=(x>.4).mean(),trades=g.trades.mean(),fees=g.fees.mean())


def uncertainty(r):
    p=r.pivot(index='year',columns='variant',values='ret');alts=[x for x in p if x!=BASE]
    d=p[alts].subtract(p[BASE],axis=0).values;n=len(p);rng=np.random.default_rng(20261116);draws=100000
    mean=d.mean(axis=0);se=d.std(axis=0,ddof=1)/np.sqrt(n);se=np.where(se>0,se,np.inf)
    obs=mean/se
    null_means=rng.choice([-1,1],size=(draws,n))@d/n
    null_se=np.sqrt(np.maximum(0,(np.square(d).sum(axis=0)-n*np.square(null_means))/(n-1)/n))
    null_t=np.divide(null_means,null_se,out=np.zeros_like(null_means),where=null_se>0)
    boot=d[rng.integers(0,n,size=(draws,n))].mean(axis=1);ci=np.quantile(boot,[.05,.95],axis=0)
    return pd.DataFrame([dict(variant=v,n=n,gain=mean[j],wins=int(sum(d[:,j]>0)),ci90_low=ci[0,j],ci90_high=ci[1,j],
        p_one_sided=(1+sum(null_t[:,j]>=obs[j]))/(draws+1),p_maxT=(1+sum(null_t.max(axis=1)>=obs[j]))/(draws+1)) for j,v in enumerate(alts)])


def main(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    results=pd.concat([run(.0039),run(.006)],ignore_index=True);results.to_csv(out/'years.csv',index=False)
    summaries=[]
    for (cost,variant),g in results.groupby(['commission','variant']):
        for period,sub in [('all',g),('early',g[g.year<=2012]),('late',g[g.year>=2013])]:
            summaries.append(dict(commission=cost,variant=variant,period=period,**stats(sub)))
    pd.DataFrame(summaries).to_csv(out/'stats.csv',index=False)
    core=results[results.commission==.0039]
    for period,r in [('all',core),('late',core[core.year>=2013])]:uncertainty(r).to_csv(out/f'paired_{period}.csv',index=False)
    wf=[]
    for cost,g in results.groupby('commission'):
        for y in range(2013,2026):
            # Choose from baseline-cost training only, even in cost stress test.
            choice=choose_training_winner(core,y)
            row=g[(g.year==y)&(g.variant==choice)].iloc[0]
            baseline=g[(g.year==y)&(g.variant==BASE)].ret.iloc[0]
            wf.append(dict(year=y,commission=cost,selected=choice,ret=row.ret,baseline=baseline,gain=row.ret-baseline,
                           training_last_year=y-1,training_mean=core[(core.year<y)&(core.variant==choice)].ret.mean()))
    pd.DataFrame(wf).to_csv(out/'walk_forward.csv',index=False)
    # Regression: benchmark must reproduce the already-published model.
    archived=pd.read_csv(ROOT/'results/seg_years.csv')
    archived=archived[(archived.min_to==300000)&(archived.basket=='płynność 21–140 (proxy)')&(archived.strat=='podium (combo, 3)')]
    merged=core[core.variant==BASE].merge(archived,on='year',suffixes=('_new','_saved'))
    error=float((merged.ret_new-merged.ret_saved).abs().max())
    if len(merged)!=23 or error>1e-10:raise AssertionError(f'Baseline mismatch: {error}')
    metadata=dict(baseline=BASE,baseline_max_error=error,variants=len(VARIANTS),windows=23,costs=[.0039,.006],
        protocol_sha256=hashlib.sha256((ROOT/'research/strategy_plan.md').read_bytes()).hexdigest(),
        seed=20261116,draws=100000,note='Retrospective expanding-window validation, not a previously unseen holdout. No competitor returns; no top-3 probability.')
    metadata['input_sha256']={name:hashlib.sha256(market.data_path(name).read_bytes()).hexdigest()
        for name in ['A.parquet','C.parquet','O.parquet','V.parquet','idx.parquet','splits.parquet','dividends.parquet']}
    metadata['code_sha256']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
        for name in ['research/backtest_hypotheses.py','research/strategy_rules.py','execution.py','bt.py','sim.py','baskets.py','corporate.py','data/market_events.csv']}
    (out/'manifest.json').write_text(json.dumps(metadata,indent=2)+'\n')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',default=str(ROOT/'results/experiments'));a=ap.parse_args();main(a.out)
