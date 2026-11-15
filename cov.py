import pandas as pd
A=pd.read_parquet('A.parquet'); C=pd.read_parquet('C.parquet'); V=pd.read_parquet('V.parquet')
for y in range(2010,2022):
    t=A.index[A.index<=pd.Timestamp(y,11,13)][-1]
    w=slice(t-pd.Timedelta(days=90),t)
    print(y,t.date(),'priced',int(A.loc[t].notna().sum()),'vol>0',int((V.loc[t]>0).sum()),'volNaN',int(V.loc[t].isna().sum()),
      'med TO>=300k',int(((C*V).loc[w].median()>=3e5).sum()), 'medianTO all', round(float((C*V).loc[w].median().median()),0))
