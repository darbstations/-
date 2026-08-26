# -*- coding: utf-8 -*-
"""Drive the region deck the way she will: read the cover slider, fill the
partners table, undo it, then download and check the partner's copy is clean
but still animated."""
import json
import pathlib
import re
import tempfile
from playwright.sync_api import sync_playwright

PAGE = pathlib.Path('/home/user/-/darb-region-slides.html')
CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
R = {}


def head(p):
    return p.eval_on_selector('.pg.cover .rframe.is-on .rhead',
                              'e => e.firstChild.textContent.trim()')


def dot_on(p):
    return p.eval_on_selector_all(
        '.pg.cover .rdot', 'ns => ns.findIndex(n => n.classList.contains("on"))')


def rows(p):
    return p.eval_on_selector_all('table[data-ptab] tbody tr', 'ns => ns.length')


with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path=CHROME, args=['--no-sandbox'])
    pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.add_init_script("""window.claude={downloads:{save:function(o){
        window.__saved=o; return Promise.resolve(); }}};""")
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(PAGE.as_uri())
    pg.wait_for_selector('.pg.cover .rframe.is-on')

    # ---- الغلاف: ثلاثة أرقام فقط، والشريط يدور على المناطق
    R['facts_on_cover'] = pg.eval_on_selector_all(
        '.pg.cover .rframe.is-on .fact .k', 'ns => ns.map(n => n.textContent)')
    R['frames'] = pg.eval_on_selector_all('.pg.cover .rframe', 'ns => ns.length')
    R['dots'] = pg.eval_on_selector_all('.pg.cover .rdot', 'ns => ns.length')
    R['opens_on'] = head(pg)

    pg.click('.pg.cover .rnav[data-r="next"]')
    R['after_next'] = head(pg)
    pg.click('.pg.cover .rdot[data-r="3"]')
    R['after_dot3'] = (head(pg), dot_on(pg))

    before = dot_on(pg)
    pg.wait_for_timeout(6500)
    R['autoplay_moves'] = dot_on(pg) != before

    # ---- ملف منطقة أخرى يفتح على منطقته
    pg.select_option('#pick', 'جدة')
    pg.wait_for_timeout(400)
    R['jeddah_opens_on'] = head(pg)
    pg.click('.pg.cover .rnav[data-r="next"]')
    R['jeddah_slider_alive'] = head(pg) != R['jeddah_opens_on']

    pg.select_option('#pick', 'مكة')
    pg.wait_for_timeout(400)

    # ---- التحرير: الشريط يقف، والصفوف تُضاف وتُحذف
    pg.click('#edit')
    stopped = dot_on(pg)
    pg.wait_for_timeout(6500)
    R['autoplay_pauses_while_editing'] = dot_on(pg) == stopped

    R['rows_start'] = rows(pg)
    pg.eval_on_selector('.ptools button[data-tool="addrow"]', 'e => e.scrollIntoView()')
    pg.click('.ptools button[data-tool="addrow"]')
    R['rows_after_add'] = rows(pg)
    R['new_row_region'] = pg.eval_on_selector(
        'table[data-ptab] tbody tr:last-child td:nth-child(4)', 'e => e.textContent')

    cell = 'table[data-ptab] tbody tr:last-child td:nth-child(1)'
    pg.eval_on_selector(cell, 'e => { e.focus(); e.textContent = "مغسلة الوسام"; }')
    pg.eval_on_selector('table[data-ptab] tbody tr:last-child td:nth-child(2)',
                        'e => { e.textContent = "غسلة كاملة بـ ١٠ ر.س"; }')
    pg.eval_on_selector('table[data-ptab] tbody tr:last-child td:nth-child(3)',
                        'e => { e.textContent = "شهر واحد"; }')
    pg.click('h2')                       # يخرج من الخانة فيُحفظ
    pg.wait_for_timeout(700)

    pg.click('table[data-ptab] tbody tr:nth-child(1) .rowx button')
    R['rows_after_del'] = rows(pg)
    pg.wait_for_timeout(300)
    pg.click('#undo')
    R['rows_after_undo'] = rows(pg)
    pg.click('#redo')
    R['rows_after_redo'] = rows(pg)
    pg.click('#undo')                    # نعيد الصف المحذوف قبل التنزيل
    pg.wait_for_timeout(300)
    R['typed_survives'] = pg.eval_on_selector_all(
        'table[data-ptab] tbody td', 'ns => ns.some(n => n.textContent === "مغسلة الوسام")')

    # ---- الملف الذي يذهب للشريك
    pg.click('#dl')
    pg.wait_for_timeout(900)
    out = pg.evaluate('window.__saved')
    R['download_name'] = out['filename']
    html = out['data']
    R['export_kb'] = len(html) // 1024
    for bad, label in [('class="bar"', 'toolbar'), ('id="edit"', 'edit button'),
                       ('contenteditable', 'contenteditable'), ('data-tool', 'tool buttons'),
                       ('class="rowx"', 'row column'), ('class="ptools"', 'row bar'),
                       ('id="bb"', 'block bar'),
                       ('id="pick"', 'region picker'), ('darbEditor', 'editor code')]:
        R['export_has_' + label.replace(' ', '_')] = bad in html
    R['export_keeps_slider'] = ('data-rslider' in html and 'function darbSlider' in html)
    # data-block يبقى ذكره في نص الأنماط فقط؛ المهم ألا يحمله عنصر
    R['export_marked_elements'] = len(re.findall(r'<[a-z][^>]*\sdata-block', html))
    R['export_keeps_typed'] = 'مغسلة الوسام' in html
    R['export_partner_cols'] = html.count('<th>الشريك</th>')

    # ---- ويعمل عند الشريك
    tmp = pathlib.Path(tempfile.mkdtemp()) / 'partner.html'
    tmp.write_text(html, encoding='utf-8')
    p2 = b.new_page(viewport={'width': 1440, 'height': 900})
    e2 = []
    p2.on('pageerror', lambda e: e2.append(str(e)))
    p2.goto(tmp.as_uri())
    p2.wait_for_selector('.pg.cover .rframe.is-on')
    R['partner_opens_on'] = head(p2)
    R['partner_cols'] = p2.eval_on_selector_all(
        'table.ptab thead th', 'ns => ns.map(n => n.textContent.trim())')
    R['partner_rows'] = rows(p2)
    R['partner_no_buttons'] = p2.eval_on_selector_all(
        '#deck button', 'ns => ns.filter(n => !n.hasAttribute("data-nav")).length') == 0
    d0 = dot_on(p2)
    p2.wait_for_timeout(6500)
    R['partner_autoplay'] = dot_on(p2) != d0
    was = dot_on(p2)
    p2.click('.pg.cover .rnav[data-r="prev"]')
    R['partner_prev_steps_back'] = dot_on(p2) == (was - 1) % 6
    p2.click('.pg.cover .rdot[data-r="4"]')
    R['partner_dot_jumps'] = (dot_on(p2), head(p2))
    R['errors_partner'] = e2

    R['errors_page'] = errs
    pg.set_viewport_size({'width': 1440, 'height': 900})
    p2.screenshot(path='/home/user/-/shots/region-cover.png', clip={'x': 0, 'y': 0,
                                                                    'width': 1440, 'height': 900})
    b.close()

print(json.dumps(R, ensure_ascii=False, indent=1))
