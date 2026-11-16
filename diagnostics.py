"""Publish aggregate data-quality limitations, not raw market bars."""
import argparse
import json
from pathlib import Path
import pandas as pd
from sim import SPLIT_CHECKS, EVENTS, C, simulate_window


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',default='results/model.json');a=ap.parse_args();out=Path(a.out)
    SPLIT_CHECKS.to_csv(out.with_name('split_checks.csv'),index=False)
    stale=[]
    for name,sg,n,buffer in [('spokojna','hi52',10,20),('podium','combo',3,6)]:
        for year in range(2003,2026):
            r=simulate_window(sg,n,buffer,.0039,year)
            for x in r.ledger:
                if x['action'] in ('stale_mark','unfilled_sell','unfilled_buy'):
                    stale.append(dict(strategy=name,year=year,action=x['action'],instrument_id=x['instrument_id'],date=str(pd.Timestamp(x['date']).date())))
    pd.DataFrame(stale,columns=['strategy','year','action','instrument_id','date']).to_csv(out.with_name('execution_warnings.csv'),index=False)
    result=dict(model='raw-pln-integer-deferred-dividends-v2',snapshot_last=str(C.index[-1].date()),
        split_events_checked=len(SPLIT_CHECKS),split_events_rejected=int((~SPLIT_CHECKS.accepted).sum()),
        explicit_market_events=len(EVENTS),historical_market_events_complete=False,
        execution_warnings=len(stale),auction_volume_verified=False,tick_assignments_verified=False,
        nc_classification='static 2021–2024 list, not point-in-time',
        historical_game_instruments_known=False,
        fractional_holdings='Purchases are integer. Splits may create fractions; no inferred cash-in-lieu settlement.',
        dividend_entitlement='Overnight holdings on ex-date; no independent settlement-calendar validation.',
        corporate_validation='Split factor is cross-checked on ex-date using A/C; unresolved events block new entries for 252 sessions. Source revisions remain possible.')
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n');print(json.dumps(result,indent=2))
