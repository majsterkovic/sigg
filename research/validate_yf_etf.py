"""Compare Yahoo (.WA) bars with the database for the 7 ETFs tested in round 2."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np,pandas as pd
from paths import data_path
CODES=['ETFBW20TR','ETFBM40TR','ETFBS80TR','ETFBSPXPL','ETFBNDXPL','ETFBTBSP','ETFBCASH']
def main():
 meta=pd.read_csv(data_path('etf_metadata.csv')).set_index('code');px=pd.read_parquet(data_path('etf_px.parquet'));px.date=pd.to_datetime(px.date)
 y=pd.read_parquet(data_path('yf_war_etf.parquet'));rows=[]
 for c in CODES:
  d=px[px.instrument_id==int(meta.instrument_id[c])].set_index('date');g=y[y.code==c].set_index('date')
  j=d.join(g,how='inner',rsuffix='_yf');j=j[j.index<=d.index.max()]
  rel=lambda a,b:(a/b-1).abs()
  rows.append(dict(code=c,common_sessions=len(j),db_only=len(d)-len(j),close_diff_gt_0_5pct=int((rel(j.close,j.Close)>.005).sum()),open_diff_gt_0_5pct=int((rel(j.open,j.Open)>.005).sum()),volume_diff_gt_20pct=int((rel(j.volume,j.Volume.replace(0,np.nan))>.2).sum()),max_close_diff=float(rel(j.close,j.Close).max())))
 r=pd.DataFrame(rows);out=ROOT/'results/experiments3';out.mkdir(parents=True,exist_ok=True);r.to_csv(out/'yf_vs_db.csv',index=False)
 bad=(r.close_diff_gt_0_5pct+r.open_diff_gt_0_5pct)/r.common_sessions
 print(r.to_string());assert (bad<=.01).all(),'Yahoo source rejected by protocol'
if __name__=='__main__':main()
