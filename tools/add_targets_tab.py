# -*- coding: utf-8 -*-
"""تبويب «المستهدفات» لكل محطة + إعادة تسمية عنواني أسباب الصعود والهبوط."""
import openpyxl, re

BUDGET = "/root/.claude/uploads/447348d0-0f0b-5d32-9f6b-27c9ad645473/994d4b5d-________Sales_Analysis_2026_Actual_vs_Budget_30.04.2026.xlsx"
SRC = OUT = "/home/user/-/darb-five-stations-analysis.html"
KEEP = ["MK007", "MK017", "MK002", "MK023", "MK019"]
MON = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
       "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]

F = lambda n: f"{round(n):,}"
def AB(n):
    n = round(n)
    return f"{n/1_000_000:.1f}م" if n >= 1_000_000 else (f"{round(n/1000):,}ألف" if n >= 1000 else f"{n:,}")

# ═══════════ 1. الموازنة والفعلي من ملف Actual vs Budget ═══════════
wb = openpyxl.load_workbook(BUDGET, data_only=True)
rows = list(wb["Sales Analysis 2026"].iter_rows(values_only=True))
N0 = lambda v: v if isinstance(v, (int, float)) else 0
BU = {}
for i in range(2, 970, 11):
    b = rows[i:i + 11]
    if not b[0][1]:
        continue
    d = {}
    for r in b:
        d[str(r[5]).strip()] = [N0(r[6 + j]) for j in range(12)]
    BU[str(b[0][2]).strip()] = d

src = open(SRC, encoding="utf-8").read()

# ═══════════ 2. إعادة تسمية العنوانين ═══════════
src, n1 = re.subn(r'▲ ما دفع للأعلى', "▲ سبب الارتفاع", src)
src, n2 = re.subn(r'▼ ما ضغط للأسفل', "▼ سبب الانخفاض", src)
#  أقل من 30 لأن بعض الأشهر بلا نقاط في أحد الاتجاهين فلا يُطبع عنوانه
assert n1 and n2, (n1, n2)

# ═══════════ 3. تقسيم الصفحات ═══════════
pages_head, pages_all = src.split('<main class="wrap" id="pages">', 1)
blocks = re.split(r'(?=<div class="pgview")', pages_all)
lead, blocks = blocks[0], blocks[1:]
PG, ORDER = {}, []
for b in blocks:
    k = re.search(r'id="pg-([\w-]+)"', b).group(1)
    PG[k] = b
    ORDER.append(k)

ez = max(int(x) for x in re.findall(r'data-ez="z(\d+)"', src))
CS_COUNT = {c: len(re.findall(r'<tr><td>\d{4}-\d\d-\d\d</td>', PG[c + "-cs"])) for c in KEEP}
PT_COUNT = {c: int(re.search(r'الشركاء داخل المحطة</div><div class="kv">(\d+)',
                             PG[c + "-partners"]).group(1)) for c in KEEP}

def tabs_of(code, active):
    t = [("", "التحليل الكامل"), ("/monthly", "المبيعات الشهرية"), ("/daily", "المبيعات اليومية"),
         ("/targets", "المستهدفات"), ("/cs", "استفسارات العملاء"), ("/partners", "الشركاء عبر اليوم")]
    return '<div class="tabs">' + "".join(
        f'<a class="tab{" on" if suf == active else ""}" href="#/{code}{suf}">{lbl}'
        + (f' <b class="tcount">{CS_COUNT[code]}</b>' if suf == "/cs" else "")
        + (f' <b class="tcount">{PT_COUNT[code]}</b>' if suf == "/partners" else "")
        + "</a>" for suf, lbl in t) + "</div>"

# ═══════════ 4. رسم الموازنة مقابل الفعلي ═══════════
def chart(bu, ac):
    mx = max(max(bu), max(ac)) or 1
    W, n = 1100, 12
    step = (W - 30) / n
    bw = (step - 14) / 2
    out = []
    for j in range(n):
        x = 15 + j * step + 7
        for k, (v, col, op) in enumerate([(bu[j], "#B9B2A6", 1), (ac[j], "#F5831F", 1)]):
            h = v / mx * 128
            xx = x + k * (bw + 2)
            out.append(f'<rect x="{xx:.1f}" y="{160-h:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="4" '
                       f'fill="{col}" opacity="{op}"></rect>'
                       f'<title>{MON[j]} — {"الموازنة" if k==0 else "الفعلي"} {F(v)} لتر</title>')
        if ac[j] and bu[j]:
            r = ac[j] / bu[j] * 100
            out.append(f'<text x="{x+bw:.1f}" y="{160-max(bu[j],ac[j])/mx*128-6:.1f}" font-size="11" '
                       f'font-weight="700" text-anchor="middle" '
                       f'fill="{"#2E8B6F" if r>=100 else "#C0503A"}">{r:.0f}٪</text>')
        out.append(f'<text x="{x+bw:.1f}" y="180" font-size="11.5" text-anchor="middle" '
                   f'fill="var(--ink2)">{MON[j]}</text>')
    return (f'<svg viewBox="0 0 1100 190" class="spark" role="img" aria-label="الموازنة مقابل الفعلي">'
            f'{"".join(out)}</svg>'
            '<div class="plegend"><span><i style="background:#B9B2A6"></i>الموازنة (المستهدف)</span>'
            '<span><i style="background:#F5831F"></i>الفعلي</span>'
            '<span>النسبة أعلى كل شهر = الإنجاز</span></div>')

# ═══════════ 5. بناء صفحة المستهدفات ═══════════
for c in KEEP:
    s = BU[c]
    bu, ac = s["BU.2026"], s["Act.2026"]
    a25 = s["Act.2025"]
    done = [j for j in range(12) if ac[j]]
    bu6, ac6 = sum(bu[j] for j in done), sum(ac[j] for j in done)
    yr = sum(bu)
    rest = yr - bu6
    hit = sum(1 for j in done if ac[j] >= bu[j])
    best = max(done, key=lambda j: ac[j] / bu[j]) if done else 0
    worst = min(done, key=lambda j: ac[j] / bu[j]) if done else 0

    kpis = (
        '<div class="skpis" style="grid-template-columns:repeat(6,1fr)">'
        f'<div class="kpi hot"><div class="kl">موازنة السنة</div><div class="kv">{AB(yr)}<small> لتر</small></div>'
        f'<div class="kn">{F(yr)} لتر لعام 2026</div></div>'
        f'<div class="kpi"><div class="kl">موازنة الأشهر المنفَّذة</div><div class="kv">{AB(bu6)}<small> لتر</small></div>'
        f'<div class="kn">{len(done)} أشهر (يناير → {MON[done[-1]] if done else "—"})</div></div>'
        f'<div class="kpi"><div class="kl">الفعلي</div><div class="kv">{AB(ac6)}<small> لتر</small></div>'
        f'<div class="kn">الفرق {"+" if ac6>=bu6 else ""}{F(ac6-bu6)} لتر</div></div>'
        f'<div class="kpi"><div class="kl">الإنجاز</div>'
        f'<div class="kv" style="color:{"#2E8B6F" if ac6>=bu6 else "#C0503A"}">{ac6/bu6*100:.0f}٪</div>'
        f'<div class="kn">الفعلي ÷ الموازنة للأشهر المسجلة</div></div>'
        f'<div class="kpi"><div class="kl">أشهر بلغت الهدف</div><div class="kv">{hit} <small>من {len(done)}</small></div>'
        f'<div class="kn">أعلى {MON[best]} {ac[best]/bu[best]*100:.0f}٪ · أدنى {MON[worst]} {ac[worst]/bu[worst]*100:.0f}٪</div></div>'
        f'<div class="kpi"><div class="kl">المتبقي من الموازنة</div><div class="kv">{AB(rest)}<small> لتر</small></div>'
        f'<div class="kn">{12-len(done)} أشهر · بمعدل {F(rest/max(12-len(done),1))} لتر/شهر</div></div>'
        "</div>")

    trows = ""
    for j in range(12):
        has = bool(ac[j])
        diff = ac[j] - bu[j] if has else None
        r = ac[j] / bu[j] * 100 if has and bu[j] else None
        g = ac[j] / a25[j] - 1 if has and a25[j] else None
        c_act = F(ac[j]) if has else '<span class="tcode">لم يُسجَّل بعد</span>'
        c_diff = ("+" if diff and diff > 0 else "") + F(diff) if diff is not None else "—"
        c_ach = '<span class="%s">%.0f٪</span>' % ("up" if r >= 100 else "dn", r) if r else "—"
        c_g = '<span class="%s">%+.0f٪</span>' % ("up" if g >= 0 else "dn", g * 100) if g is not None else "—"
        trows += ("<tr><td><b>%s</b></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                  % (MON[j], F(bu[j]) if bu[j] else "—", c_act, c_diff, c_ach,
                     F(a25[j]) if a25[j] else "—", c_g))
    tot_diff = ac6 - bu6
    s25 = sum(a25[j] for j in done)
    c_g_tot = '<span class="%s">%+.0f٪</span>' % (
        "up" if ac6 >= s25 else "dn", (ac6 / s25 - 1) * 100) if s25 else "—"
    trows += (f'<tr style="background:#FBF6EF;font-weight:800"><td>إجمالي الأشهر المسجلة</td>'
              f'<td>{F(bu6)}</td><td>{F(ac6)}</td>'
              f'<td>{"+" if tot_diff>0 else ""}{F(tot_diff)}</td>'
              f'<td><span class="{"up" if ac6>=bu6 else "dn"}">{ac6/bu6*100:.0f}٪</span></td>'
              f'<td>{F(s25) if s25 else "—"}</td><td>{c_g_tot}</td></tr>')

    mini = re.search(r'<div class="mini-head">.*?</div>\s*(?=<div class="skpis")',
                     PG[c + "-monthly"], re.S).group(0)
    nav = re.search(r'<div class="pgnav">.*?</select>\s*</div>', PG[c], re.S).group(0)
    title = re.search(r'data-title="([^"]*)"', PG[c]).group(1).split(" · ")[0]
    ez += 1

    PG[c + "-targets"] = (
        f'<div class="pgview" data-ez="z{ez}" id="pg-{c}-targets" '
        f'data-title="{title} · المستهدفات" hidden>'
        + nav + tabs_of(c, "/targets") + mini + kpis
        + '<div class="chartbox"><h3>الموازنة مقابل الفعلي — 12 شهرًا</h3>'
          '<div class="cs">العمود الرمادي: المستهدف · العمود البرتقالي: المتحقق · '
          'النسبة فوق كل شهر هي الإنجاز — أخضر إذا بلغ الهدف وأحمر إن لم يبلغه</div>'
        + chart(bu, ac) + "</div>"
        + '<div class="sec-h"><h2>جدول المستهدفات الشهرية</h2>'
          '<span>الوحدة لترات · المصدر: ملف Sales Analysis 2026 (صف BU.2026 للموازنة و Act.2026 للفعلي)</span></div>'
        + '<div class="ntable"><div class="tscroll"><table><thead><tr>'
          '<th>الشهر</th><th>الموازنة / المستهدف (لتر)</th><th>الفعلي (لتر)</th>'
          '<th>الفرق</th><th>الإنجاز</th><th>فعلي 2025 (لتر)</th><th>النمو</th>'
          f'</tr></thead><tbody>{trows}</tbody></table></div></div>'
        + '<div class="dnote">📐 <b>الوحدة لترات لا ريالات</b> — صف <code>Act.2026</code> في ملف الموازنة '
          'يطابق أرقام اللترات في لوحة المبيعات تطابقًا تامًا، فالمؤشر يقيس <b>حجم البيع</b> لا الإيراد، '
          'وهو الأنسب لأن سعر الوقود مسعّر حكوميًا. <b>«المستهدف» و«الموازنة» شيء واحد هنا</b> — '
          'الملف فيه صف هدف واحد هو <code>BU.2026</code>. '
          'الموازنة موزّعة موسميًا لا بعدد أيام الشهر (موازنة فبراير قد تفوق يناير رغم قِصره). '
          'عمود «فعلي 2025» مرتبط بملف خارجي في المصدر وقد يكون فارغًا لبعض المحطات.</div>'
        + '<div class="pgnav" style="margin-top:4px"><div class="nvl">'
          f'<a class="hb" href="#/">⌂ جميع المحطات</a>'
          f'<a href="#/{c}/monthly">← المبيعات الشهرية</a></div></div></div>')

# ═══════════ 6. التبويب في الصفحات القائمة ═══════════
for c in KEEP:
    for suf, key in (("", c), ("/monthly", c + "-monthly"), ("/daily", c + "-daily"),
                     ("/cs", c + "-cs"), ("/partners", c + "-partners")):
        p, k = re.subn(r'<div class="tabs">.*?</div>', tabs_of(c, suf), PG[key], count=1, flags=re.S)
        assert k == 1, key
        PG[key] = p

new_order = []
for k in ORDER:
    new_order.append(k)
    if k.endswith("-daily") and k[:-6] in KEEP:
        new_order.append(k[:-6] + "-targets")
pages_all = lead + "".join(PG[k] for k in new_order)

doc = pages_head + '<main class="wrap" id="pages">' + pages_all
doc = re.sub(r'data-docid="[^"]*"', 'data-docid="darb-5st-targets-v1"', doc, count=1)
open(OUT, "w", encoding="utf-8").write(doc)
print("تم · الحجم:", round(len(doc.encode()) / 1024), "KB · إعادة تسمية:", n1, n2)
for c in KEEP:
    b6 = sum(BU[c]["BU.2026"][j] for j in range(12) if BU[c]["Act.2026"][j])
    a6 = sum(x for x in BU[c]["Act.2026"] if x)
    print(f'  {c}: موازنة السنة {AB(sum(BU[c]["BU.2026"]))} لتر · إنجاز المسجل {a6/b6*100:.0f}٪')
