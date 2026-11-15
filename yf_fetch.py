"""Fetch daily bars from Yahoo (.WA) for non-delisted GPW stocks. Run with the yfinance python.
Yahoo ticker = ins.ref_ticker with .WAR replaced by .WA (ins.code can be an old code)."""
import time
import pandas as pd, yfinance as yf

START, END = '2026-10-01', '2026-11-14'   # end exclusive
BATCH, PAUSE = 100, 5

ins = pd.read_parquet('ins.parquet')
ins = ins[(ins.kind == 'stock') & (~ins.is_delisted.astype(bool))].copy()
assert ins.ref_ticker.str.endswith('.WAR').all()
ins['yf_ticker'] = ins.ref_ticker.str[:-4] + '.WA'
assert not ins.yf_ticker.duplicated().any()
tickers = sorted(ins.yf_ticker)
iid_of = ins.set_index('yf_ticker').instrument_id
failed_log = []


def log(msg):
    print(msg, flush=True)
    failed_log.append(msg)


def grab(batch):
    return yf.download(batch, start=START, end=END, auto_adjust=False,
                       group_by='ticker', threads=True, progress=False)


def extract(d, tk):
    """Rows of one ticker from a download result, or None."""
    if d is None or not len(d):
        return None
    if isinstance(d.columns, pd.MultiIndex):
        if tk not in d.columns.get_level_values(0):
            return None
        x = d[tk]
    else:
        x = d
    x = x.dropna(subset=['Close'])
    if len(x) == 0:
        return None
    x = x.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close',
                          'Adj Close': 'adj_close', 'Volume': 'volume'})
    x.index = pd.to_datetime(x.index).tz_localize(None).normalize()
    x.index.name = 'date'
    x = x.reset_index()
    x.insert(0, 'yf_ticker', tk)
    return x[['yf_ticker', 'date', 'open', 'high', 'low', 'close', 'adj_close', 'volume']]


frames, got = [], set()
for i in range(0, len(tickers), BATCH):
    batch = tickers[i:i + BATCH]
    d = None
    for attempt in range(2):
        try:
            d = grab(batch)
            if d is not None and len(d):
                break
            log(f'batch starting at {i} attempt {attempt}: empty result, tickers {batch}')
        except Exception as e:
            log(f'batch starting at {i} attempt {attempt}: error {e!r}, tickers {batch}')
        time.sleep(PAUSE)
    for tk in batch:
        x = extract(d, tk)
        if x is None:                       # nothing in the batch: retry this ticker alone once
            time.sleep(1)
            try:
                x = extract(grab([tk]), tk)
            except Exception as e:
                log(f'single retry {tk}: error {e!r}')
            if x is None:
                log(f'still no data after single retry (batch {i}): {tk}')
        if x is not None:
            frames.append(x); got.add(tk)
    print('batch', i, 'done, tickers with data so far', len(got), flush=True)
    time.sleep(PAUSE)

px = pd.concat(frames, ignore_index=True)
px.insert(0, 'instrument_id', px.yf_ticker.map(iid_of).astype('int64'))
px = px.drop(columns='yf_ticker').sort_values(['instrument_id', 'date'])
px.to_parquet('yf_px.parquet', index=False)

miss = ins[~ins.instrument_id.isin(set(px.instrument_id))][['instrument_id', 'code', 'yf_ticker']].rename(columns={'yf_ticker': 'ticker'})
miss.to_csv('yf_missing.csv', index=False)
open('yf_failed.txt', 'w').write('\n'.join(failed_log) + '\n')
print('fetched', px.instrument_id.nunique(), 'missing', len(miss), 'rows', len(px), px.date.min(), px.date.max())
