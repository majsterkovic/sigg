from db import q
import pandas as pd
pd.set_option('display.width',250); pd.set_option('display.max_rows',200); pd.set_option('display.max_colwidth',90)
print(q("select exchange_code, count(*) from listing where country_iso2='PL' or exchange_code in ('WAR','WSE') group by 1 order by 2 desc"))
print(q("""select kind, is_delisted, count(*), min(first_date), max(last_date), sum(case when n_days>500 then 1 else 0 end) n500
from v_instruments where exchange_code in ('WAR') group by 1,2 order by 1,2"""))
print(q("select ref_ticker,name,first_date,last_date,n_days from v_instruments where ref_ticker ilike any(array['WIG%%','%%WIG%%']) and kind ilike '%%ind%%' order by 1 limit 30"))
print(q("select * from v_data_cutoff"))
print(q("select table_name,column_name,source,tier,pit_safe,cutoff_date,obs_from,obs_to,left(notes,90) notes from v_data_catalog"))
