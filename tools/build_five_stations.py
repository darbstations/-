# -*- coding: utf-8 -*-
"""يبني نسخة مختصرة (٥ محطات) وقابلة للتحرير من تقرير درب لتحليل المحطات."""
import re, json, io, sys

SRC = "/root/.claude/uploads/447348d0-0f0b-5d32-9f6b-27c9ad645473/75e38ee8-locationanalysis_8.html"
OUT = "/home/user/-/darb-five-stations-analysis.html"

KEEP = ["MK007", "MK017", "MK002", "MK023", "MK019"]      # بترتيب الإيراد اليومي
RENAME = {"MK007": ("العمرة الجديدة", "العمرة النورية"),
          "MK019": ("الشرايع", "عرفات الشرايع")}

s = open(SRC, encoding="utf-8").read()

# ─────────────────────────── 1. بيانات المقارنة (JSON) ───────────────────────────
m = re.search(r'(<script id="cmpdata" type="application/json">)(.*?)(</script>)', s, re.S)
cmp_open, cmp_json, cmp_close = m.group(1), m.group(2), m.group(3)
DATA = json.loads(cmp_json)

for code, (old, new) in RENAME.items():
    assert DATA["stations"][code]["name"] == old, code
    DATA["stations"][code]["name"] = new

NAME = {c: DATA["stations"][c]["name"] for c in KEEP}
REGION = {c: DATA["stations"][c]["region"] for c in KEEP}

DATA["stations"] = {c: DATA["stations"][c] for c in KEEP}
regions_kept = []
for r in DATA["regionOrder"]:
    codes = [c for c in DATA["regions"][r]["codes"] if c in KEEP]
    if codes:
        DATA["regions"][r]["codes"] = codes
        regions_kept.append(r)
DATA["regions"] = {r: DATA["regions"][r] for r in regions_kept}
DATA["regionOrder"] = regions_kept
new_cmp = cmp_open + json.dumps(DATA, ensure_ascii=False) + cmp_close

# ─────────────────────────── 2. تقسيم المستند ───────────────────────────
head, rest = s.split("<body>", 1)
hub_open = '<div id="hub">'
before_hub, rest = rest.split(hub_open, 1)
hub_html, rest = rest.split('</main>\n</div>\n<main class="wrap" id="pages">', 1)
pages_html, tail = rest.split('<script id="cmpdata"', 1)
tail = '<script id="cmpdata"' + tail                      # سكربتات + </body></html>
tail = tail.replace(m.group(0), new_cmp, 1)

# ─────────────────────────── 3. الصفحة الرئيسية (hub) ───────────────────────────
# 3-أ بطاقات المحطات
cards_m = re.search(r'(<div class="grid-cards" id="cards">)(.*?</a>)(</div>)', hub_html, re.S)
cards_body = cards_m.group(2)
card_blocks = re.findall(r'<a class="scard" href="#/(\w+)".*?</a>', cards_body, re.S)
cards_raw = {c: b for c, b in
             zip(card_blocks, re.findall(r'<a class="scard" href="#/\w+".*?</a>', cards_body, re.S))}
hub_html = hub_html.replace(cards_m.group(0),
    cards_m.group(1) + "\n      " + "\n      ".join(cards_raw[c] for c in KEEP) + cards_m.group(3))

# 3-ب جدول الترتيب
tbody_m = re.search(r'(<table id="ovt">.*?<tbody>)(.*?)(</tbody>)', hub_html, re.S)
rows = re.findall(r'<tr data-region="[^"]*">.*?</tr>', tbody_m.group(2), re.S)
by_code = {}
for r in rows:
    c = re.search(r'href="#/(\w+)"', r)
    if c:
        by_code[c.group(1)] = r
hub_html = hub_html.replace(tbody_m.group(0),
    tbody_m.group(1) + "".join(by_code[c] for c in KEEP) + tbody_m.group(3))

# 3-ج حذف قسم «محطات خارج نطاق هذا التحليل»
hub_html = re.sub(r'\s*<div class="sec-h"><h2>محطات خارج نطاق هذا التحليل</h2>.*?</details>',
                  "", hub_html, flags=re.S)

# 3-ج-2 توضيح ترقيم جدول الترتيب (الترتيب يبقى ترتيب الشبكة الكاملة)
hub_html = hub_html.replace(
    '<h2>جدول الترتيب</h2><span>مرتب بالإيراد اليومي · (*) رصد منافسين غير مكتمل</span>',
    '<h2>جدول الترتيب</h2><span>العمود (#) هو ترتيب المحطة ضمن الشبكة الكاملة (55 محطة) بالإيراد اليومي · '
    '(*) رصد منافسين غير مكتمل</span>')

# 3-د شرائح المناطق
chip_html = ('<a class="chip" href="#/compare" style="background:var(--orange);border-color:'
             'var(--orange);color:#fff;font-weight:700">⚖️ إنشاء مقارنة</a>'
             '<button class="chip on" data-r="*"><span class="nm">الكل</span>'
             f'<span class="code">{len(KEEP)}</span></button>')
for r in regions_kept:
    n = len(DATA["regions"][r]["codes"])
    chip_html += f'<button class="chip" data-r="{r}"><span class="nm">{r}</span><span class="code">{n}</span></button>'
hub_html = re.sub(r'(<div class="chips" id="chips">).*?(?=\n  <div class="search">)',
                  lambda mm: mm.group(1) + chip_html, hub_html, flags=re.S)

# ─────────────────────────── 4. صفحات المحطات ───────────────────────────
parts = re.split(r'(?=<div class="pgview" id=")', pages_html)
lead, blocks = parts[0], parts[1:]
pg = {}
for b in blocks:
    pg[re.search(r'id="pg-([\w-]+)"', b).group(1)] = b

wanted = []
for c in KEEP:
    wanted += [c, c + "-monthly", c + "-daily"]
wanted.append("compare")
missing = [w for w in wanted if w not in pg]
assert not missing, missing

# 4-أ قائمة الانتقال (select) — تُبنى من جديد
def build_select(current):
    o = "".join(
        f'<option value="#/{c}"{" selected" if c == current else ""}>'
        f'{NAME[c]} — {c} ({REGION[c]})</option>' for c in KEEP)
    return ('<select onchange="location.hash=this.value" aria-label="انتقل إلى محطة">'
            + o + "</select>")

# 4-ب روابط السابق/التالي
def build_nav(idx):
    links = ['<a class="hb" href="#/">⌂ جميع المحطات</a>']
    if idx > 0:
        p = KEEP[idx - 1]
        links.append(f'<a href="#/{p}">→ السابقة: {NAME[p]}</a>')
    if idx < len(KEEP) - 1:
        n = KEEP[idx + 1]
        links.append(f'<a href="#/{n}">التالية: {NAME[n]} ←</a>')
    return '<div class="nvl">\n        ' + "\n        ".join(links) + "\n      </div>"

new_pages = []
for i, c in enumerate(KEEP):
    for suffix in ("", "-monthly", "-daily"):
        b = pg[c + suffix]
        b = re.sub(r'<div class="nvl">.*?</div>\s*(?=<select onchange)',
                   build_nav(i) + "\n      ", b, flags=re.S)
        b = re.sub(r'<select onchange="location\.hash=this\.value".*?</select>',
                   build_select(c), b, flags=re.S)
        new_pages.append(b)
new_pages.append(pg["compare"])
pages_html = lead + "".join(new_pages)

# 4-ج المقارنة الافتراضية = محطة مقابل محطة (المحطات الخمس كلها في منطقة واحدة)
pages_html = pages_html.replace(
    '<option value="region" selected>مقارنة مناطق</option>\n      <option value="station">مقارنة محطات</option>',
    '<option value="region">مقارنة مناطق</option>\n      <option value="station" selected>مقارنة محطات</option>')

# ─────────────────────────── 5. إعادة التسمية ───────────────────────────
def rename_all(txt):
    for code, (old, new) in RENAME.items():
        txt = txt.replace(f"درب {old}", f"درب {new}")
        txt = txt.replace(f'href="#/{code}">{old}<', f'href="#/{code}">{new}<')
        txt = txt.replace(f'data-name="{old} {code}', f'data-name="{new} {code}')
        txt = txt.replace(f">{old} — {code}", f">{new} — {code}")
    return txt

hub_html, pages_html = rename_all(hub_html), rename_all(pages_html)

# ─────────────────────────── 6. ترويسة الشبكة ───────────────────────────
visits = 0
for c in KEEP:
    body = pg[c]
    v = re.search(r'<div class="kn">([\d,]+) زيارة', body)
    visits += int(v.group(1).replace(",", ""))
revenue = sum(DATA["stations"][c]["revenue"] for c in KEEP)
rating = sum(DATA["stations"][c]["rating"] for c in KEEP) / len(KEEP)
comps = sum(DATA["stations"][c]["compn"] for c in KEEP)

before_hub = re.sub(
    r'<p>النصف الأول 2026 · 55 محطة مشمولة بالبيانات · اختر محطة لفتح صفحتها الكاملة</p>',
    '<p>النصف الأول 2026 · 5 محطات مختارة · اختر محطة لفتح صفحتها الكاملة</p>', before_hub)
kpis = (
 f'<div><div class="v">{len(KEEP)}</div><div class="l">محطات مختارة (من أصل 218 بالشبكة)</div></div>'
 f'<div><div class="v">{revenue/1e6:.1f} <small>مليون ر.س</small></div><div class="l">إيراد الفترة للمحطات الخمس</div></div>'
 f'<div><div class="v">{visits/1e6:.2f} <small>مليون</small></div><div class="l">زيارة</div></div>'
 f'<div><div class="v">{rating:.2f} ★</div><div class="l">متوسط تقييم درب على جوجل</div></div>'
 f'<div><div class="v">{comps}</div><div class="l">محطة منافسة مرصودة ضمن نطاقات 5 كم</div></div>')
before_hub = re.sub(r'(<div class="netkpis">)(.*?)(\s*</div>\s*</div>\s*</header>)',
                    lambda mm: mm.group(1) + kpis + mm.group(3), before_hub, flags=re.S)

# ─────────────────────────── 7. طبقة التحرير ───────────────────────────
EDIT_CSS = """
<style id="editor-css">
/* ── وضع التحرير ── */
body{padding-block-end:86px}
#edbar{position:fixed;inset-block-end:16px;inset-inline-start:16px;z-index:200;display:flex;gap:8px;
  align-items:center;background:#fff;border:1px solid var(--line2);border-radius:14px;padding:8px 10px;
  box-shadow:0 6px 26px rgba(61,61,61,.16);font-family:inherit;font-size:13px;flex-wrap:wrap;max-width:calc(100vw - 32px)}
#edbar button{font-family:inherit;font-size:13px;border:1px solid var(--line2);background:#fff;color:var(--ink2);
  border-radius:10px;padding:7px 12px;cursor:pointer;transition:.14s;white-space:nowrap}
#edbar button:hover{border-color:var(--orange);color:var(--ink)}
#edbar button.primary{background:var(--bgray);border-color:var(--bgray);color:#fff;font-weight:700}
#edbar button.primary.live{background:var(--orange);border-color:var(--orange)}
#edbar .edst{font-size:11.5px;color:var(--ink3);min-width:74px}
html.editing [data-ez]{outline:1px dashed rgba(245,131,31,.45);outline-offset:6px;border-radius:8px}
html.editing [data-ez]:focus{outline:2px solid var(--orange);outline-offset:6px}
html.editing a{cursor:text}
html.editing ::selection{background:#F7A94B;color:#3D3D3D}
@media print{#edbar{display:none}}
</style>
"""

EDIT_JS = r"""
<script id="editor-js">
/* ═══ طبقة التحرير: تحرير النصوص داخل الصفحة + حفظ تلقائي + تنزيل نسخة ═══ */
(function(){
  var ZONES=[].slice.call(document.querySelectorAll('[data-ez]'));
  var docId=document.documentElement.dataset.docid||'darb-5st';
  var KEY='darb-edits:'+docId;
  var editing=false,timer=null;

  /* ‏— لقطة نظيفة: نتجاهل سمات contenteditable التي يضيفها المحرّر نفسه — */
  function snap(z){
    var c=z.cloneNode(true);
    c.querySelectorAll('[contenteditable]').forEach(function(n){n.removeAttribute('contenteditable');});
    c.querySelectorAll('[spellcheck]').forEach(function(n){n.removeAttribute('spellcheck');});
    return c.innerHTML;
  }

  /* ‏— نسخة أصلية لكل منطقة، تُلتقط قبل أي استعادة — */
  var ORIG={};
  ZONES.forEach(function(z){ORIG[z.dataset.ez]=snap(z);});

  /* ‏— استعادة التعديلات المحفوظة — */
  try{
    var saved=JSON.parse(localStorage.getItem(KEY)||'{}');
    ZONES.forEach(function(z){var k=z.dataset.ez;if(saved[k]!=null)z.innerHTML=saved[k];});
  }catch(e){}

  /* ‏— شريط الأدوات — */
  var bar=document.createElement('div');
  bar.id='edbar';
  bar.innerHTML='<button id="edToggle" class="primary">✏️ وضع التحرير</button>'+
                '<button id="edSave">⬇️ تنزيل نسخة HTML</button>'+
                '<button id="edReset">↺ استعادة الأصل</button>'+
                '<span class="edst" id="edStat"></span>';
  document.body.appendChild(bar);
  var stat=bar.querySelector('#edStat');
  function say(t){stat.textContent=t;}

  /* ‏— لا نحفظ إلا المناطق التي تغيّرت فعلًا — */
  function store(){
    var o={},n=0;
    ZONES.forEach(function(z){
      var k=z.dataset.ez,h=snap(z);
      if(h!==ORIG[k]){o[k]=h;n++;}
    });
    try{
      if(n)localStorage.setItem(KEY,JSON.stringify(o));else localStorage.removeItem(KEY);
      say(n?'✓ حُفظ محليًا':'مطابق للأصل');
    }catch(e){say('تعذّر الحفظ المحلي');}
  }
  function queue(){clearTimeout(timer);say('…');timer=setTimeout(store,600);}

  /* ‏— جزر غير قابلة للتحرير حتى يبقى التنقّل شغّالًا — */
  var LOCK='.pgnav, .tabs, .cmpbar, .dimchips, #cmpOut';
  function setEditing(on){
    editing=on;
    document.documentElement.classList.toggle('editing',on);
    ZONES.forEach(function(z){
      if(on){z.setAttribute('contenteditable','true');z.setAttribute('spellcheck','false');}
      else z.removeAttribute('contenteditable');
      z.querySelectorAll(LOCK).forEach(function(n){
        if(on)n.setAttribute('contenteditable','false');else n.removeAttribute('contenteditable');
      });
    });
    var b=bar.querySelector('#edToggle');
    b.textContent=on?'✅ إنهاء التحرير':'✏️ وضع التحرير';
    b.classList.toggle('live',on);
    say(on?'اضغط على أي نص وعدّله':'');
  }

  /* ‏— منع تنقّل الروابط أثناء التحرير — */
  document.addEventListener('click',function(e){
    if(!editing)return;
    var a=e.target.closest&&e.target.closest('a');
    if(a&&a.closest('[data-ez]'))e.preventDefault();
  },true);

  ZONES.forEach(function(z){z.addEventListener('input',queue);});

  bar.querySelector('#edToggle').addEventListener('click',function(){
    setEditing(!editing);
    if(!editing){clearTimeout(timer);store();}
  });

  bar.querySelector('#edReset').addEventListener('click',function(){
    if(!confirm('استعادة النص الأصلي وحذف كل تعديلاتك في هذا الملف؟'))return;
    try{localStorage.removeItem(KEY);}catch(e){}
    location.reload();
  });

  /* ‏— تنزيل نسخة مستقلة بالتعديلات مدمجة — */
  bar.querySelector('#edSave').addEventListener('click',function(){
    var wasEditing=editing;
    if(wasEditing)setEditing(false);
    store();
    var doc=document.documentElement.cloneNode(true);
    var b2=doc.querySelector('#edbar');if(b2)b2.remove();
    doc.classList.remove('editing');
    /* معرّف جديد حتى تبدأ النسخة المنزَّلة بذاكرة تعديلات نظيفة */
    doc.dataset.docid='darb-5st-'+Math.random().toString(36).slice(2,10);
    doc.querySelectorAll('[contenteditable]').forEach(function(n){n.removeAttribute('contenteditable');});
    var html='<!DOCTYPE html>\n'+doc.outerHTML;
    var url=URL.createObjectURL(new Blob([html],{type:'text/html;charset=utf-8'}));
    var a=document.createElement('a');
    a.href=url;a.download='darb-five-stations-analysis.html';document.body.appendChild(a);a.click();
    a.remove();setTimeout(function(){URL.revokeObjectURL(url);},4000);
    if(wasEditing)setEditing(true);
    say('✓ تم التنزيل');
  });

  /* ‏— اختصارات: Ctrl/⌘+E تبديل التحرير · Ctrl/⌘+S تنزيل — */
  document.addEventListener('keydown',function(e){
    if(!(e.ctrlKey||e.metaKey))return;
    var k=e.key.toLowerCase();
    if(k==='e'){e.preventDefault();setEditing(!editing);}
    if(k==='s'){e.preventDefault();bar.querySelector('#edSave').click();}
  });
})();
</script>
"""

# 7-أ وسم المناطق القابلة للتحرير
ez = [0]
def mark(txt, pattern, count=0, flags=0):
    def rep(mm):
        ez[0] += 1
        return mm.group(1) + f' data-ez="z{ez[0]}"' + mm.group(2)
    out, n = re.subn(pattern, rep, txt, count=count, flags=flags)
    assert n, pattern
    return out

before_hub = mark(before_hub, r'(<div class="hd-title")(>)', count=1)
before_hub = mark(before_hub, r'(<div class="netkpis")(>)', count=1)
hub_html   = mark(hub_html,   r'(<main class="wrap")(>)', count=1)
# كل صفحة محطة (التحليل/الشهري/اليومي) منطقة تحرير كاملة — عدا صفحة المقارنة
pages_html = mark(pages_html, r'(<div class="pgview")( id="pg-(?!compare)[\w-]+")')
# صفحة المقارنة: العنوان والملاحظة فقط (بقيتها تُولَّد تلقائيًا من بيانات المقارنة)
pages_html = mark(pages_html, r'(<div class="sec-h")(><h2>⚖️ إنشاء مقارنة</h2>)', count=1)
pages_html = mark(pages_html, r'(<div class="cmpnote")(>)', count=1)

# ─────────────────────────── 8. التجميع ───────────────────────────
head = head.replace("<html lang=\"ar\" dir=\"rtl\">",
                    "<html lang=\"ar\" dir=\"rtl\" data-docid=\"darb-5st-v1\">")
head = head.replace("<title>درب · تحليل المحطات والمبيعات — دليل المحطات</title>",
                    "<title>درب · تحليل خمس محطات (قابل للتحرير)</title>")
head = head.replace("</head>", EDIT_CSS + "</head>")

tail = tail.replace("</body>", EDIT_JS + "</body>")
tail = tail.replace("درب · تحليل المحطات والمبيعات — دليل المحطات",
                    "درب · تحليل خمس محطات (قابل للتحرير)")

out = (head + "<body>" + before_hub + hub_open + hub_html
       + '</main>\n</div>\n<main class="wrap" id="pages">' + pages_html + tail)

open(OUT, "w", encoding="utf-8").write(out)
print("مناطق قابلة للتحرير:", ez[0])
print("حجم الملف:", round(len(out.encode()) / 1024), "KB")
print("إيراد:", round(revenue/1e6, 1), "م · زيارات:", visits, "· تقييم:", round(rating, 2), "· منافسون:", comps)
