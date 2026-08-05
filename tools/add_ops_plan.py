# -*- coding: utf-8 -*-
"""يضيف تبويب «الخطة التشغيلية» لكل محطة، مبنيًا على أرقام المحطة نفسها.

أربعة محاور كما طُلبت: حملات تشجيع مبيعات أسبوعية · شراكات شهرية ·
توزيعات في المحطة · خدمة مسح السيارات — يليها لوحة متابعة وخارطة ٩٠ يومًا
وحساب صريح لما تغلقه الخطة من الفجوة عن الموازنة.

كل الأرقام مشتقّة من تبويبات الملف نفسه (المستهدفات · الشركاء عبر اليوم ·
الشركاء الخارجيون · استفسارات العملاء)، والافتراضات التخطيطية مكتوبة صراحةً
في ملاحظة أسفل كل قسم.
"""
import re, html, os, math

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = OUT = os.path.join(BASE, "darb-five-stations-analysis.html")
KEEP = ["MK007", "MK017", "MK002", "MK023", "MK019"]
DAYS = 181                     # أيام النصف الأول المسجلة
MONTHS = ["يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]

E = lambda t: html.escape(str(t), quote=True)
F = lambda n: f"{round(n):,}"
M = lambda n: f"{n/1_000_000:.2f}م" if abs(n) >= 1_000_000 else f"{n/1000:.0f} ألف"

src = open(SRC, encoding="utf-8").read()

# ═══════════ 1. تقسيم الصفحات ═══════════
pages_head, pages_all = src.split('<main class="wrap" id="pages">', 1)
blocks = re.split(r'(?=<div class="pgview")', pages_all)
lead, blocks = blocks[0], blocks[1:]
PG, ORDER = {}, []
for b in blocks:
    k = re.search(r'id="pg-([\w-]+)"', b).group(1)
    PG[k] = b
    ORDER.append(k)

MAXEZ = max(int(m) for m in re.findall(r'data-ez="z(\d+)"', src))


# ═══════════ 2. استخراج أرقام كل محطة من الملف ═══════════
def txt(b):
    return html.unescape(re.sub(r"\|+", "|", re.sub(r"<[^>]+>", "|", b)))


N = lambda x: int(str(x).replace(",", "").replace("+", ""))
D = {}
for c in KEEP:
    t_t, t_p, t_c, t_x = (txt(PG[c + s]) for s in ("-targets", "-partners", "-cs", "-external"))
    d = {"code": c}
    ttl = re.search(r'data-title="([^"]*)"', PG[c]).group(1).split(" · ")
    d["name"], d["hood"] = ttl[0].replace("درب ", ""), ttl[1]

    m = re.search(r"إجمالي الأشهر المسجلة\|([\d,]+)\|([\d,]+)\|([+-][\d,]+)\|(\d+)٪", t_t)
    d["bu_h1"], d["ac_h1"], d["gap"], d["ach"] = N(m[1]), N(m[2]), N(m[3]), int(m[4])
    d["bu_year"] = float(re.search(r"موازنة السنة\|([\d.]+)م", t_t)[1]) * 1e6
    m = re.search(r"المتبقي من الموازنة\|([\d.]+)م\| لتر\|(\d+) أشهر · بمعدل ([\d,]+) لتر/شهر", t_t)
    d["rem"], d["rem_months"], d["rate"] = float(m[1]) * 1e6, int(m[2]), N(m[3])
    m = re.search(r"أشهر بلغت الهدف\|(\d+) \|من (\d+)\|أعلى (\S+) (\d+)٪ · أدنى (\S+) (\d+)٪", t_t)
    d["hit"], d["of"], d["best_mo"], d["best_pc"], d["worst_mo"], d["worst_pc"] = \
        int(m[1]), int(m[2]), m[3], int(m[4]), m[5], int(m[6])

    m = re.search(r"الشركاء داخل المحطة\|(\d+)\|([^|]+)\|سيارات يوميًا\|([\d,]+)", t_p)
    d["units"], d["units_mix"], d["cars"] = int(m[1]), m[2].strip(), N(m[3])
    rows = re.findall(
        r"([^|]+)\|(\d\d:\d\d – \d\d:\d\d)\|([\d,]+)\|([\d.]+)٪\|([\d,]+)\|(\d+) ثانية\|"
        r"([\d,]+) ر\.س\|([\d,]+) لتر\|(\d+)(?=\|)", t_p)
    d["parts"] = [{"name": r[0].strip(), "hrs": r[1], "cars": N(r[2]), "pc": float(r[3]),
                   "ppl": N(r[4]), "sar": N(r[6]), "lit": N(r[7]), "units": int(r[8])}
                  for r in rows]
    assert len(d["parts"]) == 6, (c, len(d["parts"]))
    d["peak"] = max(d["parts"], key=lambda p: p["cars"])
    d["low"] = min(d["parts"], key=lambda p: p["cars"])
    d["noon"] = next(p for p in d["parts"] if p["name"] == "ظهر")
    d["night"] = next(p for p in d["parts"] if p["name"] == "ليل")
    d["late"] = next(p for p in d["parts"] if p["name"] == "بعد منتصف الليل")
    d["lit_day_est"] = sum(p["lit"] for p in d["parts"])
    d["sar_day"] = sum(p["sar"] for p in d["parts"])
    d["lit_car"] = d["lit_day_est"] / d["cars"]
    d["lit_day_act"] = d["ac_h1"] / DAYS                 # الأساس المقيس

    d["cs"] = int(re.search(r"إجمالي السجلات\|(\d+)\|", t_c)[1])
    seg = t_c.split("التصنيفات الأكثر تكرارًا")[1].split("قنوات وصول")[0]
    d["cs_cats"] = [(a.strip(), int(b), round(float(p))) for a, b, p in
                    re.findall(r"\|([^|]+)\|(\d+)\| · ([\d.]+)٪", seg)
                    if a.strip() not in ("أخرى", "غير مصنّف") and int(b) >= 3][:3]

    d["xt"] = int(re.search(r"منشآت مرصودة\|(\d+)\|", t_x)[1])
    d["xt_cats"] = {}
    xb = PG[c + "-external"]
    for m in re.finditer(r'<div class="sec-h"[^>]*><h2>\S+ ([^<]+)</h2><span>(\d+) منشأة', xb):
        after = xb.split(m.group(0), 1)[1].split("</table>", 1)[0]
        d["xt_cats"][m[1].strip()] = {
            "n": int(m[2]), "names": re.findall(r"<tr><td><b>([^<]+)</b></td>", after)}
    D[c] = d


# ═══════════ 3. لبنات البناء ═══════════
def tabs_of(code, active, XT, CS, PT, OP):
    t = [("", "التحليل الكامل"), ("/monthly", "المبيعات الشهرية"), ("/daily", "المبيعات اليومية"),
         ("/targets", "المستهدفات"), ("/cs", "استفسارات العملاء"),
         ("/partners", "الشركاء عبر اليوم"), ("/external", "الشركاء الخارجيون"),
         ("/plan", "الخطة التشغيلية")]
    cnt = {"/cs": CS[code], "/partners": PT[code], "/external": XT[code], "/plan": OP}
    return '<div class="tabs">' + "".join(
        f'<a class="tab{" on" if suf == active else ""}" href="#/{code}{suf}">{lbl}'
        + (f' <b class="tcount">{cnt[suf]}</b>' if suf in cnt else "") + "</a>"
        for suf, lbl in t) + "</div>"


def tbl(cols, rows, cls=""):
    head = "".join(f"<th>{c}</th>" for c in cols)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return (f'<div class="ntable {cls}"><div class="tscroll"><table>'
            f"<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div></div>")


def sech(ico, title, sub):
    return f'<div class="sec-h" style="margin-top:22px"><h2>{ico} {title}</h2><span>{sub}</span></div>'


def note(t, warm=True):
    st = "" if warm else ' style="background:#F0F5FA;border:1px solid #CBDDEB"'
    return f'<div class="dnote"{st}>{t}</div>'


def chip(t, k="c-un"):
    return f'<span class="cls {k}">{t}</span>'


# ═══════════ 4. عدّادات التبويبات ═══════════
CS_C = {c: D[c]["cs"] for c in KEEP}
PT_C = {c: D[c]["units"] for c in KEEP}
XT_C = {c: D[c]["xt"] for c in KEEP}
OPN = 18                       # ٤ حملات + ٦ شراكات + ٥ توزيعات + ٣ صيغ غسيل

# افتراضات تخطيطية معلنة
FLEET = {"مكاتب تأجير سيارات": (4050, "15 سيارة × 45 لتر × 6 تعبئات/شهر"),
         "شركات": (2250, "10 سيارات × 45 لتر × 5 تعبئات/شهر"),
         "مدارس": (2880, "4 حافلات × 90 لتر × 8 تعبئات/شهر"),
         "خدمات سيارات": (2700, "30 عميلًا محوَّلًا × 45 لتر × تعبئتان/شهر")}
UP_CAMP, UP_DIST, UP_WASH = .03, .015, .01     # نِسَب رفع مفترضة لكل محور

for c in KEEP:
    d = D[c]
    MAXEZ += 1
    ez = f"z{MAXEZ}"
    P, L = d["peak"], d["low"]
    mo_act = d["lit_day_act"] * 30
    wk_act = d["lit_day_act"] * 7

    # ── مؤشرات الرأس ──
    gp = d["gap"]
    gcls = "hot" if gp < 0 else ""
    kpis = (
        '<div class="skpis" style="grid-template-columns:repeat(6,1fr)">'
        f'<div class="kpi {gcls}"><div class="kl">الفجوة عن الموازنة</div>'
        f'<div class="kv">{"+" if gp>0 else ""}{M(gp)}<small> لتر</small></div>'
        f'<div class="kn">النصف الأول · إنجاز {d["ach"]}٪</div></div>'
        f'<div class="kpi"><div class="kl">المطلوب شهريًا</div><div class="kv">{M(d["rate"])}'
        f'<small> لتر</small></div><div class="kn">{d["rem_months"]} أشهر متبقية من الموازنة</div></div>'
        f'<div class="kpi"><div class="kl">الأساس الحالي</div><div class="kv">{M(mo_act)}'
        f'<small> لتر/شهر</small></div><div class="kn">{F(d["lit_day_act"])} لتر/يوم فعليًا</div></div>'
        f'<div class="kpi"><div class="kl">أقوى فترة</div>'
        f'<div class="kv" style="font-size:15px">{P["name"]}</div>'
        f'<div class="kn">{F(P["cars"])} سيارة/يوم · {P["pc"]}٪ من اليوم</div></div>'
        f'<div class="kpi"><div class="kl">قاعدة الشراكة</div><div class="kv">{d["units"]}'
        f'<small> + {d["xt"]}</small></div>'
        f'<div class="kn">وحدة داخل المحطة + منشأة خارجية مرصودة</div></div>'
        f'<div class="kpi"><div class="kl">مبادرات الخطة</div><div class="kv">{OPN}</div>'
        f'<div class="kn">٤ حملات · ٦ شراكات · ٥ توزيعات · ٣ صيغ غسيل</div></div>'
        "</div>")

    intro = note(
        "🧭 <b>من أين جاءت هذه الخطة:</b> كل رقم فيها مشتقّ من تبويبات هذه المحطة — "
        f"<b>المستهدفات</b> (فجوة {F(abs(gp))} لتر وإنجاز {d['ach']}٪)، "
        f"<b>الشركاء عبر اليوم</b> ({F(d['cars'])} سيارة/يوم موزّعة على ٦ فترات)، "
        f"<b>الشركاء الخارجيون</b> ({d['xt']} منشأة)، و<b>استفسارات العملاء</b> ({d['cs']} سجل). "
        "الافتراضات التخطيطية — نِسَب الرفع والأسعار والتكاليف — مكتوبة صراحةً أسفل كل قسم "
        "لتغيّروها بأرقامكم. <b>الصفحة كلها قابلة للتحرير</b>: فعّلوا وضع التحرير واكتبوا في أي "
        "خلية، واحذفوا أي صف بزر × ، وأضيفوا صفًا أو قسمًا من الشريط السفلي.", False)

    # ══ المحور ١ — حملات أسبوعية ══
    camp = [
        ("الأسبوع 1", "«امتلئ واربح»", "اليوم كامل",
         "سحب أسبوعي على كل تعبئة ≥ 50 لترًا — الفوز بقسيمة وقود 200 ر.س + قسيمة من وحدة داخل المحطة",
         f"{F(d['cars'])} سيارة/يوم", f"+4٪ لترات الأسبوع = {F(wk_act*.04)} لتر",
         "عدد القسائم المفعّلة ÷ عدد التعبئات", "مدير المحطة"),
        ("الأسبوع 2", f"«{'صباح درب' if 'فجر' in L['name'] or 'ضحى' in L['name'] else 'انطلاقة درب'}»",
         f"{L['name']} · {L['hrs']}",
         "قهوة وتمر مجانًا مع تعبئة ≥ 40 لترًا + خصم 20٪ من وحدة داخل المحطة في نفس الفترة",
         f"{F(L['cars'])} سيارة/يوم — أضعف فترة ({L['pc']}٪ من اليوم)",
         f"+8٪ على الفترة = {F(L['lit']*.08*7)} لتر/أسبوع",
         "سيارات الفترة قبل/بعد من عدّاد المضخات", "مشرف الوردية الصباحية"),
        ("الأسبوع 3", "«ذروة العصر»", f"{P['name']} · {P['hrs']}",
         "باقة: تعبئة + مسح زجاج مجاني + قسيمة مشروب — بلا انتظار إضافي (طاقم إضافي على المضخات)",
         f"{F(P['cars'])} سيارة/يوم — أقوى فترة ({P['pc']}٪ من اليوم)",
         f"+4٪ على الفترة = {F(P['lit']*.04*7)} لتر/أسبوع",
         "متوسط اللترات لكل تعبئة في الفترة", "مشرف الذروة"),
        ("الأسبوع 4", "«أسطولك علينا»", f"{d['noon']['name']} · {d['noon']['hrs']}",
         "تسجيل الأساطيل ميدانيًا: بطاقة سائق + فاتورة شهرية موحّدة + خصم كمية — كشك تسجيل داخل المحطة",
         f"{d['xt']} منشأة خارجية مرصودة",
         "3 عقود جديدة على الأقل", "عدد العقود الموقّعة والحجم الشهري لكل عقد", "مسؤول تطوير الأعمال"),
    ]
    sec1 = (sech("📣", "المحور الأول — حملات تشجيع مبيعات أسبوعية",
                 "دورة من أربعة أسابيع تتكرر شهريًا · كل أسبوع يستهدف فترة مختلفة من اليوم")
            + tbl(["الأسبوع", "الحملة", "الفترة المستهدفة", "الآلية", "الأساس المقيس",
                   "المستهدف", "القياس", "المالك"], camp))

    scen = [(f"+{int(u*100)}٪", F(wk_act * u), F(mo_act * u),
             f'{mo_act*u/d["rate"]*100:.0f}٪',
             chip("يسير" if u <= .03 else ("ممكن" if u <= .06 else "طموح"),
                  "c-nbh" if u <= .03 else ("c-rem" if u <= .06 else "c-viv")))
            for u in (.02, .04, .06, .08)]
    sec1 += (f'<div class="sec-h" style="margin-top:4px"><h2 style="font-size:15px">أثر الرفع على '
             f'الفجوة</h2><span>الأساس {F(wk_act)} لتر/أسبوع — من الفعلي المسجل لا من التقدير</span></div>'
             + tbl(["نسبة الرفع", "لترات إضافية/أسبوع", "لترات إضافية/شهر",
                    "من المطلوب شهريًا", "التقدير"], scen)
             + note("📐 <b>الأساس مقيس</b>: لترات النصف الأول الفعلية ÷ 181 يومًا = "
                    f"{F(d['lit_day_act'])} لتر/يوم. <b>نِسَب الرفع مفترضة</b> — وُضعت للتخطيط لا "
                    "كنتيجة قياس، وتُعدَّل بعد أول دورة بالمقارنة قبل/بعد على عدّاد المضخات."))

    # ══ المحور ٢ — شراكات شهرية ══
    order = sorted(d["xt_cats"].items(), key=lambda kv: -kv[1]["n"])
    themes = []
    for cat, v in order:
        per, how = FLEET.get(cat, (2500, "افتراض عام"))
        names = "، ".join(v["names"][:3]) + (f" و{v['n']-3} أخرى" if v["n"] > 3 else "")
        themes.append((cat, v["n"], names, per, how))
    while len(themes) < 4:
        miss = [k for k in FLEET if k not in d["xt_cats"]]
        cat = miss[0] if miss else "منشآت جديدة"
        themes.append((cat, 0, "لا توجد منشآت مرصودة — مسح ميداني في نطاق 3 كم",
                       FLEET.get(cat, (2500, ""))[0], FLEET.get(cat, (0, "افتراض عام"))[1]))
    themes = themes[:4]

    OFFER = {
        "مكاتب تأجير سيارات": "عقد تعبئة أسطول بفاتورة شهرية موحّدة + خصم كمية تصاعدي + أولوية مضخة",
        "شركات": "بطاقة سائق مسبقة الدفع + تقرير استهلاك شهري لكل مركبة + فاتورة واحدة",
        "مدارس": "عقد موسم دراسي لحافلات النقل بمواعيد تعبئة ثابتة خارج الذروة",
        "خدمات سيارات": "إحالة متبادلة: خصم وقود لعملائهم مقابل خصم صيانة لعملائنا + تعبئة سيارات المركز",
    }
    plan_rows, ptotal = [], 0
    for i, mo in enumerate(MONTHS):
        if i < len(themes):
            cat, n, names, per, how = themes[i]
            take = max(1, round(n * .5)) if n else 1
            vol = take * per
            aim = f"{take} من {n}" if n else "1 (بعد المسح)"
            offer = OFFER.get(cat, "عرض يُصاغ بعد الزيارة الأولى")
        elif i == 4:
            cat, names = "الوحدات داخل المحطة", d["units_mix"]
            take, vol, aim = d["units"], round(mo_act * .01), f"{d['units']} وحدة"
            offer = ("عرض مشترك: قسيمة من الوحدة مع كل تعبئة ≥ 50 لترًا، ومقابلها لافتة "
                     "«عبّئ واستفد» داخل الوحدة")
            how = "1٪ من لترات الشهر — تقدير تحفّظي لأثر العرض المشترك"
        else:
            cat, names = "تجديد وتوسعة", "مراجعة كل العقود الموقّعة + منشآت جديدة من المسح الميداني"
            take, vol, aim = 0, round(sum(r[5] for r in plan_rows) * .15), "تجديد 100٪"
            offer = "مراجعة الأحجام الفعلية مقابل المتعاقد عليه، ورفع الخصم لمن تجاوز الحجم"
            how = "15٪ نموًّا على المتعاقد عليه حتى ذلك الشهر"
        ptotal += vol
        plan_rows.append((mo, cat, names, offer, aim, vol, how))

    sec2 = (sech("🤝", "المحور الثاني — شراكات شهرية",
                 f"شراكة محورية لكل شهر من {MONTHS[0]} إلى {MONTHS[-1]} · مبنية على المنشآت "
                 f"المرصودة فعليًا حول المحطة ({d['xt']} منشأة)")
            + tbl(["الشهر", "محور الشراكة", "منشآت مرشّحة", "صيغة العرض", "هدف التعاقد",
                   "حجم متوقع (لتر/شهر)", "أساس التقدير"],
                  [(a, f"<b>{E(b)}</b>", E(cnm), E(off), aim, F(v), E(hw))
                   for a, b, cnm, off, aim, v, hw in plan_rows])
            + note("📐 <b>أحجام التعاقد مفترضة</b> وفق المعدّلات المكتوبة في عمود «أساس التقدير»: "
                   + " · ".join(f"<b>{k}</b> {v[1]}" for k, v in FLEET.items())
                   + ". أسماء المنشآت وأرقامها مأخوذة كما هي من تبويب <b>الشركاء الخارجيون</b>، "
                     "ولم تُتحقّق أحجام أساطيلها ميدانيًا بعد — أول زيارة تصحّح الرقم."))

    # ══ المحور ٣ — توزيعات في المحطة ══
    dist = [
        ("ماء بارد + مناديل", d["noon"], .50, 1.5,
         "خفض إحساس الانتظار في أحرّ فترة، ورفع نسبة «التعبئة الكاملة»"),
        ("قهوة وتمر", L, .60, 2.5, "إحياء أضعف فترة في اليوم وبناء عادة زيارة صباحية"),
        ("قسائم وحدات المحطة", P, .40, 0.0,
         "تحويل ذروة الوقود إلى مبيعات للوحدات — التكلفة على الوحدة الشريكة لا على المحطة"),
        ("علبة أنشطة للأطفال", d["night"], .15, 3.0, "استهداف رحلات العائلات الليلية وإطالة الزيارة"),
        ("بطاقة «أسطولك علينا»", d["late"], .20, 0.5,
         "التقاط سائقي الأساطيل والشاحنات في فترة هدوء المحطة وتحويلهم إلى عقد"),
    ]
    drows, dcost = [], 0
    for nm, p, ratio, unit, why in dist:
        q = round(p["cars"] * ratio)
        cost = q * unit
        dcost += cost
        drows.append((f"<b>{nm}</b>", f'{p["name"]}<br><span class="leg">{p["hrs"]}</span>',
                      F(p["cars"]), F(q), f'{ratio*100:.0f}٪',
                      "على الشريك" if unit == 0 else f"{F(cost)} ر.س", why))
    sec3 = (sech("🎁", "المحور الثالث — توزيعات في المحطة",
                 "كل توزيع مربوط بفترة بعينها وبعدد سياراتها الفعلي — لا توزيع عشوائي على مدار اليوم")
            + tbl(["التوزيع", "الفترة", "سيارات الفترة", "الكمية اليومية", "التغطية",
                   "التكلفة اليومية", "الغرض"], drows)
            + note(f"📐 <b>التكلفة اليومية على المحطة ≈ {F(dcost)} ر.س</b> "
                   f"(≈ {F(dcost*30)} ر.س شهريًا) بأسعار وحدة تقديرية: ماء ومناديل 1.5 ر.س · "
                   "قهوة وتمر 2.5 ر.س · علبة أنشطة 3 ر.س · بطاقة 0.5 ر.س. <b>سيارات الفترة مقيسة</b> "
                   "من عدّاد الحركة، و<b>نِسَب التغطية اختيار تشغيلي</b> — ارفعوها أو اخفضوها "
                   "بحسب الميزانية المتاحة، والجدول يعيد الحساب يدويًا بعد التعديل."))

    # ══ المحور ٤ — مسح السيارات ══
    wash_cards = (
        '<div class="agrid" style="grid-template-columns:1fr 1fr 1fr;margin-bottom:16px">'
        '<div class="card"><div class="ct"><h3>① المسح السريع — مجاني</h3>'
        '<div class="leg">أداة رفع فاتورة</div></div>'
        '<p style="font-size:12.5px;color:var(--ink2);line-height:1.85;margin-top:6px">'
        'مسح زجاج ومرايا أثناء التعبئة، شرطه تعبئة ≥ 60 لترًا. لا يُحتسب إيرادًا — '
        'قيمته أنه يرفع متوسط اللترات لكل تعبئة ويقلّل شكاوى «بطء الخدمة».</p></div>'
        '<div class="card"><div class="ct"><h3>② الغسيل الخارجي — مدفوع</h3>'
        '<div class="leg">25 ر.س</div></div>'
        '<p style="font-size:12.5px;color:var(--ink2);line-height:1.85;margin-top:6px">'
        'غسيل خارجي بالماء المعاد تدويره خلال 7–10 دقائق، في موقع لا يعطّل مسار المضخات. '
        'الفترتان الأنسب: الفترة الأضعف والفترة المتوسطة — لا الذروة.</p></div>'
        '<div class="card"><div class="ct"><h3>③ الاشتراك الشهري</h3>'
        '<div class="leg">149 ر.س / 8 غسلات</div></div>'
        '<p style="font-size:12.5px;color:var(--ink2);line-height:1.85;margin-top:6px">'
        'موجَّه لسائقي الأساطيل ومكاتب التأجير المتعاقدة — يربط الغسيل بعقد الوقود '
        'ويحوّل الزيارة العابرة إلى زيارة متكرّرة.</p></div></div>')

    PRICES = (15, 25, 40)
    wrows = []
    for cap in (.02, .04, .06, .08):
        per_day = d["cars"] * cap
        wrows.append((f"{int(cap*100)}٪", F(per_day), F(per_day * 30),
                      *[f"{F(per_day*30*p)} ر.س" for p in PRICES]))
    FIXED, VAR, SETUP = 7000, 2.5, 25000
    prof = d["cars"] * .04 * 30 * (25 - VAR) - FIXED       # ربح شهري عند سيناريو 4٪
    if prof <= 0:
        payback = "لا يسترد عند هذا الحجم"
    else:
        mn = math.ceil(SETUP / prof)
        payback = ("أقل من شهر" if SETUP / prof < 1 else
                   "شهر واحد" if mn == 1 else "شهران" if mn == 2 else
                   f"{mn} أشهر" if mn <= 10 else f"{mn} شهرًا")
    be = FIXED / (25 - VAR)
    sec4 = (sech("🚿", "المحور الرابع — خدمة مسح السيارات",
                 f"ثلاث صيغ تشغيل · حجم الطلب مشتقّ من {F(d['cars'])} سيارة/يوم تمرّ بالمحطة")
            + wash_cards
            + tbl(["معدل الالتقاط", "سيارة/يوم", "غسلة/شهر"] + [f"إيراد شهري عند {p} ر.س" for p in PRICES],
                  wrows)
            + tbl(["بند التشغيل", "الافتراض", "القيمة"], [
                ("عمالة", "عاملان على وردية واحدة", f"{F(FIXED)} ر.س/شهر"),
                ("ماء ومواد", "لكل غسلة", f"{VAR} ر.س"),
                ("تجهيز أولي", "معدات ضغط + تصريف + مظلة", "25,000 ر.س لمرة واحدة"),
                ("نقطة التعادل", "عند سعر 25 ر.س", f"<b>{F(be)} غسلة/شهر</b> ≈ {F(be/30)} غسلة/يوم"),
                ("ما تعنيه", "من سيارات المحطة", f'<b>{be/30/d["cars"]*100:.1f}٪</b> من المارّين يوميًا'),
                ("استرداد التجهيز", "عند 4٪ التقاط وسعر 25 ر.س", payback),
            ])
            + note("📐 <b>المقيس هنا هو عدد السيارات فقط.</b> معدل الالتقاط والسعر والتكاليف "
                   "كلها <b>افتراضات تخطيطية</b> — الجدول مبني ليختبر السيناريو لا ليعد به. "
                   f"نقطة التعادل تعني أن الخدمة تحتاج <b>{be/30/d['cars']*100:.1f}٪</b> فقط من "
                   "سيارات هذه المحطة لتغطي تشغيلها، وهو ما يجعلها — من ناحية الحجم — "
                   "الأقل مخاطرة بين المحاور الأربعة."))

    # ══ المتابعة ══
    csrow = [(f"شكاوى «{E(a)}»", f"{b} سجل ({p}٪)", "خفض 30٪ خلال 90 يومًا",
              "تقرير خدمة العملاء الشهري", "مدير المحطة") for a, b, p in d["cs_cats"]]
    sec5 = (sech("📊", "لوحة المتابعة الأسبوعية",
                 "خمسة أرقام تُقرأ كل يوم أحد — لا تقرير شهري متأخر")
            + tbl(["المؤشر", "الأساس اليوم", "هدف 90 يومًا", "مصدر القياس", "المالك"], [
                ("لترات/يوم", f"{F(d['lit_day_act'])} لتر", f"{F(d['rate']/30)} لتر",
                 "عدّاد المضخات اليومي", "مدير المحطة"),
                ("الإنجاز مقابل الموازنة", f"{d['ach']}٪", "100٪",
                 "ملف Sales Analysis 2026", "المالية والتشغيل"),
                (f"سيارات الفترة الأضعف ({L['name']})", f"{F(L['cars'])} سيارة/يوم",
                 f"{F(L['cars']*1.08)} سيارة/يوم", "عدّاد الحركة بالساعة", "مشرف الوردية"),
                ("عقود أساطيل نشطة", "—", f"{max(3, round(d['xt']*.4))} عقدًا",
                 "سجل العقود", "مسؤول تطوير الأعمال"),
                ("غسلات/يوم", "—", f"{F(d['cars']*.04)} غسلة", "نظام نقاط البيع", "مشرف الغسيل"),
            ] + csrow))

    # ══ خارطة ٩٠ يومًا ══
    sec6 = (sech("🗓️", "خارطة التنفيذ — 90 يومًا",
                 "ثلاث مراحل · لا تبدأ مرحلة قبل أن يُقاس أثر سابقتها")
            + tbl(["المرحلة", "المدة", "ما يُنجَز", "شرط الانتقال"], [
                ("① التهيئة", "أسبوعان",
                 "قياس الأساس بالفترات · تدريب الطاقم على الحملات · تجهيز موقع الغسيل · "
                 "مسح ميداني للمنشآت المرصودة وتأكيد أحجام أساطيلها",
                 "أساس مقيس موثّق لكل فترة + قائمة منشآت مؤكَّدة"),
                ("② التشغيل", "6 أسابيع",
                 "تشغيل دورة الحملات الأربع · بدء التوزيعات · توقيع أول عقود الشراكة · "
                 "افتتاح الغسيل بسعة نصف طاقة",
                 "دورتان كاملتان من الحملات + 3 عقود موقّعة"),
                ("③ التثبيت", "4 أسابيع",
                 "الإبقاء على ما رفع الأرقام وإيقاف ما لم يرفعها · رفع سعة الغسيل · "
                 "تحويل الشراكات الناجحة إلى عقود سنوية",
                 "قرار موثّق لكل مبادرة: تُثبَّت أو تُوقَف"),
            ]))

    # ══ إغلاق الفجوة ══
    c_camp, c_dist, c_wash = mo_act * UP_CAMP, mo_act * UP_DIST, mo_act * UP_WASH
    c_part = ptotal
    tot = c_camp + c_dist + c_wash + c_part
    share = tot / d["rate"] * 100
    verdict = ("<b>القراءة:</b> المحطة قريبة من موازنتها أصلًا، فدور الخطة هنا أن تحوّل الفارق "
               "إلى فائض لا أن تنقذ رقمًا متعثرًا — وأثرها المتوقع يغطي "
               f"<b>{share:.0f}٪</b> من المطلوب شهريًا."
               if d["ach"] >= 90 else
               "<b>القراءة بصراحة:</b> الفجوة أكبر من أن يغلقها التنشيط وحده — الأثر المتوقع "
               f"يغطي <b>{share:.0f}٪</b> فقط من المطلوب شهريًا. "
               f"محطة تحقق {d['ach']}٪ من موازنتها ستة أشهر متتالية إمّا أن موازنتها نفسها "
               "بحاجة لمراجعة، وإمّا أن لديها خللًا تشغيليًا أعمق من الحملات — "
               "وكلاهما يُحسم قبل صرف ريال واحد على التنشيط.")
    sec7 = (sech("🎯", "ما تغلقه هذه الخطة من الفجوة",
                 f"المطلوب {F(d['rate'])} لتر/شهر · الأساس الحالي {F(mo_act)} لتر/شهر")
            + tbl(["المحور", "أساس التقدير", "أثر شهري متوقع (لتر)", "من المطلوب شهريًا"], [
                ("حملات أسبوعية", f"+{UP_CAMP*100:.0f}٪ على لترات الشهر", F(c_camp),
                 f"{c_camp/d['rate']*100:.0f}٪"),
                ("شراكات شهرية", "المتعاقد عليه تراكميًا حتى ديسمبر", F(c_part),
                 f"{c_part/d['rate']*100:.0f}٪"),
                ("توزيعات في المحطة", f"+{UP_DIST*100:.1f}٪ على لترات الشهر", F(c_dist),
                 f"{c_dist/d['rate']*100:.0f}٪"),
                ("مسح السيارات", f"+{UP_WASH*100:.0f}٪ تحويلًا غير مباشر", F(c_wash),
                 f"{c_wash/d['rate']*100:.0f}٪"),
                (f"<b>الإجمالي</b>", "<b>—</b>", f"<b>{F(tot)}</b>",
                 f'<b class="{"up" if share>=100 else "dn"}">{share:.0f}٪</b>'),
            ])
            + note("⚖️ " + verdict))

    nav = re.search(r'<div class="pgnav">.*?</select>\s*</div>', PG[c], re.S).group(0)
    mini = re.search(r'<div class="mini-head">.*?</div>\s*(?=<div class="skpis")',
                     PG[c + "-monthly"], re.S).group(0)
    title = re.search(r'data-title="([^"]*)"', PG[c]).group(1).split(" · ")[0]

    PG[c + "-plan"] = (
        f'<div class="pgview" data-ez="{ez}" id="pg-{c}-plan" '
        f'data-title="{title} · الخطة التشغيلية" hidden>'
        + nav + tabs_of(c, "/plan", XT_C, CS_C, PT_C, OPN) + mini + kpis + intro
        + sec1 + sec2 + sec3 + sec4 + sec5 + sec6 + sec7
        + '<div class="pgnav" style="margin-top:4px"><div class="nvl">'
          f'<a class="hb" href="#/">⌂ جميع المحطات</a>'
          f'<a href="#/{c}/external">← الشركاء الخارجيون</a></div></div></div>')
    ORDER.insert(ORDER.index(c + "-external") + 1, c + "-plan")

# ═══════════ 5. تحديث أشرطة التبويبات ═══════════
for c in KEEP:
    for suf, key in (("", c), ("/monthly", c + "-monthly"), ("/daily", c + "-daily"),
                     ("/targets", c + "-targets"), ("/cs", c + "-cs"),
                     ("/partners", c + "-partners"), ("/external", c + "-external")):
        p, k = re.subn(r'<div class="tabs">.*?</div>', tabs_of(c, suf, XT_C, CS_C, PT_C, OPN),
                       PG[key], count=1, flags=re.S)
        assert k == 1, key
        PG[key] = p

doc = pages_head + '<main class="wrap" id="pages">' + lead + "".join(PG[k] for k in ORDER)

CSS = """
<style id="plan-css">
/* ── الخطة التشغيلية ── */
#pages .ntable table td{vertical-align:top}
.pgview[id$="-plan"] table td:nth-child(1){min-width:120px}
.pgview[id$="-plan"] table td{white-space:normal;line-height:1.75}
.pgview[id$="-plan"] .agrid .card p{margin-bottom:0}
</style>
"""
doc = doc.replace("</head>", CSS + "</head>", 1)
doc = re.sub(r'data-docid="[^"]*"', 'data-docid="darb-5st-plan-v1"', doc, count=1)
open(OUT, "w", encoding="utf-8").write(doc)

print("تم · الحجم:", round(len(doc.encode()) / 1024), "KB")
for c in KEEP:
    d = D[c]
    mo = d["lit_day_act"] * 30
    print(f"  {c} {d['name']}: فجوة {d['gap']:+,} · مطلوب {d['rate']:,}/شهر · "
          f"أساس {round(mo):,}/شهر · إنجاز {d['ach']}٪ · ذروة {d['peak']['name']} "
          f"· أضعف {d['low']['name']} · خارجي {d['xt']}")
