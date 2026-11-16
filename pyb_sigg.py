"""PyBroker execution cross-check of the raw-accounting order ledger.

Signals/accounting are checked by tests, not independently by this replay.
Split-normalised units preserve cash values across corporate actions; deferred
PLN dividends are added to final equity, never made available for purchases.
No synthetic volume is used to claim auction capacity.
"""
import warnings
import numpy as np
import pandas as pd
from sim import simulate_window, C, O, V, SPLIT_FACTORS, dates, window
import pybroker as pb
from pybroker import Strategy, StrategyConfig
from pybroker.common import FeeMode

pb.disable_logging()
STRATS={'spokojna':('hi52',10,20),'podium':('combo',3,6)}


def run(signame,n,buffer,y):
    expected=simulate_window(signame,n,buffer,.0039,y)
    trades=[x for x in expected.ledger if x['action'] in ('buy','sell','delist')]
    if not trades:return expected.value/20000-1,0
    s,e=window(y);rng=dates[dates.get_loc(s)-1:dates.get_loc(e)+1];cols=sorted({x['instrument_id'] for x in trades})
    factor=SPLIT_FACTORS.loc[rng,cols].cumprod()
    rows=[]
    # PyBroker receives genuine daily volume, but replay does not model its capacity.
    for k in cols:
        cl=C[k].reindex(rng).ffill();op=O[k].reindex(rng)
        for d in rng:
            # A missing bar may value an existing position, but never creates an order.
            close=cl.at[d]
            if not np.isfinite(close):
                prior=C.loc[:d,k].dropna()
                if prior.empty:continue
                close=prior.iloc[-1]
            opening=op.at[d] if np.isfinite(op.at[d]) and op.at[d]>0 else close
            rows.append(dict(date=d,symbol=str(k),open=opening*factor.at[d,k],close=close*factor.at[d,k],
                             high=max(opening,close)*factor.at[d,k],low=min(opening,close)*factor.at[d,k],volume=float(V.at[d,k]) if pd.notna(V.at[d,k]) else 0.))
    plan={}
    for x in trades:plan[(pd.Timestamp(x['date']),str(x['instrument_id']))]=x
    def execute(ctx):
        decision=pd.Timestamp(ctx.dt)
        i=dates.get_loc(decision)
        if i+1>=len(dates):return
        key=(dates[i+1],ctx.symbol)
        if key not in plan:return
        order=plan[key];k=int(ctx.symbol);f=factor.at[key[0],k]
        if order['action']=='buy':ctx.buy_shares=order['shares']/f;ctx.buy_fill_price=order['price']*f
        else:ctx.sell_fill_price=order['price']*f;ctx.sell_all_shares()
    cfg=StrategyConfig(initial_cash=20000,fee_mode=FeeMode.ORDER_PERCENT,fee_amount=.39,
                       enable_fractional_shares=True,round_fill_price=False,buy_delay=1,sell_delay=1)
    st=Strategy(pd.DataFrame(rows),rng[0],e,cfg);st.add_execution(execute,[str(k) for k in cols])
    result=st.backtest(calc_bootstrap=False)
    return (float(result.portfolio.equity.iloc[-1])+expected.dividends)/20000-1,len(result.orders)


if __name__=='__main__':
    out=[]
    for name,(sg,n,buffer) in STRATS.items():
        for y in range(2003,2026):
            r,count=run(sg,n,buffer,y);expected=simulate_window(sg,n,buffer,.0039,y)
            out.append(dict(strat=name,year=y,pybroker=r,sim=expected.value/20000-1,diff=r-(expected.value/20000-1),orders=count,trades=expected.trades))
            print(name,y,r,expected.value/20000-1,count,expected.trades,flush=True)
    r=pd.DataFrame(out);r.to_csv('pyb_years.csv',index=False)
    if r['diff'].abs().max()>1e-6 or (r.orders!=r.trades).any():raise AssertionError('PyBroker replay disagrees with accounting ledger')
    print('Max difference',r['diff'].abs().max())
