# Pre-set rule, written before seeing results: across all tickers, for the quarter Nasdaq's
# holdings data covers, block activity must rank positively with 13F institutional change.
# H1 net: (increased - decreased shares) / shares outstanding vs active weeks and mean z_block.
# H2 gross: (increased + decreased shares) / shares outstanding vs the same.
# Pass: Spearman rank correlation above 0 with permutation p < 0.05. One run only.
import datetime as dt
import json
import pickle
import re
import sys
import time
import urllib.request
from collections import Counter

sys.path.insert(0, ".")
import numpy as np
import pandas as pd
import whale_chart as wc
import whale_watch as ww

pd.set_option("display.width", 180); pd.set_option("display.max_columns", 30); pd.set_option("display.max_rows", 120)
rng = np.random.default_rng(20261031)
HDR = {"User-Agent": "Mozilla/5.0", "Accept": "application/json", "Accept-Encoding": "identity"}
CFG = dict(ww.PRESETS["finra"]["medium"])
d1 = pickle.load(open("proof_data.pkl", "rb"))
d2 = pickle.load(open("signal_data.pkl", "rb"))
d3 = pickle.load(open("ranges.pkl", "rb"))
venues = d3["venues"]
raw = {**d2["raw"], **d1["raw"], **d3["raw"]}
ETF = {"SPY", "IWM"}
print("tickers", len(raw))


def get(sym, limit):
    url = f"https://api.nasdaq.com/api/company/{sym}/institutional-holdings?limit={limit}&type=TOTAL&sortColumn=marketValue"
    return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=40).read().decode())["data"]


num = lambda s: float(re.sub(r"[^0-9.]", "", str(s)) or 0)
full = get("MSFT", 7000)
rows = full["holdingsTransactions"]["table"]["rows"]
print("MSFT holder rows", len(rows), "| filing dates, top 6:", Counter(r["date"] for r in rows).most_common(6))
chg = [float(re.sub(r"[^0-9.\-]", "", str(r["sharesChange"])) or 0) for r in rows]
print("sum of positive changes", round(sum(c for c in chg if c > 0)), "| negative", round(sum(c for c in chg if c < 0)))
top = sorted(rows, key=lambda r: -float(re.sub(r"[^0-9.\-]", "", str(r["sharesChange"])) or 0))[:4]
print("largest adds:", [(r["ownerName"], r["date"], r["sharesChange"]) for r in top])
q_end = pd.Timestamp(Counter(r["date"] for r in rows).most_common(1)[0][0])
print("quarter tested ends", q_end.date())

H = {}
for t in raw:
    if t in ETF:
        continue
    try:
        x = get(t, 1)
        a = {r["positions"]: r for r in x["activePositions"]["rows"]}
        n = {r["positions"]: r for r in x["newSoldOutPositions"]["rows"]}
        H[t] = {"out": num(x["ownershipSummary"]["ShareoutstandingTotal"]["value"]) * 1e6,
                "inc": num(a["Increased Positions"]["shares"]), "dec": num(a["Decreased Positions"]["shares"]),
                "inc_h": num(a["Increased Positions"]["holders"]), "dec_h": num(a["Decreased Positions"]["holders"]),
                "new": num(n["New Positions"]["shares"]), "sold": num(n["Sold Out Positions"]["shares"])}
    except Exception as e:
        print(t, "skip", repr(e)[:90])
    time.sleep(0.4)
h = pd.DataFrame(H).T
h["net_%"] = 100 * (h.inc - h.dec) / h.out
h["gross_%"] = 100 * (h.inc + h.dec) / h.out
pickle.dump(h, open("holdings.pkl", "wb"))

q_start = q_end - pd.offsets.QuarterEnd(1) + pd.Timedelta(days=1)
print("quarter", q_start.date(), "to", q_end.date(), "| tickers with holdings", len(h))
rows2 = {}
for t in h.index:
    w = ww.finra_ticker_weekly(raw[t])
    w["block_dollars"] = ww.finra_block_weekly(raw[t], venues).reindex(w.index).fillna(0.0)
    sc, _ = ww.score_finra(w, pd.DataFrame(), CFG, 26)
    per = wc.find_periods(sc, CFG["z_block"])
    act = pd.Series(False, index=sc.index)
    for p in per:
        act[p["start"]:p["end"]] = True
    q = sc[(sc.index >= q_start) & (sc.index <= q_end)]
    rows2[t] = {"active_wks": int(act.loc[q.index].sum()), "mean_z": q["z_block"].mean(), "weeks": len(q)}
a = pd.DataFrame(rows2).T.join(h)
print(a[["net_%", "gross_%", "active_wks", "mean_z"]].describe().loc[["min", "50%", "max"]].round(2))


def spear(x, y, n=20000):
    d = pd.concat([x, y], axis=1).dropna()
    r1, r2 = d.iloc[:, 0].rank().to_numpy(), d.iloc[:, 1].rank().to_numpy()
    obs = np.corrcoef(r1, r2)[0, 1]
    perm = np.array([np.corrcoef(rng.permutation(r1), r2)[0, 1] for _ in range(n)])
    return obs, (1 + (perm >= obs).sum()) / (n + 1), len(d)


print("\n=== result, one-sided p ===")
for out in ("net_%", "gross_%"):
    for sig in ("active_wks", "mean_z"):
        o, p, n = spear(a[sig], a[out])
        print(f"{out:8} vs {sig:10}: rank corr {o:+.3f} | p {p:.3f} | n {n} | {'PASS' if p < 0.05 and o > 0 else 'FAIL'}")
print("\n=== net institutional change by active weeks in the quarter ===")
a["group"] = pd.cut(a.active_wks, [-1, 0, 2, 99], labels=["0 weeks", "1-2 weeks", "3+ weeks"])
print(a.groupby("group", observed=True).agg(tickers=("net_%", "size"), median_net=("net_%", "median"), median_gross=("gross_%", "median"),
                                            pct_net_buying=("net_%", lambda s: 100 * (s > 0).mean())).round(2))
show = [t for t in ["MSFT", "NVDA", "AAPL", "AMZN", "META", "TSLA", "ORCL", "JPM", "XOM"] if t in a.index]
print("\n", a.loc[show, ["inc_h", "dec_h", "inc", "dec", "new", "sold", "net_%", "active_wks", "mean_z"]].round(2).to_string())

print("\n=== ORCL latest week under different baselines ===")
for t in ("ORCL",):
    for b in (13, 26, 39, 52):
        w = ww.finra_ticker_weekly(raw[t])
        w["block_dollars"] = ww.finra_block_weekly(raw[t], venues).reindex(w.index).fillna(0.0)
        sc, _ = ww.score_finra(w, pd.DataFrame(), CFG, b)
        print(f"baseline {b}: normal {100*sc.block_normal.iloc[-1]:.2f}% | z {sc.z_block.iloc[-1]:.2f} | status {wc.current_status(sc, wc.find_periods(sc, 2.0))['state']}")
