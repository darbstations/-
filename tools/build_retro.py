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
def webp(name):
    return 'data:image/webp;base64,%s' % b64(os.path.join(BRAND, name))


HERO = webp('hero.webp')            # الكولاج مقصوصًا
SCENE = webp('scene.webp')          # الكولاج داخل المحطة — غلاف العرض
CUT_STATION = webp('cut-station.webp')
CUT_FOLDER = webp('cut-folder.webp')
COVER_SCENE = webp('cover-scene.webp')      # مشهد الغلاف
PHONE_FOLDER = webp('phone-folder.webp')    # ملف الجوال والرسائل
MAP = webp('map.webp')                      # خريطة محطات درب
POSTER = webp('poster.webp')
FOLDER_TABS = webp('folder-tabs.webp')      # الملف بألسنة الأقسام
MARK = webp('mark.webp')                    # شعار الجمعة البرتقالية وحده
SCENE_FUEL = webp('scene-fuel.webp')
CUT_FUEL_FOLDER = webp('cut-fuel-folder.webp')
SCENE_CAR = webp('scene-car.webp')          # المشهد الخاص بخدمات السيارات
CUT_CAR_FOLDER = webp('cut-car-folder.webp')
CUT_CAR_STATION = webp('cut-car-station.webp')
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
    'wa':    '<path d="M16 4a12 12 0 00-10.4 18L4 28l6.2-1.6A12 12 0 1016 4z"/>'
             '<path d="M11.5 12.5c0 4 4 8 8 8l1.6-2-3-1.6-1.4 1.4a9 9 0 01-3-3l1.4-1.4-1.6-3z"/>',
    'star':  '<path d="M16 3.5l3.6 7.6 8.4 1.1-6.1 5.8 1.5 8.2L16 22.3 8.6 26.2l1.5-8.2L4 12.2l8.4-1.1z"/>',
    'camera':'<path d="M3 10h6l2-3h10l2 3h6v16H3z"/><circle cx="16" cy="17" r="5"/>',
    'send':  '<path d="M29 3L3 14l10 4 4 10z"/><path d="M29 3L13 18"/>',
    'burst': '<path d="M16 2v6M16 24v6M2 16h6M24 16h6M6.2 6.2l4.3 4.3M21.5 21.5l4.3 4.3'
             'M25.8 6.2l-4.3 4.3M10.5 21.5l-4.3 4.3"/><circle cx="16" cy="16" r="5"/>',
}


def icon(kind, fill=False, tone=None):
    g = GLYPH[kind]
    cls = 'ric' + (' ' + tone if tone else (' on' if fill else ''))
    return ('<span class="%s"><svg viewBox="0 0 32 32" aria-hidden="true">%s</svg></span>'
            % (cls, g))


CSS = FACES + """
:root{
  /* من الشعار نفسه */
  --orange:#FC6C05; --orange-dk:#C9500A; --orange-lt:#FFA24D;
  --cream:#FDF5DE;  --paper:#F4ECD9;  --card:#FBF4E2;  --ink:#141210;
  /* السلّم الرمادي */
  --g900:#2A2724; --g800:#39342F; --g700:#4A4540; --g500:#7D776A;
  --g400:#9B948A; --g300:#C2BBAE; --g200:#DED8C9; --g100:#EDE8DA;
  --head:"Araboto","Araboto Normal","Araboto Medium","OFHead",system-ui,sans-serif;
  --body:"DIN Next LT Arabic","DIN Next Arabic","DIN Next W23","OFBody",system-ui,sans-serif;
  /* ألوان ريترو مساندة للأيقونات */
  --teal:#2F6F69; --mustard:#E8A32C; --clay:#C4522E;
  /* سلّم المسافات — كل فراغ في العرض من هذه القيم لا من التخمين */
  --s1:8px; --s2:12px; --s3:16px; --s4:22px; --s5:30px; --s6:44px;
  --pad:46px 54px;
}
*{box-sizing:border-box}
html,body{margin:0;background:#1B1916;color:var(--ink);font-family:var(--body)}
h1,h2,h3{margin:0;font-family:var(--head);font-weight:900;letter-spacing:-.015em}
h2{font-size:38px;line-height:1.22;margin-bottom:var(--s2)}
h3{font-size:15px;line-height:1.35}
p{margin:0}
.wrap{padding:26px 18px 60px}

/* ---------------- الورقة ---------------- */
.pg{width:1120px;height:630px;margin:0 auto 22px;background:var(--paper);
  border-radius:12px;overflow:hidden;position:relative;display:flex;
  flex-direction:column;padding:var(--pad);
  box-shadow:0 20px 48px rgba(0,0,0,.45)}
.pg.grey{background:var(--g900);color:var(--cream)}
.pg.orange{background:var(--orange);color:#fff}
.pg > *{position:relative}

/* حبيبات ورق خفيفة — لا خطوط ولا أشعّة */
.pg::before{content:"";position:absolute;inset:0;pointer-events:none;opacity:.5;
  background-image:
    radial-gradient(circle at 18% 22%,rgba(20,18,16,.035) 0 2px,transparent 2px),
    radial-gradient(circle at 73% 61%,rgba(20,18,16,.03) 0 2px,transparent 2px),
    radial-gradient(circle at 44% 86%,rgba(20,18,16,.03) 0 2px,transparent 2px);
  background-size:53px 61px,67px 49px,41px 73px}
.pg.grey::before,.pg.orange::before{opacity:.28}

/* ---------------- عنوان القسم: استكر مائل ---------------- */
.eyebrow{display:inline-block;align-self:flex-start;font-family:var(--head);font-size:12px;
  font-weight:900;letter-spacing:.1em;background:var(--orange);color:#fff;
  border:2.5px solid var(--ink);border-radius:8px;padding:6px 15px;
  box-shadow:-3px 3px 0 var(--ink);margin-bottom:var(--s3)}
.pg.orange .eyebrow{background:var(--ink);color:#fff;border-color:var(--ink)}
.pg.grey .eyebrow{box-shadow:-3px 3px 0 var(--cream)}

.lede{font-size:15.5px;line-height:1.9;font-weight:500;color:var(--g700);max-width:72ch}
.pg.grey .lede{color:var(--g300)}
.pg.orange .lede{color:rgba(255,255,255,.92)}
.hl{background:var(--ink);color:#fff;padding:1px 10px;border-radius:7px;
  display:inline-block}

/* ---------------- الملف: بطاقة بلسان ---------------- */
.rcard{position:relative;background:var(--card);color:var(--ink);
  border-radius:3px 14px 14px 14px;padding:var(--s4);
  box-shadow:0 4px 0 rgba(20,18,16,.12), 0 14px 26px rgba(20,18,16,.16)}
.rcard .tab{position:absolute;top:-22px;inset-inline-end:22px;background:inherit;
  padding:6px 20px 7px;border-radius:11px 11px 0 0;font-family:var(--head);
  font-weight:900;font-size:12px;letter-spacing:.04em;color:inherit;white-space:nowrap}
.rcard.o{background:var(--orange);color:#fff}
.rcard.d{background:var(--g900);color:var(--cream)}
.pg.orange .rcard{box-shadow:0 4px 0 rgba(20,18,16,.22), 0 14px 26px rgba(20,18,16,.26)}

/* ميلان خفيف يعطي إحساس القصاصات */
.tilt-2{transform:rotate(-2deg)} .tilt-1{transform:rotate(-1deg)}
.tilt1{transform:rotate(1deg)}   .tilt2{transform:rotate(2deg)}

/* شريط لاصق */
.tape{position:absolute;width:118px;height:29px;z-index:2;
  background:rgba(255,255,255,.5);box-shadow:0 2px 7px rgba(20,18,16,.14);
  clip-path:polygon(3% 0,97% 3%,100% 100%,0 97%)}
.pg.grey .tape{background:rgba(253,245,222,.17)}

/* حافّة ممزّقة أسفل القصاصة */
.torn::after{content:"";position:absolute;inset-inline:0;bottom:-9px;height:10px;
  background:inherit;
  clip-path:polygon(0 0,5% 72%,10% 8%,15% 80%,20% 18%,25% 74%,30% 12%,35% 84%,
    40% 22%,45% 70%,50% 8%,55% 80%,60% 18%,65% 76%,70% 10%,75% 82%,80% 20%,
    85% 72%,90% 12%,95% 78%,100% 16%,100% 0)}

/* استكر */
.sticker{display:inline-block;background:var(--orange);color:#fff;
  border:3px solid var(--ink);border-radius:10px;padding:7px 16px;
  font-family:var(--head);font-weight:900;box-shadow:-4px 4px 0 var(--ink)}

/* مشبك ورق */
.clip{position:absolute;top:-16px;inset-inline-start:22px;width:20px;height:44px;
  border:3px solid var(--g400);border-radius:11px;border-bottom-color:transparent;z-index:3}

/* قصاصة مصوّرة ملصقة على الشريحة — خلف النص دائمًا */
.snap{position:absolute;border:7px solid var(--cream);border-radius:3px;
  box-shadow:0 10px 26px rgba(20,18,16,.4);object-fit:cover;z-index:0}

/* صفّ بعمود صورة مخصّص: لا يتقاطع مع الكلام أبدًا */
.withpic{display:grid;grid-template-columns:1fr 296px;gap:var(--s5);flex:1;
  align-items:center;margin-top:var(--s4)}
.withpic > div{display:flex;flex-direction:column;justify-content:center;gap:var(--s4)}
.withpic .rows{margin-top:0}
.withpic .pills{margin-top:0}
.picside{width:100%;height:auto;max-height:340px;object-fit:cover;
  border:7px solid var(--cream);border-radius:3px;
  box-shadow:0 10px 26px rgba(20,18,16,.38);transform:rotate(-1.6deg)}

/* ---------------- الأيقونات ---------------- */
.ric{width:42px;height:42px;flex:0 0 42px;border:3px solid var(--ink);border-radius:11px;
  background:var(--cream);display:flex;align-items:center;justify-content:center;
  box-shadow:-3px 3px 0 var(--ink)}
.ric.on{background:var(--orange)}
.ric.c1{background:var(--orange)} .ric.c2{background:var(--mustard)}
.ric.c3{background:var(--teal)}   .ric.c4{background:var(--clay)}
.ric.c3 svg,.ric.c4 svg{stroke:#fff}
.ric svg{width:22px;height:22px;fill:none;stroke:var(--ink);stroke-width:2.6;
  stroke-linecap:round;stroke-linejoin:round}
.pg.grey .ric{box-shadow:-3px 3px 0 var(--cream)}
.pg.orange .ric{background:#fff}

/* ---------------- الغلاف ---------------- */
.cover{padding:0;background:var(--g900);justify-content:flex-end}
.cover .scene{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block}
.cover .veil{position:absolute;inset:0;background:linear-gradient(to top,
  rgba(20,18,16,.93) 0%,rgba(20,18,16,.78) 30%,rgba(20,18,16,.25) 58%,rgba(20,18,16,0) 78%)}
.cover .in{position:relative;padding:0 56px 34px;display:flex;flex-direction:column;
  align-items:flex-start;text-align:right}
.cover h1{font-family:var(--head);font-weight:900;font-size:38px;line-height:1.24;
  color:#fff;max-width:22ch;margin:0 0 var(--s3)}
.cover .when{margin-top:var(--s3);background:var(--orange);color:#fff;
  border:3px solid var(--ink);border-radius:10px;padding:10px 22px;font-weight:900;
  font-family:var(--head);font-size:14px;box-shadow:-4px 4px 0 var(--ink);
  align-self:flex-start}
.cover .mark{width:186px;height:auto;display:block;margin-bottom:var(--s3)}
.cover .foot2{display:flex;align-items:center;gap:13px;margin-top:var(--s4);
  font-size:12.5px;color:var(--g300);font-weight:700}
.cover .foot2 img{height:24px}

/* ---------------- الأرقام ---------------- */
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:var(--s4);margin-top:auto}
.stat2 .v{font-family:var(--head);font-size:48px;font-weight:900;line-height:1;
  font-variant-numeric:tabular-nums}
.stat2 .k{font-size:14.5px;font-weight:800;margin-top:9px}
.stat2 .u{font-size:12.5px;line-height:1.7;margin-top:7px;color:var(--g700)}
.rcard.d .u,.rcard.o .u{color:inherit;opacity:.88}

.goals{display:grid;grid-template-columns:1fr 1fr;gap:var(--s4);margin-top:var(--s4)}
.goal{display:flex;align-items:center;gap:15px;font-size:15.5px;font-weight:700}
.stat2 .ric{margin-bottom:var(--s2)}

.bignum{display:flex;align-items:baseline;gap:12px;margin-top:6px}
.bignum b{font-family:var(--head);font-size:54px;font-weight:900;color:var(--orange-dk);
  line-height:1;font-variant-numeric:tabular-nums}
.bignum span{font-size:14px;color:var(--g700);font-weight:700}
.segs{display:flex;flex-wrap:wrap;align-items:baseline}
.segs > span + span::before{content:"";display:inline-block;width:7px;height:7px;
  margin:0 13px;background:var(--orange);border:2px solid var(--ink);border-radius:2px;
  vertical-align:middle;transform:rotate(45deg)}

.bars{display:flex;flex-direction:column;gap:var(--s2);margin-top:var(--s4)}
.barrow{display:grid;grid-template-columns:150px 1fr 82px;align-items:center;gap:14px;
  font-size:13.5px}
.barrow .t{font-weight:700}
.barrow .track{display:block;height:19px;background:var(--g100);
  border:2.5px solid var(--ink);border-radius:4px;overflow:hidden}
.barrow .fill{display:block;height:100%;background:var(--orange)}
.barrow .v{text-align:left;font-weight:900;font-variant-numeric:tabular-nums;
  font-family:var(--head)}

.pills{display:flex;flex-wrap:wrap;gap:var(--s2);margin-top:auto}
.pill{background:var(--card);border:2.5px solid var(--ink);border-radius:8px;
  padding:9px 17px;font-size:13px;font-weight:700;box-shadow:-3px 3px 0 var(--ink)}
.pill b{font-weight:900;font-family:var(--head)}
.pg.grey .pill{background:var(--g800);color:var(--cream);box-shadow:-3px 3px 0 var(--cream)}
.pg.orange .pill{background:#fff}

/* ---------------- صفوف ---------------- */
.rows{display:flex;flex-direction:column;gap:var(--s2);margin-top:var(--s3)}
.rowi{display:flex;align-items:center;gap:14px;font-size:14.5px;font-weight:600}
.rowi .tagx{margin-inline-start:auto;font-size:11px;font-weight:900;font-family:var(--head);
  border:2.5px solid var(--ink);border-radius:7px;padding:4px 13px;background:var(--orange);
  color:#fff;white-space:nowrap;box-shadow:-3px 3px 0 var(--ink)}
.rowi .tagx.f{background:var(--card);color:var(--ink)}
.rowi.slip{background:var(--card);color:var(--ink);border-radius:3px 11px 11px 11px;
  padding:13px 17px;box-shadow:0 3px 0 rgba(20,18,16,.16),0 10px 20px rgba(20,18,16,.2)}
.rowi.slip .num{width:30px;height:30px;flex:0 0 30px;border:2.5px solid var(--ink);
  border-radius:8px;background:var(--orange);color:#fff;display:flex;align-items:center;
  justify-content:center;font-family:var(--head);font-weight:900;font-size:13px}
.pg.grey .rowi .tagx{box-shadow:-3px 3px 0 var(--cream)}

/* ---------------- خطوات ---------------- */
.steps{display:grid;grid-template-columns:repeat(4,1fr);gap:var(--s3);margin-top:auto}
.step{display:flex;flex-direction:column;gap:11px}
.step p{font-size:12.5px;line-height:1.7;color:var(--g700);font-weight:500}
.step.o p,.step.d p{color:inherit;opacity:.88}
.step .when{font-size:11px;font-weight:900;font-family:var(--head);color:var(--orange-dk);
  margin-top:auto}
.step.o .when{color:#fff}

/* ---------------- نصفان ---------------- */
.split{display:grid;grid-template-columns:1fr 1fr;flex:1;margin:-46px -54px;
  align-items:stretch}
.half{padding:var(--pad);display:flex;flex-direction:column;position:relative}
.half.orange{background:var(--orange);color:#fff}
.half.grey{background:var(--g900);color:var(--cream)}
.half.orange .eyebrow{background:var(--ink)}
.half.grey .rowi .tagx{box-shadow:-3px 3px 0 var(--cream)}
.half.orange .ric{background:#fff}

/* ---------------- صور: قصاصات بشريط لاصق ---------------- */
.grid6{display:grid;grid-template-columns:repeat(6,1fr);gap:var(--s3);margin-top:auto}
.grid6 img{width:100%;height:198px;object-fit:cover;border:5px solid var(--cream);
  border-radius:3px;display:block;box-shadow:0 5px 14px rgba(20,18,16,.3)}
.grid6 > *:nth-child(odd) img{transform:rotate(-1.4deg)}
.grid6 > *:nth-child(even) img{transform:rotate(1.2deg)}
.logos{display:grid;grid-template-columns:repeat(6,1fr);gap:var(--s3);margin-top:var(--s2)}
.logos img{width:100%;height:94px;object-fit:contain;background:#fff;
  border:5px solid var(--cream);border-radius:3px;padding:8px;display:block;
  box-shadow:0 5px 14px rgba(20,18,16,.22)}
.logos > *:nth-child(odd) img{transform:rotate(1.2deg)}
.logos > *:nth-child(even) img{transform:rotate(-1.5deg)}
.chips{display:flex;gap:var(--s3);margin-bottom:var(--s3)}
.chip{border:3px solid var(--ink);border-radius:10px;padding:12px 20px;text-align:center;
  background:var(--card);color:var(--ink);box-shadow:-4px 4px 0 var(--orange)}
.chip b{display:block;font-family:var(--head);font-size:24px;font-weight:900;
  font-variant-numeric:tabular-nums}
.chip span{font-size:11.5px;color:var(--g700);font-weight:700}

/* ---------------- شريحة النتائج: ورق، والسنة إلى اليسار ---------------- */
.pg.sheet{background:var(--paper);color:var(--ink);
  display:grid;grid-template-columns:1fr 360px;align-items:center;gap:var(--s6)}
.pg.sheet .year{font-family:var(--head);font-size:150px;font-weight:900;line-height:.92;
  color:var(--orange);text-align:center;
  text-shadow:-5px 5px 0 var(--ink);letter-spacing:-.03em}
.pg.sheet .yearbox{border:3px solid var(--ink);border-radius:3px 16px 16px 16px;
  background:var(--cream);padding:var(--s5) var(--s3);
  box-shadow:0 5px 0 rgba(20,18,16,.14), 0 16px 30px rgba(20,18,16,.18);position:relative}
.pg.sheet .yearbox .tab{position:absolute;top:-22px;inset-inline-end:24px;
  background:var(--cream);border:3px solid var(--ink);border-bottom:0;
  padding:5px 18px 7px;border-radius:11px 11px 0 0;font-family:var(--head);
  font-weight:900;font-size:12px}
.pg.sheet .yearbox .sub{text-align:center;font-size:13px;font-weight:800;
  color:var(--g700);margin-top:var(--s2)}

h2.withic{display:flex;align-items:center;gap:var(--s2)}
h2.withic .ric{width:46px;height:46px;flex:0 0 46px}
h2.withic .ric svg{width:25px;height:25px}
.ofmark{height:52px;width:auto;margin-inline-start:auto;display:block}

/* ---------------- جدول العروض ---------------- */
.otab{border-collapse:separate;border-spacing:0;width:100%;font-size:14px;
  background:var(--card);border:3px solid var(--ink);border-radius:3px 14px 14px 14px;
  overflow:hidden;margin-top:18px;box-shadow:0 5px 0 rgba(20,18,16,.12),
  0 14px 26px rgba(20,18,16,.16)}
.otab th,.otab td{padding:13px 16px;text-align:right;border-bottom:2px solid var(--ink)}
.otab thead th{background:var(--orange);font-family:var(--head);font-size:12px;
  font-weight:900;letter-spacing:.04em;color:#fff}
.otab tbody tr:last-child td{border-bottom:0}
.otab td.fill{color:var(--g400);background:var(--paper)}

/* ---------------- الختام ---------------- */
.close{justify-content:flex-end;background:var(--ink);color:#fff}
.close .art{position:absolute;inset:0;overflow:hidden}
.close .art img{width:100%;height:100%;object-fit:cover;display:block;
  filter:blur(5px);transform:scale(1.05)}   /* التكبير يمنع ظهور حواف الضباب */
.close .art::after{content:"";position:absolute;inset:0;background:rgba(0,0,0,.2)}
/* تدرّج أسفل الشريحة وحده، ليُقرأ الكلام والصورة فوقه ظاهرة */
.close .art::before{content:"";position:absolute;inset:0;z-index:1;
  background:linear-gradient(to top,rgba(0,0,0,.82) 0%,rgba(0,0,0,.45) 38%,
    rgba(0,0,0,0) 66%)}
.close h2{font-size:46px;max-width:none;white-space:nowrap;color:#fff}
.close .when{display:flex;gap:11px;flex-wrap:wrap;margin-top:22px}
.close .when span{background:#fff;color:var(--ink);border:3px solid var(--ink);
  border-radius:8px;padding:9px 18px;font-size:12.5px;font-weight:800;
  box-shadow:-4px 4px 0 var(--ink)}
.close > div{position:relative;z-index:2}
.close .sig{display:flex;align-items:center;gap:14px;margin-top:22px;font-size:13px;
  font-weight:800;color:#fff}
.close .sig img{height:30px}

.foot{position:absolute;inset-inline:54px;bottom:14px;display:flex;align-items:center;
  gap:10px;font-size:11.5px;color:var(--g500);font-weight:600}
.foot .fmark{display:block;width:38px;height:23px;background-size:contain;
  background-repeat:no-repeat;background-position:center;
  background-image:url("@@MARKCSS@@")}
.foot span:last-child{margin-inline-start:auto}
.pg.grey .foot{color:var(--g400)}
.pg.orange .foot{color:rgba(255,255,255,.72)}
"""

CSS = CSS.replace('@@MARKCSS@@', MARK)
assert '@@MARKCSS@@' not in CSS

# ---------------------------------------------------------------- الشرائح
FOOT = ('<div class="foot"><span class="fmark"></span>'
        '<span>الجمعة البرتقالية ٢٠٢٦ — محطات درب</span>'
        '<span>@@n@@</span></div>')
AR = '٠١٢٣٤٥٦٧٨٩'
ard = lambda t: ''.join(AR[int(c)] if c.isdigit() else c for c in str(t))
n0 = lambda v: ard('{:,}'.format(int(v)).replace(',', '٬'))

SLIDES = []

# ٠ · الغلاف
SLIDES.append("""
<section class="pg cover">
  <img class="scene" src="@@COVER@@" alt="الجمعة البرتقالية في محطات درب">
  <div class="veil"></div>
  <div class="in">
    <img class="mark" src="@@MARK@@" alt="الجمعة البرتقالية">
    <h1>عرضك على كل مضخة، ودرب تسوّق له.</h1>
    <div class="when">١٠ – ١٥ نوفمبر ٢٠٢٦ · أسبوعك في كل محطات درب</div>
    <div class="foot2"><img src="%s" alt="درب">
      <span>محطات درب × شركاء خدمات السيارات</span></div>
  </div>
</section>""" % LOGO_DARB)

# ١ · المستهدفات
SLIDES.append("""
<section class="pg grey">
  <p class="eyebrow">المستهدفات</p>
  <h2>أهداف الحملة وأرقامها</h2>
  <p class="lede">هدفان نعمل عليهما، وثلاثة أرقام نقيسها لك في نهاية الأسبوع.</p>
  <div class="goals">
    <div class="goal rcard"><span class="tab">الهدف الأول</span>%s
      <span>بناء صورة ذهنية إيجابية عن الشريك</span></div>
    <div class="goal rcard"><span class="tab">الهدف الثاني</span>%s
      <span>زيادة التفاعل والحضور الرقمي والميداني</span></div>
  </div>
  <div class="stats">
    <div class="stat2 rcard o"><span class="tab">واتساب</span>%s
      <div class="v">+٥٠٠٠</div><div class="k">عميل واتساب</div>
      <div class="u">رسالة فيها عرضك ومدته، ورابط يفعّله على طول</div></div>
    <div class="stat2 rcard"><span class="tab">مباشر</span>%s
      <div class="v">+١٠٠٠</div><div class="k">عميل مباشر</div>
      <div class="u">لكل شريك، من الكوبونات والباركود</div></div>
    <div class="stat2 rcard o"><span class="tab">مشاهدات</span>%s
      <div class="v">+٥ مليون</div><div class="k">مشاهدة</div>
      <div class="u">كل مشاهدات الحملة على حسابات درب</div></div>
  </div>
  %s
</section>""" % (icon('star', tone='c2'), icon('mic', tone='c3'),
                icon('wa', tone='c1'), icon('user', tone='c2'), icon('eye', tone='c3'), FOOT))

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
  <div class="withpic">
    <div>
      <div class="bars" style="margin-top:0">%s</div>
      <div class="pills">
        <div class="pill">متوسط الفاتورة <b>٥٦٫٥ ر.س</b></div>
        <div class="pill"><b>٤٦٪</b> من الحركة بعد ٥ مساءً</div>
      </div>
    </div>
    <img class="picside" src="@@STATION@@" alt="محطة درب">
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
TONES = ['c1', 'c2', 'c3', 'c1', 'c4', 'c2']
rows = ''.join('<div class="rowi">%s<span>%s</span><span class="tagx%s">%s</span></div>'
               % (icon(g, tone=TONES[i]), t, '' if k == 'إعلان' else ' f', k)
               for i, (t, k, g) in enumerate(PHASES))
SLIDES.append("""
<section class="pg grey">
  <p class="eyebrow">مراحل الحملة</p>
  <h2>نشر يخلّي الناس تنتظر العرض، وتوزيع داخل المحطة يجيب العميل.</h2>
  <div class="withpic">
    <div class="rows" style="margin-top:0;gap:var(--s2)">%s</div>
    <img class="picside tilt1" src="@@STATION2@@" alt="محطة درب">
  </div>
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
steps = ''.join('<div class="step rcard%s %s"><span class="tab">%s</span>%s'
                '<h3>%s</h3><p>%s</p><span class="when">%s</span></div>'
                % (' o' if i == 0 else '', ['tilt-1','tilt1','tilt-2','tilt1'][i],
                   ard(i + 1), icon(g, tone=['c2','c3','c1','c4'][i]), t, d, w)
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
<section class="pg sheet">
  <div>
    <p class="eyebrow">نتائج الحملة الماضية</p>
    <h2 style="font-size:50px">مو وعود.<br>هذي نتائج ٢٠٢٥.</h2>
    <p class="lede" style="margin-top:var(--s3);font-size:16.5px">شركاء ومؤثّرون حقيقيون،
      وعدد المشاهدات ظاهر على كل مقطع — تشوفها بنفسك في الصفحات التالية.</p>
    <div class="pills" style="margin-top:var(--s5)">
      <div class="pill"><b>+١٠٠ ألف</b> مشاهدة في أسبوع</div>
      <div class="pill"><b>١١</b> محطة</div>
      <div class="pill"><b>١٠٠٠</b> كوبون لكل شريك</div>
    </div>
  </div>
  <div class="yearbox"><span class="tab">الحملة الماضية</span>
    <div class="year">٢٠٢٥</div>
    <div class="sub">الجمعة البرتقالية</div></div>
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
DARB = [('التصوير والتصميم والمونتاج', 'camera'),
        ('إطلاق الحملة والنشر على المنصات', 'send'),
        ('طريقة التنفيذ والباركود وتدريب عمال المحطة', 'scan'),
        ('التنسيق مع المؤثّرين وإدارة المحتوى', 'mic'),
        ('توزيع الكوبونات والتقرير الأسبوعي', 'ticket')]
DARB_TONES = ['c1', 'c2', 'c3', 'c4', 'c1']
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
    ''.join('<div class="rowi slip">%s<span>%s</span></div>'
            % (icon(g, tone=DARB_TONES[i]), t)
            for i, (t, g) in enumerate(DARB)),
    ''.join('<div class="rowi slip %s"><span class="num">%s</span><span>%s</span></div>'
            % ('', ard(i + 1), t) for i, t in enumerate(YOU))))

# ٩ · الختام
SLIDES.append("""
<section class="pg close">
  <div class="art"><img src="@@SCENE@@" alt=""></div>
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
</section>""" % LOGO_DARB)

# ١٠ · العروض المقترحة
SLIDES.append("""
<section class="pg">
  <p class="eyebrow">العروض المقترحة</p>
  <h2 class="withic">%s<span>اكتب عرضك هنا</span></h2>
  <p class="lede">السنة الماضية كان العرض: غسلة بعشرة ريالات مقابل تعبئة بثلاثين ريالًا أو أكثر.
    وأنت أدرى بما يناسبك — اكتب ما تقترحه.</p>
  <table class="otab">
    <thead><tr><th>العرض</th><th>السعر الاعتيادي</th><th>سعر الجمعة البرتقالية</th>
      <th>مقابل تعبئة بـ</th><th>عدد الكوبونات</th></tr></thead>
    <tbody>%s</tbody>
  </table>
  <div class="pills" style="align-items:center">
    <div class="pill"><b>المواقع:</b> داخل محطات درب، وفي فروعك</div>
    <img class="ofmark" src="@@MARK@@" alt="الجمعة البرتقالية">
  </div>
  %s
</section>""" % (icon('burst', tone='c1'),
                 ''.join('<tr>' + '<td class="fill">…</td>' * 5 + '</tr>' for _ in range(4)),
                 FOOT))

DECK = ''.join(SLIDES)
for mark, val in [('@@STATION@@', MAP), ('@@STATION2@@', PHONE_FOLDER),
                  ('@@SCENE@@', SCENE_CAR), ('@@COVER@@', COVER_SCENE),
                  ('@@MARK@@', MARK)]:
    assert mark in DECK, 'snap marker missing: ' + mark
    DECK = DECK.replace(mark, val)
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
