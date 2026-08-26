# -*- coding: utf-8 -*-
"""The same partnership deck, one file per region instead of per station.

The cover and the return table read the region as a whole: its stations' cars
added together, its fuel bill and its evening share weighted by traffic, and
the busiest hour across it. The last slide is an offers table left blank, one
row per station in the region, to be filled by hand.

The page carries the tools already agreed — edit, add a slide, delete a block,
swap an image, undo and redo — and the file each region hands out is clean.
"""
import json
from collections import defaultdict

ST = json.load(open('stations11.json', encoding='utf-8'))
IMG = json.load(open('wimages.json', encoding='utf-8'))
CSS = open('user_css.txt', encoding='utf-8').read()

CSS += """
.blockbar .kind{color:#E4D8C8;font-size:12px;padding:0 6px 0 2px;white-space:nowrap}
.blockbar.show{display:flex;align-items:center}
.blockbar button.img{background:#2F5D46}
.blockbar button.img:hover{background:#3E7D5D}
body.editing img[data-block]{cursor:pointer}
body.editing img[data-block]:hover{outline:2px dashed var(--orange-hi);outline-offset:2px}
.pg.close{align-items:center;justify-content:center;text-align:center}
.pg.close h2{font-size:44px}
/* the backdrop <img> is inline; its baseline gap made the cover 4px too tall */
.pg.cover .art img{display:block}
td.fill{background:var(--ground);color:var(--ink-3)}
.stlist{display:flex;flex-wrap:wrap;gap:7px;margin-top:14px}
.stlist span{background:var(--surface);border:1px solid var(--line);border-radius:99px;
  padding:5px 13px;font-size:12.5px}
.stlist span b{color:var(--orange);font-variant-numeric:tabular-nums}

/* ---- الغلاف: شريط يعرض تحليلات منطقة بعد أخرى ---- */
.pg.cover .rslider{margin-top:auto}
.pg.cover .rframe{display:none}
.pg.cover .rframe.is-on{display:block;animation:rfade .45s ease}
@keyframes rfade{from{opacity:0;transform:translateY(7px)}to{opacity:1;transform:none}}
.pg.cover .rhead{font-size:12.5px;font-weight:800;color:#E4D3BC;margin-bottom:9px}
.pg.cover .rhead span{color:#B49F86;font-weight:400}
.pg.cover .rframe .strip{margin-top:0;grid-template-columns:repeat(3,1fr)}
.pg.cover .rframe .fact{padding:14px 16px}
.pg.cover .rframe .fact .v{font-size:32px}
.pg.cover .rbar{display:flex;align-items:center;gap:10px;margin-top:13px}
.pg.cover .rdots{display:flex;gap:6px;flex:1}
.pg.cover .rdot{width:8px;height:8px;padding:0;border:0;border-radius:50%;cursor:pointer;
  background:rgba(255,255,255,.28);transition:width .25s,background .25s}
.pg.cover .rdot.on{background:var(--amber);width:22px;border-radius:99px}
.pg.cover .rnav{width:26px;height:26px;padding:0;border-radius:50%;cursor:pointer;
  background:rgba(255,255,255,.10);border:1px solid rgba(255,255,255,.18);color:#fff;
  font-size:15px;line-height:1;display:flex;align-items:center;justify-content:center}
.pg.cover .rnav:hover{background:rgba(255,255,255,.22)}

/* ---- جدول الشركاء: أزرار الصفوف تظهر عند التحرير فقط ولا تنزل مع الملف ---- */
.ptab .rowx{width:34px;padding:4px;text-align:center;background:transparent;border-bottom:0}
.ptab .rowx button{display:none;width:24px;height:24px;padding:0;border-radius:6px;
  background:transparent;border:1px solid var(--line);color:var(--ink-3);
  font:inherit;font-size:12px;line-height:1;cursor:pointer}
body.editing .ptab .rowx button{display:inline-flex;align-items:center;justify-content:center}
body.editing .ptab .rowx button:hover{border-color:var(--orange);color:var(--orange)}
.ptools{display:none;gap:10px;align-items:center;margin-top:12px}
body.editing .ptools{display:flex}
.ptools button{background:var(--orange);color:#fff;border:0;border-radius:7px;
  padding:8px 15px;font:inherit;font-size:12.5px;font-weight:800;cursor:pointer}
.ptools button:hover{background:var(--orange-hi)}
.ptools .n{font-size:12px;color:var(--ink-3)}

/* ---- رسالة تحمل زرًا، لعرض التحديث على نسخة محفوظة قديمة ---- */
.toast{display:flex;align-items:center;gap:12px;line-height:1.75}
.toast.show{pointer-events:auto}
#toastmsg{max-width:66ch}
#toastact{background:var(--orange);color:#fff;border:0;border-radius:6px;padding:7px 15px;
  font:inherit;font-size:12.5px;font-weight:800;cursor:pointer;white-space:nowrap}
#toastact:hover{background:var(--orange-hi)}
"""

# ---------------------------------------------------------------- المناطق
GROUP = defaultdict(list)
for code, s in ST.items():
    GROUP[s['region']].append(s)
ORDER = sorted(GROUP, key=lambda r: -sum(x['dvis'] for x in GROUP[r]))
for r in ORDER:
    GROUP[r].sort(key=lambda x: -x['dvis'])

FOOT = ('<div class="foot"><span>حملة غسيل السيارات — درب</span>'
        '<span><b>{region}</b> · {nst}</span></div>')

SLIDES = [
    # ---- الغلاف
    """
<section class="pg cover">
  <div class="art"><img src="{hero}" alt=""></div><div class="veil"></div>
  <div class="in">
    <div class="brand"><img src="{logo}" alt="درب"><span>محطات درب — منطقة {region} · {nst}</span></div>
    <h1>حملة غسيل السيارات.<br><span class="hl">درب تنفّذ الحملة، وأنت تقدّم العرض.</span></h1>
    <div class="rslider" data-rslider>
      <div class="rframes">{rframes}</div>
      <div class="rbar">
        <button type="button" class="rnav" contenteditable="false" data-nav="1" data-r="prev" title="المنطقة السابقة">›</button>
        <div class="rdots">{rdots}</div>
        <button type="button" class="rnav" contenteditable="false" data-nav="1" data-r="next" title="المنطقة التالية">‹</button>
      </div>
    </div>
  </div>
</section>""",

    # ---- ١ · تحليلات المنطقة
    """
<section class="pg">
  <p class="eyebrow">١ · تحليلات المنطقة</p>
  <h2>حركة منطقة {region} على مستوى المنطقة</h2>
  <p class="lede">أرقام محطات درب في {region} مجتمعة على مدار اليوم الكامل. الفاتورة والتعبئة وحصة المساء متوسطات مرجّحة بحركة كل محطة، والذروة أعلى ساعة في المنطقة.</p>
  <table>
    <thead><tr><th>المحطة</th><th>الكود</th><th>سيارات/يوم</th><th>سيارات/شهر</th><th>متوسط الفاتورة</th><th>متوسط التعبئة</th><th>نصيب المساء</th><th>ذروة الحركة</th></tr></thead>
    <tbody>{strows}</tbody>
  </table>
  {F}
</section>""",

    # ---- ٢ · لماذا الشراكة في الحملة
    """
<section class="pg">
  <p class="eyebrow">٢ · لماذا الشراكة في الحملة</p>
  <h2>السيارة الواقفة تحت المظلة هي عميلك</h2>
  <div class="split">
    <img src="{station}" alt="محطة درب">
    <div class="gains" style="margin-top:0">
      <div class="gain"><span class="mark"></span><div><b>عملاء درب تحت المظلة يصيرون عملاءك</b><span>تقف في محطات {region} نحو {cars} سيارة كل يوم للتزوّد بالوقود، أي {month} سيارة في الشهر. السائق داخل الموقع فعلًا وسيارته أمامه.</span></div></div>
      <div class="gain"><span class="mark"></span><div><b>العميل موجود طوال اليوم</b><span>حصة المساء {eve} من حركة اليوم والصباح {morn}، فالعرض يعمل من فتح المحطة إلى إغلاقها لا في ساعة واحدة.</span></div></div>
      <div class="gain"><span class="mark"></span><div><b>تسويق ميداني فعّال</b><span>عمال المحطة يسلّمون كرت العرض للسائق عند المضخة ويشيرون إلى المغسلة.</span></div></div>
      <div class="gain"><span class="mark"></span><div><b>فريق تسويق جاهز</b><span>فريق محتوى ومؤثّرون وحملات إعلانية ينفّذون الحملة بدلًا عنك.</span></div></div>
    </div>
  </div>
  {F}
</section>""",

    # ---- ٣ · حسبة العائد
    """
<section class="pg">
  <p class="eyebrow">٣ · حسبة العائد</p>
  <h2>ماذا يعني كل ١٪ من سيارات المنطقة</h2>
  <p class="lede">{cars} سيارة تدخل محطات {region} يوميًا على مدار اليوم. معدل الالتقاط هو نسبة من يغسل سيارته منهم، والجدول يعرض الناتج عند سعر غسلة ١٠ ريالات وعند ١٥ ريالًا.</p>
  <table>
    <thead><tr><th>معدل الالتقاط</th><th>سيارات/يوم</th><th>سيارات/شهر</th><th>المبيعات الشهرية عند ١٠ ر.س</th><th>المبيعات الشهرية عند ١٥ ر.س</th></tr></thead>
    <tbody>{caprows}</tbody>
  </table>
  {F}
</section>""",

    # ---- ٤ · ماذا يكسب الشريك
    """
<section class="pg">
  <p class="eyebrow">٤ · ماذا يكسب الشريك</p>
  <h2>خمسة مكاسب مباشرة</h2>
  <div class="gains">
    <div class="gain"><span class="mark"></span><div><b>عملاء جدد</b><span>نحوّل الزائر العابر تحت المظلة إلى عميل يدخل مغسلتك.</span></div></div>
    <div class="gain"><span class="mark"></span><div><b>وصول واسع</b><span>علامتك أمام أكثر من ١٠٠ ألف مشاهدة خلال أسبوع واحد.</span></div></div>
    <div class="gain"><span class="mark"></span><div><b>محتوى احترافي جاهز</b><span>تصوير وتصميم ومونتاج وإدارة مؤثّرين، ينفّذه فريق درب بالكامل.</span></div></div>
    <div class="gain"><span class="mark"></span><div><b>حضور داخل المحطة</b><span>كروت تحمل اسم المغسلة، ولوحات على المضخات طوال مدة الحملة.</span></div></div>
    <div class="gain"><span class="mark"></span><div><b>عائد قابل للقياس</b><span>كل عميل يصلك عبر رمز QR قابل للتتبع، مع تقرير أداء أسبوعي.</span></div></div>
  </div>
  {F}
</section>""",

    # ---- ٥ · ما تنفّذه درب
    """
<section class="pg">
  <p class="eyebrow">٥ · ما تنفّذه درب</p>
  <h2>ست خدمات ينفّذها فريق درب بالكامل</h2>
  <div class="tools">
    <div class="tool"><span class="t">١</span><div><h3>صناعة محتوى الحملة</h3><p>كتابة فكرة الحملة ورسائلها وإعداد محتوى العروض للنشر.</p><span class="reach">درب</span></div></div>
    <div class="tool"><span class="t">٢</span><div><h3>التصوير والتصميم والمونتاج</h3><p>تصوير المغسلة والخدمة، وتصميم الكروت، ومونتاج المقاطع.</p><span class="reach">درب</span></div></div>
    <div class="tool"><span class="t">٣</span><div><h3>بناء الحملة الإعلانية</h3><p>تصميم خطة النشر وتوقيتها وتوزيع المحتوى على المنصات.</p><span class="reach">درب</span></div></div>
    <div class="tool"><span class="t">٤</span><div><h3>النشر على منصات التواصل</h3><p>نشر المحتوى على قنوات درب ومتابعة التفاعل والنتائج.</p><span class="reach">درب</span></div></div>
    <div class="tool"><span class="t">٥</span><div><h3>إدارة المؤثّرين</h3><p>اختيار المؤثّرين والتنسيق معهم وإدارة المحتوى.</p><span class="reach">درب تنفّذ · الشريك يتحمّل تكلفة التعاقد</span></div></div>
    <div class="tool"><span class="t">٦</span><div><h3>الترويج الميداني داخل المحطة</h3><p>توزيع كروت عرض باسم الشريك خلال فترة الحملة.</p><span class="reach">درب</span></div></div>
  </div>
  {F}
</section>""",

    # ---- ٦ · فيديوهات الحملة
    """
<section class="pg">
  <p class="eyebrow">٦ · مكوّنات الحملة — تسويق رقمي</p>
  <h2>فيديوهات الحملة</h2>
  <p class="lede">فيديو تشويقي قصير يُنشر قبل الانطلاق ليصنع ترقّبًا، ثم فيديو يعرض عرض مغسلتك وسعره ومدته على منصات درب. نماذج حقيقية من حملات نفّذتها درب، وعدد المشاهدات ظاهر على كل مقطع.</p>
  <div class="clips">{clips}</div>
  {F}
</section>""",

    # ---- ٦ · الترويج عبر المؤثّرين
    """
<section class="pg">
  <p class="eyebrow">٦ · مكوّنات الحملة — تسويق رقمي</p>
  <h2>الترويج عبر المؤثّرين</h2>
  <p class="lede">اختيار مؤثّرين مناسبين لجمهور الطريق والتنسيق معهم وإدارة المحتوى. هذه نماذج من فيديوهات مؤثّرين في حملات درب السابقة.</p>
  <div class="clips">{infl}</div>
  {F}
</section>""",

    # ---- ٦ · حملة واتساب وكروت العرض
    """
<section class="pg">
  <p class="eyebrow">٦ · مكوّنات الحملة — رقمي وميداني</p>
  <h2>حملة واتساب وكروت العرض</h2>
  <div class="split">
    <img class="cardshot" src="{card}" alt="كرت العرض">
    <div class="gains" style="margin-top:0">
      <div class="gain"><span class="mark"></span><div><b>تصل إلى الجوال مباشرة</b><span>عرض محدّد المدة مع رابط تفعيل، لا يعتمد على أن يرى العميل إعلانًا.</span></div></div>
      <div class="gain"><span class="mark"></span><div><b>محدّدة المدة</b><span>تدفع العميل للاستفادة قبل انتهاء العرض.</span></div></div>
      <div class="gain"><span class="mark"></span><div><b>قابلة للقياس</b><span>يُحصى عدد من فتح الرسالة وعدد من فعّل العرض.</span></div></div>
      <div class="gain"><span class="mark"></span><div><b>توزيع ١٠٠٠ كرت خلال فترة الحملة</b><span>عمال المحطة يسلّمون كرت العرض للسائق .</span></div></div>
    </div>
  </div>
  {F}
</section>""",

    # ---- ٧ · آلية التنفيذ
    """
<section class="pg">
  <p class="eyebrow">٧ · آلية التنفيذ</p>
  <h2>أربع خطوات من المضخة إلى مغسلتك</h2>
  <p class="lede">كل خطوة واضحة ومسؤول عنها طرف واحد، وكل عملية مسجّلة.</p>
  <div class="tools">
    <div class="tool"><span class="t">١</span><div><h3>اظهار الكيو آر للعميل</h3><p>مع توزيع كرت العرض</p><span class="reach">طوال اليوم</span></div></div>
    <div class="tool"><span class="t">٢</span><div><h3>العميل يمسح الرمز ويفعّل العرض</h3><p>تفتح صفحة العروض، يختار المغسلة ويُدخل جواله فتصله رسالة توجّهه إليك.</p><span class="reach">أقل من دقيقة</span></div></div>
    <div class="tool"><span class="t">٣</span><div><h3>موظف المغسلة يطبّق العرض</h3><p>يعرض العميل الرسالة عند الطلب فيُطبَّق العرض مباشرة دون إجراء إضافي.</p><span class="reach">عند الطلب</span></div></div>
    <div class="tool"><span class="t">٤</span><div><h3>لوحة القياس تسجّل العملية</h3><p>كل مسح يُسجّل تلقائيًا، ويصلك تقرير أسبوعي بعدد السيارات الواصلة من الحملة.</p><span class="reach">تقرير كل أسبوع</span></div></div>
  </div>
  {F}
</section>""",

    # ---- ٨ · توزيع المسؤوليات
    """
<section class="pg">
  <p class="eyebrow">٨ · توزيع المسؤوليات</p>
  <h2>المسؤوليات</h2>
  <table>
    <thead><tr><th>البند</th><th>درب</th><th>الشريك</th></tr></thead>
    <tbody>
      <tr><td>التصوير والتصميم والمونتاج</td><td class="yes">✓</td><td class="no">—</td></tr>
      <tr><td>إطلاق الحملات والنشر على مواقع التواصل</td><td class="yes">✓</td><td class="no">—</td></tr>
      <tr><td>آلية التنفيذ ورمز QR وتدريب عمال المحطة</td><td class="yes">✓</td><td class="no">—</td></tr>
      <tr><td>التنسيق مع المؤثّرين</td><td class="yes">✓</td><td class="no">—</td></tr>
      <tr><td>تكلفة التعاقد مع المؤثّرين</td><td class="no">—</td><td class="yes">✓</td></tr>
      <tr><td>قيمة العرض أو الخصم</td><td class="no">—</td><td class="yes">✓</td></tr>
      <tr><td>الالتزام بالعرض طوال ساعات العمل وتدريب الطاقم</td><td class="no">—</td><td class="yes">✓</td></tr>
    </tbody>
  </table>
  {F}
</section>""",

    # ---- الختام
    """
<section class="pg close">
  <h2>كن شريكًا لنا وشاركنا النجاح</h2>
  {F}
</section>""",

    # ---- ٩ · العروض — فارغة تُملأ باليد
    """
<section class="pg">
  <p class="eyebrow">٩ · العروض</p>
  <h2>عروض منطقة {region}</h2>
  <p class="lede">صف لكل محطة في المنطقة. اضغط «تحرير» ثم اكتب في الخانات الفارغة.</p>
  <table>
    <thead><tr><th>المحطة</th><th>الشريك</th><th>فكرة العرض</th><th>السعر الاعتيادي</th><th>سعر الحملة</th></tr></thead>
    <tbody>{offerrows}</tbody>
  </table>
  {F}
</section>""",

    # ---- ١٠ · الشركاء — صفوف تُضاف وتُحذف باليد
    """
<section class="pg">
  <p class="eyebrow">١٠ · الشركاء</p>
  <h2>شركاء منطقة {region} وعروضهم</h2>
  <p class="lede">اضغط «تحرير» ثم اكتب في أي خانة، و«+ شريك» يضيف صفًا و«✕» يحذفه. الملف الذي تنزّلينه للشريك يخرج بالجدول فقط بلا أزرار.</p>
  <table class="ptab" data-ptab>
    <thead><tr><th>الشريك</th><th>العرض</th><th>المدة</th><th>المنطقة</th><th class="rowx"></th></tr></thead>
    <tbody>{partnerrows}</tbody>
  </table>
  <div class="ptools">
    <button type="button" contenteditable="false" data-tool="addrow" data-region="{region}">+ شريك</button>
    <span class="n">كل صف شريك واحد: اسمه، والعرض الذي يقدّمه، ومدة العرض، والمنطقة.</span>
  </div>
  {F}
</section>""",
]

AR = '٠١٢٣٤٥٦٧٨٩'


def ard(t):
    return ''.join(AR[int(c)] if c.isdigit() else c for c in str(t))


def n0(v):
    return ard('{:,}'.format(int(round(v))).replace(',', '٬'))


def n1(v):
    return ard(('%.1f' % v).replace('.', '٫'))


def hour(h):
    h = int(h or 0)
    k = (h % 12) or 12
    return ard(k) + (' صباحًا' if h < 12 else ' مساءً')


def nstations(n):
    return {1: 'محطة واحدة', 2: 'محطتان'}.get(n, '%s محطات' % ard(n) if n <= 10
                                              else '%s محطة' % ard(n))


# الأرقام الثلاثة التي تظهر في شريط الغلاف، محسوبة مرّة لكل منطقة.
# العمليات شهرية لتبقى المناطق قابلة للمقارنة داخل الشريط الواحد؛ سجلّ جدة
# يغطي مدة أقصر من البقية، فأي رقم تراكمي كان سيقارن مددًا غير متساوية.
def rstat(region):
    ss = GROUP[region]
    cars = sum(x['dvis'] for x in ss)
    return dict(nst=nstations(len(ss)), cars=n0(cars), ops=n0(cars * 30),
                pay=n1(sum(x['inv'] * x['dvis'] for x in ss) / cars) + ' ر.س')


def rframes(current):
    out = ''
    for r in ORDER:
        v = rstat(r)
        out += ('<div class="rframe%s">'
                '<div class="rhead">منطقة %s <span>· %s</span></div>'
                '<div class="strip">'
                '<div class="fact"><div class="k">عدد العمليات</div><div class="v">%s</div>'
                '<div class="u">عملية تعبئة في الشهر</div></div>'
                '<div class="fact"><div class="k">متوسط الدفع</div><div class="v">%s</div>'
                '<div class="u">لكل عملية</div></div>'
                '<div class="fact"><div class="k">السيارات يوميًا</div><div class="v">%s</div>'
                '<div class="u">على مدار اليوم</div></div>'
                '</div></div>') % (' is-on' if r == current else '',
                                   r, v['nst'], v['ops'], v['pay'], v['cars'])
    return out


def rdots(current):
    return ''.join('<button type="button" class="rdot%s" contenteditable="false" '
                   'data-nav="1" data-r="%d" title="منطقة %s"></button>'
                   % (' on' if r == current else '', i, r)
                   for i, r in enumerate(ORDER))


def vals(region):
    ss = GROUP[region]
    cars = sum(x['dvis'] for x in ss)
    wavg = lambda k: sum(x[k] * x['dvis'] for x in ss) / cars
    pk = defaultdict(float)
    for x in ss:
        pk[x['peak']] += x['dvis']
    peak = max(pk.items(), key=lambda kv: kv[1])[0]

    rows = ''
    for r in [1, 3, 5, 8, 12]:
        d = cars * r / 100.0
        m = d * 30
        rows += ('<tr><td class="strong">%s٪</td><td class="num">%s</td><td class="num">%s</td>'
                 '<td class="num">%s ر.س</td><td class="num">%s ر.س</td></tr>'
                 % (ard(r), n0(d), n0(m), n0(m * 10), n0(m * 15)))

    strows = ''
    for x in ss:
        strows += ('<tr><td>%s</td><td class="strong">%s</td><td class="num">%s</td>'
                   '<td class="num">%s</td><td class="num">%s ر.س</td><td class="num">%s ل</td>'
                   '<td class="num">%s٪</td><td class="num">%s</td></tr>'
                   % (x['name'], x['code'], n0(x['dvis']), n0(x['dvis'] * 30),
                      n1(x['inv']), n1(x['lit']), ard(round(x['evening'] * 100)),
                      hour(x['peak'])))
    strows += ('<tr class="hot"><td class="strong">إجمالي المنطقة</td><td class="strong">%s</td>'
               '<td class="num strong">%s</td><td class="num strong">%s</td>'
               '<td class="num strong">%s ر.س</td><td class="num strong">%s ل</td>'
               '<td class="num strong">%s٪</td><td class="num strong">%s</td></tr>'
               % (nstations(len(ss)), n0(cars), n0(cars * 30), n1(wavg('inv')),
                  n1(wavg('lit')), ard(round(wavg('evening') * 100)), hour(peak)))

    offers = ''.join(
        '<tr><td class="strong">%s — %s</td><td class="fill">…</td><td class="fill">…</td>'
        '<td class="fill">…</td><td class="fill">…</td></tr>' % (x['name'], x['code'])
        for x in ss)

    prows = ''.join(
        '<tr><td class="fill">…</td><td class="fill">…</td><td class="fill">…</td>'
        '<td>%s</td><td class="rowx"><button type="button" contenteditable="false" '
        'data-tool="delrow" title="حذف الصف">✕</button></td></tr>' % region
        for _ in range(4))

    return dict(region=region, nst=nstations(len(ss)),
                cars=n0(cars), month=n0(cars * 30), inv=n1(wavg('inv')) + ' ر.س',
                peak=hour(peak), partnerrows=prows,
                rframes=rframes(region), rdots=rdots(region),
                eve=ard(round(wavg('evening') * 100)) + '٪',
                morn=ard(round(wavg('morning') * 100)) + '٪',
                caprows=rows, strows=strows, offerrows=offers,
                clips=''.join('<img src="@@clip%d@@" alt="">' % i for i in range(1, 7)),
                infl=''.join('<img src="@@infl%d@@" alt="">' % i for i in range(1, 7)),
                hero='@@hero@@', logo='@@logo@@', station='@@station@@', card='@@card@@')


def deck(region):
    v = vals(region)
    foot = FOOT.format(region=region, nst=v['nst'])
    return ''.join(s.replace('{F}', foot).format(**v) for s in SLIDES)


DECKS = {r: deck(r) for r in ORDER}
NAMES = {r: r for r in ORDER}

OPTS = ''.join('<option value="%s"%s>منطقة %s — %s</option>'
               % (r, ' selected' if i == 0 else '', r, nstations(len(GROUP[r])))
               for i, r in enumerate(ORDER))


# the download names must be ASCII — the host sanitises the filename before it
# checks the extension, so an Arabic stem loses its .html and is refused
SLUG = {'مكة': 'makkah', 'جدة': 'jeddah', 'الطائف': 'taif', 'الرياض': 'riyadh',
        'جازان': 'jazan', 'الخرج': 'kharj'}
for r in ORDER:
    SLUG.setdefault(r, 'region%d' % (ORDER.index(r) + 1))

# ------------------------------------------------------- الشريط والمحرّر
# نفس أدوات ملف المحطات، مع ثلاث إضافات لهذا الملف: شريط تحليلات المناطق في
# الغلاف، وأزرار الصفوف في جدول الشركاء، وتنظيفهما من الملف الذي ينزل للشريك.

SLIDER = r"""
/* ---------------------------------------------------------------------
   شريط تحليلات المناطق في الغلاف: يعرض منطقة بعد أخرى.
   مستقل تمامًا عن أدوات التحرير، فهو ينزل مع ملف الشريك ويعمل فيه.
   ------------------------------------------------------------------ */
function darbSlider(root){
  var boxes=(root||document).querySelectorAll('[data-rslider]');
  for(var i=0;i<boxes.length;i++) wire(boxes[i]);

  function wire(s){
    /* خاصية لا تُحفظ مع النص، فالنسخة المعادة من الذاكرة تُربط من جديد */
    if(s.__darbwired) return;
    s.__darbwired=true;
    var frames=s.querySelectorAll('.rframe'), dots=s.querySelectorAll('.rdot');
    if(frames.length<2) return;
    var at=0, timer=null, i;
    for(i=0;i<frames.length;i++) if(frames[i].classList.contains('is-on')) at=i;

    function show(n){
      at=(n%frames.length+frames.length)%frames.length;
      for(var j=0;j<frames.length;j++){
        frames[j].classList.toggle('is-on', j===at);
        if(dots[j]) dots[j].classList.toggle('on', j===at);
      }
    }
    function tick(){
      if(document.body.classList.contains('editing')) return;  /* يقف أثناء التحرير */
      show(at+1);
    }
    function start(){ stop(); timer=setInterval(tick, 5200); }
    function stop(){ if(timer){ clearInterval(timer); timer=null; } }

    s.addEventListener('click', function(e){
      var b=e.target.closest('button'); if(!b||!s.contains(b)) return;
      e.preventDefault();
      var r=b.getAttribute('data-r');
      if(r==='prev') show(at-1);
      else if(r==='next') show(at+1);
      else if(r!==null) show(Number(r));
      start();
    });
    s.addEventListener('mouseenter', stop);
    s.addEventListener('mouseleave', start);
    show(at); start();
  }
}
"""

ROWTOOL = r"""
  /* جدول الشركاء: صف يُضاف وصف يُحذف. الأزرار نفسها لا تنزل مع ملف الشريك */
  function rowTool(b){
    var a=b.getAttribute('data-tool');
    if(a==='addrow'){
      var pg=b.closest('.pg'), tb=pg&&pg.querySelector('table[data-ptab] tbody');
      if(!tb) return;
      snap();
      var tr=document.createElement('tr');
      tr.innerHTML='<td class="fill">…</td><td class="fill">…</td><td class="fill">…</td>'+
        '<td>'+(b.getAttribute('data-region')||'')+'</td>'+
        '<td class="rowx"><button type="button" contenteditable="false" '+
        'data-tool="delrow" title="حذف الصف">✕</button></td>';
      tb.appendChild(tr); mark(); snap(); keep();
      tr.scrollIntoView({behavior:'smooth',block:'center'});
      say('أُضيف صف — اكتب اسم الشريك وعرضه ومدته.',4500);
      return;
    }
    if(a==='delrow'){
      var row=b.closest('tr'); if(!row||!row.parentNode) return;
      if(row.parentNode.rows && row.parentNode.rows.length<=1){
        say('هذا آخر صف — امسح ما فيه بدل حذفه.',5000); return;
      }
      snap();
      if(target && row.contains(target)) place(null);
      row.parentNode.removeChild(row);
      snap(); keep(); say('حُذف الصف.',3000);
      return;
    }

  }
"""

# (المرساة، البديل) — كل مرساة مؤكَّدة حتى لا يمرّ تعديل صامت
CHROME = [
    ('حملة غسيل السيارات — عروض المحطات', 'حملة غسيل السيارات — عروض المناطق'),
    ("'darb-carwash-'+c", "'darb-region-'+SLUG[c]"),
    ('var NAMES=%s;', 'var SLUG=' + json.dumps(SLUG, ensure_ascii=False) + ';\nvar NAMES=%s;'),
    ('darb-carwash-slides-v2-', 'darb-region-slides-v2-'),
    ('label for="pick">المحطة', 'label for="pick">المنطقة'),
    ('تنزيل ملف هذه المحطة', 'تنزيل ملف هذه المنطقة'),
    ('تنزيل ملفات كل المحطات', 'تنزيل ملفات كل المناطق'),
    ("'نُزّل ملف محطة '+NAMES[c]", "'نُزّل ملف منطقة '+NAMES[c]"),
    ('نُزّلت ملفات المحطات الإحدى عشرة.', 'نُزّلت ملفات المناطق كلها.'),
    ("'حملة غسيل السيارات — '+NAMES[c]+' '+c", "'حملة غسيل السيارات — منطقة '+NAMES[c]"),
    ('/home/user/-/darb-carwash-slides.html', '/home/user/-/darb-region-slides.html'),
    ('/home/user/-/darb-carwash-slides-artifact.html',
     '/home/user/-/darb-region-slides-artifact.html'),

    # نص التلميح في الشريط العلوي
    ('اضغط «تحرير» لتعديل النص أو حذفه أو إضافة شريحة، واضغط أي صورة لاستبدالها — وكل ذلك ينزل مع الملف.',
     'اضغط «تحرير» لتعديل أي نص أو حذفه أو إضافة شريحة، واضغط أي صورة لاستبدالها، '
     'وفي جدول الشركاء «+ شريك» يضيف صفًا و«✕» يحذفه — وكل ذلك ينزل مع الملف بلا أزرار.'),

    # ١ · الشريط يُعرَّف قبل المحرّر ليكون متاحًا للصفحة وللملف المنزَّل
    ('function darbEditor(opts){', SLIDER + '\nfunction darbEditor(opts){'),

    # ٢ · بعد كل رسم: الأزرار ليست عناصر تُحذف، والشريط يُربط من جديد
    ("""      if(n[i].classList.contains('art')||n[i].classList.contains('veil')) continue;
      if(!n[i].hasAttribute('data-block')) n[i].setAttribute('data-block','');
    }
  }""",
     """      if(n[i].classList.contains('art')||n[i].classList.contains('veil')) continue;
      if(n[i].classList.contains('ptools')||n[i].hasAttribute('data-tool')) continue;
      if(n[i].hasAttribute('data-nav')) continue;
      if(!n[i].hasAttribute('data-block')) n[i].setAttribute('data-block','');
    }
    if(window.darbSlider) window.darbSlider(box);
  }"""),

    # ٣ · ضغطة على زر أداة تنفّذ الأداة ولا تحدّد عنصرًا
    ("""  box.addEventListener('click',function(e){
    if(!editing) return;
    var el=e.target.closest('[data-block]');
    place(el&&box.contains(el)?el:null);
  });""",
     """  box.addEventListener('click',function(e){
    if(!editing) return;
    if(e.target.closest('[data-nav]')) return;   /* أزرار الشريط تخصّ العرض */
    var tb=e.target.closest('[data-tool]');
    if(tb&&box.contains(tb)){ e.preventDefault(); rowTool(tb); return; }
    var el=e.target.closest('[data-block]');
    place(el&&box.contains(el)?el:null);
  });"""),

    # ٤ · أدوات الصفوف
    ('  function setEdit(on){', ROWTOOL + '\n  function setEdit(on){'),

    # ٥ · ملف الشريك: بلا أزرار ولا خانات أدوات
    (r"""    n=t.querySelectorAll('[contenteditable]');""",
     r"""    n=t.querySelectorAll('.rowx,.ptools,[data-tool]');
    for(i=0;i<n.length;i++) if(n[i].parentNode) n[i].parentNode.removeChild(n[i]);
    n=t.querySelectorAll('[contenteditable]');"""),

    # ٧ · الرسالة تحمل زرًا يُنفّذ إجراءً
    ('<div class="toast" id="toast"></div>',
     '<div class="toast" id="toast"><span id="toastmsg"></span>'
     '<button type="button" id="toastact" hidden></button></div>'),

    (r"""  function say(m,ms){ if(!toast) return; toast.textContent=m; toast.classList.add('show');
    clearTimeout(tT); tT=setTimeout(function(){ toast.classList.remove('show'); }, ms||4500); }""",
     r"""  function say(m,ms,actLabel,actFn){
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
    clearTimeout(tT); tT=setTimeout(function(){ toast.classList.remove('show'); }, ms||4500); }"""),

    # عنوان الصفحة كان يكرّر اسم المنطقة: «— مكة مكة»
    (r"""document.title='حملة غسيل السيارات — '+NAMES[this.value]+' '+this.value;""",
     r"""document.title='حملة غسيل السيارات — منطقة '+NAMES[this.value];"""),

    # ٨ · نسخة محفوظة من قبل التحديث لا تُستبدل من تلقاء نفسها، بل يُعرض عليها
    (r"""  document.title='حملة غسيل السيارات — '+NAMES[sel.value]+' '+sel.value;""",
     r"""  function offerFresh(c){
    var old=null; try{ old=localStorage.getItem('darb-region-slides-v2-'+c); }catch(e){}
    if(!old) return;
    if(old.indexOf('data-rslider')>=0 && old.indexOf('data-ptab')>=0) return;
    ed.say('نسختك المحفوظة من منطقة '+NAMES[c]+' سابقة للتحديث، فما ظهر فيها شريط '+
           'تحليلات المناطق ولا جدول الشركاء. «حدّث» يجيبهما، و«تراجع» بعده يرجّع نسختك.',
      20000, 'حدّث', function(){
        ed.snap();
        ed.box.innerHTML=fill(DECKS[c]);
        ed.mark(); ed.snap(); ed.keep(); ed.place(null);
        window.scrollTo(0,0);
        ed.say('حُدّثت شرائح '+NAMES[c]+'. «تراجع» يرجّع نسختك السابقة.',9000);
      });
  }
  offerFresh(sel.value);
  document.title='حملة غسيل السيارات — منطقة '+NAMES[sel.value];"""),

    (r"""    ed.show(load(this.value));""",
     r"""    ed.show(load(this.value));
    offerFresh(this.value);"""),

    # ٦ · الشريط وحده ينزل مع ملف الشريك ليبقى متحرّكًا عنده
    (r"""      '<div class="wrap"><div id="deck">'+body+'</div></div>\\n'+
      '</body>\\n</html>\\n';""",
     r"""      '<div class="wrap"><div id="deck">'+body+'</div></div>\\n'+
      '<script>\\n'+darbSlider.toString()+'\\ndarbSlider(document);\\n<'+'/script>\\n'+
      '</body>\\n</html>\\n';"""),
]

src = open('slides_chrome.py', encoding='utf-8').read()
for old, new in CHROME:
    assert old in src, 'chrome anchor missing: ' + old[:70]
    src = src.replace(old, new)
exec(compile(src, 'slides_chrome.py', 'exec'))
