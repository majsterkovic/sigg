import os, psycopg, pandas as pd
from dotenv import load_dotenv
if os.environ.get("SIGG_ENV_FILE"):
    load_dotenv(os.environ["SIGG_ENV_FILE"])
def q(sql, params=None):
    with psycopg.connect(os.environ["PG_DSN"], options="-c default_transaction_read_only=on") as c, c.cursor() as cur:
        cur.execute(sql, params)
        return pd.DataFrame(cur.fetchall(), columns=[d.name for d in cur.description])
