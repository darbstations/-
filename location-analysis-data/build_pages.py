# -*- coding: utf-8 -*-
"""Build hub (location-analysis.html) + one standalone page per station (stations/CODE.html)."""
import json, html, os, statistics

A = json.load(open('analysis.json'))
try:
    ACT = json.load(open('actual_daily.json'))
except FileNotFoundError:
    ACT = {}
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
.darblogo{height:64px;width:auto;display:block;filter:drop-shadow(0 4px 14px rgba(0,0,0,.25))}
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

FONTFACE = open('fontface.css', encoding='utf-8').read()
FONTS = f"""<style>{FONTFACE}</style>"""

LOGO_SVG = """<svg class="darblogo" viewBox="0 0 640 244" role="img" aria-label="شعار درب Darb"><g>
<rect x="11" y="11" width="618" height="222" rx="111" fill="#6D6E71" stroke="#F6851F" stroke-width="17"/>
<path d="M 386 80 L 512 80 Q 558 80 558 126 L 558 142" fill="none" stroke="#F6851F" stroke-width="35" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M 549 174 C 516 202 446 212 380 194" fill="none" stroke="#F6851F" stroke-width="35" stroke-linecap="round"/>
<text x="232" y="112" font-family="'DIN Next Arabic'" font-weight="700" font-size="72" text-anchor="middle" fill="#fff" direction="rtl">درب</text>
<text x="232" y="182" font-family="'DIN Next Arabic'" font-weight="700" font-size="50" letter-spacing="3" text-anchor="middle" fill="#fff" direction="ltr">Darb</text>
</g></svg>"""

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
    period = f"{len(m['months'])} أشهر" if m['nmonths'] < 6 else 'النصف الأول 2026'
    maps_url = x.get('loc', '#')

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
        <span class="cls c-hd">حي {esc(hood)}</span>
        <span class="cls {cls_cl}">{esc(cls)}</span><span class="cls c-st">{stt}</span>
      </div>
      <div class="smeta">
        <span>📍 {esc(m['region'])}</span>
        {stars(g['rating']) if g else ''}
        <a href="{esc(maps_url)}" target="_blank" rel="noopener">افتح في خرائط جوجل ↗</a>
      </div>
      <div class="saddr">{esc(g['address']) if g else ''}{(' — ' + esc(m['note'])) if m['note'] else ''}</div>
    </div>'''

    mapcard = comp_map(a)
    grid = f'''
    {mapcard}
    <div class="agrid">
      <div class="card"><div class="ct"><h3>بيرسونا العملاء</h3><div class="leg">مشتقة من مزيج الوقود والأوقات والدفع</div></div>{pers}</div>
      <div class="card"><div class="ct"><h3>تحليل SWOT</h3><div class="leg">مبيعات + موقع + منافسة</div></div>{swot}</div>
      <div class="card"><div class="ct"><h3>تحليل PEST</h3><div class="leg">بيئة {esc(m['region'])} الكلية</div></div>{pest}</div>
      {compb}
    </div>'''
    return head + kpis + sig + grid

MONTH_AR = {'2026-01':'يناير','2026-02':'فبراير','2026-03':'مارس','2026-04':'أبريل','2026-05':'مايو','2026-06':'يونيو'}
WD_AR = ['الإثنين','الثلاثاء','الأربعاء','الخميس','الجمعة','السبت','الأحد']
import datetime as _dt

def mini_head(a):
    m, g = a['metrics'], a['geo']
    return f'''<div class="mini-head"><span class="badge">{m['code']}</span><h2>درب {esc(m['name'])}</h2>
    <span class="cls c-hd">حي {esc(hood_of(a))}</span>
    <span class="rg">📍 {esc(m['region'])}</span>{f'<span class="stars">★ {g["rating"]}</span>' if g else ''}</div>'''

def tabs_html(code, active, mode):
    items = [('main','التحليل الكامل'),('monthly','المبيعات الشهرية'),('daily','المبيعات اليومية')]
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

def monthly_body(a):
    m = a['metrics']; code = m['code']
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
    <div class="dnote">(*) التغير محسوب على متوسط الإيراد اليومي لكل شهر لتحييد الأشهر الجزئية. المصدر: لوحة مبيعات درب H1 2026.</div>'''

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

# ---------------- per-station pages ----------------
for idx, a in enumerate(ORDER):
    m = a['metrics']; code = m['code']
    prv = CODES[idx-1] if idx > 0 else None
    nxt = CODES[idx+1] if idx < len(CODES)-1 else None
    opts = ''.join(
        f'<option value="{c}.html"{" selected" if c==code else ""}>{esc(A[c]["metrics"]["name"])} — {c} ({esc(A[c]["metrics"]["region"])})</option>'
        for c in CODES)
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
<title>درب {esc(m['name'])} {code} — حي {esc(hood_of(a))} · تحليل الموقع والمبيعات</title>
{FONTS}
<style>{CSS}</style>
</head>
<body>
<header>
  <div class="wrap">
    <div class="brand">
      <div class="mark"><a href="../location-analysis.html">{LOGO_SVG}</a></div>
      <div class="hd-title"><h1>تحليل الموقع والمبيعات — درب {esc(m['name'])} <span style="color:var(--gold1);font-family:'DIN Next Arabic'">{code}</span></h1>
      <p>حي {esc(hood_of(a))} · {esc(m['region'])} · المرتبة {m['rank_drev']} من {m['n_total']} بالإيراد اليومي · النصف الأول 2026</p></div>
    </div>
  </div>
</header>
<main class="wrap" style="padding-top:20px">
  {nav}
  {tabs_html(code, 'main', 'file').replace('class="tab', 'data-v="main" class="tab', 1).replace('href="#monthly"','href="#monthly" data-v="monthly"').replace('href="#daily"','href="#daily" data-v="daily"')}
  <div class="pgview" id="v-main"><section class="station">{station_body(a)}</section></div>
  <div class="pgview" id="v-monthly" hidden>{mini_head(a)}{monthly_body(a)}</div>
  <div class="pgview" id="v-daily" hidden>{mini_head(a)}{daily_body(a)}</div>
  <footer>{FOOT_METH}</footer>
</main>
<script>
function route(){{
  const h=location.hash.replace('#','');
  const k=(h==='monthly'||h==='daily')?h:'main';
  document.querySelectorAll('.pgview').forEach(p=>p.hidden=true);
  document.getElementById('v-'+k).hidden=false;
  document.querySelectorAll('.tab').forEach(t=>t.classList.toggle('on',(t.dataset.v||'main')===k));
  window.scrollTo(0,0);
}}
window.addEventListener('hashchange',route);route();
</script>
</body>
</html>'''
    open(f'stations/{code}.html', 'w', encoding='utf-8').write(page)

# ---------------- hub page ----------------
tot_rev = sum(a['metrics']['revenue'] for a in ORDER)
tot_vis = sum(a['metrics']['visits'] for a in ORDER)
avg_rt = statistics.mean(a['geo']['rating'] for a in ORDER if a['geo'])
ncomp = COMP.get('_meta', {}).get('unique_competitors')

chips = '<button class="chip on" data-r="*"><span class="nm">الكل</span><span class="code">' + str(len(ORDER)) + '</span></button>'
for r in REGIONS:
    n = sum(1 for a in ORDER if a['metrics']['region'] == r)
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
      <div class="r2"><span>حي {esc(hood)}</span><span>📍 {esc(m['region'])}</span><span class="cls {cls_cl}">{esc(cls)}</span>{f'<span class="stars">★ {g["rating"]}</span>' if g else ''}</div>
      <div class="r3"><span>إيراد يومي <b>{n0(m['daily_rev'])}</b> ر.س</span><span>#{i} {gh}</span></div>
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
      <td>{(str(c['n']) + ('*' if c.get('thin') else '')) if c else '—'}</td><td>{g['rating'] if g else '—'}</td></tr>'''

nosales = [r for r in XL if r['num'] not in A]
from collections import Counter
bycity = Counter(r['city'].strip() for r in nosales)
app_sum = '، '.join(f"{c} ({n})" for c, n in bycity.most_common())
app_rows = ''.join(f"<tr><td>{esc(r['num'])}</td><td>{esc(r['city'])}</td><td>{esc(r['name'])}</td>"
                   f"<td>{'تشغيل' if r['status']=='Operation' else 'فرنشايز'}</td>"
                   f"<td><a href='{esc(r['loc'])}' target='_blank' rel='noopener'>الموقع ↗</a></td></tr>" for r in nosales)

def spa_view(idx, a):
    m = a['metrics']; code = m['code']
    prv = CODES[idx-1] if idx > 0 else None
    nxt = CODES[idx+1] if idx < len(CODES)-1 else None
    opts = ''.join(
        f'<option value="#/{c}"{" selected" if c==code else ""}>{esc(A[c]["metrics"]["name"])} — {c} ({esc(A[c]["metrics"]["region"])})</option>'
        for c in CODES)
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
      f'''<div class="pgview" id="pg-{code}" data-title="درب {esc(m['name'])} {code} · حي {esc(hood_of(a))}" hidden>
      {nav}{tabs_html(code, 'main', 'spa')}
      <section class="station">{station_body(a)}</section>{bottom}</div>'''
      f'''<div class="pgview" id="pg-{code}-monthly" data-title="درب {esc(m['name'])} {code} · المبيعات الشهرية" hidden>
      {nav}{tabs_html(code, 'monthly', 'spa')}{mini_head(a)}{monthly_body(a)}{bottom}</div>'''
      f'''<div class="pgview" id="pg-{code}-daily" data-title="درب {esc(m['name'])} {code} · المبيعات اليومية" hidden>
      {nav}{tabs_html(code, 'daily', 'spa')}{mini_head(a)}{daily_body(a)}{bottom}</div>'''
    )

SPA_VIEWS = ''.join(spa_view(i, a) for i, a in enumerate(ORDER))

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
      <p>النصف الأول 2026 · {len(ORDER)} محطة مشمولة بالبيانات · اختر محطة لفتح صفحتها الكاملة</p></div>
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
</body>
</html>'''
open('location-analysis.html', 'w', encoding='utf-8').write(hub)
print('hub + %d pages written' % len(ORDER))
