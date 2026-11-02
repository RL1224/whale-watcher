# Runs the pre-registered tests G, P, F, D once. See PREREGISTRATION.md.
import pickle
import sys

sys.path.insert(0, ".")
import numpy as np
import pandas as pd
import whale_watch as ww

pd.set_option("display.width", 170); pd.set_option("display.max_columns", 30); pd.set_option("display.max_rows", 80)
SEED, N_PERM, N_PLACEBO, SALE_USD, SET_SIZE = 20261030, 10000, 200, 25e6, 4
rng = np.random.default_rng(SEED)
d = pickle.load(open("proof_data.pkl", "rb"))
venues, mkt = d["venues"], d["mkt"]
CFG = ww.PRESETS["finra"]["low"]


def venue_matrix(raw):
    f = raw[raw["summarytypecode"].astype(str).str.upper() == "ATS_W_SMBL_FIRM"].sort_values("lastupdatedate")
    f = f.drop_duplicates(["weekstartdate", "mpid"], keep="last").copy()
    f["wk"] = pd.to_datetime(f["weekstartdate"])
    return f.pivot_table(index="wk", columns="mpid", values="totalnotionalsum", aggfunc="sum").fillna(0.0)


def big_sale_weeks(ins):
    if ins.empty:
        return pd.Series(dtype=float)
    x = ins.drop_duplicates(["trade", "qty", "price"]).copy()   # joint filers report one sale several times
    x["t"] = pd.to_datetime(x["trade"])
    x["wk"] = x["t"] - pd.to_timedelta(x["t"].dt.day_of_week, unit="D")
    s = x.groupby("wk")["usd"].sum()
    return s[s >= SALE_USD]


T = {}
for t, raw in d["raw"].items():
    w = ww.finra_ticker_weekly(raw)
    if w.empty:
        continue
    w["block_dollars"] = ww.finra_block_weekly(raw, venues).reindex(w.index).fillna(0.0)
    sc, _ = ww.score_finra(w, mkt, CFG, 26)
    T[t] = {"sc": sc, "vm": venue_matrix(raw).reindex(sc.index).fillna(0.0), "events": big_sale_weeks(d["ins"][t]),
            "px": d["px"][t].reindex(sc.index)}

print("=== integrity ===")
print("tickers", len(T), "| failed", d["failed"], "| venues", sorted(venues))
print("scored ticker-weeks", sum(int(v["sc"]["z_block"].notna().sum()) for v in T.values()),
      "| flags z>=3", sum(int((v["sc"]["z_block"] >= 3).sum()) for v in T.values()))


def effect(zs, picks):
    """Mean of z minus the ticker's own mean, across event weeks."""
    vals = []
    for t, z in zs.items():
        ok = z.dropna()
        ev = [w for w in picks.get(t, []) if w in ok.index]
        if ev and len(ok) > len(ev):
            vals.append((ok.loc[ev] - ok.mean()).to_numpy())
    return np.concatenate(vals) if vals else np.array([])


def perm_p(zs, picks):
    """Two-sided within-ticker permutation test of the mean event effect."""
    obs_vals = effect(zs, picks)
    total = np.zeros(N_PERM); n = 0
    for t, z in zs.items():
        ok = z.dropna()
        k = sum(w in ok.index for w in picks.get(t, []))
        if k and len(ok) > k:
            c = (ok - ok.mean()).to_numpy()
            idx = np.argsort(rng.random((N_PERM, len(c))), axis=1)[:, :k]
            total += c[idx].sum(axis=1); n += k
    perm = total / n
    obs = obs_vals.mean()
    p = (1 + (np.abs(perm) >= abs(obs)).sum()) / (N_PERM + 1)
    return obs, p, n


zs = {t: v["sc"]["z_block"] for t, v in T.items()}
events = {t: list(v["events"].index) for t, v in T.items()}

print("\n=== G. ground truth: weeks with $25M+ documented insider sales ===")
obs, p, n = perm_p(zs, events)
vals = effect(zs, events)
boot = [rng.choice(vals, len(vals)).mean() for _ in range(5000)]
tick = sum(1 for t in T if any(w in zs[t].dropna().index for w in events[t]))
allz = pd.concat(zs.values()).dropna()
evz = pd.concat([zs[t].reindex(events[t]) for t in T if events[t]]).dropna()
print(f"event weeks {n} across {tick} tickers | effect {obs:+.3f} z | 95% CI [{np.percentile(boot,2.5):+.3f}, {np.percentile(boot,97.5):+.3f}] | p {p:.4f}")
print(f"median z event {evz.median():.2f} vs all {allz.median():.2f} | z>=3 rate event {(evz>=3).mean()*100:.1f}% vs all {(allz>=3).mean()*100:.1f}% | z>=2 rate event {(evz>=2).mean()*100:.1f}% vs all {(allz>=2).mean()*100:.1f}%")
print("G PASS" if p < 0.05 and obs > 0 else "G FAIL")

print("\n=== P. placebo: same test on random ordinary venues ===")
cols = pd.concat([v["vm"].gt(0).mean() for v in T.values()], axis=1).fillna(0).mean(axis=1)
pool = sorted(c for c in cols.index if c not in venues and cols[c] >= 0.5)
print("ordinary pool", len(pool), pool)
effs = []
for i in range(N_PLACEBO):
    pick = list(rng.choice(pool, SET_SIZE, replace=False))
    zp = {}
    for t, v in T.items():
        share = v["vm"].reindex(columns=pick, fill_value=0.0).sum(axis=1) / v["sc"]["dollars"]
        zp[t] = pd.Series(ww.robust_z(np.log(share.where(share > 0)), 26, 13), index=v["sc"].index)
    e = effect(zp, events)
    effs.append(e.mean() if len(e) else np.nan)
effs = np.array(effs)
pct = (effs < obs).mean() * 100
print(f"placebo effect median {np.nanmedian(effs):+.3f} | p5 {np.nanpercentile(effs,5):+.3f} | p95 {np.nanpercentile(effs,95):+.3f} | real {obs:+.3f} sits at percentile {pct:.1f}")
print("P PASS" if obs > np.nanpercentile(effs, 95) else "P FAIL")

print("\n=== F. forward activity after z>=3 weeks (next 4 weeks) ===")
fv, fr, fl = {}, {}, {}
for t, v in T.items():
    px = v["px"]
    base = px["volume"].rolling(26, min_periods=13).median().shift(1)
    nxt = pd.concat([px["volume"].shift(-k) for k in range(1, 5)], axis=1).mean(axis=1, skipna=False)
    fv[t] = np.log(nxt / base)
    fr[t] = (px["close"].shift(-4) / px["close"] - 1).abs() * 100
    fl[t] = list(v["sc"].index[v["sc"]["z_block"] >= 3])
for name, series in (("log total volume vs baseline", fv), ("absolute 4-week return %", fr)):
    o, pv, k = perm_p({t: s.where(zs[t].notna()) for t, s in series.items()}, fl)
    print(f"{name}: flags {k} | effect {o:+.3f} | p {pv:.4f} | {'PASS' if pv < 0.05 and o > 0 else 'FAIL'}")

print("\n=== D. direction after flagged weeks ===")
rows = []
for t, v in T.items():
    sc, px = v["sc"], v["px"]
    r = (px["close"].shift(-4) / px["close"] - 1) * 100
    f = sc[sc["flag"] & sc["label"].isin(["accumulation?", "distribution?"])]
    rows.append(pd.DataFrame({"label": f["label"], "ret": r.reindex(f.index)}))
x = pd.concat(rows).dropna()
a, b = x[x.label == "accumulation?"].ret, x[x.label == "distribution?"].ret
o = a.mean() - b.mean()
lab = x.ret.to_numpy(); na = len(a)
perm = np.array([(lambda s: s[:na].mean() - s[na:].mean())(rng.permutation(lab)) for _ in range(N_PERM)])
pd_one = (1 + (perm >= o).sum()) / (N_PERM + 1)
print(f"accumulation n={len(a)} mean {a.mean():+.2f}% median {a.median():+.2f}% | distribution n={len(b)} mean {b.mean():+.2f}% median {b.median():+.2f}% | diff {o:+.2f} | one-sided p {pd_one:.4f} | {'PASS' if pd_one < 0.05 else 'FAIL'}")

print("\n=== exploratory, not pre-registered ===")
for usd in (10e6, 100e6, 250e6):
    pk = {t: [w for w, a2 in big_sale_weeks(d["ins"][t]).items() if a2 >= usd] if usd >= SALE_USD else [] for t in T}
    if usd < SALE_USD:
        continue
    o2, p2, n2 = perm_p(zs, pk)
    print(f"sale >= ${usd/1e6:.0f}M: weeks {n2} | effect {o2:+.3f} | p {p2:.4f}")
prec = [(w in set(events[t])) for t in T for w in fl[t]]
base = np.mean([w in set(events[t]) for t in T for w in zs[t].dropna().index])
print(f"z>=3 weeks that contain a $25M+ sale: {np.mean(prec)*100:.1f}% vs {base*100:.1f}% of all scored weeks")
per = pd.Series({t: (effect({t: zs[t]}, events).mean() if events[t] and len(effect({t: zs[t]}, events)) else np.nan) for t in T}).dropna()
print(f"tickers with events: {len(per)} | positive effect in {(per>0).sum()} | most events:",
      {t: int(sum(w in zs[t].dropna().index for w in events[t])) for t in sorted(T, key=lambda q: -len(events[q]))[:6]})
