from db import q
import pandas as pd
pd.set_option('display.width',250)
print(q("""select f.source, count(distinct f.instrument_id) n_inst, min(f.period_end), max(f.period_end), count(*) n
from fundamental_statement f join listing l on l.instrument_id=f.instrument_id and l.exchange_code='WAR' group by 1"""))
print(q("""select f.line_item, count(distinct f.instrument_id) n from fundamental_statement f join listing l on l.instrument_id=f.instrument_id and l.exchange_code='WAR'
where f.line_item ilike any(array['%%NetIncome%%','%%EPS%%','%%Earnings%%','%%StockholdersEquity%%']) group by 1 order by 2 desc limit 12"""))
print(q("""select period_type, count(*) from fundamental_statement f join listing l on l.instrument_id=f.instrument_id and l.exchange_code='WAR' group by 1"""))
