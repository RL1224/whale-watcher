# whale-watch

A free scanner that shows when block-focused dark pools handled an unusual share of a stock's or ETF's trading, alongside what institutions reported adding or cutting each quarter.
It does not identify who traded. It has not shown that it predicts returns. One quarter of data links block share to net institutional buying, and that link still needs repeating.

## What testing found

In October 2026 the block signal was tested on 60 stocks that played no part in building it, with the pass rules written down first. It failed these tests of real-world meaning. A later test, under "Link to institutional buying", did find something.

| Test | Result |
|------|--------|
| Works from a clean install, and the numbers reproduce | Pass |
| Scores higher in weeks with $25M+ insider sales (437 weeks) | Fail: effect -0.03, p 0.58 |
| Block venues beat random ordinary dark pools on that test | Fail: 41st percentile, needed above the 95th |
| More trading or bigger price moves in the next 4 weeks | Fail: p 0.64 and p 0.99 |
| Price direction label predicts the next 4 weeks | Fail: p 0.50 |
| Buying after a flag beats buying at other times | Fail, see below |

Buying 3 weeks after a flagged week, once the data was public, and holding 13 weeks:

| | Entries | Up after 13 weeks | Beat SPY | Median return |
|-----------|---------|------|------|------|
| Score 3+ | 38 | 50% | 50% | -0.05% |
| Score 2+ | 163 | 62% | 50% | +4.98% |
| Same stocks, other weeks (score 3+ comparison) | 4,464 | 60% | 48% | +4.40% |
| Same stocks, other weeks (score 2+ comparison) | 8,499 | 60% | 47% | +4.04% |

One of the six holding-period checks reached p 0.048 (score 2+, 4 weeks). With six checks, one result like that is expected by chance. Insider sales are also an imperfect stand-in, because many are routine and may not use block venues. So the tests don't prove the signal is useless, but nothing shows it works. The stocks are today's large caps, so absolute returns are flattered and only the comparison between rows means anything.

### Link to institutional buying

This test used 13F holdings across 78 stocks for April to June 2026, counting existing holders only. Brand-new positions are left out because one filer appeared as a new holder across many stocks, including 80.8M NVDA shares, and that doesn't look like real buying.

| Average block score that quarter | Stocks | Median net change | Net bought by institutions |
|----------------------------------|--------|-------------------|----------------------------|
| Highest third | 26 | +0.27% of shares | 73% |
| Middle third | 26 | -0.32% | 27% |
| Lowest third | 26 | -1.41% | 23% |

The rank correlation was +0.50 (p below 0.0001). It stayed at +0.50 after controlling for price return and dark-pool volume, and it beat all 200 sets of random dark pools.

Treat this as promising and unconfirmed:

- It covers one quarter. July to September filings were tested too, but only early filers had reported, and that test showed nothing. Those filings are due November 16, 2026, and the test should be rerun after that.
- It was found after other tests failed, and 18 of the 78 stocks were used while building the signal.
- It's a pattern across stocks, and it says nothing about timing. A stock can go against it: ORCL had a below-average block score in that quarter and institutions still added 1.44%.
- Counting how many institutions raised positions, instead of net shares, showed a much weaker link (+0.11), measured before new positions were removed.

### Dollars and price lows

MSFT's two-year low close was on June 25, 2026. Block-venue dollars that week were $351M, in the top 1% of its last 104 weeks, and the stock rose 41% in the next 13 weeks. The share-only chart hid this, because all dark-pool trading surged that week, so the bars now show dollars. The dollar score for that week is 1.88, which is elevated but under the 2.0 bar. The bar wasn't lowered to catch it.

Testing the dollar score across stocks:

- Over April to June 2026, it also lined up with net institutional buying across 78 stocks (rank correlation +0.42, above all 200 random dark-pool sets).
- Buying after a dollar score of 2+ failed the buy test: 58% up after 13 weeks, against 60% for other weeks.
- Near a 52-week low it failed too, with 36 entries: 67% up against 56%, p 0.31, worst result -31%.
- Being near a 52-week low didn't help by itself across 80 stocks. The median 13-week return was +3.2% near a low, against +3.4% otherwise.

### Price as a reality check

Price position is never part of a score. It's an outside check: if highlighted weeks mean big buyers, they should tend to appear when a stock is cheap against its own recent range. Rule set first, on 60 stocks, using each stock's trailing 52-week range.

| | Highlighted weeks | Other weeks |
|---|---|---|
| Median position in 1-year range | 76% | 70% |
| In the lower third | 22% | 23% |
| In the upper third | 58% | 53% |

The check failed (p 0.96). Highlighted weeks sit slightly higher, so they don't look like buying at lows. Block data has no buy or sell side, so some highlights may be selling. These are today's large caps, which spend much of their time near highs.

One split was promising, though it was found by looking and hasn't been formally tested:

| Price at start | Periods | Median 13-week return | Up after 13 weeks | Any week in that zone |
|---|---|---|---|---|
| Lower third | 71 | +9.4% | 68% | +4.1%, 59% up |
| Middle third | 76 | +3.6% | 59% | +4.9%, 61% up |
| Upper third | 187 | +4.4% | 59% | +3.8%, 60% up |

The chart labels each period Low, Middle or High by where the price was when it started.

### Large trades at the MSFT low

Full-market Alpaca trades didn't show buying at MSFT's June low either. Net inferred buying was -$42M from June 15 to 30, against -$189M from October 5 to 16. The rule required a positive net at the low, so the test failed. The gap between the two windows wasn't significant (p 0.42).

### Overall

Don't read highlighted periods as whales entering. [The findings](docs/findings/2026-11-01-findings.md) collect every result, the saved output and the proposed next step. [The free tools report](reports/Free%20whale%20tracking%20tools.md) found no free site that shows institutions entering during a specific span of days or weeks with a real buy or sell side.

## Modes

| Mode | Data source | Cost | Delay | Use |
|------|-------------|------|-------|-----|
| `finra` | FINRA weekly dark-pool (ATS) data | Free, no key | ~2–4 weeks | Weekly block activity |
| `prints` | Alpaca trade data (full market) | Free account | 15+ minutes | Recent large blocks |

## Setup

```bash
pip install -r requirements.txt
```

For `prints`, create a free account at [alpaca.markets](https://alpaca.markets) (a paper account is fine). Then:

```bash
export ALPACA_KEY_ID=your_key
export ALPACA_SECRET_KEY=your_secret
```

## Usage

```bash
python whale_watch.py chart ORCL
python whale_watch.py finra ORCL NVDA SPY
python whale_watch.py finra ORCL --sensitivity medium --weeks 104
python whale_watch.py prints ORCL --days 3
```

Results print to the terminal and are saved in `whale_out/`.

`chart` also reads institutional holdings from Nasdaq's website. That isn't an official API, so it can change or stop working. If it does, the chart still builds and says the data wasn't available.

## The chart

`chart` looks back over the last 104 weeks and opens a page in your browser, with price on top and block-venue dollars below it, like a volume pane. Weeks in an active period are dark blue and shaded, and weeks that came close are light blue. The top of the page says where things stand now: high, faded recently, or quiet.

A week's score is the higher of two checks against that stock's recent past: block dollars, compared with the whole market's dark-pool dollars, and block venues' share of the stock's dark-pool dollars. Dollars show the size of a busy week, which share cancels out. A period starts when a week's score reaches the bar (2.0 at the chart's default `medium` sensitivity) and runs while nearby weeks score 1.0 or more, so it can span several weeks. One quiet week inside doesn't end it. The page doesn't say whether to buy or sell, and the testing above doesn't support using it as a signal for either.

Use `--weeks` to change how far back it goes, and `--no-open` to write the page without opening it.

## How `finra` flags a week

FINRA doesn't publish block trades per ticker, but it does publish two things that can be combined:

1. Each month, how much of each dark pool's business is in $200K+ trades. Pools at 50% or more count as block venues. In August 2026 those were BLKX, DLTA, LQNA and LQNT.
2. Each week, how many dollars of each ticker traded on each dark pool.

The scanner takes the share of a ticker's dark-pool dollars that ran through block venues, and flags weeks far above that ticker's own normal. Volume doesn't have to be high, so it can catch big orders in a quiet week.

| Column | Meaning |
|--------|---------|
| `block_$M` | Dollars on block venues that week |
| `block_%` | That amount as a share of the ticker's dark-pool dollars |
| `normal_%` | Median `block_%` over the baseline weeks before it |
| `z_block` | How far `block_%` is from normal, in robust standard deviations |
| `z_volume` | Same idea for overall dark-pool volume, for context |

Heavy trading is counted separately, as `heavy_weeks`: dark-pool dollars and average trade size both far above normal. It usually just means a busy week for the whole stock.

## Sensitivity

`--sensitivity low | medium | high` (default `low`) sets the bar for `z_block`: 3.0, 2.0 or 1.5.

- **low** flags only clearly abnormal weeks. Across 20 large stocks and ETFs it flagged 12 weeks in a year, about 1% of ticker-weeks.
- **medium** is balanced.
- **high** catches more but is noisier.

These thresholds match the volume thresholds and weren't fitted to any ticker.

When nothing is flagged, `finra` lists the three weeks closest to the bar. Those weeks are not signals. `closeness` is `z_block` as a percentage of its threshold, so 100 means the bar was met. Weekly CSVs include it for every week.

Every threshold can be overridden individually. Run `python whale_watch.py finra --help` or `python whale_watch.py prints --help` to see them.

## How it filters out noise

- **Relative to each stock's own history:** thresholds come from that ticker's own baseline, so one setting works for small and mega caps alike.
- **A ratio of the ticker's own dollars (`finra`):** block share compares block-venue dollars with total dark-pool dollars for the same ticker, so share price, stock splits and total volume mostly cancel out. It needs no market total, so the newest weeks aren't estimates.
- **Dollar value instead of share count:** stock splits don't distort volume. Trade size is a different story; see Caveats.
- **Outlier-resistant baseline:** a single extreme week can't shift what counts as normal.
- **Market-wide swings removed (`finra`):** each ticker is divided by total market dark-pool activity, so holidays, broad sell-offs and rebalancing weeks don't trigger flags. FINRA publishes that total about two weeks after Tier 1 tickers, so the newest weeks scale up the sum of all Tier 1 symbols by Tier 1's share of the last published week. The `mkt_basis` column shows `actual`, `estimated` or `none` for each week.
- **Persistence for heavy trading (`finra`, low):** it must last several weeks in a row. Block flags don't need this, because one big order can finish in a week.
- **Adaptive block cutoff (`prints`):** a trade counts as a block only if it is larger than all of these:
  - a dollar floor
  - a percentage of the day's dollar volume
  - the biggest normal on-exchange trades that day
- **Clean prints only (`prints`):**
  - regular hours only
  - skips average-price, derivatively priced, hedge-leg, late, special-settlement and after-hours reports
  - leaves official open and close records out of daily volume, because they repeat other trades
  - uses only normal on-exchange trades for the reference price and the block cutoff, so a late print can't skew either
- **Whole sessions (`prints`):** `--days` counts trading sessions, so holidays and a day that hasn't opened yet don't use one up.
- **Split orders re-joined (`prints`):** pieces at the same price, seconds apart, are counted as one order. Only pieces that are already large are combined, so small retail trades can't add up to a fake block.
- **Direction labels:** each flagged period gets "price up" if the price held or rose, and "price down" if it fell.

## Caveats

- **A block flag describes where trading happened.** Public data doesn't show who traded. `block_$M` counts all dollars on block venues, and those venues also carry smaller trades, so it isn't a total of confirmed $200K+ blocks.
- **Independent of volume isn't the same as meaningful.** Across 20 tickers, 8 of them held out of the design, `z_block` had a rank correlation of about 0.14 with total-volume surges and about 0.0–0.1 with price moves. Over the 104 weeks tested, no week flagged more than one ticker at `low`, which argues against venue-wide reporting effects.
- **The direction label is only the price move.** It says nothing about whether a block was a buy or a sell.
- **Not every big move is block activity.** A busy earnings week can have an ordinary block share and go unflagged, which is correct. Those weeks show up in `heavy_weeks` if they're unusual for the stock.
- **Heavy-trading weeks are not whale signals.** Over 153 weeks of ORCL checked against Yahoo volume, they had about twice the normal total volume, but the dark-pool share of that volume didn't change.
- **Unusual means unusual for that stock.** A stock that moves a lot all year builds a high baseline, so even big days can score as normal.
- **Average trade size follows the share price.** It only affects `heavy_weeks`, and switching it to shares made results worse in testing.
- **Splits still leave a small effect on block share.** NVDA and SMCI scored about 1.2 to 1.4 in the 8 weeks after their splits, below the `low` and `medium` bars but above the usual 0.
- **Block venues can change.** The list comes from FINRA's latest monthly report, about two months old, and is applied to the whole baseline.
- Thin stocks may have many weeks with no block-venue dollars. Those weeks aren't scored.
- Institutions split orders into small trades, so some of their activity is always missed.
- Buy/sell direction is estimated by comparing each block to the last on-exchange price. Treat it as a hint, not proof.
- FINRA weekly data runs about 2–4 weeks behind.
- Weeks marked `estimated` can shift slightly once FINRA publishes the real total. If Tier 1 data can't be fetched, those weeks stay unscored.
- Direction labels compare prices without adjusting for splits, so a split inside a flagged run can show a false "price down".
- This is a research tool, not investment advice.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

By default the tests use fixtures and make no network calls. `pytest -m live` runs the Oracle checks against the real FINRA API.
