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
THIN = {'HA043','JA053','JA060','JA348','MD009','MK004','MK014','MK028','MK046','MK054','MK100','NJ219','QS055','RY042','RY075'}
DIR8 = ['شمال','شمال شرق','شرق','جنوب شرق','جنوب','جنوب غرب','غرب','شمال غرب']

rows, seen = [], set()
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
    if r['title']=='محطة وقود' and r['rating']==3.5 and r['reviews']==2: return False
    return True

def bearing_octant(lat0,lng0,lat,lng):
    dy = lat-lat0
    dx = (lng-lng0)*math.cos(math.radians(lat0))
    ang = (math.degrees(math.atan2(dx,dy)) + 360) % 360
    return DIR8[int(((ang+22.5)%360)//45)]

comp, uniq = {}, set()
for code, v in coords.items():
    near, sisters = [], []
    for r in rows:
        d = dist(v['lat'], v['lng'], r['lat'], r['lng'])
        if d > 5000 or d <= 60: continue
        e = dict(r, dist=int(round(d)))
        if is_darb(r['title']):
            sisters.append(e); continue
        if not is_fuel(r): continue
        near.append(e)
        uniq.add((round(r['lat'],6), round(r['lng'],6), r['title']))
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
    bands = [sum(1 for x in near if x['dist']<=1000),
             sum(1 for x in near if 1000<x['dist']<=3000),
             sum(1 for x in near if 3000<x['dist']<=5000)]
    dirs = {}
    for x in near:
        o = bearing_octant(v['lat'], v['lng'], x['lat'], x['lng'])
        dirs[o] = dirs.get(o,0)+1
    dirmax = max(dirs.items(), key=lambda kv: kv[1])[0] if dirs else None
    comp[code] = dict(
        n=len(near),
        top=[{k: x[k] for k in ('title','dist','rating','reviews','lat','lng')} for x in near],
        nearest={k: near[0][k] for k in ('title','dist')} if near else None,
        avg_rating=round(statistics.mean(rated),2) if rated else None,
        weak_share=round(len(weak)/len(near),2) if near else 0,
        strong=brands[:4],
        sisters=[{k: s[k] for k in ('title','dist','lat','lng')} for s in sorted(sisters,key=lambda x:x['dist'])],
        bands=bands, dirmax=dirmax, thin=(code in THIN),
    )
comp['_meta'] = {'unique_competitors': len(uniq)}
json.dump(comp, open('competitors.json','w'), ensure_ascii=False, indent=1)
print('unique competitors:', len(uniq))
print('MK023 bands:', comp['MK023']['bands'], 'dir:', comp['MK023']['dirmax'], '| top n:', len(comp['MK023']['top']))
