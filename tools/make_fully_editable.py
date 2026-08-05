# -*- coding: utf-8 -*-
"""يجعل الملف قابلًا للتعديل من كل النواحي.

ما يضيفه:
  • صفحة المقارنة تصبح منطقة تحرير كبقية الصفحات.
  • حذف أي عمود من أي جدول (× على رأس العمود) — كان الحذف متاحًا للصفوف فقط.
  • إعادة تسمية العناصر المقفلة (التبويبات · روابط التنقّل · رقاقات المناطق ·
    قائمة المحطات) بنقرة مزدوجة — تبقى مقفلة أمام الكتابة المباشرة حتى لا
    ينكسر التنقّل، لكنها لم تعد غير قابلة للتغيير.
  • إضافة تبويب/صفحة جديدة لأي محطة، وحذف أي تبويب مع صفحته.
  • قوالب إضافة جديدة: بطاقة مؤشر · قائمة نقاط · ملاحظة.
  • بطاقات المؤشرات وبطاقات المحطات والبطاقات الشهرية صارت كتلًا كاملة:
    تُسحب وتُكرَّر وتُحذف مثل بقية الكتل.
"""
import re, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = OUT = os.path.join(BASE, "darb-five-stations-analysis.html")

doc = open(SRC, encoding="utf-8").read()
MAXEZ = max(int(m) for m in re.findall(r'data-ez="z(\d+)"', doc))

# ═══════════ 1. صفحة المقارنة تصبح قابلة للتحرير ═══════════
MAXEZ += 1
doc, n = re.subn(r'<div class="pgview" id="pg-compare"',
                 f'<div class="pgview" data-ez="z{MAXEZ}" spellcheck="false" id="pg-compare"',
                 doc, count=1)
assert n == 1, "لم يُعثر على صفحة المقارنة"

# ═══════════ 2. توسيع بنّاء الصفحات ═══════════
#  (أ) الشبكات التي تُعدّ أبناؤها كتلًا مستقلة
GRIDS_OLD = "p.matches('.agrid,.pgrid,.siggrid,.swot')"
GRIDS_NEW = ("p.matches('.agrid,.pgrid,.siggrid,.swot,.skpis,.netkpis,"
             ".grid-cards,.mcards,.mapgrid,.hchips')")
assert doc.count(GRIDS_OLD) == 1
doc = doc.replace(GRIDS_OLD, GRIDS_NEW, 1)

CANDS_OLD = "z.querySelectorAll('.agrid,.pgrid,.siggrid,.swot').forEach"
CANDS_NEW = ("z.querySelectorAll('.agrid,.pgrid,.siggrid,.swot,.skpis,.netkpis,"
             ".grid-cards,.mcards,.mapgrid').forEach")
assert doc.count(CANDS_OLD) == 1
doc = doc.replace(CANDS_OLD, CANDS_NEW, 1)

#  (ب) قوالب إضافة جديدة
TPL_OLD = """    grp:'<div class="card"><div class="ct"><h3>مجموعة شركاء جديدة</h3><div class="leg">أضف الوحدات</div></div>'+
        '<div class="ptags"><span class="ptag">شريك 1</span><span class="ptag">شريك 2</span></div></div>'
  };"""
TPL_NEW = """    grp:'<div class="card"><div class="ct"><h3>مجموعة شركاء جديدة</h3><div class="leg">أضف الوحدات</div></div>'+
        '<div class="ptags"><span class="ptag">شريك 1</span><span class="ptag">شريك 2</span></div></div>',
    kpi:'<div class="skpis" style="grid-template-columns:repeat(4,1fr)">'+
        '<div class="kpi hot"><div class="kl">اسم المؤشر</div><div class="kv">0</div><div class="kn">شرح مختصر</div></div>'+
        '<div class="kpi"><div class="kl">اسم المؤشر</div><div class="kv">0</div><div class="kn">شرح مختصر</div></div>'+
        '<div class="kpi"><div class="kl">اسم المؤشر</div><div class="kv">0</div><div class="kn">شرح مختصر</div></div>'+
        '<div class="kpi"><div class="kl">اسم المؤشر</div><div class="kv">0</div><div class="kn">شرح مختصر</div></div></div>',
    list:'<div class="card"><div class="ct"><h3>قائمة نقاط</h3><div class="leg">عدّل العنوان</div></div>'+
        '<ul style="font-size:13px;color:var(--ink2);line-height:2;margin:6px 22px 0 0">'+
        '<li>النقطة الأولى</li><li>النقطة الثانية</li><li>النقطة الثالثة</li></ul></div>',
    note:'<div class="dnote">📌 <b>ملاحظة:</b> اكتب هنا الافتراض أو المصدر أو التنبيه…</div>'
  };"""
assert doc.count(TPL_OLD) == 1
doc = doc.replace(TPL_OLD, TPL_NEW, 1)

BAR_OLD = """    '<button data-t="grp">＋ مجموعة شركاء</button>'+
    '<button data-t="tag">＋ شريك</button>';"""
BAR_NEW = """    '<button data-t="grp">＋ مجموعة شركاء</button>'+
    '<button data-t="tag">＋ شريك</button>'+
    '<button data-t="kpi">＋ مؤشرات</button>'+
    '<button data-t="list">＋ قائمة</button>'+
    '<button data-t="note">＋ ملاحظة</button>'+
    '<button data-t="page" class="bdpage" title="تبويب وصفحة جديدة للمحطة المفتوحة — تغيير بنيوي يُحفظ بتنزيل نسخة HTML">＋ تبويب</button>';"""
assert doc.count(BAR_OLD) == 1
doc = doc.replace(BAR_OLD, BAR_NEW, 1)

BTN_OLD = """    if(b.dataset.t==='tag'){"""
BTN_NEW = """    if(b.dataset.t==='page'){ if(window.DARB&&DARB.addPage)DARB.addPage(); return; }
    if(b.dataset.t==='tag'){"""
assert doc.count(BTN_OLD) == 1
doc = doc.replace(BTN_OLD, BTN_NEW, 1)

# ═══════════ 3. تسجيل المناطق المستحدثة لدى المحرّر ومكدّس التراجع ═══════════
HOOK_ED = """
  /* ‏— تسجيل منطقة تحرير أُنشئت بعد التحميل (تبويب جديد مثلًا) — */
  window.DARB=window.DARB||{};
  window.DARB.addZone=function(z){
    if(!z||!z.dataset.ez||ZONES.indexOf(z)>=0)return;
    ZONES.push(z); ORIG[z.dataset.ez]=snap(z);
    z.addEventListener('input',queue);
    if(editing){
      z.setAttribute('contenteditable','true'); z.setAttribute('spellcheck','false');
      z.querySelectorAll(LOCK).forEach(function(n){n.setAttribute('contenteditable','false');});
    }
  };
  window.DARB.dropZone=function(z){
    var i=ZONES.indexOf(z); if(i>=0)ZONES.splice(i,1);
    if(z&&z.dataset.ez)delete ORIG[z.dataset.ez];
  };

  /* ‏— تبويب يشير إلى صفحة غير موجودة: أُضيف في جلسة سابقة ولم تُنزَّل نسخة — */
  document.querySelectorAll('.tabs .tab[href^="#/"]').forEach(function(a){
    var id='pg-'+a.getAttribute('href').replace(/^#\//,'').replace(/\//g,'-');
    if(!document.getElementById(id))a.remove();
  });
})();
</script>"""
ED_TAIL = """})();
</script>"""
i = doc.index('<script id="editor-js">')
j = doc.index(ED_TAIL, i) + len(ED_TAIL)
doc = doc[:j - len(ED_TAIL)] + HOOK_ED + doc[j:]

HOOK_UN = """
  /* ‏— ضمّ المناطق المستحدثة إلى مكدّس التراجع — */
  window.DARB=window.DARB||{};
  var prevAdd=window.DARB.addZone, prevDrop=window.DARB.dropZone;
  window.DARB.addZone=function(z){
    if(prevAdd)prevAdd(z);
    if(!z||!z.dataset.ez||ZONES.indexOf(z)>=0)return;
    ZONES.push(z); LAST[z.dataset.ez]=snap(z);
    z.addEventListener('input',function(){clearTimeout(timer);timer=setTimeout(commit,700);});
  };
  window.DARB.dropZone=function(z){
    if(prevDrop)prevDrop(z);
    var i=ZONES.indexOf(z); if(i>=0)ZONES.splice(i,1);
    if(z&&z.dataset.ez)delete LAST[z.dataset.ez];
  };
  /* ‏— تغيير بنيوي (إضافة تبويب أو حذفه) يبدأ سجل تراجع جديدًا، لأن التبويب
       الواحد يظهر في كل صفحات المحطة فلا يصحّ التراجع عنه في صفحة دون أخرى — */
  window.DARB.rebase=function(){
    ZONES.forEach(function(z){LAST[z.dataset.ez]=snap(z);});
    undoS.length=0; redoS.length=0; paint();
  };
})();
</script>"""
i = doc.index('<script id="undo-js">')
j = doc.index(ED_TAIL, i) + len(ED_TAIL)
doc = doc[:j - len(ED_TAIL)] + HOOK_UN + doc[j:]

# ═══════════ 4. طبقة «تعديل كل شيء» ═══════════
CSS = """
<style id="fulledit-css">
/* ── حذف الأعمدة ── */
html.editing #pages table thead th{position:relative;padding-inline-start:20px}
.bdcolx{position:absolute;inset-inline-start:3px;inset-block-start:50%;transform:translateY(-50%);
  width:15px;height:15px;border-radius:50%;background:rgba(255,255,255,.22);border:1px solid rgba(255,255,255,.5);
  color:#fff;font-size:11px;font-weight:800;line-height:13px;text-align:center;cursor:pointer;opacity:0;
  transition:.12s;user-select:none;-webkit-user-select:none}
html.editing th:hover .bdcolx{opacity:1}
.bdcolx:hover{background:#C0503A;border-color:#C0503A}
/* ── إعادة تسمية العناصر المقفلة ── */
html.editing .tabs .tab,html.editing .pgnav a,html.editing .stationbar .chip{position:relative}
html.editing .tabs .tab::after,html.editing .pgnav a:not(.hb)::after,
html.editing .stationbar .chip::after{content:'✎';position:absolute;inset-inline-end:2px;inset-block-start:-7px;
  font-size:9.5px;opacity:0;transition:.12s;pointer-events:none}
html.editing .tabs .tab:hover::after,html.editing .pgnav a:hover::after,
html.editing .stationbar .chip:hover::after{opacity:.75}
html.editing .tabs .tab{padding-inline-end:16px}
/* ── حذف تبويب ── */
.bdtabx{display:inline-block;margin-inline-start:5px;width:14px;height:14px;border-radius:50%;
  background:#FBF0ED;border:1px solid #E3BEB4;color:#A6432E;font-size:10px;font-weight:800;
  line-height:12px;text-align:center;cursor:pointer;vertical-align:middle;opacity:0;transition:.12s}
html.editing .tab:hover .bdtabx{opacity:1}
.bdtabx:hover{background:#C0503A;color:#fff;border-color:#C0503A}
#bdbar .bdpage{background:#FDEEE2;border-color:#F5CBA8;color:#B4500F;font-weight:700}
</style>
"""

JS = r"""
<script id="fulledit-js">
/* ═══ تعديل كل شيء: أعمدة · تسميات مقفلة · تبويبات كاملة ═══
   الجزر المقفلة (التبويبات وروابط التنقّل والرقاقات) تبقى مقفلة أمام الكتابة
   المباشرة حتى لا ينكسر التنقّل، لكنها تُعاد تسميتها بنقرة مزدوجة.        */
(function(){
  var root=document.documentElement;
  var editing=function(){return root.classList.contains('editing');};
  function fire(el){
    var z=el&&el.closest&&el.closest('[data-ez]');
    if(z)z.dispatchEvent(new Event('input',{bubbles:true}));
  }

  /* ─── حذف أي عمود ─── */
  function colChrome(){
    document.querySelectorAll('.bdcolx').forEach(function(n){n.remove();});
    if(!editing())return;
    document.querySelectorAll('[data-ez] table thead th').forEach(function(th){
      if(th.querySelector('.bdcolx'))return;
      var x=document.createElement('span');
      x.className='bdcolx'; x.setAttribute('data-builder',''); x.contentEditable='false';
      x.title='حذف هذا العمود'; x.textContent='×';
      th.appendChild(x);
    });
  }
  document.addEventListener('click',function(e){
    var x=e.target.closest&&e.target.closest('.bdcolx'); if(!x)return;
    e.preventDefault(); e.stopPropagation();
    var th=x.closest('th'), tbl=th.closest('table');
    var i=[].indexOf.call(th.parentNode.cells,th);
    if(!confirm('حذف هذا العمود من كل صفوف الجدول؟'))return;
    [].slice.call(tbl.rows).forEach(function(r){ if(r.cells[i])r.deleteCell(i); });
    fire(tbl); colChrome();
  },true);

  /* ─── إعادة تسمية التبويبات وروابط التنقّل والرقاقات ─── */
  function labelOf(el){
    if(el.matches('.chip'))return el.querySelector('.nm')||el;
    return el;
  }
  function textOf(el){
    var n=labelOf(el), extra=n.querySelector('.tcount, .code');
    var t=n.textContent;
    if(extra)t=t.replace(extra.textContent,'');
    return t.trim();
  }
  function rename(el,v){
    var n=labelOf(el), extra=n.querySelector('.tcount, .code');
    n.textContent=v+(extra?' ':'');
    if(extra)n.appendChild(extra);
    fire(n);
  }
  document.addEventListener('dblclick',function(e){
    if(!editing())return;
    var el=e.target.closest&&e.target.closest('.tabs .tab, .pgnav a, .stationbar .chip');
    if(!el)return;
    e.preventDefault(); e.stopPropagation();
    var v=prompt('الاسم الجديد:',textOf(el));
    if(v==null)return; v=v.trim(); if(!v)return;
    var href=el.getAttribute&&el.getAttribute('href');
    var all=(el.classList.contains('tab')&&href)
      ? [].slice.call(document.querySelectorAll('.tabs .tab[href="'+href+'"]'))
      : [el];
    all.forEach(function(t){rename(t,v);});
  },true);

  /* قائمة المحطات المنسدلة — نقرة مزدوجة تعيد تسمية الخيار المحدَّد */
  document.addEventListener('dblclick',function(e){
    if(!editing())return;
    var s=e.target.closest&&e.target.closest('.pgnav select'); if(!s)return;
    e.preventDefault(); e.stopPropagation();
    var o=s.options[s.selectedIndex]; if(!o)return;
    var v=prompt('الاسم الجديد لهذه المحطة في القائمة:',o.textContent);
    if(v==null||!v.trim())return;
    var val=o.value;
    document.querySelectorAll('.pgnav select option').forEach(function(x){
      if(x.value===val){x.textContent=v.trim(); fire(x);}
    });
  },true);

  /* ─── تبويب/صفحة جديدة ─── */
  function stationOf(pv){ var m=/^pg-([A-Za-z]{2}\d+)/.exec(pv.id||''); return m?m[1]:null; }
  function openPage(){ return document.querySelector('.pgview:not([hidden])'); }

  function addPage(){
    var pv=openPage();
    var code=pv&&stationOf(pv);
    if(!code){ alert('افتح صفحة إحدى المحطات أولًا، ثم أضف التبويب.'); return; }
    var name=prompt('اسم التبويب الجديد:','تبويب جديد');
    if(name==null||!name.trim())return;
    name=name.trim();
    var slug='x'+Math.random().toString(36).slice(2,7);
    var href='#/'+code+'/'+slug, id='pg-'+code+'-'+slug;
    var base=(pv.dataset.title||code).split(' · ')[0];

    var page=document.createElement('div');
    page.className='pgview'; page.id=id; page.hidden=true;
    page.setAttribute('data-ez','zx'+slug);
    page.setAttribute('spellcheck','false');
    page.setAttribute('data-title',base+' · '+name);
    var nav=pv.querySelector('.pgnav'), tabs=pv.querySelector('.tabs'),
        mini=pv.querySelector('.mini-head');
    page.innerHTML=(nav?nav.outerHTML:'')+(tabs?tabs.outerHTML:'')+(mini?mini.outerHTML:'')+
      '<div class="sec-h"><h2>'+name+'</h2><span>وصف مختصر — عدّله</span></div>'+
      '<div class="card"><div class="ct"><h3>عنوان البطاقة</h3>'+
      '<div class="leg">ملاحظة جانبية</div></div>'+
      '<p style="font-size:13px;color:var(--ink2);line-height:1.8;margin-top:6px">'+
      'اكتب المحتوى هنا، أو أضف جدولًا أو مؤشرات من الشريط السفلي…</p></div>'+
      '<div class="pgnav" style="margin-top:4px"><div class="nvl">'+
      '<a class="hb" href="#/">⌂ جميع المحطات</a></div></div>';

    var last=document.querySelectorAll('.pgview[id^="pg-'+code+'"]');
    last=last[last.length-1];
    last.parentNode.insertBefore(page,last.nextSibling);

    document.querySelectorAll('.pgview[id^="pg-'+code+'"] .tabs').forEach(function(bar){
      var a=document.createElement('a');
      a.className='tab'; a.setAttribute('href',href); a.textContent=name;
      bar.appendChild(a);
    });
    page.querySelectorAll('.tabs .tab').forEach(function(a){
      a.classList.toggle('on',a.getAttribute('href')===href);
    });
    if(window.DARB&&DARB.addZone)DARB.addZone(page);
    if(window.DARB&&DARB.rebase)DARB.rebase();
    tabChrome(); colChrome();
    location.hash=href;
  }

  /* ─── حذف تبويب مع صفحته ─── */
  function tabChrome(){
    document.querySelectorAll('.bdtabx').forEach(function(n){n.remove();});
    if(!editing())return;
    document.querySelectorAll('.tabs .tab').forEach(function(a){
      if(a.querySelector('.bdtabx'))return;
      var x=document.createElement('b');
      x.className='bdtabx'; x.setAttribute('data-builder',''); x.contentEditable='false';
      x.title='حذف هذا التبويب وصفحته'; x.textContent='×';
      a.appendChild(x);
    });
  }
  document.addEventListener('click',function(e){
    var x=e.target.closest&&e.target.closest('.bdtabx'); if(!x)return;
    e.preventDefault(); e.stopPropagation();
    var a=x.closest('.tab'), href=a.getAttribute('href');
    var bars=document.querySelectorAll('.tabs .tab[href="'+href+'"]');
    var pid='pg-'+href.replace(/^#\//,'').replace(/\//g,'-');
    var page=document.getElementById(pid);
    if(!confirm('حذف التبويب «'+a.textContent.replace('×','').trim()+'» وصفحته كاملة؟'))return;
    var here=(location.hash===href);
    bars.forEach(function(t){var z=t.closest('[data-ez]');t.remove();fire(z);});
    if(page){ if(window.DARB&&DARB.dropZone)DARB.dropZone(page); page.remove(); }
    if(window.DARB&&DARB.rebase)DARB.rebase();
    if(here)location.hash='#/'+(/^pg-([A-Za-z]{2}\d+)/.exec(pid)||[])[1];
  },true);

  window.DARB=window.DARB||{};
  window.DARB.addPage=addPage;

  function chrome(){ colChrome(); tabChrome(); }
  new MutationObserver(chrome).observe(root,{attributes:true,attributeFilter:['class']});
  window.addEventListener('hashchange',function(){setTimeout(chrome,0);});
  chrome();
})();
</script>
"""

doc = doc.replace("</head>", CSS + "</head>", 1)
doc = doc.replace("</body>", JS + "</body>", 1)
doc = re.sub(r'data-docid="[^"]*"', 'data-docid="darb-5st-full-v1"', doc, count=1)
open(OUT, "w", encoding="utf-8").write(doc)

print("تم · الحجم:", round(len(doc.encode()) / 1024), "KB · مناطق التحرير:",
      len(re.findall(r'data-ez="', doc)))
