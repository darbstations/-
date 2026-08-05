# -*- coding: utf-8 -*-
"""تبويب «الشركاء الخارجيون» لكل محطة — جداول جاهزة تُملأ من استخراج Apify أو يدويًا."""
import openpyxl, re, html, json, os

LOCS = "/root/.claude/uploads/447348d0-0f0b-5d32-9f6b-27c9ad645473/f7a8faea-______5______________.xlsx"
DATA = "/home/user/-/apify/nearby-partners.json"      # يُنتجه tools/apify_nearby_partners.py
SRC = OUT = "/home/user/-/darb-five-stations-analysis.html"
KEEP = ["MK007", "MK017", "MK002", "MK023", "MK019"]
RADIUS_KM = 5

CATS = [
    ("خدمات السيارات", "🔧", ["ورشة سيارات", "مغسلة سيارات", "بنشر", "تغيير زيت",
                              "قطع غيار سيارات", "كهربائي سيارات"],
     "قرب المحطة يجعلها محطة التزود الطبيعية لعملائهم ولسيارات الورشة نفسها"),
    ("تأجير السيارات", "🚗", ["تأجير سيارات", "مكتب تأجير سيارات"],
     "أساطيل تأجير تحتاج تعبئة يومية وعقد شهري بفاتورة موحّدة"),
    ("مكاتب عمرة وحج", "🕋", ["مكتب عمرة", "مكتب حج", "نقل حجاج ومعتمرين"],
     "حافلات المعتمرين تعبئ بكميات كبيرة وتتوقف للاستراحة — أعلى قيمة لكل وقفة"),
    ("أساطيل نقل وشحن", "🚚", ["شركة نقل", "نقل بضائع", "شركة شحن", "مؤسسة باصات"],
     "ديزل بكميات، وتعاقد أسطول، وبطاقة سائق"),
    ("شركات ومنشآت قريبة", "🏢", ["شركة", "مصنع", "مستودع", "مقاولات"],
     "موظفون يتنقلون يوميًا، وسيارات شركة، وإمكانية عقد تعبئة"),
]
COLS = ["المنشأة", "النشاط", "المسافة (م)", "الهاتف", "الحالة", "الخدمة المقترحة", "ملاحظة"]
STATUSES = ["محتمل", "تم التواصل", "عميل حالي", "مستبعد"]

E = lambda t: html.escape(str(t), quote=True)

# ═══════════ 1. الإحداثيات ═══════════
ws = openpyxl.load_workbook(LOCS, data_only=True)["الورقة1"]
LOC = {}
for r in list(ws.iter_rows(values_only=True))[1:]:
    if not r or not r[0]:
        continue
    m = re.search(r"(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)", str(r[1]))
    u = re.search(r"(https?://\S+)", str(r[1]))
    LOC[str(r[0]).strip()] = dict(lat=float(m.group(1)), lng=float(m.group(2)),
                                  url=u.group(1) if u else "")
missing = [c for c in KEEP if c not in LOC]
assert not missing, missing

#  نتائج الاستخراج إن وُجدت
FOUND = {}
if os.path.exists(DATA):
    for row in json.load(open(DATA, encoding="utf-8")):
        FOUND.setdefault(row["كود المحطة"], []).append(row)

# ═══════════ 2. تقسيم الصفحات ═══════════
src = open(SRC, encoding="utf-8").read()
pages_head, pages_all = src.split('<main class="wrap" id="pages">', 1)
blocks = re.split(r'(?=<div class="pgview")', pages_all)
lead, blocks = blocks[0], blocks[1:]
PG, ORDER = {}, []
for b in blocks:
    k = re.search(r'id="pg-([\w-]+)"', b).group(1)
    PG[k] = b
    ORDER.append(k)

ez = max(int(x) for x in re.findall(r'data-ez="z(\d+)"', src))
CS_COUNT = {c: len(re.findall(r'<tr><td>\d{4}-\d\d-\d\d</td>', PG[c + "-cs"])) for c in KEEP}
PT_COUNT = {c: int(re.search(r'الشركاء داخل المحطة</div><div class="kv">(\d+)',
                             PG[c + "-partners"]).group(1)) for c in KEEP}
XT_COUNT = {c: len(FOUND.get(c, [])) for c in KEEP}


def tabs_of(code, active):
    t = [("", "التحليل الكامل"), ("/monthly", "المبيعات الشهرية"), ("/daily", "المبيعات اليومية"),
         ("/targets", "المستهدفات"), ("/cs", "استفسارات العملاء"),
         ("/partners", "الشركاء عبر اليوم"), ("/external", "الشركاء الخارجيون")]
    return '<div class="tabs">' + "".join(
        f'<a class="tab{" on" if suf == active else ""}" href="#/{code}{suf}">{lbl}'
        + (f' <b class="tcount">{CS_COUNT[code]}</b>' if suf == "/cs" else "")
        + (f' <b class="tcount">{PT_COUNT[code]}</b>' if suf == "/partners" else "")
        + (f' <b class="tcount">{XT_COUNT[code]}</b>' if suf == "/external" and XT_COUNT[code] else "")
        + "</a>" for suf, lbl in t) + "</div>"


def status_cell(v="محتمل"):
    return f'<span class="cls c-un xstate" title="اضغط لتغيير الحالة">{E(v)}</span>'


def table_for(code, cat):
    rows = [r for r in FOUND.get(code, []) if r.get("التصنيف لدينا") == cat]
    body = ""
    for r in rows:
        body += ("<tr><td><b>%s</b></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>—</td><td>—</td></tr>"
                 % (E(r.get("الاسم") or "—"), E(r.get("فئة جوجل") or "—"),
                    f'{r.get("المسافة (م)"):,}' if r.get("المسافة (م)") is not None else "—",
                    E(r.get("الهاتف") or "—"), status_cell()))
    if not body:                                    # صفان فارغان للتعبئة اليدوية
        body = ('<tr><td>—</td><td>—</td><td>—</td><td>—</td>'
                f"<td>{status_cell()}</td><td>—</td><td>—</td></tr>") * 2
    head = "".join(f"<th>{c}</th>" for c in COLS)
    return ('<div class="ntable"><div class="tscroll"><table>'
            f"<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div></div>")


# ═══════════ 3. بناء الصفحة ═══════════
for c in KEEP:
    L = LOC[c]
    n_all = XT_COUNT[c]
    pending = n_all == 0
    by_cat = {cat[0]: len([r for r in FOUND.get(c, []) if r.get("التصنيف لدينا") == cat[0]])
              for cat in CATS}
    nearest = min((r for r in FOUND.get(c, []) if r.get("المسافة (م)") is not None),
                  key=lambda r: r["المسافة (م)"], default=None)
    near_txt = "{:,} م".format(nearest["المسافة (م)"]) if nearest else "يُملأ بعد الاستخراج" 

    kpis = (
        '<div class="skpis" style="grid-template-columns:repeat(6,1fr)">'
        f'<div class="kpi hot"><div class="kl">شركاء خارجيون مرصودون</div>'
        f'<div class="kv">{n_all if n_all else "—"}</div>'
        f'<div class="kn">{"بانتظار تنفيذ الاستخراج" if pending else "ضمن نطاق المسح"}</div></div>'
        f'<div class="kpi"><div class="kl">نطاق المسح</div><div class="kv">{RADIUS_KM} <small>كم</small></div>'
        '<div class="kn">نفس نطاق تحليل المنافسين</div></div>'
        f'<div class="kpi"><div class="kl">الفئات المستهدفة</div><div class="kv">{len(CATS)}</div>'
        f'<div class="kn">{sum(len(x[2]) for x in CATS)} مصطلح بحث</div></div>'
        f'<div class="kpi"><div class="kl">إحداثيات المحطة</div>'
        f'<div class="kv" style="font-size:14px">{L["lat"]:.5f}<br>{L["lng"]:.5f}</div>'
        f'<div class="kn"><a href="{E(L["url"])}" target="_blank" rel="noopener">افتح في الخرائط ↗</a></div></div>'
        f'<div class="kpi"><div class="kl">الأقرب</div>'
        f'<div class="kv" style="font-size:15px">{E(nearest["الاسم"]) if nearest else "—"}</div>'
        f'<div class="kn">{near_txt}</div></div>'
        f'<div class="kpi"><div class="kl">الحالة</div>'
        f'<div class="kv" style="font-size:15px">{"جاهز" if not pending else "لم يُنفَّذ"}</div>'
        f'<div class="kn">{"مصدر: خرائط جوجل عبر Apify" if not pending else "حساب Apify تجاوز حده الشهري"}</div></div>'
        "</div>")

    banner = ("" if not pending else
              '<div class="dnote" style="background:#FBF0ED;border:1px solid #EBCFC7">⚠️ '
              '<b>الجداول فارغة عمدًا — الاستخراج لم يُنفَّذ بعد.</b> حساب Apify على الباقة '
              'المجانية وتجاوز حد الاستخدام الشهري، فكل تشغيل مرفوض. ملفات الإدخال جاهزة في '
              '<code>apify/input-' + c + '.json</code> — شغّلها من كونسول Apify وأرسل معرّف '
              'الداتاست فتُملأ الجداول آليًا. وحتى ذلك الحين الجداول <b>قابلة للتعبئة يدويًا</b>: '
              'فعّل وضع التحرير، اكتب في الخلايا، وأضف صفوفًا بزر «＋ صف».</div>')

    sections = ""
    for name, ico, terms, why in CATS:
        chips = "".join(f'<span class="ptag">{E(t)}</span>' for t in terms)
        cnt = by_cat[name]
        sections += (
            f'<div class="sec-h" style="margin-top:20px"><h2>{ico} {name}</h2>'
            f'<span>{cnt if cnt else "—"} منشأة · {why}</span></div>'
            f'<div class="mline hyp" style="margin-bottom:10px"><b>مصطلحات البحث المستخدمة</b>'
            f'<div class="hchips" style="margin-top:6px">{chips}</div></div>'
            + table_for(c, name))

    mini = re.search(r'<div class="mini-head">.*?</div>\s*(?=<div class="skpis")',
                     PG[c + "-monthly"], re.S).group(0)
    nav = re.search(r'<div class="pgnav">.*?</select>\s*</div>', PG[c], re.S).group(0)
    title = re.search(r'data-title="([^"]*)"', PG[c]).group(1).split(" · ")[0]
    ez += 1

    PG[c + "-external"] = (
        f'<div class="pgview" data-ez="z{ez}" id="pg-{c}-external" '
        f'data-title="{title} · الشركاء الخارجيون" hidden>'
        + nav + tabs_of(c, "/external") + mini + kpis + banner
        + '<div class="dnote" style="background:#F0F5FA;border:1px solid #CBDDEB">🎯 '
          '<b>المقصود بالشريك الخارجي:</b> منشأة <b>خارج</b> المحطة ضمن نطاق '
          f'{RADIUS_KM} كم تستطيع المحطة أن تخدمها — بعقد تعبئة أسطول، أو خصم كميات، '
          'أو بطاقة سائق، أو خدمات مساندة (غسيل، صيانة، استراحة). تختلف عن '
          '<b>الشركاء داخل المحطة</b> في التبويب المجاور، وعن <b>المنافسين</b> في صفحة '
          'التحليل الكامل.</div>'
        + sections
        + '<div class="dnote">📐 عمود <b>الحالة</b> يتغيّر بالضغط عليه: '
          + " ← ".join(STATUSES) + '. أعمدة «الخدمة المقترحة» و«ملاحظة» متروكة لكم. '
          'المسافة تُحسب بخط مستقيم من إحداثيات المحطة. مصدر المنشآت عند تنفيذ الاستخراج: '
          'خرائط جوجل عبر Apify — يشمل المدرَج في الخرائط فقط.</div>'
        + '<div class="pgnav" style="margin-top:4px"><div class="nvl">'
          f'<a class="hb" href="#/">⌂ جميع المحطات</a>'
          f'<a href="#/{c}/partners">← الشركاء عبر اليوم</a></div></div></div>')

# ═══════════ 4. التبويب في الصفحات القائمة ═══════════
for c in KEEP:
    for suf, key in (("", c), ("/monthly", c + "-monthly"), ("/daily", c + "-daily"),
                     ("/targets", c + "-targets"), ("/cs", c + "-cs"),
                     ("/partners", c + "-partners")):
        p, k = re.subn(r'<div class="tabs">.*?</div>', tabs_of(c, suf), PG[key], count=1, flags=re.S)
        assert k == 1, key
        PG[key] = p

new_order = []
for k in ORDER:
    new_order.append(k)
    if k.endswith("-partners") and k[:-9] in KEEP:
        new_order.append(k[:-9] + "-external")
pages_all = lead + "".join(PG[k] for k in new_order)

JS = """
<script id="xstate-js">
/* تدوير حالة الشريك الخارجي بالضغط */
(function(){
  var S=%s;
  var C={'محتمل':'c-un','تم التواصل':'c-hd','عميل حالي':'c-nbh','مستبعد':'c-rem'};
  document.addEventListener('click',function(e){
    var el=e.target.closest&&e.target.closest('.xstate'); if(!el)return;
    e.preventDefault();
    var i=S.indexOf(el.textContent.trim());
    var n=S[(i+1)%%S.length];
    Object.keys(C).forEach(function(k){el.classList.remove(C[k]);});
    el.classList.add(C[n]); el.textContent=n;
    var z=el.closest('[data-ez]'); if(z)z.dispatchEvent(new Event('input',{bubbles:true}));
  });
})();
</script>
""" % json.dumps(STATUSES, ensure_ascii=False)

doc = pages_head + '<main class="wrap" id="pages">' + pages_all
doc = doc.replace("</body>", JS + "</body>", 1)
doc = re.sub(r'data-docid="[^"]*"', 'data-docid="darb-5st-external-v1"', doc, count=1)
open(OUT, "w", encoding="utf-8").write(doc)
print("تم · الحجم:", round(len(doc.encode()) / 1024), "KB")
print("بيانات الاستخراج:", "موجودة" if FOUND else "غير موجودة — الجداول جاهزة للتعبئة")
for c in KEEP:
    print(f"  {c}: {XT_COUNT[c]} شريك خارجي · {LOC[c]['lat']:.5f}, {LOC[c]['lng']:.5f}")
