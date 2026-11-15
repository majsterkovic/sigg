"""SIGG window simulation: signal at close t-1, trade at open t, value at close of last day.
Commission c on each traded value. Monthly review every 21 sessions with a hold buffer."""
from bt import *
import json
O=pd.read_parquet(f'O{SUF}.parquet')
fac=(P/A)                       # clean-index / adj ratio
Oadj=(O*(A/C))*fac              # open on the clean index scale
SIG['combo']=SIG['hi52'].rank(axis=1,pct=True)+SIG['mom3'].rank(axis=1,pct=True)
def sim(sig,N,buffer,c,y,cap=20000.0,step=21,min_to=300_000,liq_k=None):
    s,e=window(y); i0=dates.get_loc(s)
    seg=dates[(dates>=s)&(dates<=e)]
    reviews=list(seg[::step])
    cash=cap; pos={}; trades=0; fees=0.0
    def px_open(d,k):
        v=Oadj.at[d,k] if k in Oadj.columns else np.nan
        return v if np.isfinite(v) and v>0 else P.loc[:d,k].ffill().iloc[-1]
    for d in reviews:
        t=dates[dates.get_loc(d)-1]
        if liq_k is not None:   # floor tied to the slot: value at the close before the review
            held=P.loc[:t].ffill().iloc[-1]
            min_to=liq_k*(cash+sum(q*held[k] for k,q in pos.items()))/N
        u=universe(t,min_to); x=SIG[sig].loc[t][u].dropna()
        if len(x)<max(3*N,20): continue
        rank=x.rank(ascending=False)
        keep={k for k in pos if k in rank.index and rank[k]<=buffer}
        sell=[k for k in pos if k not in keep]
        for k in sell:
            v=pos.pop(k)*px_open(d,k); cash+=v*(1-c); fees+=v*c; trades+=1
        want=[k for k in x.nlargest(N+len(keep)).index if k not in keep][:N-len(keep)]
        if want:
            per=cash/len(want)
            for k in want:
                p=px_open(d,k); spend=per/(1+c); pos[k]=spend/p; cash-=per; fees+=spend*c; trades+=1
    last=P.loc[:e].ffill().iloc[-1]
    val=cash+sum(q*last[k] for k,q in pos.items())
    return val/cap-1, trades, fees
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
