# -*- coding: utf-8 -*-
"""لقطات الشرائح + فحوص التخطيط: تجاوز الحدود، صورة فوق نص، نص غير مرئي."""
import json
import sys
from playwright.sync_api import sync_playwright

SRC = '/home/user/-/darb-orange-friday.html'
OUT = '/tmp/claude-0/-home-user--/b2086a51-b39c-5c55-b4a9-aeba6ad9f224/scratchpad'
want = [int(x) for x in sys.argv[1:]] or None

CHECKS = r"""
(() => {
  const res = {content_overflow: [], text_under_image: [], invisible_text: []};
  const pgs = [...document.querySelectorAll('.pg')];
  const area = (a, b) => {
    const w = Math.min(a.right, b.right) - Math.max(a.left, b.left);
    const h = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
    return w > 0 && h > 0 ? w * h : 0;
  };
  const txt = el => (el.textContent || '').trim();
  const resolveBg = el => {
    let n = el;
    while (n && n !== document.documentElement) {
      const c = getComputedStyle(n).backgroundColor;
      if (c && c !== 'rgba(0, 0, 0, 0)' && c !== 'transparent') return c;
      n = n.parentElement;
    }
    return 'rgb(255, 255, 255)';
  };
  pgs.forEach((pg, i) => {
    const box = pg.getBoundingClientRect();
    [...pg.querySelectorAll('*')].forEach(el => {
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || cs.visibility === 'hidden') return;
      let r = el.getBoundingClientRect();
      if (!r.width || !r.height) return;
      for (let n = el.parentElement; n && n !== document.body; n = n.parentElement) {
        const o = getComputedStyle(n);
        if (o.overflow !== 'visible' || o.overflowX !== 'visible') {
          const c = n.getBoundingClientRect();
          r = new DOMRect(Math.max(r.left, c.left), Math.max(r.top, c.top),
                          Math.min(r.right, c.right) - Math.max(r.left, c.left),
                          Math.min(r.bottom, c.bottom) - Math.max(r.top, c.top));
        }
      }
      if (r.width <= 0 || r.height <= 0) return;
      if (!el.classList.contains('in') &&
          (r.left < box.left - 1.5 || r.right > box.right + 1.5 ||
           r.top < box.top - 1.5 || r.bottom > box.bottom + 1.5)) {
        res.content_overflow.push({
          slide: i + 1, el: el.className || el.tagName,
          d: [Math.round(box.left - r.left), Math.round(r.right - box.right),
              Math.round(box.top - r.top), Math.round(r.bottom - box.bottom)]
        });
      }
      if (txt(el) && el.children.length === 0) {
        const col = cs.color, bg = resolveBg(el);
        if (col === bg) res.invisible_text.push({slide: i + 1, t: txt(el).slice(0, 30), col});
      }
    });
    const pics = [...pg.querySelectorAll('.snap, .picside, .ofmark, .mark, .scene')];
    pics.forEach(p => {
      const pr = p.getBoundingClientRect();
      [...pg.querySelectorAll('h1,h2,h3,p,span,div,li,td')].forEach(t => {
        if (!txt(t) || t.children.length) return;
        if (p.contains(t) || t.contains(p)) return;
        const a = area(pr, t.getBoundingClientRect());
        if (a > 1200) res.text_under_image.push({
          slide: i + 1, pic: p.className, t: txt(t).slice(0, 28), a: Math.round(a)
        });
      });
    });
  });
  return res;
})()
"""

with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
                          args=['--no-sandbox'])
    pg = b.new_page(viewport={'width': 1240, 'height': 760}, device_scale_factor=1)
    pg.goto('file://' + SRC)
    pg.wait_for_timeout(1800)
    out = pg.evaluate(CHECKS)
    for k, v in out.items():
        print('%s: %s' % (k, json.dumps(v, ensure_ascii=False)))
    secs = pg.query_selector_all('.pg')
    print('slides: %d' % len(secs))
    for i, s in enumerate(secs, 1):
        if want and i not in want:
            continue
        s.screenshot(path='%s/of-%02d.png' % (OUT, i))
    print('tool buttons on export: %d' % pg.evaluate(
        "document.querySelectorAll('#deck [data-tool]').length"))
    b.close()
