# -*- coding: utf-8 -*-
"""ملف حملة واحدة: يفتح على حملتها وحدها في الصفحات الثلاث، ويحفظ تعديلها،
ويصدّر ملفًا مصوغًا لا خامًا، ولا يمسّ مفتاح السجل الكامل."""
import json
import pathlib
import tempfile
from playwright.sync_api import sync_playwright

PAGE = pathlib.Path('/home/user/-/darb-carwash-campaign.html')
CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
OLDKEY = 'darb-campaigns-v1'
R = {}

with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path=CHROME, args=['--no-sandbox'])
    pg = b.new_page(viewport={'width': 1400, 'height': 950})
    pg.add_init_script("""window.claude={downloads:{save:function(o){
        window.__saved=o; return Promise.resolve(); }}};""")
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(PAGE.as_uri())

    # سجلّها الكامل موجود في نفس المتصفح تحت المفتاح القديم
    pg.evaluate('k => localStorage.setItem(k, JSON.stringify([{code:"CMP-2026-09"},'
                '{code:"CMP-2026-01"}]))', OLDKEY)
    pg.reload()
    pg.wait_for_timeout(800)

    R['title'] = pg.title()
    R['dir'] = pg.eval_on_selector('html', 'e => e.dir')

    # ---- صفحة الحملات
    R['cards'] = pg.eval_on_selector_all('#list article .code', 'ns => ns.map(n => n.textContent)')
    R['kpi_campaigns'] = pg.text_content('#kCamp')

    # ---- صفحة الملخّص
    pg.click('.tab[data-tab="sum"]')
    pg.wait_for_timeout(300)
    R['summary_codes'] = pg.eval_on_selector_all(
        '#sumTable tbody tr:not(.month) td.code', 'ns => ns.map(n => n.textContent)')
    R['summary_partners'] = (pg.eval_on_selector(
        '#sumTable tbody tr:not(.month) td[data-f="partners"]', 'e => e.textContent') or '')[:40]

    # ---- صفحة خطة واش واي
    pg.click('.tab[data-tab="wash"]')
    pg.wait_for_timeout(300)
    R['wash_codes'] = pg.eval_on_selector_all(
        '#wTable tbody tr td.code', 'ns => ns.map(n => n.textContent)')

    # ---- التعديل يُحفظ ويسري على الصفحات
    pg.click('.tab[data-tab="sum"]')
    pg.wait_for_timeout(250)
    pg.eval_on_selector('#sumTable td[data-f="target"]',
                        'e => { e.focus(); e.textContent = "٣٠٠٠ سيارة"; }')
    pg.click('#sumTable h2, #sumTable')
    pg.keyboard.press('Tab')
    pg.wait_for_timeout(700)
    R['saved_target'] = pg.evaluate(
        'k => (JSON.parse(localStorage.getItem(k)||"[]")[0]||{}).target',
        'darb-carwash-campaign-v1')

    # ---- لم يلمس السجل الكامل
    R['old_register_untouched'] = pg.evaluate(
        'k => JSON.parse(localStorage.getItem(k)||"[]").map(c => c.code)', OLDKEY)

    # ---- تصدير HTML مصوغ وفيه حملة واحدة
    pg.click('#btnHtml')
    pg.wait_for_timeout(1000)
    out = pg.evaluate('window.__saved')
    R['export_name'] = out['filename']
    html = out['data']
    R['export_kb'] = len(html) // 1024
    R['export_css_bytes'] = len(html.split('<style', 1)[1].split('</style>', 1)[0]) if '<style' in html else 0
    i = html.index('var SEED = ') + len('var SEED = ')
    R['export_seed'] = [c['code'] for c in json.JSONDecoder().raw_decode(html[i:])[0]]
    R['export_keeps_edit'] = '٣٠٠٠ سيارة' in html

    tmp = pathlib.Path(tempfile.mkdtemp()) / 'one.html'
    tmp.write_text(html, encoding='utf-8')
    p2 = b.new_page(viewport={'width': 1400, 'height': 950})
    e2 = []
    p2.on('pageerror', lambda e: e2.append(str(e)))
    p2.goto(tmp.as_uri())
    p2.wait_for_timeout(800)
    R['reopened_cards'] = p2.eval_on_selector_all('#list article .code', 'ns => ns.map(n => n.textContent)')
    R['reopened_styled'] = p2.eval_on_selector(
        'header', 'e => getComputedStyle(e).backgroundColor')
    R['errors_reopened'] = e2

    R['errors'] = errs
    pg.click('.tab[data-tab="camp"]')
    pg.wait_for_timeout(400)
    pg.screenshot(path='/home/user/-/shots/carwash-only.png')
    b.close()

print(json.dumps(R, ensure_ascii=False, indent=1))
