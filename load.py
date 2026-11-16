from db import q
import pandas as pd, numpy as np
from paths import data_path
data_path(".").mkdir(parents=True, exist_ok=True)
ins=q("""select i.instrument_id, i.ref_ticker, i.name, i.kind, i.is_delisted, i.sector, l.type_raw, l.code, coalesce(l.isin, x.isin) as isin
from v_instruments i join instrument x using(instrument_id) join listing l on l.instrument_id=i.instrument_id and l.exchange_code='WAR'
where i.exchange_code='WAR' and i.kind in ('stock','etf')""").drop_duplicates('instrument_id')
print(ins.type_raw.value_counts())
ids=tuple(int(x) for x in ins.instrument_id)
px=q("select instrument_id, date, open, high, low, close, adj_close, volume from daily_price where instrument_id = any(%(ids)s) order by instrument_id, date",{"ids":list(ids)})
print(len(px), px.date.min(), px.date.max())
ins.to_parquet(data_path('ins.parquet')); px.to_parquet(data_path('px.parquet'))
idx=q("select p.date, i.ref_ticker, p.close, p.adj_close from daily_price p join instrument i using(instrument_id) where i.ref_ticker in ('WIG.INDX','WIG20.INDX','MWIG40.INDX','SWIG80.INDX') order by 1")
idx.to_parquet(data_path('idx.parquet')); print(idx.groupby('ref_ticker').date.agg(['min','max','count']))

for table in ('split', 'dividend'):
    events=q(f"select * from {table} where instrument_id = any(%(ids)s)", {"ids":list(ids)})
    events.to_parquet(data_path('splits.parquet' if table=='split' else 'dividends.parquet'))
