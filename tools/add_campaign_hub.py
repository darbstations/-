# -*- coding: utf-8 -*-
"""يضيف تبويب «الحملات» في الصفحة الأولى — سجل موحّد لكل الحملات في الملف.

الفكرة: صفحة الحملات ليست نسخة ثانية من البيانات، بل **عرض حيّ** لجداول
«حملاتك المضافة» داخل صفحات الخطة التشغيلية للمحطات الخمس. أي إضافة أو حذف
أو تعديل في أي طرف ينعكس في الطرف الآخر فورًا:

  • إضافة حملة في صفحة محطة        → تظهر في سجل الحملات
  • حذفها من صفحة المحطة           → تختفي من السجل
  • تعديل خلية في السجل            → يُكتب في صف المحطة الأصلي ويُحفظ محليًا
  • ＋ / ✎ / × من داخل السجل        → تعمل على صف المحطة نفسه بالنموذج ذاته

لا تُخزَّن بيانات مكرّرة: مصدر الحقيقة الوحيد هو جدول المحطة، والسجل يُعاد
بناؤه من المصدر عند كل تغيير.

    python3 tools/add_campaign_hub.py [ملف-المصدر] [ملف-المخرَج]
"""
import re, os, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = OUT = os.path.join(BASE, "darb-five-stations-analysis.html")
if len(sys.argv) > 1:
    SRC = sys.argv[1]
    OUT = sys.argv[2] if len(sys.argv) > 2 else SRC

doc = open(SRC, encoding="utf-8").read()

# ═══════════ 1. كشف نموذج الخطة للاستعمال من صفحة الحملات ═══════════
HOOK = """
  /* ‏— كشف النموذج ليستدعيه سجل الحملات في الصفحة الأولى — */
  window.DARB=window.DARB||{};
  window.DARB.planOpen=function(kind,host,row){ open(kind,host,row); };
  window.DARB.planSync=function(){ chrome(); sums(); };
})();
</script>"""
TAIL = """})();
</script>"""
i = doc.index('<script id="planform-js">')
j = doc.index(TAIL, i) + len(TAIL)
doc = doc[:j - len(TAIL)] + HOOK + doc[j:]

CSS = """
<style id="camphub-css">
/* ── تبويبا الصفحة الأولى ── */
#hubtabs{max-width:var(--maxw,1240px);margin:0 auto;padding:0 var(--pad,26px);
  display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:2px}
#hubtabs .htab{font-family:inherit;font-size:13.5px;font-weight:700;cursor:pointer;
  background:var(--card);border:1px solid var(--line2);color:var(--ink2);
  border-radius:11px;padding:9px 17px;transition:.14s;display:flex;align-items:center;gap:7px}
#hubtabs .htab:hover{border-color:var(--orange);color:var(--ink)}
#hubtabs .htab.on{background:var(--orange);border-color:var(--orange);color:#fff;
  box-shadow:0 2px 10px rgba(246,133,31,.22)}
#hubtabs .htab .n{font-size:11.5px;font-weight:800;background:rgba(0,0,0,.08);
  border-radius:7px;padding:1px 7px;min-width:20px;text-align:center}
#hubtabs .htab.on .n{background:rgba(255,255,255,.24)}
/* ── سجل الحملات ── */
#campview{max-width:var(--maxw,1240px);margin:0 auto;padding:14px var(--pad,26px) 40px}
#campview .cvbar{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:0 0 12px}
#campview .cvadd{font-family:inherit;font-size:13px;font-weight:700;cursor:pointer;
  background:var(--orange);color:#fff;border:1px solid var(--orange);border-radius:10px;
  padding:8px 15px;box-shadow:0 2px 10px rgba(246,133,31,.22)}
#campview .cvadd:hover{filter:brightness(1.06)}
#campview select.cvst{font-family:inherit;font-size:13px;color:var(--ink);background:#FDFCFA;
  border:1px solid var(--line2);border-radius:10px;padding:8px 10px}
#campview .cvsum{font-size:12px;color:var(--ink3)}
#campview .cvsum b{color:var(--ink2)}
#campview table td{white-space:normal;line-height:1.75;vertical-align:top}
#campview table td:first-child{min-width:150px;position:relative}
#campview .cvst2{font-size:11px;color:var(--ink3);display:block}
#campview .cvempty td{text-align:center;color:var(--ink3);font-size:12.5px;padding:22px 10px}
#campview td[data-col]:focus{outline:2px solid var(--orange);outline-offset:-2px;background:#fff}
.cvx,.cvedit{display:inline-block;width:17px;height:17px;border-radius:50%;font-size:11px;
  font-weight:800;line-height:15px;text-align:center;cursor:pointer;opacity:0;transition:.12s;
  user-select:none;-webkit-user-select:none;vertical-align:middle;margin-inline-end:3px}
.cvx{background:#FBF0ED;border:1px solid #E3BEB4;color:#A6432E}
.cvedit{background:#F1EFEB;border:1px solid #DDD8CF;color:#6E6A64}
#campview tr:hover .cvx,#campview tr:hover .cvedit{opacity:1}
.cvx:hover{background:#C0503A;color:#fff;border-color:#C0503A}
.cvedit:hover{background:#55565A;color:#fff;border-color:#55565A}
#campview .cvcode{font-size:10.5px;font-weight:800;background:var(--bgray);color:#fff;
  padding:1px 7px;border-radius:6px;letter-spacing:.4px}
#campview .cvlink{color:var(--ink3);font-size:11px;text-decoration:none;display:block;margin-top:3px}
#campview .cvname{display:inline-block;margin-inline-start:5px;font-weight:700}
#campview .cvlink:hover{color:var(--orange)}
</style>
"""

JS = r"""
<script id="camphub-js">
/* ═══ سجل الحملات في الصفحة الأولى ═══
   عرض حيّ لجداول «حملاتك المضافة» في صفحات الخطة. مصدر الحقيقة هو جدول
   المحطة؛ السجل يُبنى منه ويكتب فيه، ولا يُخزَّن مستقلًا.               */
(function(){
  var COLS=['المحطة','الحملة','الفترة','المدة','الشركاء الداخليون','شروط الحملة',
            'الأدوات والمواد','الميزانية (ر.س)','المستهدف الرقمي','المستهدف الميداني'];
  var NUM=function(v){var n=parseFloat(String(v).replace(/[^\d.\-]/g,''));return isNaN(n)?0:n;};
  var FMT=function(n){return Math.round(n).toLocaleString('en-US');};
  var ESC=function(s){var d=document.createElement('div');d.textContent=s==null?'':s;return d.innerHTML;};
  var writing=false, view='stations';

  function plans(){
    return [].slice.call(document.querySelectorAll('.pgview[id$="-plan"]')).map(function(pv){
      var m=/^pg-([A-Za-z]{2}\d+)-plan$/.exec(pv.id); if(!m)return null;
      var t=(pv.dataset.title||'').split(' · ')[0]
              .replace(/^درب\s+/,'').replace(/\s*[A-Za-z]{2}\d+\s*$/,'');
      var tbl=pv.querySelector('.plantbl[data-plan="camp"]');
      return tbl?{code:m[1],name:t,tbl:tbl}:null;
    }).filter(Boolean);
  }

  function rows(){
    var out=[];
    plans().forEach(function(p){
      [].slice.call(p.tbl.querySelectorAll('tbody tr')).forEach(function(tr){
        if(tr.classList.contains('planempty'))return;
        if(!tr.dataset.cid)tr.dataset.cid='c'+Math.random().toString(36).slice(2,9);
        out.push({code:p.code,name:p.name,tbl:p.tbl,tr:tr,cid:tr.dataset.cid,
          cells:[].slice.call(tr.cells).map(function(td){
            return td.textContent.replace(/[×✎]/g,'').trim();})});
      });
    });
    return out;
  }
  var sig=function(d){return d.map(function(r){
    return r.code+'|'+r.cid+'|'+r.cells.join('§');}).join('¶');};

  /* ── بناء الهيكل مرة واحدة ── */
  var hub=document.getElementById('hub');
  if(!hub)return;
  var stationsPane=hub.querySelector('main.wrap[data-ez]');
  var bar=hub.querySelector('.stationbar');

  var tabs=document.getElementById('hubtabs');
  if(!tabs){
    tabs=document.createElement('div'); tabs.id='hubtabs';
    tabs.innerHTML='<button type="button" class="htab on" data-v="stations">⛽ المحطات'
      +'<span class="n" data-n="st">5</span></button>'
      +'<button type="button" class="htab" data-v="camps">📣 الحملات'
      +'<span class="n" data-n="cp">0</span></button>';
    hub.insertBefore(tabs,bar?bar.nextSibling:hub.firstChild);
  }
  var cv=document.getElementById('campview');
  if(!cv){
    cv=document.createElement('div'); cv.id='campview'; cv.hidden=true;
    cv.innerHTML=
      '<div class="sec-h"><h2>📣 سجل الحملات</h2><span>كل الحملات المسجَّلة في الملف '
      +'— تُقرأ وتُعدَّل من هنا أو من صفحة المحطة، والطرفان متزامنان</span></div>'
      +'<div class="cvbar"><select class="cvst" aria-label="المحطة"></select>'
      +'<button type="button" class="cvadd">＋ أضف حملة</button>'
      +'<span class="cvsum"></span></div>'
      +'<div class="ntable"><div class="tscroll"><table><thead><tr>'
      +COLS.map(function(c){return '<th>'+ESC(c)+'</th>';}).join('')
      +'</tr></thead><tbody></tbody></table></div></div>'
      +'<div class="dnote">📐 <b>مصدر البيانات:</b> جداول «حملاتك المضافة» داخل تبويب '
      +'«الخطة التشغيلية» لكل محطة — لا نسخة ثانية محفوظة هنا. الكتابة في أي خلية '
      +'تُحدِّث صف المحطة الأصلي مباشرة ويُحفظ التعديل محليًا. زر <b>✎</b> يفتح نموذج '
      +'الحملة كاملًا، و<b>×</b> يحذفها من محطتها، و<b>＋</b> يضيفها للمحطة المختارة.</div>';
    if(stationsPane&&stationsPane.parentNode)
      stationsPane.parentNode.insertBefore(cv,stationsPane.nextSibling);
    else hub.appendChild(cv);
  }
  var sel=cv.querySelector('.cvst'), tb=cv.querySelector('tbody');

  function fillStations(){
    var ps=plans(), cur=sel.value;
    var html=ps.map(function(p){
      return '<option value="'+p.code+'">'+ESC(p.name)+'</option>';}).join('');
    if(sel.innerHTML!==html){ sel.innerHTML=html; if(cur)sel.value=cur; }
    var n=tabs.querySelector('[data-n="st"]'); if(n)n.textContent=ps.length;
  }

  /* ── الرسم ── */
  var last='';
  function render(force){
    fillStations();
    var d=rows(), s=sig(d);
    var n=tabs.querySelector('[data-n="cp"]'); if(n)n.textContent=d.length;
    var tot=d.reduce(function(a,r){return a+NUM(r.cells[6]);},0);
    var by={}; d.forEach(function(r){by[r.name]=(by[r.name]||0)+1;});
    cv.querySelector('.cvsum').innerHTML=d.length
      ? '<b>'+d.length+'</b> حملة · إجمالي الميزانية <b>'+FMT(tot)+'</b> ر.س · '
        +Object.keys(by).map(function(k){return ESC(k)+' '+by[k];}).join(' · ')
      : '';
    if(!force&&s===last)return;
    if(!force&&cv.contains(document.activeElement))return;   /* لا نقطع الكتابة */
    last=s;
    if(!d.length){
      tb.innerHTML='<tr class="cvempty"><td colspan="'+COLS.length+'">لا توجد حملات مسجَّلة بعد '
        +'— أضف واحدة من هنا، أو من تبويب «الخطة التشغيلية» في أي محطة.</td></tr>';
      return;
    }
    tb.innerHTML=d.map(function(r){
      var tds=r.cells.map(function(v,i){
        return '<td data-col="'+i+'" data-cid="'+r.cid+'">'+ESC(v||'—')+'</td>';}).join('');
      return '<tr data-cid="'+r.cid+'"><td>'
        +'<span class="cvx" title="حذف الحملة من محطتها">×</span>'
        +'<span class="cvedit" title="تعديل بالنموذج">✎</span>'
        +'<span class="cvcode">'+ESC(r.code)+'</span><span class="cvname">'+ESC(r.name)+'</span>'
        +'<a class="cvlink" href="#/'+r.code+'/plan">افتح الخطة ↗</a></td>'+tds+'</tr>';
    }).join('');
    [].slice.call(tb.querySelectorAll('td[data-col]')).forEach(function(td){
      td.setAttribute('contenteditable','true'); td.setAttribute('spellcheck','false');
    });
  }

  function find(cid){
    var r=null; rows().forEach(function(x){if(x.cid===cid)r=x;}); return r;
  }

  /* ── الكتابة رجوعًا إلى صف المحطة ── */
  var t=null;
  tb.addEventListener('input',function(e){
    var td=e.target.closest&&e.target.closest('td[data-col]'); if(!td)return;
    var r=find(td.dataset.cid); if(!r)return;
    var i=+td.dataset.col, cell=r.tr.cells[i]; if(!cell)return;
    writing=true;
    var v=td.textContent.trim();
    if(i===0){                                   /* عمود الاسم فيه <b> */
      var b=cell.querySelector('b'); if(b)b.textContent=v||'—'; else cell.textContent=v||'—';
    }else{
      var keep=[].slice.call(cell.querySelectorAll('.planx,.planedit'));
      cell.textContent=v||'—';
      keep.forEach(function(k){cell.insertBefore(k,cell.firstChild);});
    }
    var z=r.tbl.closest('[data-ez]');
    if(z)z.dispatchEvent(new Event('input',{bubbles:true}));
    clearTimeout(t); t=setTimeout(function(){writing=false;render();},700);
  });

  /* ── أزرار السجل ── */
  cv.addEventListener('click',function(e){
    var x=e.target.closest&&e.target.closest('.cvx');
    if(x){
      var r=find(x.closest('tr').dataset.cid); if(!r)return;
      if(!confirm('حذف حملة «'+(r.cells[0]||'')+'» من محطة '+r.name+'؟'))return;
      var host=r.tbl, z=host.closest('[data-ez]');
      r.tr.remove();
      var body=host.querySelector('tbody');
      if(!body.querySelector('tr')){
        body.innerHTML='<tr class="planempty"><td colspan="'
          +host.querySelectorAll('thead th').length+'">لم تُضف حملة بعد</td></tr>';
      }
      if(z)z.dispatchEvent(new Event('input',{bubbles:true}));
      if(window.DARB&&DARB.planSync)DARB.planSync();
      render(true); return;
    }
    var ed=e.target.closest&&e.target.closest('.cvedit');
    if(ed){
      var r2=find(ed.closest('tr').dataset.cid); if(!r2)return;
      if(window.DARB&&DARB.planOpen)DARB.planOpen('camp',r2.tbl,r2.tr);
      return;
    }
    var add=e.target.closest&&e.target.closest('.cvadd');
    if(add){
      var code=sel.value, p=null;
      plans().forEach(function(x){if(x.code===code)p=x;});
      if(!p){alert('اختر محطة أولًا.');return;}
      if(window.DARB&&DARB.planOpen)DARB.planOpen('camp',p.tbl);
      return;
    }
  });

  /* ── تبديل العرض ── */
  function show(v){
    view=v;
    try{sessionStorage.setItem('darb-hubview',v);}catch(_){}
    tabs.querySelectorAll('.htab').forEach(function(b){
      b.classList.toggle('on',b.dataset.v===v);});
    if(stationsPane)stationsPane.hidden=(v!=='stations');
    if(bar)bar.hidden=(v!=='stations');
    cv.hidden=(v!=='camps');
    if(v==='camps')render(true);
  }
  tabs.addEventListener('click',function(e){
    var b=e.target.closest&&e.target.closest('.htab'); if(!b)return;
    e.preventDefault(); show(b.dataset.v);
  });
  try{ var saved=sessionStorage.getItem('darb-hubview'); if(saved)show(saved); }catch(_){}

  /* ── المزامنة: أي تغيير في جداول المحطات يعيد الرسم ── */
  var mo=new MutationObserver(function(){ if(!writing)render(); });
  function watch(){
    plans().forEach(function(p){
      var body=p.tbl.querySelector('tbody');
      if(body&&!body.__cvwatched){ body.__cvwatched=true;
        mo.observe(body,{childList:true,subtree:true,characterData:true}); }
    });
  }
  watch();
  new MutationObserver(function(){watch();render();})
    .observe(document.documentElement,{attributes:true,attributeFilter:['class']});
  window.addEventListener('hashchange',function(){setTimeout(function(){watch();render();},0);});
  render(true);
})();
</script>
"""

doc = doc.replace("</head>", CSS + "</head>", 1)
doc = doc.replace("</body>", JS + "</body>", 1)
open(OUT, "w", encoding="utf-8").write(doc)
print("تم · الحجم:", round(len(doc.encode()) / 1024), "KB · المخرَج:", OUT)
