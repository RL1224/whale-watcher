#!/usr/bin/env python3
"""
whale_watch.py - free scanner for "are big players active in this stock/ETF?"

It does NOT identify buyers. It measures large-size activity two ways:

  finra   FINRA weekly dark-pool (ATS) data. Free, no key. Delayed ~2-4 weeks.
          Long-term signal: weeks where this ticker's dark-pool dollar volume
          AND average trade size are far above ITS OWN normal, after removing
          market-wide swings (holidays, sell-offs, index rebalances).

  prints  Recent large off-exchange prints via Alpaca's FREE plan (full-market
          data delayed 15+ min). Needs free Alpaca API keys.
          Short-term signal: days where real blocks are a large share of the
          day's dollar volume and lean clearly one way.

Sensitivity (--sensitivity low | medium | high, default low)
  low     only rare, sustained, clearly abnormal periods (few false alarms)
  medium  balanced
  high    catches more, noisier
  Every threshold can still be overridden individually (see --help per mode).

Smart adjustments (automatic):
  - Thresholds scale with each stock's own volume and trade-size history, so
    the same setting works for a $5B small cap and a $500B mega cap.
  - Dollar values, not share counts: price level and stock splits don't distort it.
  - Robust statistics (median/MAD on log values): one freak week can't skew
    the baseline.
  - FINRA mode divides by total market dark-pool activity each week, so
    market-wide volume spikes don't trigger signals.
  - FINRA mode needs the signal to persist several weeks (low sensitivity).
  - Prints mode: block size cutoff = the largest of a dollar floor, a % of
    that day's dollar volume, and a top-percentile of that day's trades.
    Regular hours only. Skips average-price, derivatively-priced, hedge-leg
    and out-of-sequence reports. Re-joins one order split into several
    same-price prints seconds apart, but only from pieces already large,
    so retail flow (also reported off-exchange) can't add up to a fake block.
  - Each flagged period is labelled by price direction (dark-pool average
    price): "accumulation?" if price held/rose, "distribution?" if it fell.

Install:   pip install requests pandas numpy
Examples:
    python whale_watch.py finra ORCL NVDA SPY
    python whale_watch.py finra ORCL --sensitivity medium --weeks 104
    export ALPACA_KEY_ID=...  ALPACA_SECRET_KEY=...
    python whale_watch.py prints ORCL --days 3
Results print to screen and save as CSVs in ./whale_out/.

Caveats: big orders are sliced into small trades, so some activity is always
missed; direction labels are hints, not proof.
"""
import argparse
import datetime as dt
import os
import sys
import time

import numpy as np
import pandas as pd
import requests

OUT_DIR = "whale_out"

# Sensitivity presets. Low = strict.
PRESETS = {
    "finra": {
        #           robust z of volume, robust z of avg trade $, weeks in a row
        "low":    {"z_volume": 3.0, "z_size": 2.0,  "min_streak": 2},
        "medium": {"z_volume": 2.0, "z_size": 1.25, "min_streak": 1},
        "high":   {"z_volume": 1.5, "z_size": 0.75, "min_streak": 1},
    },
    "prints": {
        # block = notional >= max(floor, adv_frac * day $ volume, day quantile)
        # day flagged when block share %, lean imbalance, and block count all pass
        "low":    {"floor": 1_000_000, "adv_frac": 0.0025, "quantile": 0.9999,
                   "min_child": 100_000, "min_share_pct": 3.0,
                   "min_imbalance": 0.40, "min_blocks": 3},
        "medium": {"floor": 500_000, "adv_frac": 0.0010, "quantile": 0.999,
                   "min_child": 50_000, "min_share_pct": 1.5,
                   "min_imbalance": 0.25, "min_blocks": 2},
        "high":   {"floor": 200_000, "adv_frac": 0.0005, "quantile": 0.995,
                   "min_child": 25_000, "min_share_pct": 0.75,
                   "min_imbalance": 0.15, "min_blocks": 1},
    },
}


def resolve(mode, args):
    """Start from the preset, then apply any per-setting overrides."""
    cfg = dict(PRESETS[mode][args.sensitivity])
    for k in cfg:
        v = getattr(args, k, None)
        if v is not None:
            cfg[k] = v
    return cfg


def robust_z(values, window, min_periods):
    """z-score of each point vs. the previous `window` points, using
    median and MAD so outliers in the history don't distort the baseline."""
    v = np.asarray(values, dtype=float)
    out = np.full(len(v), np.nan)
    for i in range(len(v)):
        hist = v[max(0, i - window):i]
        hist = hist[~np.isnan(hist)]
        if len(hist) < min_periods or np.isnan(v[i]):
            continue
        med = np.median(hist)
        scale = 1.4826 * np.median(np.abs(hist - med))
        if scale == 0:
            scale = hist.std()
        if scale > 0:
            out[i] = (v[i] - med) / scale
    return out


def streaks(flags):
    run, out = 0, []
    for f in flags:
        run = run + 1 if f else 0
        out.append(run)
    return out


# ---------------------------------------------------------------- FINRA ----

FINRA_URL = "https://api.finra.org/data/group/otcMarket/name/weeklySummary"
FINRA_TOKEN_URL = ("https://ews.fip.finra.org/fip/rest/ews/oauth2/access_token"
                   "?grant_type=client_credentials")
FINRA_PAGE = 5000


def finra_headers():
    """Public data needs no key. If FINRA ever requires one, set
    FINRA_CLIENT_ID / FINRA_CLIENT_SECRET (free account at developer.finra.org)."""
    h = {"Content-Type": "application/json", "Accept": "application/json"}
    cid, secret = os.getenv("FINRA_CLIENT_ID"), os.getenv("FINRA_CLIENT_SECRET")
    if cid and secret:
        r = requests.post(FINRA_TOKEN_URL, auth=(cid, secret), timeout=30)
        r.raise_for_status()
        h["Authorization"] = "Bearer " + r.json()["access_token"]
    return h


def fetch_finra(filters, start, end, headers):
    rows, offset = [], 0
    while True:
        payload = {
            "compareFilters": [{"compareType": "EQUAL", "fieldName": k, "fieldValue": v}
                               for k, v in filters.items()],
            "dateRangeFilters": [{"fieldName": "weekStartDate",
                                  "startDate": start, "endDate": end}],
            "limit": FINRA_PAGE,
            "offset": offset,
        }
        r = requests.post(FINRA_URL, json=payload, headers=headers, timeout=60)
        if r.status_code in (401, 403):
            sys.exit("FINRA refused the request (auth). Create a free account at "
                     "developer.finra.org, set FINRA_CLIENT_ID and "
                     "FINRA_CLIENT_SECRET, and re-run.")
        if r.status_code == 204 or not r.text.strip():
            break
        r.raise_for_status()
        page = r.json()
        rows.extend(page)
        if len(page) < FINRA_PAGE:
            break
        offset += FINRA_PAGE
    df = pd.DataFrame(rows)
    df.columns = [c.lower() for c in df.columns]
    for c in ("totalweeklysharequantity", "totalweeklytradecount", "totalnotionalsum"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def finra_ticker_weekly(df):
    """One row per week: this ticker's total dark-pool shares, trades, dollars."""
    if df.empty:
        return pd.DataFrame()
    types = df["summarytypecode"].astype(str).str.upper()
    if (types == "ATS_W_SMBL").any():           # per-symbol total, if published
        d, key = df[types == "ATS_W_SMBL"].copy(), ["weekstartdate"]
    else:                                        # otherwise sum the venues
        d = df[types == "ATS_W_SMBL_FIRM"].copy()
        venue = "mpid" if "mpid" in d.columns else "firmcrdnumber"
        key = ["weekstartdate", venue]
    if d.empty:
        return pd.DataFrame()
    if "lastupdatedate" in d.columns:           # keep only the latest revision
        d = d.sort_values("lastupdatedate").drop_duplicates(key, keep="last")
    agg = {"shares": ("totalweeklysharequantity", "sum"),
           "trades": ("totalweeklytradecount", "sum")}
    if "totalnotionalsum" in d.columns:
        agg["dollars"] = ("totalnotionalsum", "sum")
    w = d.groupby("weekstartdate").agg(**agg)
    w.index = pd.to_datetime(w.index)
    return w.sort_index()


def finra_market_weekly(start, end, headers):
    """Market-wide dark-pool totals per week (for normalising). Optional."""
    try:
        m = fetch_finra({"summaryTypeCode": "ATS_W_VOL_STATS"}, start, end, headers)
    except Exception as e:  # noqa: BLE001 - normalisation is a nice-to-have
        print(f"(market normalisation skipped: {e})", file=sys.stderr)
        return pd.DataFrame()
    if m.empty:
        return m
    val = "totalnotionalsum" if "totalnotionalsum" in m.columns else "totalweeklysharequantity"
    # if several rows per week (e.g. per tier), the largest is the overall total
    m = m.sort_values(val).groupby("weekstartdate").last()
    out = pd.DataFrame({"mkt_value": m[val], "mkt_trades": m["totalweeklytradecount"]})
    out.index = pd.to_datetime(out.index)
    return out


def score_finra(w, mkt, cfg, baseline):
    w = w.copy()
    use_dollars = "dollars" in w.columns and w["dollars"].gt(0).all()
    w["value"] = w["dollars"] if use_dollars else w["shares"]
    w["avg_trade"] = w["value"] / w["trades"].where(w["trades"] > 0)
    w["vwap"] = (w["dollars"] / w["shares"]) if use_dollars else np.nan

    vol, size = w["value"].copy(), w["avg_trade"].copy()
    if not mkt.empty:  # remove market-wide swings
        m = mkt.reindex(w.index)
        if m["mkt_value"].notna().sum() >= len(w) * 0.8:
            vol = vol / m["mkt_value"]
            size = size / (m["mkt_value"] / m["mkt_trades"])
    minp = max(8, baseline // 2)
    w["z_volume"] = robust_z(np.log(vol), baseline, minp)
    w["z_size"] = robust_z(np.log(size), baseline, minp)
    w["elevated"] = (w["z_volume"] >= cfg["z_volume"]) & (w["z_size"] >= cfg["z_size"])
    w["streak"] = streaks(w["elevated"])
    w["flag"] = w["streak"] >= cfg["min_streak"]
    # price direction over the run: compare to the 4 weeks before it started
    w["price_chg_%"] = np.nan
    w["label"] = ""
    for i in np.where(w["flag"])[0]:
        start = i - int(w["streak"].iloc[i]) + 1
        before = w["vwap"].iloc[max(0, start - 4):start].mean()
        chg = 100 * (w["vwap"].iloc[i] / before - 1) if before == before else np.nan
        w.iloc[i, w.columns.get_loc("price_chg_%")] = chg
        w.iloc[i, w.columns.get_loc("label")] = (
            "?" if chg != chg else ("accumulation?" if chg >= 0 else "distribution?"))
    return w, use_dollars


def cmd_finra(a):
    cfg = resolve("finra", a)
    end = dt.date.today()
    start = end - dt.timedelta(weeks=a.weeks + a.baseline)
    s, e = start.isoformat(), end.isoformat()
    headers = finra_headers()
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"Sensitivity {a.sensitivity}: volume z>={cfg['z_volume']}, "
          f"trade-size z>={cfg['z_size']}, {cfg['min_streak']}+ weeks in a row, "
          f"baseline {a.baseline} weeks")
    mkt = finra_market_weekly(s, e, headers)
    summary = []
    for sym in (t.upper() for t in a.tickers):
        w = finra_ticker_weekly(fetch_finra({"issueSymbolIdentifier": sym}, s, e, headers))
        if w.empty:
            print(f"\n{sym}: no dark-pool data returned (check the ticker).")
            continue
        w, dollars = score_finra(w, mkt, cfg, a.baseline)
        w = w[w.index >= pd.Timestamp(end - dt.timedelta(weeks=a.weeks))]
        w.to_csv(f"{OUT_DIR}/{sym}_finra_weekly.csv")
        flagged = w[w["flag"]]
        unit = "$" if dollars else "shares"
        print(f"\n{sym}: {len(flagged)} meaningful week(s) in the last {a.weeks} "
              f"(latest data: week of {w.index[-1].date()})")
        if not flagged.empty:
            show = flagged[["value", "avg_trade", "z_volume", "z_size", "streak",
                            "price_chg_%", "label"]].copy()
            show = show.rename(columns={"value": f"dark_{unit}",
                                        "avg_trade": f"avg_trade_{unit}"})
            print(show.round(2).to_string())
        last = w.iloc[-1]
        summary.append({"ticker": sym, "latest_week": w.index[-1].date(),
                        "flagged_weeks": len(flagged),
                        "current_streak": int(last["streak"]),
                        "z_volume_now": round(last["z_volume"], 2),
                        "z_size_now": round(last["z_size"], 2),
                        "last_label": flagged["label"].iloc[-1] if len(flagged) else ""})
    if summary:
        out = pd.DataFrame(summary).sort_values(
            ["current_streak", "flagged_weeks", "z_volume_now"], ascending=False)
        out.to_csv(f"{OUT_DIR}/finra_summary.csv", index=False)
        print("\n=== Ranked ===")
        print(out.to_string(index=False))


# --------------------------------------------------------------- Alpaca ----

ALPACA_URL = "https://data.alpaca.markets/v2/stocks/{sym}/trades"
# Not fresh buying/selling at that moment: average-price (B, W), derivatively
# priced (4), qualified contingent / hedge leg (7), out of sequence (Z, U),
# extended-hours reports (T).
EXCLUDE = {"B", "W", "4", "7", "Z", "U", "T"}
NY = "America/New_York"


def alpaca_headers():
    kid = os.getenv("ALPACA_KEY_ID") or os.getenv("APCA_API_KEY_ID")
    sec = os.getenv("ALPACA_SECRET_KEY") or os.getenv("APCA_API_SECRET_KEY")
    if not (kid and sec):
        sys.exit("Set ALPACA_KEY_ID and ALPACA_SECRET_KEY (free account at alpaca.markets).")
    return {"APCA-API-KEY-ID": kid, "APCA-API-SECRET-KEY": sec}


def fetch_trades(sym, start, end, headers):
    params = {"start": start, "end": end, "limit": 10000, "feed": "sip"}
    out = []
    while True:
        r = requests.get(ALPACA_URL.format(sym=sym), params=params,
                         headers=headers, timeout=60)
        if r.status_code == 429:          # free plan: 200 requests/minute
            time.sleep(5)
            continue
        r.raise_for_status()
        j = r.json()
        out.extend(j.get("trades") or [])
        tok = j.get("next_page_token")
        if not tok:
            break
        params["page_token"] = tok
        time.sleep(0.3)
    return pd.DataFrame(out)


def analyze_day(df, cfg, dark_code="D", cluster_secs=2.0):
    """Summary dict + block rows for one day of trades, using adaptive cutoffs."""
    df = df.copy()
    df["ts"] = pd.to_datetime(df["t"], utc=True, format="ISO8601")
    local = df["ts"].dt.tz_convert(NY)
    mins = local.dt.hour * 60 + local.dt.minute
    df = df[(mins >= 570) & (mins < 960)]          # 9:30-16:00 New York
    if df.empty:
        return None, pd.DataFrame()
    df = df.sort_values("ts").reset_index(drop=True)
    df["notional"] = df["p"] * df["s"]
    lit = df["x"] != dark_code
    df["ref_px"] = df["p"].where(lit).ffill()       # last on-exchange price
    conds = df["c"] if "c" in df.columns else pd.Series([[]] * len(df))
    bad = conds.apply(lambda c: bool(set(c or []) & EXCLUDE))

    day_dollars = df["notional"].sum()
    # percentile of normal on-exchange trades, so the blocks can't set their own bar
    lit_q = df.loc[lit, "notional"].quantile(cfg["quantile"]) if lit.any() else 0
    cutoff = max(cfg["floor"], cfg["adv_frac"] * day_dollars, lit_q)

    # candidate dark pieces, then re-join same-price pieces seconds apart
    d = df[(~lit) & (~bad) & (df["notional"] >= cfg["min_child"])].copy()
    if d.empty:
        blocks = d
    else:
        new = (d["p"] != d["p"].shift()) | \
              (d["ts"].diff().dt.total_seconds().fillna(1e9) > cluster_secs)
        d["grp"] = new.cumsum()
        blocks = d.groupby("grp").agg(ts=("ts", "first"), p=("p", "first"),
                                      s=("s", "sum"), notional=("notional", "sum"),
                                      pieces=("s", "size"), ref_px=("ref_px", "first"))
        blocks = blocks[blocks["notional"] >= cutoff].copy()
    blocks["lean"] = np.sign(blocks["p"] - blocks["ref_px"]).map(
        {1.0: "buy?", -1.0: "sell?", 0.0: "mid"}).fillna("mid")

    buy = blocks.loc[blocks["lean"] == "buy?", "notional"].sum()
    sell = blocks.loc[blocks["lean"] == "sell?", "notional"].sum()
    share = 100 * blocks["notional"].sum() / day_dollars if day_dollars else 0
    imb = (buy - sell) / (buy + sell) if (buy + sell) else 0
    flag = (share >= cfg["min_share_pct"] and abs(imb) >= cfg["min_imbalance"]
            and len(blocks) >= cfg["min_blocks"])
    summ = {"block_cutoff_$": round(cutoff), "blocks": len(blocks),
            "block_$M": blocks["notional"].sum() / 1e6, "block_share_%": share,
            "buy_lean_$M": buy / 1e6, "sell_lean_$M": sell / 1e6,
            "imbalance": imb, "day_$M": day_dollars / 1e6,
            "flag": ("BUY-SIDE?" if imb > 0 else "SELL-SIDE?") if flag else ""}
    return summ, blocks


def cmd_prints(a):
    cfg = resolve("prints", a)
    headers = alpaca_headers()
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"Sensitivity {a.sensitivity}: block >= max(${cfg['floor']:,.0f}, "
          f"{cfg['adv_frac']*100:.2f}% of day $ volume, top "
          f"{(1-cfg['quantile'])*100:.2f}% of trades); day flagged if blocks >= "
          f"{cfg['min_share_pct']}% of volume, imbalance >= {cfg['min_imbalance']}, "
          f"{cfg['min_blocks']}+ blocks")
    now = dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=16)  # free-plan delay
    days, d = [], now.date()
    while len(days) < a.days:
        if d.weekday() < 5:
            days.append(d)
        d -= dt.timedelta(days=1)
    days.reverse()

    for sym in (t.upper() for t in a.tickers):
        rows, all_blocks = [], []
        for day in days:
            start = dt.datetime.combine(day, dt.time(0), dt.timezone.utc)
            end = min(start + dt.timedelta(days=1), now)
            print(f"{sym} {day}: downloading trades...", file=sys.stderr)
            df = fetch_trades(sym, start.isoformat().replace("+00:00", "Z"),
                              end.isoformat().replace("+00:00", "Z"), headers)
            if df.empty:
                continue  # holiday / no data
            summ, blocks = analyze_day(df, cfg, a.dark_code)
            if summ is None:
                continue
            rows.append({"date": day, **summ})
            all_blocks.append(blocks.assign(date=day))
        if not rows:
            print(f"\n{sym}: no trades returned.")
            continue
        daily = pd.DataFrame(rows).set_index("date")
        daily.to_csv(f"{OUT_DIR}/{sym}_prints_daily.csv")
        print(f"\n{sym}")
        print(daily.round(2).to_string())
        b = pd.concat(all_blocks)
        if not b.empty:
            b = b.sort_values("notional", ascending=False)
            b.to_csv(f"{OUT_DIR}/{sym}_blocks.csv", index=False)
            top = b.head(10)[["ts", "p", "s", "pieces", "notional", "lean"]].copy()
            top["notional"] = (top["notional"] / 1e6).round(2).astype(str) + "M"
            print(f"\nLargest blocks:\n{top.to_string(index=False)}")


# ----------------------------------------------------------------- main ----

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p):
        p.add_argument("tickers", nargs="+")
        p.add_argument("--sensitivity", choices=["low", "medium", "high"], default="low",
                       help="low = only rare, clearly meaningful periods (default)")

    f = sub.add_parser("finra", help="weekly dark-pool trend (free, no key)")
    common(f)
    f.add_argument("--weeks", type=int, default=52, help="weeks to report")
    f.add_argument("--baseline", type=int, default=26,
                   help="trailing weeks that define 'normal'")
    f.add_argument("--z-volume", type=float, help="override: volume threshold")
    f.add_argument("--z-size", type=float, help="override: trade-size threshold")
    f.add_argument("--min-streak", type=int, help="override: weeks in a row")
    f.set_defaults(func=cmd_finra)

    p = sub.add_parser("prints", help="recent large off-exchange prints (free Alpaca key)")
    common(p)
    p.add_argument("--days", type=int, default=3,
                   help="recent weekdays to scan (busy names take a minute+ per day)")
    p.add_argument("--floor", type=float, help="override: minimum block $")
    p.add_argument("--adv-frac", type=float, help="override: block as fraction of day $ volume")
    p.add_argument("--quantile", type=float, help="override: trade-size percentile (0-1)")
    p.add_argument("--min-child", type=float, help="override: smallest piece re-joined into a block")
    p.add_argument("--min-share-pct", type=float, help="override: blocks as %% of day volume")
    p.add_argument("--min-imbalance", type=float, help="override: buy/sell lean (0-1)")
    p.add_argument("--min-blocks", type=int, help="override: minimum blocks per day")
    p.add_argument("--dark-code", default="D",
                   help="exchange code for off-exchange (FINRA-reported) trades")
    p.set_defaults(func=cmd_prints)

    a = ap.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
