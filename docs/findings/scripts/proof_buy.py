# Pre-registered test B: if I bought when this fired, was it a good time?
import json
import os
import pickle
import sys
import time
import urllib.request

sys.path.insert(0, ".")
import numpy as np
import pandas as pd
import whale_watch as ww

pd.set_option("display.width", 180); pd.set_option("display.max_columns", 30); pd.set_option("display.max_rows", 80)
rng = np.random.default_rng(20261030)
N_PERM = 10000
PUBLISH_DAYS = 21          # Tier 1 weekly data is public about 3 weeks after week start
HOLDS = (4, 13, 26)
d = pickle.load(open("proof_data.pkl", "rb"))
venues, mkt = d["venues"], d["mkt"]
CFG = ww.PRESETS["finra"]["low"]


def adj(sym):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=5y&interval=1d"
    j = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=40))["chart"]["result"][0]
    a = j["indicators"]["adjclose"][0]["adjclose"]
    return pd.Series(a, index=pd.to_datetime(j["timestamp"], unit="s", utc=True).tz_convert("America/New_York").tz_localize(None).normalize()).dropna()


if os.path.exists("buy_px.pkl"):
    px = pickle.load(open("buy_px.pkl", "rb"))
else:
    px = {}
    for t in list(d["raw"]) + ["SPY"]:
        px[t] = adj(t); time.sleep(0.3)
    pickle.dump(px, open("buy_px.pkl", "wb"))
spy = px["SPY"]


def on_or_after(s, day):
    i = s.index.searchsorted(day)
    return s.index[i] if i < len(s) else None


rows = []
for t, raw in d["raw"].items():
    w = ww.finra_ticker_weekly(raw)
    if w.empty:
        continue
    w["block_dollars"] = ww.finra_block_weekly(raw, venues).reindex(w.index).fillna(0.0)
    sc, _ = ww.score_finra(w, mkt, CFG, 26)
    p = px[t]
    for wk, r in sc.dropna(subset=["z_block"]).iterrows():
        e = on_or_after(p, wk + pd.Timedelta(days=PUBLISH_DAYS))
        if e is None:
            continue
        row = {"t": t, "wk": wk, "entry": e, "z": r["z_block"], "label": r["label"], "zv": r["z_volume"]}
        for h in HOLDS:
            x = on_or_after(p, e + pd.Timedelta(weeks=h))
            if x is None or e not in spy.index or x not in spy.index or (x - e).days > h * 7 + 5:
                row[f"r{h}"] = row[f"s{h}"] = np.nan
            else:
                row[f"r{h}"] = (p[x] / p[e] - 1) * 100
                row[f"s{h}"] = (spy[x] / spy[e] - 1) * 100
        rows.append(row)
A = pd.DataFrame(rows)
for h in HOLDS:
    A[f"x{h}"] = A[f"r{h}"] - A[f"s{h}"]
print("weeks with an entry", len(A), "| tickers", A.t.nunique(), "| first entry", A.entry.min().date(), "| last", A.entry.max().date())


def thin(g, h):
    keep, last = [], None
    for i, e in g.sort_values("entry").entry.items():
        if last is None or (e - last).days >= h * 7:
            keep.append(i); last = e
    return g.loc[keep]


def stats(x, h):
    return {"n": len(x), "win_%": (x[f"r{h}"] > 0).mean() * 100, "beat_SPY_%": (x[f"x{h}"] > 0).mean() * 100,
            "med_ret": x[f"r{h}"].median(), "mean_ret": x[f"r{h}"].mean(), "med_excess": x[f"x{h}"].median(),
            "mean_excess": x[f"x{h}"].mean(), "worst": x[f"r{h}"].min()}


def permute(picks, base, h):
    """Mean excess of picks vs random weeks of the same tickers, thinned the same way."""
    col = f"x{h}"
    c = base.dropna(subset=[col])
    groups = {t: g[col].to_numpy() for t, g in c.groupby("t")}
    counts = picks.groupby("t").size()
    total = np.zeros(N_PERM); n = 0
    for t, k in counts.items():
        v = groups[t]
        idx = np.argsort(rng.random((N_PERM, len(v))), axis=1)[:, :k]
        total += v[idx].sum(axis=1); n += k
    perm = total / n
    obs = picks[col].mean()
    return obs, perm.mean(), (1 + (np.abs(perm - perm.mean()) >= abs(obs - perm.mean())).sum()) / (N_PERM + 1)


for bar in (3.0, 2.0):
    print(f"\n================ z_block >= {bar:.0f} ================")
    for h in HOLDS:
        base = A.dropna(subset=[f"r{h}", f"s{h}"])
        flagged = base[base.z >= bar]
        picks = pd.concat([thin(g, h) for _, g in flagged.groupby("t")]) if len(flagged) else flagged
        others = base[base.z < bar]
        t = pd.DataFrame({"after_flag": stats(picks, h), "same_tickers_any_other_week": stats(others[others.t.isin(picks.t)], h)}).T.round(2)
        print(f"\n--- hold {h} weeks ---"); print(t.to_string())
        obs, exp, p = permute(picks, base, h)
        mid = picks.entry.median()
        a, b = picks[picks.entry <= mid], picks[picks.entry > mid]
        print(f"mean excess {obs:+.2f}% vs random-week expectation {exp:+.2f}% | p {p:.4f} | median excess by half: early {a[f'x{h}'].median():+.2f}%, late {b[f'x{h}'].median():+.2f}%")
        if h == 13:
            s, o = stats(picks, h), stats(others[others.t.isin(picks.t)], h)
            checks = {"median excess > 0": s["med_excess"] > 0, "win rate +5 pts": s["win_%"] >= o["win_%"] + 5, "p < 0.05": p < 0.05,
                      "both halves > 0": a[f"x{h}"].median() > 0 and b[f"x{h}"].median() > 0}
            print("VERDICT at 13 weeks:", checks, "=>", "PASS" if all(checks.values()) else "FAIL")

print("\n================ exploratory, not pre-registered: accumulation label only, 13 weeks ================")
h = 13
base = A.dropna(subset=["r13", "s13"])
for lab in ("accumulation?", "distribution?"):
    f = base[(base.z >= 3) & (base.label == lab)]
    if f.empty:
        print(lab, "no entries")
        continue
    pk = pd.concat([thin(g, h) for _, g in f.groupby("t")])
    print(lab, {k: round(v, 2) for k, v in stats(pk, h).items()})
pickle.dump(A, open("buy_results.pkl", "wb"))
