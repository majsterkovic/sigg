from bt import *
from run3_lib import panel, tstat
years=range(1998,2026)
SIG['hi52+mom3']=SIG['hi52'].rank(axis=1,pct=True)+SIG['mom3'].rank(axis=1,pct=True)
w=wigret(years)
for cost in (0.0,0.0039):
  for sig,N in (('hi52',10),('mom3',5),('mom1',5),('rev1',10)):
    d=panel(sig,N,300_000,cost); print(f'panel cost={cost} {sig} top{N} ex/m={d.ex.mean():.4f} t={tstat(d.ex):.2f}')
  for sig,N,reb in (('hi52',10,None),('hi52+mom3',5,21),('mom3',3,21)):
    d=run(sig,N,300_000,cost,years,rebal=reb); ex=d.ret-w.reindex(d.index)
    print(f'window cost={cost} {sig} top{N} {"hold" if reb is None else "monthly"} mean={d.ret.mean():.3f} beatWIG={(ex>0).mean():.2f} p30={(d.ret>0.3).mean():.2f}')
