# -*- coding: utf-8 -*-
"""Every cell on page one and page three must take a value, keep it, and let
the other pages see it."""
import json
from playwright.sync_api import sync_playwright
CHROME='/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
D='/tmp/claude-0/-home-user--/b2086a51-b39c-5c55-b4a9-aeba6ad9f224/scratchpad/'

def edit(pg, sel, text):
    pg.evaluate("""([s,t])=>{const e=document.querySelector(s); e.focus();
      const r=document.createRange(); r.selectNodeContents(e);
      getSelection().removeAllRanges(); getSelection().addRange(r);
      document.execCommand('insertText', false, t); e.blur();}""", [sel, text])
    pg.wait_for_timeout(350)

with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path=CHROME,args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1280,'height':1000})
    pg=ctx.new_page(); errs=[]
    pg.on('pageerror',lambda e:errs.append('page:'+str(e)))
    pg.on('console',lambda m:errs.append('console:'+m.text) if m.type=='error' else None)
    pg.goto('file://'+D+'campaigns_editable.html',wait_until='load')
    pg.wait_for_timeout(900)
    out={}
    pg.click('.tab[data-tab="sum"]'); pg.wait_for_timeout(450)
    out['sum_editable_cells']=pg.eval_on_selector_all('#sumTable [data-f]','ns=>ns.length')
    out['sum_fields']=pg.eval_on_selector_all('#sumTable tr[data-code] [data-f]',
                                              'ns=>ns.slice(0,11).map(n=>n.dataset.f)')
    R='#sumTable tr[data-code="CMP-2026-05"] '
    edit(pg, R+'[data-f="name"]', 'اسم معدّل من الملخّص')
    edit(pg, R+'[data-f="goal"]', 'هدف معدّل')
    edit(pg, R+'[data-f="budget"]', '31500')
    edit(pg, R+'[data-f="stations"]', 'MK007 · MK019')
    edit(pg, R+'[data-f="partners"]', 'واش واي، شريك جديد')
    edit(pg, R+'[data-f="start"]', '2026-09-18')
    edit(pg, R+'[data-f="dur"]', 'أربعة أيام')
    edit(pg, R+'[data-f="status"]', 'مؤجّلة')
    saved=pg.evaluate("""()=>{const c=JSON.parse(localStorage.getItem('darb-campaigns-v1')||'[]')
      .find(x=>x.code==='CMP-2026-05'); return c;}""")
    out['saved']={k:saved.get(k) for k in ('name','goal','budget','stations','start','ovr')}
    out['saved_partners']=[p['name'] for p in saved.get('partners') or []]
    out['sum_kpi']=pg.eval_on_selector('#sumKpi','n=>n.innerText.replace(/\\n+/g," · ")')

    # page 2 must show the same edit
    pg.click('.tab[data-tab="camp"]'); pg.wait_for_timeout(400)
    out['page2_sees_name']='اسم معدّل من الملخّص' in pg.eval_on_selector('#list','n=>n.innerText')

    # page 3 cells
    pg.click('.tab[data-tab="wash"]'); pg.wait_for_timeout(450)
    out['plan_editable_cells']=pg.eval_on_selector_all('#wTable [data-f]','ns=>ns.length')
    out['plan_fields']=pg.eval_on_selector_all('#wTable tr[data-code] [data-f]',
                                               'ns=>ns.slice(0,7).map(n=>n.dataset.f)')
    W='#wTable tr[data-code="CMP-2026-07"] '
    edit(pg, W+'[data-f="name"]', 'حملة أكتوبر المعدّلة')
    edit(pg, W+'[data-f="month"]', 'أكتوبر — مؤكد')
    edit(pg, W+'[data-f="left"]', 'يُراجع لاحقًا')
    saved7=pg.evaluate("""()=>JSON.parse(localStorage.getItem('darb-campaigns-v1')||'[]')
      .find(x=>x.code==='CMP-2026-07')""")
    out['plan_saved']={'name':saved7.get('name'),'ovr':saved7.get('ovr')}

    # survives a reload, and the overrides stick
    pg.reload(wait_until='load'); pg.wait_for_timeout(900)
    pg.click('.tab[data-tab="sum"]'); pg.wait_for_timeout(450)
    out['reload_sum_dur']=pg.eval_on_selector('#sumTable tr[data-code="CMP-2026-05"] [data-f="dur"]',
                                              'n=>n.textContent.trim()')
    out['reload_sum_status']=pg.eval_on_selector('#sumTable tr[data-code="CMP-2026-05"] [data-f="status"]',
                                                 'n=>n.textContent.trim()')
    pg.click('.tab[data-tab="wash"]'); pg.wait_for_timeout(450)
    out['reload_plan_month']=pg.eval_on_selector('#wTable tr[data-code="CMP-2026-07"] [data-f="month"]',
                                                 'n=>n.textContent.trim()')
    out['reload_plan_left']=pg.eval_on_selector('#wTable tr[data-code="CMP-2026-07"] [data-f="left"]',
                                                'n=>n.textContent.trim()')
    # a duplicate code is refused
    pg.click('.tab[data-tab="sum"]'); pg.wait_for_timeout(400)
    edit(pg, '#sumTable tr[data-code="CMP-2026-05"] [data-f="code"]', 'CMP-2026-01')
    out['dupe_refused']=pg.evaluate("""()=>JSON.parse(localStorage.getItem('darb-campaigns-v1')||'[]')
      .filter(x=>x.code==='CMP-2026-01').length""")==1
    out['errors']=errs
    print(json.dumps(out,ensure_ascii=False,indent=1))
    b.close()
