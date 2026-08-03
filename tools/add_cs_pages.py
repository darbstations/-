# -*- coding: utf-8 -*-
"""يضيف لكل محطة من الخمس صفحة «استفسارات العملاء» من تقرير خدمة العملاء الشهري."""
import openpyxl, re, html, collections, datetime

XLSX = "/root/.claude/uploads/447348d0-0f0b-5d32-9f6b-27c9ad645473/a16169b5-Monthly_Report_2026.xlsx"
SRC  = "/home/user/-/darb-five-stations-analysis.html"
OUT  = "/home/user/-/darb-five-stations-analysis.html"
KEEP = ["MK007", "MK017", "MK002", "MK023", "MK019"]
#  «June - Samia» نسخة مكرّرة من تبويب June — تُستبعد حتى لا تُحتسب السجلات مرتين
SHEETS = ["Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug"]
MONTH_AR = {"Jan": "يناير", "Feb": "فبراير", "Mar": "مارس", "Apr": "أبريل",
            "May": "مايو", "June": "يونيو", "July": "يوليو", "Aug": "أغسطس"}

ENTITY = {"complaint": ("شكوى", "c-viv"), "inquiries": ("استفسار", "c-hwy"),
          "requests": ("طلب", "c-mix"), "suggestion": ("اقتراح", "c-nbh")}
STATUS = {"closed": ("مغلقة", "c-nbh"), "in process": ("قيد المعالجة", "c-rem")}
PRIORITY = {"low": "منخفضة", "medium": "متوسطة", "high": "مرتفعة", "urgent": "عاجلة"}
CHANNEL = {"call": "اتصال", "google maps": "خرائط جوجل", "surveyapp": "تطبيق الاستبيان",
           "whatsapp": "واتساب", "website": "الموقع الإلكتروني", "voicemaill": "بريد صوتي",
           "voicemail": "بريد صوتي", "email": "بريد إلكتروني", "x": "منصة X",
           "instagram": "إنستغرام", "twitter": "منصة X"}
DEPT = {"operations": "العمليات", "environment": "البيئة والسلامة", "maintenance": "الصيانة",
        "marketing": "التسويق", "real estate": "العقارات", "customer s": "خدمة العملاء",
        "customer service": "خدمة العملاء", "project m": "إدارة المشاريع",
        "franchise": "الفرنشايز", "hr": "الموارد البشرية", "investment": "الاستثمار",
        "procurement": "المشتريات", "finance": "المالية", "it": "تقنية المعلومات"}

E = lambda t: html.escape(str(t), quote=True)

def clean(v):
    if v is None:
        return ""
    t = str(v).strip()
    return "" if t in ("-", "None", "nan") else t

def ar(mapping, v, default=None):
    return mapping.get(clean(v).lower().strip(), default if default is not None else clean(v))

# ═══════════ قراءة تقرير خدمة العملاء ═══════════
wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)

def load(name):
    ws = wb[name]
    rows = list(ws.iter_rows(values_only=True))
    hdr = [(str(h).strip() if h is not None else "") for h in rows[0]]
    out = []
    for r in rows[1:]:
        if not any(c is not None and str(c).strip() not in ("", "-") for c in r):
            continue
        d = {}
        for i, h in enumerate(hdr):
            if i < len(r) and h and h not in d:      # أول ظهور للعمود هو المعتمد
                d[h] = r[i]
        d["_sheet"] = name
        out.append(d)
    return out

def station_code(d):
    m = re.search(r"\b([A-Z]{2}\d{2,4})\b", clean(d.get("station")).upper().replace(" ", ""))
    return m.group(1) if m else ""

def phone(d):
    p = re.sub(r"\D", "", clean(d.get("CS Number")) or clean(d.get("Numbers")))
    if p.endswith("0") and len(p) == 10 and p.startswith("5"):
        p = p[:-1]                                   # يزيل الصفر الناتج عن ".0"
    if len(p) == 9 and p.startswith("5"):
        p = "0" + p
    if len(p) < 7:
        return ""
    return p[:4] + "•" * (len(p) - 6) + p[-2:]       # إخفاء جزئي لبيانات العميل

def when(d):
    v = d.get("Date")
    if isinstance(v, datetime.datetime):
        return v.date()
    try:
        return datetime.date.fromisoformat(str(v)[:10])
    except Exception:
        return None

RECS = {c: [] for c in KEEP}
for sh in SHEETS:
    for d in load(sh):
        c = station_code(d)
        if c in RECS:
            RECS[c].append(d)
for c in KEEP:
    RECS[c].sort(key=lambda d: (when(d) or datetime.date(2000, 1, 1)), reverse=True)

# ═══════════ عناصر العرض ═══════════
def pill(txt, cls):
    return f'<span class="cls {cls}">{E(txt)}</span>' if txt else '<span class="cls c-un">—</span>'

def breakdown(title, leg, counter, total, limit=8):
    items = counter.most_common(limit)
    mx = max((n for _, n in items), default=1)
    rows = "".join(
        f'<div class="row"><div><div class="lb">{E(k)}</div>'
        f'<div class="bar"><i style="width:{n/mx*100:.1f}%"></i></div></div>'
        f'<div class="n">{n}<small> · {n/total*100:.0f}٪</small></div></div>'
        for k, n in items) or '<div class="row"><div class="lb">لا توجد بيانات</div><div class="n">—</div></div>'
    rest = sum(counter.values()) - sum(n for _, n in items)
    if rest:
        rows += f'<div class="row"><div class="lb">أخرى ({len(counter)-limit} تصنيفًا)</div><div class="n">{rest}</div></div>'
    return (f'<div class="card"><div class="ct"><h3>{title}</h3><div class="leg">{leg}</div></div>'
            f'<div class="brk">{rows}</div></div>')

def month_chart(by_month):
    vals = [(MONTH_AR[m], by_month.get(m, 0)) for m in SHEETS]
    mx = max((v for _, v in vals), default=0) or 1
    W, step, bw = 640, 640 / len(vals), 640 / len(vals) - 14
    out = []
    for i, (lbl, v) in enumerate(vals):
        h = v / mx * 118
        x = i * step + 7
        cx = x + bw / 2
        y = 150 - h
        fill = "#F5831F" if v == mx and v else "var(--bar)"
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="5" fill="{fill}"></rect>')
        out.append(f'<text x="{cx:.1f}" y="{y-6:.1f}" font-size="11" font-weight="700" '
                   f'text-anchor="middle" fill="var(--ink)">{v}</text>')
        out.append(f'<text x="{cx:.1f}" y="168" font-size="11" text-anchor="middle" '
                   f'fill="var(--ink2)">{lbl}</text>')
    return (f'<svg viewBox="0 0 {W} 180" class="bigchart" role="img" '
            f'aria-label="السجلات حسب الشهر">{"".join(out)}</svg>')

def log_table(recs):
    head = ("<thead><tr><th>التاريخ</th><th>النوع</th><th>التصنيف</th><th>الأولوية</th>"
            "<th>القناة</th><th>الإدارة المسؤولة</th><th>العميل</th><th>الوصف</th>"
            "<th>الإجراء المتخذ</th><th>الحالة</th></tr></thead>")
    body = []
    for d in recs:
        dt = when(d)
        ent, ecls = ENTITY.get(clean(d.get("Reporting Entity")).lower(),
                               (clean(d.get("Reporting Entity")) or "—", "c-st"))
        sts, scls = STATUS.get(clean(d.get("Status")).lower(),
                               (clean(d.get("Status")) or "", "c-un"))
        dept = ar(DEPT, d.get("Department") or d.get("Responsible Dep"))
        who = " · ".join(x for x in (clean(d.get("CS Name")), phone(d)) if x) or "—"
        body.append(
            f'<tr><td>{dt or "—"}</td><td>{pill(ent, ecls)}</td>'
            f'<td>{E(clean(d.get("Subcategory")) or "—")}</td>'
            f'<td>{E(ar(PRIORITY, d.get("Priority")) or "—")}</td>'
            f'<td>{E(ar(CHANNEL, d.get("Contact Method")) or "—")}</td>'
            f'<td>{E(dept or "—")}</td><td>{E(who)}</td>'
            f'<td class="wrapcell">{E(clean(d.get("Description")) or "—")}</td>'
            f'<td class="wrapcell">{E(clean(d.get("Action taken")) or "—")}</td>'
            f'<td>{pill(sts, scls)}</td></tr>')
    return f'<div class="dtbl cslog"><table>{head}<tbody>{"".join(body)}</tbody></table></div>'

# ═══════════ بناء صفحة لكل محطة ═══════════
src = open(SRC, encoding="utf-8").read()
pages_head, pages_all = src.split('<main class="wrap" id="pages">', 1)
blocks = re.split(r'(?=<div class="pgview")', pages_all)
lead, blocks = blocks[0], blocks[1:]
PG, ORDER = {}, []
for b in blocks:
    k = re.search(r'id="pg-([\w-]+)"', b).group(1)
    PG[k], _ = b, ORDER.append(k)

ez = max(int(x) for x in re.findall(r'data-ez="z(\d+)"', src))

def nav_of(code):
    """يعيد شريط التنقل والقائمة من صفحة المحطة الأصلية كما هي."""
    m = re.search(r'<div class="pgnav">.*?</select>\s*</div>', PG[code], re.S)
    return m.group(0)

CS_COUNT = {c: len(RECS[c]) for c in KEEP}

def tabs_of(code, active):
    t = [("", "التحليل الكامل"), ("/monthly", "المبيعات الشهرية"),
         ("/daily", "المبيعات اليومية"), ("/cs", "استفسارات العملاء")]
    return '<div class="tabs">' + "".join(
        f'<a class="tab{" on" if suf == active else ""}" href="#/{code}{suf}">{lbl}'
        + (f' <b class="tcount">{CS_COUNT[code]}</b>' if suf == "/cs" else "")
        + "</a>" for suf, lbl in t) + "</div>"

for c in KEEP:
    recs = RECS[c]
    n = len(recs)
    ent = collections.Counter(clean(d.get("Reporting Entity")).lower() for d in recs)
    sts = collections.Counter(clean(d.get("Status")).lower() for d in recs)
    closed, inproc = sts.get("closed", 0), sts.get("in process", 0)
    by_month = collections.Counter(d["_sheet"] for d in recs)
    subcat = collections.Counter(clean(d.get("Subcategory")) or "غير مصنّف" for d in recs)
    chan = collections.Counter(ar(CHANNEL, d.get("Contact Method")) or "غير محدد" for d in recs)
    dept = collections.Counter(ar(DEPT, d.get("Department") or d.get("Responsible Dep")) or "غير محدد"
                               for d in recs)
    prio = collections.Counter(ar(PRIORITY, d.get("Priority")) or "غير محددة" for d in recs)
    top = subcat.most_common(1)[0] if subcat else ("—", 0)
    peak = max(by_month.items(), key=lambda kv: kv[1]) if by_month else ("Jan", 0)

    #  ترويسة مصغّرة منسوخة من صفحة المحطة (نفس الاسم والحي والتقييم)
    mini = re.search(r'<div class="mini-head">.*?</div>\s*(?=<div class="skpis")',
                     PG[c + "-monthly"], re.S).group(0)

    kpis = (
        '<div class="skpis" style="grid-template-columns:repeat(6,1fr)">'
        f'<div class="kpi hot"><div class="kl">إجمالي السجلات</div><div class="kv">{n}</div>'
        f'<div class="kn">يناير → أغسطس 2026</div></div>'
        f'<div class="kpi"><div class="kl">شكاوى</div><div class="kv">{ent.get("complaint",0)}</div>'
        f'<div class="kn">{ent.get("complaint",0)/n*100:.0f}٪ من السجلات</div></div>'
        f'<div class="kpi"><div class="kl">استفسارات</div><div class="kv">{ent.get("inquiries",0)}</div>'
        f'<div class="kn">طلبات {ent.get("requests",0)} · اقتراحات {ent.get("suggestion",0)}</div></div>'
        f'<div class="kpi"><div class="kl">مغلقة</div><div class="kv">{closed}</div>'
        f'<div class="kn">نسبة الإغلاق {closed/n*100:.0f}٪</div></div>'
        f'<div class="kpi"><div class="kl">قيد المعالجة</div><div class="kv">{inproc}</div>'
        f'<div class="kn">{inproc/n*100:.0f}٪ من السجلات'
        f'{" · بلا حالة مسجّلة " + str(n-closed-inproc) if n-closed-inproc else ""}</div></div>'
        f'<div class="kpi"><div class="kl">أكثر تصنيف تكرارًا</div><div class="kv" style="font-size:16px">{E(top[0])}</div>'
        f'<div class="kn">{top[1]} سجل · ذروة الشهور {MONTH_AR[peak[0]]} ({peak[1]})</div></div>'
        "</div>")

    base_title = re.search(r'data-title="([^"]*)"', PG[c]).group(1).split(" · ")[0]
    page = (
        f'<div class="pgview" data-ez="z{ez+1}" id="pg-{c}-cs" '
        f'data-title="{base_title} · استفسارات العملاء" hidden>'
        + nav_of(c) + tabs_of(c, "/cs") + mini + kpis
        + '<div class="chartbox"><h3>السجلات حسب الشهر</h3>'
          '<div class="cs">العمود البرتقالي هو الشهر الأعلى · المصدر: تقرير خدمة العملاء الشهري 2026</div>'
        + month_chart(by_month) + "</div>"
        + '<div class="agrid">'
        + breakdown("التصنيفات الأكثر تكرارًا", "من حقل Subcategory", subcat, n)
        + breakdown("قنوات وصول العميل", "من حقل Contact Method", chan, n)
        + "</div>"
        + '<div class="agrid" style="margin-top:16px">'
        + breakdown("الإدارة المسؤولة", "الجهة المحوّل إليها البلاغ", dept, n)
        + breakdown("أولوية البلاغ", "من حقل Priority", prio, n, limit=5)
        + "</div>"
        + f'<div class="sec-h" style="margin-top:20px"><h2>سجل الاستفسارات والشكاوى</h2>'
          f'<span>{n} سجل مرتبط بالكود {c} · الأحدث أولًا</span></div>'
        + log_table(recs)
        + '<div class="dnote">🔗 <b>الربط:</b> السجلات مأخوذة من تقرير خدمة العملاء الشهري '
          '(يناير–أغسطس 2026) ومرتبطة بالمحطة عبر عمود <b>station</b> بكود المحطة — السجلات التي '
          'لا تحمل كودًا لا تظهر هنا. أرقام جوال العملاء مخفية جزئيًا. تبويب «June - Samia» '
          'مستبعد لأنه نسخة مكرّرة من تبويب يونيو.</div>'
        + '<div class="pgnav" style="margin-top:4px"><div class="nvl">'
          f'<a class="hb" href="#/">⌂ جميع المحطات</a><a href="#/{c}">← صفحة التحليل الكامل</a>'
          "</div></div></div>")
    ez += 1
    PG[c + "-cs"] = page

# ═══════════ إدراج التبويب الرابع في الصفحات القائمة ═══════════
for c in KEEP:
    for suf, key in (("", c), ("/monthly", c + "-monthly"), ("/daily", c + "-daily")):
        p = PG[key]
        p, k = re.subn(r'<div class="tabs">.*?</div>', tabs_of(c, suf), p, count=1, flags=re.S)
        assert k == 1, key
        PG[key] = p

new_order = []
for k in ORDER:
    new_order.append(k)
    if k.endswith("-daily") and k[:-6] in RECS:
        new_order.append(k[:-6] + "-cs")
pages_all = lead + "".join(PG[k] for k in new_order)

# ═══════════ أنماط الصفحة الجديدة ═══════════
CSS = """
<style id="cs-css">
/* ── صفحة استفسارات العملاء ── */
.brk{display:grid;gap:10px}
.brk .row{display:grid;grid-template-columns:1fr 64px;gap:10px;align-items:center}
.brk .lb{font-size:12.5px;color:var(--ink2)}
.brk .bar{height:7px;background:var(--bar);border-radius:5px;overflow:hidden;margin-top:5px}
.brk .bar i{display:block;height:100%;background:linear-gradient(90deg,var(--gold1),var(--orange))}
.brk .n{font-size:13px;font-weight:800;text-align:end;color:var(--ink)}
.brk .n small{font-size:10.5px;font-weight:500;color:var(--ink3)}
.cslog{max-height:640px}
.cslog td{vertical-align:top}
.cslog td.wrapcell{white-space:normal;min-width:230px;max-width:380px;line-height:1.55}
.tab .tcount{display:inline-block;margin-inline-start:5px;background:var(--line2);color:var(--ink2);
  border-radius:7px;padding:1px 6px;font-size:11px}
.tab.on .tcount{background:rgba(255,255,255,.28);color:#fff}
@media(max-width:900px){.brk .row{grid-template-columns:1fr 56px}}
</style>
"""
doc = pages_head + '<main class="wrap" id="pages">' + pages_all
doc = doc.replace("</head>", CSS + "</head>", 1)
doc = re.sub(r'data-docid="[^"]*"', 'data-docid="darb-5st-cs-v1"', doc, count=1)

open(OUT, "w", encoding="utf-8").write(doc)
print("تم · الحجم:", round(len(doc.encode()) / 1024), "KB")
for c in KEEP:
    print(f"  {c}: {len(RECS[c])} سجل")
print("إجمالي:", sum(len(RECS[c]) for c in KEEP))
