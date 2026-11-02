"""Look-back chart of block-venue activity, as one self-contained HTML page.

A period starts when a week clears the bar and runs while nearby weeks stay
elevated, so it can span several weeks. The page says what the data shows and
where things stand now. It describes where blocks traded. Testing has not shown
that it detects large players or predicts anything, so it never claims to.
"""
import html
import json
import math

import numpy as np
import pandas as pd

PERIOD_STAY_Z = 1.0     # a period carries on while weeks stay at or above this
PERIOD_MAX_GAP = 1      # one quiet week inside a period doesn't end it
RECENT_WEEKS = 4        # a period this close to the latest week still counts as recent
MIN_FILERS = 100        # fewer filers than this for a quarter means only stragglers
FILING_DAYS = 45        # 13F reports are due this long after a quarter ends
TOP_ADDS = 5
ELEVATED_Z = 1.5        # near the bar: worth seeing, not enough to start a period
PRICE_WINDOW = 52       # weeks of price range for the reality check
PRICE_MIN_WEEKS = 26
SPLIT_JUMP = 1.6        # a week-on-week move this big may be an unadjusted split
LOW_POS, HIGH_POS = 33.4, 66.7

WIDTH, LEFT, RIGHT = 1000, 64, 24
PRICE_TOP, PRICE_H = 28, 170
BLOCK_TOP, BLOCK_H = 244, 220
HEIGHT = BLOCK_TOP + BLOCK_H + 36
MAX_BAR = 24

STYLE = """
:root{color-scheme:light;--surface:#fcfcfb;--plane:#f9f9f7;--ink:#0b0b0b;--ink2:#52514e;--muted:#6d6c66;
--grid:#e1e0d9;--axis:#c3c2b7;--accent:#2a78d6;--elevated:#86b6ef;--quiet:#c3c2b7;--ring:rgba(11,11,11,.10)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){color-scheme:dark;--surface:#1a1a19;--plane:#0d0d0d;
--ink:#f0efec;--ink2:#c3c2b7;--muted:#a3a29a;--grid:#2c2c2a;--axis:#383835;--accent:#3987e5;--elevated:#1c5cab;--quiet:#55544f;
--ring:rgba(255,255,255,.10)}}
:root[data-theme="dark"]{color-scheme:dark;--surface:#1a1a19;--plane:#0d0d0d;--ink:#f0efec;--ink2:#c3c2b7;--muted:#a3a29a;
--grid:#2c2c2a;--axis:#383835;--accent:#3987e5;--elevated:#1c5cab;--quiet:#55544f;--ring:rgba(255,255,255,.10)}
*{box-sizing:border-box}
body{margin:0;background:var(--plane);color:var(--ink);font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:1040px;margin:0 auto;padding-block:24px 48px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
.eyebrow{color:var(--ink2);font-size:14px;margin:0}
h1{font-size:24px;line-height:1.3;font-weight:600;margin:4px 0 8px;text-wrap:balance}
h2{font-size:16px;font-weight:600;margin:0 0 8px}
.badge{display:inline-flex;gap:6px;align-items:center;font-size:14px;font-weight:600;padding:2px 10px;border-radius:999px;
box-shadow:inset 0 0 0 1px var(--ring);background:var(--surface)}
.badge.active{background:var(--accent);color:#fff;box-shadow:none}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px;margin:16px 0}
.tile,.card{background:var(--surface);border-radius:8px;box-shadow:inset 0 0 0 1px var(--ring)}
.tile{padding:10px 14px}.tile b{display:block;font-size:22px;font-weight:600}.tile span{color:var(--ink2);font-size:13px}
.card{padding:16px;margin-top:12px}
.legend{display:flex;flex-wrap:wrap;gap:6px 18px;color:var(--ink2);font-size:13px;margin-bottom:8px}
.legend i{display:inline-block;width:12px;height:12px;border-radius:3px;margin-right:6px;vertical-align:-1px}
.legend i.line{height:2px;width:16px;border-radius:0;vertical-align:3px}
.scroll{overflow-x:auto}
svg{display:block;width:100%;min-width:640px;height:auto;touch-action:pan-y}
svg:focus{outline:2px solid var(--accent);outline-offset:2px}
svg text{fill:var(--muted);font-size:12px;font-variant-numeric:tabular-nums}
svg .title{fill:var(--ink2);font-size:13px;font-variant-numeric:normal}
.grid{stroke:var(--grid);stroke-width:1}.base{stroke:var(--axis);stroke-width:1}
.period-shade{fill:var(--accent);opacity:.10}
.bar{fill:var(--quiet)}.bar.elevated{fill:var(--elevated)}.bar.active{fill:var(--accent)}
.price{fill:none;stroke:var(--ink2);stroke-width:2;stroke-linejoin:round;stroke-linecap:round}
.normal{fill:none;stroke:var(--muted);stroke-width:2;stroke-linejoin:round;stroke-linecap:round}
.dot{fill:var(--ink2);stroke:var(--surface);stroke-width:2}
.cross{stroke:var(--muted);stroke-width:1;visibility:hidden}
#tip{position:fixed;display:none;pointer-events:none;background:var(--surface);color:var(--ink2);font-size:13px;padding:8px 10px;
border-radius:8px;box-shadow:0 2px 12px rgba(0,0,0,.18),inset 0 0 0 1px var(--ring);min-width:170px;z-index:5}
#tip div{display:flex;justify-content:space-between;gap:16px}#tip b{color:var(--ink);font-weight:600}
#tip .when{color:var(--ink);font-weight:600;display:block;margin-bottom:2px}
table{border-collapse:collapse;width:100%;font-size:14px;font-variant-numeric:tabular-nums}
th{color:var(--ink2);font-weight:500;text-align:right;padding:4px 8px;border-bottom:1px solid var(--axis)}
td{text-align:right;padding:4px 8px;border-bottom:1px solid var(--grid)}
th:first-child,td:first-child{text-align:left}
summary{cursor:pointer;font-weight:600}
.note{color:var(--ink2);margin:8px 0 0}.none{color:var(--ink2);margin:0}
"""

SCRIPT = """
(function(){
var W=JSON.parse(document.getElementById('weeks').textContent);
var svg=document.querySelector('svg'),tip=document.getElementById('tip'),cross=document.getElementById('cross');
var L=+svg.dataset.left,B=+svg.dataset.band,cur=-1;
function row(v,k){var d=document.createElement('div'),s=document.createElement('span'),b=document.createElement('b');
s.textContent=k;b.textContent=v;d.appendChild(s);d.appendChild(b);return d}
function show(i,x,y){cur=i;var w=W[i],cx=L+B*(i+.5);
cross.setAttribute('x1',cx);cross.setAttribute('x2',cx);cross.style.visibility='visible';tip.textContent='';
var h=document.createElement('span');h.className='when';h.textContent='Week of '+w.week;tip.appendChild(h);
tip.appendChild(row(w.dollars,'Block dollars'));tip.appendChild(row(w.normal,'Normal'));tip.appendChild(row(w.share,'Share of dark pool'));
tip.appendChild(row(w.z,'Score'));tip.appendChild(row(w.price,'Price'));tip.appendChild(row(w.range,'1-year range'));
if(w.period)tip.appendChild(row('Yes','In a period'));
tip.style.display='block';var r=tip.getBoundingClientRect();
tip.style.left=Math.max(8,Math.min(x+14,innerWidth-r.width-8))+'px';tip.style.top=Math.max(8,Math.min(y+14,innerHeight-r.height-8))+'px'}
function hide(){cur=-1;cross.style.visibility='hidden';tip.style.display='none'}
svg.addEventListener('pointermove',function(e){var r=svg.getBoundingClientRect(),vx=(e.clientX-r.left)*svg.viewBox.baseVal.width/r.width;
var i=Math.floor((vx-L)/B);if(i<0||i>=W.length){hide();return}show(i,e.clientX,e.clientY)});
svg.addEventListener('pointerleave',hide);svg.addEventListener('blur',hide);
svg.addEventListener('keydown',function(e){if(e.key!=='ArrowLeft'&&e.key!=='ArrowRight')return;e.preventDefault();
var i=cur<0?W.length-1:Math.max(0,Math.min(W.length-1,cur+(e.key==='ArrowLeft'?-1:1)));
var r=svg.getBoundingClientRect();show(i,r.left+(L+B*(i+.5))*r.width/svg.viewBox.baseVal.width,r.top+40)});
})();
"""


def with_score(scored):
    """Add `score`: the higher of block share and block dollars, each against normal.
    Share ignores how busy a week was, and dollars keep it, so a week can stand out on either."""
    return scored.assign(score=np.fmax(scored["z_block"], scored["z_block_usd"]))


def with_price_position(scored):
    """Add `price_pos`: where the price sits in its trailing 1-year range, 0 at the low and
    100 at the high. It's a reality check for reading periods and never enters a score.
    FINRA prices aren't split-adjusted, so it stays blank for a year after a split-like jump."""
    price = scored["vwap"]
    high = price.rolling(PRICE_WINDOW, min_periods=PRICE_MIN_WEEKS).max()
    low = price.rolling(PRICE_WINDOW, min_periods=PRICE_MIN_WEEKS).min()
    step = price / price.shift(1)
    jump = ((step >= SPLIT_JUMP) | (step <= 1 / SPLIT_JUMP)).astype(float)
    recent_jump = jump.rolling(PRICE_WINDOW, min_periods=1).max() > 0
    return scored.assign(price_pos=(100 * (price - low) / (high - low)).where(~recent_jump))


def price_label(pos):
    if pos != pos:
        return "–"
    return "Low" if pos < LOW_POS else "High" if pos >= HIGH_POS else "Middle"


def find_periods(scored, enter, stay=PERIOD_STAY_Z, max_gap=PERIOD_MAX_GAP, col="z_block"):
    """Runs of elevated weeks that reach `enter` at least once, oldest first."""
    z = scored[col].to_numpy(dtype=float)
    hot = np.flatnonzero(z >= stay)
    if not len(hot):
        return []
    periods = []
    for run in np.split(hot, np.flatnonzero(np.diff(hot) > max_gap + 1) + 1):
        if z[run].max() < enter:
            continue
        first, last = int(run[0]), int(run[-1])
        peak = int(run[np.argmax(z[run])])
        vwap = scored["vwap"].to_numpy(dtype=float)
        periods.append({
            "start": scored.index[first], "end": scored.index[last], "weeks": last - first + 1,
            "peak_z": float(z[peak]), "peak_week": scored.index[peak],
            "block_dollars": float(scored["block_dollars"].iloc[first:last + 1].sum()),
            "price_chg": 100 * (vwap[last] / vwap[max(0, first - 1)] - 1),
            "price_pos": float(scored["price_pos"].iloc[first]) if "price_pos" in scored else float("nan"),
        })
    return periods


def current_status(scored, periods, col="z_block"):
    """Where things stand in the newest week of data."""
    last, week = scored.iloc[-1], scored.index[-1]
    st = {"state": "quiet", "week": week, "since": None, "weeks_ago": None, "z": float(last[col]),
          "dollars": float(last["block_dollars"]), "normal": float(last["block_normal_usd"])}
    if math.isnan(st["z"]):
        st["state"] = "unknown"
    elif periods:
        end = periods[-1]["end"]
        ago = (week - end).days // 7
        if ago == 0:
            st.update(state="active", since=periods[-1]["start"])
        elif ago <= RECENT_WEEKS:
            st.update(state="recent", weeks_ago=ago)
    return st


def status_sentence(st, sym):
    week = f"week of {st['week'].date()}"
    if st["state"] == "active":
        since = "" if st["since"] == st["week"] else f", running since {st['since'].date()}"
        return f"{sym}: block-venue activity is unusually high in the latest data ({week}){since}."
    if st["state"] == "recent":
        return f"{sym}: block-venue activity faded {st['weeks_ago']} week(s) before the latest data ({week})."
    if st["state"] == "unknown":
        return f"{sym}: the latest data ({week}) has no block-venue trading to score."
    return f"{sym}: no unusual block-venue activity in the latest data ({week})."


def holdings_by_quarter(holdings, as_of):
    """13F changes grouped by filing quarter, newest first. Brand-new positions are kept
    apart from existing holders, because a new or reorganized filer can look like buying."""
    d = pd.DataFrame(holdings["rows"])
    d["quarter"] = pd.to_datetime(d["date"], format="%m/%d/%Y")
    quarters = []
    for end, q in sorted(d.groupby("quarter"), key=lambda kv: kv[0], reverse=True):
        if len(q) < MIN_FILERS:
            continue
        held = q[~q["new"]]
        net = float(held["change"].sum())
        adds = held[held["change"] > 0].nlargest(TOP_ADDS, "change")
        quarters.append({
            "quarter_end": end, "filers": len(q), "raised": int((held["change"] > 0).sum()),
            "cut": int((held["change"] < 0).sum()), "net_shares": net,
            "net_pct": 100 * net / holdings["outstanding"], "new_shares": float(q.loc[q["new"], "change"].sum()),
            "top_adds": adds[["owner", "change"]].to_dict("records"),
            "complete": as_of >= (end + pd.Timedelta(days=FILING_DAYS)).date(),
        })
    return quarters


def quarter_name(end):
    first = end - pd.DateOffset(months=2)
    return f"{first:%b} to {end:%b %Y}"


def holdings_sentence(quarters, sym):
    done = [q for q in quarters if q["complete"]]
    if not done:
        return ""
    q = done[0]
    verb = "net added" if q["net_shares"] >= 0 else "net cut"
    return (f"{quarter_name(q['quarter_end'])}: existing institutional holders of {sym} {verb} "
            f"{abs(q['net_shares']) / 1e6:.2f}M shares ({abs(q['net_pct']):.2f}% of all shares), "
            f"with {q['raised']:,} raised and {q['cut']:,} cut.")


def holdings_card(sym, holdings, as_of):
    if holdings is None:
        return '<div class="card"><h2>Institutions adding or cutting shares</h2><p class="none">Holdings data wasn\'t available for this run.</p></div>'
    quarters = holdings_by_quarter(holdings, as_of)
    rows = "".join(
        f'<tr><td>{quarter_name(q["quarter_end"])}{"" if q["complete"] else " (filings still arriving)"}</td><td>{q["raised"]:,}</td>'
        f'<td>{q["cut"]:,}</td><td>{q["net_shares"] / 1e6:+,.1f}M</td><td>{q["net_pct"]:+.2f}%</td><td>{q["new_shares"] / 1e6:,.1f}M</td></tr>'
        for q in quarters)
    done = [q for q in quarters if q["complete"]]
    adds = "".join(f'<tr><td>{html.escape(str(a["owner"]))}</td><td>+{a["change"] / 1e6:,.2f}M</td></tr>' for a in done[0]["top_adds"]) if done else ""
    added = (f'<h2 style="margin-top:16px">Largest adds by existing holders, {quarter_name(done[0]["quarter_end"])}</h2>'
             f'<div class="scroll"><table><tr><th>Institution</th><th>Shares added</th></tr>{adds}</table></div>') if adds else ""
    return f"""<div class="card"><h2>Institutions adding or cutting shares</h2>
<div class="scroll"><table><tr><th>Quarter</th><th>Raised</th><th>Cut</th><th>Net shares</th><th>Net % of all shares</th><th>New positions</th></tr>{rows}</table></div>
{added}
<p class="note">From 13F filings, which show what institutions held at quarter end and are due 45 days later. "Raised" and "Cut" count filers. Net shares covers existing holders only. New positions are separate because a new or reorganized filer can look like buying. Filers include index funds and market makers, and some positions are hedges. Source: Nasdaq's website, not the SEC directly.</p></div>"""


def money(v):
    if v != v:
        return "–"
    return f"${v / 1e9:.2f}B" if abs(v) >= 1e9 else f"${v / 1e6:.1f}M"


def pct(v, sign=False):
    return "–" if v != v else f"{v:+.1f}%" if sign else f"{v:.2f}%"


def number(v):
    return "–" if v != v else f"{v:.2f}"


def nice_ticks(lo, hi, count=4):
    """Round axis values covering lo to hi."""
    span = (hi - lo) or abs(hi) or 1.0
    raw = span / count
    mag = 10 ** math.floor(math.log10(raw))
    step = next(m for m in (1, 2, 2.5, 5, 10) if m * mag >= raw) * mag
    first = math.floor(lo / step) * step
    return [first + i * step for i in range(int(math.ceil((hi - first) / step)) + 1)]


def bar_path(x, y, w, h):
    r = min(4.0, w / 2, h)
    return (f"M{x:.1f} {y + h:.1f}V{y + r:.1f}Q{x:.1f} {y:.1f} {x + r:.1f} {y:.1f}H{x + w - r:.1f}"
            f"Q{x + w:.1f} {y:.1f} {x + w:.1f} {y + r:.1f}V{y + h:.1f}Z")


def line_path(points):
    """SVG path through (x, y) points, broken wherever y is missing."""
    out, pen = [], "M"
    for x, y in points:
        if y != y:
            pen = "M"
            continue
        out.append(f"{pen}{x:.1f} {y:.1f}")
        pen = "L"
    return "".join(out)


def week_labels(index):
    """Positions for x-axis labels: quarter starts, or evenly spaced when short."""
    quarters = [i for i in range(1, len(index)) if index[i].month != index[i - 1].month and index[i].month in (1, 4, 7, 10)]
    return quarters if len(quarters) >= 2 else list(range(0, len(index), max(1, len(index) // 4)))


def chart_svg(sym, s, periods):
    n = len(s)
    band = (WIDTH - LEFT - RIGHT) / n
    width = min(MAX_BAR, max(1.0, band - 2))
    x_mid = lambda i: LEFT + band * (i + 0.5)
    share = s["block_dollars"].to_numpy(dtype=float) / 1e6
    normal = s["block_normal_usd"].to_numpy(dtype=float) / 1e6
    score = s["score"].to_numpy(dtype=float) if "score" in s else s["z_block"].to_numpy(dtype=float)
    vwap = s["vwap"].to_numpy(dtype=float)

    known = vwap[~np.isnan(vwap)]
    lo, hi = (known.min(), known.max()) if len(known) else (0.0, 1.0)
    pad = (hi - lo) * 0.08 or max(abs(hi) * 0.05, 1.0)
    p_ticks = nice_ticks(lo - pad, hi + pad)
    p_lo, p_hi = p_ticks[0], p_ticks[-1]
    p_y = lambda v: PRICE_TOP + PRICE_H * (1 - (v - p_lo) / (p_hi - p_lo))

    top = np.nanmax(np.concatenate([share, normal, [0.1]]))
    b_ticks = nice_ticks(0.0, float(top))
    b_hi = b_ticks[-1]
    b_y = lambda v: BLOCK_TOP + BLOCK_H * (1 - v / b_hi)

    active = np.zeros(n, dtype=bool)
    parts = []
    for p in periods:
        a, b = s.index.get_loc(p["start"]), s.index.get_loc(p["end"])
        active[a:b + 1] = True
        x, w = LEFT + band * a, band * (b - a + 1)
        parts.append(f'<rect class="period-shade" x="{x:.1f}" y="{PRICE_TOP}" width="{w:.1f}" height="{PRICE_H}"/>')
        parts.append(f'<rect class="period-shade" x="{x:.1f}" y="{BLOCK_TOP}" width="{w:.1f}" height="{BLOCK_H}"/>')

    parts.append(f'<text class="title" x="{LEFT}" y="{PRICE_TOP - 12}">Price: weekly average in dark pools ($)</text>')
    parts.append(f'<text class="title" x="{LEFT}" y="{BLOCK_TOP - 12}">Block-venue dollars each week ($M)</text>')
    for v in p_ticks:
        y = p_y(v)
        parts.append(f'<line class="grid" x1="{LEFT}" x2="{WIDTH - RIGHT}" y1="{y:.1f}" y2="{y:.1f}"/>'
                     f'<text x="{LEFT - 8}" y="{y + 4:.1f}" text-anchor="end">{v:g}</text>')
    for v in b_ticks:
        y = b_y(v)
        cls = "base" if v == 0 else "grid"
        parts.append(f'<line class="{cls}" x1="{LEFT}" x2="{WIDTH - RIGHT}" y1="{y:.1f}" y2="{y:.1f}"/>'
                     f'<text x="{LEFT - 8}" y="{y + 4:.1f}" text-anchor="end">{v:g}</text>')

    for i in range(n):
        h = 0.0 if share[i] != share[i] else BLOCK_H * share[i] / b_hi
        cls = "bar active" if active[i] else "bar elevated" if score[i] >= ELEVATED_Z else "bar"
        parts.append(f'<path class="{cls}" d="{bar_path(x_mid(i) - width / 2, BLOCK_TOP + BLOCK_H - h, width, h)}"/>')
    parts.append(f'<path class="normal" d="{line_path((x_mid(i), b_y(normal[i])) for i in range(n))}"/>')
    parts.append(f'<path class="price" d="{line_path((x_mid(i), p_y(vwap[i])) for i in range(n))}"/>')
    if vwap[-1] == vwap[-1]:
        parts.append(f'<circle class="dot" cx="{x_mid(n - 1):.1f}" cy="{p_y(vwap[-1]):.1f}" r="5"/>')

    for i in week_labels(s.index):
        parts.append(f'<text x="{x_mid(i):.1f}" y="{HEIGHT - 12}" text-anchor="middle">{s.index[i]:%b %Y}</text>')
    parts.append(f'<line id="cross" class="cross" x1="0" x2="0" y1="{PRICE_TOP}" y2="{BLOCK_TOP + BLOCK_H}"/>')
    label = html.escape(f"{sym} price and block-venue share by week, {len(periods)} period(s) shaded. "
                        f"The table below has every value.", quote=True)
    return (f'<svg viewBox="0 0 {WIDTH} {HEIGHT}" role="img" tabindex="0" aria-label="{label}" '
            f'data-left="{LEFT}" data-band="{band:.4f}">{"".join(parts)}</svg>'), active


def tiles(st, latest_price):
    rows = [(money(st["dollars"]), "Block dollars, latest week"), (money(st["normal"]), "Normal for this stock"),
            (number(st["z"]), "Score (how unusual)"), (f"${latest_price:,.2f}" if latest_price == latest_price else "–", "Price, latest week")]
    return "".join(f'<div class="tile"><b>{v}</b><span>{k}</span></div>' for v, k in rows)


def period_rows(periods):
    if not periods:
        return '<p class="none">No period cleared the bar in this window.</p>'
    rows = "".join(
        f'<tr><td>{p["start"].date()} to {p["end"].date()}</td><td>{p["weeks"]}</td><td>{number(p["peak_z"])}</td>'
        f'<td>{money(p["block_dollars"])}</td><td>{position_text(p["price_pos"])}</td><td>{pct(p["price_chg"], sign=True)}</td></tr>'
        for p in reversed(periods))
    low = sum(price_label(p["price_pos"]) == "Low" for p in periods)
    return (f'<p class="note" style="margin:0 0 8px">Price check: {low} of {len(periods)} periods started in the lower third of the '
            "stock's 1-year price range. Price is not part of the score, so this is a separate reality check.</p>"
            '<div class="scroll"><table><tr><th>Period</th><th>Weeks</th><th>Peak score</th><th>Block dollars</th>'
            f'<th>Price at start, 1-year range</th><th>Price over period</th></tr>{rows}</table></div>')


def position_text(pos):
    return "–" if pos != pos else f"{price_label(pos)} ({pos:.0f}%)"


def week_data(s, active):
    score = "score" if "score" in s.columns else "z_block"
    return [{"week": str(w.date()), "share": pct(100 * r["block_share"]), "normal": money(r["block_normal_usd"]),
             "dollars": money(r["block_dollars"]), "z": number(r[score]),
             "price": "–" if r["vwap"] != r["vwap"] else f"${r['vwap']:,.2f}", "period": bool(a),
             "range": position_text(r["price_pos"]) if "price_pos" in s.columns else "–"}
            for (w, r), a in zip(s.iterrows(), active)]


BADGES = {"active": "● High now", "recent": "◐ Faded recently", "quiet": "○ Quiet", "unknown": "? No score"}


def render_chart(sym, scored, periods, status, enter, as_of, holdings=None):
    """One self-contained HTML page for a ticker."""
    name = html.escape(str(sym))
    lead = holdings_sentence(holdings_by_quarter(holdings, as_of), str(sym)) if holdings else ""
    svg, active = chart_svg(sym, scored, periods)
    weeks = week_data(scored, active)
    table = "".join(
        f'<tr class="week"><td>{w["week"]}</td><td>{w["share"]}</td><td>{w["normal"]}</td><td>{w["dollars"]}</td>'
        f'<td>{w["z"]}</td><td>{w["price"]}</td><td>{w["range"]}</td><td>{"Yes" if w["period"] else ""}</td></tr>' for w in reversed(weeks))
    payload = json.dumps(weeks).replace("<", "\\u003c")
    built = f"{as_of:%b} {as_of.day}, {as_of.year}"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{name} Block Activity</title><meta name="claude:viewport-fit-sides" content="cover"><style>{STYLE}</style></head><body><main>
<p class="eyebrow">Block-venue activity, {name}</p>
<h1>{html.escape(status_sentence(status, str(sym)))}</h1>
<span class="badge {status['state']}">{BADGES[status['state']]}</span>
{f'<p class="note">{html.escape(lead)}</p>' if lead else ''}
<div class="tiles">{tiles(status, float(scored['vwap'].iloc[-1]))}</div>
<div class="card">
<div class="legend"><span><i style="background:var(--accent)"></i>Week in an active period</span>
<span><i style="background:var(--elevated)"></i>Elevated week, score {ELEVATED_Z:g} or more</span>
<span><i style="background:var(--quiet)"></i>Other week</span>
<span><i class="line" style="background:var(--muted)"></i>Normal for this stock</span>
<span><i style="background:var(--accent);opacity:.18"></i>Active period</span></div>
<div class="scroll">{svg}</div>
<p class="note">Data ends the week of {status['week'].date()}. Page built {built}. FINRA publishes about 3 weeks late, so the most recent weeks aren't visible yet. Source: FINRA OTC Transparency weekly and monthly dark-pool (ATS) data, amounts in USD.</p>
</div>
<div class="card"><h2>Active periods</h2>{period_rows(periods)}</div>
{holdings_card(sym, holdings, as_of)}
<div class="card"><h2>How to read this</h2>
<p class="note">Each bar is the dollars that traded on block venues that week, the dark pools FINRA reports as doing most of their business in $200K+ trades. The line is the median of the 26 weeks before each bar. A week's score is the higher of two checks against that stock's recent past: block dollars, and block venues' share of dark-pool dollars. A period starts when the score reaches {enter:g} and runs while nearby weeks stay at {PERIOD_STAY_Z:g} or more. Elevated weeks came close to starting one.</p>
<p class="note">A tall bar can simply be a busy week for the whole stock, and an index rebalance can cause one too.</p>
<p class="note">This data can't show whether large players were buying or selling, or who they were. "Price over period" only shows what the price did.</p>
<p class="note"><b>What testing found (October 2026, 60 stocks not used to build this):</b> buying after a flagged week did no better than buying the same stock in any other week. 13 weeks later, 50% of entries were up, against 60% for other weeks. Flags also didn't line up with large insider sales.</p>
<p class="note"><b>One check did find a link.</b> Across 78 large stocks in April to June 2026, existing institutions were net buyers of 73% of the stocks with the highest block share, against 23% of those with the lowest. That is one quarter, found after other tests failed, so it still needs repeating on the September filings. It's a pattern across many stocks and can be wrong for any one stock. This page isn't a buy signal.</p>
<p class="note"><b>Price check across 60 stocks:</b> highlighted weeks did not sit at low prices. They averaged 76% of the way up the 1-year range, against 70% for other weeks, so many may not be buying at all. Periods that started in the lower third did better: a median +9.4% over 13 weeks, against +4.1% for any week in that zone. That comparison hasn't been formally tested.</p></div>
<div class="card"><details><summary>Every week as a table</summary><div class="scroll"><table>
<tr><th>Week</th><th>Block share</th><th>Normal dollars</th><th>Block dollars</th><th>Score</th><th>Price</th><th>1-year range</th><th>In a period</th></tr>{table}
</table></div></details></div>
</main><div id="tip"></div><script type="application/json" id="weeks">{payload}</script><script>{SCRIPT}</script></body></html>
"""
