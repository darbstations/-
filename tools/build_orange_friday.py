# -*- coding: utf-8 -*-
"""ملف الجمعة البرتقالية بالمحتوى المُعاد صياغته.

التصميم كما في عرضها: البرتقالي #E9760C والداكن #1A1917 والكريمي #FBF6F0،
والصور مأخوذة من ملفها نفسه. النص هو الصياغة الجديدة: عناوين أقصر تدخل
صناديقها، ولسان واحد فصيح، ونطاق مكتوب لكل رقم.

الأدوات هي أدوات ملفات المحطات نفسها — تحرير وتراجع وإعادة واستبدال صورة
وتنزيل — والملف الذي ينزل للشريك يخرج نظيفًا بلا أزرار.
"""
import base64
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MEDIA = os.path.join(HERE, 'orangefriday', 'media')
CHROME_SRC = '/home/user/-/darb-carwash-slides.html'
OUT = '/home/user/-/darb-orange-friday.html'
ART = '/home/user/-/darb-orange-friday-artifact.html'


def img(name):
    p = os.path.join(MEDIA, name)
    ext = 'png' if name.endswith('.png') else 'jpeg'
    with open(p, 'rb') as f:
        return 'data:image/%s;base64,%s' % (ext, base64.b64encode(f.read()).decode())


LOGO = img('image-1-1.png')
STATION = img('image-1-2.jpeg')
PHONE = img('image-7-1.jpeg')
CLOSE_ART = img('image-15-1.jpeg')
CLIPS = [img('image-12-%d.jpeg' % i) for i in range(1, 7)]
LOGOS = [img('image-13-%d.jpeg' % i) for i in range(1, 7)]
INFL = [img('image-13-%d.jpeg' % i) for i in range(7, 13)]

CSS = """
:root{
  --orange:#E9760C; --orange-dk:#C85E05; --ink:#1A1917; --ink-2:#4A443D;
  --cream:#FBF6F0; --sand:#F2E7D8; --line:#E0D0BA; --white:#fff;
}
*{box-sizing:border-box}
html,body{margin:0;background:#231E18;color:var(--ink);
  font-family:"Noto Naskh Arabic","Segoe UI",Tahoma,system-ui,sans-serif}
h1,h2,h3{margin:0;line-height:1.18;font-weight:800}
p{margin:0}
.wrap{padding:26px 18px 60px}

/* ---------- the sheet ---------- */
.pg{width:1120px;height:630px;margin:0 auto 22px;background:var(--cream);
  border-radius:10px;overflow:hidden;position:relative;display:flex;
  flex-direction:column;padding:52px 60px;
  box-shadow:0 18px 44px rgba(0,0,0,.38)}
.pg.orange{background:var(--orange);color:var(--ink)}
.pg.dark{background:var(--ink);color:var(--cream)}
.pg .eyebrow{font-size:12px;letter-spacing:.18em;font-weight:800;color:var(--orange);
  margin-bottom:14px}
.pg.orange .eyebrow{color:var(--ink)}
.pg.dark .eyebrow{color:var(--orange)}
.pg h2{font-size:40px;margin-bottom:14px}
.pg .lede{font-size:15.5px;line-height:1.85;color:var(--ink-2);max-width:74ch}
.pg.dark .lede{color:#CFC6BA}
.pg.orange .lede{color:#4A2E09}
.hl{background:var(--orange);color:#fff;padding:0 10px;border-radius:4px}
.pg.orange .hl{background:var(--ink);color:var(--orange)}

/* ---------- cover ---------- */
.cover{flex-direction:row;gap:46px;align-items:stretch;padding:40px 48px}
.cover .shot{width:330px;flex:0 0 330px;border-radius:8px;overflow:hidden;
  position:relative;background:#2A2520}
.cover .shot img{width:100%;height:100%;object-fit:cover;display:block}
.cover .shot .stat{position:absolute;inset-inline:16px;bottom:16px;background:rgba(20,18,16,.9);
  border-radius:8px;padding:14px 18px;display:flex;align-items:baseline;
  justify-content:space-between;gap:12px;color:#fff}
.cover .shot .stat b{font-size:30px;font-weight:800;font-variant-numeric:tabular-nums}
.cover .shot .stat span{font-size:11.5px;color:#C6B29A}
.cover .side{flex:1;display:flex;flex-direction:column}
.cover .top{display:flex;align-items:center;justify-content:space-between;gap:14px}
.cover .top span{font-size:12.5px;color:#4A2E09;font-weight:700}
.cover .top img{height:30px;width:auto}
.cover .when{display:inline-block;align-self:flex-start;background:var(--ink);color:#fff;
  border-radius:99px;padding:9px 20px;font-size:12.5px;font-weight:700;margin-top:auto}
.cover h1{font-size:92px;line-height:1.02;margin-top:16px;letter-spacing:-.01em}
.cover h1 .b{display:block;color:#fff}
.cover .tag{margin-top:18px;font-size:17px;font-weight:700;color:#4A2E09}

/* ---------- bits ---------- */
.pills{display:flex;flex-wrap:wrap;gap:10px;margin-top:auto}
.pill{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.2);
  border-radius:99px;padding:10px 18px;font-size:13.5px}
.pill b{font-weight:800}
.pg.cream .pill,.pg:not(.dark):not(.orange) .pill{background:var(--sand);
  border-color:var(--line);color:var(--ink)}
.pg.orange .pill{background:rgba(26,25,23,.12);border-color:rgba(26,25,23,.22);color:var(--ink)}

.split{display:grid;grid-template-columns:1fr 1fr;gap:0;flex:1;
  margin:-52px -60px;align-items:stretch}
.split > div{padding:52px 54px;display:flex;flex-direction:column}
.half{padding:52px 54px;display:flex;flex-direction:column}
.half.orange{background:var(--orange);color:var(--ink)}
.half.dark{background:var(--ink);color:var(--cream)}
.half.orange .eyebrow{color:var(--ink)}
.half.dark .eyebrow{color:var(--orange)}
.half.dark .lede{color:#CFC6BA}

.cards{display:grid;gap:16px;margin-top:auto}
.card{border-radius:10px;padding:22px 24px}
.card.w{background:#fff;color:var(--ink)}
.card.d{background:var(--ink);color:var(--cream)}
.card.o{background:var(--orange);color:#fff}
.card .n{width:30px;height:30px;border-radius:50%;background:var(--orange);color:#fff;
  display:flex;align-items:center;justify-content:center;font-weight:800;font-size:14px;
  flex:0 0 30px}
.card.o .n{background:var(--ink)}
.card.row{display:flex;align-items:center;gap:14px;font-size:15.5px;font-weight:700}

.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:auto}
.goals{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:auto}
.goal{display:flex;align-items:center;gap:13px;font-size:15.5px;font-weight:700;
  background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.16);
  border-radius:10px;padding:16px 20px}
.goal .n{width:28px;height:28px;flex:0 0 28px;border-radius:50%;background:var(--orange);
  color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800;
  font-size:13px}
.stat2{border-radius:10px;padding:26px 24px}
.stat2 .v{font-size:52px;font-weight:800;line-height:1;font-variant-numeric:tabular-nums}
.stat2 .k{font-size:15px;font-weight:800;margin-top:10px}
.stat2 .u{font-size:12.5px;line-height:1.7;margin-top:8px;opacity:.82}

/* ---------- bars ---------- */
.bars{margin-top:20px;display:flex;flex-direction:column;gap:14px}
.barrow{display:grid;grid-template-columns:120px 1fr 80px;align-items:center;gap:14px;
  font-size:13.5px}
.barrow .t{font-weight:700}
.barrow .track{display:block;height:18px;background:var(--sand);border-radius:99px;
  overflow:hidden}
.barrow .fill{display:block;height:100%;background:var(--orange);border-radius:99px}
.barrow .v{text-align:left;font-weight:800;font-variant-numeric:tabular-nums}
.bignum{display:flex;align-items:baseline;gap:12px;margin-top:6px}
.bignum b{font-size:58px;font-weight:800;color:var(--orange);line-height:1;
  font-variant-numeric:tabular-nums}
.bignum span{font-size:14px;color:var(--ink-2);font-weight:700}
.segs{display:flex;flex-wrap:wrap;align-items:baseline;gap:0}
.segs > span{display:inline-block}
.segs > span + span::before{content:"·";display:inline-block;padding:0 12px;
  color:var(--orange);font-weight:800}

/* ---------- steps / phases ---------- */
.rows{display:flex;flex-direction:column;gap:10px;margin-top:18px}
.rowi{display:flex;align-items:center;gap:14px;font-size:14.5px;
  border-bottom:1px solid rgba(255,255,255,.12);padding-bottom:10px}
.pg:not(.dark) .rowi{border-color:var(--line)}
.rowi .tagx{margin-inline-start:auto;font-size:11px;font-weight:800;border-radius:99px;
  padding:4px 12px;background:var(--orange);color:#fff;white-space:nowrap}
.rowi .tagx.f{background:#3E7D5D}

.steps{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-top:auto}
.step{border-radius:10px;padding:20px;background:#fff;border:1px solid var(--line);
  display:flex;flex-direction:column;gap:10px}
.step:first-child{background:var(--ink);color:var(--cream);border-color:var(--ink)}
.step .n{width:28px;height:28px;border-radius:50%;background:var(--orange);color:#fff;
  display:flex;align-items:center;justify-content:center;font-weight:800;font-size:13px}
.step h3{font-size:15px}
.step p{font-size:12.5px;line-height:1.7;color:var(--ink-2)}
.step:first-child p{color:#CFC6BA}
.step .when{font-size:11px;font-weight:800;color:var(--orange);margin-top:auto}

/* ---------- offer ---------- */
.offer{display:grid;grid-template-columns:1fr 54px 1fr;align-items:center;gap:18px;
  margin-top:auto}
.offer .box{border-radius:12px;padding:34px 30px;text-align:center}
.offer .box.d{background:var(--ink);color:var(--cream)}
.offer .box.o{background:var(--orange);color:#fff}
.offer .box b{display:block;font-size:66px;font-weight:800;line-height:1;
  font-variant-numeric:tabular-nums}
.offer .box span{display:block;font-size:14px;margin-top:12px;font-weight:700}
.offer .swap{font-size:34px;text-align:center;color:var(--ink-2)}

/* ---------- media grids ---------- */
.grid6{display:grid;grid-template-columns:repeat(6,1fr);gap:11px;margin-top:auto}
.grid6 img{width:100%;height:190px;object-fit:cover;border-radius:8px;display:block}
.logos{display:grid;grid-template-columns:repeat(6,1fr);gap:11px;margin-top:14px}
.logos img{width:100%;height:104px;object-fit:contain;background:#fff;border-radius:8px;
  border:1px solid var(--line);padding:9px;display:block}
.chips{display:flex;gap:12px;margin-bottom:16px}
.chip{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.2);
  border-radius:8px;padding:12px 18px;text-align:center}
.chip b{display:block;font-size:26px;font-weight:800;font-variant-numeric:tabular-nums}
.chip span{font-size:11.5px;opacity:.8}

/* ---------- year ---------- */
.year{position:absolute;inset-inline-start:40px;top:46px;font-size:220px;font-weight:800;
  color:rgba(26,25,23,.13);line-height:1;letter-spacing:.02em;pointer-events:none}

/* ---------- close ---------- */
.close{justify-content:flex-end}
.close .art{position:absolute;inset:0}
.close .art img{width:100%;height:100%;object-fit:cover;opacity:.3;display:block}
.close .in{position:relative}
.close h2{font-size:58px;max-width:18ch}
.close .when{display:flex;gap:10px;flex-wrap:wrap;margin-top:22px}
.close .when span{background:var(--ink);color:#fff;border-radius:99px;padding:9px 18px;
  font-size:12.5px;font-weight:700}
.close .sig{display:flex;align-items:center;gap:14px;margin-top:24px;font-size:13px;
  color:#4A2E09;font-weight:700}
.close .sig img{height:30px}

.foot{position:absolute;inset-inline:60px;bottom:20px;display:flex;
  justify-content:space-between;font-size:11.5px;color:var(--ink-2);opacity:.8}
.pg.dark .foot{color:#9A9086}
.pg.orange .foot{color:#6B4409}
"""

# ------------------------------------------------------------------ الشرائح
FOOT = '<div class="foot"><span>الجمعة البرتقالية ٢٠٢٦ — محطات درب</span><span>%s</span></div>'


def foot(_=None):
    return FOOT % '@@n@@'


SLIDES = []

# ١ · الغلاف
SLIDES.append("""
<section class="pg orange cover">
  <div class="shot">
    <img src="%s" alt="محطة درب">
    <div class="stat"><b>١١٬٦٣٦</b><span>سيارة كل يوم تحت مظلاتنا</span></div>
  </div>
  <div class="side">
    <div class="top"><span>محطات درب × شركاء خدمات السيارات</span><img src="%s" alt="درب"></div>
    <div class="when">١٠ – ١٥ نوفمبر ٢٠٢٦ · أسبوعك في كل محطات درب</div>
    <h1>الجمعة<span class="b">البرتقالية</span></h1>
    <p class="tag">عرضك على كل مضخة، ودرب تسوّق له.</p>
  </div>
</section>""" % (STATION, LOGO))

# ٢ · الحقيقة البسيطة
SLIDES.append("""
<section class="pg dark">
  <p class="eyebrow">الحقيقة البسيطة</p>
  <h2>عميلك واقف تحت المظلة<br><span style="color:var(--orange)">قبل أن يسمع بك.</span></h2>
  <p class="lede">هو داخل الموقع فعلًا، وسيارته أمامه، ووقته فارغ. لا نحتاج أن نأتي به — نحتاج أن نحوّله.</p>
  <div class="pills">
    <div class="pill"><b>٥٠ ر.س</b> يدفعها للوقود</div>
    <div class="pill"><b>٥ دقائق</b> ينتظرها عند المضخة</div>
    <div class="pill"><b>سيارته</b> أمامه</div>
    <div class="pill" style="background:var(--orange);border-color:var(--orange);color:#fff"><b>= زيارة لعرضك</b></div>
  </div>
  %s
</section>""" % foot('١'))

# ٣ · الفكرة
SLIDES.append("""
<section class="pg">
  <div class="split">
    <div>
      <p class="eyebrow">الفكرة</p>
      <h2><span class="hl">شراكة تسويقية</span><br>لا عقد إيجار.</h2>
      <p class="lede" style="margin-top:18px">أنت تقدّم العرض، ودرب تصوّر وتجهّز وتنشر وتوزّع وتحسب —
        والنتيجة واحدة: سيارات تدخل مغسلتك.</p>
    </div>
    <div class="half orange">
      <p class="eyebrow">الأهداف العامة</p>
      <div class="cards">
        <div class="card w row"><span class="n">١</span><span>اسمك يوصل لسائقين أكثر</span></div>
        <div class="card d row"><span class="n">٢</span><span>ظهور أكثر على الجوال وداخل المحطة</span></div>
      </div>
    </div>
  </div>
</section>""")

# ٤ · ما نستهدفه لك
SLIDES.append("""
<section class="pg dark">
  <p class="eyebrow">المستهدفات</p>
  <h2>هدفان، وثلاثة أرقام نقيسها</h2>
  <div class="goals">
    <div class="goal"><span class="n">١</span><span>بناء صورة ذهنية إيجابية عن الشريك</span></div>
    <div class="goal"><span class="n">٢</span><span>زيادة التفاعل والحضور الرقمي والميداني</span></div>
  </div>
  <div class="stats">
    <div class="stat2 card o"><div class="v">+٥٠٠٠</div><div class="k">عميل واتساب</div>
      <div class="u">رسالة فيها عرضك ومدته، ورابط يفعّله على طول</div></div>
    <div class="stat2 card d" style="border:1px solid #3A352F"><div class="v">+١٠٠٠</div>
      <div class="k">عميل مباشر</div>
      <div class="u">لكل شريك، من الكوبونات والباركود</div></div>
    <div class="stat2 card o"><div class="v">+٥ مليون</div><div class="k">مشاهدة</div>
      <div class="u">كل مشاهدات الحملة على حسابات درب</div></div>
  </div>
  %s
</section>""" % foot('٢'))

# ٥ · الأرقام
REG = [('مكة · ٥ محطات', 5824), ('جدة', 2041), ('الطائف · محطتان', 1278),
       ('الرياض', 1169), ('جازان', 922), ('الخرج', 402)]
AR = '٠١٢٣٤٥٦٧٨٩'
ard = lambda t: ''.join(AR[int(c)] if c.isdigit() else c for c in str(t))
n0 = lambda v: ard('{:,}'.format(int(v)).replace(',', '٬'))
bars = ''.join(
    '<div class="barrow"><span class="t">%s</span>'
    '<span class="track"><span class="fill" style="width:%.1f%%"></span></span>'
    '<span class="v">%s</span></div>' % (t, v / 5824.0 * 100, n0(v)) for t, v in REG)
SLIDES.append("""
<section class="pg">
  <p class="eyebrow">أرقام محطاتنا</p>
  <h2 class="segs"><span>١١ محطة</span><span>٦ مناطق</span><span>+١١ ألف سيارة يوميًا</span></h2>
  <div class="bignum"><b>٣٤٩ ألف</b><span>تعبئة في الشهر</span></div>
  <div class="bars" style="margin-top:26px">%s</div>
  <div class="pills" style="margin-top:auto">
    <div class="pill">متوسط الفاتورة <b>٥٠٫٧ ر.س</b></div>
    <div class="pill"><b>٤٤٪</b> من الحركة بعد ٥ مساءً</div>
    <div class="pill">العرض يشتغل من الفتح للإغلاق</div>
  </div>
  %s
</section>""" % (bars, foot('٣')))

# ٦ · خطة النشر
SLIDES.append("""
<section class="pg orange">
  <p class="eyebrow">خطة النشر</p>
  <h2>أسبوع كامل لقطاعك وحده</h2>
  <p class="lede">ثلاثة أسابيع في نوفمبر، لكل قطاع أسبوع، ليأخذ شركاؤه تركيز المنصات والمحطات كاملًا.</p>
  <div class="steps" style="grid-template-columns:repeat(3,1fr)">
    <div class="step" style="background:var(--ink);color:var(--cream);border-color:var(--ink)">
      <span class="n">١</span><h3>غسيل وخدمات السيارات</h3>
      <p style="color:#CFC6BA">الأسبوع الأول · أسبوعك</p><span class="when">١٠ – ١٥ نوفمبر</span></div>
    <div class="step"><span class="n">٢</span><h3>المطاعم</h3>
      <p>الأسبوع الثاني</p><span class="when">١٦ – ٢١ نوفمبر</span></div>
    <div class="step"><span class="n">٣</span><h3>المقاهي</h3>
      <p>الأسبوع الثالث</p><span class="when">٢٢ – ٣٠ نوفمبر</span></div>
  </div>
  %s
</section>""" % foot('٤'))

# ٧ · مراحل الحملة
PHASES = [('فيديوهات قبل البداية تشوّق الناس', 'إعلان'),
          ('فيديو خاص بعرضك وسعره ومدته', 'إعلان'),
          ('مؤثّرون يوصلون عرضك للسائقين', 'إعلان'),
          ('رسالة واتساب لأكثر من ٥٬٠٠٠ عميل، فيها رابط التفعيل', 'إعلان'),
          ('١٠٠٠ كوبون باسمك يتسلّمه العميل عند المضخة', 'في المحطة'),
          ('لوحات ومطبوعات بعرضك داخل المحطة', 'في المحطة')]
rows = ''.join('<div class="rowi"><span>%s</span><span class="tagx%s">%s</span></div>'
               % (t, '' if k == 'إعلان' else ' f', k) for t, k in PHASES)
SLIDES.append("""
<section class="pg dark">
  <p class="eyebrow">مراحل الحملة</p>
  <h2>نشر يخلّي الناس تنتظر العرض، وتوزيع داخل المحطة يجيب العميل.</h2>
  <div class="rows" style="margin-top:26px;flex:1;justify-content:space-evenly">%s</div>
  %s
</section>""" % (rows, foot('٣')))

# ٨ · العرض المقترح
SLIDES.append("""
<section class="pg">
  <p class="eyebrow">العروض المقترحة</p>
  <h2>غسلة بعشرة، مقابل تعبئة بثلاثين</h2>
  <p class="lede">نفس عرض السنة الماضية، وقد نجح. وإن عندك فكرة ثانية نسمعها.</p>
  <div class="offer">
    <div class="box o"><b>١٠</b><span>ريال غسلة</span></div>
    <div class="swap">⇄</div>
    <div class="box d"><b>٣٠</b><span>ريال فاتورة بنزين أو أكثر</span></div>
  </div>
  <div class="pills" style="margin-top:20px">
    <div class="pill"><b>المواقع:</b> داخل محطات درب، وفي فروعك</div>
  </div>
  %s
</section>""" % foot('٥'))

# ٩ · العائد
CAP = [('١٪', '٦٩٨', '٦٬٩٨٢', '١٧٬٤٥٤', False),
       ('٥٪', '٣٬٤٩١', '٣٤٬٩٠٨', '٨٧٬٢٧٠', True),
       ('١٢٪', '٨٬٣٧٨', '٨٣٬٧٧٩', '٢٠٩٬٤٤٨', False)]
caps = ''.join(
    '<div class="stat2 card %s"><div class="v">%s</div>'
    '<div class="k">%s سيارة في الأسبوع</div>'
    '<div class="u">%s ر.س عند ١٠ ر.س<br>%s ر.س عند ٢٥ ر.س</div></div>'
    % ('o' if hot else 'w', p, cars, a, b) for p, cars, a, b, hot in CAP)
SLIDES.append("""
<section class="pg">
  <p class="eyebrow">العائد</p>
  <h2>لو دخل ١٪ فقط من السيارات مغسلتك</h2>
  <p class="lede">١١٬٦٣٦ سيارة تدخل محطات درب يوميًا. الحسبة على ستة أيام من أسبوعك:
    مرة بغسلة بعشرة ريالات، ومرة بمتوسط طلب ٢٥ ريالًا مع الخدمات الزيادة.</p>
  <div class="stats">%s</div>
  <p class="lede" style="margin-top:18px;font-weight:700;color:var(--orange)">
    خلّ عدد الكوبونات على قدر ما تقدر تغسله في اليوم — ردّ عميل جاك بالعرض أسوأ من عرض أصغر.</p>
  %s
</section>""" % (caps, foot('٦')))

# ١٠ · أربع خطوات
STEPS = [('كوبون وباركود عند المضخة',
          'عامل المحطة يعطيه للعميل بعد التعبئة ويدلّه على مكانك.', 'طول اليوم'),
         ('العميل يمسح ويفعّل',
          'يختارك ويكتب رقم جواله، فتوصله رسالة تدلّه عليك.', 'أقل من دقيقة'),
         ('موظفك يطبّق العرض',
          'العميل يوريه الرسالة، ويطبّق العرض على طول بلا أي إجراء.', 'عند الطلب'),
         ('نحسب ونرسل لك التقرير',
          'كل مسح ينحفظ، وتعرف بالضبط كم سيارة وصلتك.', 'تقرير كل أسبوع')]
steps = ''.join('<div class="step"><span class="n">%s</span><h3>%s</h3><p>%s</p>'
                '<span class="when">%s</span></div>'
                % (ard(i + 1), t, d, w) for i, (t, d, w) in enumerate(STEPS))
SLIDES.append("""
<section class="pg">
  <p class="eyebrow">الآلية</p>
  <h2>من المضخة إلى مغسلتك في أربع خطوات</h2>
  <div class="steps">%s</div>
  %s
</section>""" % (steps, foot('٧')))

# ١١ · النتائج
SLIDES.append("""
<section class="pg orange" style="justify-content:center">
  <div class="year">٢٠٢٥</div>
  <div style="position:relative">
    <h2 style="font-size:56px">مو وعود.<br>هذي نتائج ٢٠٢٥.</h2>
    <p class="lede" style="margin-top:18px;font-size:17px">شركاء ومؤثّرون حقيقيون،
      وعدد المشاهدات ظاهر على كل مقطع.</p>
  </div>
  %s
</section>""" % foot('٨'))

# ١٢ · المؤثّرون
SLIDES.append("""
<section class="pg dark">
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

# ١٣ · الشركاء
SLIDES.append("""
<section class="pg">
  <p class="eyebrow">شركاء ٢٠٢٥</p>
  <h2>شركاء كانوا معنا، وراجعين هذه السنة</h2>
  <p class="lede" style="margin-top:4px;font-weight:800;color:var(--orange)">شركاء الحملة</p>
  <div class="logos" style="margin-top:10px">%s</div>
  <p class="lede" style="margin-top:auto;font-weight:800;color:var(--orange)">محتوى المؤثّرين</p>
  <div class="grid6" style="margin-top:10px">%s</div>
</section>""" % (''.join('<img src="%s" alt="">' % c for c in LOGOS),
                 ''.join('<img src="%s" alt="" style="height:210px">' % c for c in INFL)))

# ١٤ · المسؤوليات
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
      <div class="rows">%s</div>
    </div>
    <div class="half dark">
      <h2 style="font-size:34px">مسؤوليات الشريك</h2>
      <div class="rows">%s</div>
    </div>
  </div>
</section>""" % (
    ''.join('<div class="rowi" style="border-color:rgba(26,25,23,.18)">'
            '<span class="tagx" style="background:var(--ink);margin:0">✓</span>'
            '<span>%s</span></div>' % t for t in DARB),
    ''.join('<div class="rowi"><span class="tagx" style="margin:0">%s</span>'
            '<span>%s</span></div>' % (ard(i + 1), t) for i, t in enumerate(YOU))))

# ١٥ · الختام
SLIDES.append("""
<section class="pg orange close">
  <div class="art"><img src="%s" alt=""></div>
  <div class="in">
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
</section>""" % (CLOSE_ART, LOGO))

# حذف بطلبها: الغلاف، والحقيقة البسيطة، وخطة النشر
DROP = [('الغلاف', 'class="pg orange cover"'),
        ('الحقيقة البسيطة', '<p class="eyebrow">الحقيقة البسيطة</p>'),
        ('خطة النشر', '<p class="eyebrow">خطة النشر</p>'),
        ('الفكرة', '<p class="eyebrow">الفكرة</p>')]
for label, mark in DROP:
    hit = [i for i, sl in enumerate(SLIDES) if mark in sl]
    assert len(hit) == 1, 'drop %s matched %d slides' % (label, len(hit))
    SLIDES.pop(hit[0])
    print('  dropped: %s' % label)

# العروض المقترحة تختم العرض بطلبها
MOVE = '<p class="eyebrow">العروض المقترحة</p>'
hit = [i for i, sl in enumerate(SLIDES) if MOVE in sl]
assert len(hit) == 1, 'offer slide matched %d slides' % len(hit)
SLIDES.append(SLIDES.pop(hit[0]))
print('  moved to last: العروض المقترحة')

DECK = ''.join(SLIDES)
AR10 = '٠١٢٣٤٥٦٧٨٩'
_c = [0]
def _num(m):
    _c[0] += 1
    return ''.join(AR10[int(d)] for d in str(_c[0]))
DECK = re.sub(r'@@n@@', _num, DECK)
assert '@@n@@' not in DECK

# ------------------------------------------------------- المحرّر من ملفاتها
src = open(CHROME_SRC, encoding='utf-8').read()
i = src.index('function darbEditor(opts){')
j = src.index('\n(function(){', i)
EDITOR = src[i:j]
assert 'function darbEditor' in EDITOR and len(EDITOR) > 6000, 'editor extract failed'
SAY_OLD = """  function say(m,ms){ if(!toast) return; toast.textContent=m; toast.classList.add('show');
    clearTimeout(tT); tT=setTimeout(function(){ toast.classList.remove('show'); }, ms||4500); }"""
SAY_NEW = """  function say(m,ms,actLabel,actFn){
    if(!toast) return;
    var msg=document.getElementById('toastmsg'), act=document.getElementById('toastact');
    if(msg) msg.textContent=m; else toast.textContent=m;
    if(act){
      if(actLabel){ act.hidden=false; act.textContent=actLabel;
        act.onclick=function(){ act.hidden=true; toast.classList.remove('show');
                                if(actFn) actFn(); }; }
      else { act.hidden=true; act.onclick=null; }
    }
    toast.classList.add('show');
    clearTimeout(tT); tT=setTimeout(function(){ toast.classList.remove('show'); }, ms||4500); }"""
assert SAY_OLD in EDITOR, 'say() not found in the borrowed editor'
EDITOR = EDITOR.replace(SAY_OLD, SAY_NEW, 1)
chrome_css = src.split('<style id="darbcss">', 1)[1].split('</style>', 1)[0]
k = chrome_css.index('/* ---------- picker ----------')
CHROME = chrome_css[k:]

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
<div class="toast" id="toast"><span id="toastmsg"></span><button type="button" id="toastact" hidden></button></div>
<input type="file" id="pickimg" accept="image/*" hidden>"""

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
  /* ملف الشريك: شرائح فقط، بلا شريط ولا أزرار */
  function fileFor(html){
    return '<!doctype html>\\n<html lang="ar" dir="rtl">\\n<head>\\n<meta charset="utf-8">\\n'+
      '<meta name="viewport" content="width=device-width, initial-scale=1">\\n'+
      '<title>الجمعة البرتقالية ٢٠٢٦ — محطات درب</title>\\n'+CSSTEXT+'\\n</head>\\n<body>\\n'+
      '<div class="wrap"><div id="deck">'+clean(html)+'</div></div>\\n</body>\\n</html>\\n';
  }
  var ed=darbEditor({
    key:'darb-orange-friday-v1',
    load:function(){ return DECK; },
    download:function(api){
      api.send('darb-orange-friday', fileFor(api.box.innerHTML),
               'نُزّل ملف الجمعة البرتقالية جاهزًا للإرسال للشريك.');
    }
  });
  document.title='الجمعة البرتقالية ٢٠٢٦ — محطات درب';
  /* نسخة محفوظة ما زالت تحمل الشرائح المحذوفة: نعرض التحديث ولا نفرضه */
  (function(){
    var old=null; try{ old=localStorage.getItem('darb-orange-friday-v1'); }catch(e){}
    if(!old) return;
    if(old.indexOf('pg orange cover')<0 && old.indexOf('خطة النشر')<0) return;
    ed.say('نسختك المحفوظة ما زالت تحمل الشرائح الثلاث المحذوفة. '+
           '«حدّث» يجيب النسخة الجديدة، و«تراجع» بعده يرجّع نسختك.',
      20000, 'حدّث', function(){
        ed.snap();
        ed.box.innerHTML=DECK;
        ed.mark(); ed.snap(); ed.keep(); ed.place(null);
        window.scrollTo(0,0);
        ed.say('حُدّثت الشرائح. «تراجع» يرجّع نسختك السابقة.',9000);
      });
  })();
})();
</script>"""

import json
APP = APP % (json.dumps(DECK, ensure_ascii=False), EDITOR)

TOASTCSS = """
.toast{display:flex;align-items:center;gap:12px;line-height:1.75}
.toast.show{pointer-events:auto}
#toastmsg{max-width:62ch}
#toastact{background:var(--orange);color:#fff;border:0;border-radius:6px;padding:7px 15px;
  font:inherit;font-size:12.5px;font-weight:800;cursor:pointer;white-space:nowrap}
#toastact:hover{background:var(--orange-dk)}
"""

HTML = ('<!doctype html>\n<html lang="ar" dir="rtl">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>الجمعة البرتقالية ٢٠٢٦ — محطات درب</title>\n<style id="darbcss">\n'
        + CSS + '\n' + CHROME + '\n' + TOASTCSS + '</style>\n</head>\n<body>\n' + BODY + '\n' + APP
        + '\n</body>\n</html>\n')
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
assert "documentElement.lang" in art, 'lang injection failed'
open(ART, 'w', encoding='utf-8').write(art)

print('slides: %d' % DECK.count('<section class="pg'))
print('page: %d KB   artifact: %d KB' % (len(HTML) // 1024, len(art) // 1024))
