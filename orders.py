"""Validated tick grids. No guessed per-instrument liquidity table."""
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR
import pandas as pd


def price_limit(close, markup=.015, step=None):
    if close<=0 or markup<0:raise ValueError('Invalid price or markup')
    value=Decimal(str(close))*(1+Decimal(str(markup)))
    if step is None:
        # Indicative only. Must be confirmed in the game before placing the order.
        return float(value.quantize(Decimal('.01'),rounding=ROUND_CEILING))
    tick=Decimal(str(step))
    if tick<=0:raise ValueError('Invalid tick')
    return float((value/tick).to_integral_value(rounding=ROUND_CEILING)*tick)


def quantity(budget,price,fee):
    if not 0<=fee<1 or budget<0 or price<=0:raise ValueError('Invalid order inputs')
    return int((Decimal(str(budget))/(1+Decimal(str(fee)))/Decimal(str(price))).to_integral_value(rounding=ROUND_FLOOR))


def confirmed_limit(isin,close,markup,trade_date,ticks):
    """CSV rows: isin,valid_from,valid_to,lower,upper,tick,source.
    Select the price band again after rounding across a boundary.
    """
    value=price_limit(close,markup)
    for _ in range(10):
        g=ticks[(ticks.isin_code==isin)&(ticks.valid_from<=trade_date)&(ticks.valid_to>=trade_date)&
                (ticks.lower<=value)&(ticks.upper>value)]
        if len(g)!=1 or g.source.isna().any() or g.source.str.strip().eq('').any():
            raise ValueError(f'Missing/ambiguous sourced tick grid for {isin} on {trade_date.date()}')
        new=price_limit(close,markup,float(g.iloc[0].tick))
        # Remain at least at the crossed boundary, even if the new grid is finer.
        new=max(new,value)
        if new==value:return new
        value=new
    raise ValueError('Tick rounding failed to converge')
