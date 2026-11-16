"""Cash accounting in raw PLN: integer purchases, no invented fills, deferred dividends.

Daily bars establish a price but not auction capacity. This remains an idealised
open-fill model. Delistings require dated, sourced events; missing data never
creates a sale. All signals are supplied from the preceding session.
"""
from dataclasses import dataclass, field
import math
import numpy as np
import pandas as pd
from corporate import stable_ranking


@dataclass
class Outcome:
    value: float
    trades: int
    fees: float
    cash: float
    dividends: float
    positions: dict
    ledger: list = field(default_factory=list)


def simulate(close, opening, volume, split_factors, dividends, events,
             start, end, scores, n, buffer, commission=.0039, capital=20000., step=21):
    if capital <= 0 or not 0 <= commission < 1 or step < 1:
        raise ValueError('Invalid capital, commission or review interval')
    calendar=close.index
    days=calendar[(calendar>=start)&(calendar<=end)]
    reviews=set(days[::step]); cash=float(capital); pos={}; receivable=0.; fees=0.; trades=0
    frozen=set(); removed=set(); ledger=[]; marks={}
    div_by={pd.Timestamp(d):g for d,g in dividends.groupby('ex_date')}
    event_by={pd.Timestamp(d):g for d,g in events.groupby('date')}
    split_by={d:row[row!=1].to_dict() for d,row in split_factors.loc[days].iterrows() if (row!=1).any()}
    for d in days:
        t=calendar[calendar.get_loc(d)-1]
        for k,factor in split_by.get(d,{}).items():
            if k in pos:
                pos[k]*=factor
                if k in marks: marks[k]/=factor
                ledger.append(dict(date=d, action='split', instrument_id=k, ratio=factor))
        # Entitlement on ex-date is based on shares held overnight, before trades.
        for row in div_by.get(d, pd.DataFrame()).itertuples():
            if row.instrument_id in pos:
                amount=float(row.unadjusted_value)
                if not np.isfinite(amount) or amount < 0 or row.currency != 'PLN':
                    raise ValueError(f'Unresolved dividend {row.instrument_id} {d.date()}')
                receivable+=pos[row.instrument_id]*amount
                ledger.append(dict(date=d, action='dividend', instrument_id=row.instrument_id, amount=pos[row.instrument_id]*amount))
        for row in event_by.get(d, pd.DataFrame()).itertuples():
            k=int(row.instrument_id)
            if row.action=='suspend': frozen.add(k)
            elif row.action=='resume': frozen.discard(k)
            elif row.action=='delist':
                removed.add(k);frozen.discard(k)
                if k in pos:
                    # A sourced forced settlement is distinct from a market fill.
                    price=float(row.price)
                    if not np.isfinite(price) or price <= 0: raise ValueError('Delisting needs explicit settlement price')
                    value=pos.pop(k)*price;fee=value*commission;cash+=value-fee;fees+=fee;trades+=1
                    ledger.append(dict(date=d, action='delist', instrument_id=k, price=price, amount=value))
            else: raise ValueError(f'Unknown event action: {row.action}')
        if d in reviews:
            previous=cash+sum(q*marks.get(k,close.at[t,k]) for k,q in pos.items())
            x=scores(t,previous)
            if x is not None:
                x=stable_ranking(x.drop(index=list(frozen|removed),errors='ignore'))
                rank=x.rank(ascending=False,method='first')
                for k in list(pos):
                    if k in rank and rank[k]<=buffer: continue
                    p=opening.at[d,k]
                    if k in frozen or k in removed or not np.isfinite(p) or p<=0 or not volume.at[d,k]>0:
                        ledger.append(dict(date=d,action='unfilled_sell',instrument_id=k));continue
                    value=pos.pop(k)*p;fee=value*commission;cash+=value-fee;fees+=fee;trades+=1
                    ledger.append(dict(date=d,action='sell',instrument_id=k,price=p,amount=value))
                slots=max(0,n-len(pos)); per=cash/slots if slots else 0
                for k in x.index:
                    if slots<=0: break
                    if k in pos: continue
                    p=opening.at[d,k]
                    if not np.isfinite(p) or p<=0 or not volume.at[d,k]>0:
                        ledger.append(dict(date=d,action='unfilled_buy',instrument_id=k));continue
                    q=math.floor((per/(1+commission))/p)
                    if q<1: continue
                    amount=q*p;fee=amount*commission;cash-=amount+fee;fees+=fee;trades+=1;pos[k]=q;marks[k]=p;slots-=1
                    ledger.append(dict(date=d,action='buy',instrument_id=k,shares=q,price=p,amount=amount))
        for k in pos:
            price=close.at[d,k]
            if np.isfinite(price) and price>0 and k not in frozen:marks[k]=price
            elif k not in marks:
                prior=close.loc[:t,k].dropna()
                if prior.empty: raise ValueError('No valuation for held instrument')
                marks[k]=prior.iloc[-1]
        for k in pos:
            if pd.isna(close.at[d,k]) and k not in frozen:
                ledger.append(dict(date=d,action='stale_mark',instrument_id=k,price=marks[k]))
        if cash < -1e-7: raise AssertionError('Negative cash')
    value=cash+receivable+sum(q*marks[k] for k,q in pos.items())
    return Outcome(value,trades,fees,cash,receivable,pos,ledger)
