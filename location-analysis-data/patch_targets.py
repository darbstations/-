# -*- coding: utf-8 -*-
import json, re

B = json.load(open('budget2026.json'))
oc = json.load(open('ops_content.json'))
d = json.load(open('data.json'))
DD = {s['code']: s for s in d['stations']}
FIVE = set(B['five'])
MONTHS = ['يناير','فبراير','مارس','أبريل','مايو','يونيو','يوليو','أغسطس','سبتمبر','أكتوبر','نوفمبر','ديسمبر']
GREEN, RED = '#2E8B6F', '#C0503A'

def fm(v):
    return f'{v/1e6:.1f}م'

def n_(v):
    return f'{v:,.0f}'

def sgn(v, signed):
    return (f'+{v:,.0f}' if v >= 0 and signed else f'{v:,.0f}')

patched, skipped = [], []
for code, tabs in oc.items():
    t = tabs.get('targets') if isinstance(tabs, dict) else None
    if not t or code not in B['all']:
        continue
    e = B['all'][code]
    bud, act0 = e['bud'], e['act']
    signed = code in FIVE
    st = DD.get(code)
    act = list(act0)
    lit = [False]*12
    for mi in (6, 7, 8):  # Jul, Aug, Sep
        if act[mi] is None and st:
            mo = st['monthly'].get(f'2026-{mi+1:02d}')
            v = (mo or {}).get('volume')
            if v:
                act[mi] = round(v)
                lit[mi] = True
    if not any(lit):
        skipped.append(code)

    # preserve existing 2025/growth columns (month rows + totals row)
    mpos = t.find('جدول المستهدفات')
    tb0 = t.find('<tbody>', mpos); tb1 = t.find('</tbody>', tb0)
    old_rows = re.findall(r'<tr[^>]*>(.*?)</tr>', t[tb0:tb1], re.S)
    keep56 = []
    for r in old_rows:
        tds = re.findall(r'<td[^>]*>(.*?)</td>', r, re.S)
        keep56.append((tds[5] if len(tds) > 5 else '—', tds[6] if len(tds) > 6 else '—'))
    while len(keep56) < 13:
        keep56.append(('—', '—'))

    ex = [i for i in range(12) if act[i] is not None]
    nex = len(ex)
    exec_bud = sum(bud[i] or 0 for i in ex)
    act_sum = sum(act[i] for i in ex)
    bud_tot = e['bud_tot'] or sum(x or 0 for x in bud)
    diff_tot = act_sum - exec_bud
    ach_tot = (act_sum / exec_bud) if exec_bud else None
    hits = [i for i in ex if bud[i] and act[i] >= bud[i]]
    pcts = {i: act[i]/bud[i]*100 for i in ex if bud[i]}
    hi = max(pcts, key=pcts.get) if pcts else None
    lo = min(pcts, key=pcts.get) if pcts else None
    contig = nex and ex == list(range(ex[0], ex[-1]+1))
    k2n = f"{nex} أشهر ({MONTHS[ex[0]]} → {MONTHS[ex[-1]]})" if contig and nex else f"{nex} أشهر"
    rem_m = 12 - nex
    rem_bud = bud_tot - act_sum
    k6n = f"{rem_m} أشهر بمعدل {n_(rem_bud/rem_m)} لتر/شهر" if rem_m else "اكتمل تسجيل السنة"
    achc = GREEN if ach_tot and ach_tot >= 1 else RED

    kpis = (f'<div class="skpis" style="grid-template-columns:repeat(6,1fr)">'
            f'<div class="kpi hot"><div class="kl">موازنة السنة</div><div class="kv">{fm(bud_tot)}<small> لتر</small></div><div class="kn">{n_(bud_tot)} لتر لعام 2026</div></div>'
            f'<div class="kpi"><div class="kl">موازنة الأشهر المنفَّذة</div><div class="kv">{fm(exec_bud)}<small> لتر</small></div><div class="kn">{k2n}</div></div>'
            f'<div class="kpi"><div class="kl">الفعلي</div><div class="kv">{fm(act_sum)}<small> لتر</small></div><div class="kn">الفرق {n_(diff_tot)} لتر</div></div>'
            f'<div class="kpi"><div class="kl">الإنجاز</div><div class="kv" style="color:{achc}">{ach_tot*100:.0f}٪</div><div class="kn">الفعلي ÷ الموازنة للأشهر المسجلة</div></div>'
            f'<div class="kpi"><div class="kl">أشهر بلغت الهدف</div><div class="kv">{len(hits)} من {nex}</div><div class="kn">'
            + (f'أعلى {MONTHS[hi]} {pcts[hi]:.0f}٪ · أدنى {MONTHS[lo]} {pcts[lo]:.0f}٪' if hi is not None else '—') + '</div></div>'
            f'<div class="kpi"><div class="kl">المتبقي من الموازنة</div><div class="kv">{fm(rem_bud)}<small> لتر</small></div><div class="kn">{k6n}</div></div></div>')

    vmax = max([x or 0 for x in bud] + [act[i] for i in ex] + [1])
    svg = []
    for i in range(12):
        x0 = 22 + i*89.2
        bv = bud[i] or 0
        hb = bv/vmax*128; yb = 160-hb
        svg.append(f'<rect x="{x0:.1f}" y="{yb:.1f}" width="37.6" height="{hb:.1f}" rx="4" fill="#B9B2A6" opacity="1"><title>{MONTHS[i]} — الموازنة {n_(bv)} لتر</title></rect>')
        if act[i] is not None:
            ha = act[i]/vmax*128; ya = 160-ha
            src = ' (لترات المبيعات)' if lit[i] else ''
            svg.append(f'<rect x="{x0+39.6:.1f}" y="{ya:.1f}" width="37.6" height="{ha:.1f}" rx="4" fill="#F5831F" opacity="1"><title>{MONTHS[i]} — الفعلي{src} {n_(act[i])} لتر</title></rect>')
            if bv:
                p = act[i]/bv*100
                col = GREEN if p >= 100 else RED
                svg.append(f'<text x="{x0+37.6:.1f}" y="{min(yb,ya)-6:.1f}" font-size="11" font-weight="700" text-anchor="middle" fill="{col}">{p:.0f}٪</text>')
        svg.append(f'<text x="{x0+37.6:.1f}" y="180" font-size="11.5" text-anchor="middle" fill="var(--ink2)">{MONTHS[i]}</text>')
    chart = (f'<div class="chartbox"><h3>الموازنة مقابل الفعلي — 12 شهرًا</h3>'
             f'<div class="cs">العمود الرمادي: المستهدف · العمود البرتقالي: المتحقق · النسبة فوق كل شهر هي الإنجاز — أخضر إذا بلغ الهدف وأحمر إن لم يبلغه · † فعلي من لترات المبيعات</div>'
             f'<svg viewBox="0 0 1100 190" class="spark" role="img" aria-label="الموازنة مقابل الفعلي">{"".join(svg)}</svg>'
             f'<div class="plegend"><span><i style="background:#B9B2A6"></i>الموازنة (المستهدف)</span><span><i style="background:#F5831F"></i>الفعلي</span><span>النسبة أعلى كل شهر = الإنجاز</span></div></div>')

    rows = []
    for i in range(12):
        bv = bud[i] or 0
        if act[i] is None:
            rows.append(f'<tr><td><b>{MONTHS[i]}</b></td><td>{n_(bv)}</td><td>—</td><td>—</td><td>—</td><td>{keep56[i][0]}</td><td>{keep56[i][1]}</td></tr>')
        else:
            dv = act[i] - bv
            p = act[i]/bv*100 if bv else None
            cls = 'up' if p is not None and p >= 100 else 'dn'
            sup = '<sup title="من لترات مبيعات المحطة الفعلية">†</sup>' if lit[i] else ''
            pc = f'<span class="{cls}">{p:.0f}٪</span>' if p is not None else '—'
            rows.append(f'<tr><td><b>{MONTHS[i]}</b></td><td>{n_(bv)}</td><td>{n_(act[i])}{sup}</td><td>{sgn(dv, signed)}</td><td>{pc}</td><td>{keep56[i][0]}</td><td>{keep56[i][1]}</td></tr>')
    tcls = 'up' if ach_tot and ach_tot >= 1 else 'dn'
    rows.append(f'<tr style="background:#FBF9F5;font-weight:700"><td><b>الإجمالي</b></td><td>{n_(bud_tot)}</td><td>{n_(act_sum)}</td><td>{sgn(diff_tot, signed)}</td>'
                f'<td><span class="{tcls}">{ach_tot*100:.0f}٪</span></td><td>{keep56[12][0]}</td><td>{keep56[12][1]}</td></tr>')
    new_tbody = ''.join(rows)

    # splice
    i_chart = t.find('<div class="chartbox">')
    i_sec = t.find('<div class="sec-h"><h2>جدول المستهدفات')
    assert t.startswith('<div class="skpis"') and i_chart > 0 and i_sec > i_chart, code
    out = kpis + chart + t[i_sec:]
    tb0 = out.find('<tbody>', out.find('جدول المستهدفات')); tb1 = out.find('</tbody>', tb0)
    out = out[:tb0+7] + new_tbody + out[tb1:]
    if any(lit):
        dn0 = out.find('<div class="dnote">', out.find('</tbody>', out.find('جدول المستهدفات')))
        dn1 = out.find('</div>', dn0)
        clause = ' فعلي <b>يوليو → سبتمبر</b> المعلَّم † مأخوذ من لترات مبيعات المحطة الفعلية (التقرير الشبكي يناير–سبتمبر 2026)، لا من ملف الموازنة.'
        out = out[:dn1] + clause + out[dn1:]
    tabs['targets'] = out
    patched.append(code)

json.dump(oc, open('ops_content.json', 'w'), ensure_ascii=False)
print('patched:', len(patched), '| no liters added (kept as-was):', skipped)
t = oc['MK001']['targets']
print('MK001 Sept row:', re.search(r'<tr><td><b>سبتمبر</b></td>.*?</tr>', t).group(0)[:220])
t7 = oc['MK007']['targets']
print('MK007 seasonal intact:', 'سبب كل شهر' in t7, '| 2025 kept:', t7.count('1,379,729') > 0, '| len', len(t7))
t17 = oc['MK017']['targets']
import re as _re
y25 = _re.findall(r'<tr><td><b>\w+</b></td>(?:<td>[^<]*</td>){4}<td>([^<]+)</td>', t17)
print('MK017 2025 col sample:', y25[:3])
