# Free options flow and unusual options activity tools for US stocks (as of 31 October 2026)

Evidence labels used throughout:
- **Direct**: the page was fetched on 2026-10-31 without logging in.
- **Index**: the page refused or did not render for the fetcher, so its text was seen only through search-engine results. Treat this as weaker and possibly stale.
- **Not reached**: neither route gave usable content.

No accounts were created and no personal information was entered. So everything below describes logged-out views or vendor statements, never a logged-in free account.

## Which sites offer this, and which are actually functional for free?

### Takeaway
Free data exists, but only a few tools give anything useful on a named ticker without payment. Fintel, Market Chameleon, Unusual Whales (delayed), MarketBeat and the OCC (not live-tested) are the main candidates. Cheddar Flow has no permanent free tier, and Yahoo and Nasdaq are option chains rather than flow tools.

### Cited Findings
- **Fintel**: a logged-out MSFT options page shows real daily put/call volume and open interest (OI), with ratio columns locked — [Fintel MSFT options](https://fintel.io/sopt/us/msft) (Direct). A separate flow page exists, but most trade fields are locked — [Fintel MSFT flow](https://fintel.io/sof/us/msft) (Direct).
- **Market Chameleon**: a logged-out MSFT page shows current-day totals. Data as of 30 Oct 2026: 554,343 contracts (320,604 calls, 233,739 puts), put/call 0.73, 30-day average 558,668 — [Market Chameleon MSFT](https://marketchameleon.com/Overview/MSFT/OptionSummary/) (Direct).
- **Unusual Whales**: has a $0 plan, but options flow on it is delayed 2 trading days — [UW pricing](https://unusualwhales.com/pricing) (Direct).
- **InsiderFinance**: free live flow shows the "15 most recent trades delayed by 30 minutes", plus free hourly AI flow analysis — [InsiderFinance home](https://www.insiderfinance.io/) (Direct).
- **OptionStrat**: vendor text says flow has a free tier with delayed data and a subset of features, available without an account — [OptionStrat blog](https://optionstrat.com/blog/introducing-enhanced-options-flow) (Index; direct fetches returned 403).
- **Barchart**: has market-wide and per-ticker unusual activity and flow pages — [unusual activity](https://www.barchart.com/options/unusual-activity), [MSFT options flow](https://www.barchart.com/stocks/quotes/MSFT/options-flow) (Index; pages rendered empty to the fetcher).
- **Cheddar Flow**: the free offer found was a single 7-day trial, then $85/month Standard, $99/month Professional — [Cheddar Flow pricing](https://www.cheddarflow.com/pricing/) (Index; direct fetch returned 403). Its own comparison page also mentions "free access" for a test run, without further detail — [Cheddar Flow vs Flow Algo](https://www.cheddarflow.com/cheddar-flow-vs-flow-algo/) (Index).
- **Yahoo Finance**: an option chain only, with no flow, unusual or buy/sell view — [Yahoo MSFT options](https://finance.yahoo.com/quote/MSFT/options/) (Direct, but the fetched copy showed an error and empty tables, which may be a fetch artifact).
- **Nasdaq**: an option chain listing price, volume and OI by strike and expiry — [Nasdaq option chain](https://www.nasdaq.com/market-activity/quotes/option-chain) (Index; the MSFT page timed out).
- **OCC**: public volume data by symbol and account type — [OCC Volume Query batch docs](https://www.theocc.com/Market-Data/Batch-Processing/Volume-Query-Batch-Processing) (Index). The live endpoint could not be tested: `marketdata.theocc.com` returned HTTP 503 "maintenance downtime or capacity problems" and timed out on 2026-10-31, a Saturday evening.

Free alternatives found:
- **MarketBeat**: a free end-of-day MSFT chain that includes volume split into ask and bid, sourced from Trade Alert and Intrinio — [MarketBeat MSFT options](https://www.marketbeat.com/stocks/NASDAQ/MSFT/options/) (Direct). This was the only logged-out free source found showing an ask/bid volume split.
- **Financhle**: guests get "a small preview" with no filters, and a free account unlocks the full list and filters — [Financhle](https://www.financhle.com/unusual-options) (Direct).
- **OptionCharts**: has a Historical Data section and says real-time data is paid, but free scope is not stated — [OptionCharts MSFT](https://optioncharts.io/options/MSFT) (Direct, inconclusive).
- **Moomoo**: its app has an unusual-activity feature for trades of 1,000+ contracts, which needs an account — [Moomoo manual](https://www.moomoo.com/ca/manual/topic-14-230) (Index).
- **Stocknear**: a third-party directory ranks it as a free options-flow tool — [FindMyMoat](https://www.findmymoat.com/free/data-partners/options-flow) (Index). A direct fetch of its flow page returned HTTP 402.

### Inferences
- For a one-off look at MSFT with no signup, Fintel and Market Chameleon are the most useful options seen. Unusual Whales may be the richest free per-trade source, but its logged-in free view could not be tested.
- "Big players" cannot be identified on any free view seen. The tools show trade size and sometimes location against the quote, not the identity of the trader.

### Gaps
- OptionStrat, Cheddar Flow, Barchart and OCC could not be read directly, so their entries are lower confidence.
- Cheddar Flow's "free access" wording was not resolved. It most likely means the trial, but that is an assumption.
- Stocknear's current free scope and delay are unconfirmed.

## For each tool, what is free, what is locked, is signup or a card needed, and what are the delay and history length?

### Takeaway
Free delays range from 15 minutes to 2 trading days, and free history is short or absent. Paid plans hold nearly all of the lookback. The clearest free lookback seen is Fintel's roughly 5 weeks of daily volume and OI.

### Cited Findings

| Tool | Free | Locked | Signup / card | Delay | Free history | Evidence |
|---|---|---|---|---|---|---|
| [Fintel options](https://fintel.io/sopt/us/msft) | OI put/call 0.59; put OI by expiry; about 2 weeks of put and OTM put OI; about 5 weeks of daily put/call volume and OI | Call OI by expiry, ratios, volume/OI columns, most premium and volume rows | Viewed logged out; unlock links go to checkout | "Update Frequency: Daily". Newest rows were 2026-10-28 when read 2026-10-31 | About 5 weeks (09-24 to 10-28) | Direct |
| [Fintel flow](https://fintel.io/sof/us/msft) | Date, time, symbol, put/call, strike, expiry; summary tiles ($108.3M premium, 29,908 trades) | Price, premium, size, OI, volume, bid/ask gauge, directional premium, unusual score, conditions | Same as above | Page says "Real-time"; visible rows were all from 2026-10-26 | Unclear | Direct |
| [Market Chameleon summary](https://marketchameleon.com/Overview/MSFT/OptionSummary/) | Day's volume, put/call, 30-day average, IV30, implied move | Premium sections (order flow sentiment and others) | Viewed logged out; "Register Free", "Free Trial" links | 15 minutes | Single day plus 30-day average | Direct |
| [Market Chameleon unusual report](https://marketchameleon.com/Reports/UnusualOptionVolumeReport) | Base report (table did not render to fetcher); 10-day market-wide counts | Historical date selection, most filters, download | Not stated for base report | 15 minutes | Historical dates are premium | Direct |
| [Market Chameleon order sentiment](https://marketchameleon.com/Overview/MSFT/OptionOrderSentiment/) | Report description and list of dates only | Net delta volume, bullish/bearish totals, top contracts, daily chart, per-date values | "Login Or Try 7-Day Free Trial" on [a similar page](https://marketchameleon.com/Overview/QURE/OptionOrderSentiment/) (Index) | 15 minutes | Dates listed back to Sep 21, values locked | Direct |
| [Unusual Whales](https://unusualwhales.com/pricing) | Delayed dashboard, screeners, charts, saved filters, watchlists, community chat | Real-time flow, news, alerts; GEX; daily options and dark pool downloads | $0 plan; no card mentioned; account need not stated | Flow 2 trading days; news 15 min; alerts 30 min | Not stated | Direct |
| [InsiderFinance](https://www.insiderfinance.io/) | 15 most recent trades; hourly AI analysis | Real-time flow, on-demand history ([$55 to $75/month](https://www.insiderfinance.io/pricing)) | Not stated | 30 minutes | Not stated | Direct |
| [OptionStrat](https://optionstrat.com/blog/introducing-enhanced-options-flow) | Delayed flow with a subset of features, no account needed | Live flow; vendor pages conflict at [$99.99](https://www.optionstrat.com/ticker/WMT) vs [$89.99](https://www.optionstrat.com)/month | No account for flow per vendor | [15 minutes](https://login-test.optionstrat.com/) | Not found | Index |
| [Barchart](https://www.barchart.com/options/unusual-activity) | Possibly the current-day list; see conflict below; 1 site download per day | History, extra dates and filters, CSV | Not confirmed | About 25 to 30 minutes, updated about every 5 minutes | None without Premier | Index |
| [Cheddar Flow](https://www.cheddarflow.com/pricing/) | One 7-day trial on Standard only | All else | Paid by card; trial auto-bills unless cancelled | Real-time when paid | Not free | Index |
| [Yahoo](https://finance.yahoo.com/quote/MSFT/options/) | Chain: last, bid, ask, change, volume, OI, IV | Real-time via AlphaSpace, listed under Premium Research | None seen | 15 minutes | None for options | Direct |
| [Nasdaq](https://www.nasdaq.com/market-activity/quotes/option-chain) | Chain: price, volume, OI | Not found | None found | Unconfirmed | None found | Index |
| [OCC](https://www.theocc.com/Market-Data/Batch-Processing/Volume-Query-Batch-Processing) | Volume by symbol and account type (ALL, C customer, F firm, M market maker); daily, weekly or monthly; CSV | No paid requirement found | None found | Unconfirmed | Unconfirmed | Index |
| [MarketBeat](https://www.marketbeat.com/stocks/NASDAQ/MSFT/options/) | Chain by expiry with ask/bid volume, OI, IV, delta, trade count | CSV export, more watchlist slots | Basic chain appeared open | End of day (updated 10/30/2026) | None shown | Direct |
| [Financhle](https://www.financhle.com/unusual-options) | Guest preview; full list and filters with free account | "Pro" tier scope not described | Free account for filters | "Live", undefined | Date filter exists, depth unknown | Direct |

Conflicts:
- **Unusual Whales delay**: the pricing page says 2 trading days. A [free-trial landing page](https://unusualwhales.com/lp/unusual-whales-free-trial) says 15 to 20 minutes, and a [legacy FAQ](https://docs.unusualwhales.com/faq/) says 5 to 12 minutes (both Index). The pricing page is the most likely current figure.
- **Barchart free scope**: one search summary says the current day is free, but another says Premier members view it. Neither could be checked live ([Barchart unusual activity](https://www.barchart.com/options/unusual-activity), Index).
- **OptionStrat flow price**: $99.99 and $89.99 both appear on vendor pages, and neither could be fetched.

### Inferences
- The free Fintel tables were at least 2 trading days old when read, since Oct 29 and 30 were missing on Saturday Oct 31. Their schedule may simply be slower than "daily" suggests.
- The Fintel flow page's "real-time" label should not be read as a free real-time feed. The visible rows were 5 days old and lacked price and size.

### Gaps
- History length on the Unusual Whales free plan is not stated anywhere I could read. A [comparison page](https://unusualwhales.com/lp/unusual-whales-vs-flowalgo) markets a full historical database without saying who gets it.
- Whether Unusual Whales needs an account for flow was not confirmed, though a "free plan" implies one.
- Fintel and Market Chameleon pricing pages were not retrieved (403 or not found in search).
- Which Barchart fields a free user sees could not be confirmed.

## Does it give a time series or history for a ticker, or only today's list?

### Takeaway
Most free views are today-only. Free lookback over past weeks is limited to Fintel's daily, non-directional volume and OI, plus possibly the OCC and delayed Unusual Whales. True per-ticker flow history is paid.

### Cited Findings
- **Fintel** shows about 5 weeks of daily MSFT put and call volume and OI, and about 2 weeks of put OI, with the Oct 28 row the only one visible for premium bought/sold — [Fintel MSFT options](https://fintel.io/sopt/us/msft) (Direct).
- **Barchart Premier**: unusual activity reports go back to 14 May 2020 — [Barchart help](https://help.barchart.com/support/solutions/articles/246565-view-historical-unusual-options-activity) (Direct). Options flow history goes back to 2 Jan 2024, limited to the latest 100 records per symbol sorted by premium — [Barchart options flow](https://www.barchart.com/stocks/quotes/MSFT/options-flow) (Index). Daily put/call history runs up to 2 years — [Barchart options history](https://www.barchart.com/stocks/quotes/MSFT/options-history) (Index).
- **Market Chameleon** lists MSFT order-sentiment dates back to Sep 21, 2026, but locks each date's values and the daily chart — [Market Chameleon sentiment](https://marketchameleon.com/Overview/MSFT/OptionOrderSentiment/) (Direct).
- **Paid vendors** list history as a paid feature: "On-Demand Historical Data" at [InsiderFinance](https://www.insiderfinance.io/pricing) (Direct) and [Cheddar Flow](https://www.cheddarflow.com/pricing/) (Index).
- **OCC** documents daily, weekly and monthly volume by symbol, and its Volume by Account Type download adds rolling-year and yearly reports — [OCC batch docs](https://www.theocc.com/Market-Data/Batch-Processing/Volume-by-Account-Type-Download-Batch-Processing) (Index).
- **MarketBeat** and **Yahoo** show no historical options series — [MarketBeat](https://www.marketbeat.com/stocks/NASDAQ/MSFT/options/), [Yahoo](https://finance.yahoo.com/quote/MSFT/options/) (Direct).

### Inferences
- For "when were big players positioning in MSFT over past weeks", the free tools only support a rough question: did daily volume or OI jump on some date? They do not show who traded, in which direction, or at what size.
- The OCC could add a free customer, firm and market maker volume split by date, if the endpoint works when tested on a weekday. "Customer" would not mean small retail, because hedge funds trade as customers of full-service brokers in [Pan and Poteshman's classification](https://www.nber.org/system/files/working_papers/w10925/w10925.pdf).
- A self-built history is possible by saving Fintel or OCC readings each day, subject to each site's terms. I did not review those terms.

### Gaps
- The OCC's retention window is unconfirmed. Older OCC material variously described five and two years of rolling data for reports that have since changed ([OCC site update notes](https://www.theocc.com/specialpages/whats-changed), Index).
- Whether Unusual Whales' free tier lets a user page back through older days for one ticker is unknown.
- The OCC does not appear to publish OI by account type, based on the [Open Interest page](https://www.theocc.com/market-data/market-data-reports/volume-and-open-interest/open-interest) description (Index), but this is not confirmed.

## Can it separate buying from selling, and how reliable is that given that opening versus closing and hedging are usually unknown?

### Takeaway
Tools infer direction from where a trade printed against the bid and ask, which is an estimate rather than a record. Opening versus closing and the trader's motive are not shown by any free tool. True open/close data exists at the exchange level but costs hundreds to thousands of dollars a month.

### Cited Findings
- **Barchart** labels each trade Ask, Bid or Mid, and filters to trades above 10 contracts — [Barchart options flow](https://www.barchart.com/options/options-flow) (Index).
- **Market Chameleon** says "there isn't a way to determine if an option was bought or sold with 100% accuracy". It warns that limit orders can distort the reading, and tags unclear trades as undetermined — [Market Chameleon method](https://marketchameleon.com/Learn/OrderFlowSentimentScreener) (Direct). Its sentiment logic counts calls bought at the offer as bullish and puts bought at the offer as bearish — [MSFT sentiment](https://marketchameleon.com/Overview/MSFT/OptionOrderSentiment/) (Direct). One of its sentiment pages reportedly says complex orders are excluded because they may be hedges — [sentiment pages, e.g. AMZN](https://marketchameleon.com/Overview/AMZN/OptionOrderSentiment/) (Index; exact page not pinned, and its method page does not cover this).
- **Fintel** describes its unusual score as a screening signal rather than proof of informed trading, and says spreads and hedges may not reflect a simple directional view — [Fintel options flow](https://fintel.io/sof) (Index).
- **Free side data** seen: MarketBeat's ask/bid volume [chain](https://www.marketbeat.com/stocks/NASDAQ/MSFT/options/) (Direct), and Financhle's Ask, Bid and Mid [filter](https://www.financhle.com/unusual-options), which appears to need a free account (Direct).
- **Accuracy**: on a CBOE dataset with true direction, the quote, Lee-Ready, EMO and tick rules signed about 83%, 80%, 77% and 59% of classifiable trades correctly. Trades outside the quote or with reversed quotes were heavily misclassified, and some complex index option trades were wrong almost half the time — [Savickas and Wilson 2003](https://ideas.repec.org/a/cup/jfinqa/v38y2003i04p881-902_00.html) (abstract only; rule-to-figure mapping taken from the abstract's order).
- **Open versus close**: Pan and Poteshman stress that public data cannot separate opening from closing trades, which makes the public signal inferior — [Pan and Poteshman](https://www.nber.org/system/files/working_papers/w10925/w10925.pdf) (Direct).
- **Paid truth data**: the ISE end-of-day product reports opening buy, closing buy, opening sell and closing sell. A 2024 fee filing lists $850/month (from $750) on an annual subscription, or $2,500/month (from $2,000) intraday — [SEC 34-101096 exhibit 5](https://www.sec.gov/files/rules/sro/ise/2024/34-101096-ex5.pdf) (Direct). Cboe sells comparable [Open-Close data](https://datashop.cboe.com/open-close-cboe-c2-exchange) (Index). A 2026 filing proposes renaming the ISE product "ISE Trade Outline" and adding market makers as an origin type — [SR-ISE-2026-17](https://listingcenter.nasdaq.com/assets/rulebook/ise/filings/SR-ISE-2026-17.pdf), [Federal Register copy](https://public-inspection.federalregister.gov/2026-08110.pdf) (Index; exact document not pinned, and the outcome of the proposal is unknown).

### Inferences
- A rough rule from these sources: treat Ask/Bid labels as about 80% reliable on simple single-leg trades in old CBOE data, and less on multi-leg trades. The current figure for electronic, multi-exchange markets could differ.
- Even a correctly signed "bought at the ask" call can be a close of a short position, a stock-hedge overlay or a leg of a spread. A bullish label is therefore an interpretation.
- Fintel's rule that volume above OI marks unusual activity hints at new positions but does not prove them. Volume can exceed OI through same-day round trips.

### Gaps
- I found no vendor-published accuracy rate for its own buy/sell classification.
- I found no current study of Lee-Ready accuracy on today's US multi-exchange equity options tape. A [2024 prize-winning thesis](https://www.bvai.de/en/press/bai-press-releases/bai-awards-2024-science-prize-in-alternative-investments-4-december-2024) reports machine learning beating classic rules on ISE and CBOE data, but I did not obtain accuracy figures. Grauer, Schuster and Uhrig-Homburg's work was not located.

## Is there academic evidence that options flow predicts stock moves, and is any effect usable by retail investors after delay?

### Takeaway
Yes, options volume has predicted stock returns in published studies, but the strongest result used non-public data from 1990 to 2001. The publicly observable signal faded in 1 to 2 trading days and then partly reversed. Later work shows much of the remaining effect is hard to capture after borrow fees, so I found no evidence that delayed free data gives retail users a usable edge, particularly in a very liquid stock like MSFT.

### Cited Findings
- **Pan and Poteshman (RFS 2006; NBER 2004 version read)**: using CBOE open-buy volume for 1990 to 2001, stocks in the lowest put/call quintile beat the highest by over 40 basis points a day and 1% a week on a risk-adjusted basis — [NBER w10925](https://www.nber.org/system/files/working_papers/w10925/w10925.pdf).
- **Public signal in that paper**: signals built from public trade and quote data with Lee-Ready predicted returns "for only the next 1 or 2 trade days", and prices then reversed. In a joint 1990 to 1996 regression, the open-buy signal kept a slope of -44 basis points (t = -16.27), while the public signal fell to -5 basis points (t = -1.68) — [NBER w10925](https://www.nber.org/system/files/working_papers/w10925/w10925.pdf).
- **Who was informed**: signals from full-service brokerage customers, which include hedge funds, were much stronger than those from discount brokerages, and firm proprietary traders' signals carried no information — [NBER w10925](https://www.nber.org/system/files/working_papers/w10925/w10925.pdf).
- **Johnson and So (JFE 2012)**: firms in the lowest option-to-stock volume decile beat the highest by 0.34% a week (19.3% annualized). The signal was stronger when short-sale costs were high or option leverage low, and it predicted earnings news — [RePEc listing](https://ideas.repec.org/a/eee/jfinec/v106y2012i2p262-286.html) (abstract only). This treats high option volume relative to stock volume as a negative sign, which runs against the "big call volume is bullish" reading.
- **Ge, Lin and Pearson (JFE 2016)**: signed volume data point to embedded leverage as the most important reason option trading predicts returns — [RePEc listing](https://ideas.repec.org/a/eee/jfinec/v120y2016i3p601-622.html) (abstract only).
- **Hu (JFE 2014)**: the part of stock order imbalance induced by options significantly predicts returns, because market makers hedge in the stock — [RePEc listing](https://ideas.repec.org/a/eee/jfinec/v111y2014i3p625-645.html) (abstract only). Muravyev, Pearson and Pollet summarize this as imbalances being passed through quickly — [working paper](https://www.aeaweb.org/conference/2023/program/paper/RsBt64RZ) (Direct).
- **Muravyev, Pearson and Pollet (JFE 2025; March 2022 working paper read)**: predictability from option signals, including the option-to-stock ratio, falls by about two-thirds after adjusting returns for stock borrow fees, and by a similar amount if high-fee stocks are excluded — [working paper](https://www.aeaweb.org/conference/2023/program/paper/RsBt64RZ). The university summary calls it "a mirage" not readily exploitable in practice — [Gies College news](https://giesbusiness.illinois.edu/news/2026/01/07/study--borrowing-fee-is-the-variable-that-debunks-theory-that-options-predict-future-stock-returns) (a press piece, stronger in tone than the abstract).
- **Muravyev, Pearson and Broussard (JFE 2013)**: for 39 highly liquid US stocks, option quotes adjust to resolve disagreements with stock quotes, and no economically significant price discovery was found in option quotes — [Hanken research portal](https://research.hanken.fi/en/publications/is-there-price-discovery-in-equity-options/). This studies quotes rather than volume. In contrast, Patel, Putniņš, Michayluk and Foley find options' role is up to five times larger than previously thought — [UTS](https://www.uts.edu.au/news/2021/07/research-price-discovery-wins-2020-phillip-brown-prize).
- **Augustin, Brenner and Subrahmanyam (Management Science 2019)**: about a quarter of 1,859 US takeovers from 1996 to 2012 showed abnormal option volume before announcement, greater in short-dated out-of-the-money calls. The SEC litigated about 8% of deals in that sample — [Hebrew University listing](https://cris.huji.ac.il/en/publications/informed-options-trading-prior-to-takeover-announcements-insider-/) (summary only). This supports informed trading around specific events, but it was identified after the fact.

### Inferences
- The academic result most often cited by flow vendors rests on data that free tools do not offer: open-buy volume by investor class. Free tools resemble the weaker public signal.
- Unusual Whales' free 2-trading-day delay is about the length of the public signal's life in Pan and Poteshman. A 15 to 30 minute delay is much shorter, though that study's data is from a far slower market, so this comparison is only suggestive.
- MSFT is close to the worst case for this signal. The cited studies find stronger effects with high short-sale costs, informed-trader concentration or corporate events such as takeover targets, while MSFT is a very liquid stock. I did not check MSFT's actual borrow fee.
- Options flow may work better as a prompt to look for news or events than as a timing signal. This is my interpretation, not a tested result.

### Gaps
- I found no peer-reviewed study testing retail flow products or alerts from these vendors, and none measuring returns after a 15-minute, 30-minute or 2-day delay.
- Muravyev (2016) on order flow and option returns was searched for but not found.
- I found no direct evidence on transaction costs for acting on these signals. Only the borrow-fee work addresses frictions.
- Johnson and So, Ge et al., Hu, Savickas and Wilson, and Augustin et al. were read at abstract or summary level only. Their figures should be checked against the full papers before being quoted in a final report.
- The published 2006 Pan and Poteshman article may differ slightly from the 2004 NBER working paper used here. Recent evidence on these signals in US data, after the growth of retail options trading, was not found. One [2026 master's thesis](https://osuva.uwasa.fi/handle/10024/8919) found no option-to-stock predictability for DAX firms from 2020 to 2025, but it is not a US study and not peer reviewed.
