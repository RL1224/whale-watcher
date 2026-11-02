# The pre-set MSFT comparison, then shortcut accuracy against complete days.
import datetime as dt
import pickle

import numpy as np
import pandas as pd

pd.set_option("display.width", 170); pd.set_option("display.max_columns", 20); pd.set_option("display.max_rows", 60)
c = pickle.load(open("prints_cache.pkl", "rb"))
rows, blocks = [], []
for (sym, day, _), v in sorted(c.items()):
    if not v or not v["summ"]:
        continue
    s = v["summ"]
    rows.append({"day": day, "rows": v["rows"], "day_$B": s["day_$M"] / 1e3, "cutoff_$M": s["block_cutoff_$"] / 1e6, "blocks": s["blocks"], "block_$M": s["block_$M"], "buy_$M": s["buy_lean_$M"], "sell_$M": s["sell_lean_$M"],
                 "mid_$M": s["block_$M"] - s["buy_lean_$M"] - s["sell_lean_$M"], "share_%": s["block_share_%"], "flag": s["flag"]})
    if len(v["blocks"]):
        blocks.append(v["blocks"].assign(day=day))
d = pd.DataFrame(rows).set_index("day")
d["net_$M"] = d["buy_$M"] - d["sell_$M"]
print(d.round(2).to_string())
print("days", len(d), "| log failures:", sum("FAILED" in l for l in open("prints_msft_none.log", encoding="utf-8", errors="replace")))
low, high = d[d.index < "2026-08-01"], d[d.index >= "2026-08-01"]
for name, x in (("LOW  Jun 15-30", low), ("HIGH Oct 5-16", high)):
    b, s = x["buy_$M"].sum(), x["sell_$M"].sum()
    print(f"{name}: days {len(x)} | blocks {int(x.blocks.sum())} | block ${x['block_$M'].sum():.0f}M | buy ${b:.0f}M | sell ${s:.0f}M | mid ${x['mid_$M'].sum():.0f}M | net ${b-s:+.0f}M | imbalance {(b-s)/(b+s) if b+s else 0:+.2f} | share of volume {100*x['block_$M'].sum()/(1e3*x['day_$B'].sum()):.2f}%")
nl, nh = low["net_$M"].sum(), high["net_$M"].sum()
il = nl / max(1e-9, low["buy_$M"].sum() + low["sell_$M"].sum()); ih = nh / max(1e-9, high["buy_$M"].sum() + high["sell_$M"].sum())
print("PRE-SET RULE:", "PASS" if nl > 0 and il > ih else "FAIL", "(net positive at the low, and better than at the high)")

rng = np.random.default_rng(20261104)
B = pd.concat(blocks)
B["window"] = np.where(B.day < "2026-08-01", "low", "high")
sign = B.lean.map({"buy?": 1, "sell?": -1, "mid": 0}).to_numpy() * B.notional.to_numpy()
is_low = (B.window == "low").to_numpy()
abs_ = np.abs(sign)
stat = lambda m: sign[m].sum() / max(1, abs_[m].sum()) - sign[~m].sum() / max(1, abs_[~m].sum())
obs = stat(is_low)
perm = np.array([stat(rng.permutation(is_low)) for _ in range(20000)])
print(f"imbalance gap low minus high {obs:+.2f} | shuffle p {(1+(perm>=obs).sum())/20001:.3f} | blocks {len(B)}")
print("largest blocks:")
print(B.sort_values("notional", ascending=False).head(10).assign(M=lambda x: (x.notional / 1e6).round(1))[["ts", "M", "pieces", "p", "ref_px", "lean"]].to_string(index=False))

b = pickle.load(open("msft_bars.pkl", "rb"))
ny = b.ts.dt.tz_convert("America/New_York")
b["mins"] = ny.dt.hour * 60 + ny.dt.minute
b["range_bp"] = 1e4 * (b.h - b.l) / b.vw
b["typ_range"] = b.groupby("day")["range_bp"].transform("median").clip(lower=0.1)
core = (b.mins >= 575) & (b.mins < 955)
b["calm"] = (b.excess / (1 + b.range_bp / b.typ_range)).where(core)
b["r"] = b.groupby("day")["calm"].rank(ascending=False)
print("\n=== shortcut accuracy against complete days ===")
ranks, usd = [], []
for _, x in B.iterrows():
    m = b[(b.ts >= x.ts.floor("min") - pd.Timedelta(minutes=1)) & (b.ts <= x.ts.floor("min") + pd.Timedelta(minutes=1))]
    ranks.append(m.r.min() if len(m) else np.nan); usd.append(x.notional)
ranks, usd = np.array(ranks, dtype=float), np.array(usd)
print("bars cover through", b.day.max(), "| blocks with a bar", int(np.isfinite(ranks).sum()), "of", len(ranks))
for k in (10, 20, 40, 60):
    f = ranks <= k
    print(f"top {k:2} minutes a day: {100*np.mean(f[np.isfinite(ranks)]):.0f}% of blocks | {100*usd[f].sum()/usd[np.isfinite(ranks)].sum():.0f}% of block dollars | requests per stock-year if every day: {k*251}")
g = pd.Series(ranks).groupby(pd.Series(B.day.to_numpy())).min()
print("calm-excess day rank vs block dollars across complete days:")
daily = b.groupby("day").calm.apply(lambda s: s.clip(lower=0).sum())
daily.index = daily.index.astype(str)
j = pd.concat([daily.rename("calm"), d["block_$M"]], axis=1).dropna()
print("rank corr", round(j.calm.rank().corr(j["block_$M"].rank()), 2), "| days", len(j))
