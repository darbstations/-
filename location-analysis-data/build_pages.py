# -*- coding: utf-8 -*-
"""Build hub (location-analysis.html) + one standalone page per station (stations/CODE.html)."""
import json, html, os, statistics

A = json.load(open('analysis.json'))
try:
    ACT = json.load(open('actual_daily.json'))
except FileNotFoundError:
    ACT = {}
try:
    OPS = json.load(open('ops_content.json'))
except FileNotFoundError:
    OPS = {}
OPS_COUNTS = {'MK007': {'cs':117,'partners':47,'external':10,'plan':18}, 'MK017': {'cs':16,'partners':9,'external':8,'plan':18}, 'MK002': {'cs':7,'partners':16,'external':4,'plan':18}, 'MK023': {'cs':14,'partners':7,'external':9,'plan':18}, 'MK019': {'cs':11,'partners':7,'external':7,'plan':18}}
try:
    _extra = json.load(open('ops_counts_extra.json'))
    for _c, _n in _extra.items():
        OPS_COUNTS.setdefault(_c, {})['partners'] = _n
except FileNotFoundError:
    pass
OPS_TABS = [('targets','المستهدفات'),('cs','استفسارات العملاء'),('partners','الشركاء عبر اليوم'),('external','الشركاء الخارجيون'),('plan','الخطة التشغيلية')]
try:
    OPS_CSS = open('ops_clean.css', encoding='utf-8').read()
except FileNotFoundError:
    OPS_CSS = ''
try:
    OPS_TPL = json.load(open('ops_template.json'))
except FileNotFoundError:
    OPS_TPL = {}
def ops_content(code, k):
    v = (OPS.get(code) or {}).get(k)
    return v if v else OPS_TPL.get(k, '')
try:
    ECO = json.load(open('ecosys.json'))  # {code: {rentals:[{title,dist,rating,reviews,lat,lng}], hajj:[...]}}
except FileNotFoundError:
    ECO = {}
DATA = json.load(open('data.json'))
XL = json.load(open('stations.json'))
COMP = json.load(open('competitors.json'))
BYCODE = {s['code']: s for s in DATA['stations']}
os.makedirs('stations', exist_ok=True)

def esc(x): return html.escape(str(x), quote=True)
def n0(x): return f"{x:,.0f}"
def sar(x):
    if x >= 1e6: return f"{x/1e6:,.1f} <small>مليون ر.س</small>"
    return f"{x/1e3:,.0f} <small>ألف ر.س</small>"
def pct(x): return f"{x*100:.0f}٪"
def hr_ar(h):
    h12 = h % 12 or 12
    return f"{h12}{'ص' if h < 12 else 'م'}"

ORDER = sorted(A.values(), key=lambda a: -a['metrics']['daily_rev'])
CODES = [a['metrics']['code'] for a in ORDER]
REGIONS = []
for a in ORDER:
    r = a['metrics']['region']
    if r not in REGIONS: REGIONS.append(r)

CSS = """
:root{--orange:#F5831F;--gold1:#F7A94B;--bgray:#55565A;--ink:#3D3D3D;--ink2:#6E6A64;--ink3:#9B968E;--bg:#F7F4EF;--card:#FFFFFF;
--line:#ECE6DD;--line2:#E3DCD1;--bar:#E0D9CD;--good:#2E8B6F;--bad:#C0503A;--blue:#3E6E8E;
--shadow:0 1px 2px rgba(61,61,61,.04),0 8px 24px rgba(61,61,61,.06);--radius:16px}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{font-family:'DIN Next Arabic','IBM Plex Sans Arabic',system-ui,sans-serif;background:var(--bg);color:var(--ink);line-height:1.6;font-size:15px}
::selection{background:var(--orange);color:#fff}
.wrap{max-width:1240px;margin:0 auto;padding:0 22px}
header{background:var(--bgray);color:#fff;padding:26px 0 22px;border-bottom:4px solid var(--orange)}
.darblogo{height:74px;width:auto;display:block;filter:drop-shadow(0 4px 14px rgba(0,0,0,.25))}
.brand{display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap}
.mark .ar{font-weight:800;font-size:28px;letter-spacing:-.5px}
.mark .ar b{color:var(--orange)}
.mark .en{font-size:10.5px;letter-spacing:3.5px;color:#b9b3aa;margin-top:3px}
.mark a{color:inherit;text-decoration:none}
.hd-title{text-align:left}
.hd-title h1{font-size:17px;font-weight:600}
.hd-title p{font-size:12px;color:#D8D9DB;margin-top:3px}
.netkpis{display:grid;grid-template-columns:repeat(5,1fr);gap:1px;background:rgba(255,255,255,.14);border-radius:14px;overflow:hidden;margin-top:22px}
.netkpis>div{background:#4A4B4F;padding:13px 16px}
.netkpis .v{font-weight:800;font-size:21px;color:var(--gold1)}
.netkpis .v small{font-size:11px;color:#b9b3aa;font-weight:500}
.netkpis .l{font-size:11.5px;color:#CFD0D2;margin-top:2px}
@media(max-width:900px){.netkpis{grid-template-columns:repeat(2,1fr)}}
.stationbar{background:var(--card);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:40;box-shadow:0 2px 10px rgba(61,61,61,.05)}
.chips{display:flex;gap:7px;overflow-x:auto;padding:11px 22px;max-width:1240px;margin:0 auto;scrollbar-width:thin;align-items:center}
.chip{flex:none;border:1px solid var(--line2);background:#fff;border-radius:11px;padding:7px 13px;cursor:pointer;font-family:inherit;font-size:13px;color:var(--ink2);transition:.14s;display:flex;gap:7px;align-items:center;text-decoration:none}
.chip:hover{border-color:var(--orange);color:var(--ink)}
.chip.on{background:var(--bgray);border-color:var(--bgray);color:#fff}
.chip .code{font-size:10.5px;color:var(--ink3);font-family:'Tajawal'}
.chip.on .code{color:var(--gold1)}
.search{flex:none;margin-inline-start:auto}
.search input{border:1px solid var(--line2);border-radius:11px;padding:8px 13px;font-family:inherit;font-size:13px;width:220px;background:#fff;color:var(--ink)}
.search input:focus{outline:2px solid var(--orange);border-color:var(--orange)}
main{padding:26px 0 40px}
.sec-h{display:flex;align-items:baseline;gap:10px;margin:8px 0 14px}
.sec-h h2{font-size:19px;font-weight:800;font-family:'Tajawal'}
.sec-h span{font-size:12px;color:var(--ink3)}
.ntable{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;box-shadow:var(--shadow);margin-bottom:34px}
.ntable .tscroll{overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:13.5px}
th{text-align:right;font-size:12px;color:var(--ink2);font-weight:600;padding:11px 14px;border-bottom:1px solid var(--line);background:#FBF9F5;white-space:nowrap}
td{padding:10px 14px;border-bottom:1px solid var(--line);white-space:nowrap}
tbody tr{transition:.12s}
tbody tr:hover{background:#FBF6EF}
td a.stlink{color:var(--ink);text-decoration:none;font-weight:700}
td a.stlink:hover{color:var(--orange)}
.tcode{font-size:11px;color:var(--ink3);letter-spacing:.4px}
.up{color:var(--good);font-weight:700}.dn{color:var(--bad);font-weight:700}
.station{background:var(--card);border:1px solid var(--line);border-radius:20px;box-shadow:var(--shadow);padding:22px 22px 18px;margin-bottom:26px}
.shead{border-bottom:1px dashed var(--line2);padding-bottom:14px;margin-bottom:16px}
.stitle{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.stitle h2{font-weight:800;font-size:24px}
.badge{font-size:12px;font-weight:700;background:var(--bgray);color:#fff;padding:3px 9px;border-radius:7px;letter-spacing:.5px}
.cls{font-size:11.5px;font-weight:700;padding:3px 10px;border-radius:8px;border:1px solid transparent}
.c-viv{background:#FDEEE2;color:#B4500F;border-color:#F5CBA8}
.c-nbh{background:#E9F2EC;color:#22694F;border-color:#BFDCCB}
.c-hwy{background:#E8EFF5;color:#2D5674;border-color:#BED3E2}
.c-mix{background:#F3ECFA;color:#5E3A85;border-color:#D8C6EC}
.c-rem{background:#F5F1E8;color:#7A6A3A;border-color:#E0D5B8}
.c-un{background:#F1EFEB;color:#6E6A64;border-color:#DDD8CF}
.c-st{background:#fff;color:var(--ink2);border-color:var(--line2)}
.c-hd{background:#FBF6EF;color:#8A5A2B;border-color:#EAD9C3;font-family:'Tajawal'}
.smeta{display:flex;gap:16px;align-items:center;font-size:13px;color:var(--ink2);margin-top:8px;flex-wrap:wrap}
.smeta a{color:var(--blue);text-decoration:none;font-weight:600}
.smeta a:hover{color:var(--orange)}
.stars{color:#C98A1B;font-weight:800;font-family:'Tajawal'}
.saddr{font-size:12px;color:var(--ink3);margin-top:5px}
.skpis{display:grid;grid-template-columns:repeat(6,1fr);gap:11px;margin-bottom:16px}
@media(max-width:1000px){.skpis{grid-template-columns:repeat(3,1fr)}}
@media(max-width:620px){.skpis{grid-template-columns:repeat(2,1fr)}}
.kpi{background:#FDFCFA;border:1px solid var(--line);border-radius:13px;padding:12px 13px;position:relative;overflow:hidden}
.kpi::before{content:"";position:absolute;top:0;right:0;width:3px;height:100%;background:var(--line2)}
.kpi.hot::before{background:linear-gradient(var(--gold1),var(--orange))}
.kpi .kl{font-size:11.5px;color:var(--ink2);font-weight:500}
.kpi .kv{font-weight:800;font-size:21px;margin-top:6px;color:var(--ink)}
.kpi .kv small{font-size:11px;color:var(--ink2);font-weight:500}
.kpi.hot .kv{color:var(--orange)}
.kpi .kn{font-size:10.5px;color:var(--ink3);margin-top:3px}
.card{background:#FDFCFA;border:1px solid var(--line);border-radius:var(--radius);padding:16px 18px 14px}
.card .ct{display:flex;align-items:baseline;justify-content:space-between;gap:10px;margin-bottom:4px}
.card .ct h3{font-size:15px;font-weight:700}
.card .ct .leg{font-size:11px;color:var(--ink3)}
.card .cs{font-size:12.5px;color:var(--ink2);margin-bottom:12px}
.sig{margin-bottom:16px}
.siggrid{display:grid;grid-template-columns:1fr 1fr;gap:24px 34px;margin-top:12px}
.sigfull{grid-column:1/-1}
@media(max-width:900px){.siggrid{grid-template-columns:1fr}}
.sglb{font-size:15px;color:var(--ink);font-weight:700;margin-bottom:8px}
.sgnote{font-size:13.5px;color:var(--ink2);margin-top:8px}
.sgnote b{color:var(--ink);font-weight:700}
.spark{width:100%;height:auto;display:block}
.mix .mixbar{display:flex;height:30px;border-radius:9px;overflow:hidden;background:var(--bar)}
.mix .mixbar i{display:flex;align-items:center;justify-content:center;height:100%;color:#fff;font-size:13px;font-weight:700;font-style:normal;min-width:0;overflow:hidden}
.mix .mixleg{display:flex;gap:16px;font-size:13.5px;color:var(--ink2);margin-top:8px;flex-wrap:wrap}
.mix .mixleg strong{color:var(--ink)}
.mix .mixleg b{display:inline-block;width:11px;height:11px;border-radius:3px;margin-inline-end:5px}
.agrid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
@media(max-width:980px){.agrid{grid-template-columns:1fr}}
.pcard{display:flex;gap:12px;padding:11px 0;border-bottom:1px dashed var(--line2)}
.pcard:last-child{border-bottom:none}
.pico{font-size:24px;flex:none;width:40px;height:40px;display:flex;align-items:center;justify-content:center;background:#FDEEE2;border-radius:12px}
.pname{font-weight:800;font-size:14.5px}
.pshare{font-size:10.5px;font-weight:600;color:#B4500F;background:#FDEEE2;padding:2px 8px;border-radius:7px;margin-inline-start:6px}
.pbody p{font-size:12.5px;color:var(--ink2);margin:4px 0}
.pline{font-size:12px;color:var(--ink2)}
.pline b{color:var(--ink)}
.pline.act b{color:var(--orange)}
.swot{display:grid;grid-template-columns:1fr 1fr;gap:10px}
@media(max-width:620px){.swot{grid-template-columns:1fr}}
.sq{border-radius:12px;padding:12px 14px;border:1px solid var(--line)}
.sq h4{font-size:13px;font-weight:800;margin-bottom:7px}
.sq ul{padding-inline-start:16px;font-size:12px;color:var(--ink2);display:grid;gap:5px}
.sq.s{background:#F0F7F2;border-color:#CBE2D3}.sq.s h4{color:#22694F}
.sq.w{background:#FBF0ED;border-color:#EBCFC7}.sq.w h4{color:#A6432E}
.sq.o{background:#F0F5FA;border-color:#CBDDEB}.sq.o h4{color:#2D5674}
.sq.t{background:#F8F3E9;border-color:#E6D9BE}.sq.t h4{color:#8A6D2B}
.pest{display:grid;gap:10px}
.pr{display:flex;gap:12px;align-items:flex-start}
.pk{flex:none;width:30px;height:30px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-weight:800;color:#fff;font-size:14px}
.pP{background:#3E6E8E}.pE{background:#F37021}.pS{background:#2E8B6F}.pT{background:#6E5A8E}
.pr b{font-size:13px}
.pr ul{padding-inline-start:16px;font-size:12px;color:var(--ink2);display:grid;gap:4px;margin-top:4px}
.comp .ctbl{overflow-x:auto;border:1px solid var(--line);border-radius:12px}
.comp table{font-size:12.5px}
.comp td,.comp th{padding:8px 12px;white-space:normal}
.dens{font-size:11.5px;font-weight:800;padding:3px 10px;border-radius:8px}
.dens.lo{background:#E9F2EC;color:#22694F}
.dens.md{background:#F8F3E9;color:#8A6D2B}
.dens.hi{background:#FBF0ED;color:#A6432E}
.sis{font-size:12px;color:var(--ink2);margin-top:9px;background:#FDEEE2;border-radius:10px;padding:8px 12px}
details.apx{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:16px 20px;margin-top:8px}
details.apx summary{cursor:pointer;font-weight:700;font-size:14px}
details.apx .tscroll{overflow-x:auto;margin-top:12px}
footer{border-top:1px solid var(--line);margin-top:30px;padding:22px 0 34px;font-size:12px;color:var(--ink3)}
#editbar{position:fixed;bottom:18px;inset-inline-start:18px;z-index:90;display:flex;gap:9px;align-items:center;
  background:var(--card);border:1px solid var(--line2);border-radius:14px;padding:9px 12px;box-shadow:0 8px 30px rgba(61,61,61,.18);font-size:13px}
#editbar button{font-family:inherit;font-size:13px;font-weight:700;border-radius:10px;padding:8px 14px;cursor:pointer;border:1px solid var(--line2);background:#fff;color:var(--ink2);transition:.15s}
#editbar button:hover{border-color:var(--orange);color:var(--ink)}
#editbar.editing #edtoggle{background:var(--orange);border-color:var(--orange);color:#fff}
#editbar .hint{color:var(--ink3);font-size:11.5px;max-width:230px;display:none}
#editbar.editing .hint{display:block}
body.editmode{outline:3px dashed var(--orange);outline-offset:-3px}
body.editmode [contenteditable="true"]:focus{outline:2px solid var(--orange);border-radius:4px}
@media print{#editbar{display:none}}
footer b{color:var(--ink2)}
.hidden{display:none!important}
.pgnav{display:flex;gap:10px;align-items:center;justify-content:space-between;flex-wrap:wrap;margin-bottom:18px}
.pgnav .nvl{display:flex;gap:8px;flex-wrap:wrap}
.pgnav a,.pgnav select{border:1px solid var(--line2);background:#fff;border-radius:11px;padding:8px 14px;font-family:inherit;font-size:13px;color:var(--ink2);text-decoration:none;transition:.14s}
.pgnav a:hover{border-color:var(--orange);color:var(--ink)}
.pgnav a.hb{background:var(--bgray);color:#fff;border-color:var(--bgray)}
.pgnav a.hb:hover{background:var(--orange);border-color:var(--orange)}
.pgnav select{cursor:pointer;max-width:290px}
.tabs{display:flex;gap:8px;margin:0 0 16px;flex-wrap:wrap}
.tab{border:1px solid var(--line2);background:#fff;border-radius:11px;padding:8px 16px;font-family:inherit;font-size:13.5px;font-weight:600;color:var(--ink2);text-decoration:none;transition:.14s}
.tab:hover{border-color:var(--orange);color:var(--ink)}
.tab.on{background:var(--orange);border-color:var(--orange);color:#fff}
.chartbox{background:#FDFCFA;border:1px solid var(--line);border-radius:var(--radius);padding:16px 18px;margin-bottom:16px}
.chartbox h3{font-size:15px;font-weight:700;margin-bottom:2px}
.chartbox .cs{font-size:12px;color:var(--ink2);margin-bottom:10px}
.bigchart{width:100%;height:auto;display:block}
.dtbl{max-height:430px;overflow-y:auto;border:1px solid var(--line);border-radius:12px}
.dtbl thead th{position:sticky;top:0;z-index:2}
.dtbl td,.dtbl th{padding:7px 12px;font-size:12.5px}
.dnote{font-size:12px;color:var(--ink2);background:#FDEEE2;border-radius:10px;padding:9px 13px;margin-top:12px}
details.moan{background:var(--card);border:1px solid var(--line);border-radius:14px;margin-bottom:10px;overflow:hidden}
details.moan summary{list-style:none;cursor:pointer;display:flex;align-items:center;gap:12px;padding:13px 16px;flex-wrap:wrap}
details.moan summary::-webkit-details-marker{display:none}
details.moan summary:hover{background:#FBF6EF}
details.moan .mnm{font-weight:800;font-size:16px;min-width:64px}
details.moan .msum{font-size:13px;color:var(--ink2)}
details.moan .msum b{color:var(--ink)}
details.moan .mbadge{margin-inline-start:auto;font-size:12px;font-weight:800;padding:3px 12px;border-radius:8px}
.mb-exc{background:#E9F2EC;color:#22694F}.mb-good{background:#F1EFEB;color:#6E6A64}.mb-down{background:#FBF0ED;color:#A6432E}
details.moan .mbody{padding:4px 16px 16px;border-top:1px dashed var(--line2)}
.mchips{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}
.mchips span{background:#FDFCFA;border:1px solid var(--line);border-radius:10px;padding:6px 12px;font-size:12.5px;color:var(--ink2)}
.mchips span b{color:var(--ink);font-weight:800}
.cksec{border:1px solid var(--line);border-radius:12px;padding:12px 14px;margin-top:10px}
.cksec .ckh{font-size:13.5px;font-weight:800;margin-bottom:4px}
.cksec .cksub{font-size:11.5px;color:var(--ink3);margin-bottom:9px}
.ckchips{display:flex;gap:7px;flex-wrap:wrap}
.ckchip{border:1px solid var(--line2);background:#fff;border-radius:10px;padding:6px 13px;font-size:12.5px;color:var(--ink2);cursor:pointer;transition:.13s;user-select:none}
.ckchip:hover{border-color:var(--orange)}
.ckchip.ck{background:var(--orange);border-color:var(--orange);color:#fff;font-weight:700}
.ckchip.ck::before{content:"✔ "}
.ckchip.free{border-style:dashed;color:var(--ink3);min-width:120px}
.confsec{border:1px solid #CBE2D3;background:#F6FBF7;border-radius:12px;padding:12px 14px;margin-top:10px}
.confsec .ckh{color:#22694F}
.confbox{background:#fff;border:1px solid var(--line2);border-radius:10px;padding:10px 13px;font-size:13px;color:var(--ink);min-height:56px;outline:none}
.confbox:empty::before{content:attr(data-ph);color:var(--ink3)}
.confbox:focus{border-color:var(--orange)}
.mini-head{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:14px}
.mini-head h2{font-weight:800;font-size:21px}
.mini-head .rg{font-size:12.5px;color:var(--ink2)}
.mapgrid{display:grid;grid-template-columns:minmax(0,520px) 1fr;gap:20px;align-items:start}
@media(max-width:900px){.mapgrid{grid-template-columns:1fr}}
.mapsvg{width:100%;height:auto;display:block;background:#FBF8F3;border:1px solid var(--line);border-radius:14px}
.maplegend{display:grid;gap:8px;font-size:12px;color:var(--ink2)}
.maplegend .li{display:flex;gap:8px;align-items:center}
.maplegend .dot{width:12px;height:12px;border-radius:50%;flex:none;border:2px solid #fff;box-shadow:0 0 0 1px var(--line2)}
.bandrow{display:flex;gap:8px;margin-top:4px;flex-wrap:wrap}
.bandrow span{background:#FDFCFA;border:1px solid var(--line);border-radius:9px;padding:4px 10px;font-size:11.5px;color:var(--ink2)}
.bandrow b{color:var(--orange);font-family:'Tajawal'}
.svcnote{font-size:12px;color:var(--ink2);background:#F0F5FA;border:1px solid #CBDDEB;border-radius:10px;padding:9px 13px;margin-top:10px}
.cmpbar{display:flex;gap:10px;align-items:center;flex-wrap:wrap;background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:14px 16px;box-shadow:var(--shadow);margin-bottom:14px}
.cmpbar select{border:1px solid var(--line2);background:#fff;border-radius:11px;padding:9px 13px;font-family:inherit;font-size:13.5px;color:var(--ink);cursor:pointer;max-width:260px}
.cmpbar .sw{border:1px solid var(--line2);background:#fff;border-radius:11px;padding:8px 12px;cursor:pointer;font-size:15px;font-family:inherit}
.cmpbar .sw:hover{border-color:var(--orange)}
.cmpbar .lbA{font-weight:800;color:var(--orange);font-family:'Tajawal'}
.cmpbar .lbB{font-weight:800;color:var(--blue);font-family:'Tajawal'}
.dimchips{display:flex;gap:7px;flex-wrap:wrap;margin-bottom:18px}
.dim{border:1px solid var(--line2);background:#fff;border-radius:11px;padding:7px 14px;cursor:pointer;font-family:inherit;font-size:13px;color:var(--ink2);transition:.14s}
.dim.on{background:var(--bgray);border-color:var(--bgray);color:#fff}
.dim:hover{border-color:var(--orange)}
.vshead{display:grid;grid-template-columns:1fr auto 1fr;gap:10px;align-items:center;margin-bottom:12px}
.vshead .side{font-weight:800;font-size:19px}
.vshead .side.a{color:var(--orange)}
.vshead .side.b{color:var(--blue);text-align:left}
.vshead .vs{font-size:12px;color:var(--ink3);font-weight:700}
.vsrow{display:grid;grid-template-columns:1fr 170px 1fr;gap:12px;align-items:center;padding:9px 0;border-bottom:1px dashed var(--line2)}
.vsrow:last-child{border-bottom:none}
.vsrow .va,.vsrow .vb{font-weight:700;font-size:15px}
.vsrow .va{text-align:right}
.vsrow .vb{text-align:left;color:var(--ink)}
.vsrow .win{color:var(--good)}
.vsrow .mid{text-align:center}
.vsrow .mid .lb{font-size:11.5px;color:var(--ink2);margin-bottom:4px}
.vsbars{display:flex;flex-direction:column;gap:3px}
.vsbars i{display:block;height:7px;border-radius:5px;background:var(--bar)}
.vsbars i.a{background:linear-gradient(90deg,var(--gold1),var(--orange))}
.vsbars i.b{background:var(--blue)}
.pcolz{display:grid;grid-template-columns:1fr 1fr;gap:14px}
@media(max-width:760px){.pcolz{grid-template-columns:1fr}.vsrow{grid-template-columns:1fr 110px 1fr}}
.pcol{background:#FDFCFA;border:1px solid var(--line);border-radius:13px;padding:13px 15px}
.pcol h4{font-weight:800;font-size:15px;margin-bottom:8px}
.pcol.a h4{color:var(--orange)}
.pcol.b h4{color:var(--blue)}
.pitem{display:flex;gap:9px;align-items:flex-start;padding:7px 0;border-bottom:1px dashed var(--line2);font-size:12.5px;color:var(--ink2)}
.pitem:last-child{border-bottom:none}
.pitem .ic{font-size:17px;flex:none}
.pitem b{color:var(--ink)}
.pitem .uniq{font-size:10px;font-weight:700;color:#B4500F;background:#FDEEE2;border-radius:6px;padding:1px 7px;margin-inline-start:5px}
.cmpnote{font-size:11.5px;color:var(--ink3);margin-top:8px}
.grid-cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:13px;margin-bottom:34px}
.scard{background:var(--card);border:1px solid var(--line);border-radius:15px;box-shadow:var(--shadow);padding:14px 16px;text-decoration:none;color:var(--ink);transition:.15s;display:block}
.scard:hover{border-color:var(--orange);transform:translateY(-2px)}
.scard .r1{display:flex;align-items:center;gap:8px;justify-content:space-between}
.scard .nm{font-weight:800;font-size:16px}
.scard .r2{display:flex;gap:8px;align-items:center;margin-top:7px;font-size:11.5px;color:var(--ink2);flex-wrap:wrap}
.scard .r3{margin-top:9px;font-size:12px;color:var(--ink2);display:flex;justify-content:space-between}
.scard .r3 b{color:var(--orange);font-size:15px}
"""
CSS = CSS + "\n" + OPS_CSS


EDITBAR = ''' <div id="editbar" contenteditable="false">
  <button id="edtoggle" onclick="__toggleEdit()">✏️ وضع التحرير</button>
  <button onclick="__saveEdits()">⬇️ تنزيل النسخة المعدلة</button>
  <span class="hint">عدّل أي نص بالنقر عليه مباشرة. عند الانتهاء نزّل النسخة لحفظ تعديلاتك — التعديلات لا تُحفظ تلقائيًا.</span>
</div>
<script>
var __ED=false;
function __toggleEdit(){
  __ED=!__ED;
  document.body.contentEditable=__ED?'true':'false';
  document.body.spellcheck=false;
  document.body.classList.toggle('editmode',__ED);
  document.getElementById('editbar').classList.toggle('editing',__ED);
}
function __saveEdits(){
  var was=__ED; if(was) __toggleEdit();
  document.body.removeAttribute('contenteditable');
  var html='<!DOCTYPE html>'+String.fromCharCode(10)+document.documentElement.outerHTML;
  var blob=new Blob([html],{type:'text/html;charset=utf-8'});
  var a=document.createElement('a');
  a.href=URL.createObjectURL(blob);
  a.download='location-analysis-edited.html';
  document.body.appendChild(a);a.click();a.remove();
  setTimeout(function(){URL.revokeObjectURL(a.href)},2000);
  if(was) __toggleEdit();
}
</script> '''
FONTFACE = open('fontface.css', encoding='utf-8').read()
FONTS = f"""<style>{FONTFACE}</style>"""

LOGO_SVG = """<img class="darblogo" alt="شعار درب Darb" src="data:image/png;base64,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"/>"""

FOOT_METH = """<b>المنهجية والمصادر:</b> بيانات المبيعات والزيارات من لوحة «درب · تحليل المبيعات والتسويق» (يناير–يونيو 2026)؛
    مواقع المحطات من ملف Station_Data.xlsx؛ رصد المنافسين والتقييمات من خرائط جوجل (بحث «محطة وقود» ضمن دائرة نصف قطرها 5 كم حول إحداثيات كل محطة، يوليو 2026) —
    القوائم تشمل المدرَج في خرائط جوجل فقط والمسافات مباشرة (خط مستقيم). الدوائر التي أعاد المسح الآلي فيها نتائج شحيحة معلَّمة بتنبيه ولا يُبنى على عددها استنتاج تنافسي.
    تحليلات PEST/SWOT/البيرسونا مولّدة قاعديًا من مؤشرات كل محطة وتُقرأ كمسودة عمل تسويقية لا كدراسة سوق ميدانية."""

def spark_hours(code):
    o = BYCODE[code]['overall']
    hs = {h['h']: h['vis'] for h in o['hours']}
    mx = max(hs.values()) or 1
    W, H = 1100, 216
    slot = (W-30)/24; bw = slot-9
    bars = []
    bars.append(f'<line x1="15" y1="{H-160-28}" x2="{W-15}" y2="{H-160-28}" stroke="var(--line2)" stroke-dasharray="3 5"/>')
    for h in range(24):
        v = hs.get(h, 0)
        bh = max(4, round(v/mx*150))
        x = 15 + h*slot + 4.5
        hot = 'url(#gO)' if v == mx else ('#F0A868' if v >= 0.75*mx else '#CFC5B4')
        bars.append(f'<g><rect x="{x:.1f}" y="{H-34-bh}" width="{bw:.1f}" height="{bh}" rx="6" fill="{hot}"/>'
                    f'<title>الساعة {hr_ar(h)} — {v:,} زيارة ({v/max(1,sum(hs.values()))*100:.0f}٪)</title></g>')
        if v == mx or (v >= 0.75*mx and h % 2 == 0):
            lab = f'{v/1000:.1f}ألف' if v >= 1000 else f'{v:,}'
            w8 = '800' if v == mx else '600'
            bars.append(f'<text x="{x+bw/2:.1f}" y="{H-42-bh}" font-size="15" font-weight="{w8}" text-anchor="middle" fill="{"var(--orange)" if v==mx else "var(--ink2)"}">{lab}</text>')
        if h % 2 == 0:
            bars.append(f'<text x="{x+bw/2:.1f}" y="{H-12}" font-size="14" text-anchor="middle" fill="var(--ink2)">{hr_ar(h)}</text>')
    return (f'<svg viewBox="0 0 {W} {H}" class="spark" role="img" aria-label="توزيع الزيارات على الساعات">'
            f'<defs><linearGradient id="gO" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="#F7A94B"/><stop offset="1" stop-color="#F5831F"/></linearGradient></defs>{"".join(bars)}</svg>')

def spark_dow(code):
    o = BYCODE[code]['overall']
    ds = [(d['d'], d['avg']) for d in o['dow']]
    if not ds: return ''
    mx = max(v for _, v in ds) or 1
    W, H = 540, 200
    slot = (W-24)/len(ds); bw = slot-16
    bars = []
    for i, (d, v) in enumerate(ds):
        bh = max(5, round(v/mx*130))
        x = 12 + i*slot + 8
        hot = 'url(#gO)' if v == mx else '#CFC5B4'
        lab = f'{v/1000:.1f}ألف' if v >= 1000 else f'{v:,.0f}'
        bars.append(f'<g><rect x="{x:.1f}" y="{H-46-bh}" width="{bw:.1f}" height="{bh}" rx="7" fill="{hot}"/>'
                    f'<title>{d} — متوسط {v:,.0f} زيارة/يوم</title></g>'
                    f'<text x="{x+bw/2:.1f}" y="{H-54-bh}" font-size="15" font-weight="{"800" if v==mx else "600"}" text-anchor="middle" fill="{"var(--orange)" if v==mx else "var(--ink2)"}">{lab}</text>'
                    f'<text x="{x+bw/2:.1f}" y="{H-16}" font-size="14.5" text-anchor="middle" fill="var(--ink)">{d}</text>')
    return (f'<svg viewBox="0 0 {W} {H}" class="spark" role="img" aria-label="متوسط الزيارات حسب اليوم">'
            f'{"".join(bars)}</svg>')

def mixbar(parts):
    seg, leg = [], []
    for lb, fr, colr in parts:
        w = max(0.0, fr*100)
        inner = f'{fr*100:.0f}٪' if w >= 12 else ''
        seg.append(f'<i style="width:{w:.1f}%;background:{colr}" title="{esc(lb)} {fr*100:.0f}٪">{inner}</i>')
        leg.append(f'<span><b style="background:{colr}"></b>{esc(lb)} <strong>{fr*100:.0f}٪</strong></span>')
    return f'<div class="mix"><div class="mixbar">{"".join(seg)}</div><div class="mixleg">{"".join(leg)}</div></div>'

def stars(r):
    return f'<span class="stars">★ {r}</span>' if r else ''

import re as _re
def hood_of(a):
    g = a['geo'] or {}
    h = (g.get('hood') or '').strip()
    if h.startswith('حي '): h = h[3:].strip()
    if len(_re.findall(r'[\u0600-\u06FF]', h)) >= 3:
        return h
    return a['metrics']['name']

def hood_lbl(a):
    h = hood_of(a)
    return h if h.startswith(('شارع', 'طريق')) else f'حي {h}'

import math as _math
def comp_map(a):
    m, g = a['metrics'], a['geo']
    code = m['code']
    comp = COMP.get(code)
    if not (g and comp): return ''
    lat0, lng0 = g['lat'], g['lng']
    S = 520; C = S/2; PX_KM = 48.0
    def XY(lat, lng):
        dxk = (lng-lng0)*111.32*_math.cos(_math.radians(lat0))
        dyk = (lat-lat0)*110.57
        return C+dxk*PX_KM, C-dyk*PX_KM
    def rcol(r):
        if r is None: return '#9B968E'
        if r >= 4.5: return '#2E8B6F'
        if r >= 4.0: return '#C98A1B'
        return '#C0503A'
    out = []
    out.append(f'<circle cx="{C}" cy="{C}" r="{2*PX_KM}" fill="#F37021" opacity="0.07"/>')
    for km, lab in ((1,'1 كم'),(3,'3 كم'),(5,'5 كم')):
        dash = ' stroke-dasharray="6 6"' if km==5 else ' stroke-dasharray="2 5"'
        out.append(f'<circle cx="{C}" cy="{C}" r="{km*PX_KM}" fill="none" stroke="#D3CBBC" stroke-width="1.4"{dash}/>')
        out.append(f'<text x="{C+4}" y="{C-km*PX_KM+14}" font-size="10.5" fill="#9B968E">{lab}</text>')
    for txt, x, y in (('ش', C, 16), ('ج', C, S-8), ('ق', S-12, C+4), ('غ', 12, C+4)):
        out.append(f'<text x="{x}" y="{y}" font-size="12" font-weight="700" text-anchor="middle" fill="#9B968E">{txt}</text>')
    out.append(f'<line x1="20" y1="{S-22}" x2="{20+PX_KM}" y2="{S-22}" stroke="#6E6A64" stroke-width="2.5"/>')
    out.append(f'<text x="{20+PX_KM/2}" y="{S-30}" font-size="10" text-anchor="middle" fill="#6E6A64">1 كم</text>')
    for s in comp.get('sisters', []):
        x, y = XY(s['lat'], s['lng'])
        if not (6 <= x <= S-6 and 6 <= y <= S-6): continue
        out.append(f'<g><circle cx="{x:.1f}" cy="{y:.1f}" r="8.5" fill="#F5A623" stroke="#fff" stroke-width="2"/>'
                   f'<text x="{x:.1f}" y="{y+3.4:.1f}" font-size="9" font-weight="800" text-anchor="middle" fill="#fff">د</text>'
                   f'<title>{esc(s["title"])} (شقيقة) — {s["dist"]:,} م</title></g>')
    for i, cpt in enumerate(comp['top']):
        x, y = XY(cpt['lat'], cpt['lng'])
        rv = cpt['reviews'] or 0
        r = 5.5 + min(5.5, _math.log10(rv+1)*2.1)
        num = f'<text x="{x:.1f}" y="{y+3.2:.1f}" font-size="8.5" font-weight="800" text-anchor="middle" fill="#fff">{i+1}</text>' if i < 10 else ''
        out.append(f'<g><circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{rcol(cpt["rating"])}" stroke="#fff" stroke-width="1.8" opacity="0.93"/>{num}'
                   f'<title>{esc(cpt["title"])} — {cpt["dist"]:,} م · {cpt["rating"] or "بلا تقييم"}★ · {rv:,} مراجعة</title></g>')
    eco = ECO.get(code) or {}
    for r in eco.get('rentals', []):
        if r.get('lat') is None: continue
        x, y = XY(r['lat'], r['lng'])
        if not (6 <= x <= S-6 and 6 <= y <= S-6): continue
        out.append(f'<g><rect x="{x-6:.1f}" y="{y-6:.1f}" width="12" height="12" rx="3" fill="#3E6E8E" stroke="#fff" stroke-width="1.8"/>'
                   f'<title>🚘 {esc(r["title"])} — {r["dist"]:,} م{f" · {r[chr(39)+chr(114)+chr(97)+chr(116)+chr(105)+chr(110)+chr(103)+chr(39)]}★" if False else ""}</title></g>')
    for h in eco.get('hajj', []):
        if h.get('lat') is None: continue
        x, y = XY(h['lat'], h['lng'])
        if not (6 <= x <= S-6 and 6 <= y <= S-6): continue
        out.append(f'<g><path d="M {x:.1f} {y-7:.1f} L {x+7:.1f} {y+6:.1f} L {x-7:.1f} {y+6:.1f} Z" fill="#2E8B6F" stroke="#fff" stroke-width="1.8"/>'
                   f'<title>🕋 {esc(h["title"])} — {h["dist"]:,} م</title></g>')
    out.append(f'<circle cx="{C}" cy="{C}" r="13" fill="#F37021" stroke="#fff" stroke-width="3"/>'
               f'<circle cx="{C}" cy="{C}" r="4.2" fill="#fff"/>')
    out.append(f'<text x="{C}" y="{C+30}" font-size="12" font-weight="800" text-anchor="middle" fill="#3D3D3D">درب {esc(m["name"])}</text>')
    svg = (f'<svg viewBox="0 0 {S} {S}" class="mapsvg" role="img" aria-label="الخريطة التنافسية">{"".join(out)}</svg>')
    b = comp.get('bands', [0,0,0])
    cls = m['cls'] or ''
    svc = {
      'حي': 'محطة أحياء: نطاق الخدمة الفعلي يتركز في 1–2 كم (النطاق البرتقالي) — كثافة الدائرة الأولى هي الحاسمة، وما بعد 3 كم تأثيره محدود.',
      'خط سفر': 'محطة خط سفر: نطاق خدمتها الحقيقي ممتد على محور الطريق (شريطي لا دائري) — المنافسة الفعلية هي محطات المحور نفسه قبلها وبعدها، والدوائر هنا إطار استرشادي.',
      'حيوية': 'موقع حيوي: يجذب من نطاق أوسع من الحي المباشر (2–5 كم) بفضل الحركة العابرة والوجهات المجاورة.',
      'مختلط': 'موقع مختلط (حي + خط سفر): نطاق مزدوج — قاعدة سكانية قريبة ضمن 2 كم وحركة محور تمتد أبعد من الدائرة.',
      'نائية': 'موقع نائي: قد تمتد خدمته أبعد من 5 كم لغياب البدائل القريبة — الكثافة المنخفضة داخل الدوائر طبيعية.',
    }.get(cls, 'النطاق البرتقالي (2 كم) تقدير للنطاق الأساسي الحضري؛ الدائرة المتقطعة حد الرصد التنافسي (5 كم).')
    dirline = f' أعلى كثافة تنافسية جهة <b>{esc(comp["dirmax"])}</b>.' if comp.get('dirmax') else ''
    legend = f'''<div class="maplegend">
      <div class="li"><span class="dot" style="background:#F37021"></span> محطة درب (المركز) · <span class="dot" style="background:#F5A623"></span> محطات درب شقيقة</div>
      <div class="li"><span class="dot" style="background:#2E8B6F"></span> منافس تقييمه ≥ 4.5 · <span class="dot" style="background:#C98A1B"></span> 4.0–4.4 · <span class="dot" style="background:#C0503A"></span> أقل من 4.0 · <span class="dot" style="background:#9B968E"></span> بلا تقييم</div>
      <div class="li">حجم النقطة يعكس عدد المراجعات؛ الأرقام 1–10 تطابق جدول المنافسين؛ مرّر بالفأرة لأي نقطة للتفاصيل.</div>
      {f'<div class="li"><span class="dot" style="background:#3E6E8E;border-radius:3px"></span> تأجير سيارات ({len(eco.get("rentals", []))}) · <span class="dot" style="background:#2E8B6F;clip-path:polygon(50% 0,100% 100%,0 100%);border-radius:0"></span> مكاتب/حملات حج وعمرة ({len(eco.get("hajj", []))})</div>' if eco else ''}
      <div class="bandrow"><span>0–1 كم: <b>{b[0]}</b> منافس</span><span>1–3 كم: <b>{b[1]}</b></span><span>3–5 كم: <b>{b[2]}</b></span></div>
      <div class="li">{('⚠️ الرصد في هذه الدائرة غير مكتمل — الخريطة تعرض المرصود فقط.' if comp.get('thin') else '')}{dirline}</div>
      <div class="svcnote">🎯 <b>نطاق الخدمة:</b> {svc}</div>
    </div>'''
    return f'''<div class="card sig"><div class="ct"><h3>الخريطة التنافسية ونطاق الخدمة</h3>
      <div class="leg">مواقع حقيقية من خرائط جوجل — الشمال للأعلى</div></div>
      <div class="mapgrid">{svg}{legend}</div></div>'''

def station_body(a):
    """Inner content: head + kpis + signature + analysis grid (shared by pages)."""
    m, g = a['metrics'], a['geo']
    code = m['code']
    comp = COMP.get(code)
    if comp and '_meta' in COMP and comp is COMP.get('_meta'): comp = None
    x = next((r for r in XL if r['num'] == code), {})
    stt = 'تشغيل' if x.get('status') == 'Operation' else ('فرنشايز' if x.get('status') == 'Franchises' else '—')
    cls = m['cls'] or 'غير مصنفة'
    cls_cl = {'حيوية':'c-viv','حي':'c-nbh','خط سفر':'c-hwy','مختلط':'c-mix','نائية':'c-rem'}.get(cls, 'c-un')
    growth = m['growth']
    gr_html = '—' if growth is None else (f'<span class="up">+{growth:.1f}٪</span>' if growth >= 0 else f'<span class="dn">{growth:.1f}٪</span>')
    period = 'شهر واحد' if m['nmonths'] == 1 else (f"{len(m['months'])} أشهر" if m['nmonths'] < 6 else 'النصف الأول 2026')
    maps_url = x.get('loc', '#')

    kpis = f'''
    <div class="skpis">
      <div class="kpi hot"><div class="kl">إيراد الفترة ({esc(period)})</div><div class="kv">{sar(m['revenue'])}</div><div class="kn">{n0(m['visits'])} زيارة · {n0(m['volume'])} لتر</div></div>
      <div class="kpi"><div class="kl">الإيراد اليومي</div><div class="kv">{sar(m['daily_rev'])}</div><div class="kn">المرتبة {m['rank_drev']} من {m['n_total']} بالشبكة</div></div>
      <div class="kpi"><div class="kl">الزيارات اليومية</div><div class="kv">{n0(m['daily_vis'])}</div><div class="kn">ذروة الزيارات {hr_ar(m['peak_hour'])}</div></div>
      <div class="kpi"><div class="kl">متوسط الفاتورة</div><div class="kv">{m['avg_invoice']:.0f} <small>ر.س</small></div><div class="kn">متوسط التعبئة {m['avg_liters']:.0f} لترًا</div></div>
      <div class="kpi"><div class="kl">نمو Q2 مقابل Q1</div><div class="kv">{gr_html}</div><div class="kn">{'مقارنة ربعية مثل-بمثل' if growth is not None else 'لا تتوفر مقارنة (بيانات جزئية)'}</div></div>
      <div class="kpi"><div class="kl">تقييم جوجل</div><div class="kv">{g['rating'] if g and g.get('rating') else '—'} <small>★</small></div><div class="kn">{n0(g['reviews']) + ' مراجعة' if g and g.get('reviews') else 'يُرصد بعد ترسيخ الملف على الخرائط'}</div></div>
    </div>'''

    sig = f'''
    <div class="card sig">
      <div class="ct"><h3>توقيع الموقع الزمني والسلوكي</h3><div class="leg">من بيانات المبيعات الفعلية</div></div>
      <div class="siggrid">
        <div class="sigfull"><div class="sglb">الزيارات على مدار اليوم (24 ساعة)</div>{spark_hours(code)}
             <div class="sgnote">المساء (4م–12ل): <b>{pct(m['evening'])}</b> · الليل (12–5ص): <b>{pct(m['night'])}</b> · الصباح: <b>{pct(m['morning'])}</b> · ذروة الزيارات: <b>{hr_ar(m['peak_hour'])}</b></div></div>
        <div><div class="sglb">متوسط الزيارات حسب اليوم</div>{spark_dow(code)}
             <div class="sgnote">نهاية الأسبوع مقابل أيام العمل: <b>{f"{m['we_ratio']:.2f}×" if m['we_ratio'] else '—'}</b></div></div>
        <div><div class="sglb">مزيج الوقود (من الإيراد)</div>{mixbar([('بنزين 91', m['g91'], '#3E6E8E'), ('بنزين 95', m['g95'], '#F5831F'), ('ديزل', m['dsl'], '#6E6A64')])}
             <div class="sglb" style="margin-top:18px">طرق الدفع (من الإيراد)</div>{mixbar([('نقد', m['cash'], '#2E8B6F'), ('بطاقة', m['card'], '#3E6E8E'), ('تطبيقات وأخرى', m['apps'], '#F7A94B')])}</div>
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
        rows = ''.join(f'''<tr><td><b>{i+1}</b></td><td>{esc(c['title'])}</td><td>{c['dist']:,} م</td>
            <td>{c['rating'] if c['rating'] else '—'}</td><td>{n0(c['reviews']) if c['reviews'] else '—'}</td></tr>''' for i, c in enumerate(comp['top'][:10]))
        sisters = ''
        if comp.get('sisters'):
            ss = '، '.join(f"{esc(s['title'])} ({s['dist']:,} م)" for s in comp['sisters'][:4])
            sisters = f'<div class="sis">🧡 محطات درب شقيقة ضمن النطاق: {ss} — تغطية شبكية وليست منافسة.</div>'
        ratingline = ''
        if comp.get('avg_rating') and g:
            diff = g['rating'] - comp['avg_rating']
            v = 'أعلى' if diff >= 0 else 'أدنى'
            ratingline = f"متوسط تقييم المنافسين {comp['avg_rating']:.1f}★ — درب {v} بـ{abs(diff):.1f} نقطة."
        warn = '⚠️ المسح الآلي لهذه الدائرة أعاد نتائج شحيحة ولا يُعتد به وحده — يُوصى بتدقيق يدوي قبل أي قرار تنافسي. ' if comp.get('thin') else ''
        compb = f'''
        <div class="card comp"><div class="ct"><h3>المنافسون ضمن 5 كم</h3>
          <div class="leg"><span class="dens {dcls}">{dens} محطة · {dlab}</span></div></div>
          <div class="cs">{warn}الأقرب: {esc(comp['nearest']['title']) if comp.get('nearest') else 'لم تُرصد محطات'}
             {f"على بعد {comp['nearest']['dist']:,} م" if comp.get('nearest') else ''} · {ratingline}
             مصدر الرصد: خرائط جوجل (يوليو 2026).</div>
          <div class="ctbl"><table><thead><tr><th>#</th><th>المحطة المنافسة</th><th>المسافة</th><th>التقييم</th><th>المراجعات</th></tr></thead>
          <tbody>{rows or '<tr><td colspan="5">لم يرصد المسح الآلي محطات منافسة داخل الدائرة</td></tr>'}</tbody></table></div>
          {f'<div class="cmpnote">يعرض الجدول أقرب 10 — الخريطة أعلاه تعرض كل المنافسين المرصودين ({comp["n"]}).</div>' if comp['n'] > 10 else ''}{sisters}
        </div>'''
    else:
        compb = '<div class="card comp"><div class="ct"><h3>المنافسون ضمن 5 كم</h3></div><div class="cs">لا تتوفر بيانات رصد.</div></div>'

    hood = hood_of(a)
    head = f'''
    <div class="shead">
      <div class="stitle">
        <span class="badge">{code}</span><h2>درب {esc(m['name'])}</h2>
        <span class="cls c-hd">{esc(hood_lbl(a))}</span>
        <span class="cls {cls_cl}">{esc(cls)}</span><span class="cls c-st">{stt}</span>
      </div>
      <div class="smeta">
        <span>📍 {esc(m['region'])}</span>
        {stars(g['rating']) if g and g.get('rating') else ''}
        <a href="{esc(maps_url)}" target="_blank" rel="noopener">افتح في خرائط جوجل ↗</a>
      </div>
      <div class="saddr">{esc(g['address']) if g else ''}{(' — ' + esc(m['note'])) if m['note'] else ''}</div>
    </div>'''

    mapcard = comp_map(a)
    eco = ECO.get(code) or {}
    ecob = ''
    if eco:
        def ecotbl(items, label):
            rws = ''.join(f'''<tr><td><b>{i+1}</b></td><td>{esc(x['title'])}</td><td>{x['dist']:,} م</td>
                <td>{x.get('rating') or '—'}</td><td>{n0(x.get('reviews') or 0) if x.get('reviews') else '—'}</td></tr>''' for i, x in enumerate(items[:12]))
            return f'''<div class="card comp"><div class="ct"><h3>{label}</h3>
              <div class="leg"><span class="dens md">{len(items)} ضمن 5 كم</span></div></div>
              <div class="ctbl"><table><thead><tr><th>#</th><th>الاسم</th><th>المسافة</th><th>التقييم</th><th>المراجعات</th></tr></thead>
              <tbody>{rws or '<tr><td colspan="5">لا يوجد ضمن النطاق حسب الرصد</td></tr>'}</tbody></table></div></div>'''
        ecob = f'''<div class="agrid" style="margin-top:16px">
          {ecotbl(eco.get('rentals', []), '🚘 مكاتب تأجير السيارات المحيطة')}
          {ecotbl(eco.get('hajj', []), '🕋 مكاتب وحملات الحج والعمرة المحيطة')}
        </div>'''
    grid = f'''
    {mapcard}
    <div class="agrid">
      <div class="card"><div class="ct"><h3>بيرسونا العملاء</h3><div class="leg">مشتقة من مزيج الوقود والأوقات والدفع</div></div>{pers}</div>
      <div class="card"><div class="ct"><h3>تحليل SWOT</h3><div class="leg">مبيعات + موقع + منافسة</div></div>{swot}</div>
      <div class="card"><div class="ct"><h3>تحليل PEST</h3><div class="leg">بيئة {esc(m['region'])} الكلية</div></div>{pest}</div>
      {compb}
    </div>{ecob}'''
    return head + kpis + sig + grid

MONTH_AR = {'2026-01':'يناير','2026-02':'فبراير','2026-03':'مارس','2026-04':'أبريل','2026-05':'مايو','2026-06':'يونيو','2026-07':'يوليو','2026-08':'أغسطس','2026-09':'سبتمبر','2026-10':'أكتوبر','2026-11':'نوفمبر','2026-12':'ديسمبر'}
WD_AR = ['الإثنين','الثلاثاء','الأربعاء','الخميس','الجمعة','السبت','الأحد']
import datetime as _dt

def mini_head(a):
    m, g = a['metrics'], a['geo']
    return f'''<div class="mini-head"><span class="badge">{m['code']}</span><h2>درب {esc(m['name'])}</h2>
    <span class="cls c-hd">{esc(hood_lbl(a))}</span>
    <span class="rg">📍 {esc(m['region'])}</span>{f'<span class="stars">★ {g["rating"]}</span>' if g and g.get('rating') else ''}</div>'''

def tabs_html(code, active, mode):
    items = [('main','التحليل الكامل'),('monthly','المبيعات الشهرية'),('daily','المبيعات اليومية'),('camp','تقرير حملة البنزين المجاني')]
    cc = OPS_COUNTS.get(code, {})
    for k, lab in OPS_TABS:
        n = cc.get(k)
        items.append((k, lab + (f' <b class="tcount">{n}</b>' if n else '')))
    out = []
    for key, lab in items:
        if mode == 'spa':
            href = f'#/{code}' if key=='main' else f'#/{code}/{key}'
        else:
            href = '#' if key=='main' else f'#{key}'
        out.append(f'<a class="tab{" on" if key==active else ""}" href="{href}">{lab}</a>')
    return '<div class="tabs">' + ''.join(out) + '</div>'

def bars_chart(vals, labels, fmt, unit=''):
    if not vals: return ''
    W, H = 640, 190
    n = len(vals); mx = max(vals) or 1
    bw = min(64, (W-30)/n - 14)
    out = ['<defs><linearGradient id="gB" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F5A623"/><stop offset="1" stop-color="#F37021"/></linearGradient></defs>']
    for i, v in enumerate(vals):
        x = 15 + i*((W-30)/n) + ((W-30)/n - bw)/2
        bh = max(3, v/mx*(H-56))
        fill = 'url(#gB)' if v == mx else 'var(--bar)'
        out.append(f'<rect x="{x:.1f}" y="{H-30-bh:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="5" fill="{fill}"/>')
        out.append(f'<text x="{x+bw/2:.1f}" y="{H-36-bh:.1f}" font-size="11" font-weight="700" text-anchor="middle" fill="var(--ink)">{fmt(v)}</text>')
        out.append(f'<text x="{x+bw/2:.1f}" y="{H-12:.1f}" font-size="11" text-anchor="middle" fill="var(--ink2)">{labels[i]}</text>')
    return f'<svg viewBox="0 0 {W} {H}" class="bigchart" role="img">{"".join(out)}</svg>'

CAND_CAUSES = ['ذروة موسم الحج','ارتفاع الحركة المرورية','إعلان أو تحويلة طريق','صيانة مضخات أو توقف جزئي','انقطاع منتج','منافس جديد قريب','تغيّر أسعار','حملة تسويقية','تغيّر فريق التشغيل','طقس أو أمطار','أعمال إنشائية مجاورة','موسم إجازات أو عودة مدارس']

def _camp_hours_svg(vis):
    W, H, PB = 1100, 250, 34
    mx = max(vis) or 1
    slot = (W-24)/24; bw = slot-8
    out = ['<defs><linearGradient id="gC" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F5A623"/><stop offset="1" stop-color="#F37021"/></linearGradient></defs>']
    for h, v in enumerate(vis):
        x = 12 + h*slot + 4
        bh = max(2, v/mx*(H-64))
        fill = 'url(#gC)' if h >= 18 else 'var(--bar)'
        out.append(f'<rect x="{x:.1f}" y="{H-PB-bh:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="6" fill="{fill}"/>')
        if v: out.append(f'<text x="{x+bw/2:.1f}" y="{H-PB-bh-6:.1f}" font-size="12" font-weight="700" text-anchor="middle" fill="var(--ink)">{v}</text>')
        out.append(f'<text x="{x+bw/2:.1f}" y="{H-12:.1f}" font-size="11" text-anchor="middle" fill="var(--ink2)">{hr_ar(h)}</text>')
    x18 = 12 + 18*slot + 4
    out.append(f'<line x1="{x18-4:.1f}" y1="14" x2="{x18-4:.1f}" y2="{H-PB}" stroke="#C0503A" stroke-width="2" stroke-dasharray="5 4"/>')
    out.append(f'<text x="{x18-10:.1f}" y="24" font-size="12" font-weight="700" fill="#C0503A">انطلاق الحملة 6م (المغرب)</text>')
    return f'<svg viewBox="0 0 {W} {H}" class="bigchart" role="img">{"".join(out)}</svg>'

def nj219_campaign():
    try:
        tx = json.load(open('nj219_tx.json'))
    except FileNotFoundError:
        return ''
    jul = [f'2026-07-{i:02d}' for i in range(1, 32)]
    def per(days):
        T = [t for t in tx if t['d'] in days]
        n = len(T); rev = sum(t['amt'] for t in T); vol = sum(t['vol'] for t in T); nd = len(days)
        return dict(nd=nd, n=n, vol=vol, n_d=n/nd, rev_d=rev/nd, vol_d=vol/nd, inv=(rev/n if n else 0))
    pre, camp = per(jul[0:3]), per([jul[3]])
    wk, rest, aft = per(jul[4:11]), per(jul[11:31]), per(jul[4:31])
    C = [t for t in tx if t['d'] == '2026-07-04']
    camp_win_vol = sum(t['vol'] for t in C if t['h'] >= 18)
    ex50 = [t for t in C if abs(t['amt']-50) < 0.005]
    zero = sum(1 for t in C if t['amt'] == 0)
    ex50_pre = sum(1 for t in tx if t['d'] in jul[0:3] and abs(t['amt']-50) < 0.005) / 3
    vouchers = len(ex50) - ex50_pre + zero
    ex50_cash = sum(1 for t in ex50 if t['pay'] == 'Cash'); ex50_card = sum(1 for t in ex50 if t['pay'] == 'Card')
    vis_h = [0]*24
    for t in C: vis_h[t['h']] += 1
    def lift(a, b):
        ch = (a/b-1)*100
        return f'+{ch:.0f}٪' if ch >= 0 else f'{ch:.0f}٪'
    def cell(a, b):
        ch = (a/b-1)*100
        cls = 'up' if ch >= 0 else 'dn'
        return f'<span class="{cls}">{"+" if ch>=0 else ""}{ch:.0f}٪</span>'
    rowsdef = [
        ('قبل الحملة (١–٣ يوليو)', pre, 'الأساس'),
        ('يوم الحملة (السبت ٤ يوليو) 🎁', camp, None),
        ('الأسبوع التالي (٥–١١ يوليو)', wk, None),
        ('بقية الشهر (١٢–٣١ يوليو)', rest, None),
        ('كامل ما بعد الحملة (٥–٣١ يوليو)', aft, None),
    ]
    trs = ''
    for lab, p, base in rowsdef:
        chv = base or cell(p['n_d'], pre['n_d'])
        chr_ = base or cell(p['rev_d'], pre['rev_d'])
        hl = ' style="background:rgba(243,112,33,.07)"' if '🎁' in lab else ''
        trs += f'''<tr{hl}><td><b>{lab}</b></td><td>{p['nd']}</td><td>{n0(p['n_d'])}</td><td>{n0(p['vol_d'])}</td><td><b>{n0(p['vol'])}</b></td><td>{n0(p['rev_d'])}</td><td>{p['inv']:.1f}</td><td>{chv}</td><td>{chr_}</td></tr>'''
    return f'''
    <div class="sec-h" style="margin-top:26px"><h2>🎁 حملة البنزين المجاني — السبت ٤ يوليو 2026</h2><span>بنزين مجاني بقيمة 50 ر.س لأول 300 سيارة · الانطلاق الساعة 6م (المغرب)</span></div>
    <div class="card" style="border:2px solid rgba(243,112,33,.4)">
      <div class="cs" style="margin-bottom:12px">نفّذت المحطة حملة «البنزين المجاني بقيمة 50 ر.س لأول 300 سيارة» يوم السبت ٤ يوليو، وانطلقت الساعة 6 مساءً (المغرب). تُظهر بيانات المعاملات إغلاقًا تجهيزيًا كاملًا بين 4–5م (صفر عمليات)، وتوافدًا مبكرًا بين 5–6م (70 عملية)، ثم قفزت الحركة مع الانطلاق إلى 163 عملية في ساعة الذروة 6–7م (~2.7 عملية بالدقيقة).</div>
      <div class="skpis" style="grid-template-columns:repeat(4,1fr)">
        <div class="kpi hot"><div class="kl">عمليات يوم الحملة</div><div class="kv">{camp['n']}</div><div class="kn">{lift(camp['n_d'], pre['n_d'])} عن متوسط ١–٣ يوليو ({n0(pre['n_d'])}/يوم)</div></div>
        <div class="kpi"><div class="kl">لترات يوم الحملة</div><div class="kv">{n0(camp['vol_d'])}</div><div class="kn">{lift(camp['vol_d'], pre['vol_d'])} عن متوسط ما قبل الحملة</div></div>
        <div class="kpi"><div class="kl">إيراد يوم الحملة</div><div class="kv">{sar(camp['rev_d'])}</div><div class="kn">{lift(camp['rev_d'], pre['rev_d'])} عن متوسط ما قبل الحملة</div></div>
        <div class="kpi"><div class="kl">قسائم مقدّرة</div><div class="kv">~{vouchers:.0f}</div><div class="kn">{len(ex50)} عملية بقيمة 50 ر.س بالضبط (مقابل ~{ex50_pre:.0f}/يوم عادةً) + {zero} مجانية بالكامل</div></div>
      </div>
      <div class="sec-h" style="margin-top:16px"><h2>إجمالي اللترات: قبل الحملة → خلالها → بعدها</h2><span>مجاميع كل فترة كاملة</span></div>
      <div class="skpis" style="grid-template-columns:repeat(3,1fr)">
        <div class="kpi"><div class="kl">قبل الحملة (١–٣ يوليو · 3 أيام)</div><div class="kv">{n0(pre['vol'])} <small>لتر</small></div><div class="kn">بمعدل {n0(pre['vol_d'])} لتر/يوم</div></div>
        <div class="kpi hot"><div class="kl">يوم الحملة (السبت ٤ يوليو)</div><div class="kv">{n0(camp['vol'])} <small>لتر</small></div><div class="kn">منها {n0(camp_win_vol)} لترًا ({camp_win_vol/camp['vol']*100:.0f}٪) بعد الانطلاق 6م — يعادل {camp['vol']/pre['vol']*100:.0f}٪ من لترات الأيام الثلاثة قبله مجتمعة</div></div>
        <div class="kpi"><div class="kl">بعد الحملة (٥–٣١ يوليو · 27 يومًا)</div><div class="kv">{n0(aft['vol'])} <small>لتر</small></div><div class="kn">بمعدل {n0(aft['vol_d'])} لتر/يوم — {lift(aft['vol_d'], pre['vol_d'])} عن قبل الحملة</div></div>
      </div>
      <div class="chartbox"><h3>عمليات يوم الحملة ساعة بساعة</h3><div class="cs">الأعمدة البرتقالية = ما بعد انطلاق الحملة (6م المغرب حتى منتصف الليل) · توقف تجهيزي كامل 4–5م، توافد مبكر 5–6م، ثم الذروة الاستثنائية 6–7م</div>{_camp_hours_svg(vis_h)}</div>
      <div class="sec-h" style="margin-top:16px"><h2>المقارنة: قبل الحملة → يومها → بعدها</h2><span>متوسطات يومية لتحييد اختلاف عدد الأيام</span></div>
      <div class="ntable"><div class="tscroll"><table>
        <thead><tr><th>الفترة</th><th>الأيام</th><th>عمليات/يوم</th><th>لترات/يوم</th><th>إجمالي اللترات</th><th>إيراد/يوم (ر.س)</th><th>الفاتورة (ر.س)</th><th>تغير العمليات</th><th>تغير الإيراد</th></tr></thead>
        <tbody>{trs}</tbody></table></div></div>
      <div class="cksec" style="margin-top:14px"><div class="ckh">قراءة النتائج</div>
        <ul style="margin:8px 18px 0 0;padding:0;line-height:2">
          <li><b>أثناء الحملة:</b> {camp['n']} عملية يوم ٤ يوليو مقابل {n0(aft['n_d'])} عملية/يوم في المتوسط بعدها — أي أعلى بـ{lift(camp['n_d'], aft['n_d'])}، وأعلى بـ{lift(camp['n_d'], pre['n_d'])} من متوسط الأيام الثلاثة قبلها.</li>
          <li><b>أثر باقٍ بعد الحملة:</b> متوسط العمليات اليومية بعد الحملة ({n0(aft['n_d'])}/يوم) أعلى بـ{lift(aft['n_d'], pre['n_d'])} من مستواه قبلها ({n0(pre['n_d'])}/يوم)، والإيراد اليومي أعلى بـ{lift(aft['rev_d'], pre['rev_d'])} — الحملة اجتذبت عملاء واصلوا التعبئة من المحطة، والأثر أقوى في الأسبوع الأول ({lift(wk['n_d'], pre['n_d'])} عمليات) ثم استقر عند {lift(rest['n_d'], pre['n_d'])} في بقية الشهر.</li>
          <li><b>إجمالي اللترات:</b> {n0(pre['vol'])} لترًا في الأيام الثلاثة قبل الحملة، مقابل {n0(camp['vol'])} لترًا في يوم الحملة وحده (منها {n0(camp_win_vol)} لترًا بعد الانطلاق 6م)، ثم {n0(aft['vol'])} لترًا في الـ27 يومًا التالية بمعدل {n0(aft['vol_d'])} لترًا/يوم ({lift(aft['vol_d'], pre['vol_d'])} عن معدل ما قبل الحملة).</li>
          <li><b>الفاتورة لم تتأثر سلبًا:</b> {camp['inv']:.1f} ر.س يوم الحملة مقابل {pre['inv']:.1f} قبلها، وارتفعت إلى {aft['inv']:.1f} بعدها.</li>
          <li><b>آلية القسائم:</b> {len(ex50)} عملية بقيمة 50 ر.س بالضبط يوم الحملة ({ex50_cash} نقدًا / {ex50_card} بطاقة) مقابل ~{ex50_pre:.0f} عملية مماثلة في اليوم العادي، إضافة إلى {zero} عملية بقيمة صفر — أي ~{vouchers:.0f} عملية إضافية تطابق تقريبًا سقف «أول 300 سيارة» المعلن وتؤكد انضباط تنفيذ العرض.</li>
        </ul></div>
      <div class="dnote">المصدر: ملفا معاملات درب المركب NJ219 لشهري يونيو ويوليو 2026 (10,406 عملية بيع). المتوسطات محسوبة على الأيام المسجلة فعليًا.</div>
    </div>'''

def _ha_daily_svg(daily):
    W, H, PB = 1100, 260, 34
    mx = max(x['rev'] for x in daily) or 1
    n = len(daily); slot = (W-24)/n; bw = slot-6
    out = ['<defs><linearGradient id="gH" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F5A623"/><stop offset="1" stop-color="#F37021"/></linearGradient></defs>']
    imax = max(range(n), key=lambda i: daily[i]['rev'])
    for i, x in enumerate(daily):
        day = int(x['date'][-2:])
        cx = 12 + i*slot + 3
        bh = max(2, x['rev']/mx*(H-70))
        fill = 'url(#gH)' if day == 22 else ('#F5A623" opacity="0.55' if day > 22 else 'var(--bar)')
        out.append(f'<rect x="{cx:.1f}" y="{H-PB-bh:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="5" fill="{fill}"><title>{x["date"]} — {n0(x["rev"])} ر.س · {x["vis"]} عملية · {n0(x["vol"])} لتر</title></rect>')
        if day == 22 or i == imax:
            out.append(f'<text x="{cx+bw/2:.1f}" y="{H-PB-bh-6:.1f}" font-size="11.5" font-weight="700" text-anchor="middle" fill="var(--ink)">{x["rev"]/1000:.1f}ألف</text>')
        out.append(f'<text x="{cx+bw/2:.1f}" y="{H-12:.1f}" font-size="10" text-anchor="middle" fill="var(--ink2)">{day}</text>')
    d22 = next(i for i, x in enumerate(daily) if int(x['date'][-2:]) == 22)
    x22 = 12 + d22*slot + 3
    out.append(f'<text x="{x22+bw/2:.1f}" y="16" font-size="12" font-weight="700" text-anchor="middle" fill="#C0503A">🎁 يوم الحملة</text>')
    return f'<svg viewBox="0 0 {W} {H}" class="bigchart" role="img">{"".join(out)}</svg>'

def ha052_campaign():
    try:
        d = json.load(open('ha052_aug.json'))
    except FileNotFoundError:
        return ''
    daily = d['daily']
    def seg(lo, hi):
        rows = [x for x in daily if lo <= int(x['date'][-2:]) <= hi]
        nd = len(rows); rev = sum(x['rev'] for x in rows); vis = sum(x['vis'] for x in rows); vol = sum(x['vol'] for x in rows)
        return dict(nd=nd, rev=rev, vis=vis, vol=vol, n_d=vis/nd, rev_d=rev/nd, vol_d=vol/nd, inv=(rev/vis if vis else 0))
    ramp, pre, camp, post = seg(6, 14), seg(15, 21), seg(22, 22), seg(23, 31)
    def lift(a, b):
        ch = (a/b-1)*100
        return f'+{ch:.0f}٪' if ch >= 0 else f'{ch:.0f}٪'
    def cell(a, b):
        ch = (a/b-1)*100
        return f'<span class="{"up" if ch>=0 else "dn"}">{"+" if ch>=0 else ""}{ch:.0f}٪</span>'
    rows = [
        ('الافتتاح والتهيئة (٦–١٤ أغسطس)', ramp, '—', '—'),
        ('أسبوع ما قبل الحملة (١٥–٢١ أغسطس)', pre, 'الأساس', 'الأساس'),
        ('يوم الحملة (السبت ٢٢ أغسطس) 🎁', camp, None, None),
        ('بعد الحملة (٢٣–٣١ أغسطس)', post, None, None),
    ]
    trs = ''
    for lab, p, cv, cr in rows:
        cv = cv or cell(p['n_d'], pre['n_d']); cr = cr or cell(p['rev_d'], pre['rev_d'])
        hl = ' style="background:rgba(243,112,33,.07)"' if '🎁' in lab else ''
        trs += f'''<tr{hl}><td><b>{lab}</b></td><td>{p['nd']}</td><td>{n0(p['n_d'])}</td><td>{n0(p['vol_d'])}</td><td><b>{n0(p['vol'])}</b></td><td>{n0(p['rev_d'])}</td><td>{p['inv']:.1f}</td><td>{cv}</td><td>{cr}</td></tr>'''
    peak22 = next(x for x in daily if int(x['date'][-2:]) == 22)['peak_h']
    return f'''
    <div class="sec-h" style="margin-top:6px"><h2>🎁 حملة البنزين المجاني — السبت ٢٢ أغسطس 2026</h2><span>بنزين مجاني لأول 100 سيارة · بعد نحو أسبوعين من الافتتاح</span></div>
    <div class="card" style="border:2px solid rgba(243,112,33,.4)">
      <div class="cs" style="margin-bottom:12px">نفّذت المحطة — المفتتحة في ٦ أغسطس — حملة «البنزين المجاني لأول 100 سيارة» يوم السبت ٢٢ أغسطس. سجّل يوم الحملة {camp['vis']:.0f} عملية بذروة عند {hr_ar(peak22)}، والأهم أن مستوى المبيعات بعد الحملة استقر أعلى بوضوح من مستواه قبلها — الحملة كانت نقطة انعطاف منحنى نمو المحطة الجديدة.</div>
      <div class="skpis" style="grid-template-columns:repeat(4,1fr)">
        <div class="kpi hot"><div class="kl">عمليات يوم الحملة</div><div class="kv">{camp['vis']:.0f}</div><div class="kn">{lift(camp['n_d'], pre['n_d'])} عن متوسط أسبوعه السابق ({n0(pre['n_d'])}/يوم)</div></div>
        <div class="kpi"><div class="kl">لترات يوم الحملة</div><div class="kv">{n0(camp['vol'])}</div><div class="kn">{lift(camp['vol_d'], pre['vol_d'])} عن متوسط ما قبل الحملة</div></div>
        <div class="kpi"><div class="kl">إيراد يوم الحملة</div><div class="kv">{sar(camp['rev'])}</div><div class="kn">{lift(camp['rev_d'], pre['rev_d'])} عن متوسط ما قبل الحملة</div></div>
        <div class="kpi"><div class="kl">الأثر الباقي بعد الحملة</div><div class="kv">{lift(post['rev_d'], pre['rev_d'])}</div><div class="kn">{sar(post['rev_d'])} يوميًا في ٢٣–٣١ مقابل {sar(pre['rev_d'])} قبلها</div></div>
      </div>
      <div class="sec-h" style="margin-top:16px"><h2>إجمالي اللترات: قبل الحملة → خلالها → بعدها</h2><span>مجاميع كل فترة كاملة</span></div>
      <div class="skpis" style="grid-template-columns:repeat(3,1fr)">
        <div class="kpi"><div class="kl">قبل الحملة (١٥–٢١ أغسطس · 7 أيام)</div><div class="kv">{n0(pre['vol'])} <small>لتر</small></div><div class="kn">بمعدل {n0(pre['vol_d'])} لتر/يوم</div></div>
        <div class="kpi hot"><div class="kl">يوم الحملة (السبت ٢٢ أغسطس)</div><div class="kv">{n0(camp['vol'])} <small>لتر</small></div><div class="kn">{lift(camp['vol_d'], pre['vol_d'])} عن المعدل اليومي قبله</div></div>
        <div class="kpi"><div class="kl">بعد الحملة (٢٣–٣١ أغسطس · 9 أيام)</div><div class="kv">{n0(post['vol'])} <small>لتر</small></div><div class="kn">بمعدل {n0(post['vol_d'])} لتر/يوم — {lift(post['vol_d'], pre['vol_d'])} عن قبل الحملة</div></div>
      </div>
      <div class="chartbox"><h3>الإيراد اليومي عبر أغسطس — أين وقعت الحملة؟</h3><div class="cs">رمادي: من الافتتاح حتى ما قبل الحملة · برتقالي غامق: يوم الحملة (٢٢) · برتقالي فاتح: ما بعد الحملة — لاحظ ثبات المستوى الأعلى بعدها</div>{_ha_daily_svg(daily)}</div>
      <div class="sec-h" style="margin-top:16px"><h2>المقارنة: قبل الحملة → يومها → بعدها</h2><span>متوسطات يومية لتحييد اختلاف عدد الأيام · الأساس = أسبوع ما قبل الحملة</span></div>
      <div class="ntable"><div class="tscroll"><table>
        <thead><tr><th>الفترة</th><th>الأيام</th><th>عمليات/يوم</th><th>لترات/يوم</th><th>إجمالي اللترات</th><th>إيراد/يوم (ر.س)</th><th>الفاتورة (ر.س)</th><th>تغير العمليات</th><th>تغير الإيراد</th></tr></thead>
        <tbody>{trs}</tbody></table></div></div>
      <div class="cksec" style="margin-top:14px"><div class="ckh">قراءة النتائج</div>
        <ul style="margin:8px 18px 0 0;padding:0;line-height:2">
          <li><b>أثناء الحملة:</b> {camp['vis']:.0f} عملية يوم ٢٢ أغسطس مقابل {n0(pre['n_d'])}/يوم في أسبوعه السابق ({lift(camp['n_d'], pre['n_d'])})، وذروة اليوم عند {hr_ar(peak22)}.</li>
          <li><b>الأثر الأهم جاء بعد الحملة:</b> متوسط الإيراد اليومي قفز من {n0(pre['rev_d'])} ر.س قبلها إلى {n0(post['rev_d'])} ر.س في الأيام التسعة التالية ({lift(post['rev_d'], pre['rev_d'])})، والعمليات من {n0(pre['n_d'])} إلى {n0(post['n_d'])}/يوم ({lift(post['n_d'], pre['n_d'])}) — وثبت المستوى حتى نهاية الشهر، أي أن الحملة عرّفت جمهور حائل بالمحطة الجديدة وحوّلت جزءًا منه إلى عملاء دائمين.</li>
          <li><b>إجمالي اللترات:</b> {n0(pre['vol'])} لترًا في أسبوع ما قبل الحملة، و{n0(camp['vol'])} لترًا يوم الحملة وحده، ثم {n0(post['vol'])} لترًا في ٩ أيام بعدها بمعدل {n0(post['vol_d'])} لتر/يوم.</li>
          <li><b>الفاتورة:</b> {camp['inv']:.1f} ر.س يوم الحملة مقابل {pre['inv']:.1f} قبلها و{post['inv']:.1f} بعدها — لا أثر سلبي يُذكر.</li>
          <li><b>آلية «أول 100 سيارة»:</b> هذا الملف مجمّع يوميًا، لذا عدّ القسائم وساعة الانطلاق بدقة يتطلبان ملف المعاملات التفصيلي — تُضاف الطبقة التفصيلية فور التزويد بنفس منهجية تقرير درب المركب NJ219.</li>
        </ul></div>
      <div class="dnote">المصدر: ملف مبيعات درب حائل HA052 لشهر أغسطس 2026 ({n0(sum(x['vis'] for x in daily))} عملية · ٦–٣١ أغسطس). المحطة افتُتحت في ٦ أغسطس 2026، لذا اعتُمد أسبوع ١٥–٢١ أساسًا للمقارنة بدل أيام التهيئة الأولى.</div>
    </div>'''

def camp_body(a):
    code = a['metrics']['code']
    if code == 'NJ219':
        rpt = nj219_campaign()
        if rpt: return rpt
    if code == 'HA052':
        rpt = ha052_campaign()
        if rpt: return rpt
    return '''<div class="sec-h"><h2>🎁 تقرير حملة البنزين المجاني</h2><span>بانتظار بيانات حملة هذه المحطة</span></div>
    <div class="card">
      <div class="cs" style="margin-bottom:10px">لم تُزوَّد بيانات حملة لهذه المحطة بعد. عند توفر ملف معاملات فترة الحملة يُبنى التقرير هنا بنفس منهجية تقرير محطة درب المركب NJ219، ويشمل:</div>
      <ul style="margin:0 18px 12px 0;padding:0;line-height:2">
        <li>يوم الحملة وساعة الانطلاق ومؤشراته: العمليات، اللترات، الإيراد، متوسط الفاتورة.</li>
        <li>إجمالي اللترات قبل الحملة وخلالها وبعدها.</li>
        <li>رسم عمليات يوم الحملة ساعة بساعة مع لحظة الانطلاق.</li>
        <li>جدول المقارنة: قبل الحملة → يومها → الأسبوع التالي → بقية الفترة.</li>
        <li>آلية القسائم والعدد المقدّر منها.</li>
        <li>قراءة النتائج والأثر الباقي بعد الحملة.</li>
      </ul>
      <div class="ckh">ملاحظات</div>
      <div class="confbox" contenteditable="true" data-ph="سجّل هنا تاريخ حملة هذه المحطة وقيمتها وشروطها… وسيُستكمل التقرير عند وصول البيانات"></div>
    </div>'''

def month_cards(code, mm, keys):
    ov = BYCODE[code]['overall']
    base_ratio = (ov.get('volume') or 0) / ov['revenue'] if ov['revenue'] else 0
    out = []
    prev = None
    for k in keys:
        v = mm[k]
        drev = v['daily_avg_rev']
        if prev is None:
            chtxt, badge, bcls = 'أول شهر مسجل', 'جيد', 'mb-good'
        else:
            ch = (drev/prev - 1) * 100
            chtxt = (f'+{ch:.0f}٪' if ch >= 0 else f'{ch:.0f}٪') + ' عن الشهر السابق'
            badge, bcls = ('ممتاز','mb-exc') if ch >= 10 else (('جيد','mb-good') if ch >= -5 else ('متراجع','mb-down'))
        prev = drev
        vol = v.get('volume')
        litd = (vol/v['ndays']) if (vol and v['ndays']) else (drev*base_ratio if base_ratio else None)
        litmark = '' if vol else '*'
        chips = f'''<div class="mchips">
          <span>إيراد/يوم <b>{n0(drev)}</b> ر.س</span>
          <span>زيارات/يوم <b>{n0(v['daily_avg_vis'])}</b></span>
          <span>فاتورة <b>{v['avg_invoice']:.0f}</b> ر.س</span>
          <span>لترات/يوم <b>{n0(litd) if litd else '—'}{litmark}</b></span>
          <span>ذروة <b>{hr_ar(v['peak_vis_hour'])}</b></span>
          <span>أيام مسجلة <b>{v['ndays']}</b></span>
        </div>'''
        cand = ''.join(f'<span class="ckchip" onclick="this.classList.toggle(\'ck\')">{c}</span>' for c in CAND_CAUSES)
        out.append(f'''<details class="moan"><summary>
          <span class="mnm">{MONTH_AR.get(k,k)}</span>
          <span class="msum">{chtxt} · <b>{n0(drev)}</b> ر.س/يوم</span>
          <span class="mbadge {bcls}">{badge}</span></summary>
          <div class="mbody">{chips}
            <div class="cksec"><div class="ckh">أسباب مرشّحة للتحقق</div>
              <div class="cksub">اضغط على السبب لتعليمه ✔ — ويمكن إضافة أسباب أخرى في الخانة الحرة. اختياراتك تُحفظ عند تنزيل النسخة المعدلة.</div>
              <div class="ckchips">{cand}<span class="ckchip free" contenteditable="true" data-ph="+ سبب آخر…"></span></div></div>
            <div class="confsec"><div class="ckh">✅ السبب المؤكد والإجراء</div>
              <div class="cksub">اكتب مباشرة — الخانة قابلة للتحرير دائمًا وتُحفظ عند تنزيل النسخة</div>
              <div class="confbox" contenteditable="true" data-ph="السبب المؤكد لأداء هذا الشهر… والإجراء المتخذ أو المقترح…"></div></div>
          </div></details>''')
    return ('<div class="sec-h" style="margin-top:20px"><h2>تحليل كل شهر</h2><span>اضغط على الشهر لفتح بطاقته: مؤشراته، الأسباب المرشّحة، والسبب المؤكد والإجراء</span></div>'
            + ''.join(out)
            + '<div class="dnote">(*) لترات الأشهر غير مكتملة اللترات محسوبة تقديريًا من نسبة لترات الفترة.</div>')

def monthly_body(a):
    m = a['metrics']; code = m['code']
    if code not in BYCODE: return awaiting_sales('monthly')
    st = BYCODE[code]; mm = st.get('monthly', {})
    keys = sorted(mm.keys())
    if not keys: return '<div class="card"><div class="cs">لا تتوفر بيانات شهرية.</div></div>'
    best = max(keys, key=lambda k: mm[k]['revenue'])
    tot = sum(mm[k]['revenue'] for k in keys)
    rows = ''
    prev_drev = None
    for k in keys:
        v = mm[k]
        mom = ''
        if prev_drev:
            ch = (v['daily_avg_rev']/prev_drev - 1)*100
            mom = f'<span class="up">+{ch:.0f}٪</span>' if ch >= 0 else f'<span class="dn">{ch:.0f}٪</span>'
        prev_drev = v['daily_avg_rev']
        partial = ' <span class="tcode">(جزئي)</span>' if v['ndays'] < 26 else ''
        vol = n0(v['volume']) if v.get('volume') else '—'
        rows += f'''<tr><td><b>{MONTH_AR.get(k,k)}</b>{partial}</td><td>{v['ndays']}</td><td>{n0(v['revenue'])}</td>
        <td>{n0(v['visits'])}</td><td>{vol}</td><td>{v['avg_invoice']:.0f}</td>
        <td>{n0(v['daily_avg_rev'])}</td><td>{hr_ar(v['peak_vis_hour'])}</td><td>{mom or '—'}</td></tr>'''
    fuel_rows = ''
    for k in keys:
        fs = {f['fuel']: f['rev'] for f in mm[k].get('fuels', [])}
        fr = sum(fs.values()) or 1
        fuel_rows += f'''<tr><td><b>{MONTH_AR.get(k,k)}</b></td><td>{fs.get('Gasoline 91',0)/fr*100:.0f}٪</td>
        <td>{fs.get('Gasoline 95',0)/fr*100:.0f}٪</td><td>{fs.get('Diesel',0)/fr*100:.0f}٪</td></tr>'''
    kpis = f'''
    <div class="skpis" style="grid-template-columns:repeat(4,1fr)">
      <div class="kpi hot"><div class="kl">إجمالي إيراد الفترة</div><div class="kv">{sar(tot)}</div><div class="kn">{len(keys)} أشهر ({MONTH_AR.get(keys[0])} → {MONTH_AR.get(keys[-1])} 2026)</div></div>
      <div class="kpi"><div class="kl">أفضل شهر</div><div class="kv">{MONTH_AR.get(best)}</div><div class="kn">{n0(mm[best]['revenue'])} ر.س</div></div>
      <div class="kpi"><div class="kl">متوسط الإيراد الشهري</div><div class="kv">{sar(tot/len(keys))}</div><div class="kn">للأشهر المسجلة</div></div>
      <div class="kpi"><div class="kl">متوسط الفاتورة (الفترة)</div><div class="kv">{m['avg_invoice']:.0f} <small>ر.س</small></div><div class="kn">{m['avg_liters']:.0f} لترًا للتعبئة</div></div>
    </div>'''
    ch1 = bars_chart([mm[k]['revenue'] for k in keys], [MONTH_AR.get(k,k) for k in keys], lambda v: f'{v/1e6:.1f}م' if v>=1e6 else f'{v/1e3:.0f}ألف')
    ch2 = bars_chart([mm[k]['daily_avg_rev'] for k in keys], [MONTH_AR.get(k,k) for k in keys], lambda v: f'{v/1e3:.0f}ألف')
    return f'''{kpis}
    <div class="chartbox"><h3>الإيراد الشهري (ر.س)</h3><div class="cs">الأشهر الجزئية تظهر أقل بحكم عدد الأيام — قارن بمتوسط اليوم أدناه</div>{ch1}</div>
    <div class="chartbox"><h3>متوسط الإيراد اليومي لكل شهر (ر.س)</h3><div class="cs">المقياس الأدق لمقارنة الأشهر بغض النظر عن اكتمال أيامها</div>{ch2}</div>
    <div class="ntable"><div class="tscroll"><table>
      <thead><tr><th>الشهر</th><th>أيام مسجلة</th><th>الإيراد (ر.س)</th><th>الزيارات</th><th>اللترات</th><th>الفاتورة (ر.س)</th><th>متوسط اليوم (ر.س)</th><th>ساعة الذروة</th><th>التغير٪*</th></tr></thead>
      <tbody>{rows}</tbody></table></div></div>
    <div class="sec-h" style="margin-top:18px"><h2>مزيج الوقود شهريًا</h2><span>نسب من إيراد الشهر</span></div>
    <div class="ntable"><div class="tscroll"><table>
      <thead><tr><th>الشهر</th><th>بنزين 91</th><th>بنزين 95</th><th>ديزل</th></tr></thead>
      <tbody>{fuel_rows}</tbody></table></div></div>
    <div class="dnote">(*) التغير محسوب على متوسط الإيراد اليومي لكل شهر لتحييد الأشهر الجزئية. المصدر: لوحة مبيعات درب H1 2026.</div>
    {month_cards(code, mm, keys)}'''

def daily_line_chart(daily):
    if len(daily) < 2: return ''
    W, H, PL, PB = 920, 240, 46, 26
    vals = [d['rev'] for d in daily]
    mx = max(vals) or 1
    n = len(vals)
    def X(i): return PL + i*(W-PL-8)/(n-1)
    def Y(v): return 10 + (1 - v/mx)*(H-10-PB)
    pts = ' '.join(f'{X(i):.1f},{Y(v):.1f}' for i, v in enumerate(vals))
    ma = []
    for i in range(n):
        w = vals[max(0,i-6):i+1]
        ma.append(sum(w)/len(w))
    mpts = ' '.join(f'{X(i):.1f},{Y(v):.1f}' for i, v in enumerate(ma))
    months_seen, ticks = set(), []
    for i, d in enumerate(daily):
        mk = d['date'][:7]
        if mk not in months_seen:
            months_seen.add(mk)
            ticks.append(f'<line x1="{X(i):.1f}" y1="10" x2="{X(i):.1f}" y2="{H-PB}" stroke="var(--line)" stroke-dasharray="2 4"/>'
                         f'<text x="{X(i)+4:.1f}" y="{H-8}" font-size="11" fill="var(--ink2)">{MONTH_AR.get(mk,mk)}</text>')
    grid = ''.join(f'<line x1="{PL}" y1="{Y(mx*f):.1f}" x2="{W-8}" y2="{Y(mx*f):.1f}" stroke="var(--line)" stroke-dasharray="2 4"/>'
                   f'<text x="{PL-6}" y="{Y(mx*f)+4:.1f}" font-size="10" text-anchor="end" fill="var(--ink3)">{mx*f/1e3:.0f}ألف</text>'
                   for f in (1.0, .5))
    return (f'<svg viewBox="0 0 {W} {H}" class="bigchart" role="img" aria-label="الإيراد اليومي">'
            f'{grid}{"".join(ticks)}'
            f'<polyline points="{pts}" fill="none" stroke="#C9BFB0" stroke-width="1.4"/>'
            f'<polyline points="{mpts}" fill="none" stroke="#F37021" stroke-width="2.6" stroke-linejoin="round"/>'
            f'</svg>')

def daily_body(a):
    m = a['metrics']; code = m['code']
    if code not in BYCODE: return awaiting_sales('daily')
    daily = [d for d in BYCODE[code]['overall'].get('daily', []) if d['rev'] > 0]
    if not daily: return '<div class="card"><div class="cs">لا تتوفر بيانات يومية بعد — بانتظار التزويد.</div></div>'
    # نسبة اللترات/الإيراد لكل شهر من الفعلي الشهري (معايرة بمزيج وقود الشهر)؛ وإلا نسبة الفترة كاملة
    ov = BYCODE[code]['overall']
    base_ratio = (ov.get('volume') or 0) / ov['revenue'] if ov['revenue'] else 0
    mratio = {}
    for mk, mv in BYCODE[code].get('monthly', {}).items():
        if mv.get('volume') and mv.get('revenue'):
            mratio[mk] = mv['volume'] / mv['revenue']
    act = ACT.get(code, {})
    def liters_of(d):
        a = act.get(d['date'])
        if a and a.get('lit'):
            return a['lit']
        r = mratio.get(d['date'][:7], base_ratio)
        return d['rev'] * r
    n_act = sum(1 for d in daily if act.get(d['date'], {}).get('lit'))
    tot_lit = sum(liters_of(d) for d in daily)
    vals = [d['rev'] for d in daily]
    avg = sum(vals)/len(vals)
    best = max(daily, key=lambda d: d['rev']); worst = min(daily, key=lambda d: d['rev'])
    last30 = vals[-30:]; prev30 = vals[-60:-30]
    trend = ''
    if len(prev30) >= 15:
        ch = (sum(last30)/len(last30))/(sum(prev30)/len(prev30)) - 1
        trend = (f'<span class="up">+{ch*100:.0f}٪</span>' if ch >= 0 else f'<span class="dn">{ch*100:.0f}٪</span>')
    def wd(ds): return WD_AR[_dt.date(*map(int, ds.split('-'))).weekday()]
    rows = ''
    for d in reversed(daily):
        inv = d['rev']/d['vis'] if d['vis'] else 0
        lit = liters_of(d)
        litv = lit/d['vis'] if d['vis'] else 0
        is_act = bool(act.get(d['date'], {}).get('lit'))
        mark = '' if is_act else '*'
        rows += f'''<tr><td>{d['date']}</td><td>{wd(d['date'])}</td><td>{n0(d['rev'])}</td><td>{n0(lit)}{mark}</td><td>{n0(d['vis'])}</td><td>{inv:.0f}</td><td>{litv:.0f}{mark}</td></tr>'''
    kpis = f'''
    <div class="skpis" style="grid-template-columns:repeat(6,1fr)">
      <div class="kpi hot"><div class="kl">متوسط الإيراد اليومي</div><div class="kv">{sar(avg)}</div><div class="kn">{len(daily)} يومًا مسجلًا</div></div>
      <div class="kpi"><div class="kl">متوسط اللترات اليومية{'' if n_act == len(daily) else '*'}</div><div class="kv">{n0(tot_lit/len(daily))} <small>لتر</small></div><div class="kn">إجمالي الفترة {n0(tot_lit)} لتر{f' · فعلي لـ{n_act} من {len(daily)} يومًا' if 0 < n_act < len(daily) else (' · فعلي 100٪ من ملفات المعاملات' if n_act == len(daily) else '')}</div></div>
      <div class="kpi"><div class="kl">أفضل يوم</div><div class="kv">{n0(best['rev'])} <small>ر.س</small></div><div class="kn">{best['date']} ({wd(best['date'])})</div></div>
      <div class="kpi"><div class="kl">أدنى يوم</div><div class="kv">{n0(worst['rev'])} <small>ر.س</small></div><div class="kn">{worst['date']} ({wd(worst['date'])})</div></div>
      <div class="kpi"><div class="kl">آخر 30 يومًا مقابل ما قبلها</div><div class="kv">{trend or '—'}</div><div class="kn">على متوسط الإيراد اليومي</div></div>
      <div class="kpi"><div class="kl">التذبذب اليومي</div><div class="kv">{m['cv']*100:.0f}٪ <small>CV</small></div><div class="kn">أقل = أكثر استقرارًا</div></div>
    </div>'''
    return f'''{kpis}
    <div class="chartbox"><h3>الإيراد اليومي عبر الفترة</h3><div class="cs">الخط الرمادي: القيم اليومية · الخط البرتقالي: متوسط متحرك 7 أيام</div>{daily_line_chart(daily)}</div>
    <div class="sec-h"><h2>سجل الأيام</h2><span>الأحدث أولًا — {daily[-1]['date']} ← {daily[0]['date']}</span></div>
    <div class="dtbl"><table>
      <thead><tr><th>التاريخ</th><th>اليوم</th><th>الإيراد (ر.س)</th><th>اللترات*</th><th>الزيارات</th><th>متوسط الفاتورة</th><th>لتر/زيارة*</th></tr></thead>
      <tbody>{rows}</tbody></table></div>
    <div class="dnote">{'📌 اللترات اليومية <b>فعلية</b> — محسوبة من ملفات المعاملات الشهرية (Drive «2026»، عمود ResponseVolume بعد استبعاد غير المبيعات). ' if n_act == len(daily) else ('📌 اللترات المعلَّمة بدون نجمة <b>فعلية</b> من ملفات المعاملات؛ والمعلَّمة بنجمة (*) تقديرية للأيام غير المغطاة. ' if n_act else '')}{'' if n_act == len(daily) else '(*) اللترات التقديرية:'} البيانات اليومية في لوحة المبيعات تتضمن الإيراد والزيارات فقط، فحسبنا اللترات بضرب إيراد كل يوم في نسبة اللترات/الإيراد <b>الفعلية لنفس الشهر</b> (المعايَرة بمزيج وقود الشهر{' — وبنسبة الفترة للأشهر ناقصة اللترات' if len(mratio) < len(BYCODE[code].get('monthly', {})) else ''}). اللترات الشهرية الفعلية في تبويب «المبيعات الشهرية». البيانات حتى {daily[-1]['date']} — عند تزويدنا بملف يومي يتضمن اللترات الفعلية تُستبدل التقديرات مباشرة.</div>'''

# ---------------- location-only stations (no sales data yet) ----------------
import gen_analysis as _GA

def _mk_xtra_ha052():
    code = 'HA052'
    geo = json.load(open('coords.json'))[code]
    base = _GA.PEST_CITY[_GA.CITY_GROUP.get('حائل', 'qassim')]
    pest = dict(p=base['P'][:4], e=base['E'][:4], s=base['S'][:4], t=base['T'][:4])
    personas = [
        dict(icon='🏘️', name='ابن الحي الوفي', share='مبدئي',
             desc='سكان الأحياء المحيطة بشارع الأمير سعود — تعبئات متكررة قصيرة على مدار الأسبوع.',
             wants='سرعة الخدمة، ثبات الجودة، متجر صغير لاحتياجات المنزل السريعة.',
             msg='برنامج ولاء افتتاحي مبكر يحوّل سكان النطاق الأول (0–2 كم) إلى قاعدة دائمة قبل ترسّخ عاداتهم مع المنافسين.'),
        dict(icon='🚗', name='الموظف العابر', share='مبدئي',
             desc='حركة ذهاب وعودة يومية على الشريان التجاري صباحًا وبعد العصر.',
             wants='مسارات دخول وخروج سلسة، دفع سريع بالبطاقة أو التطبيق.',
             msg='تجهيز مسار خدمة سريع وتفعيل الدفع الرقمي منذ اليوم الأول — ذروة متوقعة صباحية ومسائية.'),
        dict(icon='🛒', name='عميل الخدمات المكملة', share='مبدئي',
             desc='يفاضل بين محطات المدينة بحسب المتجر والمغسلة والخدمات الإضافية لا الوقود وحده.',
             wants='مغسلة، تغيير زيت، مقهى أو متجر — تجربة متكاملة.',
             msg='الخدمات المكملة هي أداة التمايز الأقوى في سوق موحّد الأسعار — تفعيلها مبكرًا يبني ميزة يصعب تقليدها.'),
    ]
    swot = dict(
        s=['موقع على شريان تجاري رئيسي في مركز حائل (شارع الأمير سعود)',
           'تغطية شبكية مع درب العريفي HA043 على بعد 1.2 كم فقط',
           'هوية درب الموحدة وتجربة علامة جاهزة منذ الافتتاح'],
        w=['الموقع لم يُفتتح بعد (فرنشايز قيد التجهيز) — لا سجل تشغيلي',
           'لا تتوفر بيانات مبيعات بعد لضبط التشغيل والتسويق',
           'تداخل محتمل لنطاق الخدمة مع المحطة الشقيقة القريبة يتطلب تمايزًا بالخدمات'],
        o=['افتتاح ترويجي على غرار حملة درب المركب NJ219 (+148٪ حركة يوم الحملة وأثر باقٍ +32٪)',
           'تكامل تشغيلي مع HA043: عروض مشتركة وتحويل الفائض وقت الذروة',
           'خدمات مكملة (متجر/مغسلة/تغيير زيت) لالتقاط عميل الخدمات في سوق موحّد الأسعار'],
        t=['منافسة محطات مركز حائل القائمة ذات القواعد الراسخة',
           'توحيد أسعار الوقود يحصر التمايز في الخدمة والتجربة',
           'أي تعثر في تجهيز الامتياز ينعكس على صورة العلامة في المدينة'])
    metrics = dict(code=code, name='حائل', region='حائل', cls=None, note='', months=[], nmonths=0,
                   n_total=len(ORDER))
    return dict(metrics=metrics, geo=geo, comp=None, personas=personas, swot=swot, pest=pest)

XTRA = {}  # location-only stations (none currently — HA052 graduated to full sales data in Aug 2026)
XCODES = list(XTRA.keys())
ALLCODES = CODES + XCODES
def _AM(c):
    return (A[c] if c in A else XTRA[c])['metrics']

AWAIT_TABS = {
    'monthly': ('المبيعات الشهرية', 'جداول الإيراد والزيارات واللترات شهريًا، مزيج الوقود، وبطاقات تحليل كل شهر'),
    'daily': ('المبيعات اليومية', 'سجل الأيام باللترات الفعلية والإيراد والزيارات مع الرسم الزمني والمتوسط المتحرك'),
}
def awaiting_sales(kind):
    lab, det = AWAIT_TABS[kind]
    return f'''<div class="sec-h"><h2>{lab}</h2><span>بانتظار بيانات المبيعات</span></div>
    <div class="card"><div class="cs" style="margin-bottom:8px">لم تُربط بيانات مبيعات لهذا الموقع بعد — الموقع قيد التجهيز (فرنشايز).
    فور تزويدنا بملفات المعاملات أو ربط الموقع بلوحة المبيعات، يُبنى هذا التبويب تلقائيًا بنفس منهجية بقية المحطات ويشمل: {det}.</div>
    <div class="ckh">ملاحظات</div>
    <div class="confbox" contenteditable="true" data-ph="سجّل هنا تاريخ الافتتاح المتوقع أو أي ملاحظات تشغيلية…"></div></div>'''

def nosales_station_body(a):
    m, g = a['metrics'], a['geo']
    code = m['code']
    comp = COMP.get(code)
    x = next((r for r in XL if r['num'] == code), {})
    stt = 'تشغيل' if x.get('status') == 'Operation' else ('فرنشايز' if x.get('status') == 'Franchises' else '—')
    maps_url = x.get('loc', '#')
    sis = (comp or {}).get('sisters') or []
    sis0 = sis[0] if sis else None
    head = f'''
    <div class="shead">
      <div class="stitle">
        <span class="badge">{code}</span><h2>درب {esc(m['name'])}</h2>
        <span class="cls c-hd">{esc(hood_lbl(a))}</span>
        <span class="cls c-un">قيد التجهيز</span><span class="cls c-st">{stt}</span>
      </div>
      <div class="smeta">
        <span>📍 {esc(m['region'])}</span>
        <a href="{esc(maps_url)}" target="_blank" rel="noopener">افتح في خرائط جوجل ↗</a>
      </div>
      <div class="saddr">{esc(g['address'])} · {g['lat']:.6f}, {g['lng']:.6f}</div>
    </div>'''
    kpis = f'''
    <div class="skpis">
      <div class="kpi hot"><div class="kl">حالة الموقع</div><div class="kv">قيد التجهيز</div><div class="kn">فرنشايز — لم يُفتتح بعد</div></div>
      <div class="kpi"><div class="kl">بيانات المبيعات</div><div class="kv">بانتظار الربط</div><div class="kn">تُضاف تلقائيًا فور توفر ملفات المعاملات</div></div>
      <div class="kpi"><div class="kl">أقرب محطة درب</div><div class="kv">{f"{sis0['dist']/1000:.1f} <small>كم</small>" if sis0 else '—'}</div><div class="kn">{esc(sis0['title']) if sis0 else '—'}</div></div>
      <div class="kpi"><div class="kl">رصد المنافسين</div><div class="kv">غير مكتمل</div><div class="kn">دائرة 5 كم تُستكمل لاحقًا</div></div>
      <div class="kpi"><div class="kl">تقييم جوجل</div><div class="kv">— <small>★</small></div><div class="kn">يُرصد بعد الافتتاح</div></div>
      <div class="kpi"><div class="kl">المدينة</div><div class="kv">{esc(m['region'])}</div><div class="kn">{esc(hood_lbl(a))}</div></div>
    </div>'''
    pers = ''.join(f'''
      <div class="pcard"><div class="pico">{p['icon']}</div>
        <div class="pbody"><div class="pname">{esc(p['name'])} <span class="pshare">{esc(p['share'])}</span></div>
        <p>{esc(p['desc'])}</p>
        <div class="pline"><b>يحتاج:</b> {esc(p['wants'])}</div>
        <div class="pline act"><b>التحرك التسويقي:</b> {esc(p['msg'])}</div></div></div>''' for p in a['personas'])
    def lis(xs): return ''.join(f'<li>{esc(i)}</li>' for i in xs)
    sw = a['swot']
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
    sisters_line = ''
    if sis:
        ss = '، '.join(f"{esc(s['title'])} ({s['dist']:,} م)" for s in sis[:4])
        sisters_line = f'<div class="sis">🧡 محطات درب شقيقة ضمن النطاق: {ss} — تغطية شبكية وليست منافسة.</div>'
    compb = f'''
    <div class="card comp"><div class="ct"><h3>المنافسون ضمن 5 كم</h3>
      <div class="leg"><span class="dens md">رصد غير مكتمل</span></div></div>
      <div class="cs">⚠️ لم يُستكمل المسح الآلي لهذه الدائرة بعد — تُعرض الخريطة بالنطاقات والمحطة الشقيقة فقط، ويُضاف المنافسون فور اكتمال الرصد.</div>
      <div class="ctbl"><table><thead><tr><th>#</th><th>المحطة المنافسة</th><th>المسافة</th><th>التقييم</th><th>المراجعات</th></tr></thead>
      <tbody><tr><td colspan="5">بانتظار استكمال رصد دائرة حائل</td></tr></tbody></table></div>{sisters_line}
    </div>'''
    note = '''<div class="card" style="border:2px solid rgba(243,112,33,.35)"><div class="cs">
      📌 هذا الموقع أُضيف بالتحليل المكاني فقط — <b>البيرسونا وSWOT هنا مبدئية مشتقة من خصائص الموقع</b> وتُستكمل وتُدقّق تلقائيًا بنفس منهجية بقية المحطات فور توفر بيانات المبيعات، وكل التبويبات جاهزة كقوالب تُعبأ تباعًا.</div></div>'''
    grid = f'''
    {comp_map(a)}
    <div class="agrid">
      <div class="card"><div class="ct"><h3>بيرسونا العملاء</h3><div class="leg">مبدئية من خصائص الموقع — تُستكمل من المبيعات</div></div>{pers}</div>
      <div class="card"><div class="ct"><h3>تحليل SWOT</h3><div class="leg">مبدئي — موقع ومنافسة وحالة تجهيز</div></div>{swot}</div>
      <div class="card"><div class="ct"><h3>تحليل PEST</h3><div class="leg">بيئة {esc(m['region'])} الكلية</div></div>{pest}</div>
      {compb}
    </div>'''
    return head + kpis + note + grid

# ---------------- per-station pages ----------------
for idx, a in list(enumerate(ORDER)) + [(None, x) for x in XTRA.values()]:
    m = a['metrics']; code = m['code']
    prv = CODES[idx-1] if idx and idx > 0 else None
    nxt = CODES[idx+1] if idx is not None and idx < len(CODES)-1 else None
    rank_txt = ('موقع جديد — بانتظار بيانات المبيعات' if code in XTRA
                else f"المرتبة {m['rank_drev']} من {m['n_total']} بالإيراد اليومي · 2026")
    opts = ''.join(
        f'<option value="{c}.html"{" selected" if c==code else ""}>{esc(_AM(c)["name"])} — {c} ({esc(_AM(c)["region"])})</option>'
        for c in ALLCODES)
    nav = f'''
    <div class="pgnav">
      <div class="nvl">
        <a class="hb" href="../location-analysis.html">⌂ جميع المحطات</a>
        {f'<a href="{prv}.html">→ السابقة: {esc(A[prv]["metrics"]["name"])}</a>' if prv else ''}
        {f'<a href="{nxt}.html">التالية: {esc(A[nxt]["metrics"]["name"])} ←</a>' if nxt else ''}
      </div>
      <select onchange="location.href=this.value" aria-label="انتقل إلى محطة">{opts}</select>
    </div>'''
    page = f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>درب {esc(m['name'])} {code} — {esc(hood_lbl(a))} · تحليل الموقع والمبيعات</title>
{FONTS}
<style>{CSS}</style>
</head>
<body>
<header>
  <div class="wrap">
    <div class="brand">
      <div class="mark"><a href="../location-analysis.html">{LOGO_SVG}</a></div>
      <div class="hd-title"><h1>تحليل الموقع والمبيعات — درب {esc(m['name'])} <span style="color:var(--gold1);font-family:'DIN Next Arabic'">{code}</span></h1>
      <p>{esc(hood_lbl(a))} · {esc(m['region'])} · {rank_txt}</p></div>
    </div>
  </div>
</header>
<main class="wrap" style="padding-top:20px">
  {nav}
  {_re.sub(r'href="#([a-z]+)"', lambda mm: 'href="#'+mm.group(1)+'" data-v="'+mm.group(1)+'"', tabs_html(code, 'main', 'file')).replace('class="tab', 'data-v="main" class="tab', 1)}
  <div class="pgview" id="v-main"><section class="station">{nosales_station_body(a) if code in XTRA else station_body(a)}</section></div>
  <div class="pgview" id="v-monthly" hidden>{mini_head(a)}{monthly_body(a)}</div>
  <div class="pgview" id="v-daily" hidden>{mini_head(a)}{daily_body(a)}</div>
  <div class="pgview" id="v-camp" hidden>{mini_head(a)}{camp_body(a)}</div>
  {''.join(f'<div class="pgview" id="v-{k}" hidden>{mini_head(a)}{ops_content(code, k)}</div>' for k, lab in OPS_TABS)}
  <footer>{FOOT_METH}</footer>
</main>
<script>
function route(){{
  const h=location.hash.replace('#','');
  const k=['monthly','daily','camp','targets','cs','partners','external','plan'].includes(h)?h:'main';
  document.querySelectorAll('.pgview').forEach(p=>p.hidden=true);
  document.getElementById('v-'+k).hidden=false;
  document.querySelectorAll('.tab').forEach(t=>t.classList.toggle('on',(t.dataset.v||'main')===k));
  window.scrollTo(0,0);
}}
window.addEventListener('hashchange',route);route();
</script>
{EDITBAR}
</body>
</html>'''
    open(f'stations/{code}.html', 'w', encoding='utf-8').write(page)

# ---------------- hub page ----------------
tot_rev = sum(a['metrics']['revenue'] for a in ORDER)
tot_vis = sum(a['metrics']['visits'] for a in ORDER)
avg_rt = statistics.mean(a['geo']['rating'] for a in ORDER if a['geo'] and a['geo'].get('rating'))
ncomp = COMP.get('_meta', {}).get('unique_competitors')

chips = '<button class="chip on" data-r="*"><span class="nm">الكل</span><span class="code">' + str(len(ORDER) + len(XTRA)) + '</span></button>'
for r in REGIONS:
    n = sum(1 for a in ORDER if a['metrics']['region'] == r) + sum(1 for x in XTRA.values() if x['metrics']['region'] == r)
    chips += f'<button class="chip" data-r="{esc(r)}"><span class="nm">{esc(r)}</span><span class="code">{n}</span></button>'

cards = ''
for i, a in enumerate(ORDER, 1):
    m, g = a['metrics'], a['geo']
    c = COMP.get(m['code']) or {}
    cls = m['cls'] or 'غير مصنفة'
    cls_cl = {'حيوية':'c-viv','حي':'c-nbh','خط سفر':'c-hwy','مختلط':'c-mix','نائية':'c-rem'}.get(cls, 'c-un')
    gr = m['growth']
    gh = '' if gr is None else (f'<span class="up">+{gr:.0f}٪</span>' if gr >= 0 else f'<span class="dn">{gr:.0f}٪</span>')
    hood = hood_of(a)
    cards += f'''<a class="scard" href="#/{m['code']}" data-region="{esc(m['region'])}" data-name="{esc(m['name'])} {m['code']} {esc(hood)}">
      <div class="r1"><span class="nm">درب {esc(m['name'])}</span><span class="badge">{m['code']}</span></div>
      <div class="r2"><span>{esc(hood_lbl(a))}</span><span>📍 {esc(m['region'])}</span><span class="cls {cls_cl}">{esc(cls)}</span>{f'<span class="stars">★ {g["rating"]}</span>' if g and g.get('rating') else ''}</div>
      <div class="r3"><span>إيراد يومي <b>{n0(m['daily_rev'])}</b> ر.س</span><span>#{i} {gh}</span></div>
    </a>'''

for x in XTRA.values():
    m = x['metrics']
    cards += f'''<a class="scard" href="#/{m['code']}" data-region="{esc(m['region'])}" data-name="{esc(m['name'])} {m['code']} {esc(hood_of(x))}">
      <div class="r1"><span class="nm">درب {esc(m['name'])}</span><span class="badge">{m['code']}</span></div>
      <div class="r2"><span>{esc(hood_lbl(x))}</span><span>📍 {esc(m['region'])}</span><span class="cls c-un">قيد التجهيز</span></div>
      <div class="r3"><span>بانتظار بيانات المبيعات</span><span>فرنشايز</span></div>
    </a>'''

ov_rows = ''
for i, a in enumerate(ORDER, 1):
    m, g = a['metrics'], a['geo']
    c = COMP.get(m['code'])
    gr = m['growth']
    gh = '—' if gr is None else (f'<span class="up">+{gr:.0f}٪</span>' if gr >= 0 else f'<span class="dn">{gr:.0f}٪</span>')
    ov_rows += f'''<tr data-region="{esc(m['region'])}">
      <td>{i}</td><td><a class="stlink" href="#/{m['code']}">{esc(m['name'])}</a> <span class="tcode">{m['code']}</span></td><td>{esc(m['region'])}</td>
      <td>{esc(m['cls'] or '—')}</td><td>{n0(m['daily_rev'])}</td><td>{m['avg_invoice']:.0f}</td><td>{gh}</td>
      <td>{(str(c['n']) + ('*' if c.get('thin') else '')) if c else '—'}</td><td>{g['rating'] if g and g.get('rating') else '—'}</td></tr>'''

for x in XTRA.values():
    m = x['metrics']
    ov_rows += f'''<tr data-region="{esc(m['region'])}">
      <td>—</td><td><a class="stlink" href="#/{m['code']}">{esc(m['name'])}</a> <span class="tcode">{m['code']}</span></td><td>{esc(m['region'])}</td>
      <td>قيد التجهيز</td><td>—</td><td>—</td><td>—</td><td>0*</td><td>—</td></tr>'''

nosales = [r for r in XL if r['num'] not in A and r['num'] not in XTRA]
from collections import Counter
bycity = Counter(r['city'].strip() for r in nosales)
app_sum = '، '.join(f"{c} ({n})" for c, n in bycity.most_common())
app_rows = ''.join(f"<tr><td>{esc(r['num'])}</td><td>{esc(r['city'])}</td><td>{esc(r['name'])}</td>"
                   f"<td>{'تشغيل' if r['status']=='Operation' else 'فرنشايز'}</td>"
                   f"<td><a href='{esc(r['loc'])}' target='_blank' rel='noopener'>الموقع ↗</a></td></tr>" for r in nosales)

def spa_view(idx, a):
    m = a['metrics']; code = m['code']
    prv = CODES[idx-1] if idx and idx > 0 else None
    nxt = CODES[idx+1] if idx is not None and idx < len(CODES)-1 else None
    opts = ''.join(
        f'<option value="#/{c}"{" selected" if c==code else ""}>{esc(_AM(c)["name"])} — {c} ({esc(_AM(c)["region"])})</option>'
        for c in ALLCODES)
    nav = f'''
    <div class="pgnav">
      <div class="nvl">
        <a class="hb" href="#/">⌂ جميع المحطات</a>
        {f'<a href="#/{prv}">→ السابقة: {esc(A[prv]["metrics"]["name"])}</a>' if prv else ''}
        {f'<a href="#/{nxt}">التالية: {esc(A[nxt]["metrics"]["name"])} ←</a>' if nxt else ''}
      </div>
      <select onchange="location.hash=this.value" aria-label="انتقل إلى محطة">{opts}</select>
    </div>'''
    bottom = f'''<div class="pgnav" style="margin-top:4px"><div class="nvl">
      <a class="hb" href="#/">⌂ جميع المحطات</a>
      {f'<a href="#/{nxt}">المحطة التالية: {esc(A[nxt]["metrics"]["name"])} ←</a>' if nxt else ''}
    </div></div>'''
    return (
      f'''<div class="pgview" id="pg-{code}" data-title="درب {esc(m['name'])} {code} · {esc(hood_lbl(a))}" hidden>
      {nav}{tabs_html(code, 'main', 'spa')}
      <section class="station">{nosales_station_body(a) if code in XTRA else station_body(a)}</section>{bottom}</div>'''
      f'''<div class="pgview" id="pg-{code}-monthly" data-title="درب {esc(m['name'])} {code} · المبيعات الشهرية" hidden>
      {nav}{tabs_html(code, 'monthly', 'spa')}{mini_head(a)}{monthly_body(a)}{bottom}</div>'''
      f'''<div class="pgview" id="pg-{code}-daily" data-title="درب {esc(m['name'])} {code} · المبيعات اليومية" hidden>
      {nav}{tabs_html(code, 'daily', 'spa')}{mini_head(a)}{daily_body(a)}{bottom}</div>'''
      f'''<div class="pgview" id="pg-{code}-camp" data-title="درب {esc(m['name'])} {code} · تقرير حملة البنزين المجاني" hidden>
      {nav}{tabs_html(code, 'camp', 'spa')}{mini_head(a)}{camp_body(a)}{bottom}</div>'''
      + ''.join(
        f'''<div class="pgview" id="pg-{code}-{k}" data-title="درب {esc(m['name'])} {code} · {lab}" hidden>
        {nav}{tabs_html(code, k, 'spa')}{mini_head(a)}{ops_content(code, k)}{bottom}</div>'''
        for k, lab in OPS_TABS)
    )

SPA_VIEWS = ''.join(spa_view(i, a) for i, a in enumerate(ORDER)) + ''.join(spa_view(None, x) for x in XTRA.values())

# ---- comparison view (regions or stations, dimension filters) ----
import gen_analysis as GA
CMP_ST = {}
for a in ORDER:
    m = a['metrics']; g = a['geo']; code = m['code']
    comp = COMP.get(code) or {}
    CMP_ST[code] = dict(
        code=code, name=m['name'], region=m['region'], nmonths=m['nmonths'],
        revenue=round(m['revenue']), drev=round(m['daily_rev']), dvis=round(m['daily_vis'],1),
        inv=m['avg_invoice'], lit=m['avg_liters'], growth=m['growth'],
        evening=m['evening'], night=m['night'], morning=m['morning'], midday=m['midday'],
        we=m['we_ratio'], peak=m['peak_hour'],
        g91=m['g91'], g95=m['g95'], dsl=m['dsl'], cash=m['cash'], card=m['card'], apps=m['apps'],
        rating=(g or {}).get('rating'), compn=comp.get('n'), compthin=bool(comp.get('thin')),
        compavg=comp.get('avg_rating'), cls=m['cls'],
        personas=[[p['icon'], p['name']] for p in a['personas']],
        pest=a['pest'],
    )
CMP_RG = {}
for r in REGIONS:
    codes = [a['metrics']['code'] for a in ORDER if a['metrics']['region'] == r]
    grp = GA.CITY_GROUP.get(r, 'qassim')
    base = GA.PEST_CITY[grp]
    CMP_RG[r] = dict(codes=codes, pest=dict(p=base['P'][:3], e=base['E'][:3], s=base['S'][:3], t=base['T'][:3]))
CMP_JSON = json.dumps({'stations': CMP_ST, 'regions': CMP_RG, 'regionOrder': REGIONS}, ensure_ascii=False)

CMP_HTML = '''<div class="pgview" id="pg-compare" data-title="مقارنة المناطق والمحطات" hidden>
  <div class="pgnav"><div class="nvl"><a class="hb" href="#/">⌂ جميع المحطات</a></div></div>
  <div class="sec-h"><h2>⚖️ إنشاء مقارنة</h2><span>اختر الطرفين وحدد الخواص المطلوبة — النتائج تتحدث فورًا</span></div>
  <div class="cmpbar">
    <select id="cmpMode" aria-label="نوع المقارنة">
      <option value="region" selected>مقارنة مناطق</option>
      <option value="station">مقارنة محطات</option>
    </select>
    <span class="lbA">أ</span><select id="cmpA"></select>
    <button class="sw" id="cmpSwap" title="تبديل الطرفين">⇄</button>
    <span class="lbB">ب</span><select id="cmpB"></select>
  </div>
  <div class="dimchips" id="cmpDims">
    <button class="dim on" data-d="sales">المبيعات</button>
    <button class="dim on" data-d="time">الأنماط الزمنية</button>
    <button class="dim on" data-d="mix">مزيج الوقود والدفع</button>
    <button class="dim on" data-d="persona">البيرسونا</button>
    <button class="dim on" data-d="pest">PEST</button>
    <button class="dim on" data-d="comp">المنافسة ≤5كم</button>
    <button class="dim on" data-d="health">مؤشرات تشغيلية</button>
  </div>
  <div id="cmpOut"></div>
  <div class="cmpnote">القيم النسبية (فاتورة، أنماط، مزيج) مرجّحة بحجم الزيارات/الإيراد؛ إيراد الفترة يتأثر بعدد الأشهر المسجلة لكل محطة — الأدق للمقارنة هو معدلات اليوم. المناطق ذات محطة واحدة تمثل تلك المحطة فقط.</div>
</div>'''

CMP_SCRIPT = r'''<script>
const CMP=JSON.parse(document.getElementById('cmpdata').textContent);
const $=id=>document.getElementById(id);
const F0=v=>v==null?'—':Math.round(v).toLocaleString('en');
const F1=v=>v==null?'—':(Math.round(v*10)/10).toLocaleString('en');
const FP=v=>v==null?'—':Math.round(v*100)+'٪';
const HR=h=>h==null?'—':((h%12)||12)+(h<12?'ص':'م');
function groupCodes(mode,key){return mode==='region'?CMP.regions[key].codes:[key];}
function agg(codes){
  const ss=codes.map(c=>CMP.stations[c]);
  const W=(f,w)=>{let n=0,d=0;ss.forEach(s=>{const x=f(s),ww=w(s);if(x!=null&&ww){n+=x*ww;d+=ww}});return d?n/d:null};
  const AV=f=>{const xs=ss.map(f).filter(x=>x!=null);return xs.length?xs.reduce((a,b)=>a+b,0)/xs.length:null};
  const SM=f=>ss.reduce((a,s)=>a+(f(s)||0),0);
  const FR=f=>{const xs=ss.filter(s=>f(s)!=null);return xs.length?xs.filter(f).length/xs.length:null};
  const peaks={};ss.forEach(s=>{peaks[s.peak]=(peaks[s.peak]||0)+1});
  const peak=Object.keys(peaks).length?+Object.entries(peaks).sort((a,b)=>b[1]-a[1])[0][0]:null;
  const pers={};ss.forEach(s=>s.personas.forEach(([ic,nm])=>{pers[nm]=pers[nm]||{ic,n:0};pers[nm].n++}));
  return {n:ss.length,rev:SM(s=>s.revenue),drev:SM(s=>s.drev),dvis:SM(s=>s.dvis),
    inv:W(s=>s.inv,s=>s.dvis),lit:W(s=>s.lit,s=>s.dvis),
    growth:AV(s=>s.growth),gN:ss.filter(s=>s.growth!=null).length,
    evening:W(s=>s.evening,s=>s.dvis),night:W(s=>s.night,s=>s.dvis),morning:W(s=>s.morning,s=>s.dvis),midday:W(s=>s.midday,s=>s.dvis),
    we:AV(s=>s.we),peak,
    g91:W(s=>s.g91,s=>s.drev),g95:W(s=>s.g95,s=>s.drev),dsl:W(s=>s.dsl,s=>s.drev),
    cash:W(s=>s.cash,s=>s.drev),card:W(s=>s.card,s=>s.drev),apps:W(s=>s.apps,s=>s.drev),
    rating:AV(s=>s.rating),
    compn:AV(s=>s.compthin?null:s.compn),thinN:ss.filter(s=>s.compthin).length,
    compavg:AV(s=>s.compavg),
    hiComp:FR(s=>s.compthin?null:(s.compn>=10)),
    posG:FR(s=>s.growth==null?null:(s.growth>0)),
    topRt:FR(s=>s.rating==null?null:(s.rating>=4.8)),
    cashHv:FR(s=>s.cash>0.6),nightAct:FR(s=>s.night>=0.15),
    pers:Object.entries(pers).map(([nm,v])=>({nm,ic:v.ic,n:v.n})).sort((a,b)=>b.n-a.n)};
}
function vsRow(lb,va,vb,fa,fb,hib){
  const aw=(hib!=null&&va!=null&&vb!=null&&va!==vb)?(hib?va>vb:va<vb):false;
  const bw=(hib!=null&&va!=null&&vb!=null&&va!==vb)?(hib?vb>va:vb<va):false;
  const mx=Math.max(Math.abs(va||0),Math.abs(vb||0))||1;
  return `<div class="vsrow"><div class="va ${aw?'win':''}">${fa}</div>
    <div class="mid"><div class="lb">${lb}</div><div class="vsbars">
    <i class="a" style="width:${Math.max(4,Math.abs(va||0)/mx*100)}%"></i>
    <i class="b" style="width:${Math.max(4,Math.abs(vb||0)/mx*100)}%"></i></div></div>
    <div class="vb ${bw?'win':''}">${fb}</div></div>`;
}
function card(title,leg,body){return `<div class="card" style="margin-bottom:16px"><div class="ct"><h3>${title}</h3><div class="leg">${leg||''}</div></div>${body}</div>`}
function mixPair(lb,parts,A,B){
  const bar=g=>'<div class="mix"><div class="mixbar">'+parts.map(([k,l,c])=>`<i style="width:${(g[k]||0)*100}%;background:${c}" title="${l}"></i>`).join('')+'</div><div class="mixleg">'+parts.map(([k,l,c])=>`<span><b style="background:${c}"></b>${l} ${FP(g[k])}</span>`).join('')+'</div></div>';
  return `<div class="pcolz"><div class="pcol a"><h4>${lb} — أ</h4>${bar(A)}</div><div class="pcol b"><h4>${lb} — ب</h4>${bar(B)}</div></div>`;
}
function pestCol(cls,name,pe){
  const K=[['p','pP','سياسي/تنظيمي'],['e','pE','اقتصادي'],['s','pS','اجتماعي'],['t','pT','تقني']];
  return `<div class="pcol ${cls}"><h4>${name}</h4><div class="pest">`+K.map(([k,kc,kl])=>
    `<div class="pr"><span class="pk ${kc}">${kl[0]==='س'?'P':kl[0]==='ا'&&k==='e'?'E':k==='s'?'S':'T'}</span><div><b>${kl}</b><ul>`+
    (pe[k]||[]).map(x=>`<li>${x}</li>`).join('')+`</ul></div></div>`).join('')+`</div></div>`;
}
function render(){
  const mode=$('cmpMode').value,ka=$('cmpA').value,kb=$('cmpB').value;
  const dims=[...document.querySelectorAll('#cmpDims .dim.on')].map(b=>b.dataset.d);
  const A=agg(groupCodes(mode,ka)),B=agg(groupCodes(mode,kb));
  const nameA=mode==='region'?ka:CMP.stations[ka].name+' '+ka;
  const nameB=mode==='region'?kb:CMP.stations[kb].name+' '+kb;
  let out=`<div class="card" style="margin-bottom:16px"><div class="vshead">
    <div class="side a">${nameA} <span class="tcode">(${A.n} ${A.n===1?'محطة':'محطات'})</span></div>
    <div class="vs">مقابل</div>
    <div class="side b">${nameB} <span class="tcode">(${B.n} ${B.n===1?'محطة':'محطات'})</span></div></div></div>`;
  if(dims.includes('sales')) out+=card('المبيعات','معدلات اليوم أدق من إجمالي الفترة لاختلاف الأشهر المسجلة',
    vsRow('إيراد الفترة المسجل (ر.س)',A.rev,B.rev,F0(A.rev),F0(B.rev),null)+
    vsRow('الإيراد اليومي الإجمالي (ر.س)',A.drev,B.drev,F0(A.drev),F0(B.drev),true)+
    vsRow('متوسط إيراد المحطة/يوم',A.drev/A.n,B.drev/B.n,F0(A.drev/A.n),F0(B.drev/B.n),true)+
    vsRow('الزيارات اليومية الإجمالية',A.dvis,B.dvis,F0(A.dvis),F0(B.dvis),true)+
    vsRow('متوسط الفاتورة (مرجّح)',A.inv,B.inv,F1(A.inv)+' ر.س',F1(B.inv)+' ر.س',true)+
    vsRow('متوسط اللترات للتعبئة',A.lit,B.lit,F1(A.lit),F1(B.lit),true)+
    vsRow('متوسط نمو Q2٪',A.growth,B.growth,A.growth==null?'—':F1(A.growth)+'٪ ('+(A.gN===1?'محطة واحدة':A.gN+' محطات')+')',B.growth==null?'—':F1(B.growth)+'٪ ('+(B.gN===1?'محطة واحدة':B.gN+' محطات')+')',true)+
    vsRow('متوسط تقييم جوجل',A.rating,B.rating,F1(A.rating)+'★',F1(B.rating)+'★',true));
  if(dims.includes('time')) out+=card('الأنماط الزمنية','حصص الزيارات مرجّحة بحجم كل محطة',
    vsRow('حصة المساء (4م–12ل)',A.evening,B.evening,FP(A.evening),FP(B.evening),null)+
    vsRow('حصة الليل (12–5ص)',A.night,B.night,FP(A.night),FP(B.night),null)+
    vsRow('حصة الصباح (5ص–12م)',A.morning,B.morning,FP(A.morning),FP(B.morning),null)+
    vsRow('نهاية الأسبوع ÷ أيام العمل',A.we,B.we,A.we==null?'—':F1(A.we)+'×',B.we==null?'—':F1(B.we)+'×',null)+
    vsRow('ساعة الذروة الغالبة',null,null,HR(A.peak),HR(B.peak),null));
  if(dims.includes('mix')) out+=card('مزيج الوقود والدفع','نسب من الإيراد (مرجّحة)',
    mixPair('الوقود',[['g91','بنزين 91','#3E6E8E'],['g95','بنزين 95','#F37021'],['dsl','ديزل','#6E6A64']],A,B)+
    '<div style="height:12px"></div>'+
    mixPair('الدفع',[['cash','نقد','#2E8B6F'],['card','بطاقة','#3E6E8E'],['apps','تطبيقات','#F5A623']],A,B));
  if(dims.includes('persona')){
    const mk=(g,other,cls,nm)=>`<div class="pcol ${cls}"><h4>${nm}</h4>`+(g.pers.slice(0,5).map(p=>{
      const uniq=!other.pers.some(q=>q.nm===p.nm);
      return `<div class="pitem"><span class="ic">${p.ic}</span><span><b>${p.nm}</b> — في ${p.n} من ${g.n} ${g.n===1?'محطة':'محطات'}${uniq?'<span class="uniq">مميزة لهذا الطرف</span>':''}</span></div>`}).join('')||'<div class="pitem">—</div>')+`</div>`;
    out+=card('البيرسونا السائدة','تكرار ظهور كل شخصية في محطات الطرف',
      `<div class="pcolz">${mk(A,B,'a',nameA)}${mk(B,A,'b',nameB)}</div>`);
  }
  if(dims.includes('pest')){
    const pa=mode==='region'?CMP.regions[ka].pest:CMP.stations[ka].pest;
    const pb=mode==='region'?CMP.regions[kb].pest:CMP.stations[kb].pest;
    out+=card('بيئة PEST','العوامل الكلية لكل طرف',`<div class="pcolz">${pestCol('a',nameA,pa)}${pestCol('b',nameB,pb)}</div>`);
  }
  if(dims.includes('comp')){
    const th=(g)=>g.thinN?` <span class="tcode">(${g.thinN} دوائر رصدها ناقص)</span>`:'';
    out+=card('المنافسة ضمن 5 كم','من رصد خرائط جوجل — الدوائر الناقصة مستبعدة من المتوسط',
      vsRow('متوسط المنافسين حول المحطة',A.compn,B.compn,A.compn==null?'—':F1(A.compn)+th(A),B.compn==null?'—':F1(B.compn)+th(B),false)+
      vsRow('٪ محطات بمنافسة عالية (10+)',A.hiComp,B.hiComp,FP(A.hiComp),FP(B.hiComp),false)+
      vsRow('متوسط تقييم المنافسين',A.compavg,B.compavg,F1(A.compavg)+'★',F1(B.compavg)+'★',null)+
      vsRow('تفوق درب على المنافسين (نقاط تقييم)',A.rating-A.compavg,B.rating-B.compavg,F1(A.rating-A.compavg),F1(B.rating-B.compavg),true));
  }
  if(dims.includes('health')) out+=card('مؤشرات تشغيلية','نِسَب من محطات كل طرف (حيث تتوفر البيانات)',
    vsRow('نمو Q2 موجب',A.posG,B.posG,FP(A.posG),FP(B.posG),true)+
    vsRow('تقييم جوجل ≥ 4.8★',A.topRt,B.topRt,FP(A.topRt),FP(B.topRt),true)+
    vsRow('اعتماد نقدي مفرط (>60٪)',A.cashHv,B.cashHv,FP(A.cashHv),FP(B.cashHv),false)+
    vsRow('ليل نشط (≥15٪ من الزيارات)',A.nightAct,B.nightAct,FP(A.nightAct),FP(B.nightAct),true));
  $('cmpOut').innerHTML=out;
}
function fillSel(){
  const mode=$('cmpMode').value,a=$('cmpA'),b=$('cmpB');
  let opts='';
  if(mode==='region') CMP.regionOrder.forEach(r=>opts+=`<option value="${r}">${r} (${CMP.regions[r].codes.length})</option>`);
  else Object.values(CMP.stations).forEach(s=>opts+=`<option value="${s.code}">${s.name} — ${s.code} (${s.region})</option>`);
  a.innerHTML=opts;b.innerHTML=opts;
  if(mode==='region'){a.value=CMP.regionOrder[0]||'';b.value=CMP.regionOrder[1]||CMP.regionOrder[0];}
  else{const ks=Object.keys(CMP.stations);a.value=ks[0];b.value=ks[1]||ks[0];}
  render();
}
['cmpA','cmpB'].forEach(id=>$(id).addEventListener('change',render));
$('cmpMode').addEventListener('change',fillSel);
$('cmpSwap').addEventListener('click',()=>{const a=$('cmpA').value;$('cmpA').value=$('cmpB').value;$('cmpB').value=a;render();});
document.querySelectorAll('#cmpDims .dim').forEach(d=>d.addEventListener('click',()=>{d.classList.toggle('on');render();}));
fillSel();
</script>'''


hub = f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>درب · تحليل المحطات والمبيعات — دليل المحطات</title>
{FONTS}
<style>{CSS}</style>
</head>
<body>
<header>
  <div class="wrap">
    <div class="brand">
      <div class="mark">{LOGO_SVG}</div>
      <div class="hd-title"><h1>تحليل المحطات والمبيعات – صفحة مستقلة لكل محطة تشمل: تحليل PEST، العميل المستهدف (Persona)، تحليل SWOT، وتحليل المنافسين ضمن نطاق 5 كم</h1>
      <p>2026 · {len(ORDER) + len(XTRA)} محطة مشمولة {f'({len(ORDER)} ببيانات مبيعات) ' if XTRA else 'بالبيانات '}· اختر محطة لفتح صفحتها الكاملة</p></div>
    </div>
    <div class="netkpis">
      <div><div class="v">{len(ORDER) + len(XTRA)}</div><div class="l">محطة مشمولة بالتحليل{f' — {len(ORDER)} ببيانات مبيعات' if XTRA else ''} (من أصل {len(XL)})</div></div>
      <div><div class="v">{tot_rev/1e6:,.1f} <small>مليون ر.س</small></div><div class="l">إيراد الفترة</div></div>
      <div><div class="v">{tot_vis/1e6:,.2f} <small>مليون</small></div><div class="l">زيارة</div></div>
      <div><div class="v">{avg_rt:.2f} ★</div><div class="l">متوسط تقييم درب على جوجل</div></div>
      <div><div class="v">{n0(ncomp) if ncomp is not None else '—'}</div><div class="l">محطة منافسة فريدة مرصودة ضمن نطاقات 5 كم</div></div>
    </div>
  </div>
</header>
<div id="hub">
<div class="stationbar"><div class="chips" id="chips"><a class="chip" href="#/compare" style="background:var(--orange);border-color:var(--orange);color:#fff;font-weight:700">⚖️ إنشاء مقارنة</a>{chips}
  <div class="search"><input id="q" type="search" placeholder="ابحث باسم المحطة أو الكود…" aria-label="بحث"></div>
</div></div>
<main class="wrap">
  <div class="sec-h"><h2>المحطات</h2><span>اضغط على أي بطاقة لفتح صفحة المحطة الكاملة</span></div>
  <div class="grid-cards" id="cards">{cards}</div>
  <div class="sec-h"><h2>جدول الترتيب</h2><span>مرتب بالإيراد اليومي · (*) رصد منافسين غير مكتمل</span></div>
  <div class="ntable"><div class="tscroll"><table id="ovt">
    <thead><tr><th>#</th><th>المحطة</th><th>المدينة</th><th>التصنيف</th><th>إيراد يومي (ر.س)</th><th>الفاتورة (ر.س)</th><th>نمو Q2</th><th>منافسون ≤5كم</th><th>جوجل ★</th></tr></thead>
    <tbody>{ov_rows}</tbody></table></div></div>
  <div class="sec-h"><h2>محطات خارج نطاق هذا التحليل</h2><span>{len(nosales)} محطة لا تتوفر لها بيانات مبيعات في لوحة التحليل</span></div>
  <details class="apx"><summary>عرض القائمة — {esc(app_sum)}</summary>
    <div class="tscroll"><table><thead><tr><th>الكود</th><th>المدينة</th><th>المحطة</th><th>النوع</th><th>الموقع</th></tr></thead><tbody>{app_rows}</tbody></table></div>
  </details>
  <footer>{FOOT_METH}</footer>
</main>
</div>
<main class="wrap" id="pages">{SPA_VIEWS}{CMP_HTML}</main>
<script id="cmpdata" type="application/json">{CMP_JSON}</script>
<script>
const hubEl=document.getElementById('hub');
function route(){{
  const h=decodeURIComponent(location.hash.replace(/^#\/?/, ''));
  document.querySelectorAll('.pgview').forEach(p=>p.hidden=true);
  const t=h?document.getElementById('pg-'+h.replace(/\//g,'-')):null;
  if(t){{hubEl.style.display='none';t.hidden=false;document.title=t.dataset.title+' — تحليل الموقع والمبيعات';window.scrollTo(0,0);}}
  else{{hubEl.style.display='';document.title='درب · تحليل المحطات والمبيعات — دليل المحطات';if(h)history.replaceState(null,'','#/');}}
}}
window.addEventListener('hashchange',route);
const chips=document.querySelectorAll('.chip');const q=document.getElementById('q');
let region='*';
function apply(){{
  const t=(q.value||'').trim();
  document.querySelectorAll('#cards .scard').forEach(s=>{{
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
route();
</script>
{CMP_SCRIPT}
{EDITBAR}
</body>
</html>'''
open('location-analysis.html', 'w', encoding='utf-8').write(hub)
print('hub + %d pages written' % len(ORDER))
