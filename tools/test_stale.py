# -*- coding: utf-8 -*-
"""A deck saved before the update must never be replaced behind her back:
it loads as she left it, the page offers the new cover, and undo brings her
copy straight back."""
import json
import pathlib
from playwright.sync_api import sync_playwright

PAGE = pathlib.Path('/home/user/-/darb-region-slides.html')
CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
KEY = 'darb-region-slides-v2-مكة'
R = {}

# نسخة قديمة: بلا شريط ولا جدول شركاء، وفيها سطر كتبته هي
OLD = ('<section class="pg cover"><div class="in"><h1>غلاف قديم</h1>'
       '<div class="strip"><div class="fact"><div class="k">سيارات كل يوم</div>'
       '<div class="v">٥٬٨٢٤</div></div></div></div></section>'
       '<section class="pg"><h2>شريحة كتبتها بنفسي</h2><p class="lede">لا تُمسح.</p></section>')

with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path=CHROME, args=['--no-sandbox'])
    pg = b.new_page(viewport={'width': 1400, 'height': 900})
    pg.add_init_script("""window.claude={downloads:{save:function(o){
        window.__saved=o; return Promise.resolve(); }}};""")
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))

    pg.goto(PAGE.as_uri())
    pg.evaluate('([k,v]) => localStorage.setItem(k,v)', [KEY, OLD])
    pg.reload()
    pg.wait_for_timeout(900)

    # ١ · تفتح على نسختها لا على البناء الجديد
    R['loads_her_copy'] = pg.eval_on_selector_all('#deck h2', 'ns => ns.map(n => n.textContent)')
    R['no_slider_yet'] = pg.eval_on_selector_all('#deck [data-rslider]', 'ns => ns.length') == 0
    R['offer_shown'] = pg.is_visible('#toastact')
    R['offer_label'] = pg.text_content('#toastact')
    R['offer_msg'] = (pg.text_content('#toastmsg') or '')[:60]

    # ٢ · الضغط على «حدّث» يجيب الجديد
    pg.click('#toastact')
    pg.wait_for_timeout(700)
    R['after_update_frames'] = pg.eval_on_selector_all('#deck .rframe', 'ns => ns.length')
    R['after_update_ptab'] = pg.eval_on_selector_all('#deck [data-ptab]', 'ns => ns.length')
    R['after_update_slides'] = pg.eval_on_selector_all('#deck .pg', 'ns => ns.length')

    # ٣ · «تراجع» يرجّع نسختها كاملة
    pg.click('#edit')
    pg.click('#undo')
    pg.wait_for_timeout(500)
    R['undo_back_to_hers'] = pg.eval_on_selector_all('#deck h2', 'ns => ns.map(n => n.textContent)')
    R['undo_persisted'] = pg.evaluate('k => (localStorage.getItem(k)||"").indexOf("شريحة كتبتها بنفسي")>=0', KEY)

    # ٤ · متصفح بلا نسخة محفوظة لا يرى العرض أصلًا
    pg.evaluate('k => localStorage.removeItem(k)', KEY)
    pg.reload()
    pg.wait_for_timeout(900)
    R['clean_browser_offer'] = pg.is_visible('#toastact')
    R['clean_browser_frames'] = pg.eval_on_selector_all('#deck .rframe', 'ns => ns.length')
    R['title'] = pg.title()

    R['errors'] = errs
    b.close()

print(json.dumps(R, ensure_ascii=False, indent=1))
