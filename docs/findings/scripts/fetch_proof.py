# Collect data for the pre-registered tests. No analysis here.
import datetime as dt
import json
import pickle
import re
import sys
import time
import urllib.request

sys.path.insert(0, ".")
import pandas as pd
import whale_watch as ww

TICKERS = ["AMZN", "META", "GOOGL", "TSLA", "AVGO", "LLY", "V", "MA", "HD", "PG", "ABBV", "MRK", "PEP", "ADBE", "CRM",
           "CSCO", "ACN", "TMO", "ABT", "LIN", "NFLX", "INTC", "QCOM", "TXN", "INTU", "AMAT", "MU", "LRCX", "NOW", "PANW",
           "UBER", "ABNB", "SHOP", "COIN", "HOOD", "DELL", "HPQ", "F", "GM", "BA", "GE", "HON", "UPS", "FDX", "NKE",
           "SBUX", "MCD", "LOW", "TGT", "CVS", "PFE", "GILD", "AMGN", "BMY", "C", "GS", "MS", "SCHW", "AXP", "BLK"]
OI = ("http://openinsider.com/screener?s={sym}&o=&pl=&ph=&ll=&lh=&fd=1461&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xs=1"
      "&vl=100&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h="
      "&sortcol=0&cnt=2000&page=1")
UA = {"User-Agent": "Mozilla/5.0"}
clean = lambda c: re.sub(r"<[^>]+>", "", c).replace("&nbsp;", " ").strip()


def sales(sym):
    with urllib.request.urlopen(urllib.request.Request(OI.format(sym=sym), headers=UA), timeout=60) as r:
        html = r.read().decode("utf-8", "replace")
    m = re.search(r'<table[^>]*class="tinytable".*?</table>', html, re.S)
    out = []
    for row in re.findall(r"<tr.*?</tr>", m.group(0), re.S)[1:] if m else []:
        c = [clean(x) for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S)]
        if len(c) >= 12 and c[6].startswith("S - Sale"):
            out.append({"trade": c[2], "owner": c[4], "title": c[5], "price": c[7], "qty": c[8],
                        "usd": abs(float(re.sub(r"[^0-9.]", "", c[11]) or 0))})
    return pd.DataFrame(out)


def yahoo(sym):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=4y&interval=1d"
    j = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40))["chart"]["result"][0]
    q = j["indicators"]["quote"][0]
    d = pd.DataFrame({"c": q["close"], "v": q["volume"]},
                     index=pd.to_datetime(j["timestamp"], unit="s", utc=True).tz_convert("America/New_York").tz_localize(None).normalize()).dropna()
    d["wk"] = d.index - pd.to_timedelta(d.index.day_of_week, unit="D")
    return d.groupby("wk").agg(close=("c", "last"), volume=("v", "sum"))


today = dt.date.today()
s, e = (today - dt.timedelta(weeks=182)).isoformat(), today.isoformat()
h = ww.finra_headers()
out = {"venues": ww.fetch_block_venues(today, h), "start": s, "end": e,
       "mkt": ww.estimate_recent_market(ww.finra_market_weekly(s, e, h), today, h), "raw": {}, "px": {}, "ins": {}, "failed": {}}
print("venues", sorted(out["venues"]), flush=True)
for i, t in enumerate(TICKERS, 1):
    try:
        out["raw"][t] = ww.fetch_finra({"issueSymbolIdentifier": t}, s, e, h)
        out["px"][t] = yahoo(t)
        out["ins"][t] = sales(t)
        print(i, t, len(out["raw"][t]), len(out["px"][t]), len(out["ins"][t]), flush=True)
    except Exception as ex:
        out["failed"][t] = repr(ex)
        print(i, t, "FAILED", repr(ex), flush=True)
    time.sleep(1.0)
pickle.dump(out, open("proof_data.pkl", "wb"))
print("saved | ok", len(out["raw"]), "| failed", out["failed"], flush=True)
