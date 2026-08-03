# -*- coding: utf-8 -*-
"""يوسّع وضع التحرير: سحب وإفلات للترتيب، وإضافة أقسام وجداول وشركاء، وحذفها."""
import re

SRC = OUT = "/home/user/-/darb-five-stations-analysis.html"
s = open(SRC, encoding="utf-8").read()

# ═══════════ 1. ترقيع سكربت المحرّر: تجاهل عناصر البنّاء في الحفظ والتصدير ═══════════
old_snap = """  function snap(z){
    var c=z.cloneNode(true);
    c.querySelectorAll('[contenteditable]').forEach(function(n){n.removeAttribute('contenteditable');});
    c.querySelectorAll('[spellcheck]').forEach(function(n){n.removeAttribute('spellcheck');});
    return c.innerHTML;
  }"""
new_snap = """  function snap(z){
    var c=z.cloneNode(true);
    c.querySelectorAll('[data-builder]').forEach(function(n){n.remove();});
    c.querySelectorAll('[data-bddrag]').forEach(function(n){n.removeAttribute('data-bddrag');});
    c.querySelectorAll('[contenteditable]').forEach(function(n){n.removeAttribute('contenteditable');});
    c.querySelectorAll('[spellcheck]').forEach(function(n){n.removeAttribute('spellcheck');});
    return c.innerHTML;
  }"""
assert old_snap in s
s = s.replace(old_snap, new_snap, 1)

old_exp = """    var b2=doc.querySelector('#edbar');if(b2)b2.remove();"""
new_exp = """    var b2=doc.querySelector('#edbar');if(b2)b2.remove();
    doc.querySelectorAll('[data-builder]').forEach(function(n){n.remove();});
    doc.querySelectorAll('[data-bddrag]').forEach(function(n){n.removeAttribute('data-bddrag');});"""
assert old_exp in s
s = s.replace(old_exp, new_exp, 1)

# ═══════════ 2. أنماط البنّاء ═══════════
CSS = """
<style id="builder-css">
/* ── أدوات البناء داخل وضع التحرير ── */
#bdbar{position:fixed;inset-block-end:16px;inset-inline-end:16px;z-index:200;display:none;gap:7px;
  align-items:center;background:var(--bgray);border-radius:14px;padding:8px 10px;flex-wrap:wrap;
  box-shadow:0 6px 26px rgba(61,61,61,.24);max-width:calc(100vw - 32px)}
html.editing #bdbar{display:flex}
#bdbar b{font-size:11px;color:#CFD0D2;font-weight:600;margin-inline-end:2px}
#bdbar button{font-family:inherit;font-size:12.5px;border:1px solid rgba(255,255,255,.22);
  background:rgba(255,255,255,.08);color:#fff;border-radius:9px;padding:6px 11px;cursor:pointer;
  transition:.14s;white-space:nowrap}
#bdbar button:hover{background:var(--orange);border-color:var(--orange)}

html.editing [data-ez]>*,html.editing .agrid>*,html.editing .pgrid>*,
html.editing .siggrid>*,html.editing .swot>*{position:relative}
.bdtb{position:absolute;inset-block-start:-13px;inset-inline-start:10px;z-index:30;display:flex;gap:4px;
  background:#fff;border:1px solid var(--line2);border-radius:9px;padding:3px 5px;
  box-shadow:0 3px 12px rgba(61,61,61,.16);opacity:0;transition:opacity .12s;
  user-select:none;-webkit-user-select:none}
html.editing *:hover>.bdtb,.bdtb:hover{opacity:1}
.bdtb button{font-family:inherit;font-size:11px;border:1px solid var(--line2);background:#FBF9F5;
  color:var(--ink2);border-radius:6px;padding:2px 7px;cursor:pointer;line-height:1.7}
.bdtb button:hover{border-color:var(--orange);color:var(--ink)}
.bdtb .bdh{cursor:grab;font-size:13px;letter-spacing:-1px;padding:2px 6px}
.bdtb .bdh:active{cursor:grabbing}
.bdtb .bdd:hover{background:#FBF0ED;border-color:#C0503A;color:#A6432E}
[data-bddrag]{opacity:.4;outline:2px dashed var(--orange);outline-offset:4px;pointer-events:none}
body[data-bddragging]{user-select:none;-webkit-user-select:none;cursor:grabbing}
.bdtb .bdh{touch-action:none}
html.editing .bdover{outline:2px solid var(--orange);outline-offset:4px;border-radius:10px}

.bdx{display:inline-block;margin-inline-start:6px;color:#C0503A;cursor:pointer;font-weight:800;
  font-size:13px;line-height:1;user-select:none;-webkit-user-select:none}
.bdx:hover{color:#8E2F1D}
.bdaddtag{font-family:inherit;cursor:pointer;border-style:dashed !important;color:var(--orange) !important;
  border-color:var(--orange) !important;background:#FFF7EF !important}
.bdnew{animation:bdin .5s ease}
@keyframes bdin{from{background:#FFF1E2}to{background:transparent}}
@media print{#bdbar,.bdtb,.bdx,.bdaddtag{display:none !important}}
</style>
"""

# ═══════════ 3. سكربت البنّاء ═══════════
JS = r"""
<script id="builder-js">
/* ═══ أدوات البناء: سحب وإفلات · إضافة قسم/جدول/شريك · حذف ═══
   يعمل فقط داخل وضع التحرير، ولا يترك أثرًا في النسخة المحفوظة أو المنزَّلة
   لأن كل عناصره تحمل data-builder ويُزيلها المحرّر عند الحفظ والتصدير.      */
(function(){
  var root=document.documentElement;
  var LOCK='.pgnav,.tabs,.cmpbar,.dimchips,#cmpOut,#edbar,#bdbar,script,style';
  var dragEl=null,lastZone=null,lastBlock=null;

  var editing=function(){return root.classList.contains('editing');};
  var zones=function(){return [].slice.call(document.querySelectorAll('[data-ez]'));};
  var seen=function(el){return !!(el&&(el.offsetParent||el.getClientRects().length));};

  function fire(el){
    var z=el&&el.closest&&el.closest('[data-ez]');
    if(z)z.dispatchEvent(new Event('input',{bubbles:true}));
  }
  function isBlock(n){
    if(!n||n.nodeType!==1||n.hasAttribute('data-builder'))return false;
    if(n.matches(LOCK)||n.closest('[data-builder]'))return false;
    var p=n.parentNode;
    return !!(p&&p.nodeType===1&&(p.hasAttribute('data-ez')||
           p.matches('.agrid,.pgrid,.siggrid,.swot')))&&!!n.closest('[data-ez]');
  }
  function blockOf(n){
    while(n&&n!==document.body){ if(isBlock(n))return n; n=n.parentNode; }
    return null;
  }

  /* ── حقن المقابض وأزرار الكتل ── */
  function chrome(){
    strip();
    if(!editing())return;
    zones().forEach(function(z){
      /* المرشّحون فقط: أبناء المنطقة وأبناء الشبكات — لا كل الشجرة */
      var cands=[].slice.call(z.children);
      z.querySelectorAll('.agrid,.pgrid,.siggrid,.swot').forEach(function(g){
        cands=cands.concat([].slice.call(g.children));
      });
      cands.forEach(function(n){
        if(!isBlock(n)||n.querySelector(':scope>.bdtb'))return;
        var tb=document.createElement('div');
        tb.className='bdtb'; tb.setAttribute('data-builder',''); tb.contentEditable='false';
        var h='<button class="bdh" title="اسحب لتغيير الترتيب">⠿</button>';
        if(n.querySelector('table'))h+='<button data-a="row">＋ صف</button><button data-a="col">＋ عمود</button>';
        if(n.querySelector('.ptags'))h+='<button data-a="tag">＋ شريك</button>';
        h+='<button data-a="dup">تكرار</button><button data-a="del" class="bdd">حذف</button>';
        tb.innerHTML=h;
        n.appendChild(tb);
      });
      z.querySelectorAll('.ptag').forEach(function(t){
        if(t.classList.contains('bdaddtag')||t.querySelector('.bdx'))return;
        var x=document.createElement('b');
        x.className='bdx'; x.setAttribute('data-builder',''); x.contentEditable='false';
        x.title='حذف الشريك'; x.textContent='×';
        t.appendChild(x);
      });
      z.querySelectorAll('.ptags').forEach(function(g){
        if(g.querySelector('.bdaddtag'))return;
        var a=document.createElement('button');
        a.className='ptag bdaddtag'; a.setAttribute('data-builder',''); a.contentEditable='false';
        a.textContent='＋ شريك';
        g.appendChild(a);
      });
    });
  }
  function strip(){
    document.querySelectorAll('[data-builder]').forEach(function(n){
      if(n.id!=='bdbar')n.remove();
    });
    document.querySelectorAll('[data-bddrag]').forEach(function(n){n.removeAttribute('data-bddrag');});
    document.querySelectorAll('.bdover').forEach(function(n){n.classList.remove('bdover');});
  }

  /* ── السحب والإفلات (pointer events — يعمل داخل المناطق القابلة للتحرير وعلى اللمس) ── */
  var drag=null;
  document.addEventListener('pointerdown',function(e){
    if(!editing())return;
    var h=e.target.closest&&e.target.closest('.bdh'); if(!h)return;
    e.preventDefault(); e.stopPropagation();
    var el=h.closest('.bdtb').parentNode;
    drag={el:el,zone:el.closest('[data-ez]'),h:h,id:e.pointerId};
    el.setAttribute('data-bddrag','');
    document.body.setAttribute('data-bddragging','');
    try{h.setPointerCapture(e.pointerId);}catch(_){}
  },true);

  document.addEventListener('pointermove',function(e){
    if(!drag)return;
    e.preventDefault();
    /* تمرير تلقائي قرب حواف الشاشة */
    if(e.clientY<90)window.scrollBy(0,-18);
    else if(e.clientY>window.innerHeight-90)window.scrollBy(0,18);
    var t=blockOf(document.elementFromPoint(e.clientX,e.clientY));
    if(!t||t===drag.el)return;
    if(t.closest('[data-ez]')!==drag.zone)return;      /* داخل نفس المنطقة فقط */
    var r=t.getBoundingClientRect();
    var after=(e.clientY-r.top)>r.height/2;
    t.parentNode.insertBefore(drag.el,after?t.nextSibling:t);
  },true);

  function endDrag(){
    if(!drag)return;
    drag.el.removeAttribute('data-bddrag');
    document.body.removeAttribute('data-bddragging');
    try{drag.h.releasePointerCapture(drag.id);}catch(_){}
    fire(drag.el); drag=null;
  }
  document.addEventListener('pointerup',endDrag,true);
  document.addEventListener('pointercancel',endDrag,true);

  /* ── تتبّع آخر منطقة/كتلة لمس المستخدم ── */
  document.addEventListener('click',function(e){
    var z=e.target.closest&&e.target.closest('[data-ez]');
    if(z){lastZone=z; var b=blockOf(e.target); if(b)lastBlock=b;}
  },true);

  /* ── أزرار الكتل ── */
  document.addEventListener('click',function(e){
    if(!editing())return;
    var x=e.target.closest&&e.target.closest('.bdx');
    if(x){e.preventDefault();e.stopPropagation();var t=x.parentNode;var z=t.closest('[data-ez]');t.remove();fire(z);return;}
    var add=e.target.closest&&e.target.closest('.bdaddtag');
    if(add){e.preventDefault();e.stopPropagation();newTag(add.parentNode);return;}
    var btn=e.target.closest&&e.target.closest('.bdtb button[data-a]');
    if(!btn)return;
    e.preventDefault(); e.stopPropagation();
    var blk=btn.closest('.bdtb').parentNode, a=btn.dataset.a;
    if(a==='del'){
      if(!confirm('حذف هذا العنصر نهائيًا من الصفحة؟'))return;
      var z=blk.closest('[data-ez]'); blk.remove(); fire(z); return;
    }
    if(a==='dup'){
      var c=blk.cloneNode(true);
      c.querySelectorAll('[data-builder]').forEach(function(n){n.remove();});
      c.removeAttribute('data-bddrag');
      blk.parentNode.insertBefore(c,blk.nextSibling);
      c.classList.add('bdnew'); chrome(); fire(c); return;
    }
    if(a==='tag'){ newTag(blk.querySelector('.ptags')); return; }
    var tbl=blk.querySelector('table'); if(!tbl)return;
    if(a==='row'){
      var body=tbl.tBodies[0]||tbl, last=body.rows[body.rows.length-1];
      var tr=document.createElement('tr'), n=last?last.cells.length:3;
      for(var i=0;i<n;i++){var td=document.createElement('td');td.textContent='—';tr.appendChild(td);}
      body.appendChild(tr); tr.classList.add('bdnew'); fire(tr);
      caret(tr.cells[0]);
    }
    if(a==='col'){
      [].forEach.call(tbl.rows,function(r){
        var head=r.parentNode.tagName==='THEAD'||r.cells[0].tagName==='TH';
        var c=document.createElement(head?'th':'td');
        c.textContent=head?'عمود جديد':'—'; r.appendChild(c);
      });
      fire(tbl);
    }
  },true);

  function newTag(group){
    if(!group)return;
    var t=document.createElement('span');
    t.className='ptag bdnew'; t.textContent='شريك جديد';
    var anchor=group.querySelector('.bdaddtag');
    group.insertBefore(t,anchor||null);
    chrome(); fire(t); caret(t,true);
  }
  function caret(el,selectAll){
    el.scrollIntoView({block:'nearest',behavior:'smooth'});
    var r=document.createRange(), sel=window.getSelection();
    r.selectNodeContents(el);
    if(!selectAll)r.collapse(true);
    sel.removeAllRanges(); sel.addRange(r);
  }

  /* ── شريط الإضافة ── */
  var TPL={
    sec:'<div class="sec-h"><h2>عنوان القسم الجديد</h2><span>وصف مختصر — عدّله</span></div>'+
        '<div class="card"><div class="ct"><h3>عنوان البطاقة</h3><div class="leg">ملاحظة جانبية</div></div>'+
        '<p style="font-size:13px;color:var(--ink2);line-height:1.8;margin-top:6px">اكتب المحتوى هنا…</p></div>',
    tbl:'<div class="ntable"><div class="tscroll"><table>'+
        '<thead><tr><th>العمود الأول</th><th>العمود الثاني</th><th>العمود الثالث</th></tr></thead>'+
        '<tbody><tr><td>—</td><td>—</td><td>—</td></tr><tr><td>—</td><td>—</td><td>—</td></tr>'+
        '<tr><td>—</td><td>—</td><td>—</td></tr></tbody></table></div></div>',
    card:'<div class="card"><div class="ct"><h3>عنوان البطاقة</h3><div class="leg">ملاحظة</div></div>'+
        '<p style="font-size:13px;color:var(--ink2);line-height:1.8;margin-top:6px">اكتب هنا…</p></div>',
    grp:'<div class="card"><div class="ct"><h3>مجموعة شركاء جديدة</h3><div class="leg">أضف الوحدات</div></div>'+
        '<div class="ptags"><span class="ptag">شريك 1</span><span class="ptag">شريك 2</span></div></div>'
  };
  function target(){
    if(lastZone&&lastZone.isConnected&&seen(lastZone))return lastZone;
    var pv=document.querySelector('.pgview:not([hidden])');          /* الصفحة المفتوحة أولًا */
    if(pv){var z=pv.matches('[data-ez]')?pv:pv.querySelector('[data-ez]');if(z)return z;}
    var hub=document.querySelector('#hub [data-ez]');                /* ثم الصفحة الرئيسية */
    if(hub&&seen(hub))return hub;
    var v=zones().filter(seen); return v[0]||zones()[0];
  }
  function insert(html){
    var z=target(); if(!z)return;
    var tmp=document.createElement('div'); tmp.innerHTML=html;
    var nodes=[].slice.call(tmp.childNodes), first=nodes[0];
    var anchor=(lastBlock&&lastBlock.isConnected&&lastBlock.closest('[data-ez]')===z)
      ? lastBlock.nextSibling
      : (function(){var n=z.querySelectorAll(':scope>.pgnav');return n.length?n[n.length-1]:null;})();
    nodes.forEach(function(n){ anchor?z.insertBefore(n,anchor):z.appendChild(n); });
    chrome(); fire(z);
    if(first&&first.nodeType===1){
      first.classList.add('bdnew');
      var h=first.querySelector('h2,h3')||first;
      caret(h,true);
    }
  }

  var bar=document.createElement('div');
  bar.id='bdbar'; bar.setAttribute('data-builder',''); bar.contentEditable='false';
  bar.innerHTML='<b>إضافة:</b>'+
    '<button data-t="sec">＋ قسم</button>'+
    '<button data-t="tbl">＋ جدول</button>'+
    '<button data-t="card">＋ بطاقة</button>'+
    '<button data-t="grp">＋ مجموعة شركاء</button>'+
    '<button data-t="tag">＋ شريك</button>';
  document.body.appendChild(bar);
  bar.addEventListener('click',function(e){
    var b=e.target.closest('button[data-t]'); if(!b)return;
    e.preventDefault();
    if(b.dataset.t==='tag'){
      var z=target(), gs=z?z.querySelectorAll('.ptags'):[];
      if(gs.length)newTag(gs[gs.length-1]); else insert(TPL.grp);
      return;
    }
    insert(TPL[b.dataset.t]);
  });

  /* ── تتبّع تشغيل/إيقاف وضع التحرير ── */
  new MutationObserver(chrome).observe(root,{attributes:true,attributeFilter:['class']});
  chrome();
})();
</script>
"""

s = s.replace("</head>", CSS + "</head>", 1)
s = s.replace('<script id="editor-js">', JS.strip() + "\n<script id=\"editor-js\">", 1)
s = re.sub(r'data-docid="[^"]*"', 'data-docid="darb-5st-builder-v1"', s, count=1)
open(OUT, "w", encoding="utf-8").write(s)
print("تم · الحجم:", round(len(s.encode()) / 1024), "KB")
