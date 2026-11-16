from paths import data_path
import pandas as pd, numpy as np
px=pd.read_parquet(data_path('px.parquet')); ins=pd.read_parquet(data_path('ins.parquet'))
px['date']=pd.to_datetime(px.date)
stk=set(ins.loc[ins.kind=='stock','instrument_id'])
px=px[px.instrument_id.isin(stk)]
A=px.pivot(index='date',columns='instrument_id',values='adj_close')
C=px.pivot(index='date',columns='instrument_id',values='close')
O=px.pivot(index='date',columns='instrument_id',values='open')
V=px.pivot(index='date',columns='instrument_id',values='volume')
r=A.pct_change(fill_method=None)
print('days',len(A),'stocks',A.shape[1])
big=(r.abs()>0.5).sum().sum(); print('daily |r|>50%:',big, ' >100%:',(r>1).sum().sum(), ' <= -0.9:',(r<-0.9).sum().sum())
# top offenders
s=r.stack(); s=s[s.abs()>1].sort_values()
print(s.head(10)); print(s.tail(10))
print('zero/neg adj:',(A<=0).sum().sum())
for n,d in dict(A=A,C=C,O=O,V=V).items(): d.to_parquet(data_path(f'{n}.parquet'))
