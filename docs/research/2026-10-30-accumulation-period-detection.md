# Detecting a period of large-player activity (not a single week): research notes

Access date for all web documents: 2026-10-30. Author: Scout research pass for `whale-watch`.

Evidence labels used throughout:
- **Verified**: I read the source text (API response, official page, spec, or full paper text) in this session.
- **Abstract only**: I reached only an abstract, catalogue record or search-result summary of the source.
- **Unverified**: not read in this session; do not rely on it.
- **Mine**: my own arithmetic or interpretation, not a claim from a source.

Items that change often (flagged **[volatile]**): FINRA API history window, Alpaca plan limits, vendor free tiers, SEC rule dates, index reconstitution dates.

---

## 1. Bottom line

1. **Detect a period with a window scan, not a point test.** Run a likelihood-ratio / max-window scan over the existing robust-z series (weekly block-venue share; later a daily series). Search windows of about 2 to 12 weeks (weekly series) or 5 to 40 trading days (daily series). Report start, end and strength of the best window. Get its p-value by resampling the same ticker's own history in blocks, so the autocorrelation stays. Use PELT (`ruptures`) only as a cross-check. Why: a window scan answers "when did it start and end" directly, and the max-over-windows p-value is what controls false alarms (Section 4; the false-alarm inflation from autocorrelation is Mine, Section 6).
2. **Add a daily layer from Reg SHO daily short sale volume files, used for timing only.** They are free, keyless, published the same day by 18:00 ET, and the files reach back to 2018-08-01 (Q1 below). They cover only off-exchange (TRF/ADF) volume and give no direction, so they give day-level resolution of total off-exchange activity, not of who is buying. Short volume must not be read as bearish (FINRA's own notice, Section 1).
3. **Word the output as "elevated large-order activity", never "accumulating".** Block-venue share and total volume carry no buy/sell sign. Signed flow needs trade-level prints plus a classifier, and even then the accuracy evidence for free data is weak (Section 3). The 13F, 13D/G and Form 4 records that could confirm direction arrive weeks later (Section 5).
4. **Expect multi-week periods to look like persistent weak excess, not one spike.** Public metaorder data show single orders finishing within a day (ANcerno: median about 35 minutes; AQR: horizon under one day on average and at most three), while same-direction order flow stays correlated for weeks (autocorrelation timescale about 26 days). A "period" is therefore a run of overlapping orders. A detector tuned to one huge week will miss it (Section 2).
5. **Define confidence operationally, not as a probability of institutional presence.** Three numbers: (a) block-bootstrap p-value of the best window, (b) FDR-adjusted across tickers scanned, (c) the detector's recall at that window length, taken from an injection test on real history. Do not print "80% confident institutions bought" because no ground truth exists to calibrate that (Sections 5 and 6).
6. **Validate in three tiers, and claim only what each tier supports.** Tier A: null calibration (false-alarm rate on the real history with block resampling). Tier B: synthetic injection of known shifts into real series (power curve). Tier C: weak external labels (13D/13G within 5 business days, Russell reconstitution dates, 13F quarter changes). Tier C needs about 95 independent labelled episodes per group to detect a precision lift from 15% to 30% (Mine, Section 6). Use Harvey-Liu-Zhu's t > 3.0 as the bar if many parameters get tuned.
7. **Decide the EDGAR contact question before building labels.** SEC fair access wants a declared User-Agent with a contact; the SEC's sample includes an email. That is a decision for the owner (for example a dedicated project mailbox). No keyless, contact-free route to 13F/13D data was confirmed (Section 5).
8. **Data-depth trap.** The FINRA API serves only about the last 365 days of `regShoDaily` (first available date was 2025-10-30 when I probed). For history, use the CDN files, which reach 2018-08-01 (checked for ORCL).

---

## 2. Findings by question

### Q1. Free daily data (FINRA)

**Dataset and metadata.** (Verified, called 2026-10-30)
- `GET https://api.finra.org/metadata/group/otcMarket/name/regShoDaily` returned `datasetName: REGSHODAILY`, description "Reg SHO Daily File", `partitionFields: ["tradeReportDate"]`.
- Fields in metadata: `tradeReportDate` (yyyy-MM-dd), `securitiesInformationProcessorSymbolIdentifier` (symbol), `shortParQuantity` ("executed short sale and short sale exempt trades during regular trading hours"), `shortExemptParQuantity`, `totalParQuantity` ("all executed trades during regular trading hours"), `marketCode`, `reportingFacilityCode`.
- Mismatch between docs and data (Verified): metadata says `reportingFacilityCode` values are N, Q, B, D. Live rows return `reportingFacilityCode` = `NYTRF` / `NQTRF` / `NCTRF` and put B/Q/N in `marketCode`. Code against the data, not the description.
- `shortParQuantity` includes the short-exempt trades, so `shortExemptParQuantity` is a subset, per the field description (Verified).
- Quantities can be fractional (for example ORCL 2026-10-21 NQTRF `totalParQuantity` 1.0448869621039E7, NCTRF 168103.422253). Parse as float (Verified, live rows).

**Sample query for ORCL** (Verified, 2026-10-30). POST to `https://api.finra.org/data/group/otcMarket/name/regShoDaily` with body `{"limit":5000,"compareFilters":[{"compareType":"EQUAL","fieldName":"securitiesInformationProcessorSymbolIdentifier","fieldValue":"ORCL"},{"compareType":"GREATER","fieldName":"tradeReportDate","fieldValue":"2025-10-01"}]}`.
- Returned 756 rows = 252 trading days x 3 facilities, 2025-10-30 to 2026-10-30.
- Summed across facilities, ORCL short share of TRF volume ranged 12.6% to 60.4%, median 35.5%. TRF total volume per day ranged 4.40M to 50.2M shares, median 11.1M (Mine, computed from the rows). The short ratio is a noisy series.
- ORCL's 2026-10-30 row was already in the API at about the end of that trading day, which agrees with FINRA's same-day publication promise.
- Sorting requires an EQUAL filter on the partition key `tradeReportDate`; otherwise HTTP 400 (Verified, error text).

**History depth.** (Verified)
- API: ORCL queries for dates up to 2025-10-27 returned HTTP 204 (no content); from 2025-10-30 returned 200. Date 2018-08-01 via API gave 204. FINRA's page says the grid shows "The last 365 days" ([FINRA short sale volume page](https://www.finra.org/finra-data/browse-catalog/short-sale-volume-data)). **[volatile]**: window rolls daily.
- CDN files: `https://cdn.finra.org/equity/regsho/daily/CNMSshvol[YYYYMMDD].txt` (pattern per [FINRA daily files page](https://www.finra.org/finra-data/browse-catalog/short-sale-volume-data/daily-short-sale-volume-files)). I fetched `CNMSshvol20180801.txt` and found `20180801|ORCL|2884353|365|5832120|Q,N`, so history reaches 2018-08-01, matching the page ("Consolidated NMS: August 1, 2018").
- File format (Verified): `Date|Symbol|ShortVolume|ShortExemptVolume|TotalVolume|Market`. 2026-10-29 ORCL row: `5527127.772940|26227|16807406.660177|B,Q,N`.
- Other prefixes on the page: `FNQC`, `FNSQ`, `FNYX` (per-TRF), `FNRA` (ADF), `FORF` (ORF).

**Publication time.** FINRA posts files "no later than 6:00:00pm ET of the same day"; files "may occasionally be updated on a later day" and are labelled "Updated" (Verified, daily files page). Plan for revisions.

**What TotalVolume does and does not cover.** (Verified)
- Only trades reported to a FINRA TRF, the ADF or the ORF during normal market hours. That is off-exchange volume (dark pools and market-maker internalisation, including retail wholesalers). Volume executed on exchanges is not in these files; exchanges publish their own short volume ([FINRA Information Notice 05/10/19](https://www.finra.org/rules-guidance/notices/information-notice-051019), as summarised by the search tool; the notice itself states the data "includes only trades that are publicly disseminated" and is published separately per facility and exchange, "not consolidated").
- To get a total-market ratio you must add exchange volume from another source. Not checked: whether exchange-published short volume files are free and keyless. **Not confirmed.**
- The ATS weekly data and this file overlap: ATS volume is a subset of TRF-reported volume (Mine, from structure; not checked numerically).

**Why short volume is not a simple bearish signal.**
- FINRA's notice (Verified): the file "does not-and is not intended to-equate to reported bi-monthly short interest"; excluding non-disseminated offsetting trades "may result in the appearance of a higher concentration of short sale to total volume"; in the notice's example a firm facilitating a customer sale "may elect to first sell an equivalent number of shares", which prints as a short sale.
- Rule text (Verified via [Cornell LII 17 CFR 242.200](https://www.law.cornell.edu/cfr/text/17/242.200)): "A broker or dealer must mark all sell orders of any equity security as 'long,' 'short,' or 'short exempt.'" Market makers' sales are marked like anyone's (the section has no market-maker carve-out). [17 CFR 242.203(b)(2)(iii)](https://www.law.cornell.edu/cfr/text/17/242.203) exempts "short sales effected by a market maker in connection with bona-fide market making activities" from the locate requirement, so market-making inventory shorts are routine and uninformative about direction.
- Academic angle: Boehmer, Jones and Zhang, "Which shorts are informed?", Journal of Finance 63(2), 2008, 491-527, found some shorts informed. **Abstract not retrieved; citation only (Unverified content).** Whatever it says, the FINRA TRF file mixes all short types, so it cannot isolate the informed ones (Mine).

**Other relevant FINRA API datasets confirmed by metadata calls** (all under group `otcMarket`, Verified 2026-10-30):
- `weeklySummary` (partitions `weekStartDate`, `tierIdentifier`), `monthlySummary` (partitions `monthStartDate`, `tierIdentifier`), `blocksSummary` (partition `monthStartDate`).
- `consolidatedShortInterest`: description says OTC equity short interest, "available online for one rolling year based on the settlement date"; fields include `currentShortPositionQuantity`, `daysToCoverQuantity`, `averageDailyVolumeQuantity`. Note the description says it concerns OTC equity securities, so it may not cover ORCL (Mine: not queried for ORCL).
- `thresholdList` (partition `tradeDate`): Reg SHO threshold securities (13 consecutive settlement days of fail-to-deliver). Rarely relevant to large-cap names.
- The generic listing endpoints `/metadata`, `/metadata/group` returned 404; names must be known in advance. The same dataset name under group `equity` returned 404 for `consolidatedShortInterest`.
- [FINRA developer catalog](https://developer.finra.org/catalog) lists Alternative Display Facility, Blocks Summary, Monthly Summary, Weekly Summary under Equity (anchor IDs only; no API names).

**Access terms and limits.** (Verified, [FINRA developer docs](https://developer.finra.org/docs))
- Sync requests: 1,200 per minute per IP; up to 5,000 records and 3 MB per request; default `limit` 1,000; `offset` max 500,000. HTTP 429 above limits.
- Individual accounts are limited to Public and Mock credentials and are "not intended for commercial purposes at this time." My calls were keyless. [FINRA fees page](https://developer.finra.org/fees): Public credentials $0; Equity access marked "Limited" without defined limits. **Whether keyless access is intended to continue indefinitely is not confirmed** [volatile].
- The Reg SHO developer page ([link](https://developer.finra.org/docs/reg-sho-daily-short-sale-volume)) lists the dataset path as `regShoDailyMock`; production `regShoDaily` worked in my calls anyway.

**Design implication.** A daily series of TRF volume (and its ratio to a tier-appropriate baseline) is available for about 8 years via files and 1 year via API. Without exchange volume it cannot express "share of dark volume", so use it as an activity-level timing aid next to the weekly block-venue share, not as a replacement.

---

### Q2. Institutional order physics

| Source | What it establishes | Label |
|---|---|---|
| Zarinelli, Treccani, Farmer, Lillo (2015), "Beyond the square root: evidence for logarithmic dependence of market impact on size and participation rate", [arXiv:1412.2152](https://ar5iv.labs.arxiv.org/html/1412.2152) | ANcerno data, Jan 2007 to Dec 2009: 28,386,564 metaorders before filters, 6,944,883 after four filters. Metaorders are defined as completed within one trading day; filter keeps orders longer than 2 minutes. In a subset of 703,497, 368,484 last 0 to 10 minutes. Daily fraction pi = Q/V_D spans over five orders of magnitude; for top-20 stocks "around 5% of the daily volume". Participation eta >= 0.3 excluded; power-law fit exponent about -0.86 for 1e-4 <= eta <= 0.1. Impact curve fit: power law RMSE about 6.70 (Y about 0.15, delta about 0.47) vs logarithmic RMSE about 2.80. After completion price decays to "remarkably close to (though slightly higher than) 2/3 of the peak impact"; low-participation long metaorders stay higher, the largest participation relaxes toward zero in the window. | Verified (first 100k of 122k characters read) |
| Bucci, Benzaquen, Lillo, Bouchaud (2019, PRL 122, 108302), "Crossover from linear to square-root market impact", [arXiv:1811.05230](https://ar5iv.labs.arxiv.org/html/1811.05230) | About 8M ANcerno metaorders, 880 trading days Jan 2007 to Jun 2010, about 5% of total market volume. "The median execution time of the metaorders in our sample is 35 minutes." Impact linear for phi = Q/V_d below about 1e-3, about square-root for 1e-3 to 1e-1. | Verified |
| Bucci, Benzaquen, Lillo, Bouchaud (2019, Market Microstructure and Liquidity 4, 1950006), "Slow decay of impact in equity markets", [arXiv:1901.05332](https://ar5iv.labs.arxiv.org/html/1901.05332) | Impact at end of execution day about 2/3 of peak (ratio 0.66 +/- 0.04). Next-day close about 4/5 of end-of-day impact (zeta about 0.80). Deconvolved long-run asymptote about 0.42 +/- 0.01 of end-of-day-one impact (about 1/2 rounded, at about 50 days); authors warn it is hard to pin down. Metaorder sign autocorrelation across days fit by an exponentially truncated power law with timescale about 26 days. Metaorder = "jointly reported executions of a single investor, through one broker within one day". | Verified |
| Lillo, Mike, Farmer (2005, Phys. Rev. E), "Theory for long memory in supply and demand", [arXiv:cond-mat/0412708](https://ar5iv.labs.arxiv.org/html/cond-mat/0412708) | Order splitting plus power-law hidden order sizes gives long memory in order signs: decay exponent gamma = alpha - 1. LSE, 20 stocks, May 2000 to Dec 2002, 16.7M trades. Measured gamma averages 0.57 +/- 0.05. | Verified |
| Toth, Palit, Lillo, Farmer, "Why is equity order flow so persistent?", [arXiv:1108.1632](https://ar5iv.labs.arxiv.org/html/1108.1632) | LSE member-coded order data, six stocks, June 2000 to June 2009. On timescales under a few hours persistence is "overwhelmingly due to splitting rather than herding"; the authors do not dispute herding at lower frequencies. Signs correlated out to "many days". Journal year not read here. | Verified |
| Frazzini, Israel, Moskowitz, "Trading Costs of Asset Pricing Anomalies", NBER conference draft Dec 2012, [PDF](https://conference.nber.org/conf_papers/f68262/f68262.pdf) | One large institutional manager, nearly $1 trillion of live trades, 1998 to 2011, 19 developed markets. "The average realized trade horizon for completion is less than one day and no more than three days." Algorithm randomises child-order size and timing. The 2018 SSRN version ([abstract](https://papers.ssrn.com/abstract=3229719)) is reported to use a larger sample; I did not read it. | Verified (2012 draft); Abstract only (2018) |
| Toth et al. (2011, Phys. Rev. X 1, 021006), "Anomalous price impact and the critical nature of liquidity", [arXiv:1105.1694](https://arxiv.org/abs/1105.1694v3) | Dynamical liquidity theory behind square-root impact. | Abstract only |
| Kyle and Obizhaeva (2016, Econometrica 84(4), 1345-1404), "Market Microstructure Invariance: Empirical Hypotheses", [IDEAS](https://ideas.repec.org/a/wly/emetrp/v84y2016i4p1345-1404.html) | Bet-size and cost invariance, tested on over 400,000 portfolio-transition orders. | Abstract only |
| Keim and Madhavan (1995, JFE 37(3), 371-398), "Anatomy of the trading process" | 21 institutions; examines "determinants of trade duration"; days to fill recorded. No duration numbers retrieved. [UPenn record](https://repository.upenn.edu/fnce_papers/383) returned 403. | Abstract only (via search summaries) |
| Chan and Lakonishok (1995, J. Finance 50(4), 1147-1174), "The behavior of stock prices around institutional trades", [IDEAS](https://ideas.repec.org/a/bla/jfinan/v50y1995i4p1147-74.html) | Abstract: managers with strong demand for immediacy tend to have larger impact. The "package" (multi-day trade sequence) framing comes from the 1993 working paper (403 when fetched). I could not obtain package durations or sizes. | Abstract only; numbers **not confirmed** |

**What this changes for the design.**
- Single metaorders are intraday (median 35 minutes in ANcerno; AQR average under one day, at most three). A period "from 12 May to 6 June" is a sequence of such orders from one or several investors, linked by the multi-day sign persistence (timescale about 26 days, Bucci 2019b). The scan's window range of 2 to 12 weeks matches that scale, but the 26-day figure is one dataset's fit (US institutional clients of one TCA provider, 2007-2010).
- Participation: ANcerno metaorders are mostly small relative to daily volume (phi mostly 1e-3 to 1e-1; "around 5%" for top-20 stocks in Zarinelli). A campaign is a small-fraction-of-volume effect that is hard to see in total volume, which supports scoring the share on block venues (volume-independent) rather than volume itself.
- Price path: impact builds during execution, about 2/3 remains at day end, and a permanent part persists for weeks (about half of day-one end impact at around 50 days, with uncertainty). So price is **not** a clean marker of campaign start and end, and a full reversal after completion should not be expected. The Zarinelli paper adds that for the largest participation rates impact relaxes toward zero, so reversal depends on style.
- Caveat: ANcerno records are institutional client orders via TCA reporting. They show how orders behave, not how often such orders land on FINRA dark pools or block venues (Mine). Nothing found links the weekly ATS counts to these metaorders.

---

### Q3. Inferring institutional flow from public data

| Method | What it needs | Accuracy evidence found | Works on free data? | Label |
|---|---|---|---|---|
| Campbell, Ramadorai, Schwartz (2009, JFE 92(1), 66-91), "Caught on tape" | TAQ trade sizes calibrated to predict 13F changes; infers daily institutional trading. Finds institutional trading persistent, short-run losses on sells, long-run profits, anticipation of earnings surprises. Differs from a simple trade-size cutoff. | No accuracy figure retrieved. | Needs trade-by-trade data with sizes (TAQ-like). Alpaca delayed SIP prints could supply trades (Section 7); quote data and calibration against 13F not tested. | Abstract only ([IDEAS](https://ideas.repec.org/a/eee/jfinec/v92y2009i1p66-91.html)) |
| Boehmer, Jones, Zhang, Zhang (2021, J. Finance), "Tracking retail investor activity" (BJZZ); Barber, Huang, Jorion, Odean, Schwarz (2024, J. Finance 79(4), 2403-2427) | Subpenny price improvement on off-exchange prints flags retail. | Barber et al. SSRN abstract, via search summary: 85,000 retail trades in six brokerage accounts, Dec 2021 to Jun 2022; original algorithm flagged about 35% of their trades as retail, mislabeled 28% of those it flagged, and gave uninformative order-imbalance measures for 30% of stocks; midpoint signing cut signing error to about 5%. | Needs sub-penny prices from prints. Identifies **retail**, not institutions. Using "not retail" as "institutional" is unsupported (Mine). | Abstract only ([SSRN 4202874](https://papers.ssrn.com/abstract=4202874)) |
| Lee and Ready (1991, J. Finance 46(2), 733-746); tick rule | Trades plus prevailing quotes (LR) or trades only (tick). | Chakrabarty, Pascual, Shkilko (2015, J. Financial Markets 25, 52-79) report TR and LR classify more accurately than BVC for stocks of all sizes ([IDEAS](https://ideas.repec.org/a/eee/finmar/v25y2015icp52-79.html)). | Yes, at print level (needs `prints` mode). Cannot be done on daily or weekly aggregates. | Abstract only |
| Bulk volume classification and VPIN: Easley, Lopez de Prado, O'Hara (2012, RFS 25(5), 1457-1493) | Volume bars of trades; assigns buy/sell share from price change. | Andersen and Bondarenko (2014, J. Financial Markets 17, 1-46): VPIN a poor volatility predictor, record high only after the Flash Crash, predictive power from a mechanical relation with trading intensity ([IDEAS](https://ideas.repec.org/p/aah/create/2011-50.html), working-paper abstract). Easley et al. rejoinder (2014, same journal 17, 47-52) says AB "attack a methodology we do not advocate" ([IDEAS](https://ideas.repec.org/a/eee/finmar/v17y2014icp47-52.html)). | Possible on prints, but contested, and BVC loses to the tick rule per Chakrabarty et al. | Abstract only |
| Hendershott and Riordan (2013, JFQA 48(4), 1001-1024), "Algorithmic trading and the market for liquidity" | German exchange order data. | Concerns algorithmic traders' liquidity supply/demand, not identification of institutional parents. Relevance here is low. | n/a | Abstract only (partial) |

**Bottom line for Q3.** No source retrieved shows a free-data method that identifies institutional parents of orders with a stated accuracy on current US markets. The best-documented inference tools are (a) retail flagging by subpenny prints (about 35% recall, 28% error per Barber et al.), and (b) trade-sign classification at print level (tick/Lee-Ready better than BVC). Neither reads weekly ATS totals. Status of any "institutional" label from this tool: inference from structure, not measurement.

**Informed or institutional trading in dark pools.**
- Comerton-Forde and Putnins (2015, JFE 118(1), 70-92), "Dark trading and price discovery": non-block dark trades are less informed than lit trades; high levels harm informational efficiency; "no evidence that block trades in the dark impede price discovery" ([IDEAS](https://ideas.repec.org/a/eee/jfinec/v118y2015i1p70-92.html), via search summary). Abstract only. Implication (Mine): the block-venue share is the right region to look for large-order informed activity, and the ordinary dark share is not.
- Zhu (2014, RFS 27(3), 747-789), "Do dark pools harm price discovery?": theory; informed traders prefer the exchange and uninformed prefer dark pools, so high dark share does not imply informed trading ([MIT DSpace](https://dspace.mit.edu/handle/1721.1/88124)). Abstract only; a model, not data.
- Menkveld, Yueshen, Zhu (2017, JFE 124(3), 503-534), "Shades of darkness": pecking order; patient institutions use low-cost, low-immediacy dark venues and move to lit venues when urgent. **Verified from paper text**: the data are Nasdaq TRF transactions split into five dark categories (DarkMid, DarkNMid, DarkRetail, DarkPrintB, DarkOther) for 117 US stocks in October 2010 (21 trading days), a proprietary Nasdaq classification, not FINRA ATS weekly data; they note FINRA's weekly volumes "are not on a trade by trade basis" ([paper](https://www.mit.edu/~zhuh/MenkveldYueshenZhu_2017JFE_dark.pdf)).
- Studies using the FINRA weekly ATS data (Verified, paper text read): Brogaard and Pan (2019 draft, later RFS), "Dark trading and the fundamental information in stock prices" use "weekly trading volume on dark pools from FINRA's ATS Transparency Data" since May 2014 ([PDF](https://sites.insead.edu/facultyresearch/research/file.cfm?fid=64858)); Buti, Rindi, Werner (2022 draft), "Diving into dark pools" use weekly FINRA OTC Transparency data for 2020 and note data "are only available weekly, and we expect to have less power" ([PDF](https://didattica.unibocconi.it/mypage/upload/48636_20220131_034055_DIVING_FINAL_SSRN_20220130.PDF)). Both address market-quality and price-informativeness questions, not detection of individual institutional campaigns.
- **I found no paper that tests whether FINRA weekly ATS or monthly block-venue figures detect specific institutional orders.** My search was limited to a few queries, so absence is not proof.

---

### Q4. Finding a period rather than a point

See the method comparison table in Section 4. Summary of the evidence:
- PELT: exact multiple-change-point search with cost "linear in the number of observations" under mild conditions, "more accurate segmentations than Binary Segmentation" (Killick, Fearnhead, Eckley 2012, JASA 107(500), 1590-1598, [arXiv:1101.1438](https://arxiv.org/abs/1101.1438); abstract only).
- Dependence matters. Lavielle and Moulines (2000, J. Time Series Analysis 21(1), 33-59) treat least-squares shift estimation under mixing conditions (abstract only, [IDEAS](https://ideas.repec.org/a/bla/jtsera/v21y2000i1p33-59.html)). Chakar, Lebarbier, Levy-Leduc, Robin (2017, Bernoulli 23(2), 1408-1447, [arXiv:1403.1958](https://arxiv.org/pdf/1403.1958)): with AR(1) noise the dynamic-programming result for independent data no longer applies directly; they estimate the AR parameter robustly and plug it in; "accounting for dependence improves performance at finite sample sizes". Abstract only (via search summary).
- BOCPD (Adams and MacKay 2007, [arXiv:0710.3742](https://arxiv.org/abs/0710.3742)): online posterior over run length. Abstract only.
- Truong, Oudre, Vayatis (2020, Signal Processing 167, 107299), "Selective review of offline change point detection methods", [arXiv:1801.00718](https://arxiv.org/abs/1801.00718): organises methods as cost + search + constraint, ships the `ruptures` package. Abstract only.
- Kulldorff (1997, Communications in Statistics - Theory and Methods 26, 1481-1496), "A spatial scan statistic": likelihood-ratio over windows with Monte Carlo critical values; the space-time variant (Kulldorff et al. 1998) addresses "preselection bias and multiple testing" ([SaTScan references](https://www.satscan.org/references.html), [PMC1509064](https://pmc.ncbi.nlm.nih.gov/articles/PMC1509064)). Abstract / secondary only. The 1-D time-only version is a direct special case (Mine).
- CUSUM (Page 1954, Biometrika) and Hamilton (1989, Econometrica) regime-switching: cited from memory; **Unverified**, not retrieved.

**`ruptures` status** (Verified, 2026-10-30; [PyPI JSON](https://pypi.org/pypi/ruptures/json), [GitHub API](https://api.github.com/repos/deepcharles/ruptures), [docs](https://centre-borelli.github.io/ruptures-docs/user-guide/detection/pelt/)):
- Latest stable release 1.1.10 (uploaded 2025-09-10); a 1.1.11rc1 pre-release exists (2025-11-27). Earlier: 1.1.9 (2023-12-11).
- License BSD-2-Clause. Python requirement on PyPI: `>=3.9,<3.14`, so the stable release declares no support for Python 3.14.
- Repository not archived, last push 2026-10-06, about 2,104 stars, 48 open issues.
- `Pelt(model=..., min_size=..., jump=...)`, penalty `pen` passed to `predict`. Cost classes listed: CostL1, CostL2, CostNormal, CostRbf, CostCosine, CostLinear, CostCLinear, CostRank, CostMl, CostAR, custom. Docs state average complexity O(CKn) "under certain conditions on the change point repartition", and that `l2` is "significantly faster than linear or autoregressive models".
- The docs page I read does not describe penalty selection or autocorrelation handling. The standard penalties assume independent noise within segments (Mine, consistent with Chakar et al.).
- Dependencies (numpy, scipy) add weight; a window scan is about 30 lines of numpy (Mine).

---

### Q5. Ground truth for validation

| Record | Resolution | Lag | Access | Label usefulness for a multi-week period |
|---|---|---|---|---|
| **13F-HR** | Quarter-end long positions of managers with at least $100M in 13(f) securities; no trade dates in the quantity reported | "Each filing is due within 45 days after the end of the calendar quarter"; the $100M test is applied monthly ([SEC 13F FAQ](https://www.sec.gov/divisions/investment/13ffaq), Verified); confidential treatment possible for programs of acquisition or disposition | EDGAR (fair access) | Weak for dating: change in quarter-end holdings over a quarter says the net direction over about 13 weeks; cannot place start/end within the quarter. Long-only; short positions excluded ("report only the long position"). Best as a quarterly sign check. |
| **13D / 13G** | Events at crossing 5% (and later changes) | 13D initial: five business days after acquiring more than 5%; 13D amendment: two business days after material change; 13G passive investors: five business days; 13G QIIs and exempt investors: 45 days after the quarter-end in which ownership exceeded 5%; QIIs over 10%: five business days after month-end (Verified, [SEC Release 33-11253](https://www.sec.gov/files/rules/final/2023/33-11253.pdf), effective Feb 5, 2024; compliance dates in section II.G not read) | EDGAR; structured XML data now required (same release) | Good for dating one large buyer's crossing of 5%, rare for mega-caps like ORCL. 13D in particular marks a purchase span ending at the filing; 13G QII filings come up to 45 days late, so they are poor timing labels. |
| **Form 4** | Insider transaction by date | "before the end of the second business day" ([17 CFR 240.16a-3(g)(1)](https://www.law.cornell.edu/cfr/text/17/240.16a-3), Verified via LII) | EDGAR; OpenInsider (third-party, worked without email per owner) | Insiders and 10% holders only. A cluster of insider buying is a label for insider activity, not institutional. Daily resolution. |
| **Form 144** | Notice of proposed sale by affiliates | Filed "concurrently with either the placing with a broker of an order... or the execution directly with a market maker" ([17 CFR 230.144(h)(3)](https://www.law.cornell.edu/cfr/text/17/230.144), Verified via LII); threshold over 5,000 shares or $50,000 in any three-month period; electronic on EDGAR since 2023-04-13 ([SEC filer pages](https://www.sec.gov/submit-filings/filer-support-resources/how-do-i-guides/file-form-144-electronically), search summary) | EDGAR | Sell-side, affiliates only; same-day. Useful as a "supply" confounder to mark in a period, not as a label for institutional buying. |
| **N-PORT** | Fund portfolio holdings | Public lag currently: stated as 60 days after quarter end in a search summary, **Unverified** from an SEC primary. SEC extended compliance dates for the 2023 N-PORT amendments to 2027-11-17 (funds with $10bn or more) and 2028-05-18 ([SEC release page](https://www.sec.gov/rules-regulations/2026/02/s7-16-22), Verified) | EDGAR | Registered funds only (mutual funds, ETFs). Coarse. Not useful for dating a period. |
| **Issuer repurchases (10-Q / 10-K Item 703)** | Monthly aggregates per quarter | Filing lag of the 10-Q/10-K. The SEC's 2023 amendments that would have required daily reporting were vacated by the Fifth Circuit on 2023-12-19; Item 703 monthly disclosure remains (law-firm summaries only, e.g. [Jenner & Block](https://www.jenner.com/print/v2/content/63347/client-alert-fifth-circuit-court-of-appeals-vacates-the-secs-share-repurchase-disclosure-modernization-rule-amendments.pdf); no SEC primary read) | EDGAR | A known large non-institutional buyer (the issuer). Monthly resolution; a useful label for an "issuer bid" period; a confounder otherwise. |
| **Secondary offerings** | Pricing date and size | Prospectus supplements same day or next | EDGAR | Supply events; dates are exact (rule details Unverified; not retrieved). |
| **Index reconstitution** | Exact effective dates, with large predictable closing-auction volume | Announced weeks ahead. Russell US 2026: June reconstitution effective after close 2026-06-26; second one moved to after close 2026-12-11 (search summaries of [LSEG pages](https://www.lseg.com/en/ftse-russell/russell-reconstitution)). **[volatile]** | Public LSEG/FTSE Russell pages | Gives dated, known heavy-trading days and pre-announced flows (index funds). They are mostly one-day closing-auction events, so they validate day-level volume timing but are not multi-week accumulation. S&P rebalance dates not checked. |

**EDGAR access rules** (Verified, [SEC "Accessing EDGAR Data"](https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data)):
- "Current max request rate: 10 requests/second." The SEC may lower it.
- Scripts should declare a User-Agent; sample format given: "Sample Company Name AdminContact@<sample company domain>.com".
- "The SEC does not allow botnets or automated tools to crawl the site."
- Submissions and extracted XBRL data are offered as JSON on `data.sec.gov`; bulk daily archives exist under Feed and Oldloads directories.
- During this research one of my plain `curl` requests to sec.gov (a generic UA string, no email) returned the SEC page "Request Rate Threshold Exceeded". I made no further requests to sec.gov. This is consistent with the owner's earlier 403.

**Free alternative to EDGAR that needs no personal contact?** Not confirmed. I found no primary source describing a contact-free route to 13F, 13D/G or Form 4 data.
- OpenInsider covers Form 4 only (owner's test; its terms not reviewed).
- Options for the owner to weigh (Mine): put a project name and a dedicated role mailbox in the UA, which fits the SEC's own sample format without exposing a personal address.
- Whether the SEC accepts a UA without any email was not tested by me and the owner saw 403 without one.

**What cannot be validated** is listed in Section 5.

---

### Q6. Validation method

Recommended plan (the choices are Mine; the supporting sources are cited):

1. **Null calibration (Tier A).** For each ticker, resample its own history with a dependence-preserving bootstrap and run the full detector. Check the false-alarm rate matches the nominal level. Use the stationary bootstrap of Politis and Romano (1994, JASA 89(428), 1303-1313; random block length, geometric, mean 1/p; abstract via search summary) with blocks chosen by Politis and White (2004, Econometric Reviews 23(1), 53-70; corrected by Patton, Politis, White 2009). Python: the `arch` package provides `StationaryBootstrap`, and `RealityCheck`, `SPA` and `StepM` ([source](https://raw.githubusercontent.com/bashtage/arch/main/arch/bootstrap/multiple_comparison.py), Verified class names; version 8.0.0 released 2025-10-21, [PyPI](https://pypi.org/pypi/arch/json); licence field was empty in PyPI metadata, check before depending on it).
   - Why: with AR(1) noise of coefficient phi, the variance of a window mean is inflated by about (1+phi)/(1-phi), so an i.i.d. threshold understates the cutoff by sqrt of that factor. At phi = 0.5 the factor is 3 (z inflated by about 1.7). Effective sample size is about n(1-phi)/(1+phi). **Mine, standard result; not simulated here (numpy was not installed in this environment).** Measure phi on the real z-series first.
2. **Injection test (Tier B).** Add a known shift (for example +1, +1.5, +2 robust-sd for 4, 8, 12 weeks) at random positions to real histories. Report recall, and start/end error, as a function of shift size and duration. This is the only test that can give honest "how confident" numbers about the detector itself, and it needs no labels. It does not prove the real world contains such shifts (Mine).
3. **Event study on weak labels (Tier C).** Event study logic: align detected windows to dated records (13D/G filing, Russell reconstitution weeks, issuer-bid months) and compare hit rates with matched control windows from the same tickers, same calendar weeks, flagged-free. MacKinlay 1997 is the standard event-study reference (**Unverified**, not retrieved). Counts must be of independent episodes (non-overlapping), not weeks.
4. **Walk-forward.** Freeze parameters (window range, penalty, thresholds) using an early period, then score a later period untouched. Keep the 2026 data out of design choices until the end. Because FINRA data is weekly with a 3-week lag, report both "as-of" detection date and the true window dates.
5. **Data-snooping.** Every tuned knob (window range, sensitivity, venue list) is a hypothesis. If more than a handful are tried, test the best against the whole set with White's Reality Check (White 2000, Econometrica 68(5), 1097-1126; IDEAS record has no abstract, [link](https://ideas.repec.org/a/ecm/emetrp/v68y2000i5p1097-1126.html)) or SPA/StepM from `arch`, and consider Harvey, Liu, Zhu's t-ratio hurdle "above 3.0" for a newly discovered factor ([NBER w20592](https://www.nber.org/papers/w20592), Oct 2014, RFS 2016; abstract). HLZ is about asset-pricing factors, so applying t > 3.0 here is analogy (Mine).
6. **Across-ticker multiplicity.** Scanning N tickers means about 0.05N false windows at 5%. Control with Benjamini-Hochberg FDR (**Unverified**; reference not retrieved) or pre-register one threshold from Tier A.

**Sample sizes (Mine, standard two-proportion formula, one-sided alpha 0.05, power 0.80):**
- To distinguish a hit rate of 30% among flagged periods from a base rate of 15% among control periods: about 95 independent flagged periods and about 95 controls. For 25% vs 15%: roughly 200 each (Mine, rounded; recompute with real base rates).
- Daily series: n_eff ~ n(1-phi)/(1+phi). With 252 days and phi = 0.5, n_eff ~ 84.
- Null calibration: at least 1,000 resamples per ticker for a 5% level, more for FDR at lower levels.
- Injection: at least 200 injections per (shift, duration) cell for recall estimates within about +/- 5 percentage points.

Honest limit: with labels available only for stocks with filings, the number of independent labelled periods in a year across a watch list of tens of stocks may be well below 95. If so, report only Tiers A and B and state Tier C as inconclusive.

---

### Q7. Intraday data

**Alpaca Basic (free) plan** (Verified, [About Market Data API](https://docs.alpaca.markets/docs/about-market-data-api), 2026-10-30) **[volatile]**:
- Real-time equities source: IEX exchange only. Equities WebSocket: 30 symbols. Historical API calls: 200 per minute. Historical data limitation: "latest 15 minutes".
- Algo Trader Plus ($99/month): all US exchanges, unlimited WebSocket symbols, 10,000 historical calls per minute, no historical restriction.
- [Market Data FAQ](https://docs.alpaca.markets/us/docs/market-data-faq) (Verified): free plan has live data only from IEX; querying recent SIP data without a subscription returns "subscription does not permit querying recent SIP data"; "For historical queries, the `end` parameter must be at least 15 minutes old to query SIP data without a subscription." So the README's "free plan SIP, 15+ minutes delayed" matches the docs.
- [Historical stock data page](https://docs.alpaca.markets/docs/historical-stock-data-1): feed parameter values iex, sip, boats, overnight; iex is "the only feed that can be used without a subscription" (this wording conflicts with the FAQ's allowance of old SIP data; the FAQ is the more specific statement). Historical depth and pagination limits **not confirmed**.
- Alpaca terms for free data (redistribution, non-professional use): the [disclosures page](https://alpaca.markets/disclosures) only links to Nasdaq and NYSE agreements; text not read. **Not confirmed.**

**Exchange code `D`.** (Verified) alpaca-py's `Exchange` enum documents `D (str): FINRA ADF` ([source](https://raw.githubusercontent.com/alpacahq/alpaca-py/master/alpaca/data/enums.py)). The CTS Pillar multicast output specification v2.11b (January 29, 2026) lists Participant ID `D` = "FINRA Alternative Display Facility (ADF)" ([CTA spec](https://www.ctaplan.com/publicdocs/ctaplan/CTS_Pillar_Output_Specification.pdf)). The same spec has a separate "Trade Reporting Facility ID" field. **Not confirmed**: whether Alpaca reports TRF-printed (dark/off-exchange) trades as `D`. It plausibly does because FINRA prints appear under the FINRA participant (Mine). Test with a real key on a known ticker before using `D` as an "off-exchange" filter.

**Conditions endpoints** (Verified, Alpaca reference pages):
- `GET https://data.alpaca.markets/v2/stocks/meta/conditions/{ticktype}?tape=` with `ticktype` in `trade`, `quote` and `tape` in `A`, `B`, `C`. Returns an object mapping code to name (example `"@": "Regular Sale"`). Needs an API key.
- `GET /v2/stocks/meta/exchanges` returns the exchange code mapping (needs key; I did not call it).
- Condition handling from the FAQ (Verified): `B` Average Price Trade (tapes A, B), `W` Average Price (C, O), `T` Extended Hours, `I` Odd Lot, `F` Intermarket Sweep, `4` Derivatively Priced, `V` Contingent Trade, `X` Cross Trade, `P` Prior Reference Price, `7` Qualified Contingent Trade. Average-price, odd-lot, contingent and prior-reference trades add to volume but not to VWAP or high/low. For block detection, condition codes should be filtered before counting a print as a block (Mine): average-price and prior-reference prints are not executions at the printed time.

**Other free trade data.**

| Source | What | Limits found | Terms | Label |
|---|---|---|---|---|
| FINRA Reg SHO CDN files | Daily off-exchange total and short volume | None found beyond CDN etiquette; keyless | Footer links to FINRA terms of use; not read | Verified (files); terms **not confirmed** |
| IEX HIST ([IEX page](https://iextrading.com/trading/market-data/)) | IEX-only DEEP (and TOPS) pcap files | "available for download on a T+1 basis"; pcap format | "IEX Historical Data Terms of Use" linked, not read. IEX is one venue's flow only (share of volume not confirmed). Cost not confirmed. | Partly verified |
| Massive (formerly Polygon) free Basic plan | End-of-day aggregates | Search summaries report 5 calls per minute, 2 years history, EOD only. The pricing page I fetched did not show the Basic plan. | Not read | **Unverified** [volatile]; no tick data on the free tier per those summaries |
| TAQ / CRSP / Databento etc. | Full tick data | Paid | n/a | Not investigated |

I did not examine Yahoo, Stooq, or other scraped sources; their terms generally disallow automated use and I did not verify them.

---

## 3. Data inventory

| Source | Resolution | Lag | Cost | Key needed | What it measures |
|---|---|---|---|---|---|
| FINRA `weeklySummary` (`ATS_W_SMBL`, `_FIRM`, `ATS_W_VOL_STATS`) | Week, per ticker per ATS | Tier 1 about 3 weeks; market totals about 35 days (owner's stated facts) | Free | No (used keyless) | Dark-pool dollars and shares per ticker and venue |
| FINRA `blocksSummary` | Month, per ATS, no ticker | About 64 days (owner's fact) | Free | No | Share of each ATS's business in $200K+ trades |
| FINRA Reg SHO daily (API `regShoDaily`) | Day, per ticker per TRF/ADF | Same day, by 18:00 ET | Free | No (used keyless) | Off-exchange short and total volume, regular hours; last 365 days only |
| FINRA Reg SHO daily (CDN files) | Day, per ticker | Same day, by 18:00 ET; may be updated later | Free | No | Same, back to 2018-08-01 |
| FINRA `consolidatedShortInterest` | Settlement date (twice monthly per FINRA rule), OTC equities per its description | Not checked | Free | No (metadata call only) | Short interest; one rolling year; probably OTC-only |
| Alpaca `prints` (SIP, history) | Trade-by-trade | End time must be at least 15 minutes old | Free (Basic) | Yes (free account) | Consolidated prints with exchange and condition codes; never run live in this repo |
| Alpaca IEX real-time | Trade-by-trade, IEX only | Real time | Free | Yes | One venue's flow |
| SEC 13F | Quarter-end positions | Up to 45 days after quarter | Free | UA with contact | Long holdings of managers over $100M |
| SEC 13D/13G | Event (5% crossing) | 13D 5 business days; 13G 5 business days to 45 days | Free | UA with contact | Large holders and changes |
| SEC Form 4 / OpenInsider | Day | 2 business days | Free | UA (SEC) / none (OpenInsider, per owner) | Insider trades |
| SEC Form 144 | Day | Concurrent with order | Free | UA with contact | Affiliate sale notices |
| SEC N-PORT | Quarter | About 60 days (Unverified) | Free | UA with contact | Fund holdings |
| 10-Q / 10-K Item 703 | Month | Report filing lag | Free | UA with contact | Issuer buybacks |
| Russell / index reconstitution schedules | Exact dates | Announced ahead | Free | No | Known heavy-trading days |

---

## 4. Method comparison (Question 4)

Series assumed: robust-z of weekly block share (about 150 weeks, 3 years) or daily TRF measure (about 250 to 750 days, mean-shifting in a window then reverting).

| Method | Finds start and end of a bounded episode? | Handles autocorrelation? | False-alarm control | Simplicity for a small Python tool | Fit |
|---|---|---|---|---|---|
| CUSUM (Page 1954; Unverified, not retrieved) | One-sided drift detection, online; end not natural | Poor unless prewhitened | Average run length, tuned by simulation | Very simple | Good as an alarm; weak for retrospective start/end |
| Binary segmentation | Yes, greedy, approximate | Poor | Penalty or fixed number of changes | Simple | Killick et al. report PELT more accurate (abstract) |
| PELT (Killick 2012) via `ruptures` (BSD-2) | Yes, optimal for a penalised cost; episodes are two change points | Assumes independent noise within segments for standard costs; AR cost exists but is slower; Chakar et al. show dependence-aware penalties help | Penalty choice; no p-value; calibrate with block bootstrap | Easy to call; adds numpy/scipy; penalty tuning is the hard part | Good cross-check |
| BOCPD (Adams and MacKay 2007) | Online posterior of run length; end needs extra logic | Model dependent | Posterior threshold; no frequentist error rate | Moderate; needs a hazard rate and predictive model | Good for live updating, poor for dated windows |
| Hidden Markov regime model (Hamilton 1989; Unverified) | Gives regime probability by period | Can model | Likelihood-ratio tests nonstandard | Moderate; `hmmlearn` 0.3.3 exists (PyPI); fits with 150 points are unstable and label switching occurs (Mine) | Not recommended at this sample size |
| Scan statistic (Kulldorff 1997; time-only special case) | Yes: best window start, end, strength directly | Via resampling null that preserves dependence | Monte Carlo p-value of the max over windows; multiple tickers need FDR | Simple: about 30 lines | **Recommended primary** |

**Recommendation.** Scan statistic with block-bootstrap null as the primary detector. PELT with a calibrated penalty as an independent cross-check; report an episode only when both agree on overlap, or label it "scan-only". Keep BOCPD for later if the tool becomes live. All fit conclusions here are Mine; no source I retrieved compared these methods on financial volume series of this length.

---

## 5. What cannot be known from public data

- **Who traded.** FINRA data carries no buyer or seller identity and no sign. A period of high block-venue share can be buying, selling, hedging, an index flow or market-maker inventory (Mine).
- **Whether a block-venue share rise reflects institutional parents.** No paper found validates the weekly ATS or monthly block-share measure against known institutional orders. The owner's tests show the share is independent of volume and price, but not that it reflects institutions.
- **Exact timing of a campaign.** 13F has quarter resolution; 13D/G exists only above 5%; Form 4 and Form 144 cover insiders and affiliates. There is no public dated record of a typical institution's purchases within a quarter.
- **Start and end dates of campaigns by managers below disclosure thresholds, and any short or derivative exposure.** 13F excludes short positions and below-threshold managers.
- **Which venue a dark print came from, per trade.** The public tape shows facility, not ATS. Weekly ATS totals give ticker by ATS by week only.
- **Causation of price moves.** Impact studies show about 2/3 of peak impact retained at day end and a persistent part afterwards, so price paths cannot separate a campaign from news.
- **Calibrated "confidence that institutions accumulated."** Without labelled campaigns, only the detector's statistical properties (Tiers A and B) can be quantified.
- **Current accuracy of free trade-sign methods on today's market.** Cited accuracy numbers come from older samples or abstracts I did not read in full.

---

## 6. Not confirmed (consolidated)

- Chan and Lakonishok package durations and sizes; Keim and Madhavan trade durations (abstract-level only; the working-paper PDFs returned 403).
- Frazzini-Israel-Moskowitz 2018 published-version figures (only the 2012 draft was read).
- Campbell-Ramadorai-Schwartz accuracy against 13F (abstract only).
- Contents of BJZZ, Comerton-Forde and Putnins, Zhu, Hendershott and Riordan beyond abstract summaries; Boehmer-Jones-Zhang (2008) abstract.
- Page (1954), Hamilton (1989), MacKinlay (1997), Benjamini-Hochberg: cited from memory.
- Whether exchange-published short volume files are free and keyless; consolidated-volume source for a total-market short ratio.
- FINRA keyless-access permanence and the terms of use for CDN files.
- Whether Alpaca labels TRF off-exchange prints with exchange code `D`; SIP history depth; free-plan data terms; the `exchanges` endpoint output (needs key).
- Massive/Polygon free tier details from a primary source; IEX HIST terms and cost.
- N-PORT current public-disclosure lag from an SEC primary; Fifth Circuit/Item 703 status from an SEC primary; SEC Form 144 electronic-filing page (search summary only); S&P rebalance dates.
- SEC acceptance of a contact-free User-Agent; any contact-free route to 13F/13D data.
- Whether `consolidatedShortInterest` covers ORCL (description says OTC securities).
- Any study that links FINRA weekly ATS or block-share measures to specific institutional campaigns (none found in a limited search).

---

## 7. Sources

FINRA (accessed 2026-10-30):
- Metadata: https://api.finra.org/metadata/group/otcMarket/name/regShoDaily ; .../name/weeklySummary ; .../name/blocksSummary ; .../name/monthlySummary ; .../name/consolidatedShortInterest ; .../name/thresholdList
- Data: POST https://api.finra.org/data/group/otcMarket/name/regShoDaily
- Daily files page: https://www.finra.org/finra-data/browse-catalog/short-sale-volume-data/daily-short-sale-volume-files
- CDN files: https://cdn.finra.org/equity/regsho/daily/CNMSshvol20180801.txt, .../CNMSshvol20261029.txt
- Short sale volume page: https://www.finra.org/finra-data/browse-catalog/short-sale-volume-data
- Information Notice 05/10/19: https://www.finra.org/rules-guidance/notices/information-notice-051019
- Developer docs: https://developer.finra.org/docs ; fees: https://developer.finra.org/fees ; catalog: https://developer.finra.org/catalog ; Reg SHO page: https://developer.finra.org/docs/reg-sho-daily-short-sale-volume
- File layout PDF (binary, not text-extracted): https://www.finra.org/sites/default/files/2021-07/DailyShortSaleVolumeFileLayout.pdf

SEC and rules:
- EDGAR access: https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data
- 13F FAQ: https://www.sec.gov/divisions/investment/13ffaq
- 13D/G release 33-11253: https://www.sec.gov/files/rules/final/2023/33-11253.pdf
- Form 144 form: https://www.sec.gov/files/form144.pdf ; Rule 144: https://www.law.cornell.edu/cfr/text/17/230.144
- Rule 16a-3: https://www.law.cornell.edu/cfr/text/17/240.16a-3
- Reg SHO 200 and 203: https://www.law.cornell.edu/cfr/text/17/242.200 ; https://www.law.cornell.edu/cfr/text/17/242.203
- N-PORT compliance extension: https://www.sec.gov/rules-regulations/2026/02/s7-16-22
- Repurchase rule vacatur (law-firm secondary): https://www.jenner.com/print/v2/content/63347/client-alert-fifth-circuit-court-of-appeals-vacates-the-secs-share-repurchase-disclosure-modernization-rule-amendments.pdf
- Russell reconstitution: https://www.lseg.com/en/ftse-russell/russell-reconstitution

Alpaca and market data:
- https://docs.alpaca.markets/docs/about-market-data-api ; https://docs.alpaca.markets/us/docs/market-data-faq ; https://docs.alpaca.markets/docs/historical-stock-data-1 ; https://docs.alpaca.markets/us/reference/stockmetaconditions-1 ; https://docs.alpaca.markets/us/reference/stockmetaexchanges-1 ; https://alpaca.markets/disclosures
- alpaca-py enums: https://raw.githubusercontent.com/alpacahq/alpaca-py/master/alpaca/data/enums.py
- CTS Pillar output spec v2.11b: https://www.ctaplan.com/publicdocs/ctaplan/CTS_Pillar_Output_Specification.pdf
- IEX: https://iextrading.com/trading/market-data/ ; Massive: https://massive.com/pricing

Papers (year; label in the text):
- Zarinelli et al. 2015, https://ar5iv.labs.arxiv.org/html/1412.2152
- Bucci et al. 2019 (PRL), https://ar5iv.labs.arxiv.org/html/1811.05230 ; Bucci et al. 2019 (MML), https://ar5iv.labs.arxiv.org/html/1901.05332
- Lillo, Mike, Farmer 2005, https://ar5iv.labs.arxiv.org/html/cond-mat/0412708
- Toth, Palit, Lillo, Farmer, https://ar5iv.labs.arxiv.org/html/1108.1632 ; Toth et al. 2011, https://arxiv.org/abs/1105.1694v3
- Frazzini, Israel, Moskowitz 2012 draft, https://conference.nber.org/conf_papers/f68262/f68262.pdf ; 2018, https://papers.ssrn.com/abstract=3229719
- Kyle and Obizhaeva 2016, https://ideas.repec.org/a/wly/emetrp/v84y2016i4p1345-1404.html
- Keim and Madhavan 1995, https://repository.upenn.edu/fnce_papers/383 ; Chan and Lakonishok 1995, https://ideas.repec.org/a/bla/jfinan/v50y1995i4p1147-74.html
- Campbell, Ramadorai, Schwartz 2009, https://ideas.repec.org/a/eee/jfinec/v92y2009i1p66-91.html
- Barber et al. 2024, https://papers.ssrn.com/abstract=4202874
- Lee and Ready 1991, https://ideas.repec.org/a/bla/jfinan/v46y1991i2p733-46.html
- Easley, Lopez de Prado, O'Hara 2012, https://ideas.repec.org/a/oup/rfinst/v25y2012i5p1457-1493.html ; Andersen and Bondarenko, https://ideas.repec.org/p/aah/create/2011-50.html ; rejoinder, https://ideas.repec.org/a/eee/finmar/v17y2014icp47-52.html
- Chakrabarty, Pascual, Shkilko 2015, https://ideas.repec.org/a/eee/finmar/v25y2015icp52-79.html
- Hendershott and Riordan 2013, https://ideas.repec.org/a/cup/jfinqa/v48y2013i04p1001-1024_00.html (via search)
- Comerton-Forde and Putnins 2015, https://ideas.repec.org/a/eee/jfinec/v118y2015i1p70-92.html ; Zhu 2014, https://dspace.mit.edu/handle/1721.1/88124 ; Menkveld, Yueshen, Zhu 2017, https://www.mit.edu/~zhuh/MenkveldYueshenZhu_2017JFE_dark.pdf
- Brogaard and Pan, https://sites.insead.edu/facultyresearch/research/file.cfm?fid=64858 ; Buti, Rindi, Werner, https://didattica.unibocconi.it/mypage/upload/48636_20220131_034055_DIVING_FINAL_SSRN_20220130.PDF
- Killick, Fearnhead, Eckley 2012, https://arxiv.org/abs/1101.1438 ; Adams and MacKay 2007, https://arxiv.org/abs/0710.3742 ; Truong, Oudre, Vayatis 2020, https://arxiv.org/abs/1801.00718
- Chakar et al. 2017, https://arxiv.org/pdf/1403.1958 ; Lavielle and Moulines 2000, https://ideas.repec.org/a/bla/jtsera/v21y2000i1p33-59.html ; Kulldorff, https://www.satscan.org/references.html
- White 2000, https://ideas.repec.org/a/ecm/emetrp/v68y2000i5p1097-1126.html ; Harvey, Liu, Zhu, https://www.nber.org/papers/w20592 ; Politis and Romano 1994, https://gnosis.library.ucy.ac.cy/handle/7/57533 ; Politis and White 2004, https://gnosis.library.ucy.ac.cy/handle/7/57548

Libraries: https://pypi.org/pypi/ruptures/json ; https://api.github.com/repos/deepcharles/ruptures ; https://centre-borelli.github.io/ruptures-docs/ ; https://pypi.org/pypi/arch/json ; https://raw.githubusercontent.com/bashtage/arch/main/arch/bootstrap/multiple_comparison.py ; https://pypi.org/pypi/hmmlearn/json
