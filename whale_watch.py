#!/usr/bin/env python3
"""
whale_watch.py - free scanner for unusual block-venue activity in a stock/ETF.

It does NOT identify buyers, and testing on 60 fresh stocks found no evidence that
its flags mark real large-player orders or predict returns. See the README. It
measures large-size activity two ways:

  finra   FINRA weekly dark-pool (ATS) data. Free, no key. Delayed ~2-4 weeks.
          Main signal: weeks where an unusual share of this ticker's dark-pool
          dollars ran through block venues, the pools FINRA reports as doing
          most of their business in $200K+ trades. Volume doesn't have to be high.
          Heavy trading is counted separately: weeks where dark-pool dollars AND
          average trade size are far above ITS OWN normal, after removing
          market-wide swings (holidays, sell-offs, index rebalances).

  prints  Recent large off-exchange prints via Alpaca's FREE plan (full-market
          data delayed 15+ min). Needs free Alpaca API keys.
          Short-term signal: days where real blocks are a large share of the
          day's dollar volume and lean clearly one way.

Sensitivity (--sensitivity low | medium | high, default low)
  low     only rare, sustained, clearly abnormal periods (few false alarms)
  medium  balanced
  high    catches more, noisier
  Block thresholds match the volume ones and were not fitted to any ticker.
  Every threshold can still be overridden individually (see --help per mode).

Smart adjustments (automatic):
  - Thresholds scale with each stock's own volume and trade-size history, so
    the same setting works for a $5B small cap and a $500B mega cap.
  - Dollar values, not share counts, so stock splits don't distort volume.
    Dollar trade size still moves with the share price; see the README caveats.
  - Robust statistics (median/MAD on log values): one freak week can't skew
    the baseline.
  - FINRA mode divides by total market dark-pool activity each week, so
    market-wide volume spikes don't trigger signals. That total lags tickers
    by about 2 weeks, so the newest weeks scale up the Tier 1 total and are
    marked "estimated" in the mkt_basis column.
  - FINRA mode needs the signal to persist several weeks (low sensitivity).
  - Prints mode: block size cutoff = the largest of a dollar floor, a % of
    that day's dollar volume, and a top-percentile of that day's normal
    on-exchange trades. Regular hours only. Skips prints that aren't fresh
    trades: average-price, derivatively-priced, hedge-leg, late, and special
    settlement reports. Re-joins one order split into several
    same-price prints seconds apart, but only from pieces already large,
    so retail flow (also reported off-exchange) can't add up to a fake block.
  - Each flagged period is labelled by price direction (dark-pool average
    price): "price up" or "price down". It says nothing about who bought or sold.

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
import pathlib
import sys
import time
import webbrowser

import numpy as np
import pandas as pd
import requests

import whale_chart

OUT_DIR = "whale_out"

# Sensitivity presets. Low = strict.
PRESETS = {
    "finra": {
        # z_block: robust z of block-venue share, the main flag.
        # The rest define heavy trading: robust z of volume, robust z of avg
        # trade $, weeks in a row.
        "low":    {"z_block": 3.0, "z_volume": 3.0, "z_size": 2.0,  "min_streak": 2},
        "medium": {"z_block": 2.0, "z_volume": 2.0, "z_size": 1.25, "min_streak": 1},
        "high":   {"z_block": 1.5, "z_volume": 1.5, "z_size": 0.75, "min_streak": 1},
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
BLOCKS_URL = "https://api.finra.org/data/group/otcMarket/name/blocksSummary"
BLOCK_VENUE_PCT = 50.0
BLOCK_LOOKBACK_DAYS = 150       # monthly reports arrive about two months late
HOLDINGS_URL = "https://api.nasdaq.com/api/company/{sym}/institutional-holdings"
HOLDINGS_PARAMS = {"limit": 20000, "type": "TOTAL", "sortColumn": "marketValue"}


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


def fetch_block_venues(end, headers):
    """Dark pools doing most of their business in blocks: at least BLOCK_VENUE_PCT
    of shares in $200K+ trades, in FINRA's latest monthly report."""
    start = (end - dt.timedelta(days=BLOCK_LOOKBACK_DAYS)).isoformat()
    payload = {
        "compareFilters": [{"compareType": "EQUAL", "fieldName": "summaryTypeCode",
                            "fieldValue": "200K"}],
        "dateRangeFilters": [{"fieldName": "monthStartDate", "startDate": start,
                              "endDate": end.isoformat()}],
        "limit": FINRA_PAGE,
        "offset": 0,
    }
    try:
        r = requests.post(BLOCKS_URL, json=payload, headers=headers, timeout=60)
        r.raise_for_status()
        rows = r.json() if r.text.strip() else []
    except Exception as e:  # noqa: BLE001 - block scores are skipped without it
        print(f"(block venue fetch failed: {e})", file=sys.stderr)
        return set()
    if not rows:
        return set()
    latest = max(row["monthStartDate"] for row in rows)
    return {row["MPID"] for row in rows if row["monthStartDate"] == latest
            and (row["ATSBlockBusinessSharePercent"] or 0) >= BLOCK_VENUE_PCT}


def fetch_holdings(sym):
    """Institutional holders built from 13F filings, from Nasdaq's website. None if unavailable."""
    try:
        r = requests.get(HOLDINGS_URL.format(sym=sym), params=HOLDINGS_PARAMS, timeout=60,
                         headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
        r.raise_for_status()
        data = r.json()["data"]
        rows = data["holdingsTransactions"]["table"]["rows"]
        outstanding = float(str(data["ownershipSummary"]["ShareoutstandingTotal"]["value"]).replace(",", "")) * 1e6
        return {"outstanding": outstanding, "rows": [
            {"owner": row["ownerName"], "date": row["date"],
             "change": float(str(row["sharesChange"]).replace(",", "") or 0),
             "new": row["sharesChangePCT"] == "New"} for row in rows]}
    except Exception as e:  # noqa: BLE001 - the chart still works without it
        print(f"(holdings fetch failed for {sym}: {e})", file=sys.stderr)
        return None


def finra_block_weekly(df, venues):
    """This ticker's dark-pool dollars on block venues, per week."""
    d = df[df["summarytypecode"].astype(str).str.upper() == "ATS_W_SMBL_FIRM"]
    d = d[d["mpid"].isin(venues)].sort_values("lastupdatedate")
    d = d.drop_duplicates(["weekstartdate", "mpid"], keep="last")
    dollars = d.groupby("weekstartdate")["totalnotionalsum"].sum()
    dollars.index = pd.to_datetime(dollars.index)
    return dollars


def finra_market_weekly(start, end, headers):
    """Market-wide dark-pool totals per week (for normalising). Optional."""
    try:
        m = fetch_finra({"summaryTypeCode": "ATS_W_VOL_STATS"}, start, end, headers)
    except Exception as e:  # noqa: BLE001 - normalisation is a nice-to-have
        print(f"(market normalisation skipped: {e})", file=sys.stderr)
        return pd.DataFrame()
    if m.empty:
        return m
    # Each week has one row per product (CTS, UTP, OTCE) and together they are the
    # market total. Mid-2023 also has an NMS subtotal with no product code; skip it.
    m = m[m["producttypecode"].notna()]
    g = m.groupby("weekstartdate")[["totalnotionalsum", "totalweeklysharequantity",
                                    "totalweeklytradecount"]].sum(min_count=1)
    out = pd.DataFrame({"mkt_dollars": g["totalnotionalsum"],
                        "mkt_shares": g["totalweeklysharequantity"],
                        "mkt_trades": g["totalweeklytradecount"],
                        "mkt_estimated": False})
    out.index = pd.to_datetime(out.index)
    return out


def tier1_totals(week, headers):
    """Dark-pool totals across Tier 1 symbols for one week, or None if unpublished."""
    day = week.date().isoformat()
    r = fetch_finra({"summaryTypeCode": "ATS_W_SMBL", "tierIdentifier": "T1"},
                    day, day, headers)
    if r.empty:
        return None
    return pd.Series({"mkt_dollars": r["totalnotionalsum"].sum(),
                      "mkt_shares": r["totalweeklysharequantity"].sum(),
                      "mkt_trades": r["totalweeklytradecount"].sum()})


def estimate_recent_market(mkt, end, headers):
    """Extend market totals through the newest weeks that have Tier 1 data.

    FINRA publishes market totals about two weeks after Tier 1 tickers. Tier 1 is
    a steady share of the total, so each newer week is its own Tier 1 sum scaled
    by that share in the last published week. Replayed against 58 published weeks
    this was off by a median of about 1% in dollars. Added rows are marked
    mkt_estimated. If Tier 1 can't be fetched, those weeks are left unscored.
    """
    if mkt.empty:
        return mkt
    last, rows = mkt.index.max(), {}
    try:
        base = tier1_totals(last, headers)
        if base is None:
            return mkt
        share = base / mkt.loc[last, base.index].astype(float)
        week = last + pd.Timedelta(weeks=1)
        while week.date() <= end:
            totals = tier1_totals(week, headers)
            if totals is None:
                break
            rows[week] = totals / share
            week += pd.Timedelta(weeks=1)
    except Exception as e:  # noqa: BLE001 - the newest weeks just stay unscored
        print(f"(recent market estimate skipped: {e})", file=sys.stderr)
        return mkt
    if not rows:
        return mkt
    return pd.concat([mkt, pd.DataFrame(rows).T.assign(mkt_estimated=True)])


def align_market(index, mkt, col):
    """Market value and trades for each week in `index`, and where each came from."""
    m = mkt.reindex(index)
    out = pd.DataFrame({"value": m[col], "trades": m["mkt_trades"]})
    out["basis"] = np.select([out["value"].isna(), m["mkt_estimated"].eq(True)],
                             ["none", "estimated"], "actual")
    return out


def score_finra(w, mkt, cfg, baseline):
    w = w.copy()
    use_dollars = "dollars" in w.columns and w["dollars"].gt(0).all()
    w["value"] = w["dollars"] if use_dollars else w["shares"]
    w["avg_trade"] = w["value"] / w["trades"].where(w["trades"] > 0)
    w["vwap"] = (w["dollars"] / w["shares"]) if use_dollars else np.nan

    vol, size = w["value"].copy(), w["avg_trade"].copy()
    market_value = None
    w["mkt_basis"] = "none"
    if not mkt.empty:  # remove market-wide swings, in the same unit as the ticker
        m = align_market(w.index, mkt, "mkt_dollars" if use_dollars else "mkt_shares")
        if (m["basis"] == "actual").sum() >= len(w) * 0.8:
            vol = vol / m["value"]
            size = size / (m["value"] / m["trades"])
            w["mkt_basis"] = m["basis"]
            market_value = m["value"]
    minp = min(baseline, max(8, baseline // 2))
    w["z_volume"] = robust_z(np.log(vol), baseline, minp)
    w["z_size"] = robust_z(np.log(size), baseline, minp)
    w["elevated"] = (w["z_volume"] >= cfg["z_volume"]) & (w["z_size"] >= cfg["z_size"])
    w["heavy"] = np.array(streaks(w["elevated"])) >= cfg["min_streak"]

    # Share of this ticker's dark dollars on block venues. Both sides are this
    # ticker's dollars, so price, splits and market totals don't enter into it.
    has_blocks = "block_dollars" in w.columns and use_dollars
    w["block_dollars"] = w["block_dollars"] if has_blocks else np.nan
    w["block_share"] = w["block_dollars"] / w["dollars"] if has_blocks else np.nan
    w["block_normal"] = w["block_share"].rolling(baseline, min_periods=minp).median().shift(1)
    w["z_block"] = robust_z(np.log(w["block_share"].where(w["block_share"] > 0)), baseline, minp)
    # Dollars keep the size of a busy week that share cancels out, so charts can show it.
    relative = w["block_dollars"] / market_value if market_value is not None else w["block_dollars"]
    w["block_normal_usd"] = w["block_dollars"].rolling(baseline, min_periods=minp).median().shift(1)
    w["z_block_usd"] = robust_z(np.log(relative.where(relative > 0)), baseline, minp)
    w["flag"] = w["z_block"] >= cfg["z_block"]
    w["streak"] = streaks(w["flag"])
    w["closeness"] = 100 * w["z_block"] / cfg["z_block"]  # 100 means the bar was met
    # price direction over the run: compare to the 4 weeks before it started
    w["price_chg_%"] = np.nan
    w["label"] = ""
    for i in np.where(w["flag"])[0]:
        start = i - int(w["streak"].iloc[i]) + 1
        before = w["vwap"].iloc[max(0, start - 4):start].mean()
        chg = 100 * (w["vwap"].iloc[i] / before - 1) if before == before else np.nan
        w.iloc[i, w.columns.get_loc("price_chg_%")] = chg
        w.iloc[i, w.columns.get_loc("label")] = (
            "?" if chg != chg else ("price up" if chg >= 0 else "price down"))
    return w, use_dollars


def score_ticker(sym, cfg, s, e, mkt, venues, baseline, headers):
    """Scored weeks for one ticker, or None if FINRA has no data for it."""
    raw = fetch_finra({"issueSymbolIdentifier": sym}, s, e, headers)
    w = finra_ticker_weekly(raw)
    if w.empty:
        return None
    if venues:
        w["block_dollars"] = finra_block_weekly(raw, venues).reindex(w.index).fillna(0.0)
    return score_finra(w, mkt, cfg, baseline)[0]


def closest_weeks(w, n=3):
    """The n scored weeks nearest the bar, for tickers with nothing flagged."""
    return w.dropna(subset=["closeness"]).nlargest(n, "closeness")


def block_view(rows, *extra):
    """Block columns for printing, plus any extra columns from `rows`."""
    t = pd.DataFrame({"block_$M": rows["block_dollars"] / 1e6,
                      "block_%": 100 * rows["block_share"],
                      "normal_%": 100 * rows["block_normal"],
                      "z_block": rows["z_block"]})
    return t.join(rows[list(extra)]).round(2).to_string()


def cmd_finra(a):
    cfg = resolve("finra", a)
    end = dt.date.today()
    start = end - dt.timedelta(weeks=a.weeks + a.baseline)
    s, e = start.isoformat(), end.isoformat()
    headers = finra_headers()
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"Sensitivity {a.sensitivity}: block-venue share z>={cfg['z_block']}, "
          f"baseline {a.baseline} weeks")
    print(f"Heavy trading, counted separately: volume z>={cfg['z_volume']}, "
          f"trade-size z>={cfg['z_size']}, {cfg['min_streak']}+ weeks in a row")
    mkt = estimate_recent_market(finra_market_weekly(s, e, headers), end, headers)
    venues = fetch_block_venues(end, headers)
    if venues:
        print(f"Block venues (FINRA, {BLOCK_VENUE_PCT:.0f}%+ of shares in $200K+ trades): "
              f"{', '.join(sorted(venues))}")
    else:
        print("(block venue list unavailable; block scores skipped)")
    summary = []
    for sym in (t.upper() for t in a.tickers):
        w = score_ticker(sym, cfg, s, e, mkt, venues, a.baseline, headers)
        if w is None:
            print(f"\n{sym}: no dark-pool data returned (check the ticker).")
            continue
        w = w[w.index >= pd.Timestamp(end - dt.timedelta(weeks=a.weeks))]
        if w.empty:
            print(f"\n{sym}: no dark-pool data in the last {a.weeks} weeks.")
            continue
        w.to_csv(f"{OUT_DIR}/{sym}_finra_weekly.csv")
        flagged = w[w["flag"]]
        heavy = int(w["heavy"].sum())
        print(f"\n{sym}: {len(flagged)} block-activity week(s) in the last {a.weeks}, "
              f"{heavy} heavy-trading week(s) (latest data: week of {w.index[-1].date()})")
        estimated = int((w["mkt_basis"] == "estimated").sum())
        if estimated:
            print(f"  Newest {estimated} week(s): volume scores use an estimated market "
                  f"total. Block scores don't need it.")
        if not flagged.empty:
            print(block_view(flagged, "streak", "price_chg_%", "label", "z_volume"))
        elif not closest_weeks(w).empty:
            print("  No week met the bar. Closest weeks, NOT flagged (closeness 100 = bar met):")
            print(block_view(closest_weeks(w), "closeness", "z_volume"))
        last = w.iloc[-1]
        summary.append({"ticker": sym, "latest_week": w.index[-1].date(),
                        "flagged_weeks": len(flagged),
                        "current_streak": int(last["streak"]),
                        "z_block_now": round(last["z_block"], 2),
                        "heavy_weeks": heavy,
                        "z_volume_now": round(last["z_volume"], 2),
                        "z_size_now": round(last["z_size"], 2),
                        "market_basis_now": last["mkt_basis"],
                        "last_label": flagged["label"].iloc[-1] if len(flagged) else ""})
    if summary:
        out = pd.DataFrame(summary).sort_values(
            ["current_streak", "flagged_weeks", "z_block_now"], ascending=False)
        out.to_csv(f"{OUT_DIR}/finra_summary.csv", index=False)
        print("\n=== Ranked ===")
        print(out.to_string(index=False))


def cmd_chart(a):
    """Write a look-back chart for each ticker."""
    cfg = resolve("finra", a)
    end = dt.date.today()
    start = end - dt.timedelta(weeks=a.weeks + max(a.baseline, whale_chart.PRICE_WINDOW))
    s, e = start.isoformat(), end.isoformat()
    headers = finra_headers()
    venues = fetch_block_venues(end, headers)
    if not venues:
        print("(block venue list unavailable; charts need it, so none were written)")
        return
    os.makedirs(OUT_DIR, exist_ok=True)
    mkt = estimate_recent_market(finra_market_weekly(s, e, headers), end, headers)
    for sym in (t.upper() for t in a.tickers):
        w = score_ticker(sym, cfg, s, e, mkt, venues, a.baseline, headers)
        if w is None:
            print(f"\n{sym}: no dark-pool data returned (check the ticker).")
            continue
        w = whale_chart.with_price_position(w)
        w = whale_chart.with_score(w[w.index >= pd.Timestamp(end - dt.timedelta(weeks=a.weeks))])
        if w.empty:
            print(f"\n{sym}: no dark-pool data in the last {a.weeks} weeks.")
            continue
        periods = whale_chart.find_periods(w, cfg["z_block"], col="score")
        status = whale_chart.current_status(w, periods, col="score")
        print(f"\n{whale_chart.status_sentence(status, sym)}")
        for p in periods:
            print(f"  {p['start'].date()} to {p['end'].date()}: {p['weeks']} week(s), "
                  f"peak score {p['peak_z']:.2f}, price {p['price_chg']:+.1f}%, "
                  f"started {whale_chart.position_text(p['price_pos']).replace('–', 'n/a')} in its 1-year range")
        holdings = fetch_holdings(sym)
        if holdings:
            sentence = whale_chart.holdings_sentence(whale_chart.holdings_by_quarter(holdings, end), sym)
            if sentence:
                print(f"  {sentence}")
        path = pathlib.Path(OUT_DIR) / f"{sym}_chart.html"
        path.write_text(whale_chart.render_chart(sym, w, periods, status, cfg["z_block"], end, holdings),
                        encoding="utf-8")
        print(f"  Chart: {path}")
        if not a.no_open:
            webbrowser.open(path.resolve().as_uri())


# --------------------------------------------------------------- Alpaca ----

ALPACA_URL = "https://data.alpaca.markets/v2/stocks/{sym}/trades"
# Not fresh buying/selling at that moment, per Alpaca's condition table: cash and
# next-day settlement (C, N, R), bunched sold (G), price variation (H), prior
# reference price (P), extended hours (T, U), contingent / hedge legs (V, 7),
# average price (W), out of sequence (Z), derivatively priced (4).
EXCLUDE = {"C", "G", "H", "N", "P", "R", "T", "U", "V", "W", "Z", "4", "7"}
# B is average price on the NYSE tapes (A, B) but a real bunched trade on tape C.
EXCLUDE_NYSE_TAPES = EXCLUDE | {"B"}
# Official open/close and corrected-close records don't add any volume.
NO_VOLUME = {"M", "Q", "9"}
NY = "America/New_York"
TRADE_RETRIES = 6
# Extra weekdays to try beyond --days, for holidays and a day that hasn't opened.
EXTRA_SESSION_TRIES = 5


def alpaca_headers():
    kid = os.getenv("ALPACA_KEY_ID") or os.getenv("APCA_API_KEY_ID")
    sec = os.getenv("ALPACA_SECRET_KEY") or os.getenv("APCA_API_SECRET_KEY")
    if not (kid and sec):
        sys.exit("Set ALPACA_KEY_ID and ALPACA_SECRET_KEY (free account at alpaca.markets).")
    return {"APCA-API-KEY-ID": kid, "APCA-API-SECRET-KEY": sec}


def get_with_retry(url, params, headers):
    """A dropped connection shouldn't lose a long download, so wait and try again."""
    for attempt in range(TRADE_RETRIES + 1):
        try:
            return requests.get(url, params=params, headers=headers, timeout=60)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            if attempt == TRADE_RETRIES:
                raise
            time.sleep(2 ** attempt)


def fetch_trades(sym, start, end, headers):
    params = {"start": start, "end": end, "limit": 10000, "feed": "sip"}
    out = []
    while True:
        r = get_with_retry(ALPACA_URL.format(sym=sym), params, headers)
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
    conds = df["c"] if "c" in df.columns else pd.Series([[]] * len(df), index=df.index)
    df["codes"] = conds.apply(lambda c: set(c) if isinstance(c, (list, tuple)) else set())
    no_volume = df["codes"].apply(lambda c: bool(c & NO_VOLUME))
    df = df[(mins >= 570) & (mins < 960) & ~no_volume]    # 9:30-16:00 New York
    if df.empty:
        return None, pd.DataFrame()
    df = df.sort_values("ts").reset_index(drop=True)
    tapes = df["z"] if "z" in df.columns else pd.Series(["A"] * len(df))
    bad = pd.Series([bool(c & (EXCLUDE if t == "C" else EXCLUDE_NYSE_TAPES))
                     for c, t in zip(df["codes"], tapes)], index=df.index)
    df["notional"] = df["p"] * df["s"]
    lit = df["x"] != dark_code
    normal_lit = lit & ~bad
    df["ref_px"] = df["p"].where(normal_lit).ffill()    # last normal on-exchange price

    day_dollars = df["notional"].sum()
    # percentile of normal on-exchange trades, so the blocks can't set their own bar
    lit_q = df.loc[normal_lit, "notional"].quantile(cfg["quantile"]) if normal_lit.any() else 0
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


def scan_sessions(sym, n_days, now, cfg, dark_code, headers):
    """Walk back from `now` until n_days sessions have trades. Weekends, holidays
    and a day that hasn't opened yet don't count. Returns rows oldest first."""
    rows, all_blocks = [], []
    day, tries = now.date(), 0
    while len(rows) < n_days and tries < n_days + EXTRA_SESSION_TRIES:
        if day.weekday() < 5:
            tries += 1
            start = dt.datetime.combine(day, dt.time(0), dt.timezone.utc)
            end = min(start + dt.timedelta(days=1), now)
            print(f"{sym} {day}: downloading trades...", file=sys.stderr)
            df = fetch_trades(sym, start.isoformat().replace("+00:00", "Z"),
                              end.isoformat().replace("+00:00", "Z"), headers)
            summ, blocks = analyze_day(df, cfg, dark_code) if not df.empty else (None, None)
            if summ is not None:
                rows.append({"date": day, **summ})
                if not blocks.empty:
                    all_blocks.append(blocks.assign(date=day))
        day -= dt.timedelta(days=1)
    rows.reverse()
    return rows, pd.concat(all_blocks) if all_blocks else pd.DataFrame()


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

    for sym in (t.upper() for t in a.tickers):
        rows, b = scan_sessions(sym, a.days, now, cfg, a.dark_code, headers)
        if not rows:
            print(f"\n{sym}: no trades returned.")
            continue
        daily = pd.DataFrame(rows).set_index("date")
        daily.to_csv(f"{OUT_DIR}/{sym}_prints_daily.csv")
        print(f"\n{sym}")
        print(daily.round(2).to_string())
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
    f.add_argument("--z-block", type=float, help="override: block-venue share threshold")
    f.add_argument("--z-volume", type=float, help="override: volume threshold")
    f.add_argument("--z-size", type=float, help="override: trade-size threshold")
    f.add_argument("--min-streak", type=int, help="override: weeks in a row")
    f.set_defaults(func=cmd_finra)

    c = sub.add_parser("chart", help="look-back chart of active periods and where things stand now")
    common(c)
    c.set_defaults(sensitivity="medium")
    c.add_argument("--weeks", type=int, default=104, help="weeks to show")
    c.add_argument("--baseline", type=int, default=26, help="trailing weeks that define 'normal'")
    c.add_argument("--z-block", type=float, help="override: score that starts a period")
    c.add_argument("--no-open", action="store_true", help="write the chart without opening it")
    c.set_defaults(func=cmd_chart)

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
