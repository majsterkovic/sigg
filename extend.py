"""Extend A/C/O/V with Yahoo rows after 2026-10-26. Run with the analysis python."""
import pandas as pd, numpy as np

LAST = pd.Timestamp('2026-10-26')
EXPECTED = ['2026-10-27', '2026-10-28', '2026-10-29', '2026-10-30', '2026-11-02', '2026-11-03',
            '2026-11-04', '2026-11-05', '2026-11-06', '2026-11-09', '2026-11-10', '2026-11-12',
            '2026-11-13']
OV0 = pd.Timestamp('2026-10-01')

A = pd.read_parquet('A.parquet'); C = pd.read_parquet('C.parquet')
O = pd.read_parquet('O.parquet'); V = pd.read_parquet('V.parquet')
assert A.index[-1] == LAST
yf = pd.read_parquet('yf_px.parquet')
yf['date'] = pd.to_datetime(yf.date).astype(A.index.dtype)
n_fetched = yf.instrument_id.nunique()
n_missing = len(pd.read_csv('yf_missing.csv'))

# Step 2: new session dates
cnt = yf[yf.close.notna()].groupby('date').instrument_id.nunique()
new = [d for d in cnt.index if d > LAST and cnt[d] >= 0.5 * n_fetched]
new = pd.DatetimeIndex(sorted(new)).astype(A.index.dtype)
got = [d.strftime('%Y-%m-%d') for d in new]
assert got == EXPECTED, f'new sessions differ: {got}'

# Step 3: validation on overlap
ov = yf[(yf.date >= OV0) & (yf.date <= LAST)]
rows = []
for iid, g in ov.groupby('instrument_id'):
    if iid not in C.columns:
        rows.append((iid, 0, np.nan)); continue
    c = C[iid].reindex(g.date.values).values
    ok = ~np.isnan(c) & g.close.notna().values & (c != 0)
    dev = np.abs(g.close.values[ok] / c[ok] - 1)
    rows.append((iid, int(ok.sum()), np.median(dev) if ok.sum() else np.nan))
val = pd.DataFrame(rows, columns=['instrument_id', 'n_overlap', 'med_dev']).set_index('instrument_id')
# instruments fetched but without any overlap rows at all
for iid in set(yf.instrument_id) - set(val.index):
    val.loc[iid] = (0, np.nan)
rej_reason = pd.Series('', index=val.index)
rej_reason[val.n_overlap < 5] = 'fewer than 5 overlap days'
rej_reason[(val.n_overlap >= 5) & (val.med_dev > 0.01)] = 'median deviation > 1%'
accepted = [i for i in val.index[rej_reason == ''] if i in A.columns]
rejected = val[rej_reason != ''].assign(reason=rej_reason[rej_reason != ''])
not_in_matrix = [i for i in val.index[rej_reason == ''] if i not in A.columns]

# stale series: volume 0/NaN on every new session, or constant close across all new sessions
ynew = yf[yf.date.isin(new)]
stale = []
for iid in accepted:
    g = ynew[ynew.instrument_id == iid]
    zero_vol = (g.volume.fillna(0) == 0).all()      # also true when no new rows at all
    const_close = g.close.dropna().nunique() <= 1
    if zero_vol or const_close:
        stale.append((iid, 'volume 0/NaN on all new sessions' if zero_vol else 'constant close on all new sessions'))
stale_ids = [i for i, _ in stale]
accepted = [i for i in accepted if i not in stale_ids]

# Step 4: splice
idx2 = A.index.append(new)
A2, C2, O2, V2 = [m.reindex(idx2) for m in (A, C, O, V)]
yfi = yf.set_index(['instrument_id', 'date'])
no_base, early_base = [], []
for iid in accepted:
    g = yf[yf.instrument_id == iid].set_index('date')
    cand = g.index[(g.index >= OV0) & (g.index <= LAST) & g.adj_close.notna().values]
    cand = [d for d in cand if d in A.index and pd.notna(A.at[d, iid]) and pd.notna(C.at[d, iid])]
    if not cand:
        no_base.append(iid); continue
    base = max(cand)
    if base < LAST: early_base.append((iid, base))
    gn = g.reindex(new)
    C2.loc[new, iid] = gn.close.values
    O2.loc[new, iid] = gn.open.values
    V2.loc[new, iid] = gn.volume.values
    A2.loc[new, iid] = A.at[base, iid] * gn.adj_close.values / g.at[base, 'adj_close']

# jumps: daily returns of new A rows (the first one is against the last DB value, i.e. the base)
rA = A2.ffill().pct_change(fill_method=None).loc[new]; rC = C2.ffill().pct_change(fill_method=None).loc[new]
flags, matched = [], 0
for iid in accepted:
    for d in new:
        a = rA.at[d, iid]
        if pd.isna(a) or not (a > 1.0 or a < -0.7):
            continue
        c = rC.at[d, iid]
        same = (not pd.isna(c)) and ((a > 1.0 and c > 1.0) or (a < -0.7 and c < -0.7))
        if same: matched += 1
        else: flags.append((iid, d.date(), a, c))

A2.to_parquet('A_x.parquet'); C2.to_parquet('C_x.parquet')
O2.to_parquet('O_x.parquet'); V2.to_parquet('V_x.parquet')

ins = pd.read_parquet('ins.parquet').set_index('instrument_id')
n_close_last = int(C2.loc[new[-1], accepted].notna().sum())
n_spliced = int(C2.loc[new[-1]].notna().sum())
L = []
L.append(f'new sessions ({len(got)}): {", ".join(got)}')
L.append(f'tickers fetched (any data): {n_fetched}')
L.append(f'tickers missing on Yahoo: {n_missing} (see yf_missing.csv)')
L.append(f'accepted (passed validation, not stale): {len(accepted) + len(not_in_matrix)} '
         f'(of which {len(not_in_matrix)} not columns of the DB matrices, skipped)')
L.append(f'rejected as stale after validation (new rows NaN): {len(stale)}')
for iid, why in stale: L.append(f'  {ins.code.get(iid, iid)}\tstale: {why}')
L.append(f'rejected: {len(rejected)}')
L.append(f'  reason fewer than 5 overlap days: {(rejected.reason == "fewer than 5 overlap days").sum()}')
L.append(f'  reason median deviation > 1%: {(rejected.reason == "median deviation > 1%").sum()}')
L.append('rejected list (code, reason, n_overlap, median |yf/DB-1|):')
for iid, r in rejected.sort_values('med_dev', ascending=False).iterrows():
    L.append(f'  {ins.code.get(iid, iid)}\t{r.reason}\tn={r.n_overlap}\tmed_dev={r.med_dev:.4f}')
L.append(f'accepted without a 2026-10-26 base row in DB or Yahoo (new rows left NaN): {len(no_base)}')
for iid in no_base: L.append(f'  {ins.code.get(iid, iid)}')
L.append(f'accepted with a splice base earlier than 2026-10-26 (last date in 2026-10-01..2026-10-26 with DB A, DB C and Yahoo adj_close): {len(early_base)}')
for iid, b in sorted(early_base, key=lambda x: ins.code.get(x[0], str(x[0]))): L.append(f'  {ins.code.get(iid, iid)}\tbase {b.date()}')
L.append(f'new-row A jumps (>+100% or <-70%) with the same move in raw C: {matched}')
L.append(f'new-row A jumps WITHOUT the same move in raw C (flagged): {len(flags)}')
for iid, d, a, c in flags:
    L.append(f'  {ins.code.get(iid, iid)}\t{d}\tA ret={a:.3f}\tC ret={c:.3f}')
L.append(f'accepted instruments with a close on {got[-1]}: {n_close_last}')
miss_df = pd.read_csv('yf_missing.csv')
tk = lambda i: ins.ref_ticker.get(i, str(i))[:-4]
L.append(f'not evaluated, section 1: no Yahoo data ({len(miss_df)}), code -> current ticker')
for _, r in miss_df.iterrows(): L.append(f'  {r.code}\t{tk(r.instrument_id)}')
L.append(f'not evaluated, section 2: frozen feed (stale), splice skipped ({len(stale)}), code -> current ticker')
for iid, why in stale: L.append(f'  {ins.code.get(iid, iid)}\t{tk(iid)}\t{why}')
open('yf_check.txt', 'w').write('\n'.join(L) + '\n')
print('\n'.join(L[:12])); print('...'); print('\n'.join(L[-6:]))
