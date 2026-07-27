# -*- coding: utf-8 -*-
"""Build location-analysis.html — per-station location & sales analysis (PEST/Persona/SWOT/Competitors)."""
import json, html, statistics

A = json.load(open('analysis.json'))
DATA = json.load(open('data.json'))
XL = json.load(open('stations.json'))
try:
    COMP = json.load(open('competitors.json'))
except FileNotFoundError:
    COMP = {}
BYCODE = {s['code']: s for s in DATA['stations']}
GEN = DATA.get('generated', '')

def esc(x): return html.escape(str(x), quote=True)
def n0(x): return f"{x:,.0f}"
def sar(x):
    if x >= 1e6: return f"{x/1e6:,.1f} <small>مليون ر.س</small>"
    return f"{x/1e3:,.0f} <small>ألف ر.س</small>"
def pct(x): return f"{x*100:.0f}٪"
def hr_ar(h):
    h12 = h % 12 or 12
    suf = 'ص' if h < 12 else 'م'
    return f"{h12}{suf}"

ORDER = sorted(A.values(), key=lambda a: -a['metrics']['daily_rev'])
REGIONS = []
for a in ORDER:
    r = a['metrics']['region']
    if r not in REGIONS: REGIONS.append(r)

def spark_hours(code):
    o = BYCODE[code]['overall']
    hs = {h['h']: h['vis'] for h in o['hours']}
    mx = max(hs.values()) or 1
    bars = []
    W, H, bw = 240, 44, 8
    for h in range(24):
        v = hs.get(h, 0)
        bh = max(2, round(v/mx*(H-12)))
        x = 2 + h*(bw+2)
        hot = 'url(#gO)' if v == mx else ('#E4B98F' if v >= 0.75*mx else 'var(--bar)')
        bars.append(f'<rect x="{x}" y="{H-8-bh}" width="{bw}" height="{bh}" rx="2" fill="{hot}"/>')
        if h % 6 == 0:
            bars.append(f'<text x="{x+bw/2}" y="{H-1}" font-size="6.5" text-anchor="middle" fill="var(--ink3)">{hr_ar(h)}</text>')
    return (f'<svg viewBox="0 0 {W+4} {H}" class="spark" role="img" aria-label="توزيع الزيارات على الساعات">'
            f'<defs><linearGradient id="gO" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="#F5A623"/><stop offset="1" stop-color="#F37021"/></linearGradient></defs>{"".join(bars)}</svg>')

def spark_dow(code):
    o = BYCODE[code]['overall']
    ds = [(d['d'], d['avg']) for d in o['dow']]
    if not ds: return ''
    mx = max(v for _, v in ds) or 1
    W, H, bw = 240, 46, 26
    bars = []
    for i, (d, v) in enumerate(ds):
        bh = max(2, round(v/mx*(H-16)))
        x = 3 + i*(bw+8)
        hot = 'url(#gO)' if v == mx else 'var(--bar)'
        bars.append(f'<rect x="{x}" y="{H-12-bh}" width="{bw}" height="{bh}" rx="3" fill="{hot}"/>'
                    f'<text x="{x+bw/2}" y="{H-2}" font-size="7" text-anchor="middle" fill="var(--ink3)">{d[:7]}</text>')
    return (f'<svg viewBox="0 0 {W+4} {H}" class="spark" role="img" aria-label="متوسط الزيارات حسب اليوم">'
            f'{"".join(bars)}</svg>')

def mixbar(parts):
    """parts: [(label, frac, color)] -> stacked bar + legend"""
    seg, leg, x = [], [], 0.0
    for lb, fr, colr in parts:
        w = max(0.0, fr*100)
        seg.append(f'<i style="width:{w:.1f}%;background:{colr}" title="{esc(lb)} {fr*100:.0f}٪"></i>')
        leg.append(f'<span><b style="background:{colr}"></b>{esc(lb)} {fr*100:.0f}٪</span>')
        x += w
    return f'<div class="mix"><div class="mixbar">{"".join(seg)}</div><div class="mixleg">{"".join(leg)}</div></div>'

def stars(r):
    return f'<span class="stars">★ {r}</span>' if r else ''

def station_section(a):
    m, g, comp = a['metrics'], a['geo'], (COMP.get(m0['code']) if (m0:=a['metrics']) else None)
    code = m['code']
    x = next((r for r in XL if r['num'] == code), {})
    stt = 'تشغيل' if x.get('status') == 'Operation' else ('فرنشايز' if x.get('status') == 'Franchises' else '—')
    cls = m['cls'] or 'غير مصنفة'
    cls_cl = {'حيوية':'c-viv','حي':'c-nbh','خط سفر':'c-hwy','مختلط':'c-mix','نائية':'c-rem'}.get(cls, 'c-un')
    growth = m['growth']
    gr_html = '—' if growth is None else (f'<span class="up">+{growth:.1f}٪</span>' if growth >= 0 else f'<span class="dn">{growth:.1f}٪</span>')
    period = f"{len(m['months'])} أشهر" if m['nmonths'] < 6 else 'النصف الأول 2026'
    maps_url = next((r['loc'] for r in XL if r['num'] == code), '#')

    kpis = f'''
    <div class="skpis">
      <div class="kpi hot"><div class="kl">إيراد الفترة ({esc(period)})</div><div class="kv">{sar(m['revenue'])}</div><div class="kn">{n0(m['visits'])} زيارة · {n0(m['volume'])} لتر</div></div>
      <div class="kpi"><div class="kl">الإيراد اليومي</div><div class="kv">{sar(m['daily_rev'])}</div><div class="kn">المرتبة {m['rank_drev']} من {m['n_total']} بالشبكة</div></div>
      <div class="kpi"><div class="kl">الزيارات اليومية</div><div class="kv">{n0(m['daily_vis'])}</div><div class="kn">ذروة الزيارات {hr_ar(m['peak_hour'])}</div></div>
      <div class="kpi"><div class="kl">متوسط الفاتورة</div><div class="kv">{m['avg_invoice']:.0f} <small>ر.س</small></div><div class="kn">متوسط التعبئة {m['avg_liters']:.0f} لترًا</div></div>
      <div class="kpi"><div class="kl">نمو Q2 مقابل Q1</div><div class="kv">{gr_html}</div><div class="kn">{'مقارنة ربعية مثل-بمثل' if growth is not None else 'لا تتوفر مقارنة (بيانات جزئية)'}</div></div>
      <div class="kpi"><div class="kl">تقييم جوجل</div><div class="kv">{g['rating'] if g else '—'} <small>★</small></div><div class="kn">{n0(g['reviews']) if g else '—'} مراجعة</div></div>
    </div>'''

    sig = f'''
    <div class="card sig">
      <div class="ct"><h3>توقيع الموقع الزمني والسلوكي</h3><div class="leg">من بيانات المبيعات الفعلية</div></div>
      <div class="siggrid">
        <div><div class="sglb">الزيارات على مدار اليوم</div>{spark_hours(code)}
             <div class="sgnote">المساء (4م–12ل): {pct(m['evening'])} · الليل (12–5ص): {pct(m['night'])} · الصباح: {pct(m['morning'])}</div></div>
        <div><div class="sglb">متوسط الزيارات حسب اليوم</div>{spark_dow(code)}
             <div class="sgnote">نهاية الأسبوع مقابل أيام العمل: {f"{m['we_ratio']:.2f}×" if m['we_ratio'] else '—'}</div></div>
        <div><div class="sglb">مزيج الوقود (من الإيراد)</div>{mixbar([('بنزين 91', m['g91'], '#3E6E8E'), ('بنزين 95', m['g95'], '#F37021'), ('ديزل', m['dsl'], '#6E6A64')])}
             <div class="sglb" style="margin-top:12px">طرق الدفع (من الإيراد)</div>{mixbar([('نقد', m['cash'], '#2E8B6F'), ('بطاقة', m['card'], '#3E6E8E'), ('تطبيقات وأخرى', m['apps'], '#F5A623')])}</div>
      </div>
    </div>'''

    pers = ''.join(f'''
      <div class="pcard"><div class="pico">{p['icon']}</div>
        <div class="pbody"><div class="pname">{esc(p['name'])} <span class="pshare">{esc(p['share'])}</span></div>
        <p>{esc(p['desc'])}</p>
        <div class="pline"><b>يحتاج:</b> {esc(p['wants'])}</div>
        <div class="pline act"><b>التحرك التسويقي:</b> {esc(p['msg'])}</div></div></div>''' for p in a['personas'])

    sw = a['swot']
    def lis(xs): return ''.join(f'<li>{esc(i)}</li>' for i in xs)
    swot = f'''
    <div class="swot">
      <div class="sq s"><h4>القوة</h4><ul>{lis(sw['s'])}</ul></div>
      <div class="sq w"><h4>الضعف</h4><ul>{lis(sw['w'])}</ul></div>
      <div class="sq o"><h4>الفرص</h4><ul>{lis(sw['o'])}</ul></div>
      <div class="sq t"><h4>التهديدات</h4><ul>{lis(sw['t'])}</ul></div>
    </div>'''

    pe = a['pest']
    pest = f'''
    <div class="pest">
      <div class="pr"><span class="pk pP">P</span><div><b>سياسي/تنظيمي</b><ul>{lis(pe['p'])}</ul></div></div>
      <div class="pr"><span class="pk pE">E</span><div><b>اقتصادي</b><ul>{lis(pe['e'])}</ul></div></div>
      <div class="pr"><span class="pk pS">S</span><div><b>اجتماعي</b><ul>{lis(pe['s'])}</ul></div></div>
      <div class="pr"><span class="pk pT">T</span><div><b>تقني</b><ul>{lis(pe['t'])}</ul></div></div>
    </div>'''

    if comp:
        dens = comp['n']
        if comp.get('thin'):
            dcls, dlab = 'md', 'رصد غير مكتمل'
        else:
            dcls, dlab = ('lo', 'منافسة منخفضة') if dens <= 4 else (('md', 'منافسة متوسطة') if dens <= 9 else ('hi', 'منافسة مرتفعة'))
        rows = ''.join(f'''<tr><td>{esc(c['title'])}</td><td>{c['dist']:,} م</td>
            <td>{c['rating'] if c['rating'] else '—'}</td><td>{n0(c['reviews']) if c['reviews'] else '—'}</td></tr>''' for c in comp['top'])
        sisters = ''
        if comp.get('sisters'):
            ss = '، '.join(f"{esc(s['title'])} ({s['dist']:,} م)" for s in comp['sisters'][:4])
            sisters = f'<div class="sis">🧡 محطات درب شقيقة ضمن النطاق: {ss} — تغطية شبكية وليست منافسة.</div>'
        ratingline = ''
        if comp.get('avg_rating') and a['geo']:
            diff = a['geo']['rating'] - comp['avg_rating']
            v = 'أعلى' if diff >= 0 else 'أدنى'
            ratingline = f"متوسط تقييم المنافسين {comp['avg_rating']:.1f}★ — درب {v} بـ{abs(diff):.1f} نقطة."
        compb = f'''
        <div class="card comp"><div class="ct"><h3>المنافسون ضمن 5 كم</h3>
          <div class="leg"><span class="dens {dcls}">{dens} محطة · {dlab}</span></div></div>
          <div class="cs">{'⚠️ المسح الآلي لهذه الدائرة أعاد نتائج شحيحة ولا يُعتد به وحده — يُوصى بتدقيق يدوي قبل أي قرار تنافسي. ' if comp.get('thin') else ''}الأقرب: {esc(comp['nearest']['title']) if comp.get('nearest') else 'لم تُرصد محطات'}
             {f"على بعد {comp['nearest']['dist']:,} م" if comp.get('nearest') else ''} · {ratingline}
             مصدر الرصد: خرائط جوجل (يوليو 2026).</div>
          <div class="ctbl"><table><thead><tr><th>المحطة المنافسة</th><th>المسافة</th><th>التقييم</th><th>المراجعات</th></tr></thead>
          <tbody>{rows or '<tr><td colspan="4">لم يرصد المسح الآلي محطات منافسة داخل الدائرة</td></tr>'}</tbody></table></div>{sisters}
        </div>'''
    else:
        compb = '<div class="card comp"><div class="ct"><h3>المنافسون ضمن 5 كم</h3></div><div class="cs">جارٍ الرصد…</div></div>'

    return f'''
  <section class="station" id="{code}" data-region="{esc(m['region'])}" data-name="{esc(m['name'])} {code}">
    <div class="shead">
      <div class="stitle">
        <span class="badge">{code}</span><h2>{esc(m['name'])}</h2>
        <span class="cls {cls_cl}">{esc(cls)}</span><span class="cls c-st">{stt}</span>
      </div>
      <div class="smeta">
        <span>📍 {esc(m['region'])}{(' · ' + esc(g['hood'])) if g and g.get('hood') else ''}</span>
        {stars(g['rating']) if g else ''}
        <a href="{esc(maps_url)}" target="_blank" rel="noopener">افتح في خرائط جوجل ↗</a>
      </div>
      <div class="saddr">{esc(g['address']) if g else ''}{(' — ' + esc(m['note'])) if m['note'] else ''}</div>
    </div>
    {kpis}
    {sig}
    <div class="agrid">
      <div class="card"><div class="ct"><h3>بيرسونا العملاء</h3><div class="leg">مشتقة من مزيج الوقود والأوقات والدفع</div></div>{pers}</div>
      <div class="card"><div class="ct"><h3>تحليل SWOT</h3><div class="leg">مبيعات + موقع + منافسة</div></div>{swot}</div>
      <div class="card"><div class="ct"><h3>تحليل PEST</h3><div class="leg">بيئة {esc(m['region'])} الكلية</div></div>{pest}</div>
      {compb}
    </div>
  </section>'''

# ---------- overview ----------
tot_rev = sum(a['metrics']['revenue'] for a in ORDER)
tot_vis = sum(a['metrics']['visits'] for a in ORDER)
avg_rt = statistics.mean(a['geo']['rating'] for a in ORDER if a['geo'])
ncomp = COMP.get('_meta',{}).get('unique_competitors') if COMP else None

chips = '<button class="chip on" data-r="*"><span class="nm">الكل</span><span class="code">' + str(len(ORDER)) + '</span></button>'
for r in REGIONS:
    n = sum(1 for a in ORDER if a['metrics']['region'] == r)
    chips += f'<button class="chip" data-r="{esc(r)}"><span class="nm">{esc(r)}</span><span class="code">{n}</span></button>'

ov_rows = ''
for i, a in enumerate(ORDER, 1):
    m, g = a['metrics'], a['geo']
    c = COMP.get(m['code'])
    gr = m['growth']
    gh = '—' if gr is None else (f'<span class="up">+{gr:.0f}٪</span>' if gr >= 0 else f'<span class="dn">{gr:.0f}٪</span>')
    ov_rows += f'''<tr data-region="{esc(m['region'])}" onclick="location.hash='{m['code']}'">
      <td>{i}</td><td><b>{esc(m['name'])}</b> <span class="tcode">{m['code']}</span></td><td>{esc(m['region'])}</td>
      <td>{esc(m['cls'] or '—')}</td><td>{n0(m['daily_rev'])}</td><td>{m['avg_invoice']:.0f}</td><td>{gh}</td>
      <td>{(str(c['n']) + ('*' if c.get('thin') else '')) if c else '—'}</td><td>{g['rating'] if g else '—'}</td></tr>'''

# excluded stations appendix
nosales = [r for r in XL if r['num'] not in A]
from collections import Counter
bycity = Counter(r['city'].strip() for r in nosales)
app_sum = '، '.join(f"{c} ({n})" for c, n in bycity.most_common())
app_rows = ''.join(f"<tr><td>{esc(r['num'])}</td><td>{esc(r['city'])}</td><td>{esc(r['name'])}</td>"
                   f"<td>{'تشغيل' if r['status']=='Operation' else 'فرنشايز'}</td>"
                   f"<td><a href='{esc(r['loc'])}' target='_blank' rel='noopener'>الموقع ↗</a></td></tr>" for r in nosales)

html_out = f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>درب · تحليل المواقع والمبيعات — PEST · بيرسونا · SWOT · المنافسون</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;500;600;700&family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet">
<style>
:root{{--orange:#F37021;--gold1:#F5A623;--ink:#3D3D3D;--ink2:#6E6A64;--ink3:#9B968E;--bg:#F7F4EF;--card:#FFFFFF;
--line:#ECE6DD;--line2:#E3DCD1;--bar:#E0D9CD;--good:#2E8B6F;--bad:#C0503A;--blue:#3E6E8E;
--shadow:0 1px 2px rgba(61,61,61,.04),0 8px 24px rgba(61,61,61,.06);--radius:16px}}
*{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth}}
body{{font-family:'IBM Plex Sans Arabic','Tajawal',system-ui,sans-serif;background:var(--bg);color:var(--ink);line-height:1.55;font-size:15px}}
::selection{{background:var(--orange);color:#fff}}
.wrap{{max-width:1240px;margin:0 auto;padding:0 22px}}
header{{background:#1d1c1b;color:#fff;padding:34px 0 26px}}
.brand{{display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap}}
.mark .ar{{font-family:'Tajawal';font-weight:800;font-size:30px;letter-spacing:-.5px}}
.mark .ar b{{color:var(--orange)}}
.mark .en{{font-size:10.5px;letter-spacing:3.5px;color:#b9b3aa;margin-top:3px}}
.hd-title{{text-align:left}}
.hd-title h1{{font-size:17px;font-weight:600}}
.hd-title p{{font-size:12px;color:#b9b3aa;margin-top:3px}}
.netkpis{{display:grid;grid-template-columns:repeat(5,1fr);gap:1px;background:rgba(255,255,255,.09);border-radius:14px;overflow:hidden;margin-top:22px}}
.netkpis>div{{background:#26241f;padding:13px 16px}}
.netkpis .v{{font-family:'Tajawal';font-weight:800;font-size:21px;color:var(--gold1)}}
.netkpis .v small{{font-size:11px;color:#b9b3aa;font-weight:500}}
.netkpis .l{{font-size:11.5px;color:#b9b3aa;margin-top:2px}}
@media(max-width:900px){{.netkpis{{grid-template-columns:repeat(2,1fr)}}}}
.stationbar{{background:var(--card);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:40;box-shadow:0 2px 10px rgba(61,61,61,.05)}}
.chips{{display:flex;gap:7px;overflow-x:auto;padding:11px 22px;max-width:1240px;margin:0 auto;scrollbar-width:thin;align-items:center}}
.chip{{flex:none;border:1px solid var(--line2);background:#fff;border-radius:11px;padding:7px 13px;cursor:pointer;font-family:inherit;font-size:13px;color:var(--ink2);transition:.14s;display:flex;gap:7px;align-items:center}}
.chip:hover{{border-color:var(--orange);color:var(--ink)}}
.chip.on{{background:var(--ink);border-color:var(--ink);color:#fff}}
.chip .code{{font-size:10.5px;color:var(--ink3);font-family:'Tajawal'}}
.chip.on .code{{color:var(--gold1)}}
.search{{flex:none;margin-inline-start:auto}}
.search input{{border:1px solid var(--line2);border-radius:11px;padding:8px 13px;font-family:inherit;font-size:13px;width:220px;background:#fff;color:var(--ink)}}
.search input:focus{{outline:2px solid var(--orange);border-color:var(--orange)}}
main{{padding:26px 0 40px}}
.sec-h{{display:flex;align-items:baseline;gap:10px;margin:8px 0 14px}}
.sec-h h2{{font-size:19px;font-weight:800;font-family:'Tajawal'}}
.sec-h span{{font-size:12px;color:var(--ink3)}}
.ntable{{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;box-shadow:var(--shadow);margin-bottom:34px}}
.ntable .tscroll{{overflow-x:auto}}
table{{width:100%;border-collapse:collapse;font-size:13.5px}}
th{{text-align:right;font-size:12px;color:var(--ink2);font-weight:600;padding:11px 14px;border-bottom:1px solid var(--line);background:#FBF9F5;white-space:nowrap}}
td{{padding:10px 14px;border-bottom:1px solid var(--line);white-space:nowrap}}
tbody tr{{cursor:pointer;transition:.12s}}
tbody tr:hover{{background:#FBF6EF}}
.tcode{{font-size:11px;color:var(--ink3);font-family:'Tajawal';letter-spacing:.4px}}
.up{{color:var(--good);font-weight:700}}.dn{{color:var(--bad);font-weight:700}}
.station{{background:var(--card);border:1px solid var(--line);border-radius:20px;box-shadow:var(--shadow);padding:22px 22px 18px;margin-bottom:26px;scroll-margin-top:70px}}
.shead{{border-bottom:1px dashed var(--line2);padding-bottom:14px;margin-bottom:16px}}
.stitle{{display:flex;align-items:center;gap:10px;flex-wrap:wrap}}
.stitle h2{{font-family:'Tajawal';font-weight:800;font-size:22px}}
.badge{{font-size:12px;font-weight:700;background:var(--ink);color:#fff;padding:3px 9px;border-radius:7px;font-family:'Tajawal';letter-spacing:.5px}}
.cls{{font-size:11.5px;font-weight:700;padding:3px 10px;border-radius:8px;border:1px solid transparent}}
.c-viv{{background:#FDEEE2;color:#B4500F;border-color:#F5CBA8}}
.c-nbh{{background:#E9F2EC;color:#22694F;border-color:#BFDCCB}}
.c-hwy{{background:#E8EFF5;color:#2D5674;border-color:#BED3E2}}
.c-mix{{background:#F3ECFA;color:#5E3A85;border-color:#D8C6EC}}
.c-rem{{background:#F5F1E8;color:#7A6A3A;border-color:#E0D5B8}}
.c-un{{background:#F1EFEB;color:#6E6A64;border-color:#DDD8CF}}
.c-st{{background:#fff;color:var(--ink2);border-color:var(--line2)}}
.smeta{{display:flex;gap:16px;align-items:center;font-size:13px;color:var(--ink2);margin-top:8px;flex-wrap:wrap}}
.smeta a{{color:var(--blue);text-decoration:none;font-weight:600}}
.smeta a:hover{{color:var(--orange)}}
.stars{{color:#C98A1B;font-weight:800;font-family:'Tajawal'}}
.saddr{{font-size:12px;color:var(--ink3);margin-top:5px}}
.skpis{{display:grid;grid-template-columns:repeat(6,1fr);gap:11px;margin-bottom:16px}}
@media(max-width:1000px){{.skpis{{grid-template-columns:repeat(3,1fr)}}}}
@media(max-width:620px){{.skpis{{grid-template-columns:repeat(2,1fr)}}}}
.kpi{{background:#FDFCFA;border:1px solid var(--line);border-radius:13px;padding:12px 13px;position:relative;overflow:hidden}}
.kpi::before{{content:"";position:absolute;top:0;right:0;width:3px;height:100%;background:var(--line2)}}
.kpi.hot::before{{background:linear-gradient(var(--gold1),var(--orange))}}
.kpi .kl{{font-size:11.5px;color:var(--ink2);font-weight:500}}
.kpi .kv{{font-family:'Tajawal';font-weight:800;font-size:21px;margin-top:6px;color:var(--ink)}}
.kpi .kv small{{font-size:11px;color:var(--ink2);font-weight:500}}
.kpi.hot .kv{{color:var(--orange)}}
.kpi .kn{{font-size:10.5px;color:var(--ink3);margin-top:3px}}
.card{{background:#FDFCFA;border:1px solid var(--line);border-radius:var(--radius);padding:16px 18px 14px}}
.card .ct{{display:flex;align-items:baseline;justify-content:space-between;gap:10px;margin-bottom:4px}}
.card .ct h3{{font-size:15px;font-weight:700}}
.card .ct .leg{{font-size:11px;color:var(--ink3)}}
.card .cs{{font-size:12.5px;color:var(--ink2);margin-bottom:12px}}
.sig{{margin-bottom:16px}}
.siggrid{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:18px;margin-top:10px}}
@media(max-width:900px){{.siggrid{{grid-template-columns:1fr}}}}
.sglb{{font-size:12px;color:var(--ink2);font-weight:600;margin-bottom:6px}}
.sgnote{{font-size:11px;color:var(--ink3);margin-top:4px}}
.spark{{width:100%;height:auto;display:block}}
.mix .mixbar{{display:flex;height:14px;border-radius:8px;overflow:hidden;background:var(--bar)}}
.mix .mixbar i{{display:block;height:100%}}
.mix .mixleg{{display:flex;gap:12px;font-size:11px;color:var(--ink2);margin-top:6px;flex-wrap:wrap}}
.mix .mixleg b{{display:inline-block;width:9px;height:9px;border-radius:3px;margin-inline-end:4px}}
.agrid{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
@media(max-width:980px){{.agrid{{grid-template-columns:1fr}}}}
.pcard{{display:flex;gap:12px;padding:11px 0;border-bottom:1px dashed var(--line2)}}
.pcard:last-child{{border-bottom:none}}
.pico{{font-size:24px;flex:none;width:40px;height:40px;display:flex;align-items:center;justify-content:center;background:#FDEEE2;border-radius:12px}}
.pname{{font-weight:800;font-family:'Tajawal';font-size:14.5px}}
.pshare{{font-size:10.5px;font-weight:600;color:#B4500F;background:#FDEEE2;padding:2px 8px;border-radius:7px;margin-inline-start:6px}}
.pbody p{{font-size:12.5px;color:var(--ink2);margin:4px 0}}
.pline{{font-size:12px;color:var(--ink2)}}
.pline b{{color:var(--ink)}}
.pline.act b{{color:var(--orange)}}
.swot{{display:grid;grid-template-columns:1fr 1fr;gap:10px}}
@media(max-width:620px){{.swot{{grid-template-columns:1fr}}}}
.sq{{border-radius:12px;padding:12px 14px;border:1px solid var(--line)}}
.sq h4{{font-size:13px;font-weight:800;font-family:'Tajawal';margin-bottom:7px}}
.sq ul{{padding-inline-start:16px;font-size:12px;color:var(--ink2);display:grid;gap:5px}}
.sq.s{{background:#F0F7F2;border-color:#CBE2D3}}.sq.s h4{{color:#22694F}}
.sq.w{{background:#FBF0ED;border-color:#EBCFC7}}.sq.w h4{{color:#A6432E}}
.sq.o{{background:#F0F5FA;border-color:#CBDDEB}}.sq.o h4{{color:#2D5674}}
.sq.t{{background:#F8F3E9;border-color:#E6D9BE}}.sq.t h4{{color:#8A6D2B}}
.pest{{display:grid;gap:10px}}
.pr{{display:flex;gap:12px;align-items:flex-start}}
.pk{{flex:none;width:30px;height:30px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-weight:800;font-family:'Tajawal';color:#fff;font-size:14px}}
.pP{{background:#3E6E8E}}.pE{{background:#F37021}}.pS{{background:#2E8B6F}}.pT{{background:#6E5A8E}}
.pr b{{font-size:13px}}
.pr ul{{padding-inline-start:16px;font-size:12px;color:var(--ink2);display:grid;gap:4px;margin-top:4px}}
.comp .ctbl{{overflow-x:auto;border:1px solid var(--line);border-radius:12px}}
.comp table{{font-size:12.5px}}
.comp td,.comp th{{padding:8px 12px;white-space:normal}}
.dens{{font-size:11.5px;font-weight:800;padding:3px 10px;border-radius:8px}}
.dens.lo{{background:#E9F2EC;color:#22694F}}
.dens.md{{background:#F8F3E9;color:#8A6D2B}}
.dens.hi{{background:#FBF0ED;color:#A6432E}}
.sis{{font-size:12px;color:var(--ink2);margin-top:9px;background:#FDEEE2;border-radius:10px;padding:8px 12px}}
details.apx{{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:16px 20px;margin-top:8px}}
details.apx summary{{cursor:pointer;font-weight:700;font-size:14px}}
details.apx .tscroll{{overflow-x:auto;margin-top:12px}}
footer{{border-top:1px solid var(--line);margin-top:30px;padding:22px 0 34px;font-size:12px;color:var(--ink3)}}
footer b{{color:var(--ink2)}}
.hidden{{display:none!important}}
</style>
</head>
<body>
<header>
  <div class="wrap">
    <div class="brand">
      <div class="mark"><div class="ar">محطات <b>درب</b></div><div class="en">DARB STATIONS</div></div>
      <div class="hd-title"><h1>تحليل المواقع والمبيعات — لكل محطة: PEST · بيرسونا · SWOT · المنافسون ≤ 5 كم</h1>
      <p>النصف الأول 2026 · {len(ORDER)} محطة مشمولة بالبيانات · أُعدّ آليًا من بيانات المبيعات وخرائط جوجل</p></div>
    </div>
    <div class="netkpis">
      <div><div class="v">{len(ORDER)}</div><div class="l">محطة مشمولة بالتحليل (من أصل {len(XL)})</div></div>
      <div><div class="v">{tot_rev/1e6:,.1f} <small>مليون ر.س</small></div><div class="l">إيراد الفترة</div></div>
      <div><div class="v">{tot_vis/1e6:,.2f} <small>مليون</small></div><div class="l">زيارة</div></div>
      <div><div class="v">{avg_rt:.2f} ★</div><div class="l">متوسط تقييم درب على جوجل</div></div>
      <div><div class="v">{n0(ncomp) if ncomp is not None else '—'}</div><div class="l">محطة منافسة فريدة مرصودة ضمن نطاقات 5 كم</div></div>
    </div>
  </div>
</header>
<div class="stationbar"><div class="chips" id="chips">{chips}
  <div class="search"><input id="q" type="search" placeholder="ابحث باسم المحطة أو الكود…" aria-label="بحث"></div>
</div></div>
<main class="wrap">
  <div class="sec-h"><h2>نظرة عامة — ترتيب المحطات</h2><span>اضغط على أي صف للانتقال إلى تحليل المحطة</span></div>
  <div class="ntable"><div class="tscroll"><table id="ovt">
    <thead><tr><th>#</th><th>المحطة</th><th>المدينة</th><th>التصنيف</th><th>إيراد يومي (ر.س)</th><th>الفاتورة (ر.س)</th><th>نمو Q2</th><th>منافسون ≤5كم</th><th>جوجل ★</th></tr></thead>
    <tbody>{ov_rows}</tbody></table></div></div>
  {''.join(station_section(a) for a in ORDER)}
  <div class="sec-h"><h2>محطات خارج نطاق هذا التحليل</h2><span>{len(nosales)} محطة لا تتوفر لها بيانات مبيعات في لوحة التحليل</span></div>
  <details class="apx"><summary>عرض القائمة — {esc(app_sum)}</summary>
    <div class="tscroll"><table><thead><tr><th>الكود</th><th>المدينة</th><th>المحطة</th><th>النوع</th><th>الموقع</th></tr></thead><tbody>{app_rows}</tbody></table></div>
  </details>
  <footer>
    <b>المنهجية والمصادر:</b> بيانات المبيعات والزيارات من لوحة «درب · تحليل المبيعات والتسويق» (يناير–يونيو 2026، آخر تحديث {esc(GEN)})؛
    مواقع المحطات من ملف Station_Data.xlsx (روابط خرائط جوجل المعتمدة)؛ رصد المنافسين والتقييمات من خرائط جوجل (بحث «محطة وقود» ضمن دائرة نصف قطرها 5 كم حول إحداثيات كل محطة، يوليو 2026) —
    القوائم تشمل المحطات المدرجة في خرائط جوجل وقد لا تشمل محطات غير مسجلة؛ المسافات دائرية مباشرة (خط مستقيم).
    (*) الدوائر التي أعاد المسح الآلي فيها نتائج شحيحة معلَّمة بنجمة في جدول النظرة العامة وبتنبيه في بطاقة المنافسين — لا يُبنى على عددها استنتاج تنافسي ويُوصى بتدقيقها يدويًا.
    تحليلات PEST/SWOT/البيرسونا مولّدة قاعديًا من مؤشرات كل محطة (مزيج الوقود، الأوقات، الدفع، النمو، الكثافة التنافسية) وتُقرأ كمسودة عمل تسويقية لا كدراسة سوق ميدانية.
  </footer>
</main>
<script>
const chips=document.querySelectorAll('.chip');const q=document.getElementById('q');
let region='*';
function apply(){{
  const t=(q.value||'').trim();
  document.querySelectorAll('section.station').forEach(s=>{{
    const okR=region==='*'||s.dataset.region===region;
    const okQ=!t||s.dataset.name.includes(t);
    s.classList.toggle('hidden',!(okR&&okQ));
  }});
  document.querySelectorAll('#ovt tbody tr').forEach(r=>{{
    const okR=region==='*'||r.dataset.region===region;
    const okQ=!t||r.textContent.includes(t);
    r.classList.toggle('hidden',!(okR&&okQ));
  }});
}}
chips.forEach(c=>c.addEventListener('click',()=>{{chips.forEach(x=>x.classList.remove('on'));c.classList.add('on');region=c.dataset.r;apply();}}));
q.addEventListener('input',apply);
</script>
</body>
</html>'''
open('location-analysis.html','w', encoding='utf-8').write(html_out)
print('written', len(html_out), 'bytes')
