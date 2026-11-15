import pandas as pd, json
R=pd.read_csv('sim_years.csv'); R=R[R.year>=2003]
def stats(g):
    x=g.ret; ex=x-g.wig
    return pd.Series(dict(n=len(x),mean=x.mean(),median=x.median(),q10=x.quantile(.1),q90=x.quantile(.9),worst=x.min(),best=x.max(),
        beatWIG=(ex>0).mean(),loss=(x<0).mean(),p20=(x>.2).mean(),p40=(x>.4).mean(),p60=(x>.6).mean(),trades=g.trades.mean(),fees=g.fees.mean()))
S=R.groupby(['strat','cost']).apply(stats,include_groups=False).reset_index()
W=R[(R.strat=='spokojna')&(R.cost==0)][['year','wig']].rename(columns={'wig':'ret'}); W['wig']=W.ret; W['trades']=0; W['fees']=0
ws=stats(W)
H=R[R.cost==0.0039].assign(half=lambda d:(d.year>=2013).map({False:'2003-2012',True:'2013-2025'})).groupby(['strat','half']).apply(stats,include_groups=False).reset_index()
pd.set_option('display.width',250); print(S.round(3).to_string()); print(H.round(3).to_string()); print('WIG',ws.round(3).to_dict())
json.dump(dict(years=R.to_dict('records'),stats=S.to_dict('records'),halves=H.to_dict('records'),wigstats=ws.to_dict()),open('sim.json','w'),default=float)
