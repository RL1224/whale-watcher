import argparse
import datetime as dt
import re

import numpy as np
import pandas as pd
import pytest

import whale_chart as wc
import whale_watch as ww
from tests.test_whale_watch import block_row, fake_finra, finra_row, firm_row


def scored(z, vwap=None, block=None):
    """The columns of score_finra that charting reads, one row per week."""
    idx = pd.date_range("2026-01-05", periods=len(z), freq="7D")
    n = len(z)
    return pd.DataFrame({
        "z_block": np.asarray(z, dtype=float),
        "vwap": np.asarray(vwap if vwap is not None else [100.0] * n, dtype=float),
        "block_dollars": np.asarray(block if block is not None else [1e6] * n, dtype=float),
        "block_share": [0.01] * n,
        "block_normal": [0.008] * n,
        "block_normal_usd": [8e5] * n,
    }, index=idx)


def spans(periods):
    return [(p["start"].strftime("%m-%d"), p["end"].strftime("%m-%d")) for p in periods]


# ---------------------------------------------------------------- periods ----

def test_one_strong_week_is_a_one_week_period():
    periods = wc.find_periods(scored([0, 0, 3.5, 0, 0]), enter=3.0)
    assert spans(periods) == [("01-19", "01-19")]
    assert periods[0]["weeks"] == 1


def test_elevated_weeks_on_both_sides_extend_the_period():
    periods = wc.find_periods(scored([0, 1.2, 3.5, 1.5, 0]), enter=3.0)
    assert spans(periods) == [("01-12", "01-26")]
    assert periods[0]["weeks"] == 3


def test_elevated_weeks_that_never_clear_the_bar_are_not_a_period():
    assert wc.find_periods(scored([0, 1.5, 2.9, 1.5, 0]), enter=3.0) == []


def test_one_quiet_week_inside_does_not_split_a_period():
    periods = wc.find_periods(scored([3.5, 0.2, 1.5, 0]), enter=3.0)
    assert spans(periods) == [("01-05", "01-19")]
    assert periods[0]["weeks"] == 3


def test_two_quiet_weeks_end_a_period():
    periods = wc.find_periods(scored([3.5, 0.2, 0.2, 3.1]), enter=3.0)
    assert spans(periods) == [("01-05", "01-05"), ("01-26", "01-26")]


def test_week_with_no_score_counts_as_quiet():
    periods = wc.find_periods(scored([3.5, np.nan, np.nan, 3.1]), enter=3.0)
    assert len(periods) == 2


def test_period_reports_peak_and_block_dollars():
    periods = wc.find_periods(scored([1.2, 3.5, 2.0], block=[1e6, 2e6, 3e6]), enter=3.0)
    p = periods[0]
    assert p["peak_z"] == 3.5
    assert p["peak_week"] == pd.Timestamp("2026-01-12")
    assert p["block_dollars"] == 6e6


def test_price_change_runs_from_the_week_before_the_period_to_its_end():
    periods = wc.find_periods(scored([0, 3.5, 3.5, 0], vwap=[100.0, 104.0, 110.0, 90.0]), enter=3.0)
    assert periods[0]["price_chg"] == pytest.approx(10.0)


def test_price_change_uses_the_first_week_when_nothing_comes_before():
    periods = wc.find_periods(scored([3.5, 3.5, 0], vwap=[100.0, 120.0, 90.0]), enter=3.0)
    assert periods[0]["price_chg"] == pytest.approx(20.0)


def test_no_scored_weeks_gives_no_periods():
    assert wc.find_periods(scored([np.nan, np.nan]), enter=3.0) == []


def test_score_takes_the_higher_of_share_and_dollars():
    s = scored([1.0, 3.0, np.nan, np.nan])
    s["z_block_usd"] = [2.5, 1.0, 1.7, np.nan]
    out = wc.with_score(s)
    assert out["score"].tolist()[:3] == [2.5, 3.0, 1.7]
    assert np.isnan(out["score"].iloc[3])


def test_periods_can_follow_the_combined_score():
    s = scored([0, 0, 0, 0])
    s["z_block_usd"] = [0, 3.5, 0, 0]
    periods = wc.find_periods(wc.with_score(s), enter=3.0, col="score")
    assert spans(periods) == [("01-12", "01-12")]


# ------------------------------------------------------------ price check ----

def prices(values):
    return scored([0.0] * len(values), vwap=values)


def test_position_is_where_the_price_sits_in_its_range():
    s = wc.with_price_position(prices([100.0] * 13 + [150.0] * 13 + [125.0]))
    assert s["price_pos"].iloc[-1] == pytest.approx(50.0)


def test_position_is_zero_at_the_low_and_full_at_the_high():
    rising = wc.with_price_position(prices([100.0 + i for i in range(30)]))
    falling = wc.with_price_position(prices([200.0 - i for i in range(30)]))
    assert rising["price_pos"].iloc[-1] == 100.0
    assert falling["price_pos"].iloc[-1] == 0.0


def test_position_needs_half_a_year_of_prices():
    s = wc.with_price_position(prices([100.0 + i for i in range(25)]))
    assert s["price_pos"].isna().all()


def test_position_is_blank_for_a_year_after_a_split_like_jump():
    # An unadjusted 10:1 split would otherwise read as a crash to the low.
    s = wc.with_price_position(prices([1000.0 + i for i in range(30)] + [100.0 + i for i in range(60)]))
    assert s["price_pos"].iloc[30:82].isna().all()
    assert s["price_pos"].iloc[82:].notna().all()


def test_price_never_changes_the_score_or_the_periods():
    s = scored([0, 1.2, 3.5, 1.5, 0], vwap=[10.0, 500.0, 3.0, 900.0, 40.0])
    before = wc.find_periods(s, enter=3.0)
    after = wc.find_periods(wc.with_price_position(s), enter=3.0)
    assert spans(before) == spans(after)
    assert before[0]["peak_z"] == after[0]["peak_z"]


def test_period_records_the_price_position_where_it_started():
    s = scored([0] * 27 + [3.5, 3.5], vwap=[100.0] * 13 + [140.0] * 14 + [110.0, 136.0])
    periods = wc.find_periods(wc.with_price_position(s), enter=3.0)
    assert periods[0]["price_pos"] == pytest.approx(25.0)


@pytest.mark.parametrize("pos, label", [(10.0, "Low"), (33.0, "Low"), (50.0, "Middle"), (90.0, "High"), (float("nan"), "–")])
def test_price_labels(pos, label):
    assert wc.price_label(pos) == label


def test_every_week_shows_its_price_position_in_the_table():
    s = wc.with_price_position(scored([0] * 27, vwap=[100.0] * 13 + [140.0] * 13 + [110.0]))
    html = wc.render_chart("MSFT", s, [], wc.current_status(s, []), enter=3.0, as_of=AS_OF)
    assert "<td>Low (25%)</td>" in html


def test_chart_shows_each_periods_price_check_and_the_tally():
    s = scored([0] * 27 + [3.5, 0, 0, 3.5], vwap=[100.0] * 13 + [140.0] * 14 + [110.0, 120.0, 120.0, 136.0])
    s = wc.with_price_position(s)
    periods = wc.find_periods(s, enter=3.0)
    html = wc.render_chart("MSFT", s, periods, wc.current_status(s, periods), enter=3.0, as_of=AS_OF)
    assert "Low (25%)" in html
    assert "High (90%)" in html
    assert "1 of 2 periods started in the lower third" in html
    assert "not part of the score" in html


# ----------------------------------------------------------------- status ----

def status_for(z):
    s = scored(z)
    return wc.current_status(s, wc.find_periods(s, enter=3.0))


def test_status_is_active_when_the_latest_week_is_in_a_period():
    st = status_for([0, 0, 1.0, 3.5])
    assert st["state"] == "active"
    assert st["since"] == pd.Timestamp("2026-01-19")


def test_sentence_names_the_start_only_for_a_period_longer_than_one_week():
    assert "running since 2026-01-12" in wc.status_sentence(status_for([0, 1.2, 3.5]), "ORCL")
    assert "running since" not in wc.status_sentence(status_for([0, 0, 3.5]), "ORCL")


def test_status_is_recent_within_four_weeks_of_a_period_ending():
    st = status_for([3.5, 0, 0, 0, 0])
    assert st["state"] == "recent"
    assert st["weeks_ago"] == 4


def test_status_is_quiet_once_a_period_is_older_than_four_weeks():
    assert status_for([3.5, 0, 0, 0, 0, 0])["state"] == "quiet"


def test_status_is_quiet_with_no_periods_at_all():
    assert status_for([0, 0, 0])["state"] == "quiet"


def test_status_is_unknown_when_the_latest_week_has_no_score():
    assert status_for([0, 0, np.nan])["state"] == "unknown"


def test_status_never_tells_the_reader_to_buy_or_sell():
    for z in ([0, 3.5], [3.5, 0, 0], [0, 0], [0, np.nan]):
        text = wc.status_sentence(status_for(z), "ORCL").lower()
        assert not re.search(r"\b(buy|sell|buying|selling|entering|exiting)\b", text)


# ------------------------------------------------------------------ chart ----

def page(z=(0, 1.2, 3.5, 1.5, 0), sym="ORCL"):
    s = scored(list(z))
    periods = wc.find_periods(s, enter=3.0)
    return wc.render_chart(sym, s, periods, wc.current_status(s, periods), enter=3.0, as_of=dt.date(2026, 10, 30))


def test_chart_shades_each_period_once():
    assert page((3.5, 0, 0, 0, 3.5)).count('class="period-shade"') == 4        # two panels, two periods


def test_chart_has_a_bar_and_a_table_row_for_each_week():
    html = page()
    assert html.count('class="bar') == 5
    assert html.count('<tr class="week"') == 5


def test_chart_marks_only_period_weeks_as_active():
    assert page().count('class="bar active"') == 3


def test_weeks_near_the_bar_are_marked_elevated_but_not_active():
    assert page((0, 0, 1.6, 0, 0)).count('class="bar elevated"') == 1
    assert page((0, 0, 1.6, 0, 0)).count('class="bar active"') == 0


def test_week_below_the_elevated_line_stays_plain():
    assert 'class="bar elevated"' not in page((0, 0, 1.4, 0, 0))


def test_a_week_in_a_period_is_active_even_when_it_also_counts_as_elevated():
    html = page((3.5, 1.6, 0))
    assert html.count('class="bar active"') == 2
    assert 'class="bar elevated"' not in html


def test_bars_are_drawn_in_dollars_so_the_biggest_week_is_the_tallest():
    s = scored([0, 0, 0], block=[1e6, 9e6, 2e6])
    periods = wc.find_periods(s, enter=3.0)
    html = wc.render_chart("MSFT", s, periods, wc.current_status(s, periods), enter=3.0, as_of=AS_OF)
    heights = [float(m) for m in re.findall(r'class="bar[^"]*" d="M[0-9.]+ ([0-9.]+)V([0-9.]+)', html)[0:0]]
    tops = [float(m) for m in re.findall(r'class="bar[^"]*" d="M[0-9.]+ [0-9.]+V([0-9.]+)', html)]
    assert tops.index(min(tops)) == 1
    assert "Block-venue dollars each week ($M)" in html


def test_chart_explains_elevated_weeks():
    assert "Elevated" in page()


def test_chart_states_the_data_date_and_the_lag():
    html = page()
    assert "2026-02-02" in html
    assert "Oct 30, 2026" in html


def test_chart_says_it_cannot_show_direction():
    assert "can't show whether" in page()


def test_chart_states_what_testing_found():
    html = page()
    assert "no better than" in html
    assert "60 stocks" in html


def test_chart_does_not_claim_to_show_whales():
    html = page((0, 0, 3.5)).lower()
    assert "whale activity" not in html
    assert "whale period" not in html


def test_chart_draws_a_week_with_no_block_share_as_an_empty_bar():
    s = scored([0, 0, 3.5])
    s["block_share"] = [0.01, np.nan, 0.01]
    s["block_normal"] = [np.nan, 0.01, 0.01]
    periods = wc.find_periods(s, enter=3.0)
    html = wc.render_chart("ORCL", s, periods, wc.current_status(s, periods), enter=3.0, as_of=dt.date(2026, 10, 30))
    assert not re.search(r"(?<![a-z])nan", html)
    assert html.count('class="bar') == 3


def test_chart_escapes_the_ticker():
    html = page(sym='<script>alert("x")</script>')
    assert '<script>alert("x")' not in html


def test_chart_handles_weeks_without_a_score():
    html = page((np.nan, np.nan, 3.5, np.nan))
    assert "NaN" not in html
    assert html.count('class="bar') == 4


def test_chart_handles_a_single_week():
    assert page((3.5,)).count('class="bar') == 1


def test_chart_handles_a_flat_price():
    assert "<path" in page((0, 0, 0))


# --------------------------------------------------------------- holdings ----

def holder(owner, date, change, new=False):
    return {"owner": owner, "date": date, "change": change, "new": new}


def filers(date, n, change=0.0):
    return [holder(f"Filer {date} {i}", date, change) for i in range(n)]


HOLDINGS = {"outstanding": 1_000_000.0, "rows": filers("6/30/2026", 100) + [
    holder("Big Fund", "6/30/2026", 30_000.0), holder("Other Fund", "6/30/2026", 20_000.0),
    holder("Seller", "6/30/2026", -10_000.0), holder("Reorganized Holdco", "6/30/2026", 500_000.0, new=True),
    holder("Stale Filer", "12/31/2025", 999_999.0)]}
AS_OF = dt.date(2026, 10, 30)


def test_quarter_nets_existing_holders_and_keeps_new_positions_apart():
    q = wc.holdings_by_quarter(HOLDINGS, AS_OF)[0]
    assert q["quarter_end"] == pd.Timestamp("2026-06-30")
    assert q["raised"] == 2
    assert q["cut"] == 1
    assert q["net_shares"] == 40_000.0
    assert q["net_pct"] == pytest.approx(4.0)
    assert q["new_shares"] == 500_000.0


def test_largest_adds_are_existing_holders_biggest_first():
    q = wc.holdings_by_quarter(HOLDINGS, AS_OF)[0]
    assert [a["owner"] for a in q["top_adds"]] == ["Big Fund", "Other Fund"]


def test_quarter_with_few_filers_is_left_out():
    assert len(wc.holdings_by_quarter(HOLDINGS, AS_OF)) == 1


def test_quarter_is_complete_only_after_the_filing_deadline():
    rows = {"outstanding": 1e6, "rows": filers("9/30/2026", 150, 1.0)}
    assert wc.holdings_by_quarter(rows, dt.date(2026, 11, 13))[0]["complete"] is False
    assert wc.holdings_by_quarter(rows, dt.date(2026, 11, 14))[0]["complete"] is True


def test_quarters_are_newest_first():
    rows = {"outstanding": 1e6, "rows": filers("3/31/2026", 120, 1.0) + filers("6/30/2026", 120, 1.0)}
    assert [q["quarter_end"].month for q in wc.holdings_by_quarter(rows, AS_OF)] == [6, 3]


def test_holdings_sentence_uses_the_latest_complete_quarter():
    rows = {"outstanding": 1e6, "rows": HOLDINGS["rows"] + filers("9/30/2026", 150, 1.0)}
    text = wc.holdings_sentence(wc.holdings_by_quarter(rows, AS_OF), "ORCL")
    assert "Apr to Jun 2026" in text
    assert "0.04M" in text and "4.00%" in text
    assert "2 raised" in text and "1 cut" in text


def test_holdings_sentence_says_when_institutions_cut_shares():
    rows = {"outstanding": 1e6, "rows": filers("6/30/2026", 100) + [holder("Seller", "6/30/2026", -5000.0)]}
    assert "net cut" in wc.holdings_sentence(wc.holdings_by_quarter(rows, AS_OF), "ORCL")


def test_chart_warns_that_tall_bars_can_be_busy_weeks():
    assert "busy week" in page()


def page_with(holdings):
    s = scored([0, 1.2, 3.5])
    periods = wc.find_periods(s, enter=3.0)
    return wc.render_chart("ORCL", s, periods, wc.current_status(s, periods), enter=3.0, as_of=AS_OF, holdings=holdings)


def test_chart_shows_holdings_with_owner_names_escaped():
    rows = {"outstanding": 1e6, "rows": filers("6/30/2026", 100) + [holder("<b>Fund</b>", "6/30/2026", 5000.0)]}
    html = page_with(rows)
    assert "Institutions adding or cutting shares" in html
    assert "&lt;b&gt;Fund&lt;/b&gt;" in html
    assert "<b>Fund</b>" not in html


def test_chart_explains_new_positions_and_filing_lag():
    html = page_with(HOLDINGS)
    assert "reorganized" in html
    assert "45 days" in html


def test_chart_says_when_holdings_are_unavailable():
    assert "Holdings data wasn't available" in page_with(None)


# -------------------------------------------------------------- command ----

def chart_args(tickers, **overrides):
    return argparse.Namespace(**{"tickers": tickers, "sensitivity": "medium", "weeks": 12, "baseline": 8,
                                 "z_block": None, "no_open": True, **overrides})


def fake_scan(monkeypatch, tmp_path, venues=("LQNA",), dollar_spike=False):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(ww, "fetch_holdings", lambda sym: None)
    today = dt.date.today()
    monday = today - dt.timedelta(days=today.weekday())
    weeks = [(monday - dt.timedelta(weeks=n)).isoformat() for n in range(10, 0, -1)]
    blocks = [0.9, 1.1] * 4 + [3.0, 1.0]
    month = (today.replace(day=1) - dt.timedelta(days=1)).replace(day=1).isoformat()
    totals = [100.0] * 10
    if dollar_spike:                     # block share stays ordinary, block dollars jump
        totals[8], blocks[8] = 900.0, 9.0
    rows = [finra_row(w, "ATS_W_SMBL", "T1", "CTS", 10, d, 2, "ORCL") for w, d in zip(weeks, totals)]
    rows += [firm_row(w, "LQNA", b) for w, b in zip(weeks, blocks)]
    fake_finra(monkeypatch, {"ORCL": rows, "200K": [block_row(month, v, 96.0) for v in venues]})


def test_chart_command_writes_a_page_and_reports_status(monkeypatch, tmp_path, capsys):
    fake_scan(monkeypatch, tmp_path)
    ww.cmd_chart(chart_args(["ORCL"]))
    out = capsys.readouterr().out
    assert (tmp_path / ww.OUT_DIR / "ORCL_chart.html").exists()
    assert "ORCL" in out and "ORCL_chart.html" in out


def test_chart_command_finds_a_period_from_dollars_alone(monkeypatch, tmp_path, capsys):
    fake_scan(monkeypatch, tmp_path, dollar_spike=True)
    ww.cmd_chart(chart_args(["ORCL"]))
    assert "peak score" in capsys.readouterr().out


def test_chart_command_prints_plain_text_when_a_period_has_no_price_position(monkeypatch, tmp_path, capsys):
    fake_scan(monkeypatch, tmp_path, dollar_spike=True)
    ww.cmd_chart(chart_args(["ORCL"]))
    line = next(x for x in capsys.readouterr().out.splitlines() if "peak score" in x)
    assert "started n/a in its 1-year range" in line
    assert line.isascii()


def test_chart_command_skips_an_unknown_ticker_and_keeps_going(monkeypatch, tmp_path, capsys):
    fake_scan(monkeypatch, tmp_path)
    ww.cmd_chart(chart_args(["NOPE", "ORCL"]))
    assert "NOPE: no dark-pool data" in capsys.readouterr().out
    assert (tmp_path / ww.OUT_DIR / "ORCL_chart.html").exists()


def test_chart_command_says_so_when_block_venues_are_unavailable(monkeypatch, tmp_path, capsys):
    fake_scan(monkeypatch, tmp_path, venues=())
    ww.cmd_chart(chart_args(["ORCL"]))
    assert "block venue list unavailable" in capsys.readouterr().out
    assert not (tmp_path / ww.OUT_DIR / "ORCL_chart.html").exists()


def test_fetch_holdings_reads_the_nasdaq_shape(monkeypatch):
    class Response:
        def raise_for_status(self):
            pass

        def json(self):
            return {"data": {"ownershipSummary": {"ShareoutstandingTotal": {"value": "7,426"}},
                             "holdingsTransactions": {"table": {"rows": [
                                 {"ownerName": "Fund A", "date": "6/30/2026", "sharesChange": "1,500", "sharesChangePCT": "2.5%"},
                                 {"ownerName": "Fund B", "date": "6/30/2026", "sharesChange": "-200", "sharesChangePCT": "-1%"},
                                 {"ownerName": "Fund C", "date": "6/30/2026", "sharesChange": "9,000", "sharesChangePCT": "New"}]}}}}

    monkeypatch.setattr(ww.requests, "get", lambda *a, **k: Response())
    h = ww.fetch_holdings("MSFT")
    assert h["outstanding"] == 7_426_000_000.0
    assert [r["change"] for r in h["rows"]] == [1500.0, -200.0, 9000.0]
    assert [r["new"] for r in h["rows"]] == [False, False, True]


def test_fetch_holdings_failure_returns_nothing_and_says_why(monkeypatch, capsys):
    def boom(*a, **k):
        raise ConnectionError("Nasdaq down")

    monkeypatch.setattr(ww.requests, "get", boom)
    assert ww.fetch_holdings("MSFT") is None
    assert "Nasdaq down" in capsys.readouterr().err
