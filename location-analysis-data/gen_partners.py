# -*- coding: utf-8 -*-
import json
DATA = json.load(open('data.json'))
BY = {s['code']: s for s in DATA['stations']}
M = json.load(open('metrics.json'))
U = json.load(open('units_data.json'))
P, FR = U['p'], U['fr']
FIVE = {'MK002','MK007','MK017','MK019','MK023'}
PERIODS = [('بعد منتصف الليل','00:00 – 05:00',range(0,5),'#55565A'),
           ('فجر وشروق','05:00 – 08:00',range(5,8),'#C98A1B'),
           ('ضحى','08:00 – 11:00',range(8,11),'#3E6E8E'),
           ('ظهر','11:00 – 15:00',range(11,15),'#6E5A8E'),
           ('عصر ومغرب','15:00 – 20:00',range(15,20),'#F5831F'),
           ('ليل','20:00 – 24:00',range(20,24),'#2E8B6F')]
CATL = {'rest':'مطاعم','cafe':'مقاهٍ','car':'خدمات سيارات','mkt':'سوبرماركت','oth':'أخرى'}
SERVE = {0:['cafe','mkt'],1:['cafe','rest'],2:['cafe','car'],3:['rest','mkt'],4:['rest','cafe','mkt'],5:['rest','cafe']}
def n0(x): return f'{x:,.0f}'
HR12 = lambda h: (f'{h%12 or 12}{"ص" if h<12 else "م"}')

def gen(code):
    st = BY[code]; o = st['overall']; m = M[code]
    nd = o['ndays'] or 1
    hv = {h['h']: h['vis'] for h in o['hours']}; hr = {h['h']: h['rev'] for h in o['hours']}
    lit_ratio = (o.get('volume') or 0)/o['revenue'] if o['revenue'] else 0
    d = P.get(code, {'bio':'','cats':{},'units':{}})
    cats = {k: v for k, v in d['cats'].items() if v}
    partners = [(nm, k) for k in ('rest','cafe','car','mkt','oth') for nm in cats.get(k, [])]
    np_core = sum(len(cats.get(k, [])) for k in ('rest','cafe','car','mkt'))
    np_all = len(partners)
    per = []
    for i, (nm, hrs, rng, col) in enumerate(PERIODS):
        cars = sum(hv.get(h,0) for h in rng)/nd
        rev = sum(hr.get(h,0) for h in rng)/nd
        per.append(dict(i=i, nm=nm, hrs=hrs, col=col, cars=cars, rev=rev, secs=len(list(rng))*3600))
    tot = sum(p['cars'] for p in per) or 1
    for p in per: p['sh'] = p['cars']/tot
    order = sorted(per, key=lambda p:-p['cars'])
    for r, p in enumerate(order): p['rank'] = r+1
    best, worst = order[0], order[-1]
    cars_day = tot; people = cars_day*2
    brk = ' · '.join(f'{CATL[k]} {len(cats[k])}' for k in ('rest','cafe','car','mkt') if k in cats) or 'لا أسماء مسجلة في الملف'
    kpis = f'''<div class="skpis" style="grid-template-columns:repeat(6,1fr)"><div class="kpi hot"><div class="kl">الشركاء داخل المحطة</div><div class="kv">{np_core if np_core else '—'}</div><div class="kn">{brk}</div></div><div class="kpi"><div class="kl">سيارات يوميًا</div><div class="kv">{n0(cars_day)}</div><div class="kn">تمرّ أمام الوحدات على مدار اليوم</div></div><div class="kpi"><div class="kl">أشخاص يوميًا</div><div class="kv">{n0(people)}</div><div class="kn">بفرض متحفّظ: راكبان لكل سيارة</div></div><div class="kpi"><div class="kl">أقوى فترة</div><div class="kv" style="font-size:17px">{best['nm']}</div><div class="kn">{n0(best['cars'])} سيارة/يوم · {best['sh']*100:.0f}٪ من اليوم</div></div><div class="kpi"><div class="kl">أضعف فترة</div><div class="kv" style="font-size:17px">{worst['nm']}</div><div class="kn">{n0(worst['cars'])} سيارة/يوم · {worst['sh']*100:.0f}٪ من اليوم</div></div><div class="kpi"><div class="kl">سيارات لكل شريك</div><div class="kv">{n0(cars_day/np_core) if np_core else '—'}</div><div class="kn">{'كل شريك أمامه هذا التدفق يوميًا' if np_core else 'بانتظار تسجيل الشركاء'}</div></div></div>'''
    mx = max(hv.values()) or 1
    bars = []
    for h in range(24):
        v = hv.get(h,0); bh = max(3, v/mx*150); x = 18 + h*44.9
        bars.append(f'<g><rect x="{x:.1f}" y="{172-bh:.1f}" width="35.6" height="{bh:.1f}" rx="5" fill="#55565A" opacity="0.72"><title>{HR12(h)} — {n0(v/nd)} سيارة/يوم</title></rect></g>')
        if h % 2 == 0: bars.append(f'<text x="{x+17.8:.1f}" y="192" font-size="12" text-anchor="middle" fill="var(--ink2)">{HR12(h)}</text>')
    chart = f'''<div class="chartbox"><h3>حركة اليوم الكامل موزّعة على الفترات</h3><div class="cs">أعمدة الساعات (سيارة/يوم) من بيانات لوحة المبيعات — والفترات الست أدناه تجمع هذه الساعات</div><svg viewBox="0 0 1100 200" class="spark" role="img" aria-label="حركة اليوم الكامل">{''.join(bars)}</svg></div>'''
    rows = ''
    for p in per:
        nserve = sum(len(cats.get(k, [])) for k in SERVE[p['i']])
        rows += f'''<tr><td><b>{p['nm']}</b></td><td>{p['hrs']}</td><td>{n0(p['cars'])}</td><td>{p['sh']*100:.1f}٪</td><td>{n0(p['cars']*2)}</td><td>{n0(p['secs']/p['cars']) if p['cars'] else '—'} ثانية</td><td>{n0(p['rev'])} ر.س</td><td>{n0(p['rev']*lit_ratio)} لتر</td><td>{nserve if np_all else '—'}</td></tr>'''
    side = f'''<div class="sec-h"><h2>الفترات الست جنبًا إلى جنب</h2><span>محسوبة من متوسطات {nd} يومًا</span></div><div class="ntable"><div class="tscroll"><table><thead><tr><th>الفترة</th><th>الساعات</th><th>سيارات/يوم</th><th>٪ من اليوم</th><th>أشخاص/يوم</th><th>سيارة كل</th><th>إيراد وقود تقديري/يوم</th><th>لترات تقديرية/يوم</th><th>وحدات تخدم الفترة</th></tr></thead><tbody>{rows}</tbody></table></div></div>'''
    cards = []
    for p in per:
        serve_names = [(nm, k) for k in SERVE[p['i']] for nm in cats.get(k, [])]
        ppl = p['cars']*2
        cap_rows = ''
        for r_ in (0.01, 0.03, 0.05, 0.08):
            cd = ppl*r_
            cap_rows += f'<tr><td><b>{r_*100:.0f}٪</b></td><td>{cd:,.0f}</td><td>{cd*7:,.0f}</td><td>{cd*20*30:,.0f} ر.س</td></tr>'
        fit = (f'<div class="pfit"><b>الوحدات التي تخدم هذه الفترة ({len(serve_names)}):</b> ' + ''.join(f'<span class="ptag">{nm}</span>' for nm, _ in serve_names) + '</div>') if serve_names else \
              ('<div class="pfit"><b>الوحدات:</b> ' + (' · '.join(f'{lbl} {v}' for lbl, v in [('كشك',d['units'].get('kiosk',0)),('محل',d['units'].get('shop',0)),('درايف ثرو',d['units'].get('drive',0)),('صراف',d['units'].get('atm',0))] if v) or 'لا أسماء شركاء مسجلة في الملف بعد') + '</div>')
        cards.append(f'''<div class="pcard2" style="--pc:{p['col']}"><div class="ph"><span class="pdot"></span><h4>{p['nm']}</h4><span class="phrs">{p['hrs']}</span><span class="prank">#{p['rank']} في اليوم</span></div><div class="pnums"><div><b>{n0(p['cars'])}</b><span>سيارة/يوم</span></div><div><b>{n0(p['cars']*2)}</b><span>شخص/يوم</span></div><div><b>{p['sh']*100:.1f}٪</b><span>من حركة اليوم</span></div><div><b>{n0(p['rev'])}</b><span>ر.س إيراد وقود تقديري</span></div></div><div class="pread">الفترة رقم {p['rank']} من 6 — {p['sh']*100:.0f}٪ من الحركة{f" · {len(serve_names)} وحدة تخدم هذه الفترة بمعدل {n0(p['cars']/len(serve_names))} سيارة لكل وحدة" if serve_names else ''}.</div>{fit}<div class="pcap"><div class="pcaph">لو التقطت الوحدات نسبة من هذه الفترة</div><table class="captbl"><thead><tr><th>معدل الالتقاط</th><th>عملاء/يوم</th><th>عملاء/أسبوع</th><th>مبيعات شهرية عند 20 ر.س</th></tr></thead><tbody>{cap_rows}</tbody></table></div></div>''')
    grid = f'''<div class="sec-h"><h2>كل فترة على حدة</h2><span>مؤشرات كل فترة وقدرة وحداتها على الالتقاط</span></div><div class="pgrid">{''.join(cards)}</div>'''
    ccards = ''
    for k in ('rest','cafe','car','mkt','oth'):
        if k not in cats: continue
        tags = ''.join(f'<span class="ptag">{nm}</span>' for nm in cats[k])
        ccards += f'<div class="card"><div class="ct"><h3>{CATL[k]}</h3><div class="leg">{len(cats[k])} وحدة</div></div><div class="ptags">{tags}</div></div>'
    if not ccards:
        un = d['units']
        ccards = '<div class="card"><div class="ct"><h3>الوحدات التأجيرية</h3></div><div class="cs">' + (' · '.join(f'{lbl}: {v}' for lbl, v in [('كشك',un.get('kiosk',0)),('محل',un.get('shop',0)),('درايف ثرو',un.get('drive',0)),('صراف',un.get('atm',0))] if v) or 'لا بيانات وحدات') + ' — أسماء المشغّلين غير مسجلة في الملف بعد.</div></div>'
    catsec = f'''<div class="sec-h"><h2>الشركاء داخل المحطة</h2><span>{np_all if np_all else '—'} وحدة حسب ملف Darb Units — {M[code]['name']}</span></div><div class="agrid">{ccards}</div>'''
    fr = FR.get(code)
    if fr:
        left = f" · المتبقي: {fr['left']}" if fr['left'] else ''
        frline = f" · وحدات الامتياز: {fr['units']:.0f} (مؤجَّر {fr['leased']:.0f} · شاغر {fr['vacant']:.0f} · إشغال {fr['occ']*100:.0f}٪{left})"
    else:
        frline = ''
    bio = f"<b>نبذة الموقع:</b> {d['bio']} · " if d['bio'] else ''
    note = f'''<div class="dnote">🧩 {bio}حركة الفترات محسوبة من بيانات ساعات لوحة المبيعات ({nd} يومًا)؛ أسماء الشركاء والوحدات من ملف Darb Units{frline}. تقديرات الالتقاط استرشادية بنفس منهجية النموذج المعتمد (راكبان/سيارة · سلة 20 ر.س).</div>'''
    return kpis + chart + side + grid + catsec + note, np_all

ops = json.load(open('ops_content.json'))
counts = {}
made = []
for code in sorted(set(P) & set(M)):
    if code in FIVE: continue
    html, np_all = gen(code)
    ops.setdefault(code, {})['partners'] = html
    if np_all: counts[code] = np_all
    made.append(code)
json.dump(ops, open('ops_content.json','w'), ensure_ascii=False)
json.dump(counts, open('ops_counts_extra.json','w'), ensure_ascii=False)
print('partners generated for', len(made), 'stations; with badges:', len(counts))
