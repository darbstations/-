# -*- coding: utf-8 -*-
"""يضيف القيمة باللترات بجانب كل قيمة إيراد بالريال، دون تغيير أي محتوى قائم."""
import re, json

SRC = "/tmp/claude-0/-home-user--/447348d0-0f0b-5d32-9f6b-27c9ad645473/scratchpad/base.html"
OUT = "/home/user/-/darb-five-stations-analysis.html"
KEEP = ["MK007", "MK017", "MK002", "MK023", "MK019"]

s = open(SRC, encoding="utf-8").read()

# ═══════════════ أدوات تنسيق ═══════════════
def N(x):            # "1,912,969" → 1912969
    return int(str(x).replace(",", ""))
def F(n):            # 1912969 → "1,912,969"
    return f"{round(n):,}"
def AB(n):           # صيغة مختصرة مطابقة لأسلوب الملف: 4.3 مليون / 722 ألف
    n = round(n)
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f} مليون"
    if n >= 1000:
        return f"{round(n/1000):,} ألف"
    return f"{n:,}"
def ABC(n):          # صيغة مختصرة داخل الرسوم: 1.3م / 574ألف
    n = round(n)
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}م"
    if n >= 1000:
        return f"{round(n/1000)}ألف"
    return str(n)

# ═══════════════ تقسيم المستند ═══════════════
head_hub, pages_all = s.split('<main class="wrap" id="pages">', 1)
blocks = re.split(r'(?=<div class="pgview")', pages_all)
lead, blocks = blocks[0], blocks[1:]
PG, ORDER = {}, []
for b in blocks:
    k = re.search(r'id="pg-([\w-]+)"', b).group(1)
    PG[k] = b
    ORDER.append(k)

# ═══════════════ استخراج بيانات اللترات لكل محطة ═══════════════
ST = {}
for c in KEEP:
    full, mon, day = PG[c], PG[c + "-monthly"], PG[c + "-daily"]
    vis, plit = re.search(r'<div class="kn">([\d,]+) زيارة · ([\d,]+) لتر</div>', full).groups()
    mrows = re.findall(
        r'<tr><td><b>([^<]+)</b></td><td>(\d+)</td><td>([\d,]+)</td>\s*'
        r'<td>([\d,]+)</td><td>([\d,]+)</td><td>([\d,]+)</td>\s*<td>([\d,]+)</td>',
        re.search(r'<th>الشهر</th>.*?<tbody>(.*?)</tbody>', mon, re.S).group(1))
    drows = re.findall(
        r'<tr><td>(\d{4}-\d\d-\d\d)</td><td>[^<]*</td><td>([\d,]+)</td><td>([\d,]+)</td>',
        re.search(r'<th>التاريخ</th>.*?<tbody>(.*?)</tbody>', day, re.S).group(1))
    ST[c] = {
        "plit":   N(plit),                                              # لترات الفترة
        "prev":   sum(N(r[2]) for r in mrows),                          # إيراد الفترة
        "dlit":   N(re.search(r'متوسط اللترات اليومية\*</div><div class="kv">([\d,]+)', day).group(1)),
        "ndays":  sum(int(r[1]) for r in mrows),
        "months": {r[0]: {"days": int(r[1]), "rev": N(r[2]), "lit": N(r[4])} for r in mrows},
        "days":   {r[0]: {"rev": N(r[1]), "lit": N(r[2])} for r in drows},
    }
    ST[c]["mlit"] = ST[c]["plit"] / len(mrows)                          # متوسط لترات الشهر
    ST[c]["ratio"] = ST[c]["plit"] / ST[c]["prev"]                      # لتر لكل ريال

# ═══════════════ 1. صفحات المحطات ═══════════════
def kn_append(txt, kl, extra):
    """يلحق نصًا بسطر .kn الخاص ببطاقة مؤشر معيّنة."""
    pat = r'(<div class="kl">' + re.escape(kl) + r'</div><div class="kv">.*?</div><div class="kn">)(.*?)(</div>)'
    out, n = re.subn(pat, lambda m: m.group(1) + m.group(2) + extra + m.group(3), txt, count=1, flags=re.S)
    assert n == 1, kl
    return out

def add_bar_liters(chart, values_by_month):
    """يضيف سطر لترات تحت اسم كل شهر في رسم أعمدة."""
    labels = re.findall(r'<text x="([\d.]+)" y="178\.0" font-size="11" text-anchor="middle" '
                        r'fill="var\(--ink2\)">([^<]+)</text>', chart)
    assert labels, "لم يُعثر على تسميات الأشهر"
    extra = "".join(
        f'<text x="{x}" y="196.0" font-size="9.5" text-anchor="middle" fill="var(--ink3)">'
        f'{ABC(values_by_month[mth])} لتر</text>'
        for x, mth in labels if mth in values_by_month)
    chart = chart.replace('viewBox="0 0 640 190"', 'viewBox="0 0 640 206"', 1)
    return chart.replace("</svg>", extra + "</svg>", 1)

for c in KEEP:
    st = ST[c]

    # ── صفحة التحليل الكامل ──
    p = PG[c]
    p = kn_append(p, "الإيراد اليومي", f' · {F(st["dlit"])} لتر/يوم')
    #  ذكر الإيراد اليومي داخل نقاط SWOT
    p = re.sub(r'(بإيراد يومي [\d.,]+ (?:ألف|مليون) ر\.س)',
               lambda m: m.group(1) + f' (≈ {AB(st["dlit"])} لتر/يوم)', p)
    PG[c] = p

    # ── صفحة المبيعات الشهرية ──
    p = PG[c + "-monthly"]
    p = kn_append(p, "إجمالي إيراد الفترة", f' · {F(st["plit"])} لتر')
    bm = re.search(r'<div class="kl">أفضل شهر</div><div class="kv">([^<]+)</div>', p).group(1).strip()
    p = kn_append(p, "أفضل شهر", f' · {F(st["months"][bm]["lit"])} لتر')
    p = kn_append(p, "متوسط الإيراد الشهري", f' · {F(st["mlit"])} لتر/شهر')

    #  رسما الأعمدة
    charts = re.findall(r'<div class="chartbox"><h3>(?:الإيراد الشهري \(ر\.س\)|'
                        r'متوسط الإيراد اليومي لكل شهر \(ر\.س\))</h3>.*?</svg>', p, re.S)
    assert len(charts) == 2, c
    p = p.replace(charts[0], add_bar_liters(charts[0],
                  {m: v["lit"] for m, v in st["months"].items()}), 1)
    p = p.replace(charts[1], add_bar_liters(charts[1],
                  {m: v["lit"] / v["days"] for m, v in st["months"].items()}), 1)

    #  عمود «متوسط اللترات/اليوم» بجانب «متوسط اليوم (ر.س)»
    p = p.replace('<th>متوسط اليوم (ر.س)</th>',
                  '<th>متوسط اليوم (ر.س)</th><th>متوسط اللترات/اليوم</th>', 1)
    def mrow(m):
        mth = m.group(1)
        v = st["months"][mth]
        return m.group(0)[:-len("</td>")] + "</td>" + f'<td>{F(v["lit"]/v["days"])}</td>'
    p = re.sub(r'<tr><td><b>([^<]+)</b></td><td>\d+</td><td>[\d,]+</td>\s*'
               r'<td>[\d,]+</td><td>[\d,]+</td><td>[\d,]+</td>\s*<td>[\d,]+</td>', mrow, p)
    PG[c + "-monthly"] = p

    # ── صفحة المبيعات اليومية ──
    p = PG[c + "-daily"]
    p = kn_append(p, "متوسط الإيراد اليومي", f' · {F(st["dlit"])} لتر/يوم')
    for kl in ("أفضل يوم", "أدنى يوم"):
        dt = re.search(r'<div class="kl">' + kl + r'</div><div class="kv">[\d,]+ <small>ر\.س</small>'
                       r'</div><div class="kn">(\d{4}-\d\d-\d\d)', p).group(1)
        p = kn_append(p, kl, f' · {F(st["days"][dt]["lit"])} لتر')

    #  محور لتري مقابل على رسم الإيراد اليومي
    ch = re.search(r'<div class="chartbox"><h3>الإيراد اليومي عبر الفترة</h3>.*?</svg>', p, re.S).group(0)
    grid = re.findall(r'<text x="40" y="([\d.]+)" font-size="10" text-anchor="end" '
                      r'fill="var\(--ink3\)">([\d.]+)(ألف|م|)</text>', ch)
    mult = {"": 1, "ألف": 1000, "م": 1_000_000}
    extra = "".join(
        f'<text x="918" y="{y}" font-size="10" text-anchor="start" fill="var(--ink3)">'
        f'{ABC(float(v) * mult[u] * st["ratio"])} لتر</text>' for y, v, u in grid)
    new = ch.replace('viewBox="0 0 920 240"', 'viewBox="0 0 1010 240"', 1)
    new = new.replace("</svg>", extra + "</svg>", 1)
    new = new.replace('<div class="cs">الخط الرمادي: القيم اليومية · الخط البرتقالي: متوسط متحرك 7 أيام</div>',
                      '<div class="cs">الخط الرمادي: القيم اليومية · الخط البرتقالي: متوسط متحرك 7 أيام'
                      f' · المحور الأيسر بالريال والأيمن بما يعادله لترات (بنسبة الفترة: '
                      f'{F(st["ratio"]*1000)} لتر لكل 1,000 ر.س)</div>', 1)
    p = p.replace(ch, new, 1)
    PG[c + "-daily"] = p

pages_all = lead + "".join(PG[k] for k in ORDER)

# ═══════════════ 2. بطاقات الصفحة الرئيسية ═══════════════
for c in KEEP:
    pat = r'(<a class="scard" href="#/' + c + r'".*?<span>إيراد يومي <b>[\d,]+</b> ر\.س)(</span>)'
    head_hub, n = re.subn(pat, lambda m: m.group(1) + f' · <b>{F(ST[c]["dlit"])}</b> لتر' + m.group(2),
                          head_hub, count=1, flags=re.S)
    assert n == 1, c

# ═══════════════ 3. جدول الترتيب ═══════════════
head_hub = head_hub.replace('<th>إيراد يومي (ر.س)</th>',
                            '<th>إيراد يومي (ر.س)</th><th>لترات/يوم</th>', 1)
def orow(m):
    return m.group(0) + f'<td>{F(ST[m.group(1)]["dlit"])}</td>'
head_hub, n = re.subn(
    r'<a class="stlink" href="#/(\w+)">[^<]*</a> <span class="tcode">\w+</span></td><td>[^<]*</td>\s*'
    r'<td>[^<]*</td><td>[\d,]+</td>', orow, head_hub)
assert n == len(KEEP), n

# ═══════════════ 4. مؤشرات الترويسة ═══════════════
tot_lit = sum(ST[c]["plit"] for c in KEEP)
head_hub = head_hub.replace('<div class="l">إيراد الفترة للمحطات الخمس</div>',
    f'<div class="l">إيراد الفترة للمحطات الخمس · {tot_lit/1e6:.1f} مليون لتر</div>', 1)

# ═══════════════ 5. صفحة المقارنة (بيانات + عرض) ═══════════════
doc = head_hub + '<main class="wrap" id="pages">' + pages_all

m = re.search(r'(<script id="cmpdata" type="application/json">)(.*?)(</script>)', doc, re.S)
DATA = json.loads(m.group(2))
for c in KEEP:
    DATA["stations"][c]["tlit"] = ST[c]["plit"]
    DATA["stations"][c]["dlit"] = ST[c]["dlit"]
doc = doc.replace(m.group(0), m.group(1) + json.dumps(DATA, ensure_ascii=False) + m.group(3), 1)

doc = doc.replace(
    "return {n:ss.length,rev:SM(s=>s.revenue),drev:SM(s=>s.drev),dvis:SM(s=>s.dvis),",
    "return {n:ss.length,rev:SM(s=>s.revenue),drev:SM(s=>s.drev),dvis:SM(s=>s.dvis),"
    "tlit:SM(s=>s.tlit),dlit:SM(s=>s.dlit),", 1)

old_rows = """    vsRow('إيراد الفترة المسجل (ر.س)',A.rev,B.rev,F0(A.rev),F0(B.rev),null)+
    vsRow('الإيراد اليومي الإجمالي (ر.س)',A.drev,B.drev,F0(A.drev),F0(B.drev),true)+
    vsRow('متوسط إيراد المحطة/يوم',A.drev/A.n,B.drev/B.n,F0(A.drev/A.n),F0(B.drev/B.n),true)+"""
new_rows = """    vsRow('إيراد الفترة المسجل (ر.س)',A.rev,B.rev,F0(A.rev),F0(B.rev),null)+
    vsRow('لترات الفترة المسجلة',A.tlit,B.tlit,F0(A.tlit)+' لتر',F0(B.tlit)+' لتر',null)+
    vsRow('الإيراد اليومي الإجمالي (ر.س)',A.drev,B.drev,F0(A.drev),F0(B.drev),true)+
    vsRow('اللترات اليومية الإجمالية',A.dlit,B.dlit,F0(A.dlit)+' لتر',F0(B.dlit)+' لتر',true)+
    vsRow('متوسط إيراد المحطة/يوم',A.drev/A.n,B.drev/B.n,F0(A.drev/A.n),F0(B.drev/B.n),true)+
    vsRow('متوسط لترات المحطة/يوم',A.dlit/A.n,B.dlit/B.n,F0(A.dlit/A.n)+' لتر',F0(B.dlit/B.n)+' لتر',true)+"""
assert old_rows in doc
doc = doc.replace(old_rows, new_rows, 1)

# ═══════════════ 6. توحيد معرّفات التدرجات داخل الرسوم ═══════════════
# كل رسم يعرّف <linearGradient id="gB"> بنفس المعرّف؛ المتصفح يربط url(#gB)
# بأول تعريف في المستند — وهو داخل صفحة مخفية — فيختفي العمود المميّز.
_seq = [0]
def uniq_svg_ids(mm):
    svg = mm.group(0)
    defs = re.search(r"<defs>.*?</defs>", svg, re.S)
    if not defs:
        return svg
    _seq[0] += 1
    for gid in set(re.findall(r'id="([A-Za-z_][\w-]*)"', defs.group(0))):
        new_id = f"{gid}-{_seq[0]}"
        svg = svg.replace(f'id="{gid}"', f'id="{new_id}"')
        svg = svg.replace(f"url(#{gid})", f"url(#{new_id})")
    return svg

doc, n_svg = re.subn(r"<svg\b.*?</svg>", uniq_svg_ids, doc, flags=re.S)
print("رسوم مُعالَجة:", _seq[0], "من", n_svg)

# ═══════════════ 7. معرّف مستند جديد (حتى لا تُستعاد نسخة محفوظة قديمة) ═══════════════
doc = re.sub(r'data-docid="[^"]*"', 'data-docid="darb-5st-liters-v1"', doc, count=1)

open(OUT, "w", encoding="utf-8").write(doc)
print("تم · الحجم:", round(len(doc.encode()) / 1024), "KB")
for c in KEEP:
    print(f'  {c}: {F(ST[c]["dlit"])} لتر/يوم · {F(ST[c]["plit"])} لتر للفترة · '
          f'{ST[c]["ratio"]*1000:,.0f} لتر لكل 1,000 ر.س')
