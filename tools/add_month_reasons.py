# -*- coding: utf-8 -*-
"""يرفق سبب كل شهر لكل محطة من تقرير التحليل التفصيلي (يناير → يونيو 2026).

مصدر البيانات: darb-monthly-reasons-2026.xlsx — ورقة لكل محطة بأعمدة
الشهر · الحالة · التحليل الموسمي · تأثير الشكاوى.

يُدرَج السبب في موضعين:
  • داخل بطاقة كل شهر في تبويب «المبيعات الشهرية» — كتلة مستقلة أعلى البطاقة.
  • جدول مجمَّع «سبب كل شهر» في تبويب «المستهدفات» أسفل جدول المستهدفات،
    ليُقرأ السبب بجانب نسبة الإنجاز.

ملاحظة على المطابقة: ورقة الملف الخامسة كودها MK072 باسم «الشرائع حي الخضراء»،
ولا يوجد بهذا الكود محطة في التقرير. الأكواد الأربعة الأخرى تطابقت حرفيًا،
والمحطة الخامسة المتبقية هي MK023 درب بن درويش وحيّها «حي الخضراء» — فرُبِطت
الورقة بها بالاستبعاد، والملاحظة مكتوبة صراحةً في الصفحة.
"""
import openpyxl, re, html, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XLSX = os.path.join(BASE, "darb-monthly-reasons-2026.xlsx")
SRC = OUT = os.path.join(BASE, "darb-five-stations-analysis.html")
KEEP = ["MK007", "MK017", "MK002", "MK023", "MK019"]
MONTHS = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو"]

#  كود الورقة في ملف الأسباب → كود المحطة في التقرير
SHEET2CODE = {"MK007": "MK007", "MK017": "MK017", "MK002": "MK002",
              "MK019": "MK019", "MK072": "MK023"}
ASSUMED = {"MK023"}          # مطابقة بالاستبعاد لا بالكود

CHIP = {"ارتفاع": "c-nbh", "جيد": "c-hwy", "انخفاض نسبي": "c-rem", "انخفاض": "c-viv"}
ICON = {"ارتفاع": "📈", "جيد": "➖", "انخفاض نسبي": "📉", "انخفاض": "📉"}

E = lambda t: html.escape(str(t), quote=True)

# ═══════════ 1. قراءة الأسباب ═══════════
wb = openpyxl.load_workbook(XLSX, data_only=True)
R = {}
SRCSHEET = {}
for ws in wb.worksheets:
    sh = ws.title.split()[0].strip()
    code = SHEET2CODE.get(sh)
    assert code, f"ورقة بكود غير معروف: {ws.title}"
    SRCSHEET[code] = ws.title
    rows = list(ws.iter_rows(values_only=True))[1:]
    R[code] = {}
    for r in rows:
        if not r or not r[0]:
            continue
        mo = str(r[0]).strip()
        R[code][mo] = {"state": str(r[1] or "").strip(),
                       "season": str(r[2] or "").strip(),
                       "cs": str(r[3] or "").strip()}
assert set(R) == set(KEEP), set(R)

doc = open(SRC, encoding="utf-8").read()


def note_for(code):
    n = ("<b>المصدر:</b> تقرير التحليل التفصيلي للمحطات يناير → يونيو 2026 — "
         f"ورقة «{E(SRCSHEET[code])}». النص منقول كما ورد دون تعديل.")
    if code in ASSUMED:
        n += (" <b>تنبيه على المطابقة:</b> كود الورقة في الملف هو <b>MK072</b> ولا توجد "
              "محطة بهذا الكود في التقرير؛ رُبطت بهذه المحطة بالاستبعاد لأن الأكواد "
              "الأربعة الأخرى تطابقت حرفيًا ولأن حيّ المحطة هو «حي الخضراء». "
              "لو كانت MK072 محطة أخرى فأبلغني لأصحّح الربط.")
    miss = [m for m in MONTHS if m not in R[code]]
    if miss:
        n += (" <b>أشهر لم ترد في التقرير:</b> " + "، ".join(miss)
              + " — تُركت فارغة ولم تُملأ بتقدير.")
    return n


# ═══════════ 2. كتلة السبب داخل بطاقة الشهر ═══════════
def why_block(code, mo):
    d = R[code].get(mo)
    if not d:
        return ('<div class="mline why"><b>📋 سبب الشهر — من تقرير التحليل التفصيلي</b>'
                '<div class="mnote">لم يرد هذا الشهر في تقرير الأسباب لهذه المحطة.</div></div>')
    cls = CHIP.get(d["state"], "c-un")
    return (
        '<div class="mline why"><b>📋 سبب الشهر — من تقرير التحليل التفصيلي</b>'
        '<div class="whyg">'
        f'<div class="whyc"><div class="wl">الحالة في التقرير</div>'
        f'<span class="cls {cls}">{ICON.get(d["state"], "•")} {E(d["state"])}</span></div>'
        f'<div class="whyc"><div class="wl">التحليل الموسمي</div><p>{E(d["season"])}</p></div>'
        f'<div class="whyc"><div class="wl">تأثير الشكاوى</div><p>{E(d["cs"])}</p></div>'
        "</div></div>")


added = {c: 0 for c in KEEP}
for code in KEEP:
    m = re.search(r'id="pg-%s-monthly".*?(?=<div class="pgview"|</main>)' % code, doc, re.S)
    page = m.group(0)

    #  الإدراج داخل كل بطاقة على حدة — لا كل الشهور فيها كتلة «سبب الارتفاع»
    cards = re.split(r'(?=<details class="mdet")', page)
    for i, card in enumerate(cards):
        cm = re.match(r'<details class="mdet"[^>]*><summary>[^<]*<b>([^<]+)</b>', card)
        if not cm:
            continue
        mo = cm.group(1).strip()
        c2, k = re.subn(r'(<div class="mnums">.*?</div>)',
                        lambda g: g.group(1) + why_block(code, mo), card, count=1, flags=re.S)
        assert k == 1, (code, mo)
        cards[i] = c2
        added[code] += 1
    new = "".join(cards)

    #  ملاحظة المصدر بعد حاوية البطاقات
    j = new.rindex("</details></div>") + len("</details></div>")
    new = new[:j] + f'<div class="dnote">📐 {note_for(code)}</div>' + new[j:]
    doc = doc.replace(page, new, 1)

# ═══════════ 3. جدول مجمَّع في تبويب المستهدفات ═══════════
for code in KEEP:
    rows = ""
    for mo in MONTHS:
        d = R[code].get(mo)
        if d:
            cls = CHIP.get(d["state"], "c-un")
            rows += (f"<tr><td><b>{mo}</b></td>"
                     f'<td><span class="cls {cls}">{ICON.get(d["state"], "•")} {E(d["state"])}</span></td>'
                     f'<td>{E(d["season"])}</td><td>{E(d["cs"])}</td></tr>')
        else:
            rows += (f"<tr><td><b>{mo}</b></td><td>—</td>"
                     f'<td colspan="2">لم يرد هذا الشهر في تقرير الأسباب</td></tr>')
    tbl = ('<div class="sec-h" style="margin-top:22px"><h2>📋 سبب كل شهر</h2>'
           "<span>من تقرير التحليل التفصيلي — يُقرأ بجانب نسبة الإنجاز في الجدول أعلاه</span></div>"
           '<div class="ntable whytbl"><div class="tscroll"><table>'
           "<thead><tr><th>الشهر</th><th>الحالة</th><th>التحليل الموسمي</th>"
           "<th>تأثير الشكاوى</th></tr></thead>"
           f"<tbody>{rows}</tbody></table></div></div>"
           f'<div class="dnote">📐 {note_for(code)}</div>')

    m = re.search(r'id="pg-%s-targets".*?(?=<div class="pgview"|</main>)' % code, doc, re.S)
    page = m.group(0)
    new, k = re.subn(r'(<div class="pgnav" style="margin-top:4px">)', tbl + r"\1",
                     page, count=1)
    assert k == 1, code
    doc = doc.replace(page, new, 1)

CSS = """
<style id="why-css">
/* ── سبب الشهر من التقرير التفصيلي ── */
.mline.why{background:#F4F8FB;border:1px solid #D5E4EF}
.mline.why>b{display:block;margin-bottom:7px;color:#2D5674}
.whyg{display:grid;grid-template-columns:auto 1fr 1fr;gap:8px 16px;align-items:start}
.whyc .wl{font-size:10.5px;font-weight:700;color:var(--ink3);letter-spacing:.2px;margin-bottom:3px}
.whyc p{font-size:12.5px;line-height:1.85;color:var(--ink2);margin:0}
.whytbl td{white-space:normal;line-height:1.8;vertical-align:top}
.whytbl td:first-child{min-width:80px}
.whytbl td:nth-child(2){min-width:110px}
@media (max-width:900px){.whyg{grid-template-columns:1fr}}
</style>
"""
doc = doc.replace("</head>", CSS + "</head>", 1)
doc = re.sub(r'data-docid="[^"]*"', 'data-docid="darb-5st-why-v1"', doc, count=1)
open(OUT, "w", encoding="utf-8").write(doc)

print("تم · الحجم:", round(len(doc.encode()) / 1024), "KB")
for c in KEEP:
    have = [m for m in MONTHS if m in R[c]]
    print(f"  {c} ← «{SRCSHEET[c]}»: {added[c]}/6 بطاقة · أشهر واردة {len(have)}"
          + ("  ⚠ ربط بالاستبعاد" if c in ASSUMED else ""))
