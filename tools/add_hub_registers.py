# -*- coding: utf-8 -*-
"""سجلّات الخطة في الصفحة الأولى: الحملات · الشراكات · التوزيعات.

يحلّ محلّ `add_campaign_hub.py` ويعمّم فكرته على المحاور الثلاثة: كل سجل
عرض حيّ لجداول «… المضافة» داخل صفحات الخطة التشغيلية للمحطات الخمس، لا
نسخة ثانية من البيانات. مصدر الحقيقة الوحيد هو جدول المحطة:

  • إضافة/حذف في صفحة محطة   → ينعكس في السجل فورًا
  • ＋ / ✎ / × من السجل        → تعمل على صف المحطة نفسه بالنموذج ذاته
  • الكتابة في خلية بالسجل    → تُكتب في صف المحطة الأصلي وتُحفظ محليًا

    python3 tools/add_hub_registers.py [ملف-المصدر] [ملف-المخرَج]
"""
import os, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = OUT = os.path.join(BASE, "darb-five-stations-analysis.html")
if len(sys.argv) > 1:
    SRC = sys.argv[1]
    OUT = sys.argv[2] if len(sys.argv) > 2 else SRC

doc = open(SRC, encoding="utf-8").read()
assert "camphub-js" not in doc, "الملف يحوي سجل الحملات القديم — ابْنِ من الأساس المعتمد"

# ═══════════ كشف نموذج الخطة لتستدعيه سجلّات الصفحة الأولى ═══════════
HOOK = """
  /* ‏— كشف النموذج لتستدعيه سجلّات الصفحة الأولى — */
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
<style id="hubreg-css">
/* ── تبويبات الصفحة الأولى ── */
#hubtabs{max-width:var(--maxw,1240px);margin:0 auto 2px;padding:0 var(--pad,26px);
  display:flex;gap:8px;align-items:center;flex-wrap:wrap}
#hubtabs .htab{font-family:inherit;font-size:13.5px;font-weight:700;cursor:pointer;
  background:var(--card);border:1px solid var(--line2);color:var(--ink2);
  border-radius:11px;padding:9px 16px;transition:.14s;display:flex;align-items:center;gap:7px}
#hubtabs .htab:hover{border-color:var(--orange);color:var(--ink)}
#hubtabs .htab.on{background:var(--orange);border-color:var(--orange);color:#fff;
  box-shadow:0 2px 10px rgba(246,133,31,.22)}
#hubtabs .htab .n{font-size:11.5px;font-weight:800;background:rgba(0,0,0,.08);
  border-radius:7px;padding:1px 7px;min-width:20px;text-align:center}
#hubtabs .htab.on .n{background:rgba(255,255,255,.24)}
/* ── السجلّات ── */
.hubreg{max-width:var(--maxw,1240px);margin:0 auto;padding:14px var(--pad,26px) 40px}
.hubreg .rgbar{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:0 0 12px}
.hubreg .rgadd{font-family:inherit;font-size:13px;font-weight:700;cursor:pointer;
  background:var(--orange);color:#fff;border:1px solid var(--orange);border-radius:10px;
  padding:8px 15px;box-shadow:0 2px 10px rgba(246,133,31,.22)}
.hubreg .rgadd:hover{filter:brightness(1.06)}
.hubreg select.rgst{font-family:inherit;font-size:13px;color:var(--ink);background:#FDFCFA;
  border:1px solid var(--line2);border-radius:10px;padding:8px 10px}
.hubreg .rgsum{font-size:12px;color:var(--ink3)}
.hubreg .rgsum b{color:var(--ink2)}
.hubreg table td{white-space:normal;line-height:1.75;vertical-align:top}
.hubreg table td:first-child{min-width:150px;position:relative}
.hubreg .rgempty td{text-align:center;color:var(--ink3);font-size:12.5px;padding:22px 10px}
.hubreg td[data-col]:focus{outline:2px solid var(--orange);outline-offset:-2px;background:#fff}
.rgx,.rgedit{display:inline-block;width:17px;height:17px;border-radius:50%;font-size:11px;
  font-weight:800;line-height:15px;text-align:center;cursor:pointer;opacity:0;transition:.12s;
  user-select:none;-webkit-user-select:none;vertical-align:middle;margin-inline-end:3px}
.rgx{background:#FBF0ED;border:1px solid #E3BEB4;color:#A6432E}
.rgedit{background:#F1EFEB;border:1px solid #DDD8CF;color:#6E6A64}
.hubreg tr:hover .rgx,.hubreg tr:hover .rgedit{opacity:1}
.rgx:hover{background:#C0503A;color:#fff;border-color:#C0503A}
.rgedit:hover{background:#55565A;color:#fff;border-color:#55565A}
.hubreg .rgcode{font-size:10.5px;font-weight:800;background:var(--bgray);color:#fff;
  padding:1px 7px;border-radius:6px;letter-spacing:.4px}
.hubreg .rgname{display:inline-block;margin-inline-start:5px;font-weight:700}
.hubreg .rglink{color:var(--ink3);font-size:11px;text-decoration:none;display:block;margin-top:3px}
.hubreg .rglink:hover{color:var(--orange)}
</style>
"""

JS = r"""
<script id="hubreg-js">
/* ═══ سجلّات الخطة في الصفحة الأولى ═══
   عرض حيّ لجداول «… المضافة» في صفحات الخطة. مصدر الحقيقة هو جدول المحطة؛
   السجل يُبنى منه ويكتب فيه، ولا يُخزَّن مستقلًا.                        */
(function(){
  var KINDS={
    camp:{tab:'📣 الحملات', title:'سجل الحملات', add:'＋ أضف حملة',
      sub:'كل حملات تشجيع المبيعات المسجَّلة في المنصّة',
      cols:['الحملة','الفترة','المدة','الشركاء الداخليون','شروط الحملة',
            'الأدوات والمواد','الميزانية (ر.س)','المستهدف الرقمي','المستهدف الميداني'],
      empty:'لا توجد حملات مسجَّلة بعد'},
    part:{tab:'🤝 الشراكات', title:'سجل الشراكات', add:'＋ أضف شراكة',
      sub:'الشركاء الداخليون والخارجيون المتعاقد معهم أو المستهدَفون',
      cols:['الشريك','النوع','المدة','شروط الشراكة','مستهدفات الشراكة',
            'مستهدف رقمي','مستهدف ميداني','مستهدف وصول'],
      empty:'لا توجد شراكات مسجَّلة بعد'},
    dist:{tab:'🎁 التوزيعات', title:'سجل التوزيعات', add:'＋ أضف توزيعًا',
      sub:'ما يوزَّع داخل المحطات، وكميته وتكلفته اليومية',
      cols:['الصنف','الفترة','الكمية اليومية','المدة','تكلفة الوحدة (ر.س)',
            'التكلفة اليومية (ر.س)','المسؤول','المستهدف'],
      empty:'لا توجد توزيعات مسجَّلة بعد'}
  };
  var NUM=function(v){var n=parseFloat(String(v).replace(/[^\d.\-]/g,''));return isNaN(n)?0:n;};
  var FMT=function(n){return Math.round(n).toLocaleString('en-US');};
  var ESC=function(s){var d=document.createElement('div');d.textContent=s==null?'':s;return d.innerHTML;};
  var writing=false;

  function plans(kind){
    return [].slice.call(document.querySelectorAll('.pgview[id$="-plan"]')).map(function(pv){
      var m=/^pg-([A-Za-z]{2}\d+)-plan$/.exec(pv.id); if(!m)return null;
      var t=(pv.dataset.title||'').split(' · ')[0]
              .replace(/^درب\s+/,'').replace(/\s*[A-Za-z]{2}\d+\s*$/,'');
      var tbl=pv.querySelector('.plantbl[data-plan="'+kind+'"]');
      return tbl?{code:m[1],name:t,tbl:tbl}:null;
    }).filter(Boolean);
  }
  function rows(kind){
    var out=[];
    plans(kind).forEach(function(p){
      [].slice.call(p.tbl.querySelectorAll('tbody tr')).forEach(function(tr){
        if(tr.classList.contains('planempty'))return;
        if(!tr.dataset.cid)tr.dataset.cid='r'+Math.random().toString(36).slice(2,9);
        out.push({code:p.code,name:p.name,tbl:p.tbl,tr:tr,cid:tr.dataset.cid,
          cells:[].slice.call(tr.cells).map(function(td){
            return td.textContent.replace(/[×✎]/g,'').trim();})});
      });
    });
    return out;
  }
  function summarize(kind,d){
    if(!d.length)return '';
    var by={}; d.forEach(function(r){by[r.name]=(by[r.name]||0)+1;});
    var spread=Object.keys(by).map(function(k){return ESC(k)+' '+by[k];}).join(' · ');
    if(kind==='camp'){
      var b=d.reduce(function(a,r){return a+NUM(r.cells[6]);},0);
      return '<b>'+d.length+'</b> حملة · إجمالي الميزانية <b>'+FMT(b)+'</b> ر.س · '+spread;
    }
    if(kind==='part'){
      var i=0,x=0; d.forEach(function(r){
        var t=(r.cells[1]||'').trim(); if(t==='خارجي')x++; else if(t==='داخلي')i++;});
      return '<b>'+d.length+'</b> شراكة · داخلي <b>'+i+'</b> · خارجي <b>'+x+'</b> · '+spread;
    }
    var s=d.reduce(function(a,r){return a+NUM(r.cells[5]);},0);
    return '<b>'+d.length+'</b> صنف · التكلفة اليومية <b>'+FMT(s)+'</b> ر.س · الشهرية <b>'
      +FMT(s*30)+'</b> ر.س · '+spread;
  }

  var hub=document.getElementById('hub'); if(!hub)return;
  var stationsPane=hub.querySelector('main.wrap[data-ez]');
  var bar=hub.querySelector('.stationbar');

  /* ── شريط التبويبات ── */
  var tabs=document.getElementById('hubtabs');
  if(!tabs){
    tabs=document.createElement('div'); tabs.id='hubtabs';
    var h='<button type="button" class="htab on" data-v="stations">⛽ المحطات'
         +'<span class="n" data-n="stations">5</span></button>';
    Object.keys(KINDS).forEach(function(k){
      h+='<button type="button" class="htab" data-v="'+k+'">'+KINDS[k].tab
        +'<span class="n" data-n="'+k+'">0</span></button>';
    });
    tabs.innerHTML=h;
    hub.insertBefore(tabs,bar?bar.nextSibling:hub.firstChild);
  }

  /* ── لوح لكل سجل ── */
  var panes={};
  Object.keys(KINDS).forEach(function(kind){
    var K=KINDS[kind], id='reg-'+kind, el=document.getElementById(id);
    if(!el){
      el=document.createElement('div'); el.id=id; el.className='hubreg'; el.hidden=true;
      el.dataset.kind=kind;
      el.innerHTML=
        '<div class="sec-h"><h2>'+K.tab+' — '+ESC(K.title)+'</h2><span>'+ESC(K.sub)
        +' · تُقرأ وتُعدَّل من هنا أو من صفحة المحطة، والطرفان متزامنان</span></div>'
        +'<div class="rgbar"><select class="rgst" aria-label="المحطة"></select>'
        +'<button type="button" class="rgadd">'+K.add+'</button>'
        +'<span class="rgsum"></span></div>'
        +'<div class="ntable"><div class="tscroll"><table><thead><tr><th>المحطة</th>'
        +K.cols.map(function(c){return '<th>'+ESC(c)+'</th>';}).join('')
        +'</tr></thead><tbody></tbody></table></div></div>'
        +'<div class="dnote">📐 <b>المصدر:</b> جداول «… المضافة» داخل تبويب «الخطة التشغيلية» '
        +'لكل محطة — لا نسخة ثانية محفوظة هنا. الكتابة في أي خلية تُحدِّث صف المحطة الأصلي '
        +'ويُحفظ التعديل محليًا. <b>✎</b> يفتح النموذج كاملًا، و<b>×</b> يحذف من المحطة، '
        +'و<b>＋</b> يضيف للمحطة المختارة.</div>';
      (stationsPane&&stationsPane.parentNode
        ? stationsPane.parentNode.insertBefore(el,stationsPane.nextSibling)
        : hub.appendChild(el));
    }
    panes[kind]=el;
  });

  var lastSig={};
  function render(kind,force){
    var el=panes[kind], K=KINDS[kind];
    var ps=plans(kind), sel=el.querySelector('.rgst');
    var opts=ps.map(function(p){
      return '<option value="'+p.code+'">'+ESC(p.name)+'</option>';}).join('');
    if(sel.innerHTML!==opts){var cur=sel.value;sel.innerHTML=opts;if(cur)sel.value=cur;}
    var d=rows(kind), s=d.map(function(r){
      return r.code+'|'+r.cid+'|'+r.cells.join('§');}).join('¶');
    var n=tabs.querySelector('[data-n="'+kind+'"]'); if(n)n.textContent=d.length;
    el.querySelector('.rgsum').innerHTML=summarize(kind,d);
    if(!force&&s===lastSig[kind])return;
    if(!force&&el.contains(document.activeElement))return;   /* لا نقطع الكتابة */
    lastSig[kind]=s;
    var tb=el.querySelector('tbody');
    if(!d.length){
      tb.innerHTML='<tr class="rgempty"><td colspan="'+(K.cols.length+1)+'">'+ESC(K.empty)
        +' — أضف واحدًا من هنا، أو من تبويب «الخطة التشغيلية» في أي محطة.</td></tr>';
      return;
    }
    tb.innerHTML=d.map(function(r){
      return '<tr data-cid="'+r.cid+'"><td>'
        +'<span class="rgx" title="حذف من محطته">×</span>'
        +'<span class="rgedit" title="تعديل بالنموذج">✎</span>'
        +'<span class="rgcode">'+ESC(r.code)+'</span>'
        +'<span class="rgname">'+ESC(r.name)+'</span>'
        +'<a class="rglink" href="#/'+r.code+'/plan">افتح الخطة ↗</a></td>'
        +r.cells.map(function(v,i){
          return '<td data-col="'+i+'" data-cid="'+r.cid+'" contenteditable="true" '
                +'spellcheck="false">'+ESC(v||'—')+'</td>';}).join('')+'</tr>';
    }).join('');
  }
  function renderAll(force){ Object.keys(KINDS).forEach(function(k){render(k,force);}); }
  function find(kind,cid){ var f=null; rows(kind).forEach(function(r){if(r.cid===cid)f=r;}); return f; }

  /* ── الكتابة رجوعًا إلى صف المحطة ── */
  var timer=null;
  Object.keys(KINDS).forEach(function(kind){
    var el=panes[kind];
    el.addEventListener('input',function(e){
      var td=e.target.closest&&e.target.closest('td[data-col]'); if(!td)return;
      var r=find(kind,td.dataset.cid); if(!r)return;
      var i=+td.dataset.col, cell=r.tr.cells[i]; if(!cell)return;
      writing=true;
      var v=td.textContent.trim();
      if(i===0){
        var b=cell.querySelector('b'); if(b)b.textContent=v||'—'; else cell.textContent=v||'—';
      }else{
        var keep=[].slice.call(cell.querySelectorAll('.planx,.planedit'));
        cell.textContent=v||'—';
        keep.forEach(function(k){cell.insertBefore(k,cell.firstChild);});
      }
      var z=r.tbl.closest('[data-ez]');
      if(z)z.dispatchEvent(new Event('input',{bubbles:true}));
      clearTimeout(timer); timer=setTimeout(function(){writing=false;renderAll();},700);
    });
    el.addEventListener('click',function(e){
      var x=e.target.closest&&e.target.closest('.rgx');
      if(x){
        var r=find(kind,x.closest('tr').dataset.cid); if(!r)return;
        if(!confirm('حذف «'+(r.cells[0]||'')+'» من محطة '+r.name+'؟'))return;
        var host=r.tbl, z=host.closest('[data-ez]');
        r.tr.remove();
        var body=host.querySelector('tbody');
        if(!body.querySelector('tr')){
          body.innerHTML='<tr class="planempty"><td colspan="'
            +host.querySelectorAll('thead th').length+'">لم يُضف شيء بعد</td></tr>';
        }
        if(z)z.dispatchEvent(new Event('input',{bubbles:true}));
        if(window.DARB&&DARB.planSync)DARB.planSync();
        renderAll(true); return;
      }
      var ed=e.target.closest&&e.target.closest('.rgedit');
      if(ed){
        var r2=find(kind,ed.closest('tr').dataset.cid); if(!r2)return;
        if(window.DARB&&DARB.planOpen)DARB.planOpen(kind,r2.tbl,r2.tr);
        return;
      }
      var add=e.target.closest&&e.target.closest('.rgadd');
      if(add){
        var code=el.querySelector('.rgst').value, p=null;
        plans(kind).forEach(function(x){if(x.code===code)p=x;});
        if(!p){alert('اختر محطة أولًا.');return;}
        if(window.DARB&&DARB.planOpen)DARB.planOpen(kind,p.tbl);
        return;
      }
    });
  });

  /* ── تبديل العرض ── */
  function show(v){
    try{sessionStorage.setItem('darb-hubview',v);}catch(_){}
    tabs.querySelectorAll('.htab').forEach(function(b){
      b.classList.toggle('on',b.dataset.v===v);});
    if(stationsPane)stationsPane.hidden=(v!=='stations');
    if(bar)bar.hidden=(v!=='stations');
    Object.keys(panes).forEach(function(k){panes[k].hidden=(k!==v);});
    var ex=document.querySelectorAll('[data-hubpane]');
    [].slice.call(ex).forEach(function(n){n.hidden=(n.dataset.hubpane!==v);});
    if(KINDS[v])render(v,true);
  }
  window.DARB=window.DARB||{};
  window.DARB.hubShow=show;
  window.DARB.hubTabs=function(){return tabs;};
  tabs.addEventListener('click',function(e){
    var b=e.target.closest&&e.target.closest('.htab'); if(!b)return;
    e.preventDefault(); show(b.dataset.v);
  });
  try{var saved=sessionStorage.getItem('darb-hubview'); if(saved)show(saved);}catch(_){}

  /* ── المزامنة ── */
  var mo=new MutationObserver(function(){ if(!writing)renderAll(); });
  function watch(){
    Object.keys(KINDS).forEach(function(kind){
      plans(kind).forEach(function(p){
        var body=p.tbl.querySelector('tbody');
        if(body&&!body.__rgwatched){ body.__rgwatched=true;
          mo.observe(body,{childList:true,subtree:true,characterData:true}); }
      });
    });
  }
  watch();
  new MutationObserver(function(){watch();renderAll();})
    .observe(document.documentElement,{attributes:true,attributeFilter:['class']});
  window.addEventListener('hashchange',function(){setTimeout(function(){watch();renderAll();},0);});
  renderAll(true);
})();
</script>
"""

doc = doc.replace("</head>", CSS + "</head>", 1)
doc = doc.replace("</body>", JS + "</body>", 1)
open(OUT, "w", encoding="utf-8").write(doc)
print("تم · الحجم:", round(len(doc.encode()) / 1024), "KB ·", OUT)
