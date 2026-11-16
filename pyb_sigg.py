"""Cross-check of sim.py with PyBroker: same signals, same SIGG windows, PyBroker executes the orders.
Decision at close t (day before review), fill at next open, fees 0.39% per order, fractional shares."""
import sys, warnings
warnings.filterwarnings('ignore')
src = open('sim.py').read().split('if __name__')[0]
exec(src)
import pybroker as pb
from pybroker import Strategy, StrategyConfig
from pybroker.common import FeeMode, PriceType

pb.disable_logging()
pb.register_columns('sig', 'uni')
C_FEE = 0.0039
STRATS = {'spokojna': ('hi52', 10, 20), 'podium': ('combo', 3, 6)}


def run(signame, N, buffer, y, min_to=300_000):
    s, e = window(y)
    i0 = dates.get_loc(s)
    seg = dates[(dates >= s) & (dates <= e)]
    decide = [dates[dates.get_loc(d) - 1] for d in seg[::21]]
    U = {t: universe(t, min_to) for t in decide}
    cols = sorted(set().union(*[set(u[u].index) for u in U.values()]))
    rng = dates[i0 - 1: dates.get_loc(e) + 1]
    cl = P.loc[rng, cols].ffill()
    op = Oadj.loc[rng, cols].where(lambda x: x > 0).fillna(cl)
    sg = SIG[signame].loc[rng, cols]
    un = pd.DataFrame(False, index=rng, columns=cols)
    for t, u in U.items():
        un.loc[t] = u.reindex(cols).fillna(False).values
    df = pd.DataFrame({'open': op.stack(), 'close': cl.stack(),
                       'sig': sg.stack(future_stack=True).reindex(cl.stack().index),
                       'uni': un.stack().reindex(cl.stack().index).astype(float)}).reset_index()
    df.columns = ['date', 'symbol', 'open', 'close', 'sig', 'uni']
    df['high'] = df[['open', 'close']].max(axis=1); df['low'] = df[['open', 'close']].min(axis=1)
    df['volume'] = 1.0; df['symbol'] = df.symbol.astype(str)
    plan = {}

    def before(ctxs):
        dt = next(iter(ctxs.values())).dt
        if pd.Timestamp(dt) not in U:
            return
        x = pd.Series({k: c.sig[-1] for k, c in ctxs.items() if c.uni[-1] > 0}).dropna()
        if len(x) < max(3 * N, 20):
            return
        rank = x.rank(ascending=False)
        held = {k for k, c in ctxs.items() if c.long_pos() is not None}
        keep = {k for k in held if k in rank.index and rank[k] <= buffer}
        sell = held - keep
        want = [k for k in x.nlargest(N + len(keep)).index if k not in keep][:N - len(keep)]
        any_ctx = next(iter(ctxs.values()))
        cash = float(any_ctx.cash) + sum(float(ctxs[k].long_pos().shares) * ctxs[k].close[-1] for k in sell)
        per = cash / len(want) if want else 0
        plan[dt] = (sell, {k: per / (1 + C_FEE) / ctxs[k].close[-1] for k in want})

    def execute(ctx):
        if ctx.dt not in plan:
            return
        sell, buy = plan[ctx.dt]
        if ctx.symbol in sell:
            ctx.sell_fill_price = PriceType.OPEN; ctx.sell_all_shares()
        if ctx.symbol in buy:
            ctx.buy_fill_price = PriceType.OPEN; ctx.buy_shares = buy[ctx.symbol]

    cfg = StrategyConfig(initial_cash=20000, fee_mode=FeeMode.ORDER_PERCENT, fee_amount=C_FEE * 100,
                         enable_fractional_shares=True)
    st = Strategy(df, rng[0], rng[-1], cfg)
    st.set_before_exec(before)
    st.add_execution(execute, sorted(df.symbol.unique()))
    res = st.backtest(calc_bootstrap=False)
    eq = res.portfolio['equity'].iloc[-1]
    return float(eq) / 20000 - 1, len(res.orders)


if __name__ == '__main__':
    years = list(range(2003, 2026))
    out = []
    for name, (sg, N, buf) in STRATS.items():
        for y in years:
            r_pb, n_orders = run(sg, N, buf, y)
            r_sim, tr, _ = sim(sg, N, buf, C_FEE, y)
            out.append(dict(strat=name, year=y, pybroker=r_pb, sim=r_sim, diff=r_pb - r_sim, orders=n_orders, trades=tr))
            print(name, y, round(r_pb, 4), round(r_sim, 4), n_orders, tr, flush=True)
    R = pd.DataFrame(out); R.to_csv('pyb_years.csv', index=False)
    print(R.groupby('strat')[['pybroker', 'sim', 'diff']].agg(['mean', 'median']).round(4).to_string())
    print('max |diff|', R.groupby('strat')['diff'].apply(lambda d: d.abs().max()).round(4).to_dict())
