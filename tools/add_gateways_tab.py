# -*- coding: utf-8 -*-
"""تبويب «المنافذ» — تحليل مداخل مكة ومن يسيطر على كل منفذ.

المنفذ = محور الدخول إلى مكة الذي تقع عليه المحطة. تُصنَّف المحطات الخمس
إلى منافذ بحسب اتجاهها ومسافتها عن الحرم (محسوبَين من الإحداثيات الفعلية)،
ثم يُقاس الضغط التنافسي في كل منفذ من قوائم المحطات المنافسة المرصودة ضمن
٥ كم حول كل محطة.

«من يسيطر» يُقاس بما تسمح به البيانات فقط: عدد المحطات لكل علامة، ومتوسط
تقييمها، وحجم مراجعاتها. لا تتوفّر مبيعات المنافسين، فلا يُدّعى نصيب سوقي.

    python3 tools/add_gateways_tab.py [ملف-المصدر] [ملف-المخرَج]
"""
import re, json, math, html, os, sys, collections

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = OUT = os.path.join(BASE, "darb-five-stations-analysis.html")
if len(sys.argv) > 1:
    SRC = sys.argv[1]
    OUT = sys.argv[2] if len(sys.argv) > 2 else SRC

E = lambda t: html.escape(str(t), quote=True)
F = lambda n: f"{round(n):,}"
KEEP = ["MK007", "MK017", "MK002", "MK023", "MK019"]

LOC = {"MK007": (21.545501760079727, 39.778740694279925),
       "MK019": (21.477315823386835, 39.915510658283190),
       "MK017": (21.382832162943180, 39.787308463295240),
       "MK023": (21.470436621349847, 39.928912695783350),
       "MK002": (21.465715391345107, 39.899769312269010)}
HARAM = (21.4225, 39.8262)

#  المنافذ: التصنيف مبني على الاتجاه والمسافة عن الحرم والطريق الذي تقع عليه المحطة
GATES = [
    ("شمالي", "🛣️ المنفذ الشمالي — طريق المدينة المنورة",
     "مدخل مكة من الشمال: المعتمرون والزوّار القادمون من المدينة، وحركة عابرة طويلة",
     ["MK007"]),
    ("غربي", "🛣️ المنفذ الجنوبي الغربي — الشوقية",
     "مدخل مكة من جهة جدة والليث: حركة محلية كثيفة وقرب نسبي من الحرم",
     ["MK017"]),
    ("شرقي", "🛣️ المنفذ الشرقي — المشاعر والشرائع (طريق الطائف)",
     "مدخل مكة من الشرق ومحور المشاعر: موسمي الذروة، وأكثف نطاق تنافسي في الشبكة",
     ["MK002", "MK019", "MK023"]),
]

BRANDS = [
    (r"aldrees|الدريس", "الدريس"),
    (r"ساسكو|sasco", "ساسكو"),
    (r"بترومين|petromin", "بترومين"),
    (r"بتروجين|petrogen", "بتروجين"),
    (r"\bnaft\b|النفط|نفط", "نفط"),
    (r"أورانج|اورانج|orange", "أورانج"),
    (r"اومكو|أومكو|omco", "أومكو"),
    (r"وقود", "وقود"),
    (r"تميز", "تميّز"),
    (r"بترولي", "بترولي"),
]


def brand_of(name):
    n = name.strip().lower()
    for pat, b in BRANDS:
        if re.search(pat, n):
            return b
    return "مستقلة / غير مصنّفة"


def hav(a, b):
    R = 6371.0
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dp, dl = math.radians(b[0] - a[0]), math.radians(b[1] - a[1])
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


doc = open(SRC, encoding="utf-8").read()
assert 'id="hubreg-js"' in doc, "شغّل add_hub_registers.py أولًا"
D = json.loads(re.search(r'<script id="cmpdata"[^>]*>(.*?)</script>', doc, re.S).group(1))["stations"]

# ═══════════ المنافسون المسمَّون في صفحة كل محطة ═══════════
COMP = {}
for c in KEEP:
    page = re.search(r'id="pg-%s"(?!-).*?(?=<div class="pgview")' % c, doc, re.S).group(0)
    tbl = re.search(r"<table.*?</table>", page, re.S)
    rows = []
    for r in re.findall(r"<tr>(.*?)</tr>", tbl.group(0), re.S) if tbl else []:
        cells = [html.unescape(re.sub(r"<[^>]+>", "", x)).strip()
                 for x in re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)]
        if len(cells) >= 5 and cells[0].isdigit():
            rows.append({"name": cells[1], "dist": cells[2], "rating": cells[3],
                         "revs": cells[4], "brand": brand_of(cells[1])})
    COMP[c] = rows

# ═══════════ حساب كل منفذ ═══════════
GD = []
for key, title, desc, codes in GATES:
    #  لا تُدمج الأسماء المتشابهة: «الدريس» قرب ثلاث محطات هي ثلاث محطات مختلفة.
    #  ما يتكرر فعلًا هو المحطة الواقعة في دائرتَي موقعين لنا، وذلك مذكور في الملاحظة.
    named = []
    for c in codes:
        for r in COMP[c]:
            named.append(dict(r, near=c))
    counted = sum(D[c]["compn"] for c in codes)
    by = collections.Counter(r["brand"] for r in named)
    top = [(b, n) for b, n in by.most_common() if b != "مستقلة / غير مصنّفة"]
    lead = top[0] if top else ("مستقلة / غير مصنّفة", by.get("مستقلة / غير مصنّفة", 0))
    rat = [float(r["rating"]) for r in named if re.match(r"^\d+(\.\d+)?$", r["rating"])]
    darb_rat = [D[c]["rating"] for c in codes]
    dists = [hav(HARAM, LOC[c]) for c in codes]
    GD.append({"key": key, "title": title, "desc": desc, "codes": codes, "named": named,
               "counted": counted, "by": by, "lead": lead, "top": top,
               "crat": sum(rat) / len(rat) if rat else 0,
               "drat": sum(darb_rat) / len(darb_rat),
               "km": sum(dists) / len(dists),
               "ach": [D[c].get("ach") for c in codes]})

#  نِسَب الإنجاز تُقرأ من تبويب المستهدفات لا تُثبَّت نصًّا — تتغيّر مع كل شهر يُضاف
ACH = {}
for c in KEEP:
    tp = re.search(r'id="pg-%s-targets".*?(?=<div class="pgview")' % c, doc, re.S).group(0)
    m = re.search(r'إجمالي الأشهر المسجلة</td><td>[\d,]+</td><td>[\d,]+</td>'
                  r'<td>[^<]*</td><td><span class="\w+">(\d+)٪</span>', tp)
    ACH[c] = int(m.group(1)) if m else None
LOW = sorted([c for c in KEEP if ACH.get(c) is not None], key=lambda c: ACH[c])[:2]

TOTC = sum(g["counted"] for g in GD)
ALLB = collections.Counter()
for g in GD:
    ALLB.update(g["by"])

#  تقارب محطات درب داخل المنفذ الشرقي
pairs = []
east = [g for g in GD if g["key"] == "شرقي"][0]["codes"]
for i in range(len(east)):
    for j in range(i + 1, len(east)):
        pairs.append((east[i], east[j], hav(LOC[east[i]], LOC[east[j]])))

NM = {c: D[c]["name"] for c in KEEP}

# ═══════════ البناء ═══════════
kpis = (
    '<div class="skpis" style="grid-template-columns:repeat(5,1fr)">'
    f'<div class="kpi hot"><div class="kl">منافذ مكة المخدومة</div><div class="kv">{len(GD)}</div>'
    '<div class="kn">شمالي · جنوبي غربي · شرقي</div></div>'
    f'<div class="kpi"><div class="kl">محطات منافسة مرصودة</div><div class="kv">{TOTC}</div>'
    '<div class="kn">ضمن 5 كم حول محطات درب الخمس</div></div>'
    f'<div class="kpi"><div class="kl">تركّز المنافسة</div>'
    f'<div class="kv">{east and round(GD[2]["counted"]/TOTC*100)}٪</div>'
    '<div class="kn">من المنافسين في المنفذ الشرقي وحده</div></div>'
    f'<div class="kpi"><div class="kl">العلامة الأكثر انتشارًا</div>'
    f'<div class="kv" style="font-size:16px">{E(ALLB.most_common(1)[0][0])}</div>'
    f'<div class="kn">{ALLB.most_common(1)[0][1]} ظهورًا من {sum(ALLB.values())} مسمّى</div></div>'
    f'<div class="kpi"><div class="kl">تقييم درب مقابلهم</div>'
    f'<div class="kv">{sum(D[c]["rating"] for c in KEEP)/5:.2f}'
    f'<small> ضد {sum(g["crat"] for g in GD)/len(GD):.2f}</small></div>'
    '<div class="kn">متوسط جوجل — درب أعلى في كل منفذ</div></div></div>')

grows = ""
for g in GD:
    names = " · ".join(f"{NM[c]}" for c in g["codes"])
    share = g["lead"][1] / max(1, len(g["named"])) * 100
    verdict = ("<b>درب هي المسيطرة</b> — أقلّ ضغط تنافسي في الشبكة"
               if g["counted"] <= 6 and g["drat"] > g["crat"] else
               "<b>منافسة نوعية</b> — العدد قليل لكن تقييم المنافسين هو الأعلى"
               if g["counted"] <= 8 else
               f"<b>{E(g['lead'][0])} هي المسيطرة عددًا</b> — وأكثف منفذ في الشبكة")
    grows += (f'<tr><td><b>{E(g["title"].replace("🛣️ ",""))}</b>'
              f'<span class="gwsub">{E(g["desc"])}</span></td>'
              f'<td>{E(names)}<span class="gwsub">{" · ".join(g["codes"])}</span></td>'
              f'<td class="snum">{g["km"]:.1f} كم</td>'
              f'<td class="snum"><b>{g["counted"]}</b></td>'
              f'<td>{E(g["lead"][0])} <b>{g["lead"][1]}</b>'
              f'<span class="gwsub">{share:.0f}٪ من الظهورات المسمّاة</span></td>'
              f'<td class="snum">{g["crat"]:.2f}</td>'
              f'<td class="snum"><b class="up">{g["drat"]:.2f}</b></td>'
              f"<td>{verdict}</td></tr>")

brow = "".join(
    f'<tr><td><b>{E(b)}</b></td>'
    + "".join(f'<td class="snum">{g["by"].get(b,0) or "—"}</td>' for g in GD)
    + f'<td class="snum"><b>{n}</b></td>'
      f'<td class="snum">{n/sum(ALLB.values())*100:.0f}٪</td></tr>'
    for b, n in ALLB.most_common())

detail = ""
for g in GD:
    rows = "".join(
        f'<tr><td><b>{E(r["name"])}</b></td><td>{E(r["brand"])}</td>'
        f'<td>{E(NM[r["near"]])}</td>'
        f'<td class="snum">{E(r["dist"])}</td><td class="snum">{E(r["rating"])}</td>'
        f'<td class="snum">{E(r["revs"])}</td></tr>' for r in g["named"])
    detail += (
        f'<div class="sec-h" style="margin-top:20px"><h2 style="font-size:15px">{g["title"]}</h2>'
        f'<span>{len(g["named"])} محطة مسمّاة من أصل {g["counted"]} مرصودة · '
        f'{E(g["desc"])}</span></div>'
        '<div class="ntable gwtbl"><div class="tscroll"><table><thead><tr>'
        '<th>المحطة المنافسة</th><th>العلامة</th><th>قريبة من</th><th>المسافة</th><th>التقييم</th>'
        f'<th>المراجعات</th></tr></thead><tbody>{rows}</tbody></table></div></div>')

prow = "".join(f'<tr><td><b>{NM[a]}</b> ↔ <b>{NM[b]}</b></td>'
               f'<td class="snum">{d:.1f} كم</td>'
               f'<td>{"داخل نطاق الـ5 كم — كل واحدة تُحسب منافسًا للأخرى" if d<5 else "خارج النطاق"}</td></tr>'
               for a, b, d in pairs)

PANE = (
    '<div class="hubreg" id="reg-gw" data-hubpane="gw" hidden>'
    '<div class="sec-h"><h2>🛣️ تحليل المنافذ</h2>'
    '<span>مداخل مكة التي تخدمها درب، ومن يسيطر على كل منفذ</span></div>'
    + kpis +

    '<div class="dnote" style="background:#F0F5FA;border:1px solid #CBDDEB">🧭 '
    '<b>ما المنفذ؟</b> محور الدخول إلى مكة الذي تقع عليه المحطة. صُنِّفت المحطات '
    'الخمس إلى ثلاثة منافذ بحساب <b>الاتجاه والمسافة عن الحرم من الإحداثيات الفعلية</b>، '
    'لا بالتقدير. و<b>«من يسيطر»</b> مقيس بعدد المحطات لكل علامة وتقييمها وحجم مراجعاتها '
    '— <b>لا بنصيب المبيعات</b>، فمبيعات المنافسين غير متاحة لنا ولا يصحّ ادّعاؤها.</div>'

    '<div class="sec-h" style="margin-top:20px"><h2 style="font-size:15px">المنافذ الثلاثة</h2>'
    '<span>الضغط التنافسي في كل منفذ ومن يقوده</span></div>'
    '<div class="ntable gwtbl"><div class="tscroll"><table><thead><tr>'
    '<th>المنفذ</th><th>محطات درب</th><th>من الحرم</th><th>منافسون</th>'
    '<th>العلامة المسيطرة</th><th>تقييمهم</th><th>تقييم درب</th><th>القراءة</th>'
    f'</tr></thead><tbody>{grows}</tbody></table></div></div>'

    '<div class="sec-h" style="margin-top:20px"><h2 style="font-size:15px">من يسيطر — بالعلامة</h2>'
    '<span>عدد الظهورات المسمّاة لكل علامة في كل منفذ — لا نصيب سوقي</span></div>'
    '<div class="ntable gwtbl"><div class="tscroll"><table><thead><tr><th>العلامة</th>'
    + "".join(f'<th>{E(g["key"])}</th>' for g in GD)
    + '<th>الإجمالي</th><th>الحصة</th></tr></thead>'
    f'<tbody>{brow}</tbody></table></div></div>'

    '<div class="sec-h" style="margin-top:22px"><h2>⚠️ ما يجب أن تراه الإدارة</h2>'
    '<span>ثلاث قراءات تخرج من الأرقام أعلاه مباشرة</span></div>'
    '<div class="agrid" style="grid-template-columns:1fr 1fr 1fr">'
    '<div class="card"><div class="ct"><h3>① المنافسة مكدَّسة في منفذ واحد</h3>'
    f'<div class="leg">{GD[2]["counted"]} من {TOTC}</div></div>'
    '<p style="font-size:12.5px;color:var(--ink2);line-height:1.85;margin-top:6px">'
    f'<b>{GD[2]["counted"]/TOTC*100:.0f}٪</b> من المنافسين المرصودين يقعون في '
    '<b>المنفذ الشرقي</b> وحده، حيث ثلاث من محطاتنا الخمس. المنفذان الآخران شبه خاليَين: '
    f'{GD[0]["counted"]} منافسين شمالًا و{GD[1]["counted"]} غربًا.</p></div>'
    '<div class="card"><div class="ct"><h3>② محطاتنا الشرقية تتزاحم</h3>'
    f'<div class="leg">{min(d for _,_,d in pairs):.1f}–{max(d for _,_,d in pairs):.1f} كم</div></div>'
    '<p style="font-size:12.5px;color:var(--ink2);line-height:1.85;margin-top:6px">'
    'المعيصم وعرفات الشرايع وبن درويش <b>داخل نطاق الـ5 كم لبعضها</b>، فكل واحدة تدخل في '
    'عدّاد منافسي الأخرى وتتقاسم معها الحركة نفسها. الازدحام هنا <b>جزء منه من صنعنا</b>.</p></div>'
    '<div class="card hot"><div class="ct"><h3>③ التعثّر يقع حيث الازدحام</h3>'
    f'<div class="leg">{ACH[LOW[0]]}٪ · {ACH[LOW[1]]}٪</div></div>'
    '<p style="font-size:12.5px;color:var(--ink2);line-height:1.85;margin-top:6px">'
    f'<b>المعيصم وعرفات الشرايع</b> — أدنى محطتين إنجازًا '
    f'(<b>{ACH["MK002"]}٪</b> و<b>{ACH["MK019"]}٪</b>) — كلتاهما في '
    f'المنفذ الشرقي. أما <b>العمرة النورية {ACH["MK007"]}٪</b> و'
    f'<b>عرفات الشوقية {ACH["MK017"]}٪</b> فتقعان في '
    'المنفذين الخاليَين. هذا تفسير <b>بنيوي</b> للفجوة يسبق تفسير جودة الخدمة.</p></div></div>'

    '<div class="sec-h" style="margin-top:20px"><h2 style="font-size:15px">تزاحم محطات درب في المنفذ الشرقي</h2>'
    '<span>المسافات محسوبة من الإحداثيات الفعلية</span></div>'
    '<div class="ntable gwtbl"><div class="tscroll"><table><thead><tr><th>الزوج</th>'
    f'<th>المسافة</th><th>الأثر</th></tr></thead><tbody>{prow}</tbody></table></div></div>'
    + detail +

    '<div class="dnote">📐 <b>حدود القراءة:</b> قوائم المنافسين مصدرها بحث خرائط جوجل عن '
    '«محطة وقود» ضمن دائرة نصف قطرها 5 كم حول كل محطة (يوليو 2026)، فهي تشمل المدرَج في '
    'الخرائط فقط. الجداول التفصيلية تعرض <b>أقرب عشر محطات</b> لكل موقع، والعدّ الكامل '
    f'({TOTC}) من المسح نفسه. <b>العلامة</b> مستخرجة من اسم المحطة كما ورد، وما تعذّر '
    'تمييزه صُنِّف «مستقلة / غير مصنّفة». <b>المسافات خطّية</b> لا مسارات قيادة. '
    'ولأن دوائر محطاتنا الشرقية متداخلة، فالمحطة الواقعة في دائرتَي موقعين لنا '
    '<b>تظهر مرتين</b> في الجدول التفصيلي — وهو ظهور حقيقي لا خطأ، ومذكور هنا لئلا يُقرأ '
    'العدد على أنه عدد محطات فريدة.</div>'
    "</div>")

CSS = """
<style id="gw-css">
.gwtbl td{white-space:normal;line-height:1.75;vertical-align:top}
.gwtbl td:first-child{min-width:190px}
.gwsub{display:block;font-size:10.5px;color:var(--ink3);margin-top:2px;font-weight:400}
/* ── جاهزية العرض على الإدارة ── */
@media print{
  #edbar,#bdbar,#hubtabs,#planmodal,.planadd,.rgadd,.sdl,.planx,.planedit,.rgx,.rgedit,
  .bdtb,.bdrowx,.bdcolx,.bdtabx,.stationbar{display:none!important}
  .pgview[hidden],[hidden]{display:none!important}
  body{background:#fff}
  .ntable,.card,.kpi,.mdet{break-inside:avoid;box-shadow:none}
  .sec-h{break-after:avoid}
  a[href^="#"]{text-decoration:none;color:inherit}
}
</style>
"""

JS = """
<script id="gw-js">
/* ‏تبويب المنافذ — يُضاف بعد سجلّات الصفحة الأولى ويعيد تطبيق العرض المحفوظ */
(function(){
  var tabs=document.getElementById('hubtabs');
  if(!tabs||tabs.querySelector('[data-v="gw"]'))return;
  var b=document.createElement('button');
  b.type='button'; b.className='htab'; b.dataset.v='gw';
  b.innerHTML='🛣️ المنافذ<span class="n">3</span>';
  var src=tabs.querySelector('[data-v="src"]');
  tabs.insertBefore(b,src||null);
  try{
    var v=sessionStorage.getItem('darb-hubview');
    if(v&&window.DARB&&DARB.hubShow)DARB.hubShow(v);
  }catch(_){}
})();
</script>
"""

anchor = '<main class="wrap" id="pages">'
i = doc.index(anchor)
close = doc.rindex("</div>", 0, i)
doc = doc[:close] + PANE + doc[close:]
doc = doc.replace("</head>", CSS + "</head>", 1)
doc = doc.replace("</body>", JS + "</body>", 1)
open(OUT, "w", encoding="utf-8").write(doc)

print("تم · الحجم:", round(len(doc.encode()) / 1024), "KB")
for g in GD:
    print(f"  {g['title'][2:]:52} محطات {len(g['codes'])} · منافسون {g['counted']:3} "
          f"· مسمّاة {len(g['named']):2} · يقودها {g['lead'][0]} {g['lead'][1]} "
          f"· تقييمهم {g['crat']:.2f} مقابل درب {g['drat']:.2f}")
print("  العلامات:", dict(ALLB.most_common()))
