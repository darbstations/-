# -*- coding: utf-8 -*-
"""صفّ «مناديل — حملة التغطية» في جدول توزيعات كل محطة داخل المنصّة.

الكميات هي نفسها الواردة في ملف `darb-tissue-campaign-2026.xlsx`: الكمية
موزَّعة بنسبة عدد العملاء في كل محطة (زيارات يوليو ٢٠٢٦)، بتغطية علبة لكل
أربعة عملاء على مدى أربعة أسابيع، وتكلفة العلبة ١٫٥ ر.س.

لا يُمسّ أيّ صف قائم — صفوف «مناديل» التي أضافها المستخدم تبقى كما هي،
والصف الجديد يحمل اسمًا مميَّزًا حتى لا يُقرأ تكرارًا لها.

يُكتب الصف في نصّ الصفحة **و** يُحقن وقت التشغيل: طبقة التحرير تستعيد
محتوى كل منطقة من التخزين المحلي عند التحميل، فالنصّ وحده لا يكفي لمن سبق
أن عدّل صفحة الخطة. ويحرس الحقنَ علمٌ في التخزين المحلي حتى لا يعود الصف
بعد أن يحذفه المستخدم عمدًا.

    python3 tools/add_tissue_rows.py [ملف-المصدر] [ملف-المخرَج]
"""
import os, sys, re, json

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = OUT = os.path.join(BASE, "darb-five-stations-analysis.html")
if len(sys.argv) > 1:
    SRC = sys.argv[1]
    OUT = sys.argv[2] if len(sys.argv) > 2 else SRC

SEED = "tissue2026"
UNIT = 1.5
WEEKS = 4
DAYS = WEEKS * 7

#  كود: (عملاء الشهر، أيام الشهر، الكمية الكلية)  — كما في ملف الحملة
PLAN = {
    "MK007": (136584, 31, 30800),
    "MK017": (35640, 31, 8000),
    "MK002": (18107, 31, 4100),
    "MK023": (21575, 31, 4900),
    "MK019": (10863, 30, 2500),
}
#  تقريب بنصف لأعلى كما يفعل Math.round في المنصّة، لا تقريب بايثون المصرفيّ
import math
RND = lambda n: math.floor(n + 0.5)
F = lambda n: f"{RND(n):,}"


def row_html(code):
    vis, days, total = PLAN[code]
    daily = RND(total / DAYS)
    cost = RND(daily * UNIT)
    cover = total / (RND(vis / days) * DAYS)
    return (
        f'<tr class="planrow bdnew" data-seed="{SEED}">'
        f"<td><b>مناديل — حملة التغطية</b></td>"
        f"<td>اليوم كامل</td>"
        f"<td>{F(daily)}</td>"
        f"<td>شهر كامل</td>"
        f"<td>{UNIT}</td>"
        f"<td>{F(cost)}</td>"
        f"<td>مدير المحطة</td>"
        f"<td>تغطية {cover*100:.0f}٪ من عملاء المحطة · {F(total)} علبة في "
        f"{WEEKS} أسابيع · {F(total*UNIT)} ر.س</td></tr>")


doc = open(SRC, encoding="utf-8").read()
before = doc
assert f'data-seed="{SEED}"' not in doc, "صفوف الحملة مضافة سلفًا"

# ═══════════ 1. الصف في نصّ كل صفحة خطة ═══════════
for code in PLAN:
    m = re.search(r'id="pg-%s-plan".*?(?=<div class="pgview")' % code, doc, re.S)
    page = m.group(0)
    tm = re.search(r'(<div class="ntable plantbl" data-plan="dist">.*?)</tbody>',
                   page, re.S)
    assert tm, code
    tbl = tm.group(1)
    new = re.sub(r'<tr class="planempty">.*?</tr>', "", tbl, flags=re.S) + row_html(code)
    doc = doc[:m.start()] + page.replace(tbl, new, 1) + doc[m.end():]

assert doc.count(f'data-seed="{SEED}"') == 5

# ═══════════ 2. الحقن وقت التشغيل لمن لديه نسخة محفوظة ═══════════
JS = """
<script id="tissue-js">
/* ═══ صف حملة المناديل في جدول توزيعات كل محطة ═══
   موجود في نصّ الصفحة أصلًا؛ وهذا الحقن لمن سبق أن عدّل صفحة الخطة فاستعادت
   طبقة التحرير نسخته المحفوظة بلا الصف. علَمٌ في التخزين المحلي يضمن أن
   الحقن يجري مرّة واحدة، فلا يعود الصف بعد حذفٍ متعمَّد.              */
(function(){
  var SEED=%s, ROWS=%s, FLAG='darb-seed:'+SEED;
  try{ if(localStorage.getItem(FLAG))return; }catch(_){}
  var zones=[];
  Object.keys(ROWS).forEach(function(code){
    var pv=document.getElementById('pg-'+code+'-plan'); if(!pv)return;
    var tbl=pv.querySelector('.plantbl[data-plan="dist"]'); if(!tbl)return;
    if(tbl.querySelector('[data-seed="'+SEED+'"]'))return;
    var tb=tbl.querySelector('tbody'); if(!tb)return;
    var e=tb.querySelector('.planempty'); if(e)e.remove();
    var tmp=document.createElement('tbody'); tmp.innerHTML=ROWS[code];
    tb.appendChild(tmp.firstChild);
    var z=tbl.closest('[data-ez]'); if(z&&zones.indexOf(z)<0)zones.push(z);
  });
  /* إطلاق الحفظ المحلي ثم تثبيت العلم بعده، لا قبله */
  zones.forEach(function(z){z.dispatchEvent(new Event('input',{bubbles:true}));});
  if(window.DARB&&DARB.planSync)DARB.planSync();
  if(window.DARB&&DARB.rebase)DARB.rebase();
  setTimeout(function(){ try{localStorage.setItem(FLAG,'1');}catch(_){} },1500);
})();
</script>
""" % (json.dumps(SEED),
       json.dumps({c: row_html(c) for c in PLAN}, ensure_ascii=False).replace("</", "<\\/"))

i = doc.index('<script id="hubreg-js">')
doc = doc[:i] + JS.strip() + "\n" + doc[i:]

open(OUT, "w", encoding="utf-8").write(doc)

bl, al = before.splitlines(), doc.splitlines()
print("تم ·", round(len(doc.encode()) / 1024), "KB ·", OUT)
print(f"الأسطر: {len(bl)} ← {len(al)}")
tot = sum(v[2] for v in PLAN.values())
print(f"الإجمالي: {F(tot)} علبة · {F(tot*UNIT)} ر.س")
for c, (vis, days, total) in PLAN.items():
    print(f"  {c}: {F(total/DAYS)} علبة/يوم · {F(total)} إجمالًا "
          f"· {F(RND(total/DAYS)*UNIT)} ر.س/يوم")
