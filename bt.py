import pandas as pd, numpy as np, sys, os
SUF=os.environ.get('GPW_SUFFIX','')
from paths import data_path
from corporate import split_prices
A=pd.read_parquet(data_path(f'A{SUF}.parquet')); C=pd.read_parquet(data_path(f'C{SUF}.parquet')); V=pd.read_parquet(data_path(f'V{SUF}.parquet'))
# An explicit cutoff also makes truncated-history regression tests possible.
if os.environ.get('GPW_AS_OF'):
    cutoff = pd.Timestamp(os.environ['GPW_AS_OF'])
    A=A.loc[:cutoff]; C=C.loc[:cutoff]; V=V.loc[:cutoff]
if not (A.index.equals(C.index) and A.columns.equals(C.columns) and A.index.equals(V.index) and A.columns.equals(V.columns)):
    raise ValueError('A/C/V axes differ')
A=A.where(A>0); C=C.where(C>0)
idx=pd.read_parquet(data_path('idx.parquet')); idx['date']=pd.to_datetime(idx.date)
WIG=idx[idx.ref_ticker=='WIG.INDX'].set_index('date').close
splits=pd.read_parquet(data_path('splits.parquet'))
SPLIT_C, SPLIT_FACTORS, SPLIT_BLOCKED, SPLIT_CHECKS = split_prices(C,A,splits)
# Preserve genuine returns, including across gaps; never use the next close.
P=A.ffill()
r=P.pct_change(fill_method=None)
traded=C.notna()&(V>0)
TO=(C*V).where(traded)
med_to=TO.rolling(63,min_periods=40).median()
hist=A.notna().rolling(260,min_periods=1).sum()
def universe(t,min_to):
    return (med_to.loc[t]>=min_to)&(C.loc[t]>=1)&(hist.loc[t]>=250)&traded.loc[t]&~SPLIT_BLOCKED.loc[t]
def lag(n):   # value n sessions back
    return P.shift(n)
SIG={
 'mom12_1': P.shift(21)/P.shift(252)-1,
 'mom6_1' : P.shift(21)/P.shift(126)-1,
 'mom3'   : P/P.shift(63)-1,
 'mom1'   : P/P.shift(21)-1,
 'rev1'   : -(P/P.shift(21)-1),
 'hi52'   : (SPLIT_C/SPLIT_C.rolling(252,min_periods=200).max()).mask(SPLIT_BLOCKED),
 'lowvol' : -r.rolling(126,min_periods=100).std(),
}
SIG['mom12_1+hi52']=SIG['mom12_1'].rank(axis=1,pct=True)+SIG['hi52'].rank(axis=1,pct=True)
# Percentiles deliberately retain the original full-matrix population.
SIG['combo']=SIG['hi52'].rank(axis=1,pct=True)+SIG['mom3'].rank(axis=1,pct=True)
dates=P.index
def window(y):
    s=dates[dates>=pd.Timestamp(y,11,16)][0]; e=dates[dates<=pd.Timestamp(y+1,3,12)][-1]; return s,e
def hold_ret(names,s,e,cost):
    # formation at close of day before s, buy at close s-1 (approx), value at close e; delisted -> last price
    i0=dates.get_loc(s)-1; t0=dates[i0]
    seg=P.loc[t0:e,names].ffill()
    rr=(seg.iloc[-1]/seg.iloc[0]-1)
    return rr.mean()-cost
def run(sig,N,min_to,cost,years,rebal=None):
    out=[]
    for y in years:
        s,e=window(y); t0=dates[dates.get_loc(s)-1]
        if rebal is None:
            u=universe(t0,min_to); x=SIG[sig].loc[t0][u].dropna()
            if len(x)<max(N,20): continue
            names=x.nlargest(N).index
            out.append((y,hold_ret(names,s,e,cost),len(x)))
        else:
            seg=dates[(dates>=t0)&(dates<=e)]; v=1.0; cur=None
            pts=list(seg[::rebal])+[e]
            for a,b in zip(pts[:-1],pts[1:]):
                u=universe(a,min_to); x=SIG[sig].loc[a][u].dropna()
                names=set(x.nlargest(N).index)
                turn=1.0 if cur is None else len(names-cur)/N
                g=(P.loc[a:b,list(names)].ffill().iloc[-1]/P.loc[a,list(names)]-1).mean()
                v*=(1+g)*(1-cost*turn*(1 if cur is None else 2)); cur=names
            out.append((y,v-1,len(x)))
    return pd.DataFrame(out,columns=['y','ret','nuniv']).set_index('y')
def wigret(years):
    o={}
    for y in years:
        s,e=window(y); t0=dates[dates.get_loc(s)-1]; o[y]=WIG.asof(e)/WIG.asof(t0)-1
    return pd.Series(o)
def ew(min_to,years):
    o={}
    for y in years:
        s,e=window(y); t0=dates[dates.get_loc(s)-1]; u=universe(t0,min_to)
        o[y]=hold_ret(u[u].index,s,e,0)
    return pd.Series(o)
