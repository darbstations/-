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
    <div class="strip">
      <div class="fact"><div class="k">سيارات كل يوم</div><div class="v">{cars}</div><div class="u">اليوم كامل</div></div>
      <div class="fact"><div class="k">سيارات في الشهر</div><div class="v">{month}</div><div class="u">على مدار اليوم</div></div>
      <div class="fact"><div class="k">متوسط فاتورة الوقود</div><div class="v">{inv}</div><div class="u">لكل تعبئة</div></div>
      <div class="fact"><div class="k">مشاهدات الحملة</div><div class="v">١٠٠ ألف</div><div class="u">خلال أسبوع</div></div>
      <div class="fact"><div class="k">ذروة الحركة</div><div class="v">{peak}</div><div class="u">أفضل وقت للتوزيع</div></div>
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

    return dict(region=region, nst=nstations(len(ss)),
                cars=n0(cars), month=n0(cars * 30), inv=n1(wavg('inv')) + ' ر.س',
                peak=hour(peak),
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

# the toolbar, editor and emit block are the ones already agreed for the decks
exec(compile(open('slides_chrome.py', encoding='utf-8').read().replace(
    'حملة غسيل السيارات — عروض المحطات', 'حملة غسيل السيارات — عروض المناطق')
    .replace("'darb-carwash-'+c", "'darb-region-'+SLUG[c]")
    .replace('var NAMES=%s;', 'var SLUG=' + json.dumps(SLUG, ensure_ascii=False) + ';\nvar NAMES=%s;')
    .replace('darb-carwash-slides-v2-', 'darb-region-slides-v2-')
    .replace("label for=\"pick\">المحطة", "label for=\"pick\">المنطقة")
    .replace('تنزيل ملف هذه المحطة', 'تنزيل ملف هذه المنطقة')
    .replace('تنزيل ملفات كل المحطات', 'تنزيل ملفات كل المناطق')
    .replace("'نُزّل ملف محطة '+NAMES[c]", "'نُزّل ملف منطقة '+NAMES[c]")
    .replace('نُزّلت ملفات المحطات الإحدى عشرة.', 'نُزّلت ملفات المناطق كلها.')
    .replace("'حملة غسيل السيارات — '+NAMES[c]+' '+c", "'حملة غسيل السيارات — منطقة '+NAMES[c]")
    .replace("/home/user/-/darb-carwash-slides.html", "/home/user/-/darb-region-slides.html")
    .replace("/home/user/-/darb-carwash-slides-artifact.html",
             "/home/user/-/darb-region-slides-artifact.html"),
    'slides_chrome.py', 'exec'))
