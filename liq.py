"""Liquidity floor tied to position size: turnover floor = liq_k * portfolio value / N, versus fixed 300 000 zl.
Both strategies, c=0.0039, windows 2003-2025."""
from sim import *
years=list(range(2003,2026)); w=wigret(years); c=0.0039
STRATS={'spokojna':('hi52',10,20),'podium':('combo',3,6)}
RULES=[None,5,10,20,50]
res=[]
for name,(sig,N,buf) in STRATS.items():
    for k in RULES:
        for y in years:
            r_,tr,fe=sim(sig,N,buf,c,y,liq_k=k); res.append(dict(strat=name,rule='fixed 300000' if k is None else f'k={k}',liq_k=k,year=y,ret=r_,trades=tr,fees=fe))
R=pd.DataFrame(res); R['wig']=R.year.map(w)
def stats(g):   # same definitions as athdma.py:stats
    x=g.ret
    return pd.Series(dict(mean=x.mean(),median=x.median(),q10=x.quantile(.1),worst=x.min(),best=x.max(),
        beatWIG=((x-g.wig)>0).mean(),loss=(x<0).mean(),p40=(x>.4).mean(),late=g[g.year>=2013].ret.mean(),trades=g.trades.mean()))
S=R.groupby(['strat','rule'],sort=False).apply(stats).reset_index()
pd.set_option('display.width',250); print(S.round(3).to_string()); print('WIG mean',round(w.mean(),3),'late',round(w[w.index>=2013].mean(),3))
S.to_csv('liq_stats.csv',index=False); R.to_csv('liq_years.csv',index=False)
