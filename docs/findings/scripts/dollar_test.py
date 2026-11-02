# Rules set before running. z_usd = robust z of log(block dollars / market dark dollars), 26-week baseline.
# U1 institutions: Q2 mean z_usd ranks positively with existing-holder net change (one-sided p < 0.05)
#    and beats the 95th percentile of 200 random 4-venue placebos.
# U2 buying: 60 stocks, adjusted closes, entry 21 days after week start, 13-week hold, one entry per ticker
#    per hold. Compare (a) z_usd >= 2 anywhere and (b) z_usd >= 2 within 10% of the 52-week low, against the
#    same tickers' other weeks. Pass needs win rate +5 points, median SPY excess above 0, permutation p < 0.05,
#    and a positive median excess in both halves of the sample.
import pickle
import sys

sys.path.insert(0, ".")
import numpy as np
import pandas as pd
import whale_watch as ww

pd.set_option("display.width", 180); pd.set_option("display.max_columns", 30); pd.set_option("display.max_rows", 60)
rng = np.random.default_rng(20261101)
d1 = pickle.load(open("proof_data.pkl", "rb")); d2 = pickle.load(open("signal_data.pkl", "rb")); d3 = pickle.load(open("ranges.pkl", "rb"))
raw = {**d2["raw"], **d1["raw"], **d3["raw"]}; venues = d3["venues"]; mkt = d1["mkt"]
q2 = pickle.load(open("q2_clean.pkl", "rb"))
px = pickle.load(open("buy_px.pkl", "rb")); spy = px["SPY"]


def vm(x):
    f = x[x["summarytypecode"] == "ATS_W_SMBL_FIRM"].sort_values("lastupdatedate").drop_duplicates(["weekstartdate", "mpid"], keep="last").copy()
    f["wk"] = pd.to_datetime(f["weekstartdate"])
    return f.pivot_table(index="wk", columns="mpid", values="totalnotionalsum", aggfunc="sum").fillna(0.0)


def z_of(usd, m):
    v = (usd / m).where(usd > 0)
    return pd.Series(ww.robust_z(np.log(v), 26, 13), index=usd.index)


Z, W, V = {}, {}, {}
for t in raw:
    w = ww.finra_ticker_weekly(raw[t])
    m = ww.align_market(w.index, mkt, "mkt_dollars")["value"]
    b = ww.finra_block_weekly(raw[t], venues).reindex(w.index).fillna(0.0)
    Z[t] = z_of(b, m); W[t] = (w, m); V[t] = vm(raw[t]).reindex(w.index).fillna(0.0)

print("=== named weeks ===")
for t, wk in (("MSFT", "2026-06-22"), ("MSFT", "2026-06-01"), ("ORCL", "2026-10-05"), ("NVDA", "2026-04-27")):
    print(t, wk, "z_usd", round(float(Z[t].get(pd.Timestamp(wk), np.nan)), 2))
Zdf = pd.DataFrame(Z)
wk = pd.Timestamp("2026-06-22")
print("week of 2026-06-22 across tickers: median z_usd", round(Zdf.loc[wk].median(), 2), "| share of tickers z>=2", round((Zdf.loc[wk] >= 2).mean() * 100), "%")
print("weeks with the most tickers at z_usd>=2 (last 104):", (Zdf.tail(104) >= 2).sum(axis=1).sort_values(ascending=False).head(5).to_dict())
print("flag rate z_usd>=2:", round((Zdf.tail(104) >= 2).mean().mean() * 100, 1), "% of ticker-weeks | z>=3:", round((Zdf.tail(104) >= 3).mean().mean() * 100, 1), "%")

print("\n=== U1 institutions, Apr-Jun 2026 ===")
mean_z = pd.Series({t: Z[t][(Z[t].index >= "2026-04-01") & (Z[t].index <= "2026-06-30")].mean() for t in q2.index})
c = lambda a, b: (lambda x: np.corrcoef(x.iloc[:, 0].rank(), x.iloc[:, 1].rank())[0, 1])(pd.concat([a, b], axis=1).dropna())
obs = c(mean_z, q2.net_clean)
x = pd.concat([mean_z, q2.net_clean], axis=1).dropna()
r1, r2 = x.iloc[:, 0].rank().to_numpy(), x.iloc[:, 1].rank().to_numpy()
p = (1 + sum(np.corrcoef(rng.permutation(r1), r2)[0, 1] >= obs for _ in range(20000))) / 20001
cols = pd.concat([v.gt(0).mean() for v in V.values()], axis=1).fillna(0).mean(axis=1)
pool = sorted(k for k, v in cols.items() if k not in venues and v >= 0.5)
eff = []
for _ in range(200):
    pick = list(rng.choice(pool, 4, replace=False))
    z2 = {}
    for t in q2.index:
        u = V[t].reindex(columns=pick, fill_value=0.0).sum(axis=1)
        zz = z_of(u, W[t][1])
        z2[t] = zz[(zz.index >= "2026-04-01") & (zz.index <= "2026-06-30")].mean()
    eff.append(c(pd.Series(z2), q2.net_clean))
eff = np.array(eff)
print(f"rank corr {obs:+.3f} | p {p:.4f} | placebo p95 {np.percentile(eff,95):+.3f} | real at percentile {(eff<obs).mean()*100:.1f} | {'PASS' if p<0.05 and obs>0 and (eff<obs).mean()>0.95 else 'FAIL'}")

print("\n=== U2 buy test, 13 weeks ===")
rows = []
for t in d1["raw"]:
    p_ = px[t]
    wkc = p_.groupby(p_.index - pd.to_timedelta(p_.index.day_of_week, unit="D")).last()
    lo = wkc.rolling(52, min_periods=40).min()
    for wk2, z in Z[t].dropna().items():
        i = p_.index.searchsorted(wk2 + pd.Timedelta(days=21))
        if i >= len(p_):
            continue
        e = p_.index[i]; j = p_.index.searchsorted(e + pd.Timedelta(weeks=13))
        if j >= len(p_) or e not in spy.index or p_.index[j] not in spy.index or wk2 not in lo.index or lo[wk2] != lo[wk2]:
            continue
        x2 = p_.index[j]
        rows.append({"t": t, "e": e, "z": z, "near": wkc[wk2] / lo[wk2] - 1 <= 0.10, "r": (p_[x2] / p_[e] - 1) * 100, "x": (p_[x2] / p_[e] - spy[x2] / spy[e]) * 100})
A = pd.DataFrame(rows)


def thin(g):
    keep, last = [], None
    for i, e in g.sort_values("e").e.items():
        if last is None or (e - last).days >= 91:
            keep.append(i); last = e
    return g.loc[keep]


def report(name, mask, base):
    picks = pd.concat([thin(g) for _, g in A[mask].groupby("t")])
    oth = A[base & ~mask & A.t.isin(picks.t)]
    groups = {t: g.x.to_numpy() for t, g in A[base].groupby("t")}
    total = np.zeros(10000); n = 0
    for t, k in picks.groupby("t").size().items():
        v = groups[t]; idx = np.argsort(rng.random((10000, len(v))), axis=1)[:, :k]; total += v[idx].sum(axis=1); n += k
    perm = total / n; ob = picks.x.mean()
    pv = (1 + (np.abs(perm - perm.mean()) >= abs(ob - perm.mean())).sum()) / 10001
    mid = picks.e.median(); a, b = picks[picks.e <= mid], picks[picks.e > mid]
    win, base_win = (picks.r > 0).mean() * 100, (oth.r > 0).mean() * 100
    ok = win >= base_win + 5 and picks.x.median() > 0 and pv < 0.05 and a.x.median() > 0 and b.x.median() > 0
    print(f"{name}: n {len(picks)} | up {win:.0f}% vs {base_win:.0f}% | beat SPY {(picks.x>0).mean()*100:.0f}% vs {(oth.x>0).mean()*100:.0f}% | median ret {picks.r.median():+.1f}% vs {oth.r.median():+.1f}% | median excess {picks.x.median():+.1f}% vs {oth.x.median():+.1f}% | worst {picks.r.min():.0f}% | p {pv:.3f} | halves {a.x.median():+.1f}/{b.x.median():+.1f} | {'PASS' if ok else 'FAIL'}")


everything = pd.Series(True, index=A.index)
report("(a) z_usd>=2 anywhere", A.z >= 2, everything)
report("(b) z_usd>=2 near low ", (A.z >= 2) & A.near, A.near)
report("(c) near low, no signal baseline check", A.near & (A.z < 2), everything)
