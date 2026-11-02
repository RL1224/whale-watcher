# whale-watch block signal: pre-registered tests

Written 2026-10-30, before any of these results were looked at. Code under test is
the uncommitted whale_watch.py. Thresholds are not changed after seeing results.

## Universe
Fresh tickers that played no part in the design: 60 large US names, none of the 20
used so far. Weeks scored after the 26-week baseline, through the latest FINRA week.

## Claim being tested
A high z_block means unusually large institutional activity in that ticker that week.

## Tests (each must clear its bar; two-sided permutation p < 0.05 unless stated)
R. Reproduction. A clean copy in a new virtualenv passes all fixture tests and all
   live tests, and reproduces ORCL 2026-10-05: $80.6M, 2.63%, z 3.69.
G. Ground truth. Weeks with a documented large insider or 10% holder sale from SEC
   Form 4 filings (at least $25M in the week) have higher z_block than the same
   ticker's other weeks. Effect must be positive.
P. Placebo venues. Repeat G with z scored on a same-sized set of ordinary dark
   pools. The real effect must beat the placebo: the real effect sits above the
   95th percentile of 200 random placebo sets.
F. Forward activity. In the 4 weeks after a z_block >= 3 week, total volume and
   absolute return are higher than the ticker's own unflagged weeks. Permutation
   within ticker. Effect must be positive.
D. Direction. After flagged weeks, next-4-week return differs in the labelled way:
   "accumulation?" above "distribution?". One-sided p < 0.05.

## Amendment, before any result was seen
EDGAR returned 403 because it requires a contact email, and none was sent. G and P
use OpenInsider instead, which republishes the same Form 4 filings. Sale code S only,
by trade date. If it can't be reached, G and P are reported as not run, not passed.

## Added 2026-10-30 at the owner's request, before any result was seen
B. Buy test. "If I bought when this fired, was it a good time?" Buy at the close of
   the first date the signal was public, never the signal week itself: FINRA data
   arrives about 3 weeks after the week starts, so entry is the close 3 weeks after
   week start. Hold 4, 13 and 26 weeks. Compare with the same ticker bought at every
   other week (within-ticker baseline) and with SPY over the same dates. Report win
   rate, median and mean return, and worst case, for z_block >= 3 and >= 2.
   "More or less accurate" means all of: median excess over SPY above 0 at 13 weeks,
   win rate above the ticker baseline by at least 5 points, permutation p < 0.05,
   and the result holds in both halves of the sample. Overlapping holds are
   thinned to one entry per ticker per holding period. Yahoo adjusted closes are
   used so splits and dividends count. Survivorship: today's large caps only, so
   absolute returns are flattered; only the comparison with baseline is meaningful.

## Reading the result
Passing R only shows the software reproduces. Passing G and P is the only evidence
that the flag relates to real large trades. Failing G or P means the README must
stop calling this a large-player signal. Failing F or D means no predictive claim.
All outcomes get reported, including failures. Tests run once on fresh tickers; a
fix made after a failure would need new tickers to be re-tested.
