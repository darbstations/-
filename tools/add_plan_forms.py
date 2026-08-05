# -*- coding: utf-8 -*-
"""يحوّل صفحة الخطة التشغيلية إلى صفحة تفاعلية: نماذج إدخال لكل محور.

ثلاثة نماذج:
  • حملة تشجيع مبيعات — الفترة · المدة · الشركاء الداخليون · الشروط ·
    المواد المطلوبة · الميزانية · المستهدف الرقمي · المستهدف الميداني
  • شراكة — نوع الشريك (داخلي/خارجي) · اسم الشريك · المدة · الشروط ·
    مستهدفات الشراكة · مستهدف رقمي · مستهدف ميداني · مستهدف وصول
  • توزيع — الصنف · الفترة · الكمية اليومية · المدة · تكلفة الوحدة ·
    المسؤول · المستهدف

كل حقل قائمة اختيار جاهزة + خيار «أخرى…» للكتابة الحرّة. قوائم الفترات
وأسماء الشركاء الداخليين والخارجيين مأخوذة من بيانات المحطة نفسها.
الصفوف المضافة محتوى حقيقي داخل منطقة التحرير: تُحفظ محليًا، وتدخل مكدّس
التراجع، وتخرج مع «تنزيل نسخة HTML».
"""
import re, json, html, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = OUT = os.path.join(BASE, "darb-five-stations-analysis.html")
KEEP = ["MK007", "MK017", "MK002", "MK023", "MK019"]

E = lambda t: html.escape(str(t), quote=True)
doc = open(SRC, encoding="utf-8").read()

# ═══════════ 1. خيارات كل محطة من بياناتها ═══════════
OPTS = {}
for c in KEEP:
    pg = re.search(r'id="pg-%s-partners".*?(?=<div class="pgview"|</main>)' % c, doc, re.S).group(0)
    xt = re.search(r'id="pg-%s-external".*?(?=<div class="pgview"|</main>)' % c, doc, re.S).group(0)
    periods = ["اليوم كامل"] + [
        f"{a.strip()} · {b}" for a, b in
        re.findall(r'<td><b>([^<]+)</b></td><td>(\d\d:\d\d – \d\d:\d\d)</td>', pg)][:7]
    periods = list(dict.fromkeys(periods))
    units = list(dict.fromkeys(
        html.unescape(x).strip() for x in re.findall(r'<span class="ptag">([^<]+)</span>', pg)))
    ext = []
    for m in re.finditer(r'<div class="sec-h"[^>]*><h2>\S+ ([^<]+)</h2><span>\d+ منشأة', xt):
        cat = m.group(1).strip()
        after = xt.split(m.group(0), 1)[1].split("</table>", 1)[0]
        ext += [f"{html.unescape(n).strip()} — {cat}"
                for n in re.findall(r"<tr><td><b>([^<]+)</b></td>", after)]
    OPTS[c] = {"periods": periods, "units": units, "external": ext}
    assert len(periods) == 7 and units, (c, len(periods))

# ═══════════ 2. الكتل المدرَجة في الصفحة ═══════════
COLS = {
    "camp": ["الحملة", "الفترة", "مدة الحملة", "الشركاء الداخليون", "شروط الحملة",
             "المواد المطلوبة", "الميزانية (ر.س)", "المستهدف الرقمي", "المستهدف الميداني"],
    "part": ["الشريك", "نوع الشريك", "مدة الشراكة", "شروط الشراكة", "مستهدفات الشراكة",
             "مستهدف رقمي", "مستهدف ميداني", "مستهدف وصول"],
    "dist": ["الصنف", "الفترة", "الكمية اليومية", "مدة التوزيع", "تكلفة الوحدة (ر.س)",
             "التكلفة اليومية (ر.س)", "المسؤول", "المستهدف"],
}
HEAD = {
    "camp": ("📣 حملاتك المضافة", "أضف حملتك بنموذج جاهز — كل حقل قائمة اختيار أو كتابة حرّة",
             "＋ أضف حملة", "لم تُضف حملة بعد — اضغط «＋ أضف حملة» أعلاه"),
    "part": ("🤝 شراكاتك المضافة", "شريك داخلي من وحدات المحطة أو خارجي من المنشآت المرصودة",
             "＋ أضف شراكة", "لم تُضف شراكة بعد — اضغط «＋ أضف شراكة» أعلاه"),
    "dist": ("🎁 توزيعاتك المضافة", "الصنف والفترة والكمية — والتكلفة اليومية تُحسب تلقائيًا",
             "＋ أضف توزيعًا", "لم يُضف توزيع بعد — اضغط «＋ أضف توزيعًا» أعلاه"),
}


def block(kind):
    ttl, sub, btn, empty = HEAD[kind]
    cols = COLS[kind]
    th = "".join(f"<th>{c}</th>" for c in cols)
    return (
        f'<div class="sec-h" style="margin-top:6px"><h2 style="font-size:15px">{ttl}</h2>'
        f"<span>{sub}</span></div>"
        f'<div class="planbar" data-kind="{kind}">'
        f'<button type="button" class="planadd" data-kind="{kind}">{btn}</button>'
        f'<span class="plansum" data-sum="{kind}"></span></div>'
        f'<div class="ntable plantbl" data-plan="{kind}"><div class="tscroll"><table>'
        f"<thead><tr>{th}</tr></thead>"
        f'<tbody><tr class="planempty"><td colspan="{len(cols)}">{empty}</td></tr></tbody>'
        "</table></div></div>")


for kind in ("camp", "part", "dist"):
    n = doc.count(f"<!--SLOT:{kind}-->")
    assert n == 5, (kind, n)
    doc = doc.replace(f"<!--SLOT:{kind}-->", block(kind))

# قائمة الخيارات لكل محطة
doc = doc.replace(
    "</body>",
    '<script type="application/json" id="plan-opts">'
    + json.dumps(OPTS, ensure_ascii=False).replace("</", "<\\/") + "</script></body>", 1)

# ═══════════ 3. الجزر المقفلة: شريط الإضافة لا يُكتب فوقه ═══════════
doc = doc.replace("var LOCK='.pgnav, .tabs, .cmpbar, .dimchips, #cmpOut';",
                  "var LOCK='.pgnav, .tabs, .cmpbar, .dimchips, #cmpOut, .planbar';", 1)
doc = doc.replace("var LOCK='.pgnav,.tabs,.cmpbar,.dimchips,#cmpOut,#edbar,#bdbar,script,style';",
                  "var LOCK='.pgnav,.tabs,.cmpbar,.dimchips,#cmpOut,#edbar,#bdbar,"
                  ".planbar,script,style';", 1)

CSS = """
<style id="planform-css">
/* ── شريط الإضافة ── */
.planbar{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin:0 0 10px}
.planbar .planadd{font-family:inherit;font-size:13px;font-weight:700;cursor:pointer;
  background:var(--orange);color:#fff;border:1px solid var(--orange);border-radius:10px;
  padding:8px 15px;transition:.14s;box-shadow:0 2px 10px rgba(246,133,31,.22)}
.planbar .planadd:hover{filter:brightness(1.06);transform:translateY(-1px)}
.plansum{font-size:12px;color:var(--ink3)}
.plansum b{color:var(--ink2)}
.plantbl td{white-space:normal;line-height:1.75;vertical-align:top}
.plantbl td:first-child{min-width:150px;position:relative}
.plantbl .planempty td{text-align:center;color:var(--ink3);font-size:12.5px;padding:16px 10px}
.planx,.planedit{display:inline-block;width:17px;height:17px;border-radius:50%;font-size:11px;
  font-weight:800;line-height:15px;text-align:center;cursor:pointer;opacity:0;transition:.12s;
  user-select:none;-webkit-user-select:none;vertical-align:middle;margin-inline-end:3px}
.planx{background:#FBF0ED;border:1px solid #E3BEB4;color:#A6432E}
.planedit{background:#F1EFEB;border:1px solid #DDD8CF;color:#6E6A64}
.plantbl tr:hover .planx,.plantbl tr:hover .planedit{opacity:1}
.planx:hover{background:#C0503A;color:#fff;border-color:#C0503A}
.planedit:hover{background:#55565A;color:#fff;border-color:#55565A}
.plantbl .bdrowx{display:none}   /* جداول الخطة لها ×/✎ الخاصان بها في كل الأوضاع */
/* ── النافذة ── */
#planmodal{position:fixed;inset:0;z-index:400;display:flex;align-items:flex-start;
  justify-content:center;background:rgba(45,45,45,.44);padding:26px 16px;overflow:auto}
#planmodal .pmbox{background:var(--card);border-radius:18px;width:min(880px,100%);
  box-shadow:0 18px 60px rgba(45,45,45,.32);overflow:hidden;font-family:inherit;
  max-height:calc(100vh - 52px);display:flex;flex-direction:column}
#planmodal .pmh,#planmodal .pmf{flex:0 0 auto}
#planmodal .pmh{display:flex;align-items:center;justify-content:space-between;gap:12px;
  background:var(--bgray);color:#fff;padding:13px 18px}
#planmodal .pmh h3{font-size:15.5px;font-weight:700;margin:0}
#planmodal .pmh span{font-size:11.5px;opacity:.75;font-weight:400}
#planmodal .pmx{background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.24);
  color:#fff;border-radius:9px;width:28px;height:28px;font-size:15px;cursor:pointer;line-height:1}
#planmodal .pmb{padding:16px 18px;display:grid;grid-template-columns:1fr 1fr;gap:13px 16px;
  overflow:auto;flex:1 1 auto}
#planmodal .pf.wide{grid-column:1/-1}
#planmodal label{display:block;font-size:12px;font-weight:700;color:var(--ink2);margin-bottom:5px}
#planmodal input,#planmodal select,#planmodal textarea{width:100%;font-family:inherit;font-size:13px;
  color:var(--ink);background:#FDFCFA;border:1px solid var(--line2);border-radius:10px;
  padding:8px 10px;outline:none;transition:.12s}
#planmodal input:focus,#planmodal select:focus,#planmodal textarea:focus{border-color:var(--orange);
  background:#fff;box-shadow:0 0 0 3px rgba(246,133,31,.13)}
#planmodal textarea{min-height:62px;resize:vertical;line-height:1.7}
#planmodal .pmulti{border:1px solid var(--line2);border-radius:10px;background:#FDFCFA;padding:7px 9px;
  max-height:132px;overflow:auto;display:flex;flex-wrap:wrap;gap:5px}
#planmodal .pmulti label{display:inline-flex;align-items:center;gap:5px;font-size:12px;font-weight:500;
  color:var(--ink2);background:#fff;border:1px solid var(--line);border-radius:8px;
  padding:4px 9px;margin:0;cursor:pointer;transition:.12s}
#planmodal .pmulti label:hover{border-color:var(--orange)}
#planmodal .pmulti input{width:auto;padding:0;margin:0;accent-color:var(--orange)}
#planmodal .pmulti label.on{background:#FDEEE2;border-color:#F5CBA8;color:#B4500F;font-weight:700}
#planmodal .pfilter{margin-bottom:6px}
#planmodal .pother{margin-top:6px}
#planmodal .pmf{display:flex;align-items:center;justify-content:space-between;gap:12px;
  border-top:1px solid var(--line);padding:12px 18px;background:#FDFCFA}
#planmodal .pmf .hint{font-size:11.5px;color:var(--ink3)}
#planmodal .pmf .go{background:var(--orange);border:1px solid var(--orange);color:#fff;font-weight:700;
  font-size:13.5px;border-radius:10px;padding:9px 22px;cursor:pointer;font-family:inherit}
#planmodal .pmf .cancel{background:#fff;border:1px solid var(--line2);color:var(--ink2);
  font-size:13px;border-radius:10px;padding:9px 16px;cursor:pointer;font-family:inherit;
  margin-inline-end:8px}
#planmodal .req{color:#C0503A}
@media (max-width:760px){#planmodal .pmb{grid-template-columns:1fr}}
</style>
"""

JS = r"""
<script id="planform-js">
/* ═══ نماذج إدخال الخطة التشغيلية ═══
   الصفوف المضافة محتوى حقيقي داخل منطقة التحرير: تُحفظ محليًا وتدخل مكدّس
   التراجع وتخرج مع النسخة المنزَّلة. النموذج نفسه لا يُحفظ (data-builder).  */
(function(){
  var OPTS={};
  try{ OPTS=JSON.parse(document.getElementById('plan-opts').textContent); }catch(e){}

  var DUR=['أسبوع واحد','أسبوعان','ثلاثة أسابيع','شهر كامل','شهران','موسم (٣ أشهر)','مستمر'];
  var PDUR=['شهر واحد','ثلاثة أشهر','ستة أشهر','سنة كاملة','موسم الحج','موسم رمضان','مفتوحة'];
  var F={
    camp:[
      {k:'name',l:'اسم الحملة',t:'text',req:1,list:['امتلئ واربح','صباح درب','ذروة العصر',
        'أسطولك علينا','عرض نهاية الأسبوع','حملة الديزل','عرض العائلة','حملة الولاء']},
      {k:'period',l:'الفترة',t:'select',req:1,src:'periods'},
      {k:'dur',l:'مدة الحملة',t:'select',req:1,opts:DUR},
      {k:'units',l:'الشركاء الداخليون',t:'multi',src:'units',wide:1},
      {k:'terms',l:'شروط الحملة',t:'multi',wide:1,opts:['تعبئة ≥ 40 لترًا','تعبئة ≥ 50 لترًا',
        'تعبئة ≥ 60 لترًا','بنزين 95 فقط','بنزين 91 فقط','ديزل فقط','للعملاء الجدد فقط',
        'عبر بطاقة الولاء','نهاية الأسبوع فقط','ضمن الفترة المحددة فقط','مرة واحدة لكل مركبة',
        'للأساطيل المتعاقدة']},
      {k:'mats',l:'المواد المطلوبة',t:'multi',wide:1,opts:['لوحات إعلانية','ستاندات',
        'قسائم مطبوعة','مناديل','فواحات','مياه باردة','قهوة وتمر','تمر','هدايا أطفال',
        'بطاقات سائق','منشورات تعريفية','طاقم إضافي','مكبر صوت','مظلة','خيمة استقبال']},
      {k:'budget',l:'الميزانية (ر.س)',t:'number'},
      {k:'kpi',l:'المستهدف الرقمي',t:'text',list:['+4٪ لترات الأسبوع','+8٪ على الفترة',
        '500 قسيمة مفعّلة','+10٪ متوسط التعبئة','200 عميل جديد','3 عقود أساطيل']},
      {k:'field',l:'المستهدف الميداني',t:'text',list:['تغطية 3 ورديات يوميًا',
        'مندوب في الذروة','زيارة 10 منشآت','لافتة على كل مضخة','استبيان رضا يومي']}
    ],
    part:[
      {k:'type',l:'نوع الشريك',t:'select',req:1,opts:['داخلي','خارجي'],noOther:1},
      {k:'name',l:'اسم الشريك',t:'select',req:1,src:'byType'},
      {k:'dur',l:'مدة الشراكة',t:'select',req:1,opts:PDUR},
      {k:'terms',l:'شروط الشراكة',t:'multi',wide:1,opts:['فاتورة شهرية موحّدة',
        'خصم كمية تصاعدي','بطاقة سائق مسبقة الدفع','حد ائتماني شهري','أولوية مضخة',
        'تقرير استهلاك لكل مركبة','إحالة متبادلة','عرض مشترك داخل المحطة',
        'لافتة تعريفية في موقع الشريك','مراجعة ربع سنوية']},
      {k:'goal',l:'مستهدفات الشراكة',t:'text',list:['تحويل الأسطول بالكامل للمحطة',
        'زيادة تكرار الزيارة','رفع متوسط التعبئة','فتح قناة إحالة']},
      {k:'kpi',l:'مستهدف رقمي',t:'text',list:['4,050 لتر/شهر','2,250 لتر/شهر',
        '2,880 لتر/شهر','+15٪ على الحجم المتعاقد','20 مركبة مسجَّلة']},
      {k:'field',l:'مستهدف ميداني',t:'text',list:['زيارتان شهريًا للشريك',
        'تدريب سائقي الشريك','كشك تسجيل داخل موقع الشريك']},
      {k:'reach',l:'مستهدف وصول',t:'text',list:['50 سائقًا','100 موظف','200 عميل للشريك',
        '4 حافلات','15 مركبة أسطول']}
    ],
    dist:[
      {k:'item',l:'الصنف',t:'select',req:1,opts:['مناديل','فواحات',
        'مسح سيارات من قبل العمال','مياه باردة','قهوة وتمر','تمر','عصائر',
        'قسائم وحدات المحطة','ألعاب وبالونات للأطفال','معطر سيارة','منشفة زجاج',
        'بطاقة «أسطولك علينا»','منشور تعريفي','بطاقة ولاء']},
      {k:'period',l:'الفترة',t:'select',req:1,src:'periods'},
      {k:'qty',l:'الكمية اليومية',t:'number',req:1},
      {k:'dur',l:'مدة التوزيع',t:'select',req:1,opts:DUR},
      {k:'cost',l:'تكلفة الوحدة (ر.س)',t:'number',step:'0.5'},
      {k:'owner',l:'المسؤول',t:'text',list:['مدير المحطة','مشرف الوردية الصباحية',
        'مشرف الذروة','مسؤول تطوير الأعمال','فريق خدمة العملاء','الوحدة الشريكة']},
      {k:'kpi',l:'المستهدف',t:'text',wide:1,list:['تغطية 50٪ من سيارات الفترة',
        'رفع سيارات الفترة 8٪','200 تفاعل يوميًا','تحويل 10 عملاء لعقد أسطول']}
    ]
  };
  var TITLE={camp:['حملة تشجيع مبيعات','املأ ما يلزمك واترك الباقي فارغًا'],
             part:['شراكة جديدة','داخلية من وحدات المحطة أو خارجية من المنشآت المرصودة'],
             dist:['توزيع داخل المحطة','التكلفة اليومية = الكمية × تكلفة الوحدة']};
  var NUM=function(v){var n=parseFloat(String(v).replace(/[^\d.\-]/g,''));return isNaN(n)?0:n;};
  var FMT=function(n){return Math.round(n).toLocaleString('en-US');};
  var ESC=function(s){var d=document.createElement('div');d.textContent=s==null?'':s;return d.innerHTML;};

  function codeOf(el){
    var pv=el.closest('.pgview'); var m=pv&&/^pg-([A-Za-z]{2}\d+)/.exec(pv.id);
    return m?m[1]:null;
  }
  function optsFor(code,f,form){
    if(f.opts)return f.opts.slice();
    var o=OPTS[code]||{};
    if(f.src==='periods')return (o.periods||[]).slice();
    if(f.src==='units')return (o.units||[]).slice();
    if(f.src==='byType'){
      var t=form?form.querySelector('[name="type"]'):null;
      var v=t?t.value:'داخلي';
      return (v==='خارجي'?(o.external||[]):(o.units||[])).slice();
    }
    return [];
  }

  /* ── بناء النموذج ── */
  function field(code,f,form,val){
    var w=document.createElement('div');
    w.className='pf'+(f.wide?' wide':'');
    var id='pf_'+f.k;
    w.innerHTML='<label for="'+id+'">'+ESC(f.l)+(f.req?' <span class="req">*</span>':'')+'</label>';
    if(f.t==='multi'){
      var opts=optsFor(code,f,form), chosen=(val||'').split('، ').filter(Boolean);
      var box=document.createElement('div'); box.className='pmulti'; box.dataset.name=f.k;
      if(opts.length>12){
        var fi=document.createElement('input');
        fi.type='search'; fi.className='pfilter'; fi.placeholder='تصفية القائمة…';
        fi.addEventListener('input',function(){
          var q=fi.value.trim();
          box.querySelectorAll('label').forEach(function(l){
            l.style.display=(!q||l.textContent.indexOf(q)>=0)?'':'none';});
        });
        w.appendChild(fi);
      }
      opts.forEach(function(o){
        var l=document.createElement('label');
        var cb=document.createElement('input'); cb.type='checkbox'; cb.value=o;
        if(chosen.indexOf(o)>=0){cb.checked=true;l.classList.add('on');}
        cb.addEventListener('change',function(){l.classList.toggle('on',cb.checked);});
        l.appendChild(cb); l.appendChild(document.createTextNode(o));
        box.appendChild(l);
      });
      w.appendChild(box);
      var ot=document.createElement('input');
      ot.type='text'; ot.className='pother'; ot.dataset.other=f.k;
      ot.placeholder='أضف بندًا غير موجود في القائمة — افصل بفاصلة';
      var extra=chosen.filter(function(x){return opts.indexOf(x)<0;});
      if(extra.length)ot.value=extra.join('، ');
      w.appendChild(ot);
      return w;
    }
    if(f.t==='select'){
      var s=document.createElement('select'); s.id=id; s.name=f.k;
      var list=optsFor(code,f,form);
      s.innerHTML='<option value="">— اختر —</option>'
        +list.map(function(o){return '<option>'+ESC(o)+'</option>';}).join('')
        +(f.noOther?'':'<option value="__other">أخرى…</option>');
      if(val){ if(list.indexOf(val)>=0)s.value=val; else if(!f.noOther)s.value='__other'; }
      w.appendChild(s);
      var ot2=document.createElement('input');
      ot2.type='text'; ot2.className='pother'; ot2.dataset.other=f.k;
      ot2.placeholder='اكتب البديل…';
      ot2.style.display=(s.value==='__other')?'':'none';
      if(s.value==='__other')ot2.value=val||'';
      s.addEventListener('change',function(){
        ot2.style.display=(s.value==='__other')?'':'none';
        if(s.value==='__other')ot2.focus();
        if(f.k==='type'){                       /* اسم الشريك يتبع نوعه */
          var host=form.querySelector('[name="name"]');
          if(host){
            var keep=host.value;
            var l2=optsFor(code,{src:'byType'},form);
            host.innerHTML='<option value="">— اختر —</option>'
              +l2.map(function(o){return '<option>'+ESC(o)+'</option>';}).join('')
              +'<option value="__other">أخرى…</option>';
            if(l2.indexOf(keep)>=0)host.value=keep;
          }
        }
      });
      w.appendChild(ot2);
      return w;
    }
    var inp=document.createElement(f.t==='area'?'textarea':'input');
    inp.id=id; inp.name=f.k;
    if(f.t==='number'){inp.type='number';inp.min='0';if(f.step)inp.step=f.step;}
    else inp.type='text';
    if(val)inp.value=val;
    if(f.list){
      var dl=document.createElement('datalist'); dl.id=id+'_dl';
      dl.innerHTML=f.list.map(function(o){return '<option value="'+ESC(o)+'">';}).join('');
      inp.setAttribute('list',dl.id); w.appendChild(dl);
    }
    w.appendChild(inp);
    return w;
  }

  function readForm(kind,form){
    var out={};
    F[kind].forEach(function(f){
      if(f.t==='multi'){
        var box=form.querySelector('.pmulti[data-name="'+f.k+'"]');
        var v=[].slice.call(box.querySelectorAll('input:checked')).map(function(c){return c.value;});
        var ot=form.querySelector('[data-other="'+f.k+'"]');
        if(ot&&ot.value.trim())v=v.concat(ot.value.split(/[،,]/).map(function(x){return x.trim();})
                                          .filter(Boolean));
        out[f.k]=v.join('، ');
      }else{
        var el=form.querySelector('[name="'+f.k+'"]');
        var v2=el?el.value.trim():'';
        if(v2==='__other'){
          var o2=form.querySelector('[data-other="'+f.k+'"]');
          v2=o2?o2.value.trim():'';
        }
        out[f.k]=v2;
      }
    });
    return out;
  }

  function cells(kind,v){
    if(kind==='camp')return [v.name,v.period,v.dur,v.units,v.terms,v.mats,
      v.budget?FMT(NUM(v.budget)):'',v.kpi,v.field];
    if(kind==='part')return [v.name,v.type,v.dur,v.terms,v.goal,v.kpi,v.field,v.reach];
    var daily=NUM(v.qty)*NUM(v.cost);
    return [v.item,v.period,v.qty?FMT(NUM(v.qty)):'',v.dur,
            v.cost?String(v.cost):'',daily?FMT(daily):'',v.owner,v.kpi];
  }

  function rowHTML(kind,v){
    var c=cells(kind,v);
    return '<tr class="planrow bdnew">'+c.map(function(x,i){
      var t=(x==null||x==='')?'—':String(x);
      return '<td>'+(i===0?'<b>'+ESC(t)+'</b>':ESC(t))+'</td>';
    }).join('')+'</tr>';
  }

  /* ── النافذة ── */
  var modal=null, ctx=null;
  function close(){ if(modal){modal.remove();modal=null;ctx=null;} }
  function open(kind,host,row){
    close();
    var code=codeOf(host);
    modal=document.createElement('div');
    modal.id='planmodal'; modal.setAttribute('data-builder',''); modal.contentEditable='false';
    modal.innerHTML='<div class="pmbox"><div class="pmh"><div><h3>'
      +(row?'تعديل ':'إضافة ')+ESC(TITLE[kind][0])+'</h3><span>'+ESC(TITLE[kind][1])+'</span></div>'
      +'<button type="button" class="pmx" title="إغلاق">✕</button></div>'
      +'<form class="pmb"></form>'
      +'<div class="pmf"><span class="hint">الحقول المعلَّمة <span class="req">*</span> مطلوبة · '
      +'كل قائمة فيها «أخرى…» للكتابة الحرّة</span><div>'
      +'<button type="button" class="cancel">إلغاء</button>'
      +'<button type="button" class="go">'+(row?'حفظ التعديل':'إضافة إلى الجدول')+'</button>'
      +'</div></div></div>';
    var form=modal.querySelector('.pmb');
    var old=row?[].slice.call(row.cells).map(function(td){
      var t=td.textContent.replace(/[×✎]/g,'').trim(); return t==='—'?'':t;}):null;
    var oldv={};
    if(old)F[kind].forEach(function(f,i){oldv[f.k]=cellToVal(kind,f,old,i);});
    F[kind].forEach(function(f){ form.appendChild(field(code,f,form,old?oldv[f.k]:'')); });
    document.body.appendChild(modal);
    ctx={kind:kind,host:host,row:row};
    modal.querySelector('.pmx').addEventListener('click',close);
    modal.querySelector('.cancel').addEventListener('click',close);
    modal.querySelector('.go').addEventListener('click',submit);
    modal.addEventListener('click',function(e){if(e.target===modal)close();});
    var first=form.querySelector('input,select,textarea'); if(first)first.focus();
  }
  /* ترتيب الحقول يطابق ترتيب الأعمدة عدا الأعمدة المحسوبة */
  function cellToVal(kind,f,old,i){
    if(kind==='camp')return old[i]||'';
    if(kind==='part'){var map={name:0,type:1,dur:2,terms:3,goal:4,kpi:5,field:6,reach:7};
      return old[map[f.k]]||'';}
    var m2={item:0,period:1,qty:2,dur:3,cost:4,owner:6,kpi:7};
    return old[m2[f.k]]||'';
  }

  function submit(){
    if(!ctx)return;
    var kind=ctx.kind, form=modal.querySelector('.pmb');
    var v=readForm(kind,form);
    var miss=F[kind].filter(function(f){return f.req&&!v[f.k];});
    if(miss.length){ alert('أكمل الحقول المطلوبة:\n• '+miss.map(function(f){return f.l;}).join('\n• ')); return; }
    var tb=ctx.host.querySelector('tbody');
    var tmp=document.createElement('tbody'); tmp.innerHTML=rowHTML(kind,v);
    var tr=tmp.firstChild;
    if(ctx.row){ ctx.row.replaceWith(tr); }
    else{ var e=tb.querySelector('.planempty'); if(e)e.remove(); tb.appendChild(tr); }
    var z=ctx.host.closest('[data-ez]');
    if(z)z.dispatchEvent(new Event('input',{bubbles:true}));
    close(); chrome(); sums();
    tr.scrollIntoView({block:'nearest',behavior:'smooth'});
  }

  /* ── أزرار الصفوف والملخصات ── */
  /* ‏— يجب أن تبقى هذه الدالة عديمة الأثر عند إعادة النداء، وإلا دخل
       مراقب التغييرات في حلقة لا تنتهي — */
  function chrome(){
    document.querySelectorAll('.plantbl tbody tr').forEach(function(tr){
      if(tr.classList.contains('planempty')){
        tr.querySelectorAll('.planx,.planedit').forEach(function(n){n.remove();});
        return;
      }
      var td=tr.cells[0]; if(!td||td.querySelector('.planx'))return;
      var x=document.createElement('span');
      x.className='planx'; x.setAttribute('data-builder',''); x.contentEditable='false';
      x.title='حذف هذا الصف'; x.textContent='×';
      var e=document.createElement('span');
      e.className='planedit'; e.setAttribute('data-builder',''); e.contentEditable='false';
      e.title='تعديل بالنموذج'; e.textContent='✎';
      td.insertBefore(e,td.firstChild); td.insertBefore(x,td.firstChild);
    });
  }
  function sums(){
    document.querySelectorAll('.plantbl').forEach(function(t){
      var kind=t.dataset.plan;
      var rows=[].slice.call(t.querySelectorAll('tbody tr')).filter(function(r){
        return !r.classList.contains('planempty');});
      var bar=t.previousElementSibling;
      var out=bar&&bar.querySelector('.plansum[data-sum="'+kind+'"]');
      if(!out)return;
      if(!rows.length){ out.innerHTML=''; return; }
      var txt='';
      if(kind==='camp'){
        var b=0; rows.forEach(function(r){b+=NUM(r.cells[6]?r.cells[6].textContent:0);});
        txt='<b>'+rows.length+'</b> حملة · إجمالي الميزانية <b>'+FMT(b)+'</b> ر.س';
      }else if(kind==='part'){
        var i=0,x=0;
        rows.forEach(function(r){
          var t2=r.cells[1]?r.cells[1].textContent.trim():'';
          if(t2==='خارجي')x++; else if(t2==='داخلي')i++;});
        txt='<b>'+rows.length+'</b> شراكة · داخلي <b>'+i+'</b> · خارجي <b>'+x+'</b>';
      }else{
        var dsum=0; rows.forEach(function(r){dsum+=NUM(r.cells[5]?r.cells[5].textContent:0);});
        txt='<b>'+rows.length+'</b> صنف · التكلفة اليومية <b>'+FMT(dsum)+'</b> ر.س'
            +' · الشهرية <b>'+FMT(dsum*30)+'</b> ر.س';
      }
      out.innerHTML=txt;
    });
  }

  document.addEventListener('click',function(e){
    var add=e.target.closest&&e.target.closest('.planadd');
    if(add){ e.preventDefault(); e.stopPropagation();
      open(add.dataset.kind,add.closest('.pgview').querySelector('.plantbl[data-plan="'+add.dataset.kind+'"]'));
      return; }
    var ed=e.target.closest&&e.target.closest('.planedit');
    if(ed){ e.preventDefault(); e.stopPropagation();
      var tr=ed.closest('tr'), t=tr.closest('.plantbl');
      open(t.dataset.plan,t,tr); return; }
    var del=e.target.closest&&e.target.closest('.planx');
    if(del){ e.preventDefault(); e.stopPropagation();
      var tr2=del.closest('tr'), t2=tr2.closest('.plantbl'), z=t2.closest('[data-ez]');
      if(!confirm('حذف هذا الصف؟'))return;
      tr2.remove();
      var tb=t2.querySelector('tbody');
      if(!tb.querySelector('tr')){
        var n=t2.querySelectorAll('thead th').length;
        tb.innerHTML='<tr class="planempty"><td colspan="'+n+'">لم يُضف شيء بعد</td></tr>';
      }
      if(z)z.dispatchEvent(new Event('input',{bubbles:true}));
      sums(); return; }
  },true);

  document.addEventListener('keydown',function(e){ if(e.key==='Escape')close(); });
  window.addEventListener('hashchange',function(){setTimeout(function(){chrome();sums();},0);});
  new MutationObserver(function(){chrome();sums();})
    .observe(document.documentElement,{attributes:true,attributeFilter:['class']});
  document.querySelectorAll('.plantbl').forEach(function(t){
    new MutationObserver(function(){chrome();sums();}).observe(t,{childList:true,subtree:true});
  });
  chrome(); sums();
})();
</script>
"""

doc = doc.replace("</head>", CSS + "</head>", 1)
doc = doc.replace("</body>", JS + "</body>", 1)
doc = re.sub(r'data-docid="[^"]*"', 'data-docid="darb-5st-forms-v1"', doc, count=1)
open(OUT, "w", encoding="utf-8").write(doc)

print("تم · الحجم:", round(len(doc.encode()) / 1024), "KB")
for c in KEEP:
    o = OPTS[c]
    print(f"  {c}: فترات {len(o['periods'])} · وحدات داخلية {len(o['units'])} "
          f"· منشآت خارجية {len(o['external'])}")
