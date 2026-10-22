# -*- coding: utf-8 -*-
"""الجمعة البرتقالية — هوية «ريترو حديث».

الألوان مأخوذة من شعارها نفسه: برتقالي #FC6C05 وكريمي #FDF5DE وحبر #141210،
ومعها سلّم رمادي كما طلبت. ولغة التصميم ريترو حديث: حدود سميكة، وظلال
مصمتة بلا تمويه، وتنقيط هاف‑تون، وأشعّة مثل أشعّة الشعار، وأيقونات مرسومة
بالأسلوب نفسه.

الخطّان المطلوبان — ARABOTO للعناوين وDIN NEXT للمتن — تجاريان ولا يمكن
جلبهما، فمكانهما محجوز أولًا في كل عائلة: من عنده الخطان يراهما، ومن لا
فعنده بديلان مضمَّنان في الملف يعملان بلا إنترنت.
"""
import base64
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MEDIA = os.path.join(HERE, 'orangefriday', 'media')
FONTS = os.path.join(HERE, 'fonts', 'files')
BRAND = os.path.join(HERE, 'brand')
CHROME_SRC = '/home/user/-/darb-carwash-slides.html'
OUT = '/home/user/-/darb-orange-friday.html'
ART = '/home/user/-/darb-orange-friday-artifact.html'


def b64(path):
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode()


def img(name, folder=None):
    p = os.path.join(folder or MEDIA, name)
    ext = 'png' if name.endswith('.png') else 'jpeg'
    return 'data:image/%s;base64,%s' % (ext, b64(p))


LOGO_OF = img('logo.png', BRAND)          # شعار الجمعة البرتقالية
LOGO_DARB = img('image-1-1.png')
STATION = img('image-1-2.jpeg')
CLOSE_ART = img('image-15-1.jpeg')
CLIPS = [img('image-12-%d.jpeg' % i) for i in range(1, 7)]
LOGOS = [img('image-13-%d.jpeg' % i) for i in range(1, 7)]
INFL = [img('image-13-%d.jpeg' % i) for i in range(7, 13)]

# ---------------------------------------------------------------- الخطوط
FACES = """
@font-face{font-family:"OFHead";font-weight:200 1000;font-style:normal;font-display:swap;
  src:url(data:font/woff2;base64,%s) format("woff2")}
@font-face{font-family:"OFBody";font-weight:400;font-style:normal;font-display:swap;
  src:url(data:font/woff2;base64,%s) format("woff2")}
@font-face{font-family:"OFBody";font-weight:500;font-style:normal;font-display:swap;
  src:url(data:font/woff2;base64,%s) format("woff2")}
@font-face{font-family:"OFBody";font-weight:700 900;font-style:normal;font-display:swap;
  src:url(data:font/woff2;base64,%s) format("woff2")}
""" % (b64(os.path.join(FONTS, 'Cairo-900.woff2')),
       b64(os.path.join(FONTS, 'Tajawal-400.woff2')),
       b64(os.path.join(FONTS, 'Tajawal-500.woff2')),
       b64(os.path.join(FONTS, 'Tajawal-700.woff2')))

# ---------------------------------------------------------------- الأيقونات
# مرسومة بالأسلوب نفسه: خطّ سميك، وزاوية مستديرة، وتعبئة برتقالية
GLYPH = {
    'spark': '<path d="M16 3l3 9 9 3-9 3-3 9-3-9-9-3 9-3z"/>',
    'play':  '<path d="M12 9l12 7-12 7z"/>',
    'mic':   '<rect x="12" y="4" width="8" height="15" rx="4"/>'
             '<path d="M7 16a9 9 0 0018 0M16 25v4M11 29h10"/>',
    'chat':  '<path d="M4 8h24v15H16l-7 6v-6H4z"/>',
    'ticket': '<path d="M4 10h24v5a3 3 0 000 6v5H4v-5a3 3 0 000-6z"/><path d="M16 10v16"/>',
    'sign':  '<rect x="4" y="6" width="24" height="13" rx="2"/><path d="M16 19v9M10 28h12"/>',
    'scan':  '<path d="M5 11V6h5M27 11V6h-5M5 21v5h5M27 21v5h-5"/><path d="M9 16h14"/>',
    'check': '<path d="M6 17l6 6 14-14"/>',
    'chart': '<path d="M5 27V17M13 27V8M21 27V13M29 27V20"/>',
    'pump':  '<path d="M6 28V7a3 3 0 013-3h7a3 3 0 013 3v21"/><path d="M4 28h17M9 11h7"/>'
             '<path d="M19 12h4a3 3 0 013 3v7a2 2 0 004 0v-9l-4-4"/>',
    'user':  '<circle cx="16" cy="11" r="6"/><path d="M5 28c0-6 5-10 11-10s11 4 11 10"/>',
    'eye':   '<path d="M2 16s5-8 14-8 14 8 14 8-5 8-14 8-14-8-14-8z"/><circle cx="16" cy="16" r="4"/>',
}


def icon(kind, fill=False):
    g = GLYPH[kind]
    cls = 'ric' + (' on' if fill else '')
    return ('<span class="%s"><svg viewBox="0 0 32 32" aria-hidden="true">%s</svg></span>'
            % (cls, g))


CSS = FACES + """
:root{
  /* من الشعار نفسه */
  --orange:#FC6C05; --orange-dk:#C9500A; --orange-lt:#FFA24D;
  --cream:#FDF5DE;  --paper:#F7F0DE;     --ink:#141210;
  /* السلّم الرمادي */
  --g900:#2A2724; --g800:#39342F; --g700:#4A4540; --g500:#7D7greyA;
  --g400:#9B948A; --g300:#C2BBAE; --g200:#DED8C9; --g100:#EDE8DA;
  --head:"Araboto","Araboto Normal","Araboto Medium","OFHead",system-ui,sans-serif;
  --body:"DIN Next LT Arabic","DIN Next Arabic","DIN Next W23","OFBody",system-ui,sans-serif;
}
*{box-sizing:border-box}
html,body{margin:0;background:#1B1916;color:var(--ink);font-family:var(--body)}
h1,h2,h3{margin:0;font-family:var(--head);font-weight:900;line-height:1.14;
  letter-spacing:-.015em}
p{margin:0}
.wrap{padding:26px 18px 60px}

/* ---------------- الورقة ---------------- */
.pg{width:1120px;height:630px;margin:0 auto 22px;background:var(--cream);
  border-radius:12px;overflow:hidden;position:relative;display:flex;
  flex-direction:column;padding:50px 58px;
  box-shadow:0 20px 48px rgba(0,0,0,.45)}
.pg.grey{background:var(--g900);color:var(--cream)}
.pg.orange{background:var(--orange);color:var(--ink)}

/* تنقيط الهاف‑تون: نسيج الريترو */
.pg::before{content:"";position:absolute;inset:0;pointer-events:none;
  background-image:radial-gradient(var(--ink) 1.3px,transparent 1.4px);
  background-size:9px 9px;opacity:.055}
.pg.grey::before{background-image:radial-gradient(var(--cream) 1.3px,transparent 1.4px);
  opacity:.07}
.pg > *{position:relative}

.eyebrow{font-family:var(--head);font-size:12px;font-weight:900;letter-spacing:.2em;
  color:var(--orange-dk);margin-bottom:12px;display:flex;align-items:center;gap:9px}
.eyebrow::before{content:"";width:22px;height:4px;background:var(--orange);
  border:2px solid var(--ink);border-radius:2px}
.pg.grey .eyebrow{color:var(--orange-lt)}
.pg.grey .eyebrow::before{border-color:var(--cream)}
.pg.orange .eyebrow{color:var(--ink)}
h2{font-size:40px;margin-bottom:12px}
.lede{font-size:15.5px;line-height:1.9;font-weight:500;color:var(--g700);max-width:74ch}
.pg.grey .lede{color:var(--g300)}
.pg.orange .lede{color:#4A2A05}

/* علامة مميّزة داخل العنوان */
.hl{background:var(--orange);color:var(--ink);padding:1px 10px;border:3px solid var(--ink);
  border-radius:8px;box-shadow:-4px 4px 0 var(--ink);display:inline-block}
.pg.grey .hl{box-shadow:-4px 4px 0 var(--cream)}

/* ---------------- بطاقات الريترو: حدّ سميك وظلّ مصمت ---------------- */
.rcard{background:var(--cream);color:var(--ink);border:3px solid var(--ink);
  border-radius:14px;box-shadow:-6px 6px 0 var(--ink);padding:20px 22px}
.rcard.o{background:var(--orange);color:var(--ink)}
.rcard.d{background:var(--g900);color:var(--cream);box-shadow:-6px 6px 0 var(--orange)}
.pg.grey .rcard{box-shadow:-6px 6px 0 var(--orange)}
.pg.orange .rcard{box-shadow:-6px 6px 0 var(--ink)}

/* ---------------- الأيقونات ---------------- */
.ric{width:42px;height:42px;flex:0 0 42px;border:3px solid var(--ink);border-radius:50%;
  background:var(--cream);display:flex;align-items:center;justify-content:center;
  box-shadow:-3px 3px 0 var(--ink)}
.ric.on{background:var(--orange)}
.ric svg{width:23px;height:23px;fill:none;stroke:var(--ink);stroke-width:2.6;
  stroke-linecap:round;stroke-linejoin:round}
.pg.grey .ric{box-shadow:-3px 3px 0 var(--orange)}

/* ---------------- الأشعّة: من الشعار ---------------- */
.rays{position:absolute;width:760px;height:760px;pointer-events:none;opacity:.16;
  background:repeating-conic-gradient(from 8deg,var(--orange) 0deg 5deg,transparent 5deg 13deg)}
.pg.orange .rays{background:repeating-conic-gradient(from 8deg,var(--ink) 0deg 5deg,
  transparent 5deg 13deg);opacity:.10}

/* ---------------- الغلاف ---------------- */
.cover{align-items:center;justify-content:center;text-align:center;background:var(--g900)}
.cover .rays{inset-inline-start:50%;top:-240px;transform:translateX(50%)}
.cover .mark{width:560px;max-width:86%;height:auto;display:block;
  filter:drop-shadow(-8px 10px 0 rgba(0,0,0,.45))}
.cover .when{margin-top:26px;display:inline-flex;align-items:center;gap:10px;
  background:var(--orange);border:3px solid var(--cream);border-radius:99px;
  padding:11px 24px;font-weight:800;font-size:14px;color:var(--ink);
  box-shadow:-5px 5px 0 var(--ink)}
.cover .tag{margin-top:20px;font-family:var(--head);font-weight:900;font-size:25px;
  color:var(--cream)}
.cover .foot2{position:absolute;inset-inline:40px;bottom:26px;display:flex;
  align-items:center;justify-content:space-between;font-size:12px;color:var(--g400)}
.cover .foot2 img{height:26px}

/* ---------------- الأرقام ---------------- */
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-top:auto}
.stat2 .v{font-family:var(--head);font-size:50px;font-weight:900;line-height:1;
  font-variant-numeric:tabular-nums}
.stat2 .k{font-size:15px;font-weight:800;margin-top:9px}
.stat2 .u{font-size:12.5px;line-height:1.7;margin-top:7px;color:var(--g700)}
.rcard.d .u,.rcard.o .u{color:inherit;opacity:.85}

.goals{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:auto;
  margin-bottom:auto}
.goal{display:flex;align-items:center;gap:15px;font-size:16px;font-weight:700;
  background:var(--g800);border:3px solid var(--cream);border-radius:14px;
  padding:20px 22px;box-shadow:-6px 6px 0 var(--orange)}

.bignum{display:flex;align-items:baseline;gap:12px;margin-top:8px}
.bignum b{font-family:var(--head);font-size:56px;font-weight:900;color:var(--orange-dk);
  line-height:1;font-variant-numeric:tabular-nums;
  text-shadow:-3px 3px 0 var(--ink)}
.bignum span{font-size:14px;color:var(--g700);font-weight:700}
.segs{display:flex;flex-wrap:wrap;align-items:baseline}
.segs > span + span::before{content:"";display:inline-block;width:7px;height:7px;
  margin:0 13px;background:var(--orange);border:2px solid var(--ink);border-radius:50%;
  vertical-align:middle}

.bars{display:flex;flex-direction:column;gap:12px;margin-top:24px}
.barrow{display:grid;grid-template-columns:150px 1fr 82px;align-items:center;gap:14px;
  font-size:13.5px}
.barrow .t{font-weight:700}
.barrow .track{display:block;height:20px;background:var(--g100);border:2.5px solid var(--ink);
  border-radius:99px;overflow:hidden}
.barrow .fill{display:block;height:100%;background:var(--orange)}
.barrow .v{text-align:left;font-weight:900;font-variant-numeric:tabular-nums;
  font-family:var(--head)}

.pills{display:flex;flex-wrap:wrap;gap:11px;margin-top:auto}
.pill{background:var(--cream);border:3px solid var(--ink);border-radius:99px;
  padding:9px 18px;font-size:13px;font-weight:700;box-shadow:-4px 4px 0 var(--ink)}
.pill b{font-weight:900;font-family:var(--head)}
.pg.grey .pill{background:var(--g800);color:var(--cream);box-shadow:-4px 4px 0 var(--orange)}
.pg.orange .pill{background:var(--cream)}

/* ---------------- صفوف ---------------- */
.rows{display:flex;flex-direction:column;gap:11px;margin-top:20px}
.rowi{display:flex;align-items:center;gap:14px;font-size:14.5px;font-weight:600}
.rowi .tagx{margin-inline-start:auto;font-size:11px;font-weight:900;font-family:var(--head);
  border:2.5px solid var(--ink);border-radius:99px;padding:4px 13px;background:var(--orange);
  color:var(--ink);white-space:nowrap;box-shadow:-3px 3px 0 var(--ink)}
.rowi .tagx.f{background:var(--g200)}
.pg.grey .rowi .tagx{box-shadow:-3px 3px 0 var(--cream)}

/* ---------------- خطوات ---------------- */
.steps{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-top:auto}
.step{display:flex;flex-direction:column;gap:11px}
.step h3{font-size:15px}
.step p{font-size:12.5px;line-height:1.7;color:var(--g700);font-weight:500}
.step .when{font-size:11px;font-weight:900;font-family:var(--head);color:var(--orange-dk);
  margin-top:auto}

/* ---------------- نصفان ---------------- */
.split{display:grid;grid-template-columns:1fr 1fr;flex:1;margin:-50px -58px;
  align-items:stretch}
.half{padding:50px 54px;display:flex;flex-direction:column;position:relative}
.half.orange{background:var(--orange)}
.half.grey{background:var(--g900);color:var(--cream)}
.half.grey .eyebrow{color:var(--orange-lt)}
.half.grey .rowi .tagx{box-shadow:-3px 3px 0 var(--cream)}

/* ---------------- صور ---------------- */
.grid6{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin-top:auto}
.grid6 img{width:100%;height:200px;object-fit:cover;border:3px solid var(--ink);
  border-radius:10px;box-shadow:-4px 4px 0 var(--ink);display:block}
.pg.grey .grid6 img{box-shadow:-4px 4px 0 var(--orange)}
.logos{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin-top:12px}
.logos img{width:100%;height:96px;object-fit:contain;background:var(--cream);
  border:3px solid var(--ink);border-radius:10px;padding:9px;display:block;
  box-shadow:-4px 4px 0 var(--ink)}
.chips{display:flex;gap:13px;margin-bottom:16px}
.chip{border:3px solid var(--ink);border-radius:12px;padding:12px 20px;text-align:center;
  background:var(--cream);color:var(--ink);box-shadow:-4px 4px 0 var(--orange)}
.chip b{display:block;font-family:var(--head);font-size:25px;font-weight:900;
  font-variant-numeric:tabular-nums}
.chip span{font-size:11.5px;color:var(--g700);font-weight:700}

/* ---------------- السنة العملاقة ---------------- */
.year{position:absolute;inset-inline-start:46px;top:40px;font-family:var(--head);
  font-size:210px;font-weight:900;line-height:1;color:transparent;
  -webkit-text-stroke:4px rgba(20,18,16,.22);pointer-events:none}

/* ---------------- جدول العروض ---------------- */
.otab{border-collapse:separate;border-spacing:0;width:100%;font-size:14px;
  background:var(--cream);border:3px solid var(--ink);border-radius:12px;
  overflow:hidden;margin-top:20px;box-shadow:-6px 6px 0 var(--ink)}
.otab th,.otab td{padding:14px 16px;text-align:right;border-bottom:2px solid var(--ink)}
.otab thead th{background:var(--orange);font-family:var(--head);font-size:12px;
  font-weight:900;letter-spacing:.05em;color:var(--ink)}
.otab tbody tr:last-child td{border-bottom:0}
.otab td.fill{color:var(--g400);background:var(--paper)}

/* ---------------- الختام ---------------- */
.close{justify-content:flex-end;background:var(--orange)}
.close .art{position:absolute;inset:0}
.close .art img{width:100%;height:100%;object-fit:cover;opacity:.26;display:block}
.close h2{font-size:54px;max-width:17ch}
.close .when{display:flex;gap:11px;flex-wrap:wrap;margin-top:22px}
.close .when span{background:var(--g900);color:var(--cream);border:3px solid var(--ink);
  border-radius:99px;padding:9px 18px;font-size:12.5px;font-weight:800;
  box-shadow:-4px 4px 0 var(--cream)}
.close .sig{display:flex;align-items:center;gap:14px;margin-top:22px;font-size:13px;
  font-weight:800;color:#4A2A05}
.close .sig img{height:30px}

.foot{position:absolute;inset-inline:58px;bottom:18px;display:flex;
  justify-content:space-between;font-size:11.5px;color:var(--g500);font-weight:600}
.pg.grey .foot{color:var(--g400)}
.pg.orange .foot{color:#6B4409}
"""
CSS = CSS.replace('--g500:#7D7greyA;', '--g500:#7D776A;')

# ---------------------------------------------------------------- الشرائح
FOOT = ('<div class="foot"><span>الجمعة البرتقالية ٢٠٢٦ — محطات درب</span>'
        '<span>@@n@@</span></div>')
AR = '٠١٢٣٤٥٦٧٨٩'
ard = lambda t: ''.join(AR[int(c)] if c.isdigit() else c for c in str(t))
n0 = lambda v: ard('{:,}'.format(int(v)).replace(',', '٬'))

SLIDES = []

# ٠ · الغلاف
SLIDES.append("""
<section class="pg cover">
  <div class="rays"></div>
  <img class="mark" src="%s" alt="الجمعة البرتقالية">
  <div class="when">١٠ – ١٥ نوفمبر ٢٠٢٦ · أسبوعك في كل محطات درب</div>
  <p class="tag">عرضك على كل مضخة، ودرب تسوّق له.</p>
  <div class="foot2"><span>محطات درب × شركاء خدمات السيارات</span>
    <img src="%s" alt="درب"></div>
</section>""" % (LOGO_OF, LOGO_DARB))

# ١ · المستهدفات
SLIDES.append("""
<section class="pg grey">
  <p class="eyebrow">المستهدفات</p>
  <h2>هدفان، وثلاثة أرقام نقيسها</h2>
  <div class="goals">
    <div class="goal">%s<span>بناء صورة ذهنية إيجابية عن الشريك</span></div>
    <div class="goal">%s<span>زيادة التفاعل والحضور الرقمي والميداني</span></div>
  </div>
  <div class="stats">
    <div class="stat2 rcard o"><div class="v">+٥٠٠٠</div><div class="k">عميل واتساب</div>
      <div class="u">رسالة فيها عرضك ومدته، ورابط يفعّله على طول</div></div>
    <div class="stat2 rcard"><div class="v">+١٠٠٠</div><div class="k">عميل مباشر</div>
      <div class="u">لكل شريك، من الكوبونات والباركود</div></div>
    <div class="stat2 rcard o"><div class="v">+٥ مليون</div><div class="k">مشاهدة</div>
      <div class="u">كل مشاهدات الحملة على حسابات درب</div></div>
  </div>
  %s
</section>""" % (icon('user', True), icon('eye', True), FOOT))

# ٢ · أرقام محطاتنا
REG = [('مكة · ٢٦ محطة', 34270), ('الطائف · ١٠ محطات', 12637),
       ('جازان · ١٠ محطات', 8114), ('جدة · ٧ محطات', 7391),
       ('الرياض · محطتان', 1976), ('الخرج · ٣ محطات', 1767),
       ('٧ مناطق أخرى', 4696)]
bars = ''.join('<div class="barrow"><span class="t">%s</span>'
               '<span class="track"><span class="fill" style="width:%.1f%%"></span></span>'
               '<span class="v">%s</span></div>' % (t, v / 34270.0 * 100, n0(v))
               for t, v in REG)
SLIDES.append("""
<section class="pg">
  <p class="eyebrow">أرقام محطاتنا</p>
  <h2 class="segs"><span>٦٩ محطة</span><span>١٣ منطقة</span><span>+٧٠ ألف سيارة يوميًا</span></h2>
  <div class="bignum"><b>٢٫١ مليون</b><span>تعبئة في الشهر</span></div>
  <div class="bars">%s</div>
  <div class="pills">
    <div class="pill">متوسط الفاتورة <b>٥٦٫٥ ر.س</b></div>
    <div class="pill"><b>٤٦٪</b> من الحركة بعد ٥ مساءً</div>
    <div class="pill">العرض يشتغل من الفتح للإغلاق</div>
  </div>
  %s
</section>""" % (bars, FOOT))

# ٣ · مراحل الحملة
PHASES = [('فيديوهات قبل البداية تشوّق الناس', 'إعلان', 'spark'),
          ('فيديو خاص بعرضك وسعره ومدته', 'إعلان', 'play'),
          ('مؤثّرون يوصلون عرضك للسائقين', 'إعلان', 'mic'),
          ('رسالة واتساب لأكثر من ٥٬٠٠٠ عميل، فيها رابط التفعيل', 'إعلان', 'chat'),
          ('١٠٠٠ كوبون باسمك يتسلّمه العميل عند المضخة', 'في المحطة', 'ticket'),
          ('لوحات ومطبوعات بعرضك داخل المحطة', 'في المحطة', 'sign')]
rows = ''.join('<div class="rowi">%s<span>%s</span><span class="tagx%s">%s</span></div>'
               % (icon(g, k == 'إعلان'), t, '' if k == 'إعلان' else ' f', k)
               for t, k, g in PHASES)
SLIDES.append("""
<section class="pg grey">
  <p class="eyebrow">مراحل الحملة</p>
  <h2>نشر يخلّي الناس تنتظر العرض، وتوزيع داخل المحطة يجيب العميل.</h2>
  <div class="rows" style="flex:1;justify-content:space-evenly">%s</div>
  %s
</section>""" % (rows, FOOT))

# ٤ · الآلية
STEPS = [('كوبون وباركود عند المضخة',
          'عامل المحطة يعطيه للعميل بعد التعبئة ويدلّه على مكانك.', 'طول اليوم', 'ticket'),
         ('العميل يمسح ويفعّل',
          'يختارك ويكتب رقم جواله، فتوصله رسالة تدلّه عليك.', 'أقل من دقيقة', 'scan'),
         ('موظفك يطبّق العرض',
          'العميل يوريه الرسالة، ويطبّق العرض على طول بلا أي إجراء.', 'عند الطلب', 'check'),
         ('نحسب ونرسل لك التقرير',
          'كل مسح ينحفظ، وتعرف بالضبط كم سيارة وصلتك.', 'تقرير كل أسبوع', 'chart')]
steps = ''.join('<div class="step rcard%s">%s<h3>%s</h3><p>%s</p>'
                '<span class="when">%s</span></div>'
                % (' o' if i == 0 else '', icon(g, i != 0), t, d, w)
                for i, (t, d, w, g) in enumerate(STEPS))
SLIDES.append("""
<section class="pg">
  <p class="eyebrow">الآلية</p>
  <h2>من المضخة إلى مغسلتك في أربع خطوات</h2>
  <div class="steps">%s</div>
  %s
</section>""" % (steps, FOOT))

# ٥ · نتائج ٢٠٢٥
SLIDES.append("""
<section class="pg orange" style="justify-content:center">
  <div class="rays" style="inset-inline-end:-300px;top:-300px"></div>
  <div class="year">٢٠٢٥</div>
  <div>
    <h2 style="font-size:56px">مو وعود.<br>هذي نتائج ٢٠٢٥.</h2>
    <p class="lede" style="margin-top:16px;font-size:17px">شركاء ومؤثّرون حقيقيون،
      وعدد المشاهدات ظاهر على كل مقطع.</p>
  </div>
  %s
</section>""" % FOOT)

# ٦ · المؤثّرون
SLIDES.append("""
<section class="pg grey">
  <p class="eyebrow">نتائج ٢٠٢٥</p>
  <h2 style="font-size:34px">وصلنا لعملائك عن طريق المؤثّرين</h2>
  <div class="chips" style="margin-top:16px">
    <div class="chip"><b>+١٠٠ ألف</b><span>مشاهدة في أسبوع</span></div>
    <div class="chip"><b>١١</b><span>محطة</span></div>
    <div class="chip"><b>١٠٠٠</b><span>كوبون لكل شريك</span></div>
  </div>
  <p class="lede">نفكّر ونكتب ونصوّر ونجهّز مقطعًا خاصًا لكل شريك. أمثلة حقيقية من حسابات درب:</p>
  <div class="grid6">%s</div>
</section>""" % ''.join('<img src="%s" alt="">' % c for c in CLIPS))

# ٧ · الشركاء
SLIDES.append("""
<section class="pg">
  <p class="eyebrow">شركاء ٢٠٢٥</p>
  <h2>شركاء كانوا معنا، وراجعين هذه السنة</h2>
  <p class="lede" style="margin-top:4px;font-weight:900;color:var(--orange-dk)">شركاء الحملة</p>
  <div class="logos" style="margin-top:10px">%s</div>
  <p class="lede" style="margin-top:auto;font-weight:900;color:var(--orange-dk)">محتوى المؤثّرين</p>
  <div class="grid6" style="margin-top:10px">%s</div>
</section>""" % (''.join('<img src="%s" alt="">' % c for c in LOGOS),
                 ''.join('<img src="%s" alt="" style="height:188px">' % c for c in INFL)))

# ٨ · المسؤوليات
DARB = ['التصوير والتصميم والمونتاج', 'إطلاق الحملة والنشر على المنصات',
        'طريقة التنفيذ والباركود وتدريب عمال المحطة',
        'التنسيق مع المؤثّرين وإدارة المحتوى', 'توزيع الكوبونات والتقرير الأسبوعي']
YOU = ['قيمة العرض أو الخصم',
       'الالتزام بالعرض طول ساعات العمل وتدريب موظفيك']
SLIDES.append("""
<section class="pg">
  <div class="split">
    <div class="half orange">
      <h2 style="font-size:34px">مسؤوليات درب</h2>
      <div class="rows" style="flex:1;justify-content:center">%s</div>
    </div>
    <div class="half grey">
      <h2 style="font-size:34px">مسؤوليات الشريك</h2>
      <div class="rows" style="flex:1;justify-content:center">%s</div>
    </div>
  </div>
</section>""" % (
    ''.join('<div class="rowi">%s<span>%s</span></div>' % (icon('check'), t) for t in DARB),
    ''.join('<div class="rowi"><span class="tagx" style="margin:0">%s</span>'
            '<span>%s</span></div>' % (ard(i + 1), t) for i, t in enumerate(YOU))))

# ٩ · الختام
SLIDES.append("""
<section class="pg close">
  <div class="art"><img src="%s" alt=""></div>
  <div>
    <p class="eyebrow">الجمعة البرتقالية ٢٠٢٦</p>
    <h2>كن شريكًا لنا وشاركنا النجاح.</h2>
    <div class="when">
      <span>نتفق قبل ٣٠ أكتوبر</span>
      <span>التصوير أول نوفمبر</span>
      <span>عرضك على كل مضخة ١٠ نوفمبر</span>
    </div>
    <div class="sig"><img src="%s" alt="درب">
      <span>فريق التسويق — محطات درب · marketing@darb.sa</span></div>
  </div>
</section>""" % (CLOSE_ART, LOGO_DARB))

# ١٠ · العروض المقترحة
SLIDES.append("""
<section class="pg">
  <p class="eyebrow">العروض المقترحة</p>
  <h2>اكتب عرضك هنا</h2>
  <p class="lede">السنة الماضية كان العرض: غسلة بعشرة ريالات مقابل تعبئة بثلاثين ريالًا أو أكثر.
    وأنت أدرى بما يناسبك — اكتب ما تقترحه.</p>
  <table class="otab">
    <thead><tr><th>العرض</th><th>السعر الاعتيادي</th><th>سعر الجمعة البرتقالية</th>
      <th>مقابل تعبئة بـ</th><th>عدد الكوبونات</th></tr></thead>
    <tbody>%s</tbody>
  </table>
  <div class="pills">
    <div class="pill"><b>المواقع:</b> داخل محطات درب، وفي فروعك</div>
  </div>
  %s
</section>""" % (''.join('<tr>' + '<td class="fill">…</td>' * 5 + '</tr>' for _ in range(4)),
                 FOOT))

DECK = ''.join(SLIDES)
_c = [0]


def _num(_m):
    _c[0] += 1
    return ard(_c[0])


import re
DECK = re.sub(r'@@n@@', _num, DECK)
assert '@@n@@' not in DECK

# ---------------------------------------------------- الشريط والمحرّر
src = open(CHROME_SRC, encoding='utf-8').read()
i = src.index('function darbEditor(opts){')
j = src.index('\n(function(){', i)
EDITOR = src[i:j]
assert 'function darbEditor' in EDITOR and len(EDITOR) > 6000, 'editor extract failed'
chrome_css = src.split('<style id="darbcss">', 1)[1].split('</style>', 1)[0]
CHROME = chrome_css[chrome_css.index('/* ---------- picker ----------'):]

BODY = """
<div class="bar">
  <div class="in">
    <button type="button" id="edit" class="ghost">تحرير</button>
    <button type="button" id="addpg" class="ghost" hidden>+ شريحة</button>
    <button type="button" id="undo" class="ghost" hidden disabled>↶ تراجع</button>
    <button type="button" id="redo" class="ghost" hidden disabled>↷ إعادة</button>
    <button type="button" id="reset" class="ghost" hidden>استعادة الأصل</button>
    <button type="button" id="dl">تنزيل الملف للشريك</button>
    <button type="button" class="ghost" id="pr">طباعة / PDF</button>
    <span class="savedot" id="savedot">جاهز</span>
    <span class="hint">اضغط «تحرير» عشان تعدّل أي كلام أو تحذفه أو تضيف شريحة، واضغط أي صورة عشان تبدّلها — والملف اللي ينزل للشريك يطلع بلا أزرار.</span>
  </div>
</div>
<div class="wrap"><div id="deck"></div></div>
<div class="blockbar" id="bb">
  <span class="kind" id="bbk">فقرة</span>
  <button type="button" data-a="img" class="img" hidden>استبدال الصورة</button>
  <button type="button" data-a="out" title="تحديد العنصر الأكبر">⤴</button>
  <button type="button" data-a="up" title="لأعلى">▲</button>
  <button type="button" data-a="down" title="لأسفل">▼</button>
  <button type="button" data-a="dup">تكرار</button>
  <button type="button" data-a="del" class="del">حذف</button>
</div>
<div class="toast" id="toast"><span id="toastmsg"></span>
  <button type="button" id="toastact" hidden></button></div>
<input type="file" id="pickimg" accept="image/*" hidden>"""

TOASTCSS = """
.toast{display:flex;align-items:center;gap:12px;line-height:1.75}
.toast.show{pointer-events:auto}
#toastmsg{max-width:62ch}
#toastact{background:var(--orange);color:var(--ink);border:0;border-radius:6px;
  padding:7px 15px;font:inherit;font-size:12.5px;font-weight:800;cursor:pointer;
  white-space:nowrap}
.bar{background:var(--g900) !important;border-bottom-color:var(--g700) !important}
.bar button{background:var(--orange) !important;color:var(--ink) !important}
.bar button.ghost{background:transparent !important;color:var(--g200) !important;
  border-color:var(--g700) !important}
"""

APP = """<script>
var DECK=%s;
var CSSTEXT=(function(){
  var mine=document.getElementById('darbcss');
  if(mine) return mine.outerHTML;
  var all=document.querySelectorAll('style'), out='';
  for(var i=0;i<all.length;i++)
    if(all[i].textContent.indexOf('.pg{')>=0) out+=all[i].outerHTML;
  return out || (all.length?all[all.length-1].outerHTML:'');
})();
%s
(function(){
  function clean(h){
    var t=document.createElement('div'); t.innerHTML=h;
    var n=t.querySelectorAll('[data-block]'), i;
    for(i=0;i<n.length;i++) n[i].removeAttribute('data-block');
    n=t.querySelectorAll('.hot'); for(i=0;i<n.length;i++) n[i].classList.remove('hot');
    n=t.querySelectorAll('[contenteditable]');
    for(i=0;i<n.length;i++) n[i].removeAttribute('contenteditable');
    return t.innerHTML;
  }
  function fileFor(html){
    return '<!doctype html>\\n<html lang="ar" dir="rtl">\\n<head>\\n<meta charset="utf-8">\\n'+
      '<meta name="viewport" content="width=device-width, initial-scale=1">\\n'+
      '<title>الجمعة البرتقالية ٢٠٢٦ — محطات درب</title>\\n'+CSSTEXT+'\\n</head>\\n<body>\\n'+
      '<div class="wrap"><div id="deck">'+clean(html)+'</div></div>\\n</body>\\n</html>\\n';
  }
  var ed=darbEditor({
    key:'darb-orange-friday-v2',
    load:function(){ return DECK; },
    download:function(api){
      api.send('darb-orange-friday', fileFor(api.box.innerHTML),
               'نُزّل ملف الجمعة البرتقالية جاهزًا للإرسال للشريك.');
    }
  });
  document.title='الجمعة البرتقالية ٢٠٢٦ — محطات درب';
  /* التصميم تغيّر بالكامل، فالمفتاح جديد. نسخة التصميم السابق تبقى محفوظة
     ولا تُحذف، ونخبرها بمكانها مرّة واحدة. */
  (function(){
    var seen=null; try{ seen=localStorage.getItem('darb-orange-friday-v2-note'); }catch(e){}
    if(seen) return;
    var prev=null; try{ prev=localStorage.getItem('darb-orange-friday-v1'); }catch(e){}
    try{ localStorage.setItem('darb-orange-friday-v2-note','1'); }catch(e){}
    if(!prev) return;
    ed.say('هذا تصميم جديد بهوية الجمعة البرتقالية. نسختك من التصميم السابق محفوظة '+
           'ولم تُحذف — قولي لي إن أردتِ نصًّا منها.', 13000);
  })();
})();
</script>"""

APP = APP % (json.dumps(DECK, ensure_ascii=False), EDITOR)

HTML = ('<!doctype html>\n<html lang="ar" dir="rtl">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>الجمعة البرتقالية ٢٠٢٦ — محطات درب</title>\n<style id="darbcss">\n'
        + CSS + '\n' + CHROME + '\n' + TOASTCSS + '</style>\n</head>\n<body>\n' + BODY
        + '\n' + APP + '\n</body>\n</html>\n')
open(OUT, 'w', encoding='utf-8').write(HTML)

art = HTML
for frag in ['<!doctype html>\n', '<html lang="ar" dir="rtl">\n', '<head>\n',
             '<meta charset="utf-8">\n',
             '<meta name="viewport" content="width=device-width, initial-scale=1">\n',
             '</head>\n', '<body>\n', '\n</body>', '\n</html>']:
    assert frag in art, 'wrapper fragment missing: ' + repr(frag)
    art = art.replace(frag, '', 1)
ANCHOR = "(function(){\n  function clean(h)"
art = art.replace(ANCHOR, "(function(){\n  document.documentElement.lang='ar';\n"
                  "  document.documentElement.dir='rtl';\n  function clean(h)", 1)
assert 'documentElement.lang' in art, 'lang injection failed'
open(ART, 'w', encoding='utf-8').write(art)

print('slides: %d' % DECK.count('<section class="pg'))
print('page: %d KB   artifact: %d KB' % (len(HTML) // 1024, len(art) // 1024))
