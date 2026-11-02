# Free trackers of institutional and insider buying from regulatory filings (US stocks)

All checks were made on 2026-10-31 using MSFT as the test stock. No accounts were created and no personal information was entered. Nothing here is a buy or sell recommendation.

Check levels used below:
- **A**: I read the vendor's live page for MSFT (or the vendor's own pricing or FAQ page) and the data was present.
- **B**: I reached a vendor page, but the data did not render in my text-only fetch, or only part of the answer was on the page.
- **C**: The vendor page was blocked or failed, so the information comes from third-party sources or search summaries only.

My fetcher reads text and does not run a full browser, so "not visible in capture" does not mean "not offered". Charts in particular rarely appear in text captures.

## Which sites show who added shares in a named stock over multiple quarters or dates?

### Takeaway
Yes, usable free options exist, but no single free site I could fully verify combines multi-quarter holder history, net shares, new positions, price paid and a chart against price. The strongest verified free combination is 13F.info (quarterly totals since 2014 and manager-by-stock history), Dataroma (per-manager quarterly history since at least 2016), Fintel (latest-quarter buyers, sellers, new and exited positions), and SECForm4 or EDGAR for insiders. HedgeFollow looks closest on features, but its values did not render and its free access is unconfirmed.

### Cited Findings
**13F (institutional) trackers**
- **13F.info (A):** The MSFT CUSIP page lists 13F holders by quarter from 2014 Q1 to 2026 Q3, with number of filings, shares, value and options value, plus 13D/G filers. [13F.info MSFT](https://13f.info/cusip/594918104)
- **13F.info (A):** It also offers period-to-period comparisons and a manager's holding history for a specific stock. It is run by Todd Schneider, the code is on GitHub, and it warns that the SEC has not verified the data. [13F.info home](https://13f.info/)
- **Dataroma (A):** MSFT is held by 37 tracked superinvestors. Each row shows the % of portfolio, shares, value and recent action (such as "Add 25.00%" or "Reduce 11.01%"), with All, Buys, Sells and Insider filters. [Dataroma MSFT](https://www.dataroma.com/m/stock.php?sym=MSFT)
- **Dataroma (A):** The per-manager history page gives quarterly shares, % of portfolio, activity, % change to portfolio and reported price. The Berkshire/AAPL example runs from 2016 Q1 to 2026 Q2. [Dataroma history](https://www.dataroma.com/m/hist/hist.php?f=BRK&s=AAPL)
- **Fintel (A for latest quarter):** MSFT shows 8,318 owners, 4,146 buyers, 3,533 sellers, 614 unchanged, 352 newly reported and 486 exited. Net shares changed +184,003,625. [Fintel MSFT](https://fintel.io/so/us/msft)
- **Fintel source mix:** The holder count mixes 13F filers (6,634 owners, 75.76% of shares) and N-PORT funds (2,148 owners, 24.24%). [Fintel MSFT](https://fintel.io/so/us/msft)
- **MarketBeat (A):** It shows buyer and seller counts, inflows and outflows, and a holder table with quarterly change in shares. Latest reports are dated 10/30 to 10/31/2026. [MarketBeat MSFT](https://www.marketbeat.com/stocks/NASDAQ/MSFT/institutional-ownership/)
- **Yahoo Finance (A):** It lists the top 10 institutional and top 10 mutual fund holders with report dates, and 8,181 institutions holding. It is a snapshot with no history. [Yahoo holders](https://finance.yahoo.com/quote/MSFT/holders/)
- **Stockzoa (A, added alternative):** The free page shows a holder snapshot with % change and notable buyers and sellers. Multi-quarter history is a paid feature. [Stockzoa MSFT](https://stockzoa.com/ticker/msft/)
- **Finviz (A, added alternative):** The quote page shows Inst Own 76.72% and Inst Trans 0.26% as single figures, not holder lists. [Finviz MSFT](https://finviz.com/quote.ashx?t=MSFT)
- **WhaleWisdom (B):** The MSFT page is titled "Microsoft Corporation 13F Hedge Fund and Asset Management Owners", but no holdings data appeared in my capture. [WhaleWisdom MSFT](https://whalewisdom.com/stock/msft)
- **HedgeFollow (B):** The MSFT page has column and chart labels for average buy price, range of average buy prices, buys vs sells, net ownership and a quarter selector (Q2 2026 / Previous). No values rendered. [HedgeFollow MSFT](https://hedgefollow.com/stocks/MSFT)
- **Quiver Quantitative (B):** The MSFT table has columns for Investor, Shares, Change in Shares, Market Value, Date and Reported. No rows rendered. [Quiver MSFT](https://www.quiverquant.com/stock/MSFT/institutions)
- **Stockcircle (B):** The MSFT page shows 2,168 investors holding and names of well-known investors, but dollar figures showed $0 and the insider and congress tables stayed on "Loading". [Stockcircle MSFT](https://stockcircle.com/stocks/msft)

**Insider trackers**
- **SECForm4 (A):** The MSFT page has trade date, reported date/time, relationship, shares, average price, total, shares owned and a filing link, plus a chart image with a time selector. Results run to 16 pages. It also has company tabs for 13D/13G history and institutional holders. [SECForm4 MSFT](https://www.secform4.com/insider-trading/789019.htm)
- **SEC EDGAR ownership view (A):** It lists insiders and each transaction with A/D code, dates, type (S-Sale, A-Award, F-InKind, G-Gift), shares and a Form 4 link. There are no charts. The page itself notes it holds only part of each filing. [EDGAR MSFT](https://www.sec.gov/cgi-bin/own-disp?action=getissuer&CIK=0000789019)
- **Insider Screener (A):** The MSFT table showed notification date, transaction date, type, insider, shares, price and value, from 22 Nov 2024 to 13 Oct 2026. [Insider Screener MSFT](https://www.insiderscreener.com/en/company/microsoft-corp)
- **Yahoo Finance (A):** The insider page shows a 6-month purchases/sales summary, net shares and 50 listed transactions. [Yahoo insider](https://finance.yahoo.com/quote/MSFT/insider-transactions/)
- **Finviz (A):** The insider table shows relationship, date, transaction, cost, shares, value, total shares and a Form 4 link. [Finviz MSFT](https://finviz.com/quote.ashx?t=MSFT)
- **OpenInsider (C):** Third-party reviews describe a free, no-account Form 4 screener with cluster buys (two or more insiders within seven days), filters by type, role and size, and no official API. [HoldingsIntel](https://www.holdingsintel.com/vs/openinsider); [Apify listing](https://apify.com/nexgendata/sec-form4-insider-tracker)

**Free bulk data**
- **SEC Form 13F Data Sets:** Quarterly ZIP files cover July 2013 through August 2026. The SEC says to check original filings before making decisions. [SEC](https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets)
- **SEC Insider Transactions Data Sets:** Quarterly ZIP files cover January 2006 through September 2026. [SEC](https://www.sec.gov/data-research/sec-markets-data/insider-transactions-data-sets)

**Sites disagree on the same stock and quarter**
- Fintel reports net institutional shares of +184.0M, with long institutional shares up 253.01M (+3.69%). [Fintel](https://fintel.io/so/us/msft)
- Yahoo reports net institutional activity of -710,898,791 shares (-12.63%). [Yahoo insider](https://finance.yahoo.com/quote/MSFT/insider-transactions/)
- 13F.info shows 5.39B shares in 2026 Q1 and 9.50B in 2026 Q2. [13F.info](https://13f.info/cusip/594918104)
- MarketBeat's "12-month" inflow and outflow totals ($332.47B and $99.86B) exactly match the dollar totals its FAQ gives for 24 months, and its buyer and seller counts differ between the two sections. [MarketBeat](https://www.marketbeat.com/stocks/NASDAQ/MSFT/institutional-ownership/)
- Vanguard reorganized into two advisers in 2026, and Yahoo now lists Vanguard Capital Management and Vanguard Portfolio Management separately. [Cooley](https://governancebeat.cooley.com/vanguard-will-restructure-into-two-distinct-investment-advisors/); [Yahoo holders](https://finance.yahoo.com/quote/MSFT/holders/)
- 13F.info shows a Vanguard Group 13G/A at 0% (event date 3/13/2026) and Vanguard Capital Management at 7.5% (event date 3/31/2026). [13F.info](https://13f.info/cusip/594918104)

### Inferences
- 13F.info's 9.50B shares for 2026 Q2 cannot be real long ownership. Yahoo's BlackRock line (607.37M = 8.18%) and Fintel's 6.896B = 92.87% both imply about 7.43B shares outstanding. The aggregate is therefore inflated by double counting or filing issues, and the cause is unconfirmed.
- The Vanguard reorganization is a plausible driver of the gap between sites: a holder that changes legal entity can appear as an exit and a new position. This is my inference, not something any site stated.
- Totals are not evidence of direction on their own. Per-manager rows and the actual filing are safer than any "net institutional" headline number.
- For a long-only reader, a manager-by-stock history (13F.info or Dataroma) answers "who actually added" better than an aggregate count of buyers and sellers. Many large holders are index funds, whose changes may reflect fund flows rather than a view on the stock.

### Gaps
- **Nasdaq institutional holdings:** Could not be verified. The page timed out twice, and search returned no Nasdaq-owned description. From prior knowledge only, it shows increased, decreased, new and sold-out position counts. Treat that as unconfirmed.
- **OpenInsider:** Both direct fetches failed, so no first-hand check was made. Its chart features are unconfirmed.
- **GuruFocus:** Both pages tried returned 403, so nothing was checked first-hand.
- **Holdings Channel:** The URL I tried returned 404, so it was not assessed. ValueSider's pricing page returned 403.
- **Dataroma's insider summary:** It shows 23 sells and no buys over six months, but the same capture lists two open-market buys at $397.35 and $377.46. I could not resolve their dates.
- **Blocked pages:** I did not try to get past any block. The pages that returned 403 were left unverified, and a person opening them in a normal browser could settle these items in minutes.

## What is free with no payment, what is locked, and is a signup or card needed?

### Takeaway
Dataroma, 13F.info, SECForm4, EDGAR, and the Yahoo and Finviz tables were readable with no login. WhaleWisdom has a stated free tier limited to about two years of data. Fintel's free account states "No credit card required". Insider Screener has no free plan but its transaction table is still public. HedgeFollow, Quiver, GuruFocus and Stockcircle free limits could not be confirmed from vendor pages.

### Cited Findings
| Tool | Check | Free without paying | Locked or paid | Signup or card |
|---|---|---|---|---|
| WhaleWisdom | A (pricing, FAQ) | 2 years of 13F data, unlimited email alerts, 5-member fund groups, 5-stock watchlists, 2-year backtester ([pricing](https://whalewisdom.com/pricing)). FAQ says the last 9 quarters are free to everyone ([FAQ](https://whalewisdom.com/info/faq)) | Older history, Combined Holdings, WhaleTrader, advanced backtester. Standard $90/qtr, Pro $150/qtr ([pricing](https://whalewisdom.com/pricing)) | Card not stated. "There are no trial accounts" ([pricing](https://whalewisdom.com/pricing)) |
| Fintel | A (MSFT, free page); pricing 403 | Latest-quarter summary visible without login ([MSFT](https://fintel.io/so/us/msft)) | Shares outstanding "Click to Unlock", Fund Sentiment Score "Subscription Required" ([MSFT](https://fintel.io/so/us/msft)). Free accounts exclude premium data, leaderboards and Options Flow ([free](https://fintel.io/free)) | "No credit card required" ([free](https://fintel.io/free)). The signup page title showed a cap of 250 users a month in a search result ([free](https://fintel.io/free)) |
| HedgeFollow | B | Not stated | Level 1 (about a dollar a day per its FAQ) and Level 2 (all fund and insider aggregations, portfolio builder, export). Quarterly or annual billing ([plans](https://hedgefollow.com/plans.php)) | No free tier, trial or card detail on the plans page ([plans](https://hedgefollow.com/plans.php)) |
| Dataroma | A | All pages checked: no paywall, login, or Pro label ([home](https://www.dataroma.com/m/home.php)) | None seen | None seen |
| Yahoo Finance | A | Holders and insider tables visible without sign-in ([holders](https://finance.yahoo.com/quote/MSFT/holders/)) | Insider Sentiment appears to link to a paid tier ([insider](https://finance.yahoo.com/quote/MSFT/insider-transactions/)) | Sign-in only for portfolio features |
| MarketBeat | A | Summary and holder table visible ([MSFT](https://www.marketbeat.com/stocks/NASDAQ/MSFT/institutional-ownership/)) | CSV/Excel export needs All Access; watchlist capped at ten stocks unless upgraded ([MSFT](https://www.marketbeat.com/stocks/NASDAQ/MSFT/institutional-ownership/)) | Login for watchlist |
| Stockcircle | B, pricing 404 | MSFT page partly rendered ([MSFT](https://stockcircle.com/stocks/msft)) | AI earnings summary is Pro-only ([MSFT](https://stockcircle.com/stocks/msft)). Third parties cite $16.49/mo or $99/yr, a limited screener, and one monthly recap email ([FindMyMoat](https://www.findmymoat.com/vs/stockcircle-vs-yahoo-finance); [HoldingsIntel](https://www.holdingsintel.com/vs/stockcircle)) | Follow button leads to sign-up |
| 13F.info | A | All pages checked; no login mentioned ([home](https://13f.info/)) | None seen | None seen |
| SECForm4 | A | Transaction tables visible without a gate ([MSFT](https://www.secform4.com/insider-trading/789019.htm)) | None seen | Sign-up links exist but no gate seen |
| Insider Screener | A | MSFT transaction table ([MSFT](https://www.insiderscreener.com/en/company/microsoft-corp)) | Volume chart, filters, sorting, signals, top insiders ([MSFT](https://www.insiderscreener.com/en/company/microsoft-corp)). No free tier listed; Plus is CA$23/mo or CA$179/yr ([pricing](https://www.insiderscreener.com/en/pricing)) | No login prompt seen for the table |
| GuruFocus | C (403) | Third parties say a limited free tier: 3 portfolios of up to 25 stocks and 100 API requests a month ([StockUnlock](https://stockunlock.com/gurufocus-review.html); [FindMyMoat](https://www.findmymoat.com/vs/gurufocus-vs-wallstreetzen)) | Paid from $499 to $549/yr, sources conflict ([StockUnlock](https://stockunlock.com/gurufocus-review.html); [FindMyMoat](https://www.findmymoat.com/vs/gurufocus-vs-wallstreetzen)) | Not confirmed |
| Quiver Quantitative | B (pricing shows signup page) | Not stated. Many datasets carry no Premium label ([site](https://www.quiverquant.com/pricing)) | Premium nav includes Alerts, Screener, Institutional Holdings Backtester and Export Data ([site](https://www.quiverquant.com/pricing)). Insider trades on the price line are Premium ([MSFT](https://www.quiverquant.com/stock/MSFT/institutions)) | Account needed to sign up; card not stated ([site](https://www.quiverquant.com/pricing)) |
| OpenInsider | C | Free, no account per reviewers ([HoldingsIntel](https://www.holdingsintel.com/vs/openinsider)) | None reported | None reported |
| SEC EDGAR | A | Everything; free government data ([EDGAR view](https://www.sec.gov/cgi-bin/own-disp?action=getissuer&CIK=0000789019)) | None | None seen |
| Stockzoa | A | Latest snapshot ([MSFT](https://stockzoa.com/ticker/msft/)) | History, charts and raw data back to 2004: $48/qtr or $160/yr ([MSFT](https://stockzoa.com/ticker/msft/)) | Login to subscribe or download |
| Finviz | A | Insider table appears visible without login ([MSFT](https://finviz.com/quote.ashx?t=MSFT)) | Charts and alerts link to Elite, from $24.96/mo ([MSFT](https://finviz.com/quote.ashx?t=MSFT)) | Sign-up is optional for the table |

### Inferences
- The only no-login, full-history free 13F sources I verified are 13F.info, Dataroma and the SEC's own data. Everything else trims history, charts or export.
- WhaleWisdom's "2 years" and "last 9 quarters" look like two wordings of nearly the same limit, but the two pages do not match exactly.
- Fintel's free page copy states a monthly cap, so signup may not always be available. That cap may also be a marketing device; I could not tell.

### Gaps
- **Fintel paid prices:** Unconfirmed. Third-party sources conflict ($14.95/mo on [NexusFi](https://nexusfi.com/d/data-providers/fintel/), about $20/mo billed yearly on [FindMyMoat](https://www.findmymoat.com/vs/fintel-vs-wall-st-rank)).
- **HedgeFollow prices and free scope:** Not on the plans page text. Whether average buy price is free is unknown.
- **Quiver prices:** The pricing URL returned a signup page and the search found no reliable figure. A "50% off, ends September 7" banner still showed, which suggests stale page content.
- **GuruFocus free scope for guru trades:** Unconfirmed.
- **13F.info conflict:** A third-party search summary said sign-up is required ([FindMyMoat](https://www.findmymoat.com/free/alternatives/13f-info)), but the site's own pages showed no such requirement. I rely on the site.
- **Dataroma conflict:** The same third-party summary mentioned a paid Pro tier. Dataroma's home page mentions none. I rely on the site, though I cannot rule out unlisted features.
- **ValueSider:** A third-party summary says a free Basic plan includes five years of history ([FindMyMoat](https://www.findmymoat.com/free/alternatives/13f-info)). The vendor page returned 403, so this is unconfirmed.

## Does each show quarterly ownership history for one stock, net shares, new positions and average price, and is it charted against price?

### Takeaway
Multi-quarter history for one stock is verified free on 13F.info (totals) and Dataroma (per manager). Fintel verifies net shares and new positions, for the latest quarter only. Average price is only labeled on HedgeFollow, WhaleWisdom and GuruFocus. Charts against price exist in labels on Fintel and HedgeFollow, but I could not view them in text captures.

### Cited Findings
| Tool | Quarterly history for one stock | Net shares bought or sold | New positions | Average price | Chart vs price |
|---|---|---|---|---|---|
| WhaleWisdom | Free tier about 2 years ([pricing](https://whalewisdom.com/pricing)); stock page not rendered | Not confirmed | Not confirmed | Estimated Avg Price, per FAQ ([FAQ](https://whalewisdom.com/info/faq)) | Not confirmed |
| Fintel | Latest quarter only in capture ([MSFT](https://fintel.io/so/us/msft)) | Yes, latest quarter | Yes, 352 new and 486 exited | Not shown | Ownership vs price chart described, data not captured |
| HedgeFollow | Quarter selector ([MSFT](https://hedgefollow.com/stocks/MSFT)) | Labeled | Labeled ("New"/"Closed" filters) | Labeled, with range | "Average buy prices vs current price" labeled; no data seen |
| Dataroma | Yes, per manager ([history](https://www.dataroma.com/m/hist/hist.php?f=BRK&s=AAPL)) | Per manager, not aggregate | "Buy" action ([MSFT](https://www.dataroma.com/m/stock.php?sym=MSFT)) | Reported Price and Hold Price only | No embedded chart; links to TradingView |
| Yahoo Finance | No ([holders](https://finance.yahoo.com/quote/MSFT/holders/)) | One net figure ([insider](https://finance.yahoo.com/quote/MSFT/insider-transactions/)) | No | No | No |
| MarketBeat | "Buying and Selling by Quarter" section, chart data not captured ([MSFT](https://www.marketbeat.com/stocks/NASDAQ/MSFT/institutional-ownership/)) | Inflows and outflows in dollars; per-holder change | N/A entries only | No | Not confirmed |
| Stockcircle | Not confirmed | Not confirmed | Not confirmed | Not shown ([MSFT](https://stockcircle.com/stocks/msft)) | None in capture |
| 13F.info | Yes, 2014 Q1 onward ([MSFT](https://13f.info/cusip/594918104)) | Compute from totals; comparison pages exist ([home](https://13f.info/)) | Via comparison pages | No | None confirmed |
| SECForm4 | Insider history; institutional tab not tested | Per trade | N/A | Actual reported price ([MSFT](https://www.secform4.com/insider-trading/789019.htm)) | Insider chart image |
| Insider Screener | Insider table from Nov 2024 in capture | Per trade | N/A | Actual reported price | Chart paywalled ([MSFT](https://www.insiderscreener.com/en/company/microsoft-corp)) |
| Quiver | Not confirmed | "Change in Shares" column, rows empty ([MSFT](https://www.quiverquant.com/stock/MSFT/institutions)) | Not confirmed | No | Price chart only; overlay of insider trades is Premium |
| SEC EDGAR | Full filings | Compute it | Compute it | Form 4 price in the filing | None ([view](https://www.sec.gov/cgi-bin/own-disp?action=getissuer&CIK=0000789019)) |
| Stockzoa | Paid ([MSFT](https://stockzoa.com/ticker/msft/)) | % change snapshot | Unclear "100%" entries | No | Paid |

- 13F.info's table has no explicit change column on the CUSIP page, so changes must be calculated from the listed values. [13F.info MSFT](https://13f.info/cusip/594918104)

### Inferences
- For a chart of holdings against price with free tools, the verified route is manual: take quarterly rows from Dataroma or 13F.info and plot them against a price series. No fully confirmed free one-click chart turned up.
- Fintel and HedgeFollow are the two to open in a browser first, since both name that chart.

### Gaps
- Whether Fintel's and HedgeFollow's charts load without an account is unconfirmed.
- Whether WhaleWisdom's stock page shows new, added, reduced and sold-out counts to free users is unconfirmed.
- GuruFocus and OpenInsider could not be scored here. Nasdaq also could not be scored.

## 13F lag and limits, Form 4 timing, and 13D or 13G for big stakes

### Takeaway
13F is a delayed quarter-end snapshot of long US-listed positions with no trade dates or prices, due 45 days after quarter-end. Form 4 is far fresher, generally two business days, and gives actual prices. Schedules 13D and 13G flag stakes above 5% on shorter timelines for some filers since the 2023 amendments.

### Cited Findings
**Form 13F**
- Managers with investment discretion over $100M or more in Section 13(f) securities must file. Individuals investing only their own money are excluded. [SEC FAQ](https://www.sec.gov/rules-regulations/staff-guidance/division-investment-management-frequently-asked-questions/frequently-asked-questions-about-form-13f)
- Reports are due within 45 days after quarter-end, and the SEC grants no extensions. [SEC FAQ](https://www.sec.gov/rules-regulations/staff-guidance/division-investment-management-frequently-asked-questions/frequently-asked-questions-about-form-13f)
- 2026 due dates are May 15, Aug 14 and Nov 16, and Feb 16, 2027 for the fourth quarter. [SEC FAQ](https://www.sec.gov/rules-regulations/staff-guidance/division-investment-management-frequently-asked-questions/frequently-asked-questions-about-form-13f)
- Only securities on the Official List count: mainly US exchange-traded stocks, closed-end funds and ETFs, plus some convertibles, options and warrants. Mutual funds are not reported. [SEC FAQ](https://www.sec.gov/rules-regulations/staff-guidance/division-investment-management-frequently-asked-questions/frequently-asked-questions-about-form-13f)
- Short positions are not reported and may not be netted against longs. Written options are excluded. [SEC FAQ](https://www.sec.gov/rules-regulations/staff-guidance/division-investment-management-frequently-asked-questions/frequently-asked-questions-about-form-13f)
- Small positions can be omitted if under both 10,000 shares and $200,000. [SEC FAQ](https://www.sec.gov/rules-regulations/staff-guidance/division-investment-management-frequently-asked-questions/frequently-asked-questions-about-form-13f)
- Confidential treatment can be requested, typically for risk arbitrage or ongoing acquisition or disposition programs, for 3, 6, 9 or 12 months initially, justified security by security. A denied or expired request requires an amendment within six business days. [SEC FAQ](https://www.sec.gov/rules-regulations/staff-guidance/division-investment-management-frequently-asked-questions/frequently-asked-questions-about-form-13f)
- Positions are aggregated at the manager level, not the fund level, and the SEC does not require a filer to state what type of filer it is. [Angelini et al.](http://wp.lancs.ac.uk/fofi2020/files/2020/04/FoFI-2020-090-Farouk-Jivraj.pdf)
- Quarterly long-only data cannot show short positions or intra-quarter changes. [Angelini et al.](http://wp.lancs.ac.uk/fofi2020/files/2020/04/FoFI-2020-090-Farouk-Jivraj.pdf)
- Fintel reports an average reporting lag of 37 days on MSFT. [Fintel MSFT](https://fintel.io/so/us/msft)
- WhaleWisdom says filings appear within an hour of SEC release, and stats pages update 1 to 2 days after the deadline. [WhaleWisdom FAQ](https://whalewisdom.com/info/faq)

**Form 4 and related**
- Officers, directors and holders of more than 10% of a class must report. [SEC bulletin, 2013](https://www.sec.gov/files/forms-3-4-5.pdf)
- Form 3 is due within 10 days of becoming an insider. Form 4 is due within two business days after the transaction. Form 5 is generally due 45 days after fiscal year-end for unreported or exempt items. [SEC bulletin, 2013](https://www.sec.gov/files/forms-3-4-5.pdf)
- Form 4 shows the amount and price per share. Key codes are P (purchase), S (sale), A (award), F (tax or exercise payment), M (exercise) and G (gift). [SEC bulletin, 2013](https://www.sec.gov/files/forms-3-4-5.pdf)
- The SEC bulletin notes insiders may sell for many reasons, including liquidity and diversification. [SEC bulletin, 2013](https://www.sec.gov/files/forms-3-4-5.pdf)

**Schedules 13D and 13G**
- Holders of more than 5% of a covered class must file. Control-intent investors file 13D; qualified institutional, exempt and passive investors file 13G. [SEC fact sheet](https://www.sec.gov/files/33-11253-fact-sheet.pdf)
- 13D: initial filing within five business days (was 10 days), amendments within two business days. [SEC fact sheet](https://www.sec.gov/files/33-11253-fact-sheet.pdf)
- 13G for qualified institutional and exempt investors: initial filing 45 days after the quarter-end in which ownership exceeds 5% (was 45 days after year-end). [SEC fact sheet](https://www.sec.gov/files/33-11253-fact-sheet.pdf)
- 13G for passive investors: initial filing within five business days (was 10 days). [SEC fact sheet](https://www.sec.gov/files/33-11253-fact-sheet.pdf)
- 13G amendments: generally 45 days after the quarter of a material change, with faster deadlines for qualified and passive investors crossing 10% or moving by 5%. [SEC fact sheet](https://www.sec.gov/files/33-11253-fact-sheet.pdf)
- Revised 13G deadlines took effect Sept 30, 2024. Structured data was required from Dec 18, 2024. [SEC press release](https://www.sec.gov/newsroom/press-releases/2023-219)

### Inferences
- A purchase on the first day of a quarter may stay hidden for about 138 days. For example, Jul 1 to the Nov 16, 2026 deadline is 138 days (calculated by me).
- As of Oct 31, 2026, 2026 Q3 13F data is partial. 13F.info shows 2,982 Q3 filings against 6,672 for Q2, with the deadline on Nov 16. Q2 is the last full quarter, so "latest" net-buying views should be read with that in mind.
- A 13F increase can reflect a change in the mix of a multi-strategy manager rather than a single decision, because long positions may hedge shorts, options or other exposures that are not shown.
- On insider data, filter for code P. Awards (A) and tax withholding (F) are not market buying or selling decisions.
- Yahoo's "Purchases" of 513,644 shares across 16 transactions likely includes awards, given EDGAR's list of A-Award entries and Dataroma's six-month count of no buys. This is inferred, not stated by Yahoo.

### Gaps
- The Form 4 source is a 2013 SEC bulletin. A search of recent SEC-hosted documents repeated the two-business-day rule, but I did not read the current Rule 16a-3 text.
- I did not confirm the exact current deadlines for the accelerated 13G amendments. The fact sheet only describes them generally.

## Which tools show the estimated price range where a manager bought?

### Takeaway
HedgeFollow is the closest match by label ("Range of Average Buy Prices"), but no values rendered and its free access is unconfirmed. WhaleWisdom gives a single estimate and calls it a guess. No 13F tool can show a real price paid, since 13F has no trade prices. Only Form 4 gives real prices, for insiders.

### Cited Findings
- **HedgeFollow (B):** The MSFT page labels "Average Buy Price", "Price History", "Range of Average Buy Prices" and a chart of "average buy prices vs. current price". [HedgeFollow MSFT](https://hedgefollow.com/stocks/MSFT)
- **WhaleWisdom (A on method):** "Estimated Avg Price uses the stock price at the quarter end date to determine the average price paid", adjusted for past transactions. It calls this "just a guesstimate" because the fund could have bought at any point in the quarter. [WhaleWisdom FAQ](https://whalewisdom.com/info/faq)
- **GuruFocus (C):** Tutorial and add-in documentation describe a field for the average share price for the quarter and another for the highest price for the quarter. [GuruFocus tutorial](https://www.gurufocus.com/tutorial/article/134/gurug-guru-trades)
- **GuruFocus caveat:** It describes guru trades as an idea-generation and research tool, not automatic signals. [GuruFocus tutorial](https://www.gurufocus.com/tutorial/article/134/gurug-guru-trades)
- **Dataroma (A):** It shows a quarterly Reported Price, and a Hold Price defined as the last known price at which an investor still held a security, using quarter-end dates. It shows no range. [Dataroma MSFT](https://www.dataroma.com/m/stock.php?sym=MSFT); [Dataroma history](https://www.dataroma.com/m/hist/hist.php?f=BRK&s=AAPL)
- **Insiders:** SECForm4 lists average price per trade and Finviz lists cost per trade, both from Form 4. [SECForm4](https://www.secform4.com/insider-trading/789019.htm); [Finviz](https://finviz.com/quote.ashx?t=MSFT)
- **13Range (C):** A third-party product listing says it estimates buy, hold and sell price bands on daily charts, with estimated average-cost ranges, because 13F shows only quarter-end holdings. Its cost and accuracy are unverified. [Hunted.space listing](https://hunted.space/dashboard/13range)

### Inferences
- A free do-it-yourself range works with verified tools: find a quarter with a share increase on Dataroma or 13F.info, then read that quarter's high and low from any price chart. That bracket is the widest plausible range for the added shares, assuming the manager held throughout. It is not a price paid.
- Any 13F "average price" is modeled from quarterly data. It should be presented as an estimate, and it is least reliable in quarters with large price moves.
- A manager can buy and sell within a quarter and show no net change, so a range can only cover the net change.

### Gaps
- HedgeFollow's method for calculating its range was not found.
- I found no official GuruFocus definition of a "Price Range" column, and could not view the page.
- I could not confirm that any tool in the list gives a price range for free, other than the manual method.

## Is there evidence that following 13F or insider purchases works, and does it survive the filing delay?

### Takeaway
Evidence is stronger for insider purchases than for 13F cloning, especially opportunistic rather than routine insiders, and the strongest headline insider result is a long-short portfolio rather than buy-only. 13F evidence is mixed: lagged cloning can match or modestly beat benchmarks with careful manager selection, while filing-date copycatting has been found to add little long-term value. Most results pre-date 2020, and transaction costs are often not fully included.

### Cited Findings
**Insider trades**
- **Cohen, Malloy, Pomorski (*Journal of Finance* 67(3), 2012), sample and method:** Data run from January 1986 to December 2007. Routine traders are those who traded in the same calendar month for several prior years, and insiders need three consecutive years of history to be classified. [Paper](https://dash.harvard.edu/server/api/core/bitstreams/7312037e-2b77-6bd4-e053-0100007fdf3b/content)
- **Cohen et al., main result:** Opportunistic buys minus opportunistic sells earns 82 basis points a month value-weighted (9.8% annualized, t=2.15) and 180 basis points equal-weighted (21.6%, t=6.07). Routine trades earn -20 basis points value-weighted (t=-0.57). [Paper](https://dash.harvard.edu/server/api/core/bitstreams/7312037e-2b77-6bd4-e053-0100007fdf3b/content)
- **Cohen et al., buys alone:** Opportunistic buys yield an incremental 90 basis points in the next month relative to all insider trades (t=4.64), against 14 basis points for routine buys (t=0.81). [Paper](https://dash.harvard.edu/server/api/core/bitstreams/7312037e-2b77-6bd4-e053-0100007fdf3b/content)
- **Cohen et al., delay:** Median reporting was 3 days. Rerunning returns from the 11th of the next month gave "virtually identical" results, which the authors call "fully tradable in real-time". [Paper](https://dash.harvard.edu/server/api/core/bitstreams/7312037e-2b77-6bd4-e053-0100007fdf3b/content)
- **Cohen et al., size:** Opportunistic trades predict returns for both large and small stocks. [Paper](https://dash.harvard.edu/server/api/core/bitstreams/7312037e-2b77-6bd4-e053-0100007fdf3b/content)
- **Lakonishok and Lee (NBER WP 6656, 1998):** All NYSE, Amex and Nasdaq firms, 1975 to 1995. Market moves around trades and SEC reports are small, predictive power comes mainly from smaller firms, and purchases are more informative than sales. [RePEc](https://ideas.repec.org/p/nbr/nberwo/6656.html)
- **Jeng, Metrick, Zeckhauser:** Insiders' purchase portfolios earned about 40 basis points a month, sales earned no significant abnormal return, and top executives did not beat other insiders. This measures returns to insiders rather than outsiders who copy them. [NBER WP 6913](https://www.nber.org/papers/w6913)
- **Costs (secondary):** A recent paper's literature review says Rozeff and Zaman (1988) found the anomaly largely explained by size and earnings/price effects after costs, and Lin and Howe (1990) concluded costs prevent outsiders from profiting. [arXiv 2602.06198](https://arxiv.org/html/2602.06198v2)
- **Speed (search snippet only):** A 2024 *Finance Research Letters* paper buys at VWAP within 30 minutes of publication and finds positive percentage but negative USD abnormal returns, before costs. The page was blocked, so its market and sample are unconfirmed. [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S1544612324015435)

**13F and holdings cloning**
- **Brown and Schwarz:** Press summaries say trading spiked around 13F filing dates, but copycat portfolios gave no long-term benefit over similar stocks. I did not read the abstract. [NYU Stern news](https://www.stern.nyu.edu/experience-stern/news/stephen-brown-ft-1-14); [SSRN](https://doi.org/10.2139/ssrn.1683628)
- **Frank, Poterba, Shackelford, Shoven (*JLE* 2004):** After expenses, copycat mutual funds were statistically indistinguishable from active funds and possibly ahead, in a limited 1990s sample of high-expense funds. [Journal page](https://www.journals.uchicago.edu/doi/10.1086/422982); [NBER w8653](https://nber.org/papers/w8653)
- **Verbeek and Wang (*JBF* 2013):** 3,046 US equity funds, with copycats built on a 60-day lag. Performance was comparable to targets after costs and expenses, relative success rose after 2004 quarterly disclosure, and copying past winners did best. [RePEc](https://ideas.repec.org/a/eee/jbfina/v37y2013i9p3454-3471.html); [CFA digest](https://rpc.cfainstitute.org/research/cfa-digest/2013/11/better-than-the-original-the-relative-success-of-copycat-funds-digest-summary)
- **Cohen, Polk, Silli ("Best Ideas"):** Managers' highest-conviction positions beat the market by roughly 2.8% to 4.5% a year, depending on the benchmark. This is a holdings-based study and the figure comes from secondary reports. [Citywire](https://citywire.com/ch/news/why-managers-should-only-buy-5-stocks-and-why-they-shouldn-t/a2392538); [Substack](https://behindthebalancesheet.substack.com/p/do-best-ideas-really-work)
- **Angelini, Iqbal, Jivraj (2019 working paper):** Rebalancing 47 days after quarter-end, a hedge-fund conviction-and-consensus strategy beat the S&P 500 by 3.80% a year (May 2004 to June 2019), with a Sharpe ratio of 0.75 and six-factor alpha of 0.32% a month. [Paper](http://wp.lancs.ac.uk/fofi2020/files/2020/04/FoFI-2020-090-Farouk-Jivraj.pdf)
- **Angelini et al., selection matters:** The alpha was -0.003% and insignificant for other hedge funds. The manager grouping uses proprietary Novus data. The authors are from Barclays and Novus, and quantitative funds were expected to suffer "significant alpha decay" from the lag. [Paper](http://wp.lancs.ac.uk/fofi2020/files/2020/04/FoFI-2020-090-Farouk-Jivraj.pdf)
- **Agarwal, Jiang, Tang, Yang (*Journal of Finance* 2013):** Confidential positions are driven mainly by private information and show superior performance for up to twelve months. They appear late through 13F amendments. [RePEc](https://ideas.repec.org/a/bla/jfinan/v68y2013i2p739-783.html); [Columbia](https://business.columbia.edu/faculty/research/uncovering-hedge-fund-skill-portfolio-holdings-they-hide)
- **Restatements (search snippet):** A study reports 13.43% annualized abnormal return from the original filing to the restatement date, read as strategic misreporting by some managers. [Working paper](https://academicweb.nd.edu/~zda/Restatement.pdf)
- **Decay (secondary):** Quantpedia notes a significant decline in 13F cloning's abnormal returns after the 2008 crisis. Treat its 21% historical backtest figure with caution. [Quantpedia](https://quantpedia.com/strategies/alpha-cloning-following-13f-fillings)

### Inferences
- Form 4's two-day lag leaves far less time for the signal to fade than 13F's lag of up to about 138 days, which fits the stronger insider evidence, though the studies differ too much to compare directly.
- 13F evidence suggests that who you copy matters more than the fact of copying. Headline "net institutional buying" for a stock such as MSFT is not what those studies tested.
- Opportunistic insider signals are not one filter on the free tools. A free approximation is code P purchases by insiders with no same-calendar-month pattern, which would need manual checking over three years or more.
- For very large stocks like MSFT, Lakonishok and Lee point to weaker aggregate signals, while Cohen et al. find opportunistic signals work in both large and small stocks. These can both hold, since they test different things, but evidence for a specific large-cap filing should not be overread.
- Past results do not guarantee future results, and published anomalies can shrink after publication. Nothing here shows that following filings produces reliable profits today.

### Gaps
- I found no study testing Form 4 mimicry by retail investors, net of full costs, on recent US data. A keyword search of extracted text found no transaction-cost discussion in the Cohen et al. paper version I read, and no net-of-cost figure in Angelini et al. Text extraction is imperfect, so this is not conclusive.
- I read Cohen et al. and Angelini et al. directly. Lakonishok and Lee, Jeng et al., Frank et al., Verbeek and Wang, and Agarwal et al. are from abstracts or summaries. Brown and Schwarz, Best Ideas and the restatement study are from secondary sources or snippets.
- The published version of Lakonishok and Lee (*Review of Financial Studies*, 2001) was not retrieved; I used the NBER abstract.
- I found no reliable post-2020 evidence that isolates 13F cloning after the filing date. A 2025 vendor analysis from Equibles exists, but I did not assess it.
