# Head to head: block share only (old) vs share-or-dollars (new), same stocks, same tests.
import pickle
import sys

sys.path.insert(0, ".")
import numpy as np
import pandas as pd
import whale_chart as wc
import whale_watch as ww

pd.set_option("display.width", 170); pd.set_option("display.max_columns", 20)
rng = np.random.default_rng(20261103)
d = pickle.load(open("proof_data.pkl", "rb"))
px = pickle.load(open("buy_px.pkl", "rb")); spy = px["SPY"]
q2 = pickle.load(open("q2_clean.pkl", "rb"))
venues, mkt = d["venues"], d["mkt"]
CFG = dict(ww.PRESETS["finra"]["medium"])
S = {}
for t, raw in d["raw"].items():
    w = ww.finra_ticker_weekly(raw)
    w["block_dollars"] = ww.finra_block_weekly(raw, venues).reindex(w.index).fillna(0.0)
    S[t] = wc.with_score(ww.score_finra(w, mkt, CFG, 26)[0])


def weekly_close(t):
    p = px[t]
    return p.groupby(p.index - pd.to_timedelta(p.index.day_of_week, unit="D")).last()


def run(col, name):
    entries, active, total, big_hit, big_all = [], 0, 0, 0, 0
    for t, sc in S.items():
        per = wc.find_periods(sc, CFG["z_block"], col=col)
        c = weekly_close(t)
        lo, hi = c.rolling(52, min_periods=40).min(), c.rolling(52, min_periods=40).max()
        pos = 100 * (c - lo) / (hi - lo)
        act = pd.Series(False, index=sc.index)
        for q in per:
            act[q["start"]:q["end"]] = True
        move = c.pct_change().abs().reindex(sc.index) * 100
        ok = sc[col].notna()
        active += int(act[ok].sum()); total += int(ok.sum())
        big = (move >= 10) & ok
        big_all += int(big.sum()); big_hit += int((big & act).sum())
        p = px[t]
        last = None
        for q in per:
            i = p.index.searchsorted(q["start"] + pd.Timedelta(days=21))
            if i >= len(p):
                continue
            e = p.index[i]
            j = p.index.searchsorted(e + pd.Timedelta(weeks=13))
            if j >= len(p) or e not in spy.index or p.index[j] not in spy.index or (last is not None and (e - last).days < 91):
                continue
            x = p.index[j]; last = e
            entries.append({"t": t, "r": (p[x] / p[e] - 1) * 100, "x": (p[x] / p[e] - spy[x] / spy[e]) * 100, "pos": pos.get(q["start"], np.nan)})
    E = pd.DataFrame(entries)
    low = E[E.pos < 33.4]
    q = pd.Series({t: S[t].loc["2026-04-01":"2026-06-30", col].mean() for t in S if t in q2.index})
    x = pd.concat([q, q2.net_clean], axis=1).dropna()
    rc = np.corrcoef(x.iloc[:, 0].rank(), x.iloc[:, 1].rank())[0, 1]
    return {"": name, "active_%": round(100 * active / total, 1), "10%_weeks_caught_%": round(100 * big_hit / big_all), "entries": len(E), "up_%": round((E.r > 0).mean() * 100), "beat_SPY_%": round((E.x > 0).mean() * 100),
            "med_ret": round(E.r.median(), 1), "low_entries": len(low), "low_up_%": round((low.r > 0).mean() * 100), "low_med": round(low.r.median(), 1), "13F_corr": round(rc, 2), "n13F": len(x)}


base = []
for t, sc in S.items():
    p = px[t]
    for wk in sc.dropna(subset=["score"]).index:
        i = p.index.searchsorted(wk + pd.Timedelta(days=21))
        if i >= len(p):
            continue
        e = p.index[i]; j = p.index.searchsorted(e + pd.Timedelta(weeks=13))
        if j < len(p):
            base.append((p[p.index[j]] / p[e] - 1) * 100)
base = np.array(base)
print(pd.DataFrame([run("z_block", "old: block share"), run("score", "new: share or dollars")]).to_string(index=False))
print(f"any week, same stocks: up {100*(base>0).mean():.0f}% | median {np.median(base):+.1f}%")
