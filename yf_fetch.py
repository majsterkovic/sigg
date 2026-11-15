"""Fetch daily bars from Yahoo (.WA) for non-delisted GPW stocks. Run with the yfinance python."""
import time
import pandas as pd, yfinance as yf

START, END = '2026-10-01', '2026-11-14'   # end exclusive
BATCH, PAUSE = 100, 5

ins = pd.read_parquet('ins.parquet')
ins = ins[(ins.kind == 'stock') & (~ins.is_delisted.astype(bool))]
codes = sorted(set(ins.code))
tickers = [c + '.WA' for c in codes]


def grab(batch):
    return yf.download(batch, start=START, end=END, auto_adjust=False,
                       group_by='ticker', threads=True, progress=False)


frames = []
for i in range(0, len(tickers), BATCH):
    batch = tickers[i:i + BATCH]
    d = None
    for attempt in range(2):
        try:
            d = grab(batch)
            if d is not None and len(d):
                break
        except Exception as e:
            print('batch', i, 'attempt', attempt, 'error', e)
        time.sleep(PAUSE)
    if d is not None and len(d):
        for tk in batch:
            if tk not in d.columns.get_level_values(0):
                continue
            x = d[tk].dropna(how='all')
            x = x.dropna(subset=['Close'])
            if len(x) == 0:
                continue
            x = x.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close',
                                  'Adj Close': 'adj_close', 'Volume': 'volume'})
            x.index = pd.to_datetime(x.index).tz_localize(None).normalize()
            x.index.name = 'date'
            x = x.reset_index()
            x.insert(0, 'ticker', tk)
            frames.append(x[['ticker', 'date', 'open', 'high', 'low', 'close', 'adj_close', 'volume']])
    print('batch', i, 'done, tickers with data so far', len(frames), flush=True)
    time.sleep(PAUSE)

px = pd.concat(frames, ignore_index=True)
px['code'] = px.ticker.str[:-3]
m = ins.drop_duplicates('code').set_index('code').instrument_id
px.insert(0, 'instrument_id', px.code.map(m).astype('int64'))
px = px.drop(columns=['ticker', 'code']).sort_values(['instrument_id', 'date'])
px.to_parquet('yf_px.parquet', index=False)

got = set(px.instrument_id)
miss = ins[~ins.instrument_id.isin(got)][['instrument_id', 'code']].copy()
miss['ticker'] = miss.code + '.WA'
miss.to_csv('yf_missing.csv', index=False)
print('fetched', len(got), 'missing', len(miss), 'rows', len(px), px.date.min(), px.date.max())
