# Free websites and apps for dark pool and block trade activity in US stocks

Research date: 2026-10-31. All pages were opened logged out, from a non-browser fetcher. No accounts were created and no personal information was entered.

Access labels used below:
- **Verified**: I opened the page or called the endpoint and saw the content or data.
- **Partial**: the page opened, but tables or charts did not render for my fetcher, so I saw labels or static text only.
- **Vendor claim**: the statement comes from the vendor and I could not test it.
- **Blocked**: the site refused my fetcher (HTTP 403/404, timeout or challenge), so anything said about it is second-hand.

## Which sites offer this?

### Takeaway
Only a handful of options work for free today, and none shows confirmed big-player buying or selling. The strongest verified choices are FINRA's raw daily and weekly data, ChartExchange's free account, and TradingView's FINRA short volume indicator for charting. Stockgrid, the name most old blog posts recommend, now redirects to AXLFI, where Dark Pools is a Pro feature with a limited free visit.

### Cited Findings

**Summary table** (each row is detailed in the next section)

| Site | Usable for free for this purpose? | Access status |
|---|---|---|
| FINRA daily short sale files | Yes, no account, any covered symbol | Verified |
| FINRA OTC Transparency (weekly ATS/non-ATS) | Yes, no account via API; website has an agreement page | Verified (API); Partial (website) |
| ChartExchange | Yes, free account; aggregates visible logged out | Partial |
| TradingView + FINRA indicator | Likely yes, free account | Partial |
| Equibles | Yes for the weekly table, logged out | Partial |
| Sensa (locosdewallstreet) | Yes per vendor: 4-hour-delayed prints | Vendor claim |
| InfoLib | Yes per vendor: no signup | Vendor claim |
| Unusual Whales | Possibly, free account; dark pool scope conflicts between its own pages | Vendor claim, conflicting |
| Quiver Quantitative | Partly: market-wide off-exchange view seen; per-ticker view not confirmed | Partial |
| DarkPoolHeatmap (Moby Tick) | Sector heatmap only; full report gated | Partial |
| Stockgrid / AXLFI | No longer a plain free tool: Pro page with a limited free visit | Verified from site code, not rendered |
| Fintel | Unknown, some public short volume pages appear to exist | Blocked |
| Barchart | Unconfirmed | Blocked |
| MarketChameleon | Not for this purpose on the pages I saw | Partial |
| Finviz | No dark pool or block data on the quote page | Verified |
| Nasdaq | No dark pool tool found | Blocked |
| Tradytics | Free tier exists; dark pool on it unconfirmed | Partial |
| Cheddar Flow | Probably no free tier | Blocked |
| BlackBoxStocks | No free tier listed | Verified |
| FlowAlgo | No free tier; new sign-ups paused | Verified |

**Stockgrid status change**
- `stockgrid.io/`, `/darkpools/MSFT` and the old data endpoint all return HTTP 301 to `axlfi.com` — tested 2026-10-31 at [stockgrid.io](https://www.stockgrid.io/).
- AXLFI describes the page as "Off-exchange short volume from FINRA data: daily dark pool flow, the largest buyers and sellers, and positioning by ticker and sector" — [AXLFI Dark Pools](https://axlfi.com/darkpools).
- The site's own JavaScript marks the Dark Pools route as Pro, and its gate text includes "This page is for Pro users." and "Your free visit has ended." The Dark Pools page detail reads "Pro opens any stock's off-exchange short volume and net position on its price, the daily leaderboard and positioning by sector." — [AXLFI Dark Pools](https://axlfi.com/darkpools).

**Other free-tier alternatives found**
- Equibles shows MSFT weekly ATS volume, non-ATS OTC volume and off-exchange share, sourced from FINRA — [Equibles MSFT](https://equibles.com/stocks/msft/off-exchange).
- Sensa offers dark pool prints on a 4-hour delay for free accounts — [Sensa](https://sensamarket.locosdewallstreet.com/dark-pool).
- InfoLib says it charts dark volume against price, lists raw prints, and needs no signup for core functions. It does not state its data source or delay — [InfoLib](https://infolib.org/market-dashboard/dark-pools-data).
- Capitol Whale marks its dark pool feed as Pro, so it is not free — [Capitol Whale](https://capitolwhale.com/dark-pool-prints).
- Options Trading Toolbox shows a daily limit and an upgrade prompt, and states no data source or free scope — [Options Trading Toolbox](https://optionstradingtoolbox.com/dark-pool-tracker).
- Meridian describes a FINRA off-exchange short volume dashboard and free account. This comes from Meridian's own marketing article — [Meridian](https://meridianfin.io/knowledge/free-dark-pool-data).

### Inferences
- Treat any pre-2026 list that calls Stockgrid "free" as out of date until someone tests AXLFI in a real browser.
- For a named stock, the best free stack is one site for aggregates (ChartExchange or FINRA), one for charting (TradingView), and one for recent prints (ChartExchange prior-day, or Sensa if its claim holds).
- Paid-only products (FlowAlgo, BlackBoxStocks, probably Cheddar Flow) can be dropped from a free shortlist.

### Gaps
- I could not confirm how long AXLFI's "free visit" lasts or what triggers it, because I could not render the logged-in-state logic. Its pricing did not appear in the strings I inspected.
- I found no public announcement explaining the Stockgrid to AXLFI move, so the link between them rests on the redirect alone.
- A search summary named a "Gatech Dark Pool Monitor" (`dpm.gatech.edu`) as free, attributed to a vendor page I could not pin down. That host failed DNS lookup on 2026-10-31, so it is excluded as non-functional.

## What is free, what is locked, and is a signup or card needed?

### Takeaway
Free truly means no account only at FINRA and a few logged-out aggregate pages. Print-level data usually needs a free account, which generally needs no card, and the most useful ticker-level print history is the first thing paid tiers lock.

### Cited Findings

**FINRA (free, no signup)**
- Daily files: I downloaded `CNMSshvol20261030.txt` with no account or key on 2026-10-31 — [FINRA file](https://cdn.finra.org/equity/regsho/daily/CNMSshvol20261030.txt).
- Weekly OTC data: FINRA's public API returned MSFT rows with no key or login on 2026-10-31 — [FINRA API](https://api.finra.org/data/group/otcMarket/name/weeklySummary).
- FINRA's OTC Data section sits behind an agreement page — [FINRA OTC Transparency](https://www.finra.org/filing-reporting/otc-transparency).
- FINRA announced free public access to weekly ATS data in 2014 — [FINRA release](https://finra.org/media-center/news-releases/2014/finra-makes-dark-pool-data-available-free-investing-public).

**ChartExchange (free plan $0, no card, signup required)**
- Free includes charts, screener, watchlists and 2 alerts delayed 15 minutes, with 12 months of dataset history and 5 years of partial financials — [ChartExchange pricing](https://chartexchange.com/pricing/).
- Free limits: Dark Pool Prints previous day only, Dark Pool Levels 3 market days, Trade Flow 15-minute delayed for up to 3 symbols — [ChartExchange pricing](https://chartexchange.com/pricing/).
- Locked on free: daily short interest, market-wide alerts, screener CSV export, real-time option flow — [ChartExchange pricing](https://chartexchange.com/pricing/).
- Investor plan at $20/month adds complete dark pool history and real-time trade flow, with a 14-day trial. The page does not say whether a trial needs a card — [ChartExchange pricing](https://chartexchange.com/pricing/).
- Logged out, the MSFT dark pool page shows the off-exchange summary, while its Levels and Prints tables appeared empty in my capture. It says full access covers "all dates, custom aggregation, live updates, and CSV export" — [ChartExchange dark pool](https://chartexchange.com/symbol/nasdaq-msft/dark-pool/).

**TradingView (free Basic plan, signup, no card)**
- Basic gives 1 chart per tab, 2 indicators per chart and 5K historical bars, with "No credit card needed" — [TradingView pricing](https://www.tradingview.com/pricing/).
- TradingView's own FINRA indicator is published as an open-source script. The page does not explicitly say it is free on Basic — [TradingView indicator](https://www.tradingview.com/script/4KIgeLGo-FINRA-Daily-Short-Sale-Volume/).

**Unusual Whales (free plan $0, account required, no card)**
- Free plan: full dashboard, screeners and charts delayed; options flow delayed 2 trading days; news 15 minutes; alerts 30 minutes — [UW pricing](https://unusualwhales.com/pricing).
- Paid starts at $50/month, or $34/month annually for Retail Basic. The pricing page does not say whether free users get dark pool data — [UW pricing](https://unusualwhales.com/pricing).
- Its free-trial page says "No credit card required", and its free list does not name dark pool data — [UW free page](https://unusualwhales.com/lp/unusual-whales-free-trial).
- Its June 2026 guide says the free tier shows individual prints on a 15-minute delay. This is a vendor claim about its own product — [UW guide](https://unusualwhales.com/guides/best-dark-pool-tracking-tools).

**Quiver Quantitative**
- `/darkpool/` has a ticker search and a "Yesterday's off-exchange activity" section, with a "% short volume (off-exchange)" heatmap scale in the page source. It invites users to "Sign Up for Free" — [Quiver](https://www.quiverquant.com/darkpool/).
- Its Premium navigation lists Strategies, Alerts, Screener, backtesters, Videos and Export Data, not off-exchange data — [Quiver pricing](https://www.quiverquant.com/pricing/).

**Tradytics (free Basic $0, no card)**
- Free includes market overview, AI news, "Delayed analytics", simple flow data and a daily scanner. Pro is $69/month with a 15-day $15 trial and no refunds. A "Darkpools" navigation link exists, with no plan stated — [Tradytics](https://tradytics.com/).

**Paid-only products**
- BlackBoxStocks lists $59 to $149/month, shows no free tier, and states "All sales are final" — [BlackBoxStocks pricing](https://blackboxstocks.com/pricing/).
- FlowAlgo says "New sign-ups are paused", shows a $37 two-week trial and $149/month, and mentions no free tier — [FlowAlgo](https://www.flowalgo.com/).
- Cheddar Flow blocked my fetcher. Third-party sources mostly say no free tier and that dark pool sits on a higher plan: [NexusFi listing](https://nexusfi.com/d/platforms/cheddar-flow/); [Pure Power Picks](https://purepowerpicks.com/cheddar-flow-review/). A search summary cited a Pineify comparison calling its free tier "rich", but I could not locate that wording: [Pineify's free flow page](https://pineify.app/options-flow-free) does not mention Cheddar Flow. Treat that claim as unconfirmed.

**Sites without a usable free feature on pages I saw**
- Finviz's MSFT page shows insider trades and short interest (Short Float 0.90%, Short Interest 65.67M) but no dark pool, block or daily short volume. Elite starts at $24.96/month — [Finviz MSFT](https://finviz.com/quote.ashx?t=MSFT).
- MarketChameleon's MSFT pages showed no short sale, dark pool or stock block data, only an "Option Block Trades" menu item and "For Premium Users" sections — [MarketChameleon MSFT](https://marketchameleon.com/Overview/MSFT/Stock-Block-Trades/).
- A Market Chameleon instructional page surfaced by search suggests it tracks large trades in dark pools and lit exchanges, but I found no free scope stated — [Market Chameleon instructional page](https://marketchameleon.com/Instructional-Stock-and-Options-Trading-Videos/471/How-to-Spot-Large-Volume-Bursts-in-Stocks-|-Track-Institutional-Orders-Like-a-Pro).
- DarkPoolHeatmap gates its full weekly report and lists no price — [DarkPoolHeatmap](https://darkpoolheatmap.com/).

### Inferences
- A free ChartExchange account looks like the only verified way, from a primary pricing page, to see ticker-level prints at no cost. Its limit means a rolling view of yesterday's prints, not a searchable history.
- For Unusual Whales, the pricing page is the more cautious source. Treat the 15-minute print claim as unconfirmed until tested in a free account by the user.

### Gaps
- **Fintel:** every page I tried returned 403 or 404, including pricing. I did not try to get around the block. A [Fintel public short volume page](https://fintel.io/ssv/us/az) appeared in search, listing daily updates at close. Tiers named Bronze, Silver and Gold, with entry around $20/month on a yearly basis, come from [aggregators](https://www.holdingsintel.com/vs/fintel), which may be stale. [Tapeboard](https://tapeboard.com/compare/fintel-alternative), a competitor, claims most short-side data is paywalled. Free scope is unconfirmed.
- **Barchart:** pages returned empty or HTTP 202. A search summary attributed to a Meridian article pointed to `barchart.com/stocks/dark-pool-prints` as a limited free page, but neither Meridian page I opened ([free data](https://meridianfin.io/knowledge/free-dark-pool-data), [best free tools](https://meridianfin.io/knowledge/best-free-dark-pool-data-2026)) mentions Barchart, and a [third-party comparison](https://tradingtoolshub.com/compare/barchart-vs-unusual-whales/) says Barchart does not emphasize dark pool tracking. [A Barchart article](https://www.barchart.com/story/news/2571723/a-short-squeeze-could-be-brewing-in-la-z-boy-stock) quotes an off-exchange short volume ratio, so the data may exist somewhere on the site. Existence of a free tool is unconfirmed.
- **Nasdaq:** the MSFT short interest page timed out, and the old Nasdaq Trader short sale URL returned 404. A [Nasdaq specification](https://m.nasdaqtrader.com/content/technicalsupport/specifications/dataproducts/ShortSaleFileSpecifications.pdf) describes a daily short sale file but looks legacy. No Nasdaq dark pool tool was confirmed.
- **MarketChameleon pricing** returned 404. **Quiver's** per-ticker view and pricing tiers could not be confirmed.
- **Sensa and InfoLib:** no independent check of operator or data vendor. Sensa's account requirement is not clearly stated.

## What are the data delay, history length and ticker coverage on the free tier?

### Takeaway
FINRA daily data arrives the same evening but covers off-exchange trades only, while FINRA's weekly venue data for MSFT arrives about 17 days after the week ends. Free print data runs from a few hours to a day old, and every print feed has one extra hidden delay: dark trades can be reported late.

### Cited Findings

| Source | Delay | History | Coverage |
|---|---|---|---|
| FINRA daily file | Posted by 6:00 pm ET same day — [FINRA](https://www.finra.org/finra-data/browse-catalog/short-sale-volume-data/daily-short-sale-volume-files) | Consolidated files from 2018-08-01 (tested 200 OK) — [FINRA](https://www.finra.org/finra-data/browse-catalog/short-sale-volume-data/daily-short-sale-volume-files); monthly archives back to 2009 — [FINRA 2009](https://www.finra.org/filing-reporting/trf/trf-regulation-sho-2009) | All symbols in the file |
| FINRA weekly Tier 1 | Week of 2026-10-05 first published 2026-10-26; week of 2026-10-12 not yet available on 2026-10-31 — [FINRA API](https://api.finra.org/data/group/otcMarket/name/weeklySummary) | Not confirmed | Tier 1, other NMS, OTC |
| FINRA weekly Tier 2 | About two weeks behind Tier 1: an August 2022 notice lists Tier 1 week of July 11 and Tier 2 week of June 27 together — [FINRA notice](https://finra.org/filing-reporting/otc-transparency-data) | Not confirmed | As above |
| FINRA block data | Monthly — [FINRA notice](https://www.finra.org/rules-guidance/rulebooks/january-2023-otc-transparency-block-data-publication-delay) | Not confirmed | Fields seen are per ATS, not per stock — [FINRA metadata](https://api.finra.org/metadata/group/otcMarket/name/blocksSummary) |
| ChartExchange free | Prints: previous day. Levels: 3 market days — [pricing](https://chartexchange.com/pricing/) | 12 months of datasets — [pricing](https://chartexchange.com/pricing/) | Any listed symbol, implied by URL structure |
| TradingView | Daily data — [indicator](https://www.tradingview.com/script/4KIgeLGo-FINRA-Daily-Short-Sale-Volume/); a community script notes a one-day lag on the chart — [FINRA scripts](https://www.tradingview.com/scripts/finra/) | 5K bars on Basic — [pricing](https://www.tradingview.com/pricing/) | NASDAQ, NYSE, NYSE ARCA — [indicator](https://www.tradingview.com/script/4KIgeLGo-FINRA-Daily-Short-Sale-Volume/) |
| Equibles | Latest week shown was 2026-09-21, older than FINRA's latest — [Equibles](https://equibles.com/stocks/msft/off-exchange) | 47 weeks listed; range buttons up to 5Y and All | Ticker pages |
| Sensa free | 4 hours; past days fully visible — [Sensa](https://sensamarket.locosdewallstreet.com/dark-pool) | Not stated | Not stated |
| Unusual Whales free | 15 to 20 minutes per FAQ — [UW](https://unusualwhales.com/lp/unusual-whales-free-trial); options flow 2 trading days — [pricing](https://unusualwhales.com/pricing) | Not stated | Not stated |
| DarkPoolHeatmap | "real time" with no latency stated — [site](https://darkpoolheatmap.com/) | Claims 5+ years | Sectors and popular tickers seen |

- Publication for all four MSFT Tier 1 weeks I sampled was the Monday 21 days after the week start: 09-14 to 10-05, 09-21 to 10-12, 09-28 to 10-19, 10-05 to 10-26 — [FINRA API](https://api.finra.org/data/group/otcMarket/name/weeklySummary).
- FlowAlgo warns that equity block and print data can lag up to 20 minutes, and dark pool transactions may be reported hours later, the next day or the following Monday — [FlowAlgo](https://www.flowalgo.com/).
- ChartExchange's logged-out exchange volume history showed 25 trading days per page across "Page 1 / 11" — [ChartExchange](https://chartexchange.com/symbol/nasdaq-msft/exchange-volume/).

### Inferences
- "Page 1 / 11" at 25 rows implies roughly 275 trading days, which fits the 12-month free history claim.
- Weekly FINRA data cannot show recent activity for MSFT: on 2026-10-31 the newest available week ended 2026-10-09. It suits look-back analysis, not monitoring.

### Gaps
- FINRA's Rule 6110 text was not retrieved, so the Tier 1 and Tier 2 schedules are shown from observed dates, not rule wording. A search summary quoted a FINRA notice saying "four-week delay" for other NMS and OTC securities, but I could not locate that notice. The OTC Transparency FAQ URL I tried returned 404.
- I could not confirm the earliest week in the free weekly API, or whether a per-stock monthly block dataset exists. The block metadata I read was truncated.

## Does it show direction, or only volume, and how is direction derived?

### Takeaway
No free source reports real direction. Regulators publish volume and a "short" flag; everything labeled buy or sell is a website's inference, and the common methods measure different things.

### Cited Findings

**Official data has no direction**
- FINRA's daily file has date, symbol, short volume, short exempt volume, total volume and market only — [FINRA file](https://cdn.finra.org/equity/regsho/daily/CNMSshvol20261030.txt).
- FINRA's weekly records give shares, notional and trade counts, with no buy or sell field in the rows I read — [FINRA API](https://api.finra.org/data/group/otcMarket/name/weeklySummary).

**Method 1: short volume ratio as a buy proxy (AXLFI/Stockgrid, DIX style)**
- AXLFI's text: "Market makers sell short to fill buy orders, so a short share above half reads as buying and below half as selling; the net position sums that net short volume in dollars over 20 sessions" — [AXLFI](https://axlfi.com/darkpools).
- The same logic appears in SqueezeMetrics' 2018 paper, which argues "short volume is actually representative of investor buying volume" and treats all TRF data, internalizers included, as "dark pool" data — [SqueezeMetrics](https://squeezemetrics.com/monitor/download/pdf/short_is_long.pdf).
- Quiver also displays a "% short volume (off-exchange)" scale and a DPI label — [Quiver](https://www.quiverquant.com/darkpool/).

**Method 2: quote-based side on each print**
- Sensa tags prints at or above the ask as Buy, at or below the bid as Sell, and inside the spread as Neutral — [Sensa](https://sensamarket.locosdewallstreet.com/dark-pool).
- ChartExchange's prints table has a Side column; its method is not stated on the page — [ChartExchange](https://chartexchange.com/symbol/nasdaq-msft/dark-pool/). Its trade-condition doc shows condition codes per trade, including average price and contingent trades — [ChartExchange docs](https://chartexchange.com/docs/stock-trade-conditions/).
- BlackBoxStocks has no stated buy or sell label, only AA (above ask) and BB (below bid) codes — [BlackBoxStocks docs](https://docs.blackboxstocks.com/en/stocks-platform/dark-pool-prints-block-trades/).

**Method 3: no direction, activity or price levels only**
- DarkPoolHeatmap states individual prints "don't tell you direction" and grades activity against average volume — [DarkPoolHeatmap](https://darkpoolheatmap.com/).
- ChartExchange's Dark Pool Levels table has columns Level, Trades, Volume and Premium, so it groups activity by price with no side — [ChartExchange](https://chartexchange.com/symbol/nasdaq-msft/dark-pool/).
- FINRA itself notes short volume is distinct from short interest. ChartExchange repeats that short interest is "the standing position" — [ChartExchange short volume](https://chartexchange.com/symbol/nasdaq-msft/short-volume/).

**Worked MSFT check from FINRA's own data** (computed in code; shares from [FINRA daily files](https://cdn.finra.org/equity/regsho/daily/CNMSshvol20261030.txt) and the [weekly API](https://api.finra.org/data/group/otcMarket/name/weeklySummary))

| Trade date | Short volume | Total volume | Short share |
|---|---:|---:|---:|
| 2026-10-26 | 2,312,483 | 6,364,616 | 36.3% |
| 2026-10-27 | 2,161,597 | 6,081,729 | 35.5% |
| 2026-10-28 | 2,584,128 | 8,253,901 | 31.3% |
| 2026-10-29 | 6,681,747 | 16,148,122 | 41.4% |
| 2026-10-30 | 3,670,922 | 10,649,951 | 34.5% |

| Week start | ATS shares | Non-ATS OTC shares | ATS share of off-exchange | Avg ATS trade | Avg non-ATS trade |
|---|---:|---:|---:|---:|---:|
| 2026-09-14 | 17,354,832 | 31,969,729 | 35.2% | 45.5 sh | 38.8 sh |
| 2026-09-21 | 23,704,105 | 36,898,435 | 39.1% | 49.2 sh | 37.0 sh |
| 2026-09-28 | 18,029,661 | 27,857,972 | 39.3% | 42.6 sh | 31.6 sh |
| 2026-10-05 | 19,953,792 | 28,548,417 | 41.1% | 44.3 sh | 30.7 sh |

**Site figures differ from the raw file for the same day**
- For 2026-10-30, FINRA's consolidated file gives short volume 3,670,922 of 10,649,951 (34.5%) — [FINRA file](https://cdn.finra.org/equity/regsho/daily/CNMSshvol20261030.txt).
- ChartExchange shows 4,816,443 and 35.40% for the same date, footnoting FINRA and Nasdaq data — [ChartExchange](https://chartexchange.com/symbol/nasdaq-msft/short-volume/). It also shows 26.85% "Short Vol % (off-exch)" on a related page — [ChartExchange](https://chartexchange.com/symbol/nasdaq-msft/dark-pool/).

### Inferences
- All five MSFT days had a short share below 50%. Under AXLFI's rule every one reads as "selling", including 2026-10-29, when total volume roughly doubled. ChartExchange's 30-day average for MSFT is also below 50%, at 38.74%, so that label may mostly reflect how this stock normally prints.
- Average dark pool trades near 45 shares show that most MSFT ATS volume is ordinary small-sized flow, not visible whale blocks. "High dark pool volume" and "big players active" are different claims. Institutions can slice orders, so this neither proves nor rules out large parents behind the small trades.
- ATS venues were only 35% to 41% of FINRA-reported off-exchange shares in these weeks. Most so-called dark pool volume on free sites is therefore dealer or wholesaler volume, not dark pools.
- Quote-based labels are weak for dark prints: SqueezeMetrics notes dark pool trades usually execute between the bid and ask, often at the midpoint, which would land in "Neutral".

### Gaps
- I found no free site that explicitly says it uses a tick test.
- ChartExchange's Side method, and Unusual Whales' direction handling on free accounts, are unconfirmed.
- I could not reconcile ChartExchange's 4.8M and 26.85% figures to FINRA's file, and the 2026-10-29 volume jump has an unknown cause. I do not infer one.

## Does it chart activity over a date range against price?

### Takeaway
Yes, but with limits. TradingView is the most practical free way to put FINRA short volume under a price chart, ChartExchange offers a price toggle on its exchange volume chart, and AXLFI's chart is the closest match to the goal but is Pro-gated. No free option I verified charts individual block prints over weeks.

### Cited Findings
- TradingView loads FINRA data by symbol, for example `FINRA:AAPL_SHORT_VOLUME`, directly on a price chart — [TradingView indicator](https://www.tradingview.com/script/4KIgeLGo-FINRA-Daily-Short-Sale-Volume/).
- Its caveat: short sale volume "is not consolidated with exchange data" and excludes activity that is not publicly disseminated — [TradingView indicator](https://www.tradingview.com/script/4KIgeLGo-FINRA-Daily-Short-Sale-Volume/).
- Community scripts on the same platform plot short volume as a percentage of total — [TradingView FINRA scripts](https://www.tradingview.com/scripts/finra/).
- ChartExchange's exchange volume page has percent and volume views over 1 day, 1 week or 1 month, with a "Price" option, plus a daily history table with Export. The chart showed "Loading…" in my capture — [ChartExchange](https://chartexchange.com/symbol/nasdaq-msft/exchange-volume/).
- ChartExchange's short volume page has venue charts, with no price overlay visible in my capture — [ChartExchange](https://chartexchange.com/symbol/nasdaq-msft/short-volume/).
- AXLFI has a "Price, Short Volume & Net Position" section. Each bar is the session's off-exchange volume, and a lower panel sums 20 sessions of net short dollars — [AXLFI](https://axlfi.com/darkpools).
- InfoLib claims dark volume charted against price for a chosen date range — [InfoLib](https://infolib.org/market-dashboard/dark-pools-data).
- Equibles offers 1M to All range buttons for weekly volume. Only the table appeared in my capture — [Equibles](https://equibles.com/stocks/msft/off-exchange).
- A developer can chart FINRA data directly. A public tutorial does this in Python — [DEV Community tutorial](https://dev.to/fishinabowl95/track-dark-pool-volume-for-any-stock-with-free-finra-data-python-45oe). I confirmed the daily files and weekly API respond for MSFT.

### Inferences
- To see when activity was elevated in MSFT over days or weeks, the most defensible free approach is off-exchange volume relative to the stock's own average, shown with price. Direction claims can be left out.
- For this project, FINRA's files could feed a self-built chart with full control of the definitions. That avoids dependence on sites that can change or gate access, as Stockgrid did.

### Gaps
- No chart rendered in my fetcher for any JavaScript site, so all overlays except TradingView's data path are described from page text, and none was seen drawn.
- Whether TradingView's Basic plan permits this indicator without limits was not explicitly stated.

## Is there independent evidence the signal works, or that it is misleading?

### Takeaway
The evidence does not support reading a single day's dark pool or short volume as big-player intent. FINRA warns the data looks inflated, the popular "short means buying" claim rests on a vendor's same-day correlation, and peer-reviewed work on sustained short volume found the opposite sign at longer horizons.

### Cited Findings

**FINRA's own cautions (primary)**
- The Daily File "does not—and is not intended to—equate to" short interest, and the two are related but not necessarily correlated — [FINRA notice](https://www.finra.org/industry/information-notice-051019).
- Facilitated customer long sales appear as short sales "without any indication that it is associated with an offsetting purchase", which "may result in the appearance of a higher concentration of short sale to total volume" — [FINRA notice](https://www.finra.org/industry/information-notice-051019).
- FINRA's example: a FINRA-only figure implied 20% short volume, but about 10.7% once exchange data was combined — [FINRA notice](https://www.finra.org/industry/information-notice-051019).
- FINRA says some sites wrongly label the daily file "short interest", that free site figures are often proprietary calculations, and that investors should ask how they are derived — [FINRA investor page](https://www.finra.org/investors/insights/short-interest).
- Example of the mislabel: Quiver's off-exchange page metadata says "Track off-exchange short interest" — [Quiver](https://www.quiverquant.com/darkpool/).

**The claim that short volume means buying (vendor, not peer reviewed)**
- SqueezeMetrics tested 11,254 securities and 12.74M security-days from 2010. Mean intraday return was -0.0593% on days with 0–49% dark pool short volume and +0.1184% on days with 50–100% — [SqueezeMetrics](https://squeezemetrics.com/monitor/download/pdf/short_is_long.pdf).
- The paper calls speculative short volume "tiny", without measuring it in the sections I read — [SqueezeMetrics](https://squeezemetrics.com/monitor/download/pdf/short_is_long.pdf).

**Peer-reviewed research**
- Wang, Yan and Zheng (Journal of Financial Economics, 2020): shorting flows predicted *negative* returns in 2010–2015, with predictability lasting a year. "Abnormal short-term shorting flows do not predict future returns or anticipate bad news", and long-term flows are the informative ones. The study uses FINRA's daily stock-level short volume — [Wang, Yan and Zheng](https://www.lehigh.edu/~xuy219/research/Short_Final_Version.pdf).
- Boulton and Braga-Alves (Managerial Finance, 2020): dark pool share of volume correlates positively with short interest, and heavily shorted stocks with higher dark pool volume have lower later returns — [Boulton and Braga-Alves](https://emerald.com/insight/content/doi/10.1108/MF-07-2019-0382/full/html).
- Zhu (Review of Financial Studies, 2014, a model): informed traders tend toward exchanges, and the dark pool acts like a screening device that siphons off uninformed traders — [Zhu](https://www.mit.edu/~zhuh/Zhu_darkpool_RFS.pdf). This is a model rather than a measurement — [MIT News](https://news.mit.edu/2014/how-dark-pools-can-help-public-stock-markets-0203).
- Ye's working paper reaches the opposite theoretical result and says empirical findings are mixed — [Ye](https://arxiv.org/pdf/1612.08486).

**Trade signing error (adjacent evidence)**
- Barber, Huang, Jorion, Odean and Schwarz (Journal of Finance, 2024) tested the BJZZ quote-based method on 85,000 real retail trades. It signed about 72% correctly, from 93% at one-cent spreads to 52% at ten cents or more. These numbers come from a secondary summary — [Alpha Architect](https://alphaarchitect.com/subpenny-price-movements/); paper at [SSRN](https://papers.ssrn.com/abstract=4202874). Sources disagree on which paper reports some related figures, so check the original before quoting — [arXiv](https://arxiv.org/html/2403.17095v1).

**Market structure**
- Off-exchange is not the same as dark pools. The SEC estimated ATSs at about 12% of NMS share volume in a 2012 sample, which is old — [SEC](https://www.sec.gov/files/alternative-trading-systems-03-2014.pdf). Nasdaq put off-exchange at 47% of shares in January 2021, with wholesalers driving most 2020 growth — [Nasdaq](https://www.nasdaq.com/articles/a-deep-dive-into-dark-trades-2021-04-29).
- ChartExchange's own footnote says off-exchange "includes dark pool trades and trades that update volume from the CTA" — [ChartExchange](https://chartexchange.com/symbol/nasdaq-msft/exchange-volume/).

**Critiques from interested parties, weaker evidence**
- Keubiko, a pseudonymous independent writer, compares almost 140M of Tesla short volume in a two-week span with a roughly 1.5M short interest rise — [Keubiko](https://keubiko.substack.com/p/misunderstood-and-misused-daily-short).
- A commenter there, employed by Equibles, reports a weak +0.229 correlation between short-ratio changes and short interest changes across 660,000 windows. This is unverified and from a vendor — [Keubiko comments](https://keubiko.substack.com/p/misunderstood-and-misused-daily-short/comments).
- OTC Markets argues market makers inflate daily short volumes in stocks with little directional shorting — [OTC Markets](https://blog.otcmarkets.com/2023/05/08/what-investors-should-know-about-finra-daily-short-sale-volume-data/). ORTEX makes a similar case — [ORTEX](https://public.ortex.com/why-daily-short-volumes-are-often-misinterpreted/). Both have commercial interests.

**Vendor accuracy claims that should not be relied on**
- DarkPoolHeatmap cites a "91% accuracy rate on trade callouts" with no substantiation — [DarkPoolHeatmap](https://darkpoolheatmap.com/).

### Inferences
- Short volume above 50% cannot safely be called bullish or bearish. SqueezeMetrics reads it as buying on the same day, while Wang et al. link sustained short flows to weaker returns over months. The horizons differ, so both can be partly true, but neither supports a single-day "whale buying" read.
- SqueezeMetrics' result is contemporaneous: same-day returns versus a ratio published after that day's close. It does not show the ratio forecasts anything.
- Dark pool research is about market structure, not the print-watching signals retail sites sell. I found no study validating the retail use of dark pool "levels".

### Gaps
- I found no independent, peer-reviewed test of AXLFI's net position, Quiver's DPI, or Dark Pool Levels as trading signals.
- Comerton-Forde and Putniņš (2015) and Peretti and Tapiero (2014) are cited by [Ye](https://arxiv.org/pdf/1612.08486), but I did not read them.
- I found no reliable Reddit reports. Searches returned nothing usable, so user experience is effectively untested here. The only review I saw was a [Trustpilot comment on Fintel](https://nl-be.trustpilot.com/review/fintel.io), which is anecdotal.
- An HKUST thesis snippet on short volume ratios could not be opened, so it is excluded.
