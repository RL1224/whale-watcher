# whale-watch

A free scanner that flags when large players are unusually active in a stock or ETF.
It does not identify buyers. It looks for large trades and abnormal dark-pool activity.

## Modes

| Mode | Data source | Cost | Delay | Use |
|------|-------------|------|-------|-----|
| `finra` | FINRA weekly dark-pool (ATS) data | Free, no key | ~2–4 weeks | Long-term trend |
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
python whale_watch.py finra ORCL NVDA SPY
python whale_watch.py finra ORCL --sensitivity medium --weeks 104
python whale_watch.py prints ORCL --days 3
```

Results print to the terminal and are saved as CSVs in `whale_out/`.

## Sensitivity

`--sensitivity low | medium | high` (default `low`).

- **low** flags only rare, sustained, clearly abnormal periods.
- **medium** is balanced.
- **high** catches more but is noisier.

Every threshold can be overridden individually. Run `python whale_watch.py finra --help` or `python whale_watch.py prints --help` to see them.

## How it filters out noise

- **Relative to each stock's own history:** thresholds come from that ticker's own baseline, so one setting works for small and mega caps alike.
- **Dollar value instead of share count:** share price and stock splits don't distort the numbers.
- **Outlier-resistant baseline:** a single extreme week can't shift what counts as normal.
- **Market-wide swings removed (`finra`):** each ticker is divided by total market dark-pool activity, so holidays, broad sell-offs and rebalancing weeks don't trigger flags.
- **Persistence required (`finra`, low):** abnormal activity must last several weeks in a row.
- **Adaptive block cutoff (`prints`):** a trade counts as a block only if it is larger than all of these:
  - a dollar floor
  - a percentage of the day's dollar volume
  - the biggest normal on-exchange trades that day
- **Clean prints only (`prints`):**
  - regular hours only
  - skips average-price, derivatively priced, hedge-leg, out-of-sequence and after-hours reports
- **Split orders re-joined (`prints`):** pieces at the same price, seconds apart, are counted as one order. Only pieces that are already large are combined, so small retail trades can't add up to a fake block.
- **Direction labels:** each flagged period gets "accumulation?" if the price held or rose, and "distribution?" if it fell.

## Caveats

- Institutions split orders into small trades, so some of their activity is always missed.
- Buy/sell direction is estimated by comparing each block to the last on-exchange price. Treat it as a hint, not proof.
- FINRA weekly data runs about 2–4 weeks behind.
- This is a research tool, not investment advice.
