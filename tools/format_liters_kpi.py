# -*- coding: utf-8 -*-
"""يعرض لترات «إيراد الفترة» و«الإيراد اليومي» بنفس تنسيق قيمة الريال (مختصرة بمليون/ألف)."""
import re

SRC = OUT = "/home/user/-/darb-five-stations-analysis.html"
s = open(SRC, encoding="utf-8").read()

def AB(n):
    """نفس أسلوب الملف: مليون بخانة عشرية واحدة، وألف بعدد صحيح."""
    n = round(n)
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}", "مليون لتر"
    if n >= 1000:
        return f"{round(n/1000):,}", "ألف لتر"
    return f"{n:,}", "لتر"

#  البطاقات المستهدفة: التسمية → نمط استخراج اللترات من سطر .kn
TARGETS = [
    ("إيراد الفترة (النصف الأول 2026)", r"·\s*([\d,]+)\s*لتر"),      # صفحة التحليل الكامل
    ("الإيراد اليومي",                   r"·\s*([\d,]+)\s*لتر/يوم"),   # صفحة التحليل الكامل
    ("إجمالي إيراد الفترة",              r"·\s*([\d,]+)\s*لتر"),      # صفحة المبيعات الشهرية
    ("متوسط الإيراد اليومي",             r"·\s*([\d,]+)\s*لتر/يوم"),   # صفحة المبيعات اليومية
]

count = 0
for label, lit_pat in TARGETS:
    pat = (r'(<div class="kl">' + re.escape(label) + r'</div>)'
           r'(<div class="kv">.*?</div>)'
           r'(<div class="kn">(.*?)</div>)')

    def rep(m):
        global count
        found = re.search(lit_pat, m.group(4))
        if not found:
            return m.group(0)
        val, unit = AB(int(found.group(1).replace(",", "")))
        count += 1
        return (m.group(1) + m.group(2)
                + f'<div class="kv kvl">{val} <small>{unit}</small></div>'
                + m.group(3))

    s = re.sub(pat, rep, s, flags=re.S)

assert count == 20, count      # 5 محطات × 4 بطاقات

CSS = """
<style id="kvl-css">
/* ── قيمة اللترات بنفس تنسيق قيمة الريال داخل البطاقة ── */
.kpi .kv.kvl{color:var(--ink2);margin-top:1px}
.kpi.hot .kv.kvl{color:var(--bgray)}
.kpi .kv.kvl small{color:var(--ink3)}
</style>
"""
s = s.replace("</head>", CSS + "</head>", 1)
s = re.sub(r'data-docid="[^"]*"', 'data-docid="darb-5st-kvl-v1"', s, count=1)

open(OUT, "w", encoding="utf-8").write(s)
print("بطاقات مُعدَّلة:", count, "· الحجم:", round(len(s.encode()) / 1024), "KB")
