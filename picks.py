"""Repeatable SIGG ranking and a cash-constrained review, with explicit dates."""
import argparse
import os
import json
import re
from pathlib import Path
import numpy as np
import pandas as pd
from bt import C, V, P, SIG, med_to, universe, data_path
from paths import ROOT, reference_path
from corporate import stable_ranking
from baskets import basket_mask, size_rank
from orders import price_limit, quantity, confirmed_limit

STRATS={'spokojna':('hi52',10,20),'podium':('combo',3,6)}


def instrument_ids(path,meta):
    isins=set(re.findall(r'\b[A-Z]{2}[A-Z0-9]{9}\d\b',Path(path).read_text()))
    if not isins:raise ValueError('Empty ISIN list')
    if 'isin' not in meta:raise ValueError('Re-run load.py: ins.parquet must contain ISIN')
    return set(meta.index[meta['isin'].isin(isins)])


def build(args):
    t=pd.Timestamp(args.as_of) if args.as_of else C.index[-1]
    if t not in C.index:raise ValueError('Signal date must be a session in the dataset')
    trade_date=pd.Timestamp(args.trade_date)
    calendar=pd.DatetimeIndex(pd.to_datetime(pd.read_csv(args.sessions).date))
    if t not in calendar or trade_date not in calendar or calendar[calendar>t].empty or calendar[calendar>t][0]!=trade_date:
        raise ValueError('Trade date must be the next exchange session after the signal')
    if trade_date<=t:raise ValueError('Trade date must follow the signal date')
    # Do not silently use an old signal if the snapshot has an intervening session.
    if len(C.index[(C.index>t)&(C.index<trade_date)]):raise ValueError('Signal is not the preceding session')
    meta=pd.read_parquet(data_path('ins.parquet')).set_index('instrument_id')
    game=instrument_ids(args.instruments,meta)
    if args.holdings and args.strategy=='both':raise ValueError('Select one --strategy for a portfolio review')
    held=pd.read_csv(args.holdings) if args.holdings else pd.DataFrame(columns=['strategy','instrument_id','shares'])
    if not set(held.strategy).issubset(STRATS):raise ValueError('Unknown holdings strategy')
    if held.duplicated(['strategy','instrument_id']).any() or (held.shares<=0).any():raise ValueError('Invalid/duplicate holdings')
    if len(held) and (not np.isfinite(held.shares).all() or not held.instrument_id.isin(C.columns).all()):raise ValueError('Invalid holdings')
    ticks=pd.read_csv(args.ticks).rename(columns={'isin':'isin_code'}) if args.ticks else None
    if ticks is not None:
        ticks.valid_from=pd.to_datetime(ticks.valid_from);ticks.valid_to=pd.to_datetime(ticks.valid_to)
    events=pd.read_csv(args.events)
    events['date']=pd.to_datetime(events.date)
    states={}
    for event in events[events.date<=trade_date].sort_values('date').itertuples():
        if pd.isna(event.source) or not str(event.source).strip():raise ValueError('Market event needs a source')
        if event.action not in ('suspend','resume','delist'):raise ValueError('Unknown market event')
        states[int(event.instrument_id)]=(event.action,event.date)
    unavailable={k for k,(action,d) in states.items() if action in ('suspend','delist')}
    ranks=[];orders=[];summaries={}
    for strategy,(sig,n,buffer) in STRATS.items():
        if args.strategy!='both' and strategy!=args.strategy:continue
        pos=held[held.strategy==strategy].set_index('instrument_id').shares.to_dict()
        if len(pos)>n:raise ValueError('More holdings than strategy slots')
        # Each strategy is a separate alternative portfolio, never a combined order.
        cash=args.cash if args.holdings else args.capital
        if cash is None or cash<0 or not np.isfinite(cash):raise ValueError('--cash is required with --holdings')
        held_close={}
        for k,q in pos.items():
            state,event_date=states.get(k,('resume',None))
            if state=='delist':raise ValueError(f'{k}: confirm forced settlement and cash before review')
            if state=='suspend':
                earlier=C.loc[C.index<event_date,k].dropna()
                if earlier.empty:raise ValueError(f'{k}: missing pre-suspension valuation')
                held_close[k]=float(earlier.iloc[-1])
            else:
                if pd.isna(C.at[t,k]) or not V.at[t,k]>0:raise ValueError(f'{strategy}: missing quote for held instrument {k}; resolve event/data gap')
                held_close[k]=float(C.at[t,k])
        floor=args.fixed if args.liq_k is None else args.liq_k*(cash+sum(q*held_close[k] for k,q in pos.items()))/n
        if not np.isfinite(floor) or floor<0:raise ValueError('Cannot value holdings; resolve stale quotes first')
        u=universe(t,floor)&basket_mask(args.basket,t)&C.columns.isin(game)&~C.columns.isin(unavailable)
        # Current is_delisted is not used to filter historical snapshots.
        x=stable_ranking(SIG[sig].loc[t][u]);rank={k:i for i,k in enumerate(x.index,1)}
        status='ready' if len(x)>=n+2 else 'insufficient_universe'
        for k in x.index:
            ranks.append(dict(strategy=strategy,rank=rank[k],instrument_id=k,ticker=meta.at[k,'ref_ticker'][:-4],isin=meta.at[k,'isin'],
                signal_date=t.date(),trade_date=trade_date.date(),close=float(C.at[t,k]),hi52=SIG['hi52'].at[t,k],mom3=SIG['mom3'].at[t,k],
                combo=SIG['combo'].at[t,k],med_turnover_63=med_to.at[t,k],size_rank=size_rank(t).get(k),floor=floor))
        keep={};sale_cash=0.;sale_rows=[]
        for k,q in pos.items():
            action='keep' if k in unavailable or status!='ready' or rank.get(k,np.inf)<=buffer else 'sell'
            row=dict(strategy=strategy,action=action,role=action,instrument_id=k,ticker=meta.at[k,'ref_ticker'][:-4],isin=meta.at[k,'isin'],shares=q,
                     close=held_close[k],limit=np.nan,amount=q*held_close[k],estimated=True,limit_confirmed=False)
            if action=='keep':keep[k]=q
            else:sale_cash+=q*held_close[k]*(1-args.commission);sale_rows.append(row)
            orders.append(row)
        slots=max(0,n-len(keep));budget=cash+sale_cash;per=budget/slots if slots else 0.;spent=0.;buys=0;reserves=0
        if status=='ready' and slots>0:
            for k in x.index:
                if k in keep:continue
                close=float(C.at[t,k]);isin=meta.at[k,'isin']
                # Tick metadata is mandatory to label an executable limit as confirmed.
                limit=confirmed_limit(isin,close,args.markup,trade_date,ticks) if ticks is not None else price_limit(close,args.markup)
                q=quantity(per,limit,args.commission)
                if q<1:continue
                if buys<slots:role='buy';buys+=1;spent+=q*limit*(1+args.commission)
                elif reserves<5:role='reserve';reserves+=1
                else:break
                orders.append(dict(strategy=strategy,action=role,role=role,instrument_id=k,ticker=meta.at[k,'ref_ticker'][:-4],isin=isin,
                    rank=rank[k],shares=q,close=close,limit=limit,amount=q*limit,estimated=True,limit_confirmed=ticks is not None))
        if spent>budget+1e-7:raise AssertionError('Budget exceeded')
        summaries[strategy]=dict(status=status,signal_date=str(t.date()),trade_date=str(trade_date.date()),basket=args.basket,
            turnover_floor=floor,available_cash=cash,estimated_sale_proceeds=sale_cash,estimated_buy_cost=spent,
            estimated_cash_left=budget-spent,conditional_on_sales=bool(sale_rows),limits_confirmed=ticks is not None,
            note='Sales are estimated at signal close; recalculate buys from actual proceeds. Auction volume is unverified.')
    return pd.DataFrame(ranks),pd.DataFrame(orders),summaries


def parser():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--as-of',help='Signal session; default last snapshot session')
    ap.add_argument('--trade-date',required=True)
    ap.add_argument('--sessions',default=str(ROOT/'data/sessions_2026_2027.csv'))
    ap.add_argument('--events',default=os.environ.get('SIGG_EVENTS_FILE',str(ROOT/'data/market_events.csv')))
    ap.add_argument('--basket',choices=['all','main-proxy','liquidity-21-140'],default='liquidity-21-140')
    ap.add_argument('--instruments',default=str(ROOT/'data/sigg_instruments_2026-11-16.txt'))
    ap.add_argument('--strategy',choices=['both',*STRATS],default='both')
    ap.add_argument('--holdings',help='CSV: strategy,instrument_id,shares')
    ap.add_argument('--cash',type=float)
    ap.add_argument('--capital',type=float,default=20000.)
    ap.add_argument('--commission',type=float,default=.0039)
    rules=ap.add_mutually_exclusive_group();rules.add_argument('--fixed',type=float,default=300000.);rules.add_argument('--liq-k',type=float)
    ap.add_argument('--markup',type=float,default=.015)
    ap.add_argument('--ticks',help='Dated sourced per-ISIN tick-grid CSV; without it orders are indicative')
    ap.add_argument('--out',default='picks.csv')
    return ap


if __name__=='__main__':
    a=parser().parse_args()
    if not 0<=a.commission<1 or a.capital<=0 or a.markup<0:raise ValueError('Invalid parameters')
    ranks,orders,summary=build(a)
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    orders.to_csv(out,index=False);ranks.to_csv(out.with_suffix('.ranking.csv'),index=False)
    out.with_suffix('.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False))
    print(orders.to_string(index=False));print(json.dumps(summary,indent=2,ensure_ascii=False))
