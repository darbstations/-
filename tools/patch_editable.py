# -*- coding: utf-8 -*-
"""Make every cell on the summary and the plan editable, in place.

A cell that maps to a real field writes straight into the campaign, so the
other pages follow it. A cell the page works out for itself — the duration,
the month, the status, what is left after a campaign — keeps whatever is typed
over it as an override on that campaign, otherwise the next redraw would erase
it. Everything is saved the moment the cell is left.
"""
import re
import sys

SRC = sys.argv[1] if len(sys.argv) > 1 else 'hers5.html'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'campaigns_editable.html'
s = open(SRC, encoding='utf-8').read()
n = 0


def sub(old, new, why):
    global s, n
    assert old in s, 'missing: ' + why
    s = s.replace(old, new, 1)
    n += 1


# ---------------------------------------------------------------- 1. الأنماط
sub('.savestate.ok{color:var(--ok)}',
    """.savestate.ok{color:var(--ok)}
[data-f]{outline:none}
td[data-f],span[data-f]{cursor:text}
td[data-f]:hover,span[data-f]:hover{background:color-mix(in srgb,var(--orange-hi) 9%,transparent)}
td[data-f]:focus,span[data-f]:focus{background:var(--ground);
  box-shadow:inset 0 0 0 2px var(--orange-hi);border-radius:4px}
tr.month td[data-f]:hover{background:var(--sand)}
.editnote{font-size:12.5px;color:var(--ink-2);margin:10px 0 0}
.editnote b{color:var(--orange)}""",
    'cell styling')

# --------------------------------------------- 2. القيم المكتوبة فوق المحسوبة
sub('  function durOf(c){',
    """  /* ما تكتبه المستخدمة فوق خانة محسوبة يُحفظ على الحملة، وإلا محاه أول رسم */
  function ovr(c, k){ return (c && c.ovr && c.ovr[k]!=null) ? c.ovr[k] : null; }
  function setOvr(c, k, v){
    c.ovr = c.ovr || {};
    if(v==='' || v==null) delete c.ovr[k]; else c.ovr[k]=v;
  }
  function durTxt(c){ return ovr(c,'dur') || durOf(c); }
  function monthTxt(c){ return ovr(c,'month') || monthLabel(monthKey(c.start)); }
  function statusTxt(c){ var o=ovr(c,'status'); return o || statusOf(c).t; }
  function statusCls(c){ return ovr(c,'status') ? 'soon' : statusOf(c).k; }
  function digits(t){
    var m={'٠':'0','١':'1','٢':'2','٣':'3','٤':'4','٥':'5','٦':'6','٧':'7','٨':'8','٩':'9'};
    return String(t||'').replace(/[٠-٩]/g, function(d){ return m[d]; });
  }
  function numOf(t){ var d=digits(t).replace(/[^0-9.\\-]/g,''); return d===''?0:Number(d); }
  function dateOf(t){
    var d=digits(t).trim().replace(/[^0-9\\-\\/]/g,'').replace(/\\//g,'-');
    return /^\\d{4}-\\d{1,2}-\\d{1,2}$/.test(d)
      ? d.replace(/-(\\d)(?=-|$)/g,'-0$1').replace(/^(\\d{4})-(\\d)-/,'$1-0$2-') : '';
  }
  function durOf(c){""",
    'override helpers')

# ------------------------------------------------- 3. خانات صفحة الملخّص
sub("""      h+='<tr>'+
        '<td class="code">'+esc(c.code)+'</td>'+
        '<td>'+esc(c.name||'')+(c.parent?'<div class="small">ضمن '+esc(c.parent)+'</div>':'')+'</td>'+
        '<td class="small">'+esc(c.start||'—')+'<br>'+esc(c.end||'—')+'</td>'+
        '<td class="small">'+esc(durOf(c))+'</td>'+
        '<td class="small">'+(sts.length?esc(sts.join(' · ')):'—')+'</td>'+
        '<td class="small">'+(pas.length?esc(pas.join('، ')):'—')+'</td>'+
        '<td class="small">'+esc(c.goal||'—')+'</td>'+
        '<td class="small">'+esc(c.target||'—')+'</td>'+
        '<td class="money">'+(Number(c.budget)?money(c.budget):'—')+'</td>'+
        '<td><span class="pill '+s2.k+'">'+s2.t+'</span></td>'+
      '</tr>';""",
"""      h+='<tr data-code="'+esc(c.code)+'">'+
        '<td class="code" data-f="code" contenteditable="true">'+esc(c.code)+'</td>'+
        '<td><span data-f="name" contenteditable="true">'+esc(c.name||'')+'</span>'+
            (c.parent?'<div class="small">ضمن '+esc(c.parent)+'</div>':'')+'</td>'+
        '<td class="small"><span data-f="start" contenteditable="true">'+esc(c.start||'—')+'</span>'+
            '<br><span data-f="end" contenteditable="true">'+esc(c.end||'—')+'</span></td>'+
        '<td class="small" data-f="dur" contenteditable="true">'+esc(durTxt(c))+'</td>'+
        '<td class="small" data-f="stations" contenteditable="true">'+(sts.length?esc(sts.join(' · ')):'—')+'</td>'+
        '<td class="small" data-f="partners" contenteditable="true">'+(pas.length?esc(pas.join('، ')):'—')+'</td>'+
        '<td class="small" data-f="goal" contenteditable="true">'+esc(c.goal||'—')+'</td>'+
        '<td class="small" data-f="target" contenteditable="true">'+esc(c.target||'—')+'</td>'+
        '<td class="money" data-f="budget" contenteditable="true">'+(Number(c.budget)?money(c.budget):'—')+'</td>'+
        '<td><span class="pill '+statusCls(c)+'" data-f="status" contenteditable="true">'+esc(statusTxt(c))+'</span></td>'+
      '</tr>';""",
    'summary cells')

sub("""    $('sumTable').innerHTML=h+'</tbody></table></div>';
  }""",
"""    $('sumTable').innerHTML=h+'</tbody></table></div>'+
      '<p class="editnote">كل خانة في الجدول <b>قابلة للتعديل</b> — اضغط عليها واكتب، '+
      'ثم اخرج منها أو اضغط Enter فتُحفظ وتتحدّث بقية الصفحات.</p>';
  }""",
    'summary hint')

# --------------------------------------------------- 4. خانات صفحة الخطة
sub("""      h+='<tr data-code="'+esc(c.code)+'">'+
        '<td class="code">'+esc(c.code)+'</td>'+
        '<td>'+esc(c.name||'')+'</td>'+
        '<td class="small">'+esc(monthLabel(monthKey(c.start)))+'</td>'+
        '<td class="small">'+esc(c.start||'—')+' ← '+esc(c.end||'—')+'</td>'+""",
"""      h+='<tr data-code="'+esc(c.code)+'">'+
        '<td class="code" data-f="code" contenteditable="true">'+esc(c.code)+'</td>'+
        '<td data-f="name" contenteditable="true">'+esc(c.name||'')+'</td>'+
        '<td class="small" data-f="month" contenteditable="true">'+esc(monthTxt(c))+'</td>'+
        '<td class="small"><span data-f="start" contenteditable="true">'+esc(c.start||'—')+'</span>'+
            ' ← <span data-f="end" contenteditable="true">'+esc(c.end||'—')+'</span></td>'+""",
    'plan cells (head)')

sub("""        '<td class="money w-left">—</td>'+
        '<td><span class="pill '+s3.k+'">'+s3.t+'</span></td>'+""",
"""        '<td class="money w-left" data-f="left" contenteditable="true">—</td>'+
        '<td><span class="pill '+statusCls(c)+'" data-f="status" contenteditable="true">'+esc(statusTxt(c))+'</span></td>'+""",
    'plan cells (tail)')

sub("""    $('wTable').innerHTML=h+'</tbody></table></div>';
    paintPlan();""",
"""    $('wTable').innerHTML=h+'</tbody></table></div>'+
      '<p class="editnote">كل خانة هنا <b>قابلة للتعديل</b> أيضًا — والمحطات والتواريخ '+
      'والأسماء تُحفظ على الحملة نفسها فتظهر في بقية الصفحات.</p>';
    paintPlan();""",
    'plan hint')

# ----- المتبقي المحسوب يحترم ما كُتب فوقه
sub("""      var left=total-run, cell=rows[i].querySelector('.w-left');
      if(cell){ cell.textContent=money(left); cell.className='money w-left'+(left<0?' neg':''); }""",
"""      var left=total-run, cell=rows[i].querySelector('.w-left');
      if(cell && document.activeElement!==cell){
        var o=c?ovr(c,'left'):null;
        cell.textContent=o!=null?o:money(left);
        cell.className='money w-left'+(o==null&&left<0?' neg':'');
      }""",
    'plan running total honours overrides')

# ------------------------------------------------ 5. تطبيق ما كُتب في الخانة
sub("  function renderSummary(){",
"""  /* خانة تُغيّر حقلًا حقيقيًا تكتب في الحملة، وخانة محسوبة تُحفظ كقيمة مكتوبة فوقها */
  function applyCell(c, f, txt){
    txt=(txt||'').replace(/\\s+/g,' ').trim();
    if(txt==='—') txt='';
    if(f==='code'){
      var v=txt.toUpperCase();
      if(!v || v===c.code) return false;
      if(campByCode(v)){ say('الكود '+v+' مستخدم في حملة أخرى.',6000); return false; }
      var old=c.code; c.code=v;
      campaigns.forEach(function(x){ if(x.parent===old) x.parent=v; });
      return true;
    }
    if(f==='name'){ c.name=txt; return true; }
    if(f==='goal'){ c.goal=txt; return true; }
    if(f==='target'){ c.target=txt; return true; }
    if(f==='budget'){ c.budget=numOf(txt); return true; }
    if(f==='start'||f==='end'){
      var d=dateOf(txt);
      if(!d){ say('اكتب التاريخ هكذا: 2026-08-16',6000); return false; }
      c[f]=d;
      if(c.start&&c.end&&c.end<c.start){ say('تاريخ الانتهاء قبل البدء.',6000); }
      return true;
    }
    if(f==='stations'){
      c.stations = txt ? txt.split(/[·،,\\s]+/).map(function(x){ return x.trim().toUpperCase(); })
                            .filter(Boolean) : [];
      return true;
    }
    if(f==='partners'){
      var names = txt ? txt.split(/[،,·]+/).map(function(x){ return x.trim(); }).filter(Boolean) : [];
      var old2 = c.partners || [];
      c.partners = names.map(function(nm, i){
        var keep = old2.filter(function(p){ return p.name===nm; })[0] || old2[i] || {};
        return {name:nm, type:keep.type||'', code:keep.code||'', offer:keep.offer||'',
                old:keep.old||'', newp:keep.newp||'', status:keep.status||'بانتظار الرد'};
      });
      return true;
    }
    setOvr(c, f, txt);          /* dur · month · status · left */
    return true;
  }
  function wireCells(box){
    box.addEventListener('keydown', function(e){
      var cell=e.target.closest('[data-f]'); if(!cell) return;
      if(e.key==='Enter'){ e.preventDefault(); cell.blur(); }
      if(e.key==='Escape'){ e.preventDefault(); renderSummary(); renderWash(); }
    });
    box.addEventListener('focusout', function(e){
      var cell=e.target.closest('[data-f]'); if(!cell) return;
      var row=cell.closest('tr'); if(!row) return;
      var c=campByCode(row.getAttribute('data-code')); if(!c) return;
      if(!applyCell(c, cell.getAttribute('data-f'), cell.textContent)){
        renderSummary(); renderWash(); return;
      }
      stamp(c); persist();
      render(); renderSummary(); renderWash();
      say('حُفظ.',2000);
    });
  }
  function renderSummary(){""",
    'apply + wiring')

sub("  load(); loadExt();",
"""  wireCells($('sumTable'));
  wireCells($('wTable'));
  load(); loadExt();""",
    'wire on boot')

open(OUT, 'w', encoding='utf-8').write(s)
print('patches applied:', n)
print('written:', OUT, len(s) // 1024, 'KB')
