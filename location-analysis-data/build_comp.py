# -*- coding: utf-8 -*-
import json, math, re, statistics
coords = json.load(open('coords.json'))
R = 6371000.0
def dist(a,b,c,d):
    p1,p2 = math.radians(a), math.radians(c)
    dp,dl = math.radians(c-a), math.radians(d-b)
    x = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(x))

EXCL = re.compile(r'مغسل|مغاسل|غسيل|لغسيل|wash|واش|حافلات|موقف|مسجد|مستودع|الكعكي|لزينة السيارات|الضيافة|وميزان', re.I)
rows = []
seen = set()
for ln in open('competitors_raw.txt', encoding='utf-8'):
    ln = ln.rstrip('\n')
    if not ln.strip(): continue
    lat,lng,score,rev,title = ln.split('|',4)
    lat,lng = float(lat), float(lng)
    key = (round(lat,6), round(lng,6), title)
    if key in seen: continue
    seen.add(key)
    rows.append(dict(lat=lat,lng=lng,rating=float(score) if score else None,
                     reviews=int(rev) if rev else 0, title=title.strip()))
print('unique places:', len(rows))

def is_darb(t): return 'درب' in t
def is_fuel(r):
    if EXCL.search(r['title']): return False
    if r['title']=='محطة وقود' and r['rating']==3.5 and r['reviews']==2: return False  # ورشة الجعرانة
    return True

comp = {}
for code, v in coords.items():
    near = []
    sisters = []
    for r in rows:
        d = dist(v['lat'], v['lng'], r['lat'], r['lng'])
        if d > 5000: continue
        if d <= 60: continue  # نقطة المحطة نفسها في جوجل (قد تكون بلا كلمة «درب»)
        e = dict(r, dist=int(round(d)))
        if is_darb(r['title']):
            if d > 120:  # own pin ~0m
                sisters.append(e)
            continue
        if not is_fuel(r): continue
        near.append(e)
    near.sort(key=lambda x: x['dist'])
    rated = [x['rating'] for x in near if x['rating'] and x['reviews'] >= 5]
    weak = [x for x in near if x['rating'] and x['rating'] < 4.0 and x['reviews'] >= 5]
    brands = []
    for x in near:
        t = x['title']
        for b,label in [('aldrees','الدريس'),('الدريس','الدريس'),('sasco','ساسكو'),('ساسكو','ساسكو'),
                        ('بترومين','بترومين'),('نفط','نفط'),('لتر','لتر'),('بترولي','بترولي'),
                        ('adnoc','أدنوك'),('petromin','بترومين'),('naft','نفط'),('جي اويل','جي أويل')]:
            if b in t.lower() and label not in brands:
                brands.append(label)
    comp[code] = dict(
        n=len(near),
        top=[{k: x[k] for k in ('title','dist','rating','reviews')} for x in near[:10]],
        nearest={k: near[0][k] for k in ('title','dist')} if near else None,
        avg_rating=round(statistics.mean(rated),2) if rated else None,
        weak_share=round(len(weak)/len(near),2) if near else 0,
        strong=brands[:4],
        sisters=[{k: s[k] for k in ('title','dist')} for s in sorted(sisters,key=lambda x:x['dist'])],
    )
json.dump(comp, open('competitors.json','w'), ensure_ascii=False, indent=1)
thin = [(c, comp[c]['n']) for c in comp if comp[c]['n'] <= 1]
print('thin coverage (<=1):', sorted(thin))
for c in sorted(comp):
    print(c, coords[c]['gcity'], '| n=', comp[c]['n'], '| nearest:', comp[c]['nearest']['title'] if comp[c]['nearest'] else '—',
          comp[c]['nearest']['dist'] if comp[c]['nearest'] else '', '| sisters:', len(comp[c]['sisters']))
