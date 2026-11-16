"""Split-only signal prices. No clipping and no future observations."""
import numpy as np
import pandas as pd


def split_prices(close, adjusted, events):
    factors = pd.DataFrame(1.0, index=close.index, columns=close.columns)
    uncertain = pd.DataFrame(False, index=close.index, columns=close.columns)
    checks = []
    relative = adjusted / close
    previous = relative.ffill().shift(1)
    for event in events.itertuples():
        k, d, ratio = int(event.instrument_id), pd.Timestamp(event.ex_date), float(event.ratio)
        if k not in close or d < close.index[0] or d > close.index[-1]:
            continue
        # Do not silently move an event onto a later trading day.
        observed = relative.at[d, k] / previous.at[d, k] if d in close.index else np.nan
        valid = np.isfinite(ratio) and ratio > 0 and np.isfinite(observed) and abs(observed / ratio - 1) <= .03
        checks.append(dict(instrument_id=k, ex_date=d, ratio=ratio,
                           observed_factor=observed, accepted=bool(valid)))
        if d in close.index:
            if valid:
                factors.at[d, k] *= ratio
            else:
                uncertain.at[d, k] = True
        elif not valid:
            # Unknown event date cannot be safely interpreted as a split.
            later = close.index[close.index > d]
            if len(later):
                uncertain.at[later[0], k] = True
    price = close * factors.cumprod()
    blocked = uncertain.rolling(252, min_periods=1).max().astype(bool)
    return price, factors, blocked, pd.DataFrame(checks, columns=[
        'instrument_id', 'ex_date', 'ratio', 'observed_factor', 'accepted'])


def stable_ranking(scores):
    """Descending signal, instrument_id breaks ties, independently of input order."""
    return scores.dropna().sort_index().sort_values(ascending=False, kind='stable')
