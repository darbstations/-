# -*- coding: utf-8 -*-
"""يضيف مبيعات يوليو 2026 — شهريًا ويوميًا — إلى المنصّة.

المصدر: لوحة «درب · تحليل المبيعات وحركة العملاء» (دفعة 2026-08-12) التي
تحمل بيانات 55 محطة من يناير إلى يوليو، شهريًا وبسلسلة يومية كاملة.
تُقرأ منها الخمس محطات فقط.

ما يتغيّر:
  • المبيعات الشهرية — صف يوليو في الجدول · عمود في الرسمين · بطاقة شهر
    يوليو · صف في مزيج الوقود.
  • المبيعات اليومية — الصفحة تُعاد كاملة على 212 يومًا (يناير → يوليو):
    الإيراد والزيارات مطابقان تمامًا لما كان، واللترات صارت **مقيسة يوميًا**
    من المصدر بدل اشتقاقها بنسبة الفترة كما كانت.
  • ترويسة الصفحة الأولى ومؤشرات الشبكة تُحدَّث للفترة الجديدة.

    python3 tools/add_july.py [ملف-المصدر] [ملف-المخرَج]
"""
import json, re, os, sys, math, datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data", "08-july-dashboard-2026.json")
SRC = OUT = os.path.join(BASE, "darb-five-stations-analysis.html")
if len(sys.argv) > 1:
    SRC = sys.argv[1]
    OUT = sys.argv[2] if len(sys.argv) > 2 else SRC

KEEP = ["MK007", "MK017", "MK002", "MK023", "MK019"]
MONTH_AR = {1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل", 5: "مايو",
            6: "يونيو", 7: "يوليو"}
DOW_AR = ["الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]


def HR(h):
    """17 → «5م» — نظام 12 ساعة كما في بقية الجداول."""
    h = int(h)
    if h == 0:  return "12ص"
    if h == 12: return "12م"
    return f"{h-12}م" if h > 12 else f"{h}ص"

F = lambda n: f"{round(n):,}"
def M(n):
    a = abs(n)
    if a >= 1_000_000: return f"{n/1_000_000:.1f}م"
    if a >= 1000:      return f"{n/1000:.0f}ألف"
    return f"{round(n)}"

D = json.load(open(DATA, encoding="utf-8"))
ST = {s["code"]: s for s in D["stations"]}
doc = open(SRC, encoding="utf-8").read()
assert "<td><b>يوليو</b></td><td>31</td>" not in doc, "يوليو مضاف سلفًا"


# ═══════════ رسم الأعمدة الشهرية ═══════════
def bars(vals, labels, fmt, gid):
    """يعيد بناء الرسم العمودي بلغة الرسم نفسها المستعملة في الملف."""
    W, base, top = 640, 160.0, 26.0
    L = 33.75
    avail = W - 2 * L
    n = len(vals)
    b = avail / (n + (n - 1) * 0.589)
    g = b * 0.589
    mx = max(vals) or 1
    hi = vals.index(mx)
    out = (f'<svg viewBox="0 0 {W} 206" class="bigchart" role="img"><defs>'
           f'<linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
           f'<stop offset="0" stop-color="#F5A623"></stop>'
           f'<stop offset="1" stop-color="#F37021"></stop></linearGradient></defs>')
    for i, v in enumerate(vals):
        h = (v / mx) * (base - top)
        x = L + i * (b + g)
        y = base - h
        fill = f"url(#{gid})" if i == hi else "var(--bar)"
        out += (f'<rect x="{x:.1f}" y="{y:.1f}" width="{b:.1f}" height="{h:.1f}" rx="5" '
                f'fill="{fill}"></rect>'
                f'<text x="{x+b/2:.1f}" y="{y-6:.1f}" font-size="11" font-weight="700" '
                f'text-anchor="middle" fill="var(--ink)">{fmt(v)}</text>'
                f'<text x="{x+b/2:.1f}" y="178.0" font-size="11" text-anchor="middle" '
                f'fill="var(--ink2)">{labels[i]}</text>')
    return out + "</svg>"


# ═══════════ رسم السلسلة اليومية ═══════════
def line_chart(days, ratio):
    W, H = 1010, 240
    x0, x1, y0, y1 = 46.0, 912.0, 10.0, 214.0
    revs = [d["rev"] for d in days]
    mx = max(revs) or 1
    n = len(days)
    X = lambda i: x0 + (x1 - x0) * (i / max(1, n - 1))
    Y = lambda v: y1 - (v / mx) * (y1 - y0)
    out = (f'<svg viewBox="0 0 {W} {H}" class="bigchart" role="img" '
           f'aria-label="الإيراد اليومي">')
    for frac in (1.0, 0.5):
        y = Y(mx * frac)
        out += (f'<line x1="{x0:.0f}" y1="{y:.1f}" x2="{x1:.0f}" y2="{y:.1f}" '
                f'stroke="var(--line)" stroke-dasharray="2 4"></line>'
                f'<text x="{x0-6:.0f}" y="{y+4:.1f}" font-size="10" text-anchor="end" '
                f'fill="var(--ink3)">{M(mx*frac)}</text>')
    seen = set()
    for i, d in enumerate(days):
        mo = int(d["date"][5:7])
        if mo in seen:
            continue
        seen.add(mo)
        x = X(i)
        out += (f'<line x1="{x:.1f}" y1="{y0:.0f}" x2="{x:.1f}" y2="{y1:.0f}" '
                f'stroke="var(--line)" stroke-dasharray="2 4"></line>'
                f'<text x="{x+4:.1f}" y="232" font-size="11" fill="var(--ink2)">'
                f'{MONTH_AR[mo]}</text>')
    pts = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(revs))
    out += (f'<polyline points="{pts}" fill="none" stroke="var(--bar)" '
            f'stroke-width="1.4"></polyline>')
    ma = []
    for i in range(n):
        w = revs[max(0, i - 6):i + 1]
        ma.append(sum(w) / len(w))
    pts = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(ma))
    out += (f'<polyline points="{pts}" fill="none" stroke="#F37021" stroke-width="2.6" '
            f'stroke-linejoin="round"></polyline>')
    for frac in (1.0, 0.5):
        y = Y(mx * frac)
        out += (f'<text x="{x1+6:.0f}" y="{y+4:.1f}" font-size="10" text-anchor="start" '
                f'fill="var(--ink3)">{M(mx*frac*ratio)} لتر</text>')
    return out + "</svg>"


# ═══════════ بطاقة شهر يوليو ═══════════
GENERIC = ["إغلاق أو تحويلة طريق", "صيانة مضخات أو توقف جزئي", "انقطاع منتج",
           "منافس جديد قريب", "تغيّر أسعار", "حملة تسويقية", "تغيّر فريق التشغيل",
           "طقس أو أمطار", "أعمال إنشائية مجاورة"]
PLACE = "اكتب الإجراء المتخذ، أو أضف سببًا مؤكدًا آخر من عندك…"


def month_card(jun, jul):
    dj, dn = jul["daily_avg_rev"], jun["daily_avg_rev"]
    ch = (dj - dn) / dn * 100 if dn else 0
    vj = jul["visits"] / jul["ndays"]
    vn = jun["visits"] / jun["ndays"]
    vch = (vj - vn) / vn * 100 if vn else 0
    lj = jul["volume"] / jul["ndays"]
    icon = "📈" if ch >= 3 else ("📉" if ch <= -3 else "➖")
    state = ("ممتاز", "c-nbh") if ch >= 8 else (("جيد", "c-hwy") if ch >= 0
             else (("يحتاج متابعة", "c-rem") if ch > -10 else ("حرج", "c-viv")))
    up, dn_ = [], []
    tgt = up if ch >= 0 else dn_
    tgt.append(f'الإيراد اليومي {"+" if ch>=0 else ""}{ch:.0f}٪ عن يونيو '
               f'({F(dn)} ← {F(dj)} ر.س)')
    (up if vch >= 0 else dn_).append(
        f'الزيارات اليومية {"+" if vch>=0 else ""}{vch:.0f}٪ ({F(vn)} ← {F(vj)} سيارة/يوم)')
    dr, dv = dj - dn, (vj - vn) * jul["avg_invoice"]
    if dr:
        share = abs(dv) / abs(dr) * 100
        (up if ch >= 0 else dn_).append(
            f'<b>مصدر التغير:</b> نحو {share:.0f}٪ منه يعود إلى '
            f'<b>{"عدد الزيارات" if share>=50 else "متوسط الفاتورة"}</b> لا إلى الطرف الآخر')
    (up if jul["avg_invoice"] >= jun["avg_invoice"] else dn_).append(
        f'متوسط الفاتورة {jun["avg_invoice"]:.0f} ← {jul["avg_invoice"]:.0f} ر.س')
    up.append(f'شهر كامل مسجَّل ({jul["ndays"]} يومًا) · ذروة الزيارات '
              f'{HR(jul["peak_vis_hour"])}')
    if not dn_:
        dn_.append("لا مؤشر سالب في أرقام هذا الشهر مقابل يونيو")

    def ul(items):
        return "<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>"

    chips = "".join(f'<span class="hchip">{c}</span>' for c in GENERIC)
    return (
        f'<details class="mdet"><summary>{icon} <b>يوليو</b>'
        f'<span class="msum">{ch:+.0f}٪ عن الشهر السابق · {F(dj)} ر.س/يوم · '
        f'{jul["ndays"]} يومًا</span>'
        f'<span class="cls {state[1]} mstate" title="اضغط لتغيير الحالة">{state[0]}</span>'
        f'</summary><div class="mbody"><div class="mnums">'
        f'<span>إيراد/يوم <b>{F(dj)}</b> ر.س</span>'
        f'<span>زيارات/يوم <b>{F(vj)}</b></span>'
        f'<span>فاتورة <b>{jul["avg_invoice"]:.0f}</b> ر.س</span>'
        f'<span>لترات <b>{M(jul["volume"])}</b></span>'
        f'<span>لترات/يوم <b>{F(lj)}</b></span>'
        f'<span>ذروة <b>{HR(jul["peak_vis_hour"])}</b></span>'
        f'<span>أيام مسجلة <b>{jul["ndays"]}</b></span></div>'
        f'<div class="mline up"><b>▲ سبب الارتفاع</b>{ul(up)}</div>'
        f'<div class="mline dn"><b>▼ سبب الانخفاض</b>{ul(dn_)}</div>'
        f'<div class="mline hyp"><b>أسباب مرشّحة للتحقق</b>'
        f'<div class="mnote">لا يوجد نص تحليل لهذا الشهر في تقرير الأسباب '
        f'(ينتهي عند يونيو)، فلم تُعلَّم أي رقاقة. اضغط ما ينطبق ليُعلَّم.</div>'
        f'<div class="hchips">{chips}</div></div>'
        f'<div class="mline act"><b>✅ السبب المؤكد والإجراء</b>'
        f'<div class="cfrm none">لم يرد يوليو في تقرير التحليل التفصيلي — '
        f'أرقامه من لوحة المبيعات، والسبب يُكتب هنا.</div>'
        f'<p class="mfree">{PLACE}</p></div></div></details>')


# ═══════════ التطبيق على كل محطة ═══════════
log = []
for code in KEEP:
    s = ST[code]
    mo = s["monthly"]
    months = [f"2026-{m:02d}" for m in range(1, 8)]
    jul, jun = mo["2026-07"], mo["2026-06"]

    page = re.search(r'id="pg-%s-monthly".*?(?=<div class="pgview")' % code, doc, re.S).group(0)
    new = page

    # ── 1. صف يوليو في الجدول الشهري ──
    prev_daily = jun["daily_avg_rev"]
    ch = (jul["daily_avg_rev"] - prev_daily) / prev_daily * 100
    cls = "up" if ch >= 0 else "dn"
    row = (f'<tr><td><b>يوليو</b></td><td>{jul["ndays"]}</td><td>{F(jul["revenue"])}</td>'
           f'<td>{F(jul["visits"])}</td><td>{F(jul["volume"])}</td>'
           f'<td>{jul["avg_invoice"]:.0f}</td>'
           f'<td>{F(jul["daily_avg_rev"])}</td>'
           f'<td>{F(jul["volume"]/jul["ndays"])}</td>'
           f'<td>{HR(jul["peak_vis_hour"])}</td>'
           f'<td><span class="{cls}">{ch:+.0f}٪</span></td></tr>')
    new, k = re.subn(r'(<td><b>يونيو</b></td>.*?</tr>)', lambda g: g.group(1) + row,
                     new, count=1, flags=re.S)
    assert k == 1, (code, "monthly row")

    # ── 2. الرسمان ──
    labels = [MONTH_AR[i] for i in range(1, 8)]
    revs = [mo[m]["revenue"] for m in months]
    davg = [mo[m]["daily_avg_rev"] for m in months]
    boxes = list(re.finditer(r'(<div class="chartbox">.*?)<svg.*?</svg>', new, re.S))
    assert len(boxes) >= 2, (code, len(boxes))
    new = (new[:boxes[0].start()] + boxes[0].group(1) + bars(revs, labels, M, f"gR-{code}")
           + new[boxes[0].end():])
    boxes = list(re.finditer(r'(<div class="chartbox">.*?)<svg.*?</svg>', new, re.S))
    new = (new[:boxes[1].start()] + boxes[1].group(1) + bars(davg, labels, M, f"gD-{code}")
           + new[boxes[1].end():])

    # ── 3. مزيج الوقود ──
    fu = {f["fuel"]: f["rev"] for f in jul["fuels"]}
    tot = sum(fu.values()) or 1
    frow = (f'<tr><td><b>يوليو</b></td><td>{fu.get("Gasoline 91",0)/tot*100:.0f}٪</td>'
            f'<td>{fu.get("Gasoline 95",0)/tot*100:.0f}٪</td>'
            f'<td>{fu.get("Diesel",0)/tot*100:.0f}٪</td></tr>')
    seg = re.search(r'(مزيج الوقود شهريًا.*?<td><b>يونيو</b></td>.*?</tr>)', new, re.S)
    new = new[:seg.end()] + frow + new[seg.end():]

    # ── 4. بطاقة يوليو ──
    j = new.rindex("</details>") + len("</details>")
    new = new[:j] + month_card(jun, jul) + new[j:]

    doc = doc.replace(page, new, 1)

    # ═══════ الصفحة اليومية — إعادة بناء على 212 يومًا ═══════
    days = s["overall"]["daily"]
    dpage = re.search(r'id="pg-%s-daily".*?(?=<div class="pgview")' % code, doc, re.S).group(0)
    nd = dpage
    tot_rev = sum(d["rev"] for d in days)
    tot_vol = sum(d["vol"] for d in days)
    n = len(days)
    ratio = tot_vol / tot_rev * 1000
    best = max(days, key=lambda d: d["rev"])
    worst = min(days, key=lambda d: d["rev"])
    last30 = days[-30:]
    prev30 = days[-60:-30]
    a30 = sum(d["rev"] for d in last30) / len(last30)
    p30 = sum(d["rev"] for d in prev30) / len(prev30)
    delta = (a30 - p30) / p30 * 100
    mean = tot_rev / n
    cv = math.sqrt(sum((d["rev"] - mean) ** 2 for d in days) / n) / mean * 100
    dow = lambda ds: DOW_AR[datetime.date(*map(int, ds.split("-"))).weekday()]

    kpis = (
        '<div class="skpis" style="grid-template-columns:repeat(6,1fr)">'
        f'<div class="kpi hot"><div class="kl">متوسط الإيراد اليومي</div>'
        f'<div class="kv">{M(mean)} <small>ر.س</small></div>'
        f'<div class="kv kvl">{M(tot_vol/n)} <small>لتر</small></div>'
        f'<div class="kn">{n} يومًا مسجلًا · {F(tot_vol/n)} لتر/يوم</div></div>'
        f'<div class="kpi"><div class="kl">متوسط اللترات اليومية</div>'
        f'<div class="kv">{F(tot_vol/n)} <small>لتر</small></div>'
        f'<div class="kn">إجمالي الفترة {F(tot_vol)} لتر</div></div>'
        f'<div class="kpi"><div class="kl">أفضل يوم</div>'
        f'<div class="kv">{F(best["rev"])} <small>ر.س</small></div>'
        f'<div class="kn">{best["date"]} ({dow(best["date"])}) · {F(best["vol"])} لتر</div></div>'
        f'<div class="kpi"><div class="kl">أدنى يوم</div>'
        f'<div class="kv">{F(worst["rev"])} <small>ر.س</small></div>'
        f'<div class="kn">{worst["date"]} ({dow(worst["date"])}) · {F(worst["vol"])} لتر</div></div>'
        f'<div class="kpi"><div class="kl">آخر 30 يومًا مقابل ما قبلها</div>'
        f'<div class="kv"><span class="{"up" if delta>=0 else "dn"}">{delta:+.0f}٪</span></div>'
        f'<div class="kn">على متوسط الإيراد اليومي</div></div>'
        f'<div class="kpi"><div class="kl">التذبذب اليومي</div>'
        f'<div class="kv">{cv:.0f}٪ <small>CV</small></div>'
        f'<div class="kn">أقل = أكثر استقرارًا</div></div></div>')
    nd = re.sub(r'<div class="skpis"[^>]*>.*?</div>\s*(?=<div class="chartbox")',
                lambda g: kpis, nd, count=1, flags=re.S)

    cs = ('<div class="cs">الخط الرمادي: القيم اليومية · الخط البرتقالي: متوسط متحرك '
          '7 أيام · المحور الأيسر بالريال والأيمن بما يعادله لترات '
          f'(بنسبة الفترة: {ratio:.0f} لتر لكل 1,000 ر.س)</div>')
    nd = re.sub(r'(<div class="chartbox"><h3>الإيراد اليومي عبر الفترة</h3>)'
                r'<div class="cs">.*?</div><svg.*?</svg>',
                lambda g: g.group(1) + cs + line_chart(days, ratio), nd, count=1, flags=re.S)

    body = "".join(
        f'<tr><td>{d["date"]}</td><td>{dow(d["date"])}</td><td>{F(d["rev"])}</td>'
        f'<td>{F(d["vol"])}</td><td>{F(d["vis"])}</td>'
        f'<td>{d["rev"]/d["vis"]:.0f}</td><td>{d["vol"]/d["vis"]:.0f}</td></tr>'
        for d in reversed(days))
    nd, k = re.subn(r'(<tbody>).*?(</tbody>)', lambda g: g.group(1) + body + g.group(2),
                    nd, count=1, flags=re.S)
    assert k == 1, (code, "daily body")
    nd = re.sub(r'الأحدث أولًا — [\d-]+ ← [\d-]+',
                f'الأحدث أولًا — {days[-1]["date"]} ← {days[0]["date"]}', nd, count=1)
    nd = nd.replace("<th>اللترات*</th>", "<th>اللترات</th>")
    nd = nd.replace("<th>لتر/زيارة*</th>", "<th>لتر/زيارة</th>")
    nd = nd.replace("متوسط اللترات اليومية*", "متوسط اللترات اليومية")
    note = ('<div class="dnote">📐 <b>اللترات مقيسة يوميًا</b> من تصدير لوحة المبيعات '
            '(دفعة 2026-08-12) لا مشتقّة بنسبة الفترة كما كانت — الإيراد والزيارات لم '
            f'يتغيّرا. الفترة الآن {n} يومًا: يناير → يوليو 2026.</div>')
    nd = re.sub(r'(<div class="ntable"><div class="tscroll"><table>.*?</table></div></div>)',
                lambda g: g.group(1) + note, nd, count=1, flags=re.S)
    doc = doc.replace(dpage, nd, 1)

    # ═══════ تبويب المستهدفات — تسجيل فعلي يوليو مقابل موازنته ═══════
    tpage = re.search(r'id="pg-%s-targets".*?(?=<div class="pgview")' % code, doc, re.S).group(0)
    nt = tpage
    jrow = re.search(r'<tr><td><b>يوليو</b></td><td>([\d,]+)</td>.*?</tr>', nt, re.S)
    bud = int(jrow.group(1).replace(",", ""))
    prev25 = re.findall(r"<td>(.*?)</td>", jrow.group(0), re.S)[-2]
    act = jul["volume"]
    diff = act - bud
    pct = act / bud * 100 if bud else 0
    g25 = (f'<span class="{"up" if act>=float(prev25.replace(",","")) else "dn"}">'
           f'{(act-float(prev25.replace(",","")))/float(prev25.replace(",",""))*100:+.0f}٪</span>'
           if re.fullmatch(r"[\d,]+", prev25 or "") else "—")
    newrow = (f'<tr><td><b>يوليو</b></td><td>{F(bud)}</td><td>{F(act)}</td>'
              f'<td>{"+" if diff>=0 else ""}{F(diff)}</td>'
              f'<td><span class="{"up" if pct>=100 else "dn"}">{pct:.0f}٪</span></td>'
              f'<td>{prev25}</td><td>{g25}</td></tr>')
    nt = nt.replace(jrow.group(0), newrow, 1)

    #  صف الإجمالي على سبعة أشهر
    trow = re.search(r'<tr([^>]*)><td>إجمالي الأشهر المسجلة</td>'
                     r'<td>([\d,]+)</td><td>([\d,]+)</td>.*?</tr>', nt, re.S)
    tstyle = trow.group(1)
    tb = int(trow.group(2).replace(",", "")) + bud
    ta = int(trow.group(3).replace(",", "")) + act
    td_ = ta - tb
    tp = ta / tb * 100 if tb else 0
    tail = re.findall(r"<td>(.*?)</td>", trow.group(0), re.S)[-2:]
    nt = nt.replace(trow.group(0),
        f'<tr{tstyle}><td>إجمالي الأشهر المسجلة</td><td>{F(tb)}</td><td>{F(ta)}</td>'
        f'<td>{"+" if td_>=0 else ""}{F(td_)}</td>'
        f'<td><span class="{"up" if tp>=100 else "dn"}">{tp:.0f}٪</span></td>'
        f'<td>{tail[0]}</td><td>{tail[1]}</td></tr>', 1)

    #  مؤشرات الرأس
    rows7 = re.findall(r'<tr><td><b>(\S+)</b></td><td>([\d,]+)</td><td>([\d,]+)</td>', nt)
    done = [(a, int(b.replace(",", "")), int(c.replace(",", ""))) for a, b, c in rows7
            if a in MONTH_AR.values()]
    hits = sum(1 for _, b, a2 in done if a2 >= b)
    pcts = [(m2, a2 / b * 100) for m2, b, a2 in done if b]
    best = max(pcts, key=lambda x: x[1]); worst = min(pcts, key=lambda x: x[1])
    yr = int(re.search(r'(\d[\d,]*) لتر لعام 2026', nt).group(1).replace(",", ""))
    rem = yr - tb
    nt = re.sub(r'(<div class="kl">موازنة الأشهر المنفَّذة</div><div class="kv">)[^<]*(<small> لتر</small></div>'
                r'<div class="kn">)[^<]*(</div>)',
                lambda g: g.group(1) + f"{tb/1e6:.1f}م" + g.group(2)
                + f"{len(done)} أشهر (يناير → يوليو)" + g.group(3), nt, count=1)
    nt = re.sub(r'(<div class="kl">الفعلي</div><div class="kv">)[^<]*(<small> لتر</small></div>'
                r'<div class="kn">)الفرق [^<]*(</div>)',
                lambda g: g.group(1) + f"{ta/1e6:.1f}م" + g.group(2)
                + f'الفرق {"+" if td_>=0 else ""}{F(td_)} لتر' + g.group(3), nt, count=1)
    nt = re.sub(r'(الإنجاز</div><div class="kv" style="color:)#[0-9A-Fa-f]{6}(">)\d+٪',
                lambda g: g.group(1) + ("#2E8B6F" if tp >= 100 else "#C0503A")
                + g.group(2) + f"{tp:.0f}٪", nt, count=1)
    nt = re.sub(r'(أشهر بلغت الهدف</div><div class="kv">)\d+ <small>من \d+</small>'
                r'(</div><div class="kn">)[^<]*(</div>)',
                lambda g: g.group(1) + f"{hits} <small>من {len(done)}</small>" + g.group(2)
                + f"أعلى {best[0]} {best[1]:.0f}٪ · أدنى {worst[0]} {worst[1]:.0f}٪"
                + g.group(3), nt, count=1)
    nt = re.sub(r'(المتبقي من الموازنة</div><div class="kv">)[^<]*(<small> لتر</small></div>'
                r'<div class="kn">)[^<]*(</div>)',
                lambda g: g.group(1) + f"{rem/1e6:.1f}م" + g.group(2)
                + f"5 أشهر · بمعدل {F(rem/5)} لتر/شهر" + g.group(3), nt, count=1)

    #  عمود الفعلي في الرسم + نسبة الإنجاز فوقه
    jb = re.search(r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"'
                   r' rx="4" fill="#B9B2A6" opacity="1"></rect><title>يوليو — الموازنة', nt)
    scale = float(jb.group(4)) / bud
    h = act * scale
    y = 160.0 - h
    lbl = min(float(jb.group(2)), y) - 6.0
    nt = re.sub(r'<rect x="([\d.]+)" y="[\d.]+" width="([\d.]+)" height="[\d.]+" rx="4"'
                r' fill="#F5831F" opacity="1"></rect><title>يوليو — الفعلي 0 لتر</title>'
                r'(<text x="([\d.]+)" y="180")',
                lambda g: (f'<rect x="{g.group(1)}" y="{y:.1f}" width="{g.group(2)}" '
                           f'height="{h:.1f}" rx="4" fill="#F5831F" opacity="1"></rect>'
                           f'<title>يوليو — الفعلي {F(act)} لتر</title>'
                           f'<text x="{g.group(4)}" y="{lbl:.1f}" font-size="11" '
                           f'font-weight="700" text-anchor="middle" '
                           f'fill="{"#2E8B6F" if pct>=100 else "#C0503A"}">{pct:.0f}٪</text>'
                           + g.group(3)), nt, count=1)
    doc = doc.replace(tpage, nt, 1)

    log.append((code, jul, ch, n, tot_vol, bud, act, pct, tp))

# ═══════════ الترويسة ومؤشرات الشبكة ═══════════
net_rev = sum(ST[c]["overall"]["revenue"] for c in KEEP)
net_vol = sum(ST[c]["overall"]["volume"] for c in KEEP)
net_vis = sum(ST[c]["overall"]["visits"] for c in KEEP)
doc = doc.replace(
    "<p>النصف الأول 2026 · 5 محطات مختارة · اختر محطة لفتح صفحتها الكاملة</p>",
    "<p>يناير → يوليو 2026 · 5 محطات مختارة · اختر محطة لفتح صفحتها الكاملة</p>", 1)
doc = re.sub(r'(<div class="v">)79\.5( <small>مليون ر\.س</small>)',
             lambda g: g.group(1) + f"{net_rev/1e6:.1f}" + g.group(2), doc, count=1)
doc = re.sub(r'إيراد الفترة للمحطات الخمس · [\d.]+ مليون لتر',
             f'إيراد الفترة للمحطات الخمس · {net_vol/1e6:.1f} مليون لتر', doc, count=1)
doc = re.sub(r'(<div class="v">)1\.39( <small>مليون</small>)',
             lambda g: g.group(1) + f"{net_vis/1e6:.2f}" + g.group(2), doc, count=1)

open(OUT, "w", encoding="utf-8").write(doc)
print("تم · الحجم:", round(len(doc.encode()) / 1024), "KB ·", OUT)
print(f"الشبكة (5 محطات): {net_rev/1e6:.1f} مليون ر.س · {net_vol/1e6:.1f} مليون لتر "
      f"· {net_vis/1e6:.2f} مليون زيارة")
for code, jul, ch, n, vol, bud, act, pct, tp in log:
    print(f"  {code} يوليو: {F(jul['revenue'])} ر.س · {F(jul['visits'])} زيارة · "
          f"{F(jul['volume'])} لتر · {jul['ndays']} يومًا · {ch:+.0f}٪ عن يونيو "
          f"| اليومية {n} يومًا | الموازنة {F(bud)} → إنجاز {pct:.0f}٪ "
          f"| الإجمالي المسجّل {tp:.0f}٪")
