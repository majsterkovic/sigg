from db import q
import pandas as pd, numpy as np
ins=q("""select i.instrument_id, i.ref_ticker, i.name, i.kind, i.is_delisted, i.sector, l.type_raw, l.code
from v_instruments i join listing l on l.instrument_id=i.instrument_id and l.exchange_code='WAR'
where i.exchange_code='WAR' and i.kind in ('stock','etf')""").drop_duplicates('instrument_id')
print(ins.type_raw.value_counts())
ids=tuple(int(x) for x in ins.instrument_id)
px=q("select instrument_id, date, open, high, low, close, adj_close, volume from daily_price where instrument_id = any(%(ids)s) order by instrument_id, date",{"ids":list(ids)})
print(len(px), px.date.min(), px.date.max())
ins.to_parquet('ins.parquet'); px.to_parquet('px.parquet')
idx=q("select p.date, i.ref_ticker, p.close, p.adj_close from daily_price p join instrument i using(instrument_id) where i.ref_ticker in ('WIG.INDX','WIG20.INDX','MWIG40.INDX','SWIG80.INDX') order by 1")
idx.to_parquet('idx.parquet'); print(idx.groupby('ref_ticker').date.agg(['min','max','count']))
