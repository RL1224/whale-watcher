# Owner's reality check: highlighted weeks should sit at relatively low prices. Price is NOT in the score.
# Rule set before running. 60 fresh stocks. Position = where the adjusted close sits in its trailing 52-week
# high-low range, 0% at the low and 100% at the high. Active weeks follow the chart's rule (medium, score >= 2
# starts a period). PASS: active weeks sit lower than the same ticker's other weeks, one-sided p < 0.05 from
# 10,000 random circular shifts of each ticker's active weeks (this keeps periods clustered).
import pickle
import sys

sys.path.insert(0, ".")
import numpy as np
import pandas as pd
import whale_chart as wc
import whale_watch as ww

pd.set_option("display.width", 170); pd.set_option("display.max_columns", 30); pd.set_option("display.max_rows", 90)
rng = np.random.default_rng(20261102)
d = pickle.load(open("proof_data.pkl", "rb"))
px = pickle.load(open("buy_px.pkl", "rb"))
venues, mkt = d["venues"], d["mkt"]
CFG = dict(ww.PRESETS["finra"]["medium"])
T = {}
pers = []
for t, raw in d["raw"].items():
    w = ww.finra_ticker_weekly(raw)
    w["block_dollars"] = ww.finra_block_weekly(raw, venues).reindex(w.index).fillna(0.0)
    sc = wc.with_score(ww.score_finra(w, mkt, CFG, 26)[0])
    periods = wc.find_periods(sc, CFG["z_block"], col="score")
    p = px[t]
    close = p.groupby(p.index - pd.to_timedelta(p.index.day_of_week, unit="D")).last()
    hi, lo = close.rolling(52, min_periods=40).max(), close.rolling(52, min_periods=40).min()
    pos = (100 * (close - lo) / (hi - lo)).reindex(sc.index)
    act = pd.Series(False, index=sc.index)
    for q in periods:
        act[q["start"]:q["end"]] = True
        f = close[close.index >= q["end"]]
        fwd = (f.iloc[13] / f.iloc[0] - 1) * 100 if len(f) > 13 else np.nan
        pers.append({"t": t, "start": q["start"], "weeks": q["weeks"], "peak": q["peak_z"], "pos_start": pos.get(q["start"], np.nan),
                     "pos_mean": pos[q["start"]:q["end"]].mean(), "fwd13": fwd})
    ok = sc["score"].notna() & pos.notna()
    T[t] = pd.DataFrame({"a": act[ok], "pos": pos[ok]})

A = pd.concat([x.assign(t=k) for k, x in T.items()])
act, oth = A[A.a], A[~A.a]
print("tickers", len(T), "| scored weeks", len(A), "| active weeks", len(act), f"({100*len(act)/len(A):.1f}%) | periods", len(pers))
print(f"median position: active {act.pos.median():.1f}% vs other {oth.pos.median():.1f}%")
print(f"in lower third of range: active {100*(act.pos<33.3).mean():.1f}% vs other {100*(oth.pos<33.3).mean():.1f}%")
print(f"in upper third of range: active {100*(act.pos>66.7).mean():.1f}% vs other {100*(oth.pos>66.7).mean():.1f}%")
stat = lambda: np.mean([x.pos[x.a].mean() - x.pos.mean() for x in T.values() if x.a.any()])
obs = stat()
null = np.zeros(10000)
keys = [x for x in T.values() if x.a.any() and len(x) > 10]
for i in range(10000):
    vals = []
    for x in keys:
        a = np.roll(x.a.to_numpy(), rng.integers(1, len(x)))
        vals.append(x.pos.to_numpy()[a].mean() - x.pos.mean())
    null[i] = np.mean(vals)
p = (1 + (null <= obs).sum()) / 10001
print(f"mean gap vs own ticker {obs:+.2f} points | shuffled mean {null.mean():+.2f} | one-sided p {p:.4f} | {'PASS' if obs < 0 and p < 0.05 else 'FAIL'}")

P = pd.DataFrame(pers).dropna(subset=["pos_start"])
print("\n=== by period, where the price was at the start ===")
P["zone"] = pd.cut(P.pos_start, [-1, 33.3, 66.7, 101], labels=["lower third", "middle third", "upper third"])
print(P.groupby("zone", observed=True).agg(periods=("t", "size"), median_fwd13=("fwd13", "median"), pct_up=("fwd13", lambda s: 100 * (s.dropna() > 0).mean()), n_fwd=("fwd13", "count")).round(1).to_string())
print("\n=== same split, all scored weeks (what any week did) ===")
rows = []
for t, x in T.items():
    c = px[t].groupby(px[t].index - pd.to_timedelta(px[t].index.day_of_week, unit="D")).last()
    f = (c.shift(-13) / c - 1).reindex(x.index) * 100
    rows.append(x.assign(fwd=f))
B = pd.concat(rows)
B["zone"] = pd.cut(B.pos, [-1, 33.3, 66.7, 101], labels=["lower third", "middle third", "upper third"])
print(B.groupby("zone", observed=True).agg(weeks=("pos", "size"), median_fwd13=("fwd", "median"), pct_up=("fwd", lambda s: 100 * (s.dropna() > 0).mean())).round(1).to_string())
