# Does the Q2 link survive with brand-new positions removed? Same test, same bars as V1, V3, V4.
import pickle
import sys
import time

sys.path.insert(0, ".")
import numpy as np
import pandas as pd
import whale_watch as ww

pd.set_option("display.width", 170); pd.set_option("display.max_columns", 20)
rng = np.random.default_rng(20261101)
tabs = pickle.load(open("holdings_tabs.pkl", "rb")); h = pickle.load(open("holdings.pkl", "rb"))
d1 = pickle.load(open("proof_data.pkl", "rb")); d2 = pickle.load(open("signal_data.pkl", "rb")); d3 = pickle.load(open("ranges.pkl", "rb"))
raw = {**d2["raw"], **d1["raw"], **d3["raw"]}; venues = d3["venues"]
t = tabs["Q2"].copy()
rows = {}
for s in t.index:
    x = ww.fetch_holdings(s)
    if x:
        q = pd.DataFrame(x["rows"]); q = q[q["date"] == "6/30/2026"]
        old = q[~q["new"]]
        rows[s] = {"net_clean": 100 * old["change"].sum() / x["outstanding"], "new_pct": 100 * q.loc[q["new"], "change"].sum() / x["outstanding"]}
    time.sleep(0.5)
c = pd.DataFrame(rows).T
t = t.join(c)
pickle.dump(t, open("q2_clean.pkl", "wb"))
print("tickers", int(t.net_clean.notna().sum()), "| median net all", round(t.net.median(), 3), "| median net existing only", round(t.net_clean.median(), 3), "| median new", round(t.new_pct.median(), 3))


def perm(a, b, n=20000):
    d = pd.concat([a, b], axis=1).dropna()
    r1, r2 = d.iloc[:, 0].rank().to_numpy(), d.iloc[:, 1].rank().to_numpy()
    o = np.corrcoef(r1, r2)[0, 1]
    return o, (1 + sum(np.corrcoef(rng.permutation(r1), r2)[0, 1] >= o for _ in range(n))) / (n + 1)


o, p = perm(t.z, t.net_clean)
print(f"existing holders only vs z: rank corr {o:+.3f} | p {p:.4f}")
o2, p2 = perm(t.z, t.new_pct)
print(f"new positions only vs z:    rank corr {o2:+.3f} | p {p2:.4f}")
d = t.dropna(subset=["net_clean", "z", "ret", "dark"])
r = d[["net_clean", "z", "ret", "dark"]].rank()
X = np.column_stack([np.ones(len(r)), r["ret"], r["dark"]])
res = lambda y: y - X @ np.linalg.lstsq(X, y, rcond=None)[0]
o3, p3 = perm(pd.Series(res(r["z"].to_numpy())), pd.Series(res(r["net_clean"].to_numpy())))
print(f"after return and dark volume: {o3:+.3f} | p {p3:.4f}")
t["bin"] = pd.qcut(t.z, 3, labels=["lowest third", "middle third", "highest third"])
print(t.groupby("bin", observed=True).agg(tickers=("net_clean", "size"), median_net=("net_clean", "median"), pct_net_buying=("net_clean", lambda s: 100 * (s > 0).mean())).round(2).to_string())


def vm(x):
    f = x[x["summarytypecode"] == "ATS_W_SMBL_FIRM"].sort_values("lastupdatedate").drop_duplicates(["weekstartdate", "mpid"], keep="last").copy()
    f["wk"] = pd.to_datetime(f["weekstartdate"])
    return f.pivot_table(index="wk", columns="mpid", values="totalnotionalsum", aggfunc="sum").fillna(0.0)


CFG = dict(ww.PRESETS["finra"]["medium"])
W, V = {}, {}
for s in t.index:
    w = ww.finra_ticker_weekly(raw[s])
    W[s] = w
    V[s] = vm(raw[s]).reindex(w.index).fillna(0.0)
pool = sorted(c2 for c2, v in pd.concat([v.gt(0).mean() for v in V.values()], axis=1).fillna(0).mean(axis=1).items() if c2 not in venues and v >= 0.5)
effs = []
for _ in range(200):
    pick = list(rng.choice(pool, 4, replace=False))
    zs = {}
    for s, w in W.items():
        share = V[s].reindex(columns=pick, fill_value=0.0).sum(axis=1) / w["dollars"]
        z = pd.Series(ww.robust_z(np.log(share.where(share > 0)), 26, 13), index=w.index)
        zs[s] = z[(z.index >= "2026-04-01") & (z.index <= "2026-06-30")].mean()
    x = pd.concat([pd.Series(zs), t.net_clean], axis=1).dropna()
    effs.append(np.corrcoef(x.iloc[:, 0].rank(), x.iloc[:, 1].rank())[0, 1])
effs = np.array(effs)
print(f"placebo median {np.median(effs):+.3f} | p95 {np.percentile(effs,95):+.3f} | real at percentile {(effs < o).mean()*100:.1f}")
print("VERDICT Q2 existing-only:", "PASS" if p < 0.05 and o > 0 and (effs < o).mean() > 0.95 and p3 < 0.05 and o3 > 0 else "FAIL")
