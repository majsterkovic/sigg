"""Strategies on restricted baskets. Index membership is a proxy: main-market stocks ranked by
12-month median daily turnover at the review (WIG20 = 1-20, mWIG40 = 21-60, sWIG80 = 61-140).
NewConnect = ISINs from GPW NC segment lists of 12.2021, 06.2022 and 03.2024."""
from sim import *
from paths import reference_path
from concurrent.futures import ProcessPoolExecutor

from baskets import NC, TO12, size_rank
isnc = pd.Series(P.columns.isin(list(NC)), index=P.columns)


def band(a, b):
    return lambda t: (size_rank(t) >= a) & (size_rank(t) <= b)


BASKETS = {
    'całość (z NC)': None,
    'rynek główny (bez NC)': lambda t: ~isnc,
    'płynność 1–20 (proxy)': band(1, 20),
    'płynność 21–60 (proxy)': band(21, 60),
    'płynność 61–140 (proxy)': band(61, 140),
    'płynność 1–60 (proxy)': band(1, 60),
    'płynność 21–140 (proxy)': band(21, 140),
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
