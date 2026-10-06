# -*- coding: utf-8 -*-
"""تعبئة قالب «حملة توزيع المناديل» ببيانات المحطات الخمس.

القاعدة المطلوبة: توزيع العدد بنسبة عدد العملاء في كل محطة. عدد العملاء
المستخدم هو زيارات يوليو ٢٠٢٦ المسجَّلة في منصّة المحطات الخمس — آخر شهر
مُقاس كاملًا. وحدة «المبيعات» و«المستهدف» في القالب لترات، لأن المستهدفات
في ملف Sales Analysis 2026 موضوعة بالّلتر لا بالريال.

ما يُضاف للملف:
  • ورقة «أساس التوزيع» — مُحدِّدات الحملة وحساب نصيب كل محطة بالصيغ، فتغيير
    «علبة لكل عدد عملاء» أو «مدة الحملة» يعيد توزيع الكميات كلها تلقائيًا
  • «المحطات المستهدفة» — صفوف المحطات الخمس مرتَّبة بالأولوية
  • «خطة التوزيع» — ٤ أسابيع × ٥ محطات
  • «متابعة التنفيذ» — ٢٠ حدث توزيع بالكمية المخططة والفعلي فارغ للتسجيل
  • «نتائج الحملة» — خط الأساس قبل الحملة وكمية المناديل وتكلفتها
  • Dashboard — سطرا التكلفة والوحدة وشرح أساس التوزيع

    python3 tools/fill_tissue_campaign.py <قالب-الإدخال> <ملف-المخرَج>
"""
import sys, copy, datetime
import openpyxl
from openpyxl.styles import Alignment

SRC, OUT = sys.argv[1], sys.argv[2]

# ═══════════ بيانات يوليو ٢٠٢٦ من منصّة المحطات الخمس ═══════════
#  الترتيب بالأولوية: الأقل إنجازًا أولًا — كما ينصّ القالب على الاستهداف
ST = [
    # كود      الاسم                الحي               عملاء   أيام  فعلي(لتر)  موازنة(لتر) إنجاز  ذروة  أولوية
    ("MK002", "درب المعيصم",         "حي المعيصم",       18107, 31,   375727,   1568154,  24, "6م", 1),
    ("MK019", "درب عرفات الشرايع",   "حي الخضراء",       10863, 30,   250930,    875943,  29, "9م", 1),
    ("MK023", "درب بن درويش",        "حي الخضراء",       21575, 31,   428657,    502777,  85, "5م", 2),
    ("MK007", "درب العمرة النورية",  "حي العمرة الجديدة", 136584, 31, 4111763,   4438091,  93, "5م", 2),
    ("MK017", "درب عرفات الشوقية",   "حي الشوقية",       35640, 31,   744369,    769484,  97, "10م", 3),
]
PRIO = {1: "أولوية 1 - مرتفعة", 2: "أولوية 2 - متوسطة", 3: "أولوية 3 - منخفضة"}
AIM = {
    "MK002": "سدّ فجوة 1,192,427 لتر شهريًا — أكبر فجوة في الشبكة وأقل إنجاز",
    "MK019": "سدّ فجوة 625,013 لتر شهريًا — ثاني أقل إنجاز",
    "MK023": "سدّ فجوة 74,120 لتر والعودة إلى تحقيق الموازنة",
    "MK007": "سدّ فجوة 326,328 لتر — أكبر قاعدة عملاء، فأعلى وصول لكل علبة",
    "MK017": "فوق الموازنة — الهدف حفاظ على العملاء ومنع تسرّبهم للمنافس",
}
WEEKS = [datetime.date(2026, 10, 11), datetime.date(2026, 10, 18),
         datetime.date(2026, 10, 25), datetime.date(2026, 11, 1)]
R0 = 13                                   # أول صف بيانات في ورقة أساس التوزيع

wb = openpyxl.load_workbook(SRC)
S_DASH = wb["Dashboard"]
S_TGT = wb["المحطات المستهدفة"]
S_PLAN = wb["خطة التوزيع"]
S_EXEC = wb["متابعة التنفيذ"]
S_RES = wb["نتائج الحملة"]


def style_from(src_cell):
    """نسخ هيئة خلية قائمة — لتبقى الإضافات بهيئة القالب نفسها."""
    return dict(font=copy.copy(src_cell.font), fill=copy.copy(src_cell.fill),
                border=copy.copy(src_cell.border), alignment=copy.copy(src_cell.alignment))


def put(ws, coord, value, st=None, fmt=None, align=None):
    c = ws[coord]
    c.value = value
    if st:
        c.font, c.fill, c.border = st["font"], st["fill"], st["border"]
        c.alignment = copy.copy(st["alignment"])
    if align:
        c.alignment = Alignment(horizontal=align, vertical="center", wrap_text=False)
    if fmt:
        c.number_format = fmt
    return c


HEAD = style_from(S_TGT["A1"])             # ترويسة كحلية بخط أبيض
BODY = style_from(S_TGT["A2"])             # خلية بإطار رقيق
KEYB = style_from(S_DASH["B4"])            # وسم أزرق في اللوحة
KEYV = style_from(S_DASH["C4"])            # قيمة خضراء في اللوحة
NOTEH = style_from(S_DASH["E4"])
NOTEB = style_from(S_DASH["E5"])

# ═══════════ 1. ورقة «أساس التوزيع» ═══════════
ws = wb.create_sheet("أساس التوزيع", 1)
ws.sheet_view.showGridLines = False
for col, w in zip("ABCDEFGHIJKL",
                  [13, 22, 20, 20, 11, 13, 13, 20, 22, 20, 14, 16]):
    ws.column_dimensions[col].width = w

t = put(ws, "B2", "أساس توزيع المناديل — الكمية بنسبة عدد العملاء في كل محطة")
t.font = copy.copy(S_DASH["B2"].font)

DRV = [
    ("B3", "مدة الحملة (أسابيع)", "C3", 4, "#,##0"),
    ("B4", "أيام التوزيع", "C4", "=C3*7", "#,##0"),
    ("B5", "علبة واحدة لكل كم عميل", "C5", 4, "#,##0"),
    ("B6", "معدل التغطية", "C6", "=IFERROR(1/C5,0)", "0٪"),
    ("B7", "تكلفة العلبة (ر.س)", "C7", 1.5, "#,##0.00"),
    ("B8", "إجمالي عملاء الشهر", "C8", f"=SUM(D{R0}:D{R0+4})", "#,##0"),
    ("B9", "إجمالي المناديل المخططة", "C9", f"=SUM(I{R0}:I{R0+4})", "#,##0"),
    ("B10", "تكلفة الحملة (ر.س)", "C10", "=C9*C7", "#,##0"),
]
for lc, lv, vc, vv, fmt in DRV:
    put(ws, lc, lv, KEYB)
    put(ws, vc, vv, KEYV, fmt)

put(ws, "E3", "كيف تتغيّر الخطة", NOTEH)
n = put(ws, "E4",
        "الكميات كلها صيغ مربوطة بالخليتين C3 و C5. غيّر «مدة الحملة» أو «علبة "
        "واحدة لكل كم عميل» فتُعاد الكميات وأسابيع التوزيع والتكاليف تلقائيًا في "
        "كل الأوراق — لا تكتب كمية يدويًا إلا إذا أردت تثبيتها.", NOTEB)
n.alignment = Alignment(vertical="center", wrap_text=True)
ws.merge_cells("E4:H4")
ws.row_dimensions[4].height = 58

COLS = ["كود المحطة", "اسم المحطة", "الحي", "عملاء الشهر (زيارات يوليو)",
        "أيام الشهر", "عملاء/يوم", "نسبة العملاء", "الأولوية",
        "كمية المناديل المخططة", "معدل التوزيع اليومي", "تغطية العملاء",
        "التكلفة (ر.س)"]
ws.row_dimensions[12].height = 32
for i, h in enumerate(COLS):
    c = put(ws, f"{chr(65+i)}12", h, HEAD)
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

for i, (code, name, hood, vis, days, act, bud, ach, peak, pr) in enumerate(ST):
    r = R0 + i
    put(ws, f"A{r}", code, BODY, align="center")
    put(ws, f"B{r}", name, BODY)
    put(ws, f"C{r}", hood, BODY)
    put(ws, f"D{r}", vis, BODY, "#,##0", "center")
    put(ws, f"E{r}", days, BODY, "#,##0", "center")
    put(ws, f"F{r}", f"=ROUND(D{r}/E{r},0)", BODY, "#,##0", "center")
    put(ws, f"G{r}", f"=IFERROR(D{r}/$C$8,0)", BODY, "0.0٪", "center")
    put(ws, f"H{r}", PRIO[pr], BODY, align="center")
    #  الكمية = عملاء/يوم × أيام الحملة × معدل التغطية، مقرَّبة لأقرب 100 علبة
    put(ws, f"I{r}", f"=ROUND(F{r}*$C$4*$C$6,-2)", BODY, "#,##0", "center")
    put(ws, f"J{r}", f"=ROUND(I{r}/$C$4,0)", BODY, "#,##0", "center")
    put(ws, f"K{r}", f"=IFERROR(I{r}/(F{r}*$C$4),0)", BODY, "0.0٪", "center")
    put(ws, f"L{r}", f"=I{r}*$C$7", BODY, "#,##0", "center")

rt = R0 + 5
put(ws, f"A{rt}", "الإجمالي", HEAD, align="center")
for col in "BCEHJK":
    put(ws, f"{col}{rt}", None, HEAD)
put(ws, f"D{rt}", f"=SUM(D{R0}:D{R0+4})", HEAD, "#,##0", "center")
put(ws, f"F{rt}", f"=SUM(F{R0}:F{R0+4})", HEAD, "#,##0", "center")
put(ws, f"G{rt}", f"=SUM(G{R0}:G{R0+4})", HEAD, "0.0٪", "center")
put(ws, f"I{rt}", f"=SUM(I{R0}:I{R0+4})", HEAD, "#,##0", "center")
put(ws, f"L{rt}", f"=SUM(L{R0}:L{R0+4})", HEAD, "#,##0", "center")

put(ws, f"B{rt+2}", "المصدر", NOTEH)
src = put(ws, f"B{rt+3}",
          "عدد العملاء = الزيارات المسجَّلة في يوليو 2026 بمنصّة تحليل المحطات "
          "الخمس (آخر شهر مُقاس كاملًا؛ MK019 ثلاثون يومًا لنقص يوم في المصدر). "
          "الفعلي والموازنة بالّلتر من ملف Sales Analysis 2026. التقريب لأقرب "
          "100 علبة لتسهيل التعبئة بالكراتين.", NOTEB)
src.alignment = Alignment(vertical="center", wrap_text=True)
ws.merge_cells(f"B{rt+3}:H{rt+3}")
ws.row_dimensions[rt + 3].height = 58

put(ws, f"B{rt+5}", "ملاحظة على الأساس", NOTEH)
warn = put(ws, f"B{rt+6}",
           "التوزيع بنسبة عدد العملاء وحده يمنح MK007 نحو 61٪ من الكمية لأنها "
           "الأكبر حركةً، مع أن إنجازها 93٪؛ بينما MK002 و MK019 — وفجوتهما "
           "معًا 1.82 مليون لتر شهريًا وإنجازهما 24٪ و29٪ — تأخذان 13٪ فقط. "
           "عمود «الأولوية» هنا يوازن ذلك تشغيليًا؛ ولو أُريد ترجيح الكمية "
           "بالأولوية لا بعدد العملاء فهو تغيير في قاعدة التوزيع يُقرَّر صراحةً.",
           NOTEB)
warn.alignment = Alignment(vertical="center", wrap_text=True)
ws.merge_cells(f"B{rt+6}:H{rt+6}")
ws.row_dimensions[rt + 6].height = 72

# ═══════════ 2. «المحطات المستهدفة» ═══════════
for cc, suffix in (("F1", " (لتر)"), ("G1", " (لتر)")):
    if not str(S_TGT[cc].value).endswith(suffix):
        S_TGT[cc] = str(S_TGT[cc].value) + suffix

for i, (code, name, hood, vis, days, act, bud, ach, peak, pr) in enumerate(ST):
    r, br = 2 + i, R0 + i
    put(S_TGT, f"B{r}", code, BODY, align="center")
    put(S_TGT, f"C{r}", name, BODY)
    put(S_TGT, f"D{r}", "مكة", BODY, align="center")
    put(S_TGT, f"E{r}", hood, BODY)
    put(S_TGT, f"F{r}", act, BODY, "#,##0", "center")
    put(S_TGT, f"G{r}", bud, BODY, "#,##0", "center")
    S_TGT[f"H{r}"].number_format = "#,##0"
    put(S_TGT, f"J{r}", PRIO[pr], BODY)
    put(S_TGT, f"K{r}", AIM[code], BODY)
    put(S_TGT, f"L{r}", f"='أساس التوزيع'!I{br}", BODY, "#,##0", "center")
    put(S_TGT, f"M{r}", WEEKS[0], BODY, "yyyy-mm-dd", "center")
    put(S_TGT, f"N{r}", "مدير المحطة", BODY)
    put(S_TGT, f"O{r}", "لم تبدأ", BODY, align="center")
    put(S_TGT, f"P{r}", f"الإنجاز في يوليو {ach}٪ · الذروة {peak} · "
                        f"الكمية بنسبة {vis:,} عميل", BODY)

# ═══════════ 3. «خطة التوزيع» — ٤ أسابيع × ٥ محطات ═══════════
r = 2
for w, wdate in enumerate(WEEKS, start=1):
    for i, (code, name, hood, vis, days, act, bud, ach, peak, pr) in enumerate(ST):
        br = R0 + i
        put(S_PLAN, f"A{r}", f"الأسبوع {w}", BODY, align="center")
        put(S_PLAN, f"B{r}", wdate, BODY, "yyyy-mm-dd", "center")
        put(S_PLAN, f"C{r}", "مكة", BODY, align="center")
        put(S_PLAN, f"D{r}", hood, BODY)
        put(S_PLAN, f"E{r}", 1, BODY, "#,##0", "center")
        put(S_PLAN, f"F{r}", code, BODY, align="center")
        put(S_PLAN, f"G{r}",
            f"=ROUND('أساس التوزيع'!I{br}/'أساس التوزيع'!$C$3,0)",
            BODY, "#,##0", "center")
        put(S_PLAN, f"H{r}", "موظفو المحطة", BODY, align="center")
        put(S_PLAN, f"I{r}", "مشرف الوردية", BODY)
        put(S_PLAN, f"J{r}", "لم تبدأ", BODY, align="center")
        put(S_PLAN, f"K{r}", f"{name} — تركيز على الذروة {peak}", BODY)
        r += 1

# ═══════════ 4. «متابعة التنفيذ» ═══════════
r = 2
for w, wdate in enumerate(WEEKS, start=1):
    for i, (code, name, hood, vis, days, act, bud, ach, peak, pr) in enumerate(ST):
        put(S_EXEC, f"B{r}", code, BODY, align="center")
        put(S_EXEC, f"C{r}", name, BODY)
        put(S_EXEC, f"D{r}", wdate, BODY, "yyyy-mm-dd", "center")
        put(S_EXEC, f"E{r}", f"='خطة التوزيع'!G{r}", BODY, "#,##0", "center")
        S_EXEC[f"F{r}"].number_format = "#,##0"
        S_EXEC[f"G{r}"].number_format = "#,##0"
        put(S_EXEC, f"I{r}", "لم تبدأ", BODY, align="center")
        put(S_EXEC, f"K{r}", f"الأسبوع {w}", BODY, align="center")
        r += 1

# ═══════════ 5. «نتائج الحملة» ═══════════
for i, (code, name, hood, vis, days, act, bud, ach, peak, pr) in enumerate(ST):
    r, br = 2 + i, R0 + i
    put(S_RES, f"A{r}", code, BODY, align="center")
    put(S_RES, f"B{r}", name, BODY)
    put(S_RES, f"C{r}", act, BODY, "#,##0", "center")
    for col in "DEFG":
        S_RES[f"{col}{r}"].number_format = "#,##0"
    S_RES[f"H{r}"].number_format = "0.0٪"
    put(S_RES, f"I{r}", f"='أساس التوزيع'!I{br}", BODY, "#,##0", "center")
    put(S_RES, f"J{r}", f"='أساس التوزيع'!L{br}", BODY, "#,##0", "center")
    put(S_RES, f"K{r}", "لم يتم القياس", BODY, align="center")
    put(S_RES, f"L{r}", f"خط الأساس = لترات يوليو 2026 · الموازنة {bud:,} لتر", BODY)

# ═══════════ 6. Dashboard ═══════════
put(S_DASH, "B11", "تكلفة الحملة (ر.س)", KEYB)
put(S_DASH, "C11", "='أساس التوزيع'!C10", KEYV, "#,##0")
put(S_DASH, "B12", "وحدة المبيعات", KEYB)
put(S_DASH, "C12", "لتر", KEYV)
put(S_DASH, "E11", "أساس توزيع الكمية", NOTEH)
d = put(S_DASH, "E12",
        "الكمية موزَّعة بنسبة عدد العملاء في كل محطة — زيارات يوليو 2026. "
        "التفصيل والمُحدِّدات في ورقة «أساس التوزيع»: غيّر «مدة الحملة» أو "
        "«علبة واحدة لكل كم عميل» فتُعاد كل الكميات تلقائيًا.", NOTEB)
d.alignment = Alignment(vertical="center", wrap_text=True)
S_DASH.merge_cells("E12:H12")
S_DASH.row_dimensions[12].height = 58

wb.save(OUT)
print("تم ·", OUT)
print("الأوراق:", wb.sheetnames)
