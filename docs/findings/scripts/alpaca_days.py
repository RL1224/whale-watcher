# Run real analyze_day over ticker-days, caching each day's summary. Usage: alpaca_days.py SYM:DATE ...
import datetime as dt
import os
import pickle
import sys
import time

sys.path.insert(0, ".")
import pandas as pd
import whale_watch as ww

CACHE = sys.argv[1]
JOBS = sys.argv[2:]
cache = pickle.load(open(CACHE, "rb")) if os.path.exists(CACHE) else {}
H = ww.alpaca_headers()
for preset in ("medium",):
    cfg = ww.PRESETS["prints"][preset]
    for job in JOBS:
        sym, day = job.split(":")
        if (sym, day, preset) in cache:
            continue
        t0 = time.time()
        try:
            df = ww.fetch_trades(sym, f"{day}T13:00:00Z", f"{day}T21:30:00Z", H)
            if df.empty:
                print(sym, day, "no trades", flush=True)
                cache[(sym, day, preset)] = None
            else:
                summ, blocks = ww.analyze_day(df, cfg)
                keep = blocks[["ts", "p", "s", "notional", "pieces", "ref_px", "lean"]].copy() if len(blocks) else blocks
                cache[(sym, day, preset)] = {"summ": summ, "blocks": keep, "rows": len(df)}
                print(sym, day, "rows", len(df), "secs", round(time.time() - t0), {k: (round(v, 2) if isinstance(v, float) else v) for k, v in (summ or {}).items()}, flush=True)
        except Exception as e:
            print(sym, day, "FAILED", repr(e)[:200], flush=True)
        pickle.dump(cache, open(CACHE, "wb"))
print("finished", len(cache), flush=True)
