# Free Charting Tools and Indicators That Mark Accumulation Periods (US Stocks)

Research date: 2026-10-31. Pricing and plan facts come from pages read on that date unless marked otherwise. No accounts were created, so nothing was checked inside a logged-in platform. Some items come from search-result excerpts rather than a full page read. Those are labelled. This is not a buy or sell recommendation.

## Which free charts offer this, and is a paid plan needed?

### Takeaway
No platform I checked documents a built-in feature that shades an accumulation period on the price chart. The closest free match is TradingView Basic with a community script, limited to 2 indicators per chart. thinkorswim is the strongest documented free option with built-in tools, but it needs a Schwab account. Its docs confirm Volume Profile and accumulation/distribution studies, but not shaded zones.

### Cited Findings

Summary table (details and sources are in the bullets below):

| Platform | Cost and account | Accumulation-related tools confirmed | Shades a period on the chart? | Main limit |
|---|---|---|---|---|
| TradingView Basic | Free plan | Community scripts; built-in Volume Profile appears paid-only | Yes, through community scripts | 2 indicators per chart; 5K bars; Cboe-only default feed |
| StockCharts free | Free tier | Volume-by-Price overlay exists; free-tier access not stated | Not found | 3 indicators, 3 overlays |
| Finviz free | Free tier | None named | Not found | Charting suite is "Not Included" on free |
| Yahoo Finance | Free tier plus paid plans | Advanced Chart; volume indicators not confirmed | Not found | Technical event overlays need a paid plan |
| thinkorswim | No charge; Schwab account needed | VolumeProfile, AccumulationDistribution and AccDist studies | Not found | Account needed; Guest Pass for non-clients |
| Webull | Desktop described as free | 50 to 60+ indicators, names unconfirmed | Not found | Orderflow Chart looks like a paid add-on |
| Fidelity Trader+ | Free; offered through brokerage accounts | 100+ indicators, only 3 named | Not found | Requires a Fidelity relationship |

**TradingView**
- The Basic (free) plan shows 2 indicators per chart, 5K historical bars and 3 active price alerts. No technical alerts are listed for Basic. — [TradingView pricing](https://www.tradingview.com/pricing/)
- Volume Profile and volume footprint appear in the paid plan feature lists, starting at Essential. The page extraction did not map checkmarks cleanly to columns, so Basic's lack of access is likely but not fully confirmed. — [TradingView pricing](https://www.tradingview.com/pricing/)
- Community Volume Profile scripts in Pine Script exist as a workaround. — [TradingView script listing](https://www.tradingview.com/scripts/search/volume%20profile/) (listing seen in search; individual scripts not opened)
- Open-source scripts show their full code to anyone and are free to use. Protected scripts can be used but their code is hidden. Invite-only scripts can be used only by people the author invites, and public invite-only scripts can charge money. — [Pine Script publishing docs](https://www.tradingview.com/pine-script-docs/writing/publishing/)
- By default, TradingView shows real-time US stock data from Cboe. TradingView says Cboe handles over 25% of US stock trading, and that its data can differ because volume is lower than on primary exchanges. Direct NYSE, Nasdaq and ARCA data is a paid add-on. — [TradingView support](https://in.tradingview.com/support/solutions/43000473924) (read through a search excerpt)

**StockCharts**
- The free tier allows 3 indicators and 3 overlays per chart, versus 25 each on paid plans. It also allows 1 ChartList, 1 saved multi-chart layout, 1 scan, 1 screener, 2 price alerts and a 900px SharpChart width. Historical data goes back to 1980. — [StockCharts pricing](https://stockcharts.com/pricing/)
- The free data plan is described as BATS real-time data for the US. The same page also says all data is delayed 15 minutes "unless otherwise indicated," so the two statements need reading together. Paid plans are $19.95, $29.95 and $49.95 per month. Official real-time data is a further $9.95 per month. — [StockCharts pricing](https://stockcharts.com/pricing/)
- Volume-by-Price is a SharpCharts overlay, but the pages read do not state whether free users get it. — [StockCharts ChartSchool](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/volume-by-price)

**Finviz**
- The Elite comparison lists the charting suite as "Not Included" on free. Pattern drawing, indicators and intraday charts are Elite features. Free quotes are delayed 1 minute. — [Finviz Elite](https://finviz.com/elite)
- The page names no accumulation/distribution, OBV, CMF or volume profile tool on either plan. — [Finviz Elite](https://finviz.com/elite)

**Yahoo Finance**
- Yahoo's web help describes adding overlays such as Bollinger Bands and moving averages, and oscillators such as MACD and Stochastics, through Advanced Chart. — [Yahoo help](https://help.yahoo.com/kb/SLN8326.html) (search excerpt)
- Technical analysis and corporate event indicators are added by upgrading to "select subscription plans." The named items are moving-average, momentum, Bollinger, KST, RSI and CCI events, plus Trading Central patterns such as Rounded Bottom. No accumulation event is named. — [Yahoo help](https://help.yahoo.com/kb/SLN29177.html)
- AAII describes the free Advanced Chart as having 19 chart types, over 120 technical indicators and 30 drawing tools. — [AAII](https://www.aaii.com/journal/article/503989-analyze-charts-quicker-with-these-tech-tools) (search excerpt; the article date was not confirmed)
- Plans are listed as Bronze $7.95, Silver $19.95 and Gold $39.95 per month, with Gold showing "50+ technical chart patterns." The extraction did not show which features belong to which tier. — [Yahoo plans](https://finance.yahoo.com/about/plans/)

**thinkorswim (Schwab)**
- Schwab says clients get the platform for no charge, a Schwab account is required to log in, and non-clients can try a Guest Pass. — [Schwab](https://www.schwab.com/trading/thinkorswim) (search excerpt; a direct fetch returned an authorization error)
- A built-in VolumeProfile study is reached through Charts > Studies > Add Study. — [Schwab Learn](https://www.schwab.com/learn/story/richer-technical-view-analyzing-volume-by-price) (search excerpt)
- thinkorswim documents an AccumulationDistribution study based on comparing current and past price ranges, and describes it as tied to Dow theory phases. It also documents AccDist, the classic cumulative line. — [AccumulationDistribution](https://toslc.thinkorswim.com/center/reference/Tech-Indicators/studies-library/A-B/AccumulationDistribution); [AccDist](https://toslc.thinkorswim.com/center/reference/Tech-Indicators/studies-library/A-B/AccDist)

**Webull**
- Webull describes "Free Access to Webull Desktop" and says it supports 50 technical indicators and 12 charting tools. — [Webull intro](https://webullapp.com/introduce)
- A different Webull page says "60+ Indicators" and "20+ Drawing Tools," which conflicts with the figure above. It names no specific volume indicator. It lists Trading Central signals. — [Webull charts](https://www.webull.com/charts-tools)
- Orderflow Chart sits under "Data Subscription," which suggests a paid data product. No price was shown. — [Webull charts](https://www.webull.com/charts-tools); [Webull pricing](https://www.webull.com/pricing)

**Fidelity**
- "Fidelity Trader+ is available for free," though account fees may apply. It is offered through Fidelity brokerage accounts and has "100+ indicators," naming only RSI, MACD and Bollinger Bands. The cost of Active Trader Pro Classic is not stated. — [Fidelity](https://www.fidelity.com/trading/advanced-trading-tools/active-trader-pro/overview)
- Fidelity's indicator guide says it covers indicators available on Fidelity's platforms, and it has entries for Accumulation/Distribution and CMF. It does not say which platform has which indicator. — [Fidelity guide](https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/overview); [A/D](https://fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/accumulation-distribution); [CMF](https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/cmf)

### Inferences
- A shaded region on the price chart was confirmed only through TradingView community scripts. The other platforms provide lines, oscillators or side histograms that the user must read. Absence from public docs does not prove absence from the product.
- TradingView's 2-indicator cap means one zone script leaves room for one other tool. Whether a Volume bar overlay counts against the cap was not checked.
- Volume-based tools on TradingView's default feed could differ from consolidated-tape versions, because the feed is single-venue. Whether this also affects free daily bars is unknown.

### Gaps
- Could not confirm from a logged-in session whether TradingView Basic can use built-in Volume Profile or anchored drawing tools. No account was created, by instruction.
- Could not confirm whether StockCharts free users can add Volume-by-Price.
- Could not confirm whether Yahoo's free Advanced Chart includes OBV, A/D or CMF. The AAII count suggests it may, but the indicator list was not retrieved. Yahoo's help and AAII also point in different directions on what is free.
- Could not confirm named Webull or Fidelity indicators. Spam-like PDFs dominated Webull search results and were ignored.
- Schwab's own web charts were not separately checked, nor was Finviz's static quote-page chart.
- An EdgeRater page carries a banner for "Chart Central," a free Windows charting program needing no account. It is an unverified vendor claim and was not evaluated. — [EdgeRater](https://www.edgerater.com/docs/adline)

## Which indicators are relevant, what do they calculate, and can they separate institutions from everyone else?

### Takeaway
Every indicator here with a disclosed method is built from public bars, so none can see who traded. The IBD rating's formula is undisclosed, but it is reported to use price and volume too. These tools measure the direction, location or concentration of volume. "Accumulation" in these tools is an interpretation of price and volume, not an observation of big-player buying.

### Cited Findings

| Indicator | What it calculates | Inputs | Separates institutions? |
|---|---|---|---|
| On-Balance Volume | Running total: add the day's volume on an up close, subtract it on a down close | Close direction and total volume | No |
| Accumulation/Distribution Line | Cumulative sum of volume times close location in the bar's range | High, low, close, volume | No |
| Chaikin Money Flow | Same multiplier, summed over about 20 bars, divided by total volume | High, low, close, volume | No |
| Money Flow Index | RSI-like ratio of positive to negative price-times-volume flow over 14 bars | High, low, close, volume | No |
| Volume Profile | Volume traded at each price level over a period | Bars and volume | No; shows where trading happened, not who traded |
| Anchored VWAP | Volume-weighted average price from a chosen starting bar | Price, volume, chosen anchor | No |
| Wyckoff | Discretionary reading of ranges, spread, closes and volume | Price and volume plus judgment | No; it infers a hypothetical operator |
| Smart Money Concepts | Price-structure labels such as order blocks and fair value gaps | Price; the LuxAlgo page mentions no volume | No |
| IBD A/D Rating | Proprietary letter grade over 13 weeks | Reported to be price and volume | Claimed, but not by observing holders |
| Weinstein stages | Four-stage cycle around a 30-week moving average | Price; the role of volume was not confirmed from a primary source | No |

- OBV adds volume on up closes, subtracts it on down closes and holds flat when unchanged. Only its direction matters. StockCharts says unusually heavy volume can distort it. It does not discuss institutions. Rising OBV in a range is described as accumulation. — [StockCharts OBV](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/on-balance-volume-obv)
- The A/D Line is the cumulative sum of volume times Close Location Value. — [thinkorswim AccDist](https://toslc.thinkorswim.com/center/reference/Tech-Indicators/studies-library/A-B/AccDist)
- CMF multiplier = [(Close − Low) − (High − Close)] / (High − Low). Money Flow Volume = multiplier × volume. CMF = 20-period sum of Money Flow Volume / 20-period sum of volume. It ignores close-to-close change, so a stock can gap down and show rising CMF if it closes in the upper half of its range. — [StockCharts CMF](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/chaikin-money-flow-cmf)
- MFI: typical price = (H + L + C) / 3; raw money flow = typical price × volume; MFI = 100 − 100 / (1 + 14-period money flow ratio). Above 80 is usually called overbought and below 20 oversold. The page does not claim to detect institutions. — [StockCharts MFI](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/money-flow-index-mfi)
- TradingView builds Volume Profile from lower-timeframe bars. A bar counts as up volume if its close is at or above its open. That is a bar-direction rule, not actual buy and sell orders. TradingView calls the tool reactive. — [TradingView support](https://www.tradingview.com/support/solutions/43000502040-volume-profile-indicators-basic-concepts/)
- StockCharts' Volume-by-Price uses only closing prices, 12 zones by default, and a split based on up days and down days. — [StockCharts Volume-by-Price](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/volume-by-price)
- Anchored VWAP uses the VWAP formula from a chosen first bar through the latest bar. Typical anchors are a significant high or low, earnings, a gap or news. The page does not mention institutions. — [StockCharts Anchored VWAP](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/anchored-vwap)
- Brian Shannon's Alphatrends calls anchored VWAP a zone for observation, not a mechanical signal. — [Alphatrends](https://alphatrends.net/when-where-why-to-set-anchored-vwap/) (search excerpt)
- Wyckoff's Composite Man is a heuristic device for reading price moves as one operator's campaign. In accumulation Phase B, large interests are said to build a "cause." Heavy volume with little price progress is read as absorption. StockCharts says the reading is nuanced and takes considerable practice, phases may not follow a fixed sequence, and Phase C can be hard to identify. — [StockCharts Wyckoff](https://chartschool.stockcharts.com/table-of-contents/market-analysis/wyckoff-analysis-articles/the-wyckoff-method-a-tutorial)
- The LuxAlgo Smart Money Concepts page lists structure breaks, order blocks, fair value gaps and premium/discount zones, and does not mention volume. — [LuxAlgo SMC](https://www.tradingview.com/script/CnB3fSph-Smart-Money-Concepts-SMC-LuxAlgo/)
- IBD's A/D Rating is described as gauging institutional buying or selling over the prior 13 weeks, on an A+ to E scale, updated daily. — [NexusFi copy of IBD's glossary](https://nexusfi.com/showthread.php?p=605320)
- William O'Neil + Company reportedly describes it as a technical rating built from price and volume data, with a numeric form from +100 to −100. — [William O'Neil](https://origin.williamoneil.com/?p=623) (search excerpt only; a later direct fetch of this host failed to resolve); [O'Neil ratings page](https://www.williamoneil.com/about-us/legal/oneil-proprietary-rating-and-rankings)
- Stage Analysis comes from Weinstein's 1988 book. — [TinTin Trading School](https://tintintrading-school.teachable.com/courses/1694172) (practitioner source). Its use of four stages and a 30-week moving average appeared only in low-quality search results. The StockCharts page tried returned Page Not Found.

### Inferences
- If the O'Neil description is right, the IBD rating's "institutional" label is an inference from price and volume, not a measurement of institutional holders. The exact formula is undisclosed in what I could read.
- OBV, A/D, CMF and MFI overlap heavily, so showing several does not add independent confirmation. They differ mainly in which price comparison they use.
- Wyckoff's Composite Man is explicitly a heuristic in the source. So a Wyckoff label should not be read as evidence that a real large buyer exists.
- Stage 1 basing is the part of Weinstein closest to the user's idea, but it describes a price pattern, not who is buying.

### Gaps
- IBD's own methodology page could not be read, because investors.com blocked fetching. IBD or MarketSmith pricing was not confirmed, and no free source of the rating was verified.
- No primary-source definition of Weinstein's stages was retrieved. The book was not available to read.
- The base VWAP formula itself was not retrieved. The StockCharts page points to a separate article.

## Which community scripts shade accumulation zones, how do they decide, and is the logic disclosed?

### Takeaway
Named shaded-zone scripts exist, but the ones I could read define accumulation by swing shape or low volatility, and use volume only to draw a profile inside the zone. So "accumulation" often means a price pattern. I found no script that demonstrated it identifies institutions.

### Cited Findings

| Script | Access | Zone rule | Volume in the zone rule? | Repainting statement |
|---|---|---|---|---|
| [Accumulation And Distribution Zones (Zeiierman)](https://www.tradingview.com/script/xPd1d97H-Accumulation-And-Distribution-Zones-Zeiierman/) | Open-source; Nov 24, 2025 | Staircase: higher lows with compressing highs, over 4 or 6 swings | No; volume only for in-zone profile and POC | Not addressed |
| [Accumulation Zone Profiles (UAlgo)](https://www.tradingview.com/script/3k0H6Mbx-Accumulation-Zone-Profiles-UAlgo/) | Open-source (listing) | Volatility z-score drops below a threshold; a drift filter rejects trending periods | No; volume spread into a profile by candle overlap | Offers a non-repainting mode |
| [HTF Accumulation Distribution Zones (Analysis)](https://kr.tradingview.com/script/POKCSsi4-HTF-Accumulation-Distribution-Zones-Analysis) | Open-source; Dec 24, 2025, later updated | Candle strength vs ATR, volume participation, momentum; DIST also uses stretch from VWAP | Yes, mixed with price | Claims non-repaint on confirmed bars; live bar provisional |
| [Accumulation Map (LuxAlgo)](https://www.tradingview.com/script/hKHli2eM-Accumulation-Map-LuxAlgo/) | Protected; Oct 30, 2024 | Heatmap of traded volume per price level between anchor points | Yes, but "accumulation" means activity at a price | None |
| [Price Range Accumulation-Distribution (MarktQuant)](https://www.tradingview.com/script/SA8oyiVU-Price-Range-Accumulation-Distribution-MarktQuant/) | Invite-only; Mar 14, 2025 | Price far below a smoothed OHLC mean | Not mentioned | None |

- The Zeiierman script draws the zone once the pattern completes and says it is context, not a trade signal. It does not mention institutions. — [Zeiierman](https://www.tradingview.com/script/xPd1d97H-Accumulation-And-Distribution-Zones-Zeiierman/)
- The UAlgo rule uses log returns and an EWMA volatility estimate. A zone ends after volatility recovers for a set number of confirmation bars. — [UAlgo](https://www.tradingview.com/script/3k0H6Mbx-Accumulation-Zone-Profiles-UAlgo/) (from search excerpts; a regional page returned 404 and the main page was not read in full)
- The HTF script's defaults are tuned to NIFTY/NSE, not US stocks. It says higher timeframes are where "institutional activity tends to leave clearer footprints," and treats signals as reads on one "operator." It calls its labels context, not buy or sell signals. — [HTF script](https://kr.tradingview.com/script/POKCSsi4-HTF-Accumulation-Distribution-Zones-Analysis)
- The MarktQuant page has inconsistent labelling of bullish and bearish zones, and describes no volume use. — [MarktQuant](https://www.tradingview.com/script/SA8oyiVU-Price-Range-Accumulation-Distribution-MarktQuant/)
- Wyckoff scripts include Wyckoff Accumulation Phase Map [AGPro Series], reported as open-source and drawing events only after a bullish Change of Character. Wyckoff [theUltimator5] is reported as open-source. Wyckoff Phase Classifier uses a state machine and a filter requiring a close in the upper 55% of the bar's range. FibAlgo is reported as closed-source and Wyckoff Schematic [TrendX_] as invite-only. — [AGPro](https://www.tradingview.com/script/cJ65zYuc-Wyckoff-Accumulation-Phase-Map-AGPro-Series/); [theUltimator5](https://www.tradingview.com/script/tJzKloJn-Wyckoff-theUltimator5/); [Classifier](https://www.tradingview.com/script/9ap94IDt-Wyckoff-Phase-Classifier/); [FibAlgo](https://www.tradingview.com/script/HzH1gd30-FibAlgo-Wyckoff-Accumulation-Distribution/); [TrendX](https://www.tradingview.com/script/5UgTZK9u-Wyckoff-Schematic-Accumulation-TrendX/) (all from search excerpts, pages not opened)
- Smart Money Concepts [LuxAlgo] is labelled open-source on the TradingView page, published Oct 2022 and updated Sep 2025. Its Mode setting offers Historical or Present. It makes no repainting statement. — [LuxAlgo SMC](https://www.tradingview.com/script/CnB3fSph-Smart-Money-Concepts-SMC-LuxAlgo/). This conflicts with a LuxAlgo blog post that points to Invite-only scripts, which may refer to a different product. — [LuxAlgo blog](https://www.luxalgo.com/blog/smart-money-concept-indicator-for-tradingview-free/) (search excerpt)
- Repainting means a script's historical and realtime calculations or plots behave differently. — [Pine Script repainting docs](https://www.tradingview.com/pine-script-docs/concepts/repainting/)
- TradingView says pivots are confirmed only after later bars, and plotting them back in time makes them look on-time. It places such plots in a "potentially misleading" category, suggests making them opt-in, and treats future leaks as unacceptable. It also says not all repainting is useless. — [Pine Script repainting docs](https://www.tradingview.com/pine-script-docs/concepts/repainting/)
- Publishing rules bar misleading or unsubstantiated statements, and say lookahead-biased `request.security()` calls are not suitable for publications. — [Pine Script publishing docs](https://www.tradingview.com/pine-script-docs/writing/publishing/)

### Inferences
- The scripts' swing-based zones are confirmed only after the pattern finishes, so the shaded box can start well before the moment it was knowable. On a past chart it will look earlier than it could have been in real time. A script can honestly be "non-repainting" and still have this delay.
- A low-volatility rule would likely also flag quiet ranges that resolve downward, because the rule has no direction test. The same applies to the Zeiierman pattern if price then breaks down. Neither page reports a rate of failed zones.
- Protected and invite-only scripts cannot be audited, so their repainting and lookahead behavior cannot be checked from source.
- A practical check is to compare where zones appear with replayed or forward-saved charts, not with the finished chart. Note that Bar Replay availability on the free plan was not checked.

### Gaps
- No script's source code was read, so the rules above come from the authors' own descriptions. Repainting behavior was not tested.
- Found no independent review or performance data for any named script.
- This list is a sample of what searches surfaced, not a census of TradingView's script library.

## Is there independent evidence that these indicators predict returns or identify institutional buying?

### Takeaway
Evidence is thin. I found no study validating any of these indicators against real institutional trades or holdings. The best positive result is a small monthly forecasting effect for OBV-style rules on the S&P 500 index, not on individual stocks. A major test of technical rules found they did not survive persistence tests and costs. For Wyckoff, Smart Money Concepts, anchored VWAP, Weinstein stages, CMF, MFI and the IBD rating, I found no independent peer-reviewed tests.

### Cited Findings

**Positive or mixed**
- Neely, Rapach, Tu and Zhou (Management Science, 2014) found technical indicators had statistically and economically significant forecasting power for the equity risk premium, matching or exceeding macro variables. — [Paper page](https://ink.library.smu.edu.sg/lkcsb_research_smu/147/)
- Their working paper tests monthly OBV-based moving average rules on the S&P 500. VOL(1,12) has a slope of 0.89 (t = 2.31) and an in-sample R² of 0.92%, covering 1951 to 2011. — [St. Louis Fed working paper](https://fraser.stlouisfed.org/docs/publications/frbsl_wp/2010-008.pdf)
- Out of sample (1966 to 2011), VOL(1,12) shows an R²OS of 0.80%, about −0.24% in expansions and 2.94% in recessions. The paper says technical predictive power concentrates in recessions. — [St. Louis Fed working paper](https://fraser.stlouisfed.org/docs/publications/frbsl_wp/2010-008.pdf) (read from a PDF text extraction whose table columns were misaligned; check against the published table)
- Tsang and Chong (Economics Bulletin, 2009) report the OBV rule "is increasingly profitable" in Greater China stock markets. Only the abstract was read, and the markets are not US. — [RePEc](https://ideas.repec.org/a/ebl/ecbull/eb-09-00423.html)
- Gervais, Kaniel and Mingelgrin (Journal of Finance, 2001) found stocks with unusually high volume over a day or week tend to rise over the next month, and low-volume stocks tend to fall. They link this to investor attention, not institutional accumulation. — [RePEc](https://ideas.repec.org/a/bla/jfinan/v56y2001i3p877-919.html)

**Negative**
- Bajgrowicz and Scaillet (Journal of Financial Economics, 2012) tested technical rules on daily DJIA data. Performance before costs looked useful for 1897 to 1996 even after data-snooping controls, but persistence tests show investors could never have selected the best rules in advance, and in-sample performance is fully offset by transaction costs. Backtested outperformance disappears in January 1997 to July 2007. — [RePEc](https://ideas.repec.org:443/a/eee/jfinec/v106y2012i3p473-491.html); [CFA digest](https://rpc.cfainstitute.org/research/cfa-digest/2013/02/technical-trading-revisited-false-discoveries-persistence-tests-and-transaction-costs-digest)
- A 1971 UBC thesis tested OBV on five stocks, found profits on two, and judged return variability too large to accept the method. It is old and small. — [UBC](https://open.library.ubc.ca/collections/831/items/1.0101773)

**No rigorous test found**
- Wyckoff: LuxAlgo's library says event and phase labels are far easier to assign in hindsight, and that no broadly accepted statistical study shows the schematics predict outcomes. LuxAlgo sells related tools, so this is a vendor statement against interest, not a study. — [LuxAlgo Wyckoff](https://www.luxalgo.com/library/concept/wyckoff-method.md) (search excerpt)
- CMF: Chaikin Analytics reports favorable internal backtests, but the firm created the indicator, so this is not independent. — [Chaikin Analytics](https://www.chaikinanalytics.com/?p=39750) (search excerpt)
- Anchored VWAP: one web page presents an "academic" summary but names no papers, authors or data. It should not be relied on. — [nacsa page](https://kobo.nacsa.gov.sl/anchored-vwap-academic-paper-decoding-the-metrics-that-move-the-market)

**What real institutional data says (relevant to the "low prices" idea)**
- Campbell, Ramadorai and Schwartz (JFE, 2009) estimated daily institutional trades from tape data, calibrated to quarterly 13-F filings. Trades are highly persistent, respond positively to recent daily returns and negatively to longer-run past returns. Trades, particularly sells, appear to produce short-term losses but are profitable over longer horizons, partly by anticipating earnings surprises. Results differ from a standard trade-size cutoff rule. — [RePEc](https://ideas.repec.org/a/eee/jfinec/v92y2009i1p66-91.html)
- The 2005 working paper found both very large and very small trades signal institutional activity, while medium trades reflect the rest of the market. — [NBER](https://www.nber.org/papers/w11439)

### Inferences
- The OBV result is an index timing effect at monthly frequency, in a sample where it mostly worked in recessions. It does not show that OBV finds accumulation in a single stock.
- Neely tested a few rule settings, and the paper's result is for a period already past. It is not a sign of a current edge.
- Finding that very small trades can be institutional undercuts any chart logic that assumes large means institutional.
- The short-term losses in Campbell et al. suggest big buyers may not look "right" immediately, which also makes after-the-fact zone reading easy to overrate.
- Hindsight risk is likely large for shaded zones. A viewer sees mainly the zones that preceded a rise, and failed zones draw no attention.

### Gaps
- Found no peer-reviewed or rigorous independent test of MFI, CMF, A/D Line, Volume Profile, Anchored VWAP, Smart Money Concepts, Wyckoff schematics, Weinstein stages or the IBD A/D Rating. This reflects a limited search, not proof that none exists. Google Scholar and SSRN were not searched directly.
- Found no study comparing any of these indicators with 13F changes or actual institutional flow.
- The Chinese-market OBV paper was seen only in part, so its findings are not reported. — [arXiv](https://arxiv.org/pdf/1504.06397)
- The 2018 paper "Dynamic trading volume and stock return relation: Does it hold out of sample?" was seen only as metadata, so its findings are unknown. — [RePEc](https://ideas.repec.org:443/a/eee/finana/v58y2018icp195-210.html)
- Sample dates for Bajgrowicz and Scaillet differ across versions, so check before quoting end dates.

## Do institutional order-flow estimates from academic work exist in any free public tool?

### Takeaway
I found no free public tool that publishes Campbell-Ramadorai-Schwartz or BJZZ-style estimates per stock. Both methods need trade-level data from NYSE TAQ. BJZZ also targets retail trades, not institutions. The nearest free public data is FINRA short sale volume, which does not identify institutions.

### Cited Findings
- Campbell et al. use the NYSE Transactions and Quotes database, calibrated to quarterly 13-F data. — [RePEc](https://ideas.repec.org/a/eee/jfinec/v92y2009i1p66-91.html). A later conference deck describes relating 13F changes to order flow across trade-size bins, with Lee-Ready trade direction. — [ABFER slides](https://www.abfer.org/media/abfer-events-2017/annual-conference/investment-finance/22-2-a_jingi-ha.pdf) (secondary, search excerpt)
- BJZZ identifies retail trades in NYSE TAQ: off-exchange trades reported to a FINRA facility with subpenny price improvement. It signs a buy for a fractional cent between 0.6 and 1.0, a sell between 0.0 and 0.4, and excludes 0.4 to 0.6. — [Ardia, Aymard and Cenesizoglu, 2024](https://ar5iv.labs.arxiv.org/html/2403.17095)
- Barber et al. tested about 85,000 trades across six retail brokerage accounts. BJZZ accurately identified only about 35%, and about 28% of the trades it did identify were signed incorrectly. A quote-midpoint method reduces signing errors to about 5%, without changing identification rates. — [Ardia et al.](https://ar5iv.labs.arxiv.org/html/2403.17095)
- Battalio, Jennings, Saglam and Wu report that just over 94% of matched known retail trades had the correct inferred side, in tension with the Barber signing-error figure. — [Battalio et al.](https://tc.lsu.edu/business/files/event-files/2025-finance-mardi-gras/battalio-jennings-saglam-wu.pdf) (search excerpt)
- Ardia et al. replicate BJZZ for 2010 to 2015, but predictive power weakens significantly in 2016 to 2021. Past imbalance no longer predicts weekly returns for large caps, and a long-short strategy is no longer profitable across all stocks. — [Ardia et al.](https://ar5iv.labs.arxiv.org/html/2403.17095)
- FINRA's site shows the last 365 days of short sale volume, with older data by daily or monthly file or Query API. — [FINRA](https://www.finra.org/finra-data/browse-catalog/short-sale-volume-data)
- Daily short volume covers trades reported to FINRA facilities on a T+1 basis, and venue-level ATS volumes come with a two-to-four-week lag. A print records a completed trade and does not show which side initiated it. — [LuxAlgo dark pool concept](https://www.luxalgo.com/library/concept/dark-pool-prints/) (secondary)
- SqueezeMetrics DIX is a dollar-weighted average of dark-pool short-sale ratios for S&P 500 stocks, presented as a proxy for possible buying activity. The page did not say whether it is free or per-stock. — [SqueezeMetrics](https://squeezemetrics.com/monitor/dix)
- Fintel republishes FINRA short volume by ticker. — [Fintel](https://fintel.io/ss/us/fdx) (search excerpt)
- Stockgrid's dark pool URL now redirects to axlfi.com, and that page showed only the title "Market Overview." — [Stockgrid URL](https://www.stockgrid.io/darkpools); [axlfi](https://axlfi.com/)

### Inferences
- A self-built version of either method would need trade-level data, so it is not a free charting option. For Campbell-style work, 13F files alone are quarterly, so they cannot date an accumulation window finely.
- Even if BJZZ were free, it would answer "what are retail traders doing?" Institutional flow would remain the unexplained remainder, not a measured quantity.
- FINRA short volume is not a buying measure at face value. Treating high short volume as institutional accumulation depends on a market-maker interpretation that this research did not validate.

### Gaps
- Found no public implementation or free per-stock feed, but the search for one was limited. Searches were general web queries, not GitHub searches.
- TAQ pricing and access terms were not confirmed. WRDS was not checked.
- FINRA's explanatory page returned 404, so coverage and timing rest on a secondary source. Its fee status was not stated, although the page loaded without a login.
- Could not confirm Stockgrid's current status, or whether axlfi is its successor.
- The Interactive Brokers article on tracking retail activity in TAQ returned 403 and was not read.
