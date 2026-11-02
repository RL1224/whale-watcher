"""Expected values are worked out by hand from the fixtures, not by the code.

The robust-z fixtures use log(ratio) = +/-0.1 around a constant, so the median
is that constant and MAD = 0.1. Scale = 1.4826 * 0.1 = 0.14826, which makes a
week 0.6 above normal score 0.6 / 0.14826 = 4.0469.
"""
import argparse
import datetime as dt

import numpy as np
import pandas as pd
import pytest

import whale_watch as ww

SPIKE_Z = 4.0469
FINRA_CFG = {"z_block": 3.0, "z_volume": 3.0, "z_size": 2.0, "min_streak": 1}
PRINTS_CFG = {"floor": 1_000_000, "adv_frac": 0.0, "quantile": 0.5, "min_child": 100_000,
              "min_share_pct": 1.0, "min_imbalance": 0.2, "min_blocks": 1}


# ------------------------------------------------------------ FINRA fakes ----

def finra_row(week, summary, tier, product, shares, dollars, trades, symbol=None):
    """One record as api.finra.org returns it (camelCase, all fields present)."""
    return {"totalWeeklyShareQuantity": shares, "issueSymbolIdentifier": symbol,
            "issueName": symbol, "lastUpdateDate": week, "lastReportedDate": week,
            "tierDescription": "x", "initialPublishedDate": week, "tierIdentifier": tier,
            "summaryStartDate": week, "totalNotionalSum": dollars,
            "totalWeeklyTradeCount": trades, "weekStartDate": week, "MPID": None,
            "firmCRDNumber": None, "productTypeCode": product,
            "marketParticipantName": None, "summaryTypeCode": summary}


class FakeResponse:
    def __init__(self, rows):
        self.rows = rows
        self.status_code = 200 if rows else 204
        self.text = "rows" if rows else ""

    def raise_for_status(self):
        pass

    def json(self):
        return self.rows


def fake_finra(monkeypatch, rows_by_filter):
    """Filters on every compare value and on the week range, like the real API.
    A filter value mapped to an exception raises it."""
    def post(url, json=None, headers=None, timeout=None):
        key = "|".join(f["fieldValue"] for f in json["compareFilters"])
        rows = rows_by_filter.get(key, [])
        if isinstance(rows, Exception):
            raise rows
        span = json["dateRangeFilters"][0]
        rows = [r for r in rows
                if span["startDate"] <= (r.get("weekStartDate") or r["monthStartDate"]) <= span["endDate"]]
        return FakeResponse(rows[json["offset"]:json["offset"] + json["limit"]])
    monkeypatch.setattr(ww.requests, "post", post)


def weekly(log_offsets, base=1e7, trades=100, vwap=10.0):
    """Ticker table whose dollars sit at base * e^offset each week."""
    idx = pd.date_range("2026-01-05", periods=len(log_offsets), freq="7D")
    dollars = base * np.exp(np.asarray(log_offsets, dtype=float))
    prices = np.full(len(idx), vwap) if np.isscalar(vwap) else np.asarray(vwap, dtype=float)
    return pd.DataFrame({"shares": dollars / prices, "trades": float(trades),
                         "dollars": dollars}, index=idx)


def with_blocks(w, log_offsets, base_share=0.01):
    """Add block dollars at base_share * e^offset of each week's dark dollars."""
    w = w.copy()
    w["block_dollars"] = w["dollars"] * base_share * np.exp(np.asarray(log_offsets, dtype=float))
    return w


def block_row(month, mpid, pct):
    """One record of FINRA's monthly blocksSummary dataset."""
    return {"MPID": mpid, "marketParticipantName": mpid, "summaryTypeCode": "200K",
            "monthStartDate": month, "ATSBlockBusinessSharePercent": pct, "atsOtc": "ATS"}


def firm_row(week, mpid, dollars, updated=None):
    row = finra_row(week, "ATS_W_SMBL_FIRM", "T1", None, 100, dollars, 5, "ORCL")
    return {**row, "MPID": mpid, "lastUpdateDate": updated or week}


def market(index, dollars=1e9, shares=1e8, trades=1e6, estimated=False):
    out = pd.DataFrame({"mkt_dollars": dollars, "mkt_shares": shares,
                        "mkt_trades": trades}, index=index, dtype=float)
    out["mkt_estimated"] = estimated
    return out


ALTERNATING = [0.1, -0.1] * 4


# ----------------------------------------------------------------- paging ----

def test_finra_rows_are_collected_across_pages(monkeypatch):
    monkeypatch.setattr(ww, "FINRA_PAGE", 2)
    rows = [finra_row(f"2026-01-0{i}", "ATS_W_SMBL", "T1", "CTS", i, 10.0 * i, 1, "ORCL")
            for i in range(1, 6)]
    fake_finra(monkeypatch, {"ORCL": rows})
    df = ww.fetch_finra({"issueSymbolIdentifier": "ORCL"}, "2026-01-01", "2026-12-31", {})
    assert df["totalnotionalsum"].tolist() == [10.0, 20.0, 30.0, 40.0, 50.0]


def test_alpaca_trades_follow_page_tokens_and_retry_rate_limits(monkeypatch):
    class Response:
        def __init__(self, status, body):
            self.status_code, self.body = status, body

        def raise_for_status(self):
            pass

        def json(self):
            return self.body

    tokens_seen = []
    replies = iter([Response(429, {}),
                    Response(200, {"trades": [{"p": 1.0}], "next_page_token": "abc"}),
                    Response(200, {"trades": [{"p": 2.0}], "next_page_token": None})])

    def get(url, params=None, headers=None, timeout=None):
        tokens_seen.append(params.get("page_token"))
        return next(replies)

    monkeypatch.setattr(ww.requests, "get", get)
    monkeypatch.setattr(ww.time, "sleep", lambda s: None)
    df = ww.fetch_trades("ORCL", "start", "end", {})
    assert df["p"].tolist() == [1.0, 2.0]
    assert tokens_seen == [None, None, "abc"]


class AlpacaPage:
    status_code = 200

    def __init__(self, body):
        self.body = body

    def raise_for_status(self):
        pass

    def json(self):
        return self.body


def test_a_dropped_connection_keeps_earlier_pages_and_retries(monkeypatch):
    outcomes = iter([AlpacaPage({"trades": [{"p": 1.0}], "next_page_token": "abc"}),
                     ww.requests.exceptions.ReadTimeout("timed out"),
                     ww.requests.exceptions.ConnectionError("dropped"),
                     AlpacaPage({"trades": [{"p": 2.0}], "next_page_token": None})])
    tokens = []

    def get(url, params=None, headers=None, timeout=None):
        tokens.append(params.get("page_token"))
        result = next(outcomes)
        if isinstance(result, Exception):
            raise result
        return result

    monkeypatch.setattr(ww.requests, "get", get)
    monkeypatch.setattr(ww.time, "sleep", lambda s: None)
    df = ww.fetch_trades("MSFT", "start", "end", {})
    assert df["p"].tolist() == [1.0, 2.0]
    assert tokens == [None, "abc", "abc", "abc"]


def test_a_connection_that_stays_down_gives_up_with_the_error(monkeypatch):
    calls = []

    def get(url, params=None, headers=None, timeout=None):
        calls.append(1)
        raise ww.requests.exceptions.ConnectionError("down")

    monkeypatch.setattr(ww.requests, "get", get)
    monkeypatch.setattr(ww.time, "sleep", lambda s: None)
    with pytest.raises(ww.requests.exceptions.ConnectionError):
        ww.fetch_trades("MSFT", "start", "end", {})
    assert len(calls) == ww.TRADE_RETRIES + 1


# ---------------------------------------------------------- market totals ----

def test_market_total_adds_every_product_for_the_week(monkeypatch):
    # Real totals for 2026-09-07: all 14,488 symbol rows sum to the same $702.35B.
    week = "2026-09-07"
    fake_finra(monkeypatch, {"ATS_W_VOL_STATS": [
        finra_row(week, "ATS_W_VOL_STATS", "NA", "CTS", 3_000, 372_650_000_000.0, 30),
        finra_row(week, "ATS_W_VOL_STATS", "NA", "OTCE", 2_000, 1_840_000_000.0, 1),
        finra_row(week, "ATS_W_VOL_STATS", "NA", "UTP", 1_000, 327_860_000_000.0, 20),
    ]})
    m = ww.finra_market_weekly("2026-01-01", "2026-12-31", {})
    row = m.loc[pd.Timestamp(week)]
    assert row["mkt_dollars"] == 702_350_000_000.0
    assert row["mkt_shares"] == 6_000
    assert row["mkt_trades"] == 51


def test_market_total_does_not_double_count_the_2023_nms_subtotal(monkeypatch):
    # June-Nov 2023 add a fourth row with no product code equal to CTS + UTP.
    week = "2023-06-05"
    fake_finra(monkeypatch, {"ATS_W_VOL_STATS": [
        finra_row(week, "ATS_W_VOL_STATS", "NA", "CTS", 30, 199.0, 3),
        finra_row(week, "ATS_W_VOL_STATS", "NA", "OTCE", 10, 1.0, 1),
        finra_row(week, "ATS_W_VOL_STATS", "NA", "UTP", 20, 136.0, 2),
        finra_row(week, "ATS_W_VOL_STATS", "NMS", None, 50, 335.0, 5),
    ]})
    m = ww.finra_market_weekly("2023-01-01", "2023-12-31", {})
    assert m.loc[pd.Timestamp(week), "mkt_dollars"] == 336.0


def tier1_rows(week, dollars, shares, trades):
    """Two Tier 1 symbols that add up to the given totals."""
    return [finra_row(week, "ATS_W_SMBL", "T1", "CTS", shares - 1, dollars - 1.0, trades - 1, "AAA"),
            finra_row(week, "ATS_W_SMBL", "T1", "UTP", 1, 1.0, 1, "BBB")]


PUBLISHED_WEEK = "2026-09-21"
PUBLISHED = market(pd.to_datetime([PUBLISHED_WEEK]), dollars=1000.0, shares=500.0, trades=100.0)
TODAY = dt.date(2026, 10, 30)


def test_newest_weeks_scale_tier1_by_its_share_of_the_last_published_week(monkeypatch):
    # Published week: Tier 1 is 800/1000 of dollars, 100/500 of shares, 60/100 of trades.
    fake_finra(monkeypatch, {"ATS_W_SMBL|T1": tier1_rows(PUBLISHED_WEEK, 800.0, 100, 60)
               + tier1_rows("2026-09-28", 900.0, 110, 66)})
    m = ww.estimate_recent_market(PUBLISHED, TODAY, {})
    row = m.loc[pd.Timestamp("2026-09-28")]
    assert row["mkt_dollars"] == pytest.approx(1125.0)
    assert row["mkt_shares"] == pytest.approx(550.0)
    assert row["mkt_trades"] == pytest.approx(110.0)
    assert m["mkt_estimated"].tolist() == [False, True]


def test_estimates_stop_at_the_first_week_with_no_tier1_data(monkeypatch):
    fake_finra(monkeypatch, {"ATS_W_SMBL|T1": tier1_rows(PUBLISHED_WEEK, 800.0, 100, 60)
               + tier1_rows("2026-09-28", 900.0, 110, 66)
               + tier1_rows("2026-10-12", 900.0, 110, 66)})        # 10-05 is missing
    m = ww.estimate_recent_market(PUBLISHED, TODAY, {})
    assert m.index.max() == pd.Timestamp("2026-09-28")


def test_estimates_stop_at_the_end_date(monkeypatch):
    fake_finra(monkeypatch, {"ATS_W_SMBL|T1": tier1_rows(PUBLISHED_WEEK, 800.0, 100, 60)
               + tier1_rows("2026-09-28", 900.0, 110, 66)
               + tier1_rows("2026-10-05", 900.0, 110, 66)})
    m = ww.estimate_recent_market(PUBLISHED, dt.date(2026, 10, 1), {})
    assert m.index.max() == pd.Timestamp("2026-09-28")


def test_scan_scores_the_newest_week_from_tier1_data(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    today = dt.date.today()
    monday = today - dt.timedelta(days=today.weekday())
    weeks = [(monday - dt.timedelta(weeks=n)).isoformat() for n in range(9, 0, -1)]
    published, newest = weeks[:-1], weeks[-1]
    fake_finra(monkeypatch, {
        "ORCL": [finra_row(w, "ATS_W_SMBL", "T1", "CTS", 10, 100.0, 2, "ORCL") for w in weeks],
        "ATS_W_VOL_STATS": [finra_row(w, "ATS_W_VOL_STATS", "NA", "CTS", 500, 1000.0, 100)
                            for w in published],
        "ATS_W_SMBL|T1": tier1_rows(published[-1], 800.0, 100, 60)
        + tier1_rows(newest, 900.0, 110, 66),
    })
    args = argparse.Namespace(tickers=["ORCL"], sensitivity="low", weeks=4, baseline=26,
                              z_volume=None, z_size=None, min_streak=None)
    ww.cmd_finra(args)
    summary = pd.read_csv(tmp_path / ww.OUT_DIR / "finra_summary.csv")
    assert summary["market_basis_now"].tolist() == ["estimated"]


def test_no_new_tier1_weeks_leaves_market_unchanged(monkeypatch):
    fake_finra(monkeypatch, {"ATS_W_SMBL|T1": tier1_rows(PUBLISHED_WEEK, 800.0, 100, 60)})
    m = ww.estimate_recent_market(PUBLISHED, TODAY, {})
    assert m["mkt_estimated"].tolist() == [False]


def test_tier1_failure_keeps_published_totals(monkeypatch, capsys):
    fake_finra(monkeypatch, {"ATS_W_SMBL|T1": ConnectionError("FINRA down")})
    m = ww.estimate_recent_market(PUBLISHED, TODAY, {})
    assert m["mkt_dollars"].tolist() == [1000.0]
    assert "FINRA down" in capsys.readouterr().err


def test_week_with_no_market_total_stays_unscored_and_says_so():
    w = weekly(ALTERNATING + [0.1, 0.6])
    scored, _ = ww.score_finra(w, market(w.index[:9]), FINRA_CFG, 8)
    assert np.isnan(scored["z_volume"].iloc[-1])
    assert scored["mkt_basis"].iloc[-1] == "none"


def test_ticker_with_no_weeks_past_the_market_total_scores_with_real_api_types(monkeypatch):
    # The API sends trade counts as integers, and a fractional median can't go
    # in an integer column. Found live: this crashed the whole scan on TSM.
    weeks = ["2026-01-05", "2026-01-12", "2026-01-19", "2026-01-26"]
    fake_finra(monkeypatch, {"ATS_W_VOL_STATS": [
        finra_row(week, "ATS_W_VOL_STATS", "NA", "CTS", 100, 1000.0, trades)
        for week, trades in zip(weeks, [10, 11, 12, 14])]})
    mkt = ww.finra_market_weekly("2026-01-01", "2026-12-31", {})
    idx = pd.to_datetime(weeks)
    aligned = ww.align_market(idx, mkt, "mkt_dollars")
    assert aligned["basis"].tolist() == ["actual"] * 4
    assert aligned["trades"].tolist() == [10, 11, 12, 14]


# ---------------------------------------------------------------- scoring ----

def test_estimated_weeks_are_scored_and_marked():
    # Market totals land 2 weeks after Tier 1 tickers; these weeks must still
    # score, or current_streak can never be above zero.
    w = weekly(ALTERNATING + [0.1, 0.6])
    mkt = market(w.index, estimated=[False] * 8 + [True, True])
    scored, _ = ww.score_finra(w, mkt, FINRA_CFG, 8)
    assert scored["z_volume"].iloc[-1] == pytest.approx(SPIKE_Z, abs=1e-3)
    assert scored["z_size"].iloc[-1] == pytest.approx(SPIKE_Z, abs=1e-3)
    assert bool(scored["heavy"].iloc[-1])
    assert scored["mkt_basis"].tolist() == ["actual"] * 8 + ["estimated"] * 2


def test_market_wide_spike_is_removed_when_market_data_exists():
    w = weekly(ALTERNATING + [0.6])
    mkt = market(w.index, dollars=[1e9] * 8 + [1e9 * np.exp(0.6)])
    scored, _ = ww.score_finra(w, mkt, FINRA_CFG, 8)
    assert scored["z_volume"].iloc[-1] == pytest.approx(0.0, abs=1e-6)
    assert not bool(scored["heavy"].iloc[-1])


def test_share_fallback_divides_by_market_shares_not_dollars():
    w = weekly(ALTERNATING + [0.6])
    w.iloc[0, w.columns.get_loc("dollars")] = 0.0        # forces the share fallback
    wild = [1e9, 7e9, 2e8, 4e10, 3e9, 9e8, 6e10, 5e7, 8e9]
    scored, use_dollars = ww.score_finra(w, market(w.index, dollars=wild), FINRA_CFG, 8)
    assert not use_dollars
    assert scored["z_volume"].iloc[-1] == pytest.approx(SPIKE_Z, abs=1e-3)


def test_baseline_shorter_than_eight_weeks_still_scores():
    w = weekly([0.1, -0.1] * 3 + [0.6])
    scored, _ = ww.score_finra(w, pd.DataFrame(), FINRA_CFG, 6)
    assert scored["z_volume"].iloc[-1] == pytest.approx(SPIKE_Z, abs=1e-3)


def test_market_basis_is_none_without_market_data():
    w = weekly(ALTERNATING + [0.6])
    scored, _ = ww.score_finra(w, pd.DataFrame(), FINRA_CFG, 8)
    assert set(scored["mkt_basis"]) == {"none"}


@pytest.mark.parametrize("last_price, change, label", [(11.0, 10.0, "price up"),
                                                       (9.0, -10.0, "price down")])
def test_flagged_week_is_labelled_by_price_move(last_price, change, label):
    w = with_blocks(weekly(ALTERNATING + [0.0], vwap=[10.0] * 8 + [last_price]), ALTERNATING + [0.6])
    scored, _ = ww.score_finra(w, pd.DataFrame(), FINRA_CFG, 8)
    assert scored["price_chg_%"].iloc[-1] == pytest.approx(change)
    assert scored["label"].iloc[-1] == label


def test_heavy_trading_needs_consecutive_weeks():
    w = weekly(ALTERNATING + [0.6])
    scored, _ = ww.score_finra(w, pd.DataFrame(), {**FINRA_CFG, "min_streak": 2}, 8)
    assert not bool(scored["heavy"].iloc[-1])


# ------------------------------------------------------------ block signal ----

def test_block_share_spike_flags_a_week_with_ordinary_volume():
    w = with_blocks(weekly(ALTERNATING + [0.0]), ALTERNATING + [0.6])
    scored, _ = ww.score_finra(w, pd.DataFrame(), FINRA_CFG, 8)
    assert scored["z_block"].iloc[-1] == pytest.approx(SPIKE_Z, abs=1e-3)
    assert bool(scored["flag"].iloc[-1])
    assert not bool(scored["heavy"].iloc[-1])


def test_heavy_trading_alone_does_not_flag_block_activity():
    w = with_blocks(weekly(ALTERNATING + [0.6]), ALTERNATING + [0.0])
    scored, _ = ww.score_finra(w, pd.DataFrame(), FINRA_CFG, 8)
    assert bool(scored["heavy"].iloc[-1])
    assert not bool(scored["flag"].iloc[-1])


def test_block_score_is_unchanged_by_a_ten_for_one_price_level_shift():
    # A split or a big price move scales block and total dollars together.
    offsets = ALTERNATING + [0.6]
    flat = with_blocks(weekly([0.0] * 9), offsets)
    shifted = with_blocks(weekly([0.0] * 4 + [np.log(10)] * 5), offsets)
    a, _ = ww.score_finra(flat, pd.DataFrame(), FINRA_CFG, 8)
    b, _ = ww.score_finra(shifted, pd.DataFrame(), FINRA_CFG, 8)
    assert b["z_block"].iloc[-1] == pytest.approx(a["z_block"].iloc[-1])


def test_dollar_score_rises_with_block_dollars_against_the_market():
    # Block dollars 0.6 above normal while market totals stay flat: z = 4.0469.
    w = with_blocks(weekly(ALTERNATING + [0.6]), [0.0] * 9)
    scored, _ = ww.score_finra(w, market(w.index), FINRA_CFG, 8)
    assert scored["z_block_usd"].iloc[-1] == pytest.approx(SPIKE_Z, abs=1e-3)


def test_dollar_score_cancels_a_market_wide_rise():
    w = with_blocks(weekly(ALTERNATING + [0.6]), [0.0] * 9)
    mkt = market(w.index, dollars=[1e9] * 8 + [1e9 * np.exp(0.6)])
    scored, _ = ww.score_finra(w, mkt, FINRA_CFG, 8)
    assert scored["z_block_usd"].iloc[-1] == pytest.approx(0.0, abs=1e-6)


def test_normal_block_dollars_leave_out_the_current_week():
    w = with_blocks(weekly([0.0] * 9), [0.0] * 8 + [2.0])
    w["block_dollars"] = [1e6, 1e6, 1e6, 1e6, 2e6, 2e6, 2e6, 2e6, 9e6]
    scored, _ = ww.score_finra(w, pd.DataFrame(), FINRA_CFG, 8)
    assert scored["block_normal_usd"].iloc[-1] == pytest.approx(1.5e6)


def test_dollar_score_does_not_change_the_finra_flag():
    w = with_blocks(weekly(ALTERNATING + [0.6]), [0.0] * 9)
    scored, _ = ww.score_finra(w, market(w.index), FINRA_CFG, 8)
    assert not bool(scored["flag"].iloc[-1])


def test_block_score_needs_no_market_total():
    w = with_blocks(weekly(ALTERNATING + [0.0]), ALTERNATING + [0.6])
    scored, _ = ww.score_finra(w, market(w.index[:8]), FINRA_CFG, 8)
    assert np.isnan(scored["z_volume"].iloc[-1])
    assert scored["z_block"].iloc[-1] == pytest.approx(SPIKE_Z, abs=1e-3)


def test_week_with_no_block_dollars_is_unscored_not_a_crash():
    w = with_blocks(weekly(ALTERNATING + [0.0]), ALTERNATING + [0.0])
    w.iloc[-1, w.columns.get_loc("block_dollars")] = 0.0
    scored, _ = ww.score_finra(w, pd.DataFrame(), FINRA_CFG, 8)
    assert np.isnan(scored["z_block"].iloc[-1])
    assert not bool(scored["flag"].iloc[-1])


def test_normal_block_share_is_the_median_of_earlier_weeks_only():
    w = with_blocks(weekly(ALTERNATING + [0.0]), [0.0] * 8 + [2.0])
    scored, _ = ww.score_finra(w, pd.DataFrame(), FINRA_CFG, 8)
    assert scored["block_normal"].iloc[-1] == pytest.approx(0.01)


def test_normal_block_share_leaves_out_the_current_week():
    # Earlier eight weeks: four at 1% and four at 2%, so the median is 1.5%.
    # Counting the current week would shift the window and give 2%.
    double = float(np.log(2))
    w = with_blocks(weekly([0.0] * 9), [0.0] * 4 + [double] * 4 + [2.0])
    scored, _ = ww.score_finra(w, pd.DataFrame(), FINRA_CFG, 8)
    assert scored["block_normal"].iloc[-1] == pytest.approx(0.015)


def test_block_dollars_ignore_non_ats_rows_for_the_same_firm(monkeypatch):
    week = "2026-10-05"
    otc = {**firm_row(week, "LQNA", 500.0), "summaryTypeCode": "OTC_W_SMBL_FIRM"}
    fake_finra(monkeypatch, {"ORCL": [firm_row(week, "LQNA", 58.0), otc]})
    df = ww.fetch_finra({"issueSymbolIdentifier": "ORCL"}, week, week, {})
    assert ww.finra_block_weekly(df, {"LQNA"}).loc[pd.Timestamp(week)] == 58.0


def test_ticker_without_block_data_is_not_flagged():
    scored, _ = ww.score_finra(weekly(ALTERNATING + [0.6]), pd.DataFrame(), FINRA_CFG, 8)
    assert scored["z_block"].isna().all()
    assert not scored["flag"].any()


def test_block_venues_come_from_the_latest_month_at_or_above_half(monkeypatch):
    fake_finra(monkeypatch, {"200K": [
        block_row("2026-07-01", "OLDX", 90.0), block_row("2026-07-01", "LQNT", 97.0),
        block_row("2026-08-01", "OLDX", 20.0), block_row("2026-08-01", "LQNT", 96.3),
        block_row("2026-08-01", "LQNA", 50.0), block_row("2026-08-01", "BIDS", 49.9)]})
    assert ww.fetch_block_venues(dt.date(2026, 10, 30), {}) == {"LQNT", "LQNA"}


def test_failed_block_venue_fetch_returns_nothing_and_says_why(monkeypatch, capsys):
    fake_finra(monkeypatch, {"200K": ConnectionError("FINRA down")})
    assert ww.fetch_block_venues(dt.date(2026, 10, 30), {}) == set()
    assert "FINRA down" in capsys.readouterr().err


def test_no_published_block_months_returns_nothing(monkeypatch):
    fake_finra(monkeypatch, {})
    assert ww.fetch_block_venues(dt.date(2026, 10, 30), {}) == set()


def test_block_dollars_add_block_venues_and_ignore_the_rest(monkeypatch):
    week = "2026-10-05"
    fake_finra(monkeypatch, {"ORCL": [
        firm_row(week, "LQNA", 58.0), firm_row(week, "LQNT", 8.0), firm_row(week, "UBSA", 900.0),
        finra_row(week, "ATS_W_SMBL", "T1", "CTS", 100, 966.0, 10, "ORCL")]})
    df = ww.fetch_finra({"issueSymbolIdentifier": "ORCL"}, week, week, {})
    assert ww.finra_block_weekly(df, {"LQNA", "LQNT"}).loc[pd.Timestamp(week)] == 66.0


def test_block_dollars_keep_only_the_latest_revision_of_a_venue_week(monkeypatch):
    week = "2026-10-05"
    fake_finra(monkeypatch, {"ORCL": [firm_row(week, "LQNA", 50.0, "2026-10-26"),
                                      firm_row(week, "LQNA", 58.0, "2026-11-02")]})
    df = ww.fetch_finra({"issueSymbolIdentifier": "ORCL"}, week, week, {})
    assert ww.finra_block_weekly(df, {"LQNA"}).loc[pd.Timestamp(week)] == 58.0


def test_closeness_is_the_block_score_as_a_percent_of_its_threshold():
    # Week 0.3 above normal: z = 0.3 / 0.14826 = 2.0234, and 2.0234 / 3.0 = 67.45%.
    w = with_blocks(weekly(ALTERNATING + [0.0]), ALTERNATING + [0.3])
    scored, _ = ww.score_finra(w, pd.DataFrame(), FINRA_CFG, 8)
    assert scored["closeness"].iloc[-1] == pytest.approx(67.45, abs=0.01)


def test_closest_weeks_are_the_highest_scoring_and_skip_unscored_weeks():
    idx = pd.date_range("2026-01-05", periods=5, freq="7D")
    w = pd.DataFrame({"closeness": [np.nan, 10.0, 40.0, 30.0, 20.0]}, index=idx)
    assert ww.closest_weeks(w, 2)["closeness"].tolist() == [40.0, 30.0]


def test_closest_weeks_is_empty_when_nothing_was_scored():
    idx = pd.date_range("2026-01-05", periods=2, freq="7D")
    assert ww.closest_weeks(pd.DataFrame({"closeness": [np.nan, np.nan]}, index=idx)).empty


# ------------------------------------------------------------- finra run ----

def run_scan(monkeypatch, tmp_path, block_spike=0.0, venues=("LQNA",), **overrides):
    """Scan ORCL over ten recent weeks with a block spike of e^block_spike two weeks ago."""
    monkeypatch.chdir(tmp_path)
    today = dt.date.today()
    monday = today - dt.timedelta(days=today.weekday())
    weeks = [(monday - dt.timedelta(weeks=n)).isoformat() for n in range(10, 0, -1)]
    dollars = [100.0] * 10
    blocks = [0.9, 1.1] * 4 + [1.0 * np.exp(block_spike), 1.0]
    month = (today.replace(day=1) - dt.timedelta(days=1)).replace(day=1).isoformat()
    rows = [finra_row(w, "ATS_W_SMBL", "T1", "CTS", 10, d, 2, "ORCL") for w, d in zip(weeks, dollars)]
    rows += [firm_row(w, "LQNA", b) for w, b in zip(weeks, blocks)]
    fake_finra(monkeypatch, {"ORCL": rows, "200K": [block_row(month, v, 96.0) for v in venues]})
    args = {"tickers": ["ORCL"], "sensitivity": "low", "weeks": 12, "baseline": 8,
            "z_volume": None, "z_size": None, "min_streak": None, **overrides}
    ww.cmd_finra(argparse.Namespace(**args))
    return weeks[-2]


def test_quiet_ticker_shows_its_closest_weeks_as_unflagged(monkeypatch, tmp_path, capsys):
    run_scan(monkeypatch, tmp_path, block_spike=0.1)
    out = capsys.readouterr().out
    assert "ORCL: 0 block-activity week(s)" in out
    assert "No week met the bar" in out
    assert "closeness" in out


def test_block_spike_is_reported_and_ranked(monkeypatch, tmp_path, capsys):
    week = run_scan(monkeypatch, tmp_path, block_spike=1.0)
    out = capsys.readouterr().out
    assert "ORCL: 1 block-activity week(s)" in out
    assert week in out
    assert "No week met the bar" not in out
    summary = pd.read_csv(tmp_path / ww.OUT_DIR / "finra_summary.csv")
    assert summary["flagged_weeks"].tolist() == [1]
    assert summary["heavy_weeks"].tolist() == [0]


def test_z_block_override_changes_the_bar(monkeypatch, tmp_path, capsys):
    run_scan(monkeypatch, tmp_path, block_spike=1.0, z_block=99.0)
    assert "ORCL: 0 block-activity week(s)" in capsys.readouterr().out


def test_scan_without_block_venues_says_so_and_still_finishes(monkeypatch, tmp_path, capsys):
    run_scan(monkeypatch, tmp_path, block_spike=1.0, venues=())
    out = capsys.readouterr().out
    assert "block venue list unavailable" in out
    assert "ORCL: 0 block-activity week(s)" in out


def test_ticker_with_no_recent_weeks_does_not_stop_the_scan(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    today = dt.date.today()
    recent = (today - dt.timedelta(weeks=1)).isoformat()
    old = (today - dt.timedelta(weeks=20)).isoformat()
    fake_finra(monkeypatch, {
        "OLD": [finra_row(old, "ATS_W_SMBL", "T1", "CTS", 10, 100.0, 2, "OLD")],
        "NEW": [finra_row(recent, "ATS_W_SMBL", "T1", "CTS", 10, 100.0, 2, "NEW")],
    })
    args = argparse.Namespace(tickers=["OLD", "NEW"], sensitivity="low", weeks=4,
                              baseline=26, z_volume=None, z_size=None, min_streak=None)
    ww.cmd_finra(args)
    out = capsys.readouterr().out
    assert "OLD: no dark-pool data in the last 4 weeks" in out
    summary = pd.read_csv(tmp_path / ww.OUT_DIR / "finra_summary.csv")
    assert summary["ticker"].tolist() == ["NEW"]


# ------------------------------------------------------------ Alpaca fakes ----

def trade(clock, exchange, price, size, conds=(" ",), tape="A"):
    """One record as Alpaca's /v2/stocks/{sym}/trades returns it."""
    return {"t": f"2026-10-07T{clock}.123456789Z", "x": exchange, "p": price, "s": size,
            "c": list(conds), "i": 1, "z": tape}


LIT = [trade(f"14:00:0{i}", "N", 100.00, 100) for i in range(5)]     # $10k each, $50k total


def analyze(*extra, cfg=PRINTS_CFG):
    df = pd.DataFrame(LIT + list(extra))
    return ww.analyze_day(df, cfg)


# ------------------------------------------------------------- block logic ----

def test_large_dark_print_becomes_a_block():
    summ, blocks = analyze(trade("14:10:00", "D", 100.05, 20_000))
    assert summ["block_cutoff_$"] == 1_000_000
    assert summ["blocks"] == 1
    assert summ["block_$M"] == pytest.approx(2.001)
    assert summ["day_$M"] == pytest.approx(2.051)
    assert summ["block_share_%"] == pytest.approx(97.5622, abs=1e-3)
    assert summ["imbalance"] == 1.0
    assert summ["flag"] == "BUY-SIDE?"
    assert blocks["lean"].tolist() == ["buy?"]


def test_print_below_last_exchange_price_leans_sell():
    summ, blocks = analyze(trade("14:10:00", "D", 99.95, 20_000))
    assert blocks["lean"].tolist() == ["sell?"]
    assert summ["flag"] == "SELL-SIDE?"


def test_large_pieces_of_one_order_are_rejoined():
    summ, blocks = analyze(trade("14:10:00", "D", 100.05, 6_000),
                           trade("14:10:01", "D", 100.05, 6_000))
    assert summ["blocks"] == 1
    assert blocks["pieces"].tolist() == [2]
    assert blocks["notional"].iloc[0] == pytest.approx(1_200_600)


def test_pieces_too_far_apart_are_not_rejoined():
    summ, _ = analyze(trade("14:10:00", "D", 100.05, 6_000),
                      trade("14:10:05", "D", 100.05, 6_000))
    assert summ["blocks"] == 0


def test_retail_sized_pieces_cannot_add_up_to_a_block():
    retail = [trade(f"14:10:{i:02d}", "D", 100.05, 900) for i in range(30)]   # $90,045 each
    summ, _ = analyze(*retail)
    assert summ["blocks"] == 0


def test_trades_outside_regular_hours_are_ignored():
    summ, _ = analyze(trade("13:29:59", "D", 100.05, 20_000),
                      trade("20:00:00", "D", 100.05, 20_000))
    assert summ["blocks"] == 0
    assert summ["day_$M"] == pytest.approx(0.05)


@pytest.mark.parametrize("code", ["C", "G", "H", "N", "P", "R", "T", "U", "V", "W", "Z", "4", "7"])
def test_prints_that_are_not_fresh_trades_never_count_as_blocks(code):
    summ, _ = analyze(trade("14:10:00", "D", 100.05, 20_000, (" ", code)))
    assert summ["blocks"] == 0


@pytest.mark.parametrize("tape, blocks", [("A", 0), ("B", 0), ("C", 1)])
def test_code_b_is_average_price_on_nyse_tapes_but_bunched_on_nasdaq(tape, blocks):
    summ, _ = analyze(trade("14:10:00", "D", 100.05, 20_000, ("B",), tape))
    assert summ["blocks"] == blocks


@pytest.mark.parametrize("code", ["M", "Q", "9"])
def test_records_that_carry_no_volume_stay_out_of_day_dollars(code):
    summ, _ = analyze(trade("14:10:00", "N", 100.00, 1_000_000, (code,)))
    assert summ["day_$M"] == pytest.approx(0.05)


def test_day_of_only_no_volume_records_is_not_a_session():
    df = pd.DataFrame([trade("14:10:00", "N", 100.00, 1_000_000, ("Q",))])
    summ, blocks = ww.analyze_day(df, PRINTS_CFG)
    assert summ is None
    assert blocks.empty


def test_trades_with_null_or_missing_conditions_are_treated_as_regular():
    no_conds = trade("14:10:00", "D", 100.05, 20_000)
    del no_conds["c"]
    summ, _ = analyze(no_conds, {**trade("14:11:00", "D", 100.05, 20_000), "c": None})
    assert summ["blocks"] == 2


def test_late_exchange_print_is_not_used_as_the_reference_price():
    summ, blocks = analyze(trade("14:09:59", "N", 110.00, 100, ("Z",)),
                           trade("14:10:00", "D", 100.05, 20_000))
    assert blocks["lean"].tolist() == ["buy?"]
    assert blocks["ref_px"].tolist() == [100.00]


def test_late_exchange_print_cannot_raise_the_block_cutoff():
    cfg = {**PRINTS_CFG, "quantile": 1.0}
    summ, _ = analyze(trade("14:09:59", "N", 100.00, 500_000, ("V",)), cfg=cfg)
    assert summ["block_cutoff_$"] == 1_000_000


# ---------------------------------------------------------- session walking ----

def fake_trades(monkeypatch, by_date):
    calls = []

    def fetch(sym, start, end, headers):
        day = dt.date.fromisoformat(start[:10])
        calls.append(day)
        return pd.DataFrame(by_date.get(day, []))
    monkeypatch.setattr(ww, "fetch_trades", fetch)
    return calls


def session(day, *extra):
    rows = LIT + list(extra)
    stamp = day.isoformat()
    return [{**r, "t": r["t"].replace("2026-10-07", stamp)} for r in rows]


def test_requested_days_are_sessions_not_calendar_weekdays(monkeypatch):
    fri, mon = dt.date(2026, 10, 2), dt.date(2026, 10, 5)
    wed = dt.date(2026, 10, 7)
    premarket = [{**LIT[0], "t": "2026-10-07T12:00:00.000000000Z"}]
    calls = fake_trades(monkeypatch, {fri: session(fri), mon: session(mon), wed: premarket})
    now = dt.datetime(2026, 10, 7, 13, 0, tzinfo=dt.timezone.utc)      # before the open

    rows, _ = ww.scan_sessions("ORCL", 2, now, PRINTS_CFG, "D", {})

    assert [r["date"] for r in rows] == [fri, mon]                      # oldest first
    assert all(d.weekday() < 5 for d in calls)                          # weekend skipped


def test_session_walk_stops_when_there_is_no_data(monkeypatch):
    calls = fake_trades(monkeypatch, {})
    now = dt.datetime(2026, 10, 7, 13, 0, tzinfo=dt.timezone.utc)
    rows, blocks = ww.scan_sessions("ORCL", 1, now, PRINTS_CFG, "D", {})
    assert rows == []
    assert blocks.empty
    assert len(calls) == 6


def test_block_table_has_only_block_columns_when_a_day_has_none(monkeypatch):
    quiet, busy = dt.date(2026, 10, 5), dt.date(2026, 10, 6)
    fake_trades(monkeypatch, {
        quiet: session(quiet),
        busy: session(busy, trade("14:10:00", "D", 100.05, 20_000)),
    })
    now = dt.datetime(2026, 10, 6, 21, 0, tzinfo=dt.timezone.utc)
    rows, blocks = ww.scan_sessions("ORCL", 2, now, PRINTS_CFG, "D", {})
    assert len(rows) == 2
    assert sorted(blocks.columns) == sorted(["ts", "p", "s", "notional", "pieces", "ref_px",
                                             "lean", "date"])
