from bt import *
import bt
years=range(1998,2026); MIN=300_000; COST=0.0039
w=wigret(years)
# 1) per-year detail for mom1 top5 / hi52 top5
for sig in ('mom1','hi52','mom12_1'):
    d=run(sig,5,MIN,COST,years); d['wig']=w.reindex(d.index); print(sig, d.round(3).T.to_string(), sep='\n')
# 2) one-day delayed entry (buy at close of first window day instead of formation close)
def hold_ret_lag(names,s,e,cost):
    seg=P.loc[s:e,names].ffill(); return (seg.iloc[-1]/seg.iloc[0]-1).mean()-cost
bt.hold_ret=hold_ret_lag
for sig in ('mom1','hi52','mom3','mom12_1'):
    for N in (3,5,10):
        d=run(sig,N,MIN,COST,years); ex=d.ret-w.reindex(d.index)
        print('LAG1',sig,N,'mean',round(d.ret.mean(),3),'median',round(d.ret.median(),3),'beatWIG',round((ex>0).mean(),2),'exWIG',round(ex.mean(),3))
