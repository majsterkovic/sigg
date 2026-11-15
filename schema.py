from db import q
import pandas as pd
pd.set_option('display.width',250); pd.set_option('display.max_rows',300); pd.set_option('display.max_colwidth',60)
t=q("""select table_schema, table_name, (xpath('/row/c/text()', query_to_xml('select count(*) as c from '||table_schema||'.'||table_name, false, true, '')))[1]::text::bigint as n
from information_schema.tables where table_schema not in ('pg_catalog','information_schema') order by 1,2""")
print(t)
c=q("""select table_name, string_agg(column_name||':'||data_type, ', ' order by ordinal_position) cols from information_schema.columns
where table_schema='public' group by 1 order by 1""")
for r in c.itertuples(): print(r.table_name, '->', r.cols)
