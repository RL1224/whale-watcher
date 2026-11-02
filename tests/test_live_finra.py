"""Tests against the real FINRA API, using Oracle as the reference stock.

Skipped by default. Run them with:  pytest -m live

Reference values were checked on 2026-10-30. ORCL's week of 2025-09-08 had a
35.95% one-day move, and Yahoo's volume-weighted price for that week was within
1.07% of FINRA's. FINRA can revise old weeks, so the checks allow some slack.
"""
import argparse
import datetime as dt

import pandas as pd
import pytest

import whale_watch as ww

pytestmark = pytest.mark.live

SURGE_WEEK = pd.Timestamp("2025-09-08")
BLOCK_WEEK = pd.Timestamp("2026-10-05")


@pytest.fixture(scope="module")
def headers():
    return ww.finra_headers()


@pytest.fixture(scope="module")
def orcl_2025(headers):
    start, end = "2025-01-06", "2025-10-06"
    w = ww.finra_ticker_weekly(ww.fetch_finra({"issueSymbolIdentifier": "ORCL"}, start, end, headers))
    return w, ww.finra_market_weekly(start, end, headers)


def scored_block_week(sym, headers):
    """Score one ticker through 2026-10-05 with FINRA's real venue list."""
    start, end = "2026-01-05", "2026-10-11"
    venues = ww.fetch_block_venues(dt.date(2026, 10, 30), headers)
    raw = ww.fetch_finra({"issueSymbolIdentifier": sym}, start, end, headers)
    w = ww.finra_ticker_weekly(raw)
    w["block_dollars"] = ww.finra_block_weekly(raw, venues).reindex(w.index).fillna(0.0)
    mkt = ww.estimate_recent_market(ww.finra_market_weekly(start, end, headers),
                                    dt.date(2026, 10, 11), headers)
    scored, _ = ww.score_finra(w, mkt, ww.PRESETS["finra"]["low"], 26)
    return scored.loc[BLOCK_WEEK]


def test_orcl_surge_week_matches_the_public_record(orcl_2025):
    w, _ = orcl_2025
    week = w.loc[SURGE_WEEK]
    assert week["dollars"] / week["shares"] == pytest.approx(306.5, rel=0.02)
    assert week["dollars"] == pytest.approx(17.29e9, rel=0.02)


def test_orcl_surge_week_counts_as_heavy_trading_at_medium(orcl_2025):
    w, mkt = orcl_2025
    scored, _ = ww.score_finra(w, mkt, ww.PRESETS["finra"]["medium"], 26)
    assert bool(scored.loc[SURGE_WEEK, "heavy"])


def test_real_block_venue_list_has_the_known_specialists(headers):
    venues = ww.fetch_block_venues(dt.date(2026, 10, 30), headers)
    assert {"LQNT", "BLKX"} <= venues
    assert "UBSA" not in venues


def test_orcl_block_week_flags_at_the_default_setting_in_a_quiet_week(headers):
    week = scored_block_week("ORCL", headers)
    assert week["block_dollars"] == pytest.approx(80.6e6, rel=0.02)
    assert week["z_block"] >= 3.0
    assert bool(week["flag"])
    assert week["z_volume"] < 2.0


def test_same_week_is_not_flagged_for_a_control_ticker(headers):
    assert not bool(scored_block_week("AAPL", headers)["flag"])


def test_market_total_equals_the_sum_of_every_symbol(headers):
    week = "2026-09-07"
    symbols = ww.fetch_finra({"summaryTypeCode": "ATS_W_SMBL"}, week, week, headers)
    total = ww.finra_market_weekly(week, week, headers).loc[pd.Timestamp(week), "mkt_dollars"]
    assert total == pytest.approx(symbols["totalnotionalsum"].sum(), rel=1e-6)


def test_scan_scores_newest_weeks_across_tickers_with_different_lags(monkeypatch, tmp_path):
    # ORCL has weeks past the market total. TSM had none, which once crashed the scan.
    monkeypatch.chdir(tmp_path)
    args = argparse.Namespace(tickers=["ORCL", "TSM"], sensitivity="medium", weeks=8,
                              baseline=26, z_volume=None, z_size=None, min_streak=None)
    ww.cmd_finra(args)
    summary = pd.read_csv(tmp_path / ww.OUT_DIR / "finra_summary.csv").set_index("ticker")
    assert set(summary.index) == {"ORCL", "TSM"}
    assert summary[["z_volume_now", "z_size_now"]].notna().all(axis=None)
