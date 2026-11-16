from paths import data_path
import pandas as pd
idx=pd.read_parquet(data_path('idx.parquet')); idx['date']=pd.to_datetime(idx.date)
cal=pd.DatetimeIndex(sorted(idx[idx.ref_ticker=='WIG.INDX'].date.unique()))
A=pd.read_parquet(data_path('A.parquet'))
cnt=A.notna().sum(axis=1)
keep=cal.intersection(A.index)
# also drop WIG days where almost nothing priced (data holes)
med=cnt.loc[keep].rolling(21,min_periods=5).median()
bad=keep[(cnt.loc[keep]<0.5*med).values]
print('calendar days',len(keep),'dropped non-session rows',len(A.index.difference(keep)),'holes',len(bad), list(bad[:20].date))
keep=keep.difference(bad)
for n in 'ACOV':
    d=pd.read_parquet(data_path(f'{n}.parquet')).reindex(keep); d.to_parquet(data_path(f'{n}.parquet'))
