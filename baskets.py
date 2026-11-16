"""Explicitly named liquidity proxies, not historical index membership."""
import pandas as pd
from paths import reference_path
from bt import C, TO, hist, traded

NC=set(pd.read_csv(reference_path('nc_ids.csv')).instrument_id)
TO12=TO.rolling(252,min_periods=120).median()

def size_rank(t):
    ok=(~C.columns.isin(NC))&(hist.loc[t]>=250)&traded.loc[t]&(C.loc[t]>=1)
    return TO12.loc[t].where(ok).rank(ascending=False,method='first')

def basket_mask(name,t):
    if name=='all':return pd.Series(True,index=C.columns)
    if name=='main-proxy':return pd.Series(~C.columns.isin(NC),index=C.columns)
    if name=='liquidity-21-140':return size_rank(t).between(21,140)
    raise ValueError(f'Unknown basket: {name}')
