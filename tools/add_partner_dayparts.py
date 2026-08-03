# -*- coding: utf-8 -*-
"""يضيف لكل محطة صفحة «الشركاء عبر اليوم»: قراءة حركة كل فترة وفرصتها للشركاء."""
import openpyxl, re, html, unicodedata

XLSX = "/root/.claude/uploads/447348d0-0f0b-5d32-9f6b-27c9ad645473/7761cf91-Darb__Units.xlsx"
SRC = OUT = "/home/user/-/darb-five-stations-analysis.html"
KEEP = ["MK007", "MK017", "MK002", "MK023", "MK019"]

#  الفترات الست — نفس تقسيم «قراءة الحركة الصباحية»
PERIODS = [
    ("bmn", 0,  5,  "بعد منتصف الليل", "00:00 – 05:00", "#55565A"),
    ("fjr", 5,  8,  "فجر وشروق",       "05:00 – 08:00", "#3E6E8E"),
    ("dha", 8,  11, "ضحى",             "08:00 – 11:00", "#2E8B6F"),
    ("zhr", 11, 15, "ظهر",             "11:00 – 15:00", "#C98A1B"),
    ("asr", 15, 20, "عصر ومغرب",       "15:00 – 20:00", "#F5831F"),
    ("lyl", 20, 24, "ليل",             "20:00 – 24:00", "#6B4E9B"),
]
#  الفئات التي تخدم كل فترة عادةً — طبقة توصية لا قياس
FIT = {
    "bmn": ["cafe", "market"],
    "fjr": ["cafe", "rest"],
    "dha": ["cafe", "car"],
    "zhr": ["rest", "market"],
    "asr": ["rest", "cafe", "market"],
    "lyl": ["rest", "cafe"],
}
CATS = [("rest", "مطاعم", "Restaurants"), ("cafe", "مقاهٍ", "Cafe"),
        ("car", "خدمات سيارات", "Car Services"), ("market", "سوبرماركت", "Market")]
CATN = {k: n for k, n, _ in CATS}

OCCUPANCY = 2          # راكبان لكل سيارة — فرضية
TICKET = 20            # ر.س لفاتورة الفطور/الوجبة — فرضية
RATES = [1, 3, 5, 8]   # معدلات الالتقاط المعروضة

E = lambda t: html.escape(str(t), quote=True)
F = lambda n: f"{round(n):,}"
AR = lambda n: str(n)  # أرقام غربية اتساقًا مع بقية التقرير

# ═══════════ 1. الشركاء من ملف الوحدات ═══════════
wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
ws = wb["Stations 2025"]
rows = list(ws.iter_rows(values_only=True))
hdr = [str(c).strip() if c else "" for c in rows[0]]

def split_units(v):
    if v is None:
        return []
    parts = re.split(r"[\n\-–—·,،/]+", str(v))
    out, seen = [], set()
    for p in parts:
        p = unicodedata.normalize("NFKC", p).strip(" \t.()")
        if len(p) < 2:
            continue
        key = re.sub(r"\s+", "", p)
        if key not in seen:
            seen.add(key)
            out.append(p)
    return out

PARTNERS = {}
for r in rows[1:]:
    if not r or not r[0]:
        continue
    code = str(r[0]).strip().upper().replace(" ", "")
    if code not in KEEP:
        continue
    d = {"cats": {}, "extra": {}}
    for key, _, col in CATS:
        d["cats"][key] = split_units(r[hdr.index(col)] if col in hdr else None)
    for col, lbl in (("كشك", "أكشاك"), ("محل", "محلات"), ("درايف قرو", "درايف ثرو"), ("صراف", "صرافات")):
        if col in hdr:
            v = r[hdr.index(col)]
            if isinstance(v, (int, float)) and v:
                d["extra"][lbl] = int(v)
    d["street"] = str(r[hdr.index("Street/Road")] or "").strip()
    PARTNERS[code] = d
missing = [c for c in KEEP if c not in PARTNERS]
assert not missing, missing

def uniq_total(p):
    seen = set()
    for lst in p["cats"].values():
        for u in lst:
            seen.add(re.sub(r"\s+", "", u))
    return len(seen)

# ═══════════ 2. حركة الساعات من التقرير ═══════════
src = open(SRC, encoding="utf-8").read()
pages_head, pages_all = src.split('<main class="wrap" id="pages">', 1)
blocks = re.split(r'(?=<div class="pgview")', pages_all)
lead, blocks = blocks[0], blocks[1:]
PG, ORDER = {}, []
for b in blocks:
    k = re.search(r'id="pg-([\w-]+)"', b).group(1)
    PG[k] = b
    ORDER.append(k)

TRAFFIC = {}
for c in KEEP:
    chart = re.search(r'الزيارات على مدار اليوم \(24 ساعة\)</div>(<svg.*?</svg>)', PG[c], re.S).group(1)
    H = [0] * 24
    for hh, ap, v in re.findall(r'<title>الساعة (\d+)(ص|م) — ([\d,]+) زيارة', chart):
        H[int(hh) % 12 + (12 if ap == "م" else 0)] = int(v.replace(",", ""))
    days = int(re.search(r'<div class="kn">(\d+) يومًا مسجلًا', PG[c + "-daily"]).group(1))
    inv = int(re.search(r'<div class="kl">متوسط الفاتورة</div><div class="kv">(\d+)', PG[c]).group(1))
    lit = int(re.search(r'متوسط التعبئة (\d+) لترًا', PG[c]).group(1))
    TRAFFIC[c] = {"hours": [h / days for h in H], "total": sum(H) / days,
                  "days": days, "inv": inv, "lit": lit}

# ═══════════ 3. عناصر العرض ═══════════
def day_chart(hours):
    mx = max(hours) or 1
    W, n = 1100, 24
    step = (W - 30) / n
    bw = step - 9
    out = []
    for h in range(n):
        col = next(c for _, a, b, _, _, c in PERIODS if a <= h < b)
        ht = hours[h] / mx * 130
        x = 15 + h * step + 4.5
        cx = x + bw / 2
        y = 172 - ht
        ampm = ("12ص" if h == 0 else f"{h}ص" if h < 12 else "12م" if h == 12 else f"{h-12}م")
        out.append(f'<g><rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{ht:.1f}" rx="5" '
                   f'fill="{col}" opacity="{0.95 if hours[h]==mx else 0.72}"></rect>'
                   f'<title>{ampm} — {F(hours[h])} سيارة/يوم</title></g>')
        if h % 2 == 0:
            out.append(f'<text x="{cx:.1f}" y="192" font-size="12" text-anchor="middle" '
                       f'fill="var(--ink2)">{ampm}</text>')
        if hours[h] == mx:
            out.append(f'<text x="{cx:.1f}" y="{y-6:.1f}" font-size="13" font-weight="700" '
                       f'text-anchor="middle" fill="var(--ink)">{F(mx)}</text>')
    return f'<svg viewBox="0 0 1100 200" class="spark" role="img" aria-label="حركة اليوم الكامل">{"".join(out)}</svg>'

def legend():
    return '<div class="plegend">' + "".join(
        f'<span><i style="background:{col}"></i>{nm} <small>{lbl}</small></span>'
        for _, _, _, nm, lbl, col in PERIODS) + "</div>"

def capture_table(people):
    rows_ = "".join(
        f'<tr><td><b>{AR(r)}٪</b></td><td>{F(people*r/100)}</td>'
        f'<td>{F(people*r/100*7)}</td><td>{F(people*r/100*TICKET*30)} ر.س</td></tr>'
        for r in RATES)
    return ('<table class="captbl"><thead><tr><th>معدل الالتقاط</th><th>عملاء/يوم</th>'
            f'<th>عملاء/أسبوع</th><th>مبيعات شهرية عند {AR(TICKET)} ر.س</th></tr></thead>'
            f"<tbody>{rows_}</tbody></table>")

def read_line(key, share, rank, n_periods, cars, fit_units):
    """جملة قراءة مشتقة من الأرقام لا من الانطباع."""
    if rank == 1:
        head = f"أقوى فترة في اليوم — {share:.0f}٪ من حركة المحطة"
    elif rank == n_periods:
        head = f"أضعف فترة في اليوم — {share:.0f}٪ فقط من الحركة"
    else:
        head = f"الفترة رقم {AR(rank)} من {AR(n_periods)} — {share:.0f}٪ من الحركة"
    if not fit_units:
        tail = "لا توجد وحدات من الفئات التي تخدم هذه الفترة — فرصة تأجير مباشرة."
    elif cars / max(fit_units, 1) > 200:
        tail = f"{AR(fit_units)} وحدة تخدم هذه الفترة تستقبل {F(cars/fit_units)} سيارة لكل وحدة — ضغط عالٍ، الطاقة الاستيعابية هي القيد."
    else:
        tail = f"{AR(fit_units)} وحدة تخدم هذه الفترة بمعدل {F(cars/fit_units)} سيارة لكل وحدة."
    return head + " · " + tail

# ═══════════ 4. بناء الصفحات ═══════════
ez = max(int(x) for x in re.findall(r'data-ez="z(\d+)"', src))
CS_COUNT = {c: len(re.findall(r'<tr><td>\d{4}-\d\d-\d\d</td>', PG[c + "-cs"])) for c in KEEP}

def tabs_of(code, active):
    t = [("", "التحليل الكامل"), ("/monthly", "المبيعات الشهرية"), ("/daily", "المبيعات اليومية"),
         ("/cs", "استفسارات العملاء"), ("/partners", "الشركاء عبر اليوم")]
    return '<div class="tabs">' + "".join(
        f'<a class="tab{" on" if suf == active else ""}" href="#/{code}{suf}">{lbl}'
        + (f' <b class="tcount">{CS_COUNT[code]}</b>' if suf == "/cs" else "")
        + (f' <b class="tcount">{uniq_total(PARTNERS[code])}</b>' if suf == "/partners" else "")
        + "</a>" for suf, lbl in t) + "</div>"

for c in KEEP:
    t, p = TRAFFIC[c], PARTNERS[c]
    tot = t["total"]
    per = []
    for key, a, b, nm, lbl, col in PERIODS:
        cars = sum(t["hours"][a:b])
        fit = sum(len(p["cats"][k]) for k in FIT[key])
        per.append(dict(key=key, nm=nm, lbl=lbl, col=col, cars=cars, share=cars / tot * 100,
                        people=cars * OCCUPANCY, rev=cars * t["inv"], lit=cars * t["lit"],
                        hrs=b - a, fit=fit))
    order = sorted(range(len(per)), key=lambda i: -per[i]["cars"])
    for rank, i in enumerate(order, 1):
        per[i]["rank"] = rank
    best, worst = per[order[0]], per[order[-1]]
    nunits = uniq_total(p)

    kpis = (
        '<div class="skpis" style="grid-template-columns:repeat(6,1fr)">'
        f'<div class="kpi hot"><div class="kl">الشركاء داخل المحطة</div><div class="kv">{nunits}</div>'
        f'<div class="kn">' + " · ".join(f'{CATN[k]} {len(p["cats"][k])}' for k, _, _ in CATS if p["cats"][k]) + '</div></div>'
        f'<div class="kpi"><div class="kl">سيارات يوميًا</div><div class="kv">{F(tot)}</div>'
        f'<div class="kn">تمرّ أمام الوحدات على مدار اليوم</div></div>'
        f'<div class="kpi"><div class="kl">أشخاص يوميًا</div><div class="kv">{F(tot*OCCUPANCY)}</div>'
        f'<div class="kn">بفرض متحفّظ: راكبان لكل سيارة</div></div>'
        f'<div class="kpi"><div class="kl">أقوى فترة</div><div class="kv" style="font-size:17px">{best["nm"]}</div>'
        f'<div class="kn">{F(best["cars"])} سيارة/يوم · {best["share"]:.0f}٪ من اليوم</div></div>'
        f'<div class="kpi"><div class="kl">أضعف فترة</div><div class="kv" style="font-size:17px">{worst["nm"]}</div>'
        f'<div class="kn">{F(worst["cars"])} سيارة/يوم · {worst["share"]:.0f}٪ من اليوم</div></div>'
        f'<div class="kpi"><div class="kl">سيارات لكل شريك</div><div class="kv">{F(tot/nunits)}</div>'
        f'<div class="kn">يوميًا — قبل معدل الالتقاط</div></div>'
        "</div>")

    ptable = ('<div class="ntable"><div class="tscroll"><table><thead><tr>'
              '<th>الفترة</th><th>الساعات</th><th>سيارات/يوم</th><th>٪ من اليوم</th>'
              '<th>أشخاص/يوم</th><th>سيارة كل</th><th>إيراد وقود تقديري/يوم</th>'
              '<th>لترات تقديرية/يوم</th><th>وحدات تخدم الفترة</th></tr></thead><tbody>'
              + "".join(
                  f'<tr><td><b>{d["nm"]}</b></td><td>{d["lbl"]}</td><td>{F(d["cars"])}</td>'
                  f'<td>{d["share"]:.1f}٪</td><td>{F(d["people"])}</td>'
                  f'<td>{F(d["hrs"]*3600/d["cars"])} ثانية</td><td>{F(d["rev"])} ر.س</td>'
                  f'<td>{F(d["lit"])} لتر</td><td>{d["fit"]}</td></tr>' for d in per)
              + "</tbody></table></div></div>")

    cards = []
    for d in per:
        fit_names = []
        for k in FIT[d["key"]]:
            fit_names += [f'<span class="ptag">{E(u)}</span>' for u in p["cats"][k]]
        cards.append(
            f'<div class="pcard2" style="--pc:{d["col"]}">'
            f'<div class="ph"><span class="pdot"></span><h4>{d["nm"]}</h4>'
            f'<span class="phrs">{d["lbl"]}</span>'
            f'<span class="prank">#{AR(d["rank"])} في اليوم</span></div>'
            f'<div class="pnums">'
            f'<div><b>{F(d["cars"])}</b><span>سيارة/يوم</span></div>'
            f'<div><b>{F(d["people"])}</b><span>شخص/يوم</span></div>'
            f'<div><b>{d["share"]:.1f}٪</b><span>من حركة اليوم</span></div>'
            f'<div><b>{F(d["rev"])}</b><span>ر.س إيراد وقود تقديري</span></div></div>'
            f'<div class="pread">{read_line(d["key"], d["share"], d["rank"], len(per), d["cars"], d["fit"])}</div>'
            + (f'<div class="pfit"><b>الوحدات التي تخدم هذه الفترة ({d["fit"]}):</b> '
               + "".join(fit_names) + "</div>" if fit_names else
               '<div class="pfit"><b>لا توجد وحدات من فئات هذه الفترة</b> — '
               + " · ".join(CATN[k] for k in FIT[d["key"]]) + "</div>")
            + '<div class="pcap"><div class="pcaph">لو التقطت الوحدات نسبة من هذه الفترة</div>'
            + capture_table(d["people"]) + "</div></div>")

    plist = '<div class="agrid">' + "".join(
        f'<div class="card"><div class="ct"><h3>{nm}</h3><div class="leg">{len(p["cats"][k])} وحدة</div></div>'
        '<div class="ptags">' + "".join(f'<span class="ptag">{E(u)}</span>' for u in p["cats"][k]) + "</div></div>"
        for k, nm, _ in CATS if p["cats"][k]) + "</div>"
    if p["extra"]:
        plist += ('<div class="dnote" style="background:#F1EFEB">🏪 <b>وحدات مسجّلة بالعدد دون أسماء:</b> '
                  + " · ".join(f"{lbl} {n}" for lbl, n in p["extra"].items()) + "</div>")

    mini = re.search(r'<div class="mini-head">.*?</div>\s*(?=<div class="skpis")',
                     PG[c + "-monthly"], re.S).group(0)
    nav = re.search(r'<div class="pgnav">.*?</select>\s*</div>', PG[c], re.S).group(0)
    title = re.search(r'data-title="([^"]*)"', PG[c]).group(1).split(" · ")[0]
    ez += 1

    PG[c + "-partners"] = (
        f'<div class="pgview" data-ez="z{ez}" id="pg-{c}-partners" '
        f'data-title="{title} · الشركاء عبر اليوم" hidden>'
        + nav + tabs_of(c, "/partners") + mini + kpis
        + '<div class="chartbox"><h3>حركة اليوم الكامل موزّعة على الفترات</h3>'
          f'<div class="cs">متوسط السيارات في كل ساعة على مدار {AR(t["days"])} يومًا مسجلًا '
          '(النصف الأول 2026) — كل لون فترة · مرّر على أي عمود للرقم</div>'
        + day_chart(t["hours"]) + legend() + "</div>"
        + '<div class="sec-h"><h2>الفترات الست جنبًا إلى جنب</h2>'
          '<span>الإيراد واللترات تقديرية: عدد السيارات × متوسط فاتورة المحطة وتعبئتها</span></div>'
        + ptable
        + '<div class="sec-h"><h2>كل فترة على حدة</h2>'
          '<span>حجم الحركة · الوحدات التي تخدمها · قيمة كل نقطة التقاط</span></div>'
        + '<div class="pgrid">' + "".join(cards) + "</div>"
        + '<div class="sec-h" style="margin-top:22px"><h2>الشركاء داخل المحطة</h2>'
          f'<span>{nunits} وحدة حسب ملف Darb Units — {E(p["street"])}</span></div>'
        + plist
        + '<div class="dnote">📐 <b>ما هو مقيس وما هو مفترض:</b> عدد السيارات وتوزيعها على الساعات '
          f'<b>مقيس</b> من {F(t["total"]*t["days"])} تعبئة فعلية خلال {AR(t["days"])} يومًا. '
          f'الإيراد واللترات لكل فترة <b>تقديرية</b>: عدد سيارات الفترة × متوسط فاتورة المحطة '
          f'({AR(t["inv"])} ر.س) وتعبئتها ({AR(t["lit"])} لترًا) — لأن الفاتورة الفعلية تختلف بين الفترات '
          'ولا تتوفر بياناتها على مستوى العملية إلا في تقرير الترانزكشن. '
          'جدول الالتقاط <b>نموذج حسابي</b> بفرضيتين: راكبان لكل سيارة، وفاتورة '
          f'{TICKET} ر.س، وشهر 30 يومًا — وليس مبيعات مسجّلة، لأن كاشير الوحدات غير مربوط بالساعة. '
          'قائمة الشركاء من ملف Darb Units (Stations 2025). ربط الفئة بالفترة اجتهاد تشغيلي قابل للتعديل.</div>'
        + '<div class="pgnav" style="margin-top:4px"><div class="nvl">'
          f'<a class="hb" href="#/">⌂ جميع المحطات</a><a href="#/{c}">← صفحة التحليل الكامل</a>'
          "</div></div></div>")

# ═══════════ 5. التبويب الخامس في الصفحات القائمة ═══════════
for c in KEEP:
    for suf, key in (("", c), ("/monthly", c + "-monthly"), ("/daily", c + "-daily"), ("/cs", c + "-cs")):
        p2, k = re.subn(r'<div class="tabs">.*?</div>', tabs_of(c, suf), PG[key], count=1, flags=re.S)
        assert k == 1, key
        PG[key] = p2

new_order = []
for k in ORDER:
    new_order.append(k)
    if k.endswith("-cs") and k[:-3] in TRAFFIC:
        new_order.append(k[:-3] + "-partners")
pages_all = lead + "".join(PG[k] for k in new_order)

# ═══════════ 6. الأنماط ═══════════
CSS = """
<style id="partners-css">
/* ── صفحة الشركاء عبر اليوم ── */
.plegend{display:flex;gap:16px;flex-wrap:wrap;margin-top:10px;font-size:12.5px;color:var(--ink2)}
.plegend i{display:inline-block;width:11px;height:11px;border-radius:3px;margin-inline-end:6px}
.plegend small{color:var(--ink3);font-size:11px}
.pgrid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
@media(max-width:900px){.pgrid{grid-template-columns:1fr}}
.pcard2{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);
  padding:15px 17px 14px;box-shadow:var(--shadow);border-top:3px solid var(--pc)}
.pcard2 .ph{display:flex;align-items:center;gap:9px;flex-wrap:wrap;margin-bottom:12px}
.pcard2 .ph h4{font-size:17px;font-weight:800}
.pcard2 .pdot{width:11px;height:11px;border-radius:50%;background:var(--pc);flex:none}
.pcard2 .phrs{font-size:12px;color:var(--ink2);font-family:'Tajawal'}
.pcard2 .prank{margin-inline-start:auto;font-size:11.5px;font-weight:700;color:var(--pc);
  background:#FBF9F5;border:1px solid var(--line2);border-radius:8px;padding:2px 8px}
.pcard2 .pnums{display:grid;grid-template-columns:repeat(4,1fr);gap:9px;margin-bottom:11px}
.pcard2 .pnums>div{background:#FDFCFA;border:1px solid var(--line);border-radius:11px;padding:9px 10px}
.pcard2 .pnums b{display:block;font-size:19px;font-weight:800;color:var(--ink)}
.pcard2 .pnums span{font-size:10.5px;color:var(--ink3);display:block;margin-top:2px;line-height:1.35}
@media(max-width:620px){.pcard2 .pnums{grid-template-columns:1fr 1fr}}
.pcard2 .pread{font-size:12.5px;color:var(--ink2);background:#FBF6EF;border-radius:10px;
  padding:9px 12px;margin-bottom:11px;line-height:1.6}
.pcard2 .pfit{font-size:12px;color:var(--ink2);margin-bottom:11px;line-height:2}
.ptags{display:flex;flex-wrap:wrap;gap:6px}
.ptag{display:inline-block;font-size:11.5px;background:#FBF9F5;border:1px solid var(--line2);
  border-radius:8px;padding:2px 8px;color:var(--ink2);margin:2px 0}
.pcaph{font-size:11.5px;color:var(--ink3);margin-bottom:5px}
table.captbl{width:100%;font-size:12.5px}
table.captbl th{padding:6px 9px;font-size:11px}
table.captbl td{padding:6px 9px;white-space:nowrap}
table.captbl tbody tr:last-child td{border-bottom:none}
</style>
"""
doc = pages_head + '<main class="wrap" id="pages">' + pages_all
doc = doc.replace("</head>", CSS + "</head>", 1)
doc = re.sub(r'data-docid="[^"]*"', 'data-docid="darb-5st-partners-v1"', doc, count=1)
open(OUT, "w", encoding="utf-8").write(doc)

print("تم · الحجم:", round(len(doc.encode()) / 1024), "KB")
for c in KEEP:
    t = TRAFFIC[c]
    print(f'  {c}: {uniq_total(PARTNERS[c])} شريك · {F(t["total"])} سيارة/يوم')
