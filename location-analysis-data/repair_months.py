# -*- coding: utf-8 -*-
import json

d = json.load(open('data.json'))
DD = {s['code']: s for s in d['stations']}
met = json.load(open('metrics.json'))
net = json.load(open('net_sep.json'))
ns = {s['code']: s for s in (net.get('stations') or net.get('st'))}

# ---- 0. validate metric formulas against current stored metrics ----
def shares(ov):
    hv = [h['vis'] for h in ov['hours']] if ov.get('hours') else [0]*24
    tot = sum(hv) or 1
    return (sum(hv[16:24])/tot, sum(hv[0:5])/tot, sum(hv[5:12])/tot, sum(hv[12:16])/tot)

bad = 0
for c, m in met.items():
    st = DD.get(c)
    if not st: continue
    ov = st['overall']
    if abs(m['revenue'] - ov['revenue']) > 1: bad += 1; print('rev mismatch', c)
    if m['ndays'] and abs(m['daily_rev'] - ov['revenue']/ov['ndays']) > 1: bad += 1; print('drev mismatch', c, m['daily_rev'], ov['revenue']/ov['ndays'])
    ev, ni, mo_, mi = shares(ov)
    if m.get('evening') is not None and abs(m['evening'] - ev) > 0.002: bad += 1; print('evening mismatch', c, m['evening'], round(ev,3))
# rank check
order = sorted((x for x in met.values() if x.get('daily_rev')), key=lambda x: -x['daily_rev'])
rk, prev, cur = {}, None, 0
for x in order:
    cur += 1 if x['daily_rev'] != prev else 0
    # dense rank
for i, x in enumerate(order):
    rk[x['code']] = i + 1
mism = [c for c, r in rk.items() if met[c].get('rank_drev') != r]
print('formula check: bad =', bad, '| rank_drev mismatches:', mism[:5], len(mism))

# ---- 1. repair ----
REPLACE_OK = {('JA060','2026-07'), ('MK001','2026-07'), ('MK016','2026-07'),
              ('MK031','2026-07'), ('MK035','2026-07'), ('MK047','2026-07')}
log_add, log_repl, touched = [], [], set()
for c, n in ns.items():
    st = DD.get(c)
    if not st: continue
    hrMon = n.get('hrMon') or []
    for i, slot in enumerate(n['months'][:8]):
        if not slot or not slot.get('amt'): continue
        mo = f"2026-{i+1:02d}"
        hrm = hrMon[i] if i < len(hrMon) and hrMon[i] else None
        ours = st['monthly'].get(mo)
        amt, tx = slot['amt'], slot['tx']
        vol, days = slot.get('vol') or 0, slot.get('days') or 0
        if not ours:
            ent = dict(revenue=amt, visits=tx, volume=vol, ndays=days,
                       avg_invoice=round(amt/tx, 2) if tx else None,
                       avg_liters=round(vol/tx, 2) if tx else None,
                       daily_avg_rev=round(amt/days, 2) if days else None,
                       daily_avg_vis=round(tx/days, 1) if days else None,
                       vol_partial=False)
            if hrm:
                pv = max(range(24), key=lambda h: hrm[h])
                ent.update(peak_vis_hour=pv, peak_vis_val=hrm[pv], peak_rev_hour=pv, peak_rev_val=0)
            st['monthly'][mo] = ent
            ov = st['overall']
            ov['revenue'] += amt; ov['visits'] += tx; ov['volume'] += vol; ov['ndays'] += days
            if hrm:
                for h in range(24): ov['hours'][h]['vis'] += hrm[h]
            log_add.append((c, mo, round(amt))); touched.add(c)
        elif (c, mo) in REPLACE_OK:
            old = (ours['revenue'], ours['visits'], ours.get('volume') or 0, ours.get('ndays') or 0)
            old_h = [x.get('vis', 0) for x in ours.get('hours', [])] if ours.get('hours') else None
            ours.update(revenue=amt, visits=tx, volume=vol, ndays=days,
                        avg_invoice=round(amt/tx, 2) if tx else ours.get('avg_invoice'),
                        avg_liters=round(vol/tx, 2) if tx else ours.get('avg_liters'),
                        daily_avg_rev=round(amt/days, 2) if days else None,
                        daily_avg_vis=round(tx/days, 1) if days else None)
            ov = st['overall']
            ov['revenue'] += amt - old[0]; ov['visits'] += tx - old[1]
            ov['volume'] += vol - old[2]; ov['ndays'] += days - old[3]
            if hrm and old_h and len(old_h) == 24:
                for h in range(24): ov['hours'][h]['vis'] += hrm[h] - old_h[h]
            log_repl.append((c, mo, round(old[0]), round(amt))); touched.add(c)

# ---- 2. refresh overall deriveds + metrics for touched ----
for c in sorted(touched):
    st = DD[c]; ov = st['overall']; m = met[c]
    ov['avg_invoice'] = round(ov['revenue'] / ov['visits']) if ov['visits'] else None
    ov['avg_liters'] = round(ov['volume'] / ov['visits']) if ov['visits'] else None
    ov['daily_avg_rev'] = round(ov['revenue'] / ov['ndays']) if ov['ndays'] else None
    ov['daily_avg_vis'] = round(ov['visits'] / ov['ndays']) if ov['ndays'] else None
    if ov.get('hours'):
        pv = max(ov['hours'], key=lambda h: h['vis']); pr = max(ov['hours'], key=lambda h: h['rev'])
        ov['peak_vis_hour'], ov['peak_vis_val'] = pv['h'], round(pv['vis'])
        ov['peak_rev_hour'], ov['peak_rev_val'] = pr['h'], round(pr['rev'])
    months = sorted(st['monthly'])
    m['months'] = months; m['nmonths'] = len(months)
    m['revenue'] = round(ov['revenue'], 2); m['visits'] = ov['visits']
    m['volume'] = round(ov['volume'], 2); m['ndays'] = ov['ndays']
    m['avg_invoice'] = round(ov['revenue'] / ov['visits'], 2) if ov['visits'] else None
    m['avg_liters'] = round(ov['volume'] / ov['visits'], 2) if ov['visits'] else None
    m['daily_rev'] = round(ov['revenue'] / ov['ndays'], 2) if ov['ndays'] else None
    m['daily_vis'] = round(ov['visits'] / ov['ndays'], 1) if ov['ndays'] else None
    ev, ni, mo_, mi = shares(ov)
    m['evening'], m['night'], m['morning'], m['midday'] = round(ev,3), round(ni,3), round(mo_,3), round(mi,3)
    if ov.get('hours'):
        m['peak_hour'] = ov['peak_vis_hour']; m['peak_rev_hour'] = ov['peak_rev_hour']

# ---- 3. dense re-rank everyone ----
order = sorted((x for x in met.values() if x.get('daily_rev')), key=lambda x: -x['daily_rev'])
for i, x in enumerate(order): x['rank_drev'] = i + 1
order2 = sorted((x for x in met.values() if x.get('avg_invoice')), key=lambda x: -x['avg_invoice'])
for i, x in enumerate(order2): x['rank_inv'] = i + 1

json.dump(d, open('data.json', 'w'), ensure_ascii=False)
json.dump(met, open('metrics.json', 'w'), ensure_ascii=False, indent=1)
print('added months:', len(log_add), log_add)
print('replaced months:', len(log_repl), log_repl)
net_rev = sum(x['revenue'] for x in met.values())
print('network revenue now:', round(net_rev))
print('MK001 now:', met['MK001']['months'], '| drev', met['MK001']['daily_rev'], '| rank', met['MK001']['rank_drev'])
