from bt import *
import bt
years=range(1998,2026); MIN=300_000; COST=0.0039
SIG['hi52+mom3']=SIG['hi52'].rank(axis=1,pct=True)+SIG['mom3'].rank(axis=1,pct=True)
w=wigret(years); rows=[]
for sig in ('hi52','mom3','hi52+mom3','mom12_1'):
  for N in (1,3,5,10):
    for reb in (None,21):
      d=run(sig,N,MIN,COST,years,rebal=reb); x=d.ret; ex=x-w.reindex(x.index)
      rows.append(dict(sig=sig,N=N,reb='hold' if reb is None else 'monthly',n=len(x),mean=x.mean(),median=x.median(),q10=x.quantile(.1),q90=x.quantile(.9),beatWIG=(ex>0).mean(),exWIG=ex.mean(),p30=(x>0.3).mean(),p50=(x>0.5).mean()))
R=pd.DataFrame(rows); pd.set_option('display.width',250)
print(R.round(3).to_string()); R.to_csv('run4.csv')
