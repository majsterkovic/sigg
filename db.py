import os, psycopg, pandas as pd
from dotenv import load_dotenv
load_dotenv("/home/mariusz/projects/my-stock-portfolio/.env")
def q(sql, params=None):
    with psycopg.connect(os.environ["PG_DSN"], options="-c default_transaction_read_only=on") as c, c.cursor() as cur:
        cur.execute(sql, params)
        return pd.DataFrame(cur.fetchall(), columns=[d.name for d in cur.description])
