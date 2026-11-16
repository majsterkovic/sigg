"""Extend a DB snapshot using Yahoo and an explicit session calendar.

Never rewrites DB rows. Median agreement is not proof of per-day agreement:
all outliers, base-date deviations, O/V discrepancies and stale runs are recorded.
"""
import argparse
import hashlib
import json
import numpy as np
import pandas as pd
from paths import data_path


def extend(through,sessions):
    mats={n:pd.read_parquet(data_path(f'{n}.parquet')) for n in 'ACOV'}
    A,C,O,V=(mats[n] for n in 'ACOV');last=C.index[-1];through=pd.Timestamp(through)
    calendar=pd.DatetimeIndex(pd.to_datetime(pd.read_csv(sessions).date)).sort_values()
    if calendar.has_duplicates or through not in calendar:raise ValueError('Invalid calendar or endpoint')
    new=calendar[(calendar>last)&(calendar<=through)].astype(C.index.dtype)
    if len(new)==0:raise ValueError('Nothing to extend')
    yf=pd.read_parquet(data_path('yf_px.parquet'));yf.date=pd.to_datetime(yf.date).astype(C.index.dtype)
    if yf.duplicated(['instrument_id','date']).any():raise ValueError('Duplicate Yahoo bars')
    # Every expected session needs broad coverage. A calendar hole cannot disappear silently.
    counts=yf[yf.close>0].groupby('date').instrument_id.nunique().reindex(new,fill_value=0)
    if (counts < .5*yf.instrument_id.nunique()).any():raise ValueError(f'Yahoo session coverage too small: {counts[counts<.5*yf.instrument_id.nunique()].to_dict()}')
    ins=pd.read_parquet(data_path('ins.parquet')).set_index('instrument_id')
    extended={n:m.reindex(m.index.append(new)) for n,m in mats.items()}
    checks=[];outliers=[]
    for iid,g in yf.groupby('instrument_id'):
        if iid not in C:continue
        g=g.set_index('date').sort_index();ov=g.loc[:last];ov=ov[ov.index.isin(C.index)]
        db=C[iid].reindex(ov.index);dev=(ov.close/db-1).abs().replace([np.inf,-np.inf],np.nan).dropna()
        shared=ov.index[(ov.adj_close>0)&db.gt(0)&A[iid].reindex(ov.index).gt(0)]
        base=shared[-1] if len(shared) else None
        gn=g.reindex(new)
        base_dev=float(abs(g.at[base,'close']/C.at[base,iid]-1)) if base is not None else np.nan
        reason=''
        if len(dev)<5:reason='fewer than 5 overlap days'
        elif dev.median()>.01:reason='median deviation > 1%'
        elif base_dev>.01:reason='base deviation > 1%'
        elif base is None:reason='no common adjusted base'
        elif (gn.volume.fillna(0)<=0).all():reason='stale: no positive volume'
        elif gn.close.dropna().nunique()<=1:reason='stale: constant close'
        # Local stale/no-volume runs are left unavailable, rather than fed to signals.
        stale=gn.volume.fillna(0).le(0)
        for d in dev.index[dev>.01]:
            outliers.append(dict(instrument_id=iid,date=d,field='close',db=db.at[d],yahoo=ov.at[d,'close'],relative_error=dev.at[d]))
        for field,m in [('open',O),('volume',V)]:
            b=m[iid].reindex(ov.index);error=(ov[field]/b-1).abs().replace([np.inf,-np.inf],np.nan)
            for d in error.index[error>.01]:outliers.append(dict(instrument_id=iid,date=d,field=field,db=b.at[d],yahoo=ov.at[d,field],relative_error=error.at[d]))
        if not reason:
            for n,field in [('C','close'),('O','open'),('V','volume')]:extended[n].loc[new,iid]=gn[field].mask(stale).values
            extended['A'].loc[new,iid]=(A.at[base,iid]*gn.adj_close/g.at[base,'adj_close']).mask(stale).values
        checks.append(dict(instrument_id=iid,ticker=ins.at[iid,'ref_ticker'],accepted=not bool(reason),reason=reason,
            n_overlap=len(dev),median_deviation=dev.median(),max_deviation=dev.max(),q95_deviation=dev.quantile(.95),
            base_date=base,base_deviation=base_dev,new_rows=int(gn.close.notna().sum()),positive_volume=int((gn.volume>0).sum())))
    # Missing and rejected instruments remain NaN on every extension day.
    validation=pd.DataFrame(checks)
    validation.to_csv(data_path('yf_validation.csv'),index=False)
    pd.DataFrame(outliers,columns=['instrument_id','date','field','db','yahoo','relative_error']).to_csv(data_path('yf_outliers.csv'),index=False)
    for n,m in extended.items():m.to_parquet(data_path(f'{n}_x.parquet'))
    report=dict(database_cutoff=str(last.date()),through=str(through.date()),new_sessions=[str(d.date()) for d in new],
        accepted=int(validation.accepted.sum()),rejected=int((~validation.accepted).sum()),
        overlap_outliers=len(outliers),warning='Overlap agreement is not an independent validation of new sessions; see yf_outliers.csv',
        sha256={f'{n}_x.parquet':hashlib.sha256(data_path(f'{n}_x.parquet').read_bytes()).hexdigest() for n in 'ACOV'})
    data_path('yf_check.json').write_text(json.dumps(report,indent=2))
    data_path('yf_check.txt').write_text(json.dumps(report,indent=2)+'\n'+validation[~validation.accepted].to_string(index=False)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--through',required=True)
    ap.add_argument('--sessions',required=True,help='CSV with date column from the exchange calendar')
    a=ap.parse_args();extend(a.through,a.sessions)
