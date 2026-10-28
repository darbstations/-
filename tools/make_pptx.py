# -*- coding: utf-8 -*-
"""يحوّل ملف العرض إلى PowerPoint قابل للتحرير (ويُستورد في كانفا):
كل شريحة = صورة خلفية مرسومة من الصفحة بعد إخفاء النصوص، وفوقها مربّعات
نصّ حقيقية في أماكنها نفسها، بالخط والحجم واللون والمحاذاة ذاتها."""
import json
import os
import shutil

from playwright.sync_api import sync_playwright
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Emu, Pt

SRC = 'file:///home/user/-/darb-orange-friday-partner.html'   # نسختها بتعديلاتها
OUT_DIR = '/tmp/claude-0/-home-user--/b2086a51-b39c-5c55-b4a9-aeba6ad9f224/scratchpad/pptx'
OUT = '/home/user/-/darb-orange-friday.pptx'
SLIDE_W, SLIDE_H = 1120.0, 630.0          # مقاس الشريحة بالبكسل في الصفحة

COLLECT = r"""
(idx) => {
  const pg = document.querySelectorAll('.pg')[idx];
  const box = pg.getBoundingClientRect();
  const out = [];
  const leaf = el => {
    for (const c of el.children) if ((c.textContent || '').trim()) return false;
    return (el.innerText || '').trim().length > 0;
  };
  pg.querySelectorAll('*').forEach(el => {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity === 0) return;
    if (!leaf(el)) return;
    const r = el.getBoundingClientRect();
    if (!r.width || !r.height) return;
    /* صندوق المحتوى لا صندوق الحدود: الحشو والحدود تبقى في الخلفية */
    const px = n => parseFloat(cs[n]) || 0;
    const cl = r.left + px('paddingLeft') + px('borderLeftWidth');
    const ct = r.top + px('paddingTop') + px('borderTopWidth');
    const cw = r.width - px('paddingLeft') - px('paddingRight')
             - px('borderLeftWidth') - px('borderRightWidth');
    const ch = r.height - px('paddingTop') - px('paddingBottom')
             - px('borderTopWidth') - px('borderBottomWidth');
    if (cw <= 1 || ch <= 1) return;
    const m = (cs.color.match(/[\d.]+/g) || [0, 0, 0]).map(Number);
    out.push({
      text: el.innerText.replace(/ /g, ' ').trim(),
      left: cl - box.left, top: ct - box.top,
      width: cw, height: ch,
      size: parseFloat(cs.fontSize),
      weight: parseInt(cs.fontWeight, 10) || 400,
      lh: cs.lineHeight === 'normal' ? parseFloat(cs.fontSize) * 1.3 : parseFloat(cs.lineHeight),
      color: [m[0], m[1], m[2]],
      align: cs.textAlign,
      head: /OFHead|Araboto/i.test(cs.fontFamily),
      tag: el.tagName,
    });
  });
  return out;
}
"""

HIDE = """
(idx) => {
  const pg = document.querySelectorAll('.pg')[idx];
  const leaf = el => {
    for (const c of el.children) if ((c.textContent || '').trim()) return false;
    return (el.innerText || '').trim().length > 0;
  };
  const hidden = [];
  /* نُخفي الحروف لا العنصر: الاستكرات والبطاقات والحدود تبقى في الخلفية */
  pg.querySelectorAll('*').forEach(el => {
    if (!leaf(el)) return;
    hidden.push(el);
    el.style.setProperty('color', 'transparent', 'important');
    el.style.setProperty('-webkit-text-fill-color', 'transparent', 'important');
    el.style.setProperty('text-shadow', 'none', 'important');
  });
  window.__hidden = hidden;
}
"""

SHOW = """() => {
  (window.__hidden || []).forEach(el => {
    el.style.removeProperty('color');
    el.style.removeProperty('-webkit-text-fill-color');
    el.style.removeProperty('text-shadow');
  });
  window.__hidden = [];
}"""

shutil.rmtree(OUT_DIR, ignore_errors=True)
os.makedirs(OUT_DIR, exist_ok=True)

pages = []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
                          args=['--no-sandbox'])
    pg = b.new_page(viewport={'width': 1240, 'height': 800}, device_scale_factor=2)
    pg.goto(SRC)
    pg.wait_for_timeout(2500)
    n = pg.evaluate("document.querySelectorAll('.pg').length")
    for i in range(n):
        items = pg.evaluate(COLLECT, i)
        pg.evaluate(HIDE, i)
        pg.wait_for_timeout(120)
        shot = '%s/bg-%02d.png' % (OUT_DIR, i + 1)
        pg.query_selector_all('.pg')[i].screenshot(path=shot)
        pg.evaluate(SHOW)
        pages.append({'bg': shot, 'items': items})
        print('شريحة %2d: %2d نصًّا' % (i + 1, len(items)))
    b.close()

prs = Presentation()
prs.slide_width = Emu(12192000)           # 13.333 بوصة — ١٦:٩
prs.slide_height = Emu(6858000)
SX = prs.slide_width / SLIDE_W
SY = prs.slide_height / SLIDE_H
blank = prs.slide_layouts[6]

ALIGN = {'right': PP_ALIGN.RIGHT, 'left': PP_ALIGN.LEFT, 'center': PP_ALIGN.CENTER,
         'start': PP_ALIGN.RIGHT, 'end': PP_ALIGN.LEFT, 'justify': PP_ALIGN.JUSTIFY}

for page in pages:
    s = prs.slides.add_slide(blank)
    s.shapes.add_picture(page['bg'], 0, 0, width=prs.slide_width, height=prs.slide_height)
    for it in page['items']:
        pad = 2
        tb = s.shapes.add_textbox(Emu(int((it['left'] - pad) * SX)), Emu(int((it['top'] - pad) * SY)),
                                  Emu(int((it['width'] + 2 * pad) * SX)),
                                  Emu(int((it['height'] + 2 * pad) * SY)))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        lines = [l for l in it['text'].split('\n')]
        for k, line in enumerate(lines):
            para = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
            para.alignment = ALIGN.get(it['align'], PP_ALIGN.RIGHT)
            para._p.get_or_add_pPr().set('rtl', '1')
            para.line_spacing = max(0.8, min(2.0, it['lh'] / it['size']))
            run = para.add_run()
            run.text = line
            f = run.font
            f.name = 'Cairo' if it['head'] else 'Tajawal'
            f.size = Pt(it['size'] * 0.75)
            f.bold = it['weight'] >= 600
            f.color.rgb = RGBColor(*[max(0, min(255, int(c))) for c in it['color']])

prs.save(OUT)
print('\n%s — %d شريحة، %d كيلوبايت' % (OUT, len(pages), os.path.getsize(OUT) // 1024))
print('مربّعات النصّ:', sum(len(p['items']) for p in pages))
