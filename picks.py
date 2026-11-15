"""Pick list for the SIGG start on 16.11.2026: signals from closes of 13.11.2026.
Run with GPW_SUFFIX=_x. Rule: turnover floor = liq_k*20000/N per strategy, or --fixed MIN_TO for both."""
import argparse, re
from sim import *          # bt names, SIG['combo'] as in the backtest (ranks over ALL instruments)

CAP, COMM = 20000.0, 0.0039
STRATS = {'spokojna': ('hi52', 10), 'podium': ('combo', 3)}
NRES = 5

def zl(x, d=0):
    return f'{x:,.{d}f}'.replace(',', ' ')

def yf_codes(path='yf_check.txt'):
    """Codes rejected/stale/missing/without base row in the yfinance extension."""
    codes = set(pd.read_csv('yf_missing.csv').code.astype(str))
    sec = None
    for ln in open(path, encoding='utf-8'):
        if not ln.startswith(' '):          # a header line starts a section
            sec = 'tab' if ln.startswith(('rejected as stale', 'rejected list')) else 'plain' if ln.startswith('accepted without a') else None
            continue
        s = ln.strip()
        if sec == 'tab' and '\t' in s: codes.add(s.split('\t')[0])
        elif sec == 'plain' and re.fullmatch(r'[A-Z0-9]+', s): codes.add(s)
    assert codes, 'no codes parsed from yf_check.txt / yf_missing.csv'
    return codes

def unevaluable(ins, floors, cutoff='2026-10-26'):
    """Per strategy: codes from yf_codes() that were in the universe (strategy floor) on the last session <= cutoff,
    with their rank on the strategy signal in that universe. Returns (t_ref, {strategy: (floor, n, [(code, rank)])})."""
    codes = yf_codes()
    t_ref = P.index[P.index <= pd.Timestamp(cutoff)][-1]
    code_of = ins.set_index('instrument_id').code
    out = {}
    for strat, (sig, N) in STRATS.items():
        u = universe(t_ref, floors[strat])
        x = SIG[sig].loc[t_ref][u[u].index].dropna()
        rk = x.rank(ascending=False, method='first')
        hit = sorted(((code_of[k], int(rk[k])) for k in x.index if code_of.get(k) in codes), key=lambda z: z[1])
        out[strat] = (floors[strat], len(x), hit)
    return t_ref, out

def build(liq_k, fixed):
    ins = pd.read_parquet('ins.parquet')
    t = P.index[-1]
    assert t == pd.Timestamp('2026-11-13'), t
    delisted = set(ins.loc[ins.is_delisted == True, 'instrument_id'])
    meta = ins.set_index('instrument_id')
    rows = []
    for strat, (sig, N) in STRATS.items():
        floor = fixed if fixed is not None else liq_k * CAP / N
        u = universe(t, floor) & C.loc[t].notna() & (V.loc[t] > 0)
        u = u & ~u.index.isin(delisted)
        x = SIG[sig].loc[t][u].dropna().sort_values(ascending=False)
        slot = CAP / N
        kept = 0
        for srank, k in enumerate(x.index, 1):
            close = float(C.loc[t, k])
            shares = int(np.floor(slot / (1 + COMM) / close))
            if shares < 1:
                if kept < N + NRES:
                    print(f'{meta.at[k, "code"]} skipped ({strat}, signal rank {srank}): 1 share costs {zl(close, 2)} zl > slot {zl(slot)} zl')
                continue
            kept += 1
            if kept > N + NRES: break
            rows.append(dict(strategy=strat, role='buy' if kept <= N else 'reserve', rank=kept, signal_rank=srank,
                code=meta.at[k, 'code'], name=meta.at[k, 'name'], sector=meta.at[k, 'sector'],
                close_13_11=close, hi52=float(SIG['hi52'].at[t, k]), mom3=float(SIG['mom3'].at[t, k]),
                combo=float(SIG['combo'].at[t, k]), med_turnover_63=float(med_to.at[t, k]),
                shares=shares, amount=shares * close,
                rule=f'floor {floor:.0f} zl ({"fixed" if fixed is not None else f"{liq_k:g}*20000/{N}"})', _floor=floor))
    df = pd.DataFrame(rows)
    # Step 3 checks
    buy = df[df.role == 'buy']
    assert (buy.strategy == 'spokojna').sum() == 10 and (buy.strategy == 'podium').sum() == 3, 'buy rows'
    assert (df.role == 'reserve').sum() == 10, 'reserve rows'
    assert (buy.med_turnover_63 >= buy._floor).all(), 'turnover floor'
    assert (buy.groupby('strategy').amount.sum() <= CAP).all(), 'amount > capital'
    assert (df.shares >= 1).all(), 'unbuyable row'
    floors = df.groupby('strategy')._floor.first().to_dict()
    return df.drop(columns='_floor'), ins, t, floors

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--liq-k', type=float, default=10)
    ap.add_argument('--fixed', type=float, default=None, help='fixed turnover floor in zl for both strategies')
    ap.add_argument('--out', default='picks.csv')
    a = ap.parse_args()
    df, ins, t, floors = build(a.liq_k, a.fixed)
    df.to_csv(a.out, index=False)
    pd.set_option('display.width', 300); pd.set_option('display.max_columns', 30); pd.set_option('display.max_colwidth', 28)
    print(f'signal day {t.date()}, rule: {df.rule.iloc[0]} / {df.rule.iloc[-1]}  -> {a.out}')
    print(df.drop(columns='rule').round({'close_13_11': 2, 'hi52': 3, 'mom3': 3, 'combo': 3, 'med_turnover_63': 0, 'amount': 2}).to_string(index=False))
    print(df[df.role == 'buy'].groupby('strategy').amount.sum().round(2).to_string())
    t_ref, un = unevaluable(ins, floors)
    for strat, (fl, n, hit) in un.items():
        print(f'Not evaluated (rejected/stale/missing in yfinance extension), in universe on {t_ref.date()}, {strat}, floor {zl(fl)} zl, '
              f'universe {n} names (code: rank on signal): ' + (', '.join(f'{c}: {r}' for c, r in hit) or 'none'))
