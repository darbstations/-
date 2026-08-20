# -*- coding: utf-8 -*-
"""المحور الرابع يصير محورًا مسجَّلًا مثل إخوته: «مسح السيارات».

كان المحور الرابع تحليلًا ساكنًا في صفحة الخطة (نقطة تعادل وافتراضات
تشغيل) بلا نموذج إدخال ولا سجل في الصفحة الأولى، بينما للمحاور الثلاثة
الأخرى نموذج وسجل. هذا السكربت يسدّ الفرق:

  • جدول «🚿 خدمات المسح المضافة» في صفحة الخطة لكل محطة + زر «＋ أضف خدمة مسح»
  • نموذج إدخال: الخدمة · صيغة التشغيل · الفترة · عدد العمال · السعر ·
    الطاقة اليومية · المسؤول · المستهدف — والإيراد اليومي يُحسب تلقائيًا
  • تبويب «🚿 مسح السيارات» في الصفحة الأولى يجمع خدمات المحطات الخمس،
    متزامنًا في الاتجاهين مثل بقية السجلّات

    python3 tools/add_wash_register.py [ملف-المصدر] [ملف-المخرَج]

‏— الكتلة تُحقَن وقت التشغيل لا في نصّ الصفحة: طبقة التحرير تستعيد محتوى
   كل منطقة من التخزين المحلي عند التحميل، فأي HTML يُكتب في الملف داخل
   منطقة محرَّرة سابقًا يُمحى عند أول فتح لدى من عدّل تلك الصفحة —
"""
import os, sys, re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = OUT = os.path.join(BASE, "darb-five-stations-analysis.html")
if len(sys.argv) > 1:
    SRC = sys.argv[1]
    OUT = sys.argv[2] if len(sys.argv) > 2 else SRC

doc = open(SRC, encoding="utf-8").read()
before = doc
assert "wash-js" not in doc, "سجل مسح السيارات مضاف سلفًا"


def patch(anchor, new, label):
    """استبدال موضع واحد لا غير — أي تعدّد يعني أن الأساس تغيّر."""
    global doc
    n = doc.count(anchor)
    assert n == 1, f"{label}: وجدت {n} مطابقة لا واحدة"
    doc = doc.replace(anchor, new, 1)


# ═══════════ 1. حقول النموذج داخل planform-js ═══════════
A = "'تحويل 10 عملاء لعقد أسطول']}\n    ]\n  };"
patch(A, """'تحويل 10 عملاء لعقد أسطول']}
    ],
    wash:[
      {k:'item',l:'الخدمة',t:'select',req:1,opts:['مسح خارجي سريع',
        'مسح زجاج فقط','غسيل خارجي','غسيل خارجي وداخلي','غسيل شامل وتلميع',
        'تنظيف جنوط','معطر وتلميع داخلي','غسيل بالبخار']},
      {k:'mode',l:'صيغة التشغيل',t:'select',req:1,opts:[
        'عمالة المحطة — مجانية ترويجية','عمالة المحطة — مدفوعة',
        'مشغّل متعاقد بنسبة إيراد','شريك خارجي بامتياز وإيجار شهري']},
      {k:'period',l:'الفترة',t:'select',req:1,src:'periods'},
      {k:'crew',l:'عدد العمال',t:'number'},
      {k:'price',l:'السعر (ر.س)',t:'number',step:'0.5'},
      {k:'cap',l:'الطاقة اليومية (غسلة)',t:'number',req:1},
      {k:'owner',l:'المسؤول',t:'text',list:['مشرف الغسيل','مدير المحطة',
        'مشرف الوردية الصباحية','مشرف الذروة','المشغّل المتعاقد']},
      {k:'kpi',l:'المستهدف',t:'text',wide:1,list:['تجاوز نقطة التعادل',
        '10 غسلات/يوم','32 غسلة/يوم','التقاط 4٪ من سيارات الفترة',
        'استرداد التجهيز خلال شهرين','رفع تكرار الزيارة']}
    ]
  };""", "حقول نموذج المسح")

patch("             dist:['توزيع داخل المحطة','التكلفة اليومية = الكمية × تكلفة الوحدة']};",
      "             dist:['توزيع داخل المحطة','التكلفة اليومية = الكمية × تكلفة الوحدة'],\n"
      "             wash:['خدمة مسح سيارات','الإيراد اليومي المتوقع = السعر × الطاقة اليومية']};",
      "عنوان نافذة المسح")

patch("""    if(kind==='part')return [v.name,v.type,v.dur,v.terms,v.goal,v.kpi,v.field,v.reach];
    var daily=NUM(v.qty)*NUM(v.cost);""",
      """    if(kind==='part')return [v.name,v.type,v.dur,v.terms,v.goal,v.kpi,v.field,v.reach];
    if(kind==='wash'){
      var rev=NUM(v.price)*NUM(v.cap);
      return [v.item,v.mode,v.period,v.crew?FMT(NUM(v.crew)):'',
              v.price?String(v.price):'',v.cap?FMT(NUM(v.cap)):'',
              rev?FMT(rev):'',v.owner,v.kpi];
    }
    var daily=NUM(v.qty)*NUM(v.cost);""",
      "خلايا صف المسح")

patch("    var m2={item:0,period:1,qty:2,dur:3,cost:4,owner:6,kpi:7};",
      "    if(kind==='wash'){\n"
      "      var m3={item:0,mode:1,period:2,crew:3,price:4,cap:5,owner:7,kpi:8};\n"
      "      return old[m3[f.k]]||'';}\n"
      "    var m2={item:0,period:1,qty:2,dur:3,cost:4,owner:6,kpi:7};",
      "قراءة صف المسح للتعديل")

patch("""      }else{
        var dsum=0; rows.forEach(function(r){dsum+=NUM(r.cells[5]?r.cells[5].textContent:0);});
        txt='<b>'+rows.length+'</b> صنف · التكلفة اليومية <b>'+FMT(dsum)+'</b> ر.س'
            +' · الشهرية <b>'+FMT(dsum*30)+'</b> ر.س';
      }""",
      """      }else if(kind==='wash'){
        var cap=0,rev=0;
        rows.forEach(function(r){
          cap+=NUM(r.cells[5]?r.cells[5].textContent:0);
          rev+=NUM(r.cells[6]?r.cells[6].textContent:0);});
        txt='<b>'+rows.length+'</b> خدمة · الطاقة اليومية <b>'+FMT(cap)+'</b> غسلة'
            +' · الإيراد اليومي المتوقع <b>'+FMT(rev)+'</b> ر.س'
            +' · الشهري <b>'+FMT(rev*30)+'</b> ر.س';
      }else{
        var dsum=0; rows.forEach(function(r){dsum+=NUM(r.cells[5]?r.cells[5].textContent:0);});
        txt='<b>'+rows.length+'</b> صنف · التكلفة اليومية <b>'+FMT(dsum)+'</b> ر.س'
            +' · الشهرية <b>'+FMT(dsum*30)+'</b> ر.س';
      }""",
      "ملخّص جدول المسح")

# ═══════════ 2. السجل في الصفحة الأولى داخل hubreg-js ═══════════
patch("      empty:'لا توجد توزيعات مسجَّلة بعد'}\n  };",
      """      empty:'لا توجد توزيعات مسجَّلة بعد'},
    wash:{tab:'🚿 مسح السيارات', title:'سجل خدمات مسح السيارات', add:'＋ أضف خدمة مسح',
      sub:'صيغ تشغيل خدمة المسح في المحطات، وطاقتها اليومية وإيرادها المتوقع',
      cols:['الخدمة','صيغة التشغيل','الفترة','عدد العمال','السعر (ر.س)',
            'الطاقة اليومية (غسلة)','الإيراد اليومي المتوقع (ر.س)','المسؤول','المستهدف'],
      empty:'لا توجد خدمات مسح مسجَّلة بعد'}
  };""", "سجل المسح في الصفحة الأولى")

patch("""    var s=d.reduce(function(a,r){return a+NUM(r.cells[5]);},0);""",
      """    if(kind==='wash'){
      var cap=d.reduce(function(a,r){return a+NUM(r.cells[5]);},0);
      var rev=d.reduce(function(a,r){return a+NUM(r.cells[6]);},0);
      return '<b>'+d.length+'</b> خدمة · الطاقة اليومية <b>'+FMT(cap)+'</b> غسلة · '
        +'الإيراد اليومي المتوقع <b>'+FMT(rev)+'</b> ر.س · الشهري <b>'+FMT(rev*30)
        +'</b> ر.س · '+spread;
    }
    var s=d.reduce(function(a,r){return a+NUM(r.cells[5]);},0);""",
      "ملخّص سجل المسح")

# ═══════════ 3. حقن الكتلة في صفحات الخطة وقت التشغيل ═══════════
COLS = ["الخدمة", "صيغة التشغيل", "الفترة", "عدد العمال", "السعر (ر.س)",
        "الطاقة اليومية (غسلة)", "الإيراد اليومي المتوقع (ر.س)", "المسؤول", "المستهدف"]
TH = "".join(f"<th>{c}</th>" for c in COLS)
BLOCK = (
    '<div class="sec-h" style="margin-top:6px"><h2 style="font-size:15px">'
    "🚿 خدمات المسح المضافة</h2><span>صيغة التشغيل والسعر والطاقة اليومية — "
    "والإيراد اليومي المتوقع يُحسب تلقائيًا</span></div>"
    '<div class="planbar" data-kind="wash">'
    '<button type="button" class="planadd" data-kind="wash">＋ أضف خدمة مسح</button>'
    '<span class="plansum" data-sum="wash"></span></div>'
    '<div class="ntable plantbl" data-plan="wash"><div class="tscroll"><table>'
    f"<thead><tr>{TH}</tr></thead>"
    f'<tbody><tr class="planempty"><td colspan="{len(COLS)}">'
    "لم تُضف خدمة مسح بعد — اضغط «＋ أضف خدمة مسح» أعلاه</td></tr></tbody>"
    "</table></div></div>")

JS = """
<script id="wash-js">
/* ═══ المحور الرابع: كتلة إدخال خدمات مسح السيارات في كل صفحة خطة ═══
   تُحقن وقت التشغيل بعد أن تستعيد طبقة التحرير المحتوى المحفوظ محليًا،
   وإلا مُحيت لدى من سبق أن عدّل صفحة الخطة. الدالة عديمة الأثر عند
   إعادة النداء: تتخطّى أي صفحة فيها الجدول أصلًا.                    */
(function(){
  var HTML=%s;
  function inject(){
    var made=0;
    document.querySelectorAll('.pgview[id$="-plan"]').forEach(function(pv){
      if(pv.querySelector('.plantbl[data-plan="wash"]'))return;
      var anchor=null;
      pv.querySelectorAll('.sec-h').forEach(function(s){
        if(!anchor&&s.textContent.indexOf('لوحة المتابعة')>=0)anchor=s;
      });
      var frag=document.createElement('div'); frag.innerHTML=HTML;
      var nodes=[].slice.call(frag.childNodes);
      if(anchor&&anchor.parentNode){
        nodes.forEach(function(n){anchor.parentNode.insertBefore(n,anchor);});
      }else{
        var host=pv.querySelector('[data-ez]')||pv;
        nodes.forEach(function(n){host.appendChild(n);});
      }
      made++;
    });
    return made;
  }
  var n=inject();
  if(n){
    /* الحقن غيّر بنية المناطق: أعِد ضبط لقطة التراجع حتى لا يُقرأ كتعديل */
    if(window.DARB&&DARB.rebase)DARB.rebase();
    if(window.DARB&&DARB.planSync)DARB.planSync();
  }
  window.addEventListener('hashchange',function(){setTimeout(inject,0);});
})();
</script>
"""

import json
JS = JS % json.dumps(BLOCK, ensure_ascii=False).replace("</", "<\\/")

i = doc.index('<script id="hubreg-js">')
doc = doc[:i] + JS.strip() + "\n" + doc[i:]

open(OUT, "w", encoding="utf-8").write(doc)

# ═══════════ تقرير الفرق ═══════════
bl, al = before.splitlines(), doc.splitlines()
print("تم ·", round(len(doc.encode()) / 1024), "KB ·", OUT)
print(f"الأسطر: {len(bl)} ← {len(al)}")
print("عدد صفحات الخطة:", len(re.findall(r'id="pg-\w+-plan"', doc)))
for k in ("camp", "part", "dist", "wash"):
    print(f"  KINDS.{k}:", doc.count(f"    {k}:{{tab:") or doc.count(f"{k}:{{tab:"))
