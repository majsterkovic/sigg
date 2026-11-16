"""SIGG accounting: previous-close decisions, raw opens, integer buys.
No claim about auction capacity. Missing quotes freeze positions, never create fills.
"""
from bt import *
import json
from pathlib import Path
from paths import ROOT
from execution import simulate

O=pd.read_parquet(data_path(f'O{SUF}.parquet')).reindex(index=C.index,columns=C.columns)
# Compatibility for old research scripts only; this is not a cash-accounting price.
Oadj=O*(A/C)
DIVIDENDS=pd.read_parquet(data_path('dividends.parquet'))
DIVIDENDS['ex_date']=pd.to_datetime(DIVIDENDS.ex_date)
EVENTS=pd.read_csv(os.environ.get('SIGG_EVENTS_FILE', ROOT/'data/market_events.csv'))
EVENTS['date']=pd.to_datetime(EVENTS.date)
if EVENTS.duplicated(['instrument_id','date']).any():
    raise ValueError('Duplicate market event')
if len(EVENTS) and (EVENTS.source.isna().any() or EVENTS.source.str.strip().eq('').any()):
    raise ValueError('Every market event requires a source')
inside=EVENTS.date.between(C.index[0],C.index[-1])
if not EVENTS.loc[inside,'date'].isin(C.index).all():
    raise ValueError('Market event effective date must be a session in the dataset')


def simulate_window(sig,N,buffer,c,y,cap=20000.,step=21,min_to=300_000,liq_k=None,basket=None,min_n=None):
    s,e=window(y)
    def scores(t,value):
        floor=min_to if liq_k is None else liq_k*value/N
        u=universe(t,floor)
        if basket is not None: u=u&basket(t)
        x=SIG[sig].loc[t][u].dropna()
        return x if len(x)>=(max(3*N,20) if min_n is None else min_n) else None
    return simulate(C,O,V,SPLIT_FACTORS,DIVIDENDS,EVENTS,s,e,scores,N,buffer,c,cap,step)


def sim(sig,N,buffer,c,y,cap=20000.,step=21,min_to=300_000,liq_k=None,basket=None,min_n=None):
    out=simulate_window(sig,N,buffer,c,y,cap,step,min_to,liq_k,basket,min_n)
    return out.value/cap-1,out.trades,out.fees


if __name__ == '__main__':
    years=list(range(1998,2026)); w=wigret(years)
    STRATS={'spokojna':('hi52',10,20),'podium':('combo',3,6)}
    COSTS=[0.0,0.002,0.0039,0.006]
    res=[]
    for name,(sig,N,buf) in STRATS.items():
        for c in COSTS:
            for y in years:
                r,tr,fe=sim(sig,N,buf,c,y); res.append(dict(strat=name,cost=c,year=y,ret=r,trades=tr,fees=fe))
    R=pd.DataFrame(res)
    mix=R.pivot_table(index=['cost','year'],columns='strat',values='ret').reset_index()
    mix['ret']=0.5*mix.spokojna+0.5*mix.podium; mix['strat']='mix 50/50'
    R=pd.concat([R,mix[['strat','cost','year','ret']]],ignore_index=True)
    R['wig']=R.year.map(w)
    def stats(g):
        x=g.ret; ex=x-g.wig
        return pd.Series(dict(n=len(x),mean=x.mean(),median=x.median(),q10=x.quantile(.1),q90=x.quantile(.9),worst=x.min(),best=x.max(),
            beatWIG=(ex>0).mean(),loss=(x<0).mean(),p20=(x>.2).mean(),p40=(x>.4).mean(),p60=(x>.6).mean(),trades=g.get('trades',pd.Series(dtype=float)).mean(),fees=g.get('fees',pd.Series(dtype=float)).mean()))
    S=R.groupby(['strat','cost']).apply(stats).reset_index()
    H=R[R.cost==0.0039].groupby(['strat',R.year>=2013]).apply(stats).reset_index()
    pd.set_option('display.width',250); print(S.round(3).to_string()); print(H.round(3).to_string())
    wigS=stats(pd.DataFrame({'ret':w,'wig':w})); print('WIG',wigS.round(3).to_dict())
    R.to_csv('sim_years.csv',index=False); S.to_csv('sim_stats.csv',index=False)
    json.dump(dict(years=R.to_dict('records'),stats=S.to_dict('records'),halves=H.rename(columns={'year':'after2013'}).to_dict('records'),
      wig={int(k):float(v) for k,v in w.items()},wigstats=wigS.to_dict()),open('sim.json','w'),default=float)
