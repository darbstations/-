# -*- coding: utf-8 -*-
"""يرفق سبب كل شهر لكل محطة من تقرير التحليل التفصيلي (يناير → يونيو 2026).

مصدر البيانات: darb-monthly-reasons-2026.xlsx — ورقة لكل محطة بأعمدة
الشهر · الحالة · التحليل الموسمي · تأثير الشكاوى.

أين يظهر السبب:
  • تحت عنوان «السبب المؤكد والإجراء» داخل بطاقة كل شهر — لأنه سبب موثّق
    في تقرير رسمي لا فرضية، ويبقى تحته سطر حرّ للإجراء المتخذ.
  • «الأسباب المرشّحة للتحقق» تُعاد صياغتها لكل شهر على حدة: تُستخرج من نص
    تحليل ذلك الشهر رقاقات مطابقة وتُعلَّم ✓، ويُستكمل الباقي بالمرشّحات
    العامة غير المعلَّمة.
  • جدول مجمَّع «سبب كل شهر» في تبويب «المستهدفات» بجانب نسبة الإنجاز.

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

SHEET2CODE = {"MK007": "MK007", "MK017": "MK017", "MK002": "MK002",
              "MK019": "MK019", "MK072": "MK023"}
ASSUMED = {"MK023"}          # مطابقة بالاستبعاد لا بالكود

CHIP = {"ارتفاع": "c-nbh", "جيد": "c-hwy", "انخفاض نسبي": "c-rem", "انخفاض": "c-viv"}
ICON = {"ارتفاع": "📈", "جيد": "➖", "انخفاض نسبي": "📉", "انخفاض": "📉"}

#  ما يُستخرج من نص الشهر → رقاقة تُعلَّم ✓ (الترتيب مقصود: الأخصّ أولًا)
RULES = [
    (r"انتهاء الإجاز", "انتهاء الإجازات وعودة الدوام"),
    (r"إجازة منتصف العام", "إجازة منتصف العام"),
    (r"إجازة|الإجازات", "إجازة مدارس"),
    (r"انتهاء رمضان|انتهاء العيد|بعد رمضان|بعد العيد", "انتهاء رمضان والعيد"),
    (r"رمضان", "رمضان"),
    (r"العيد", "إجازة العيد"),
    (r"قبل ذروة الحج", "قبل ذروة الحج"),
    (r"ذروة الحج", "ذروة موسم الحج"),
    (r"قبل الحج|انتقالية", "فترة انتقالية قبل الحج"),
    (r"الحج|المشاعر", "موسم الحج"),
    (r"عمرة|معتمر", "موسم العمرة"),
    (r"طريق المدينة|الطريق الرئيسي|طريق", "الموقع على طريق رئيسي — حركة عابرة"),
    (r"الحركة المحلية", "الاعتماد على الحركة المحلية"),
    (r"حركة مرورية مرتفعة|زيادة الحركة|زيادة الإقبال|زيادة أعداد", "ارتفاع الحركة المرورية"),
    (r"انخفاض الحركة|تراجع الحركة", "انخفاض الحركة المرورية"),
    (r"زيادة عدد المركبات", "زيادة عدد المركبات"),
    (r"انخفاض المركبات", "انخفاض عدد المركبات"),
    (r"متوسط الفاتورة", "تغيّر متوسط الفاتورة"),
    (r"بطء الخدمة|طول الانتظار|بطء خدمة", "بطء الخدمة وطول الانتظار"),
    (r"تعامل", "تعامل العاملين"),
    (r"أخطاء تشغيلية|مشكلات التشغيل|المشكلات التشغيلية", "أخطاء تشغيلية"),
    (r"طلب(?:ات)? غير مكتمل", "طلبات غير مكتملة"),
    (r"فقدان مقتنيات", "فقدان مقتنيات"),
    (r"عدم توفر العامل", "عدم توفر العامل"),
    (r"ضعف التنظيم", "ضعف التنظيم داخل المحطة"),
    (r"جودة الخدمة", "جودة الخدمة"),
    (r"كثرة الشكاوى|شكاوى", "شكاوى العملاء"),
    (r"رضا العملاء|ثقة العملاء", "انخفاض رضا العملاء"),
    (r"لا يوجد موسم|عدم وجود موسم", "غياب موسم مؤثر"),
]
#  مرشّحات عامة تبقى بلا تعليم ليختار منها المستخدم
GENERIC = ["إغلاق أو تحويلة طريق", "صيانة مضخات أو توقف جزئي", "انقطاع منتج",
           "منافس جديد قريب", "تغيّر أسعار", "حملة تسويقية", "تغيّر فريق التشغيل",
           "طقس أو أمطار", "أعمال إنشائية مجاورة"]

PLACE_OLD = "اكتب هنا ما تعرفه عن سبب حركة هذا الشهر، والإجراء المتخذ…"
PLACE_NEW = "اكتب الإجراء المتخذ، أو أضف سببًا مؤكدًا آخر من عندك…"

E = lambda t: html.escape(str(t), quote=True)

# ═══════════ 1. قراءة الأسباب ═══════════
wb = openpyxl.load_workbook(XLSX, data_only=True)
R, SRCSHEET = {}, {}
for ws in wb.worksheets:
    code = SHEET2CODE.get(ws.title.split()[0].strip())
    assert code, f"ورقة بكود غير معروف: {ws.title}"
    SRCSHEET[code] = ws.title
    R[code] = {}
    for r in list(ws.iter_rows(values_only=True))[1:]:
        if not r or not r[0]:
            continue
        R[code][str(r[0]).strip()] = {"state": str(r[1] or "").strip(),
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
              + " — تُركت بلا سبب مؤكد ولم تُملأ بتقدير.")
    return n


CS_FLAG = "ملاحظات تشغيلية أثّرت على رضا العملاء"


def matched_chips(d):
    """الرقاقات المستخرَجة من نص هذا الشهر — بالترتيب وبلا تكرار.

    الاستخراج من عمود «التحليل الموسمي» وحده لأنه النص الخاص بالشهر؛ أما عمود
    «تأثير الشكاوى» فنصّه قالب متكرر يحمل معلومة واحدة (مؤثرة أو لا)، فيُترجَم
    إلى رقاقة واحدة ولا تُشتقّ منه رقاقات تفصيلية تتكرر في كل شهر.
    """
    if not d:
        return []
    txt = d["season"]
    out = []
    for pat, lbl in RULES:
        if re.search(pat, txt) and lbl not in out:
            out.append(lbl)
    if "لا توجد شكاوى" in txt and "شكاوى العملاء" in out:
        out.remove("شكاوى العملاء")
    #  الأخصّ يلغي الأعمّ
    for spec, gen in (("انتهاء الإجازات وعودة الدوام", "إجازة مدارس"),
                      ("إجازة منتصف العام", "إجازة مدارس"),
                      ("ذروة موسم الحج", "موسم الحج"),
                      ("فترة انتقالية قبل الحج", "موسم الحج"),
                      ("قبل ذروة الحج", "ذروة موسم الحج"),
                      ("قبل ذروة الحج", "موسم الحج"),
                      ("انتهاء رمضان والعيد", "رمضان"),
                      ("انتهاء رمضان والعيد", "إجازة العيد")):
        if spec in out and gen in out:
            out.remove(gen)
    if "وجود ملاحظات تشغيلية" in d["cs"]:
        out.append(CS_FLAG)
    return out


# ═══════════ 2. الكتلتان داخل بطاقة الشهر ═══════════
def act_block(code, mo):
    d = R[code].get(mo)
    if not d:
        body = ('<div class="cfrm none">لم يرد سبب لهذا الشهر في تقرير التحليل التفصيلي — '
                "اكتب السبب المؤكد بنفسك في السطر أدناه.</div>")
    else:
        cls = CHIP.get(d["state"], "c-un")
        body = (
            '<div class="cfrm">'
            f'<div class="cfh"><span class="cls {cls}">{ICON.get(d["state"], "•")} '
            f'{E(d["state"])}</span>'
            f'<span class="cfsrc">مؤكَّد من تقرير التحليل التفصيلي — '
            f'ورقة «{E(SRCSHEET[code])}»</span></div>'
            f'<div class="cfl"><b>موسميًا وتشغيليًا:</b> {E(d["season"])}</div>'
            f'<div class="cfl"><b>أثر الشكاوى:</b> {E(d["cs"])}</div>'
            "</div>")
    return ('<div class="mline act"><b>✅ السبب المؤكد والإجراء</b>' + body
            + f'<p class="mfree">{PLACE_NEW}</p></div>')


def hyp_block(code, mo):
    d = R[code].get(mo)
    on = matched_chips(d)
    chips = "".join(f'<span class="hchip on" title="مستخرج من نص تحليل هذا الشهر">{E(c)}</span>'
                    for c in on)
    chips += "".join(f'<span class="hchip">{E(c)}</span>'
                     for c in GENERIC if c not in on)
    lead = (f"<b>{len(on)}</b> رقاقة معلَّمة ✓ مستخرَجة من نص تحليل هذا الشهر — "
            "ألغِ تعليم ما لا ينطبق. " if on else
            "لا يوجد نص تحليل لهذا الشهر، فلم تُعلَّم أي رقاقة. ")
    return ('<div class="mline hyp"><b>أسباب مرشّحة للتحقق</b>'
            f'<div class="mnote">{lead}الباقي مرشّحات <b>لم تُقَس</b> — '
            "اضغط ما ينطبق ليُعلَّم، وأضف غيره من وضع التحرير.</div>"
            f'<div class="hchips">{chips}</div></div>')


stats = {c: [0, 0] for c in KEEP}
for code in KEEP:
    m = re.search(r'id="pg-%s-monthly".*?(?=<div class="pgview"|</main>)' % code, doc, re.S)
    page = m.group(0)
    cards = re.split(r'(?=<details class="mdet")', page)
    for i, card in enumerate(cards):
        cm = re.match(r'<details class="mdet"[^>]*><summary>[^<]*<b>([^<]+)</b>', card)
        if not cm:
            continue
        mo = cm.group(1).strip()
        c2, k1 = re.subn(r'<div class="mline hyp">.*?</div></div>',
                         lambda g: hyp_block(code, mo), card, count=1, flags=re.S)
        c2, k2 = re.subn(r'<div class="mline act">.*?</div>(?=</div></details>)',
                         lambda g: act_block(code, mo), c2, count=1, flags=re.S)
        assert k1 == 1 and k2 == 1, (code, mo, k1, k2)
        cards[i] = c2
        stats[code][0] += 1
        stats[code][1] += len(matched_chips(R[code].get(mo)))
    new = "".join(cards)
    j = new.rindex("</details></div>") + len("</details></div>")
    new = new[:j] + f'<div class="dnote">📐 {note_for(code)}</div>' + new[j:]
    doc = doc.replace(page, new, 1)

#  نص الإرشاد في السطر الحرّ (في المحتوى وفي السكربت الذي يعيده عند الخروج)
doc = doc.replace(PLACE_OLD, PLACE_NEW)

# ═══════════ 3. جدول مجمَّع في تبويب المستهدفات ═══════════
for code in KEEP:
    rows = ""
    for mo in MONTHS:
        d = R[code].get(mo)
        if d:
            cls = CHIP.get(d["state"], "c-un")
            tags = "".join(f'<span class="cls c-un tagm">{E(c)}</span>'
                           for c in matched_chips(d))
            rows += (f"<tr><td><b>{mo}</b></td>"
                     f'<td><span class="cls {cls}">{ICON.get(d["state"], "•")} {E(d["state"])}</span></td>'
                     f'<td>{E(d["season"])}</td><td>{E(d["cs"])}</td>'
                     f'<td>{tags or "—"}</td></tr>')
        else:
            rows += (f"<tr><td><b>{mo}</b></td><td>—</td>"
                     f'<td colspan="3">لم يرد هذا الشهر في تقرير الأسباب</td></tr>')
    tbl = ('<div class="sec-h" style="margin-top:22px"><h2>📋 سبب كل شهر</h2>'
           "<span>من تقرير التحليل التفصيلي — يُقرأ بجانب نسبة الإنجاز في الجدول أعلاه</span></div>"
           '<div class="ntable whytbl"><div class="tscroll"><table>'
           "<thead><tr><th>الشهر</th><th>الحالة</th><th>التحليل الموسمي</th>"
           "<th>تأثير الشكاوى</th><th>الأسباب المعلَّمة في بطاقة الشهر</th></tr></thead>"
           f"<tbody>{rows}</tbody></table></div></div>"
           f'<div class="dnote">📐 {note_for(code)}</div>')
    m = re.search(r'id="pg-%s-targets".*?(?=<div class="pgview"|</main>)' % code, doc, re.S)
    page = m.group(0)
    new, k = re.subn(r'(<div class="pgnav" style="margin-top:4px">)', tbl + r"\1", page, count=1)
    assert k == 1, code
    doc = doc.replace(page, new, 1)

CSS = """
<style id="why-css">
/* ── السبب المؤكد من التقرير التفصيلي ── */
.cfrm{background:#fff;border:1px solid #EAD9C3;border-radius:10px;padding:9px 11px;margin:6px 0 8px}
.cfrm.none{color:var(--ink3);font-size:12px}
.cfh{display:flex;align-items:center;gap:9px;flex-wrap:wrap;margin-bottom:5px}
.cfsrc{font-size:10.5px;color:var(--ink3)}
.cfl{font-size:12.5px;line-height:1.9;color:var(--ink2)}
.cfl b{color:var(--ink)}
.whytbl td{white-space:normal;line-height:1.8;vertical-align:top}
.whytbl td:first-child{min-width:80px}
.whytbl td:nth-child(2){min-width:110px}
.whytbl td:last-child{min-width:190px}
.tagm{display:inline-block;margin:0 0 4px 4px}
</style>
"""
doc = doc.replace("</head>", CSS + "</head>", 1)
doc = re.sub(r'data-docid="[^"]*"', 'data-docid="darb-5st-why-v2"', doc, count=1)
open(OUT, "w", encoding="utf-8").write(doc)

print("تم · الحجم:", round(len(doc.encode()) / 1024), "KB")
for c in KEEP:
    have = [m for m in MONTHS if m in R[c]]
    print(f"  {c} ← «{SRCSHEET[c]}»: {stats[c][0]}/6 بطاقة · أشهر واردة {len(have)}"
          f" · رقاقات معلَّمة {stats[c][1]}"
          + ("  ⚠ ربط بالاستبعاد" if c in ASSUMED else ""))
    for mo in MONTHS:
        d = R[c].get(mo)
        print(f"      {mo}: " + ("، ".join(matched_chips(d)) if d else "—"))
