from bt import *
import numpy as np, pandas as pd
# Monthly panel: rebalance every 21 sessions, all months 2001-2026, long-only topN vs EW universe
def panel(sig,N,min_to,cost,start='2001-01-01',step=21):
    ds=dates[dates>=start]; pts=ds[::step]
    out=[]; cur=None
    for a,b in zip(pts[:-1],pts[1:]):
        u=universe(a,min_to); x=SIG[sig].loc[a][u].dropna()
        if len(x)<max(3*N,20): cur=None; continue
        names=set(x.nlargest(N).index); allu=list(x.index)
        seg=P.loc[a:b].ffill()
        g=(seg.loc[b,list(names)]/seg.loc[a,list(names)]-1).mean()
        m=(seg.loc[b,allu]/seg.loc[a,allu]-1).mean()
        turn=1.0 if cur is None else len(names-cur)/N
        out.append((a,g-2*cost*turn,m)); cur=names
    d=pd.DataFrame(out,columns=['d','ret','ew']).set_index('d'); d['ex']=d.ret-d.ew; return d
def tstat(x): return x.mean()/x.std(ddof=1)*np.sqrt(len(x))
rows=[]
for sig in ['mom1','rev1','mom3','mom12_1','hi52','lowvol']:
  for N in (5,10):
    for MIN in (300_000,1_000_000):
      d=panel(sig,N,MIN,0.0039)
      for lab,dd in (('all',d),('2001-12',d[:'2012']),('2013-26',d['2013':])):
        rows.append(dict(sig=sig,N=N,minTO=MIN,per=lab,n=len(dd),ex_m=dd.ex.mean(),t=tstat(dd.ex),hit=(dd.ex>0).mean(),ann=(1+dd.ret).prod()**(12/len(dd))-1,ann_ew=(1+dd.ew).prod()**(12/len(dd))-1))
R=pd.DataFrame(rows); pd.set_option('display.width',250); pd.set_option('display.max_rows',300)
print(R.round(3).to_string()); R.to_csv('run3.csv')
