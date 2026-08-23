# -*- coding: utf-8 -*-
"""Six regions, region-level analytics on the front, a blank offers table last,
and the same editing tools — with a clean file per region."""
import base64, json
from playwright.sync_api import sync_playwright
CHROME='/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
D='/tmp/claude-0/-home-user--/b2086a51-b39c-5c55-b4a9-aeba6ad9f224/scratchpad/'
open(D+'swap.png','wb').write(base64.b64decode(
 'iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAYAAABytg0kAAAAFUlEQVR4nGP8z8Dwn4GBgYGJAQkMLgAAtjEDxRCsSDsAAAAASUVORK5CYII='))
T='عنوان معدّل'
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path=CHROME,args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1280,'height':950},accept_downloads=True)
    pg=ctx.new_page(); errs=[]
    pg.on('pageerror',lambda e:errs.append('page:'+str(e)))
    pg.on('console',lambda m:errs.append('console:'+m.text) if m.type=='error' else None)
    pg.goto('file:///home/user/-/darb-region-slides.html',wait_until='load')
    pg.wait_for_timeout(900)
    out={}
    out['regions']=pg.eval_on_selector_all('#pick option','ns=>ns.map(n=>n.value)')
    out['labels']=pg.eval_on_selector_all('#pick option','ns=>ns.map(n=>n.textContent.trim())')
    out['slides']=pg.eval_on_selector_all('#deck .pg','ns=>ns.length')
    out['tools']=pg.eval_on_selector_all('.bar button','ns=>ns.map(n=>n.textContent.trim())')
    txt=pg.eval_on_selector('#deck','n=>n.innerText')
    out['region_analytics_first']=pg.eval_on_selector(
        '#deck .pg:nth-of-type(2) .eyebrow','n=>n.textContent.trim()')
    out['has_region_total']='إجمالي المنطقة' in txt
    out['last_is_offers']=pg.eval_on_selector(
        '#deck .pg:last-of-type .eyebrow','n=>n.textContent.trim()')
    out['offer_rows_blank']=pg.eval_on_selector_all(
        '#deck .pg:last-of-type tbody td.fill','ns=>ns.every(n=>n.textContent.trim()==="…")')
    out['offer_row_count']=pg.eval_on_selector_all(
        '#deck .pg:last-of-type tbody tr','ns=>ns.length')
    # per-region numbers must differ
    nums={}
    for r in out['regions']:
        pg.select_option('#pick', r); pg.wait_for_timeout(320)
        nums[r]=pg.eval_on_selector('#deck .cover .fact .v','n=>n.textContent.trim()')
    out['cars_per_region']=nums
    # editing + image swap + add + undo/redo
    pg.select_option('#pick', out['regions'][0]); pg.wait_for_timeout(350)
    pg.click('#edit'); pg.wait_for_timeout(250)
    out['editable']=pg.eval_on_selector('#deck','n=>n.isContentEditable')
    pg.evaluate("""()=>{const h=document.querySelector('#deck h2');h.focus();
      const r=document.createRange();r.selectNodeContents(h);
      getSelection().removeAllRanges();getSelection().addRange(r);}""")
    pg.keyboard.type(T); pg.wait_for_timeout(600)
    out['typed']=pg.eval_on_selector('#deck h2','n=>n.textContent.trim()')==T
    pg.click('#undo'); pg.wait_for_timeout(300)
    out['undo']=pg.eval_on_selector('#deck h2','n=>n.textContent.trim()')!=T
    pg.click('#redo'); pg.wait_for_timeout(300)
    out['redo']=pg.eval_on_selector('#deck h2','n=>n.textContent.trim()')==T
    pg.evaluate("""()=>{const i=document.querySelector('#deck .clips img');
      i.scrollIntoView({block:'center'});
      i.dispatchEvent(new MouseEvent('click',{bubbles:true}));}""")
    pg.wait_for_timeout(350)
    pg.set_input_files('#pickimg', D+'swap.png'); pg.wait_for_timeout(700)
    out['img_swap']=pg.eval_on_selector('#deck .clips img','n=>n.src.indexOf("data:image/png")===0')
    pg.click('#addpg'); pg.wait_for_timeout(400)
    out['added']=pg.eval_on_selector_all('#deck .pg','ns=>ns.length')==out['slides']+1
    pg.reload(wait_until='load'); pg.wait_for_timeout(900)
    out['survives_reload']=T in pg.eval_on_selector('#deck','n=>n.innerText')
    # a clean file per region
    with pg.expect_download() as d: pg.click('#dl')
    dl=d.value; p=D+'rg_'+dl.suggested_filename; dl.save_as(p)
    h=open(p,encoding='utf-8').read()
    css=h.split('<style',1)[1].split('</style>')[0] if '<style' in h else ''
    out['dl_name']=dl.suggested_filename
    out['dl_kb']=round(len(h.encode())/1024)
    out['dl_clean']=('<button' not in h and '<script' not in h and 'class="bar"' not in h)
    out['dl_css_ok']='.pg{' in css
    out['dl_keeps_edit']=T in h
    out['dl_has_offers']='العروض' in h
    out['errors']=errs
    print(json.dumps(out,ensure_ascii=False,indent=1))
    b.close()
