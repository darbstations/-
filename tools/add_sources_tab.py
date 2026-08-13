# -*- coding: utf-8 -*-
"""تبويب «المصادر والدراسات» في الصفحة الأولى — أرشيف المنصّة.

يجمع في مكان واحد كل ما بُنيت عليه المنصّة:
  • ملفات المصدر السبعة مضمَّنة داخل الصفحة (base64) وتُنزَّل بضغطة، مع
    بيان ما يغذّيه كل ملف من تبويبات المنصّة.
  • دراسة «الحركة الصباحية وخطة تفعيل الفطور» تُفتح داخل المنصّة كما هي
    في إطار مستقل — بلا تصادم أنماط ولا فقدان تنسيق.
  • خريطة المنصّة: ما تحتويه من صفحات وتبويبات.
  • سلسلة النسخ السابقة للتقرير موثّقة بالتاريخ والحجم.

    python3 tools/add_sources_tab.py [ملف-المصدر] [ملف-المخرَج]
"""
import base64, html, json, os, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
SRC = OUT = os.path.join(BASE, "darb-five-stations-analysis.html")
if len(sys.argv) > 1:
    SRC = sys.argv[1]
    OUT = sys.argv[2] if len(sys.argv) > 2 else SRC

E = lambda t: html.escape(str(t), quote=True)

XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

#  الملف · الاسم المعروض · ما يغذّيه · الفترة · نوع المحتوى
FILES = [
    ("01-monthly-report-2026.xlsx", "تقرير المبيعات الشهري 2026",
     "المبيعات الشهرية واليومية · بطاقات الشهور · مزيج الوقود · ساعات الذروة",
     "يناير → يونيو 2026", XLSX),
    ("02-actual-vs-budget-2026.xlsx", "الموازنة مقابل الفعلي — حتى 30 أبريل",
     "تبويب المستهدفات · نِسَب الإنجاز · الفجوة عن الموازنة باللترات",
     "2026 كاملة (موازنة) · مسجَّل حتى يونيو", XLSX),
    ("03-station-units.xlsx", "وحدات وشركاء داخل المحطات",
     "تبويب الشركاء عبر اليوم · الفترات الست · قوائم الشركاء في النماذج",
     "قائمة حالية", XLSX),
    ("04-external-partners.xlsx", "المنشآت حول المحطات",
     "تبويب الشركاء الخارجيون · قائمة الشركاء الخارجيين في نموذج الشراكة",
     "مسح ميداني", XLSX),
    ("05-station-locations.xlsx", "مواقع المحطات وإحداثياتها",
     "إحداثيات كل محطة · روابط الخرائط · حساب المسافات",
     "ثابت", XLSX),
    ("06-monthly-reasons-2026.xlsx", "تقرير التحليل التفصيلي — أسباب الأشهر",
     "«السبب المؤكد» في بطاقة كل شهر · جدول «سبب كل شهر» في المستهدفات",
     "يناير → يونيو 2026", XLSX),
    ("08-july-dashboard-2026.json", "لوحة المبيعات — دفعة 2026-08-12 (الخمس محطات)",
     "مبيعات يوليو شهريًا ويوميًا · السلسلة اليومية الكاملة 212 يومًا · مزيج الوقود",
     "يناير → يوليو 2026", "application/json"),
]
STUDY = ("07-morning-breakfast-plan.html", "محطة العمرة — الحركة الصباحية وخطة تفعيل الفطور",
         "دراسة مستقلة سابقة: قراءة الحركة الصباحية في MK007 وخطة تفعيلها",
         "دراسة قائمة بذاتها")

#  سلسلة النسخ السابقة — توثيق لا تضمين (النسخة الحالية تغني عنها)
LINEAGE = [
    ("تحليل المواقع — 55 محطة", "4.2 م.ب", "الأصل الذي قُلِّصت منه المنصّة إلى خمس محطات"),
    ("تحليل الخمس محطات — النسخة الأولى", "474 ك.ب", "بعد التقليص وإضافة طبقة التحرير"),
    ("+ اللترات بجانب الريال", "484 ك.ب", "كل رقم بالريال صار معه مقابله باللترات"),
    ("+ استفسارات العملاء", "659 ك.ب", "165 سجلًا مربوطًا بكود المحطة"),
    ("+ الشركاء عبر اليوم والخطة التشغيلية", "1.12 م.ب", "الفترات الست ومحاور الخطة الأربعة"),
    ("+ أسباب الأشهر (النسخة المعتمدة)", "1.30 م.ب", "الأساس الذي تُبنى عليه الإضافات الآن"),
]

MAP = [
    ("الصفحة الأولى", "بطاقات المحطات الخمس · سجل الحملات · سجل الشراكات · "
                      "سجل التوزيعات · المصادر والدراسات"),
    ("لكل محطة (8 تبويبات)", "التحليل الكامل · المبيعات الشهرية · المبيعات اليومية · "
                             "المستهدفات · استفسارات العملاء · الشركاء عبر اليوم · "
                             "الشركاء الخارجيون · الخطة التشغيلية"),
    ("مقارنة", "مقارنة المناطق والمحطات على أي مؤشر"),
    ("التحرير", "تحرير كل نص وجدول وعمود وتبويب · تراجع وإعادة · تنزيل نسخة مستقلة"),
]

doc = open(SRC, encoding="utf-8").read()
assert 'id="hubreg-js"' in doc, "شغّل add_hub_registers.py أولًا"

# ═══════════ تضمين الملفات ═══════════
blobs, rows = {}, ""
total = 0
for fn, name, feeds, period, mime in FILES:
    p = os.path.join(DATA, fn)
    raw = open(p, "rb").read()
    total += len(raw)
    blobs[fn] = {"b64": base64.b64encode(raw).decode(), "mime": mime, "name": fn}
    rows += (f"<tr><td><b>{E(name)}</b><span class='sfn'>{E(fn)}</span></td>"
             f"<td>{E(feeds)}</td><td>{E(period)}</td>"
             f"<td class='snum'>{len(raw)/1024:,.0f} ك.ب</td>"
             f"<td><button type='button' class='sdl' data-f='{E(fn)}'>⬇️ تنزيل</button></td></tr>")

sp = os.path.join(DATA, STUDY[0])
study_html = open(sp, encoding="utf-8").read()
study_size = os.path.getsize(sp)
total += study_size
blobs[STUDY[0]] = {"b64": base64.b64encode(study_html.encode()).decode(),
                   "mime": "text/html;charset=utf-8", "name": STUDY[0]}

lineage = "".join(f"<tr><td><b>{E(a)}</b></td><td class='snum'>{E(b)}</td><td>{E(c)}</td></tr>"
                  for a, b, c in LINEAGE)
mapping = "".join(f"<tr><td><b>{E(a)}</b></td><td>{E(b)}</td></tr>" for a, b in MAP)

PANE = (
    '<div class="hubreg" id="reg-src" data-hubpane="src" hidden>'
    '<div class="sec-h"><h2>📚 المصادر والدراسات</h2>'
    '<span>كل ما بُنيت عليه المنصّة — محفوظ داخلها ويُنزَّل بضغطة</span></div>'

    '<div class="skpis" style="grid-template-columns:repeat(4,1fr)">'
    f'<div class="kpi hot"><div class="kl">ملفات المصدر</div><div class="kv">{len(FILES)}'
    '</div><div class="kn">مضمَّنة داخل الصفحة — لا تُفقد مع الملف</div></div>'
    '<div class="kpi"><div class="kl">دراسات مرفقة</div><div class="kv">1</div>'
    '<div class="kn">تُفتح داخل المنصّة كما هي</div></div>'
    f'<div class="kpi"><div class="kl">حجم الأرشيف</div><div class="kv">{total/1024/1024:.2f}'
    '<small> م.ب</small></div><div class="kn">قبل ترميز التضمين</div></div>'
    f'<div class="kpi"><div class="kl">نسخ سابقة موثّقة</div><div class="kv">{len(LINEAGE)}'
    '</div><div class="kn">سلسلة بناء المنصّة</div></div></div>'

    '<div class="sec-h" style="margin-top:20px"><h2 style="font-size:15px">ملفات المصدر</h2>'
    '<span>كل ملف وما يغذّيه من تبويبات المنصّة</span></div>'
    '<div class="ntable srctbl"><div class="tscroll"><table><thead><tr>'
    '<th>الملف</th><th>ما يغذّيه في المنصّة</th><th>الفترة</th><th>الحجم</th><th></th>'
    f'</tr></thead><tbody>{rows}</tbody></table></div></div>'

    '<div class="sec-h" style="margin-top:20px"><h2 style="font-size:15px">📖 دراسة مرفقة</h2>'
    f'<span>{E(STUDY[2])}</span></div>'
    '<div class="card"><div class="ct">'
    f'<h3>{E(STUDY[1])}</h3><div class="leg">{E(STUDY[3])} · {study_size/1024:,.0f} ك.ب</div></div>'
    '<div class="rgbar" style="margin:10px 0 0">'
    '<button type="button" class="rgadd" id="sOpen">📖 افتح الدراسة هنا</button>'
    f"<button type=\"button\" class='sdl' data-f='{E(STUDY[0])}'>⬇️ تنزيل</button>"
    '<span class="rgsum">تُعرض كما كُتبت أصلًا، بتنسيقها المستقل</span></div>'
    '<div id="sFrameWrap" hidden><iframe id="sFrame" title="دراسة الحركة الصباحية"></iframe></div>'
    '</div>'

    '<div class="sec-h" style="margin-top:20px"><h2 style="font-size:15px">🗺️ خريطة المنصّة</h2>'
    '<span>ما تحتويه هذه المنصّة</span></div>'
    '<div class="ntable"><div class="tscroll"><table><thead><tr><th>الموضع</th>'
    f'<th>المحتوى</th></tr></thead><tbody>{mapping}</tbody></table></div></div>'

    '<div class="sec-h" style="margin-top:20px"><h2 style="font-size:15px">🧬 سلسلة النسخ</h2>'
    '<span>كيف وصلت المنصّة إلى شكلها الحالي — النسخة الحالية تغني عن سابقاتها</span></div>'
    '<div class="ntable"><div class="tscroll"><table><thead><tr><th>النسخة</th><th>الحجم</th>'
    f'<th>ما أضافته</th></tr></thead><tbody>{lineage}</tbody></table></div></div>'

    '<div class="dnote">📐 <b>ملاحظة على الأرشفة:</b> الملفات الستة والدراسة مضمَّنة داخل هذا '
    'الملف نفسه، فتبقى معه أينما نُقل ولا تحتاج مرفقات خارجية. '
    'أما <b>استفسارات العملاء</b> فمصدرها جدول Google خارجي وليس ملفًا محليًا — '
    'بياناتها منقولة داخل تبويب الاستفسارات لكل محطة، ولا يوجد ملف يُنزَّل لها هنا. '
    'وسلسلة النسخ السابقة موثّقة للرجوع ولم تُضمَّن لأن النسخة الحالية تحتويها جميعًا.</div>'
    "</div>")

CSS = """
<style id="sources-css">
.srctbl td{white-space:normal;line-height:1.7;vertical-align:top}
.srctbl td:first-child{min-width:230px}
.srctbl .sfn{display:block;font-size:10.5px;color:var(--ink3);margin-top:2px;
  font-family:ui-monospace,SFMono-Regular,Menlo,monospace;direction:ltr;text-align:right}
.snum{font-variant-numeric:tabular-nums;white-space:nowrap}
.sdl{font-family:inherit;font-size:12.5px;font-weight:700;cursor:pointer;white-space:nowrap;
  background:#fff;border:1px solid var(--line2);color:var(--ink2);border-radius:9px;
  padding:6px 12px;transition:.14s}
.sdl:hover{border-color:var(--orange);color:var(--orange)}
#sFrameWrap{margin-top:12px;border:1px solid var(--line2);border-radius:12px;overflow:hidden;
  background:#fff}
#sFrame{width:100%;height:78vh;border:0;display:block}
</style>
"""

JS = """
<script type="application/json" id="src-blobs">%s</script>
<script id="sources-js">
/* ═══ تبويب المصادر والدراسات ═══
   الملفات مضمَّنة base64؛ التنزيل عبر قدرة المنصّة إن وُجدت، وإلا برابط Blob. */
(function(){
  var B={};
  try{ B=JSON.parse(document.getElementById('src-blobs').textContent); }catch(e){}

  var tabs=document.getElementById('hubtabs');
  if(tabs&&!tabs.querySelector('[data-v="src"]')){
    var b=document.createElement('button');
    b.type='button'; b.className='htab'; b.dataset.v='src';
    b.innerHTML='📚 المصادر<span class="n">'+Object.keys(B).length+'</span>';
    tabs.appendChild(b);
    /* ‏سجلّات الصفحة الأولى استعادت العرض المحفوظ قبل وجود هذا الزر،
       فنعيد تطبيقه الآن حتى يفتح التبويب الصحيح بعد إعادة التحميل */
    try{
      var v=sessionStorage.getItem('darb-hubview');
      if(v&&window.DARB&&DARB.hubShow)DARB.hubShow(v);
    }catch(_){}
  }

  function bytes(b64){
    var bin=atob(b64), a=new Uint8Array(bin.length);
    for(var i=0;i<bin.length;i++)a[i]=bin.charCodeAt(i);
    return a;
  }
  function download(fn){
    var rec=B[fn]; if(!rec)return;
    var dl=window.claude&&window.claude.downloads;
    if(dl&&dl.save){
      dl.save({filename:fn,data:bytes(rec.b64).buffer})
        .catch(function(err){
          var c=err&&err.code;
          if(c==='rejected_extension'||c==='extension_not_enabled'){
            dl.save({filename:fn+'.txt',data:bytes(rec.b64).buffer}).catch(function(){});
            alert('نُزِّل باسم ‎.txt — غيّر الامتداد إلى الأصلي: '+fn);
          }else if(c!=='declined'){ alert('تعذّر التنزيل من الصفحة المنشورة.'); }
        });
      return;
    }
    var url=URL.createObjectURL(new Blob([bytes(rec.b64)],{type:rec.mime}));
    var a=document.createElement('a'); a.href=url; a.download=fn;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(function(){URL.revokeObjectURL(url);},4000);
  }
  document.addEventListener('click',function(e){
    var d=e.target.closest&&e.target.closest('.sdl');
    if(d){ e.preventDefault(); download(d.dataset.f); return; }
    var o=e.target.closest&&e.target.closest('#sOpen');
    if(o){
      e.preventDefault();
      var w=document.getElementById('sFrameWrap'), f=document.getElementById('sFrame');
      if(w.hidden){
        if(!f.getAttribute('srcdoc')){
          var rec=B['%s'];
          if(rec)f.setAttribute('srcdoc',new TextDecoder().decode(bytes(rec.b64)));
        }
        w.hidden=false; o.textContent='📕 أغلق الدراسة';
        f.scrollIntoView({block:'nearest',behavior:'smooth'});
      }else{ w.hidden=true; o.textContent='📖 افتح الدراسة هنا'; }
      return;
    }
  });
})();
</script>
""" % (json.dumps(blobs, ensure_ascii=False).replace("</", "<\\/"), STUDY[0])

#  اللوح يُدرَج داخل الصفحة الأولى بعد سجلّات الخطة
anchor = '<main class="wrap" id="pages">'
i = doc.index(anchor)
close = doc.rindex("</div>", 0, i)          # إغلاق #hub
doc = doc[:close] + PANE + doc[close:]

doc = doc.replace("</head>", CSS + "</head>", 1)
doc = doc.replace("</body>", JS + "</body>", 1)
open(OUT, "w", encoding="utf-8").write(doc)

print("تم · الحجم:", round(len(doc.encode()) / 1024), "KB ·", OUT)
print("  ملفات مضمَّنة:", len(blobs), "· أرشيف خام:", round(total / 1024 / 1024, 2), "م.ب")
