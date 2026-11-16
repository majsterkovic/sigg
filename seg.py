"""Strategies on restricted baskets. Index membership is a proxy: main-market stocks ranked by
12-month median daily turnover at the review (WIG20 = 1-20, mWIG40 = 21-60, sWIG80 = 61-140).
NewConnect = ISINs from GPW NC segment lists of 12.2021, 06.2022 and 03.2024."""
src = open('sim.py').read().split('if __name__')[0]
exec(src)
from concurrent.futures import ProcessPoolExecutor

NC = set(pd.read_csv('nc_ids.csv').instrument_id)
isnc = pd.Series(P.columns.isin(list(NC)), index=P.columns)
TO12 = TO.rolling(252, min_periods=120).median()
_rank = {}


def size_rank(t):
    if t not in _rank:
        ok = (~isnc) & (hist.loc[t] >= 250) & traded.loc[t] & (C.loc[t] >= 1)
        _rank[t] = TO12.loc[t].where(ok).rank(ascending=False)
    return _rank[t]


def band(a, b):
    return lambda t: (size_rank(t) >= a) & (size_rank(t) <= b)


BASKETS = {
    'całość (z NC)': None,
    'rynek główny (bez NC)': lambda t: ~isnc,
    'WIG20': band(1, 20),
    'mWIG40': band(21, 60),
    'sWIG80': band(61, 140),
    'WIG20+mWIG40': band(1, 60),
    'mWIG40+sWIG80': band(21, 140),
    'trzy indeksy (1-140)': band(1, 140),
    'poza indeksami (141+)': band(141, 10**6),
    'sWIG80+poza (61+)': band(61, 10**6),
    'NewConnect': lambda t: isnc,
}
STRATS = {'spokojna (hi52, 10)': ('hi52', 10, 20), 'podium (combo, 3)': ('combo', 3, 6),
          'mom3, 10': ('mom3', 10, 20), 'mom3, 3': ('mom3', 3, 6)}
YEARS = list(range(2003, 2026))


def job(args):
    bname, sname, mt = args
    sig, N, buf = STRATS[sname]
    out = []
    for y in YEARS:
        r, tr, fe = sim(sig, N, buf, 0.0039, y, min_to=mt, basket=BASKETS[bname], min_n=N + 2)
        out.append(dict(basket=bname, strat=sname, min_to=mt, year=y, ret=r, trades=tr))
    return out


if __name__ == '__main__':
    jobs = [(b, s, mt) for mt in [300_000, 50_000] for b in BASKETS for s in STRATS]
    res = []
    with ProcessPoolExecutor(8) as ex:
        for o in ex.map(job, jobs):
            res += o
            print(o[0]['basket'], o[0]['strat'], o[0]['min_to'], flush=True)
    R = pd.DataFrame(res); R['wig'] = R.year.map(wigret(YEARS))
    R.to_csv('seg_years.csv', index=False)

    def st(g):
        inv = g[g.trades > 0]; x = inv.ret
        return pd.Series(dict(n=len(inv), mean=x.mean(), median=x.median(), loss=(x < 0).mean(), worst=x.min(),
                              p20=(x > .2).mean(), beatWIG=((x - inv.wig) > 0).mean(), late=inv[inv.year >= 2013].ret.mean()))
    S = R.groupby(['min_to', 'basket', 'strat'], sort=False).apply(st).reset_index()
    S.to_csv('seg_stats.csv', index=False)
    pd.set_option('display.width', 250); pd.set_option('display.max_rows', 500)
    print(S.round(3).to_string())
