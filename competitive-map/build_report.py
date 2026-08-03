# -*- coding: utf-8 -*-
"""يبني تقرير الخريطة التنافسية التفاعلي (HTML مستقل بالكامل)."""
import json, math

geo = json.load(open("geo.json", encoding="utf-8"))
try:
    pois = json.load(open("pois.json", encoding="utf-8"))
except FileNotFoundError:
    pois = {}          # يُملأ تلقائياً بعد تشغيل collect_pois.py

DATA = json.dumps({"geo": geo, "pois": pois}, ensure_ascii=False)

HTML = """<title>درب · الخريطة التنافسية لمواقع مكة المكرمة</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root{
  --paper:#FBF6EF; --paper-2:#F3E9DC; --ink:#2A1D14; --ink-2:#6E5A48; --ink-3:#9A8674;
  --line:#E4D6C4; --surface:#FFFFFF;
  --amber:#E8760C; --amber-2:#C85E05; --amber-soft:#FBE3C6;
  --green:#1B7A4B; --green-2:#4E9E74; --rose:#C6486B; --gold:#C79A3A; --blue:#2F6F9F;
  --shadow:0 18px 40px -22px rgba(52,28,10,.55); --r:16px;
}
@media (prefers-color-scheme:dark){:root{
  --paper:#17100A; --paper-2:#1F150D; --ink:#F4E9DB; --ink-2:#C7B49E; --ink-3:#9A836C;
  --line:#332417; --surface:#211710; --amber:#F59A2E; --amber-2:#E8760C; --amber-soft:#3A2614;
  --green-2:#5FB689; --rose:#E27795; --gold:#D9B45B; --blue:#7FB2D8;
  --shadow:0 18px 44px -20px rgba(0,0,0,.7);}}
:root[data-theme="light"]{--paper:#FBF6EF;--paper-2:#F3E9DC;--ink:#2A1D14;--ink-2:#6E5A48;--ink-3:#9A8674;
  --line:#E4D6C4;--surface:#FFFFFF;--amber:#E8760C;--amber-soft:#FBE3C6;--green-2:#4E9E74;--rose:#C6486B;--gold:#C79A3A;--blue:#2F6F9F}
:root[data-theme="dark"]{--paper:#17100A;--paper-2:#1F150D;--ink:#F4E9DB;--ink-2:#C7B49E;--ink-3:#9A836C;
  --line:#332417;--surface:#211710;--amber:#F59A2E;--amber-soft:#3A2614;--green-2:#5FB689;--rose:#E27795;--gold:#D9B45B;--blue:#7FB2D8}
*{box-sizing:border-box}
body{margin:0;direction:rtl;background:var(--paper);color:var(--ink);
  font-family:"Tahoma","Segoe UI","Noto Sans Arabic",system-ui,sans-serif;line-height:1.6}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px}
h1,h2,h3{line-height:1.2;margin:0;text-wrap:balance}
.tnum{font-variant-numeric:tabular-nums}
.toggle{position:fixed;inset-block-start:14px;inset-inline-start:14px;z-index:40;background:var(--surface);
  color:var(--ink-2);border:1px solid var(--line);border-radius:100px;padding:7px 14px;font:inherit;
  font-size:13px;cursor:pointer;box-shadow:var(--shadow)}
.toggle:hover{color:var(--amber)}

header.hero{background:linear-gradient(140deg,#3A2416,#241209 60%,#120A05);color:#F7EEDF;padding:54px 0 46px;position:relative;overflow:hidden}
header.hero::after{content:"";position:absolute;inset-block-end:-60px;inset-inline-start:-40px;width:280px;height:280px;
  border-radius:50%;background:radial-gradient(circle,rgba(232,118,12,.34),transparent 68%)}
.eyebrow{font-size:13px;letter-spacing:.12em;color:var(--amber);margin-bottom:12px}
header.hero h1{font-size:clamp(26px,4.4vw,40px)}
header.hero p{margin:14px 0 0;color:#D9C7B0;max-width:64ch}

section{padding:42px 0}
.sec-title{display:flex;align-items:baseline;gap:12px;margin-bottom:20px}
.sec-title h2{font-size:clamp(19px,2.6vw,25px)}
.sec-title span{color:var(--ink-3);font-size:13px}

.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(168px,1fr));gap:14px}
.kpi{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:18px}
.kpi b{display:block;font-size:27px;color:var(--amber);font-variant-numeric:tabular-nums}
.kpi span{font-size:13px;color:var(--ink-2)}

/* ====== الخريطة ====== */
.maplayout{display:grid;grid-template-columns:1fr 320px;gap:18px;align-items:start}
@media(max-width:900px){.maplayout{grid-template-columns:1fr}}
.mapbox{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);
  padding:12px;box-shadow:var(--shadow);overflow:hidden}
svg.map{width:100%;height:auto;display:block;touch-action:none;cursor:grab}
svg.map text{pointer-events:none;user-select:none}
svg.map:active{cursor:grabbing}
.legend{display:flex;flex-wrap:wrap;gap:14px;margin-top:12px;padding-top:12px;border-top:1px solid var(--line);font-size:12.5px;color:var(--ink-2)}
.legend i{width:11px;height:11px;border-radius:50%;display:inline-block;margin-inline-end:6px;vertical-align:-1px}
.ctrls{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}
.ctrls button{background:var(--paper-2);border:1px solid var(--line);color:var(--ink-2);border-radius:100px;
  padding:6px 14px;font:inherit;font-size:12.5px;cursor:pointer}
.ctrls button:hover{border-color:var(--amber);color:var(--amber)}
.ctrls button[aria-pressed="true"]{background:var(--amber);border-color:var(--amber);color:#fff}

.panel{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:18px;position:sticky;top:16px}
.panel h3{font-size:18px;color:var(--amber)}
.panel .code{font-size:12px;color:var(--ink-3);letter-spacing:.08em}
.panel dl{margin:14px 0 0;display:grid;grid-template-columns:auto 1fr;gap:7px 12px;font-size:13.5px}
.panel dt{color:var(--ink-3)}
.panel dd{margin:0;font-variant-numeric:tabular-nums}
.panel .go{display:inline-block;margin-top:15px;background:var(--amber);color:#fff;text-decoration:none;
  border-radius:100px;padding:8px 17px;font-size:13px}
.hint{color:var(--ink-3);font-size:13px;margin-top:10px}

/* ====== الجداول ====== */
.tablewrap{overflow-x:auto;border:1px solid var(--line);border-radius:var(--r);background:var(--surface)}
table{border-collapse:collapse;width:100%;font-size:13.5px;min-width:560px}
th,td{padding:11px 13px;text-align:right;border-bottom:1px solid var(--line);white-space:nowrap}
thead th{background:var(--paper-2);color:var(--ink-2);font-weight:600;position:sticky;top:0}
tbody tr:last-child td{border-bottom:0}
td.num{font-variant-numeric:tabular-nums}
.self{color:var(--ink-3)}
.hot{background:var(--amber-soft);color:var(--amber-2);font-weight:700;border-radius:6px}

/* ====== البطاقات ====== */
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:16px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:20px}
.card h3{font-size:17px}
.card .code{font-size:11.5px;color:var(--ink-3);letter-spacing:.09em;margin-bottom:9px}
.chip{display:inline-block;font-size:11.5px;border-radius:100px;padding:3px 11px;margin:0 0 9px}
.chip.cluster{background:var(--amber-soft);color:var(--amber-2)}
.chip.solo{background:rgba(78,158,116,.16);color:var(--green-2)}
.card ul{margin:11px 0 0;padding-inline-start:18px;font-size:13px;color:var(--ink-2)}
.card li{margin-bottom:4px}
.bar{height:7px;border-radius:100px;background:var(--paper-2);margin:9px 0 4px;overflow:hidden}
.bar>i{display:block;height:100%;background:var(--amber);border-radius:100px}

.note{background:var(--paper-2);border:1px solid var(--line);border-inline-start:4px solid var(--gold);
  border-radius:var(--r);padding:18px 20px;font-size:13.5px;color:var(--ink-2)}
.note b{color:var(--ink)}
.note ol{margin:10px 0 0;padding-inline-start:20px}
footer{padding:34px 0;color:var(--ink-3);font-size:12.5px;border-top:1px solid var(--line);text-align:center}
</style>

<button class="toggle" id="tg">◐ تبديل السمة</button>

<header class="hero"><div class="wrap">
  <div class="eyebrow">درب · دراسة مواقع</div>
  <h1>الخريطة التنافسية لمحطات مكة المكرمة</h1>
  <p>تحليل جغرافي لخمسة مواقع تشغيلية: المسافات البينية، تداخل نطاقات الخدمة،
     والقرب من الحرم والمشاعر المقدسة — مع إطار حصر المنشآت المحيطة بكل موقع.</p>
</div></header>

<div class="wrap">

<section>
  <div class="sec-title"><h2>المؤشرات العامة</h2></div>
  <div class="kpis" id="kpis"></div>
</section>

<section>
  <div class="sec-title"><h2>خريطة المواقع</h2><span>اضغط على أي محطة لعرض تفاصيلها · اسحب للتحريك</span></div>
  <div class="maplayout">
    <div class="mapbox">
      <svg class="map" id="svg" viewBox="0 0 900 700" role="img" aria-label="خريطة مواقع محطات درب بمكة المكرمة"></svg>
      <div class="ctrls">
        <button data-r="1">نطاق ١ كم</button>
        <button data-r="3" aria-pressed="true">نطاق ٣ كم</button>
        <button data-r="5">نطاق ٥ كم</button>
        <button id="reset">إعادة الضبط</button>
      </div>
      <div class="legend">
        <span><i style="background:#E8760C"></i>محطة درب</span>
        <span><i style="background:#1B7A4B"></i>المسجد الحرام</span>
        <span><i style="background:#C79A3A"></i>المشاعر المقدسة</span>
        <span><i style="background:#C6486B"></i>نطاقات متداخلة</span>
      </div>
    </div>
    <aside class="panel" id="panel"></aside>
  </div>
</section>

<section>
  <div class="sec-title"><h2>مصفوفة المسافات البينية</h2><span>بالكيلومترات · المظلّل = تداخل مرتفع (أقل من ٥ كم)</span></div>
  <div class="tablewrap"><table id="matrix"></table></div>
</section>

<section>
  <div class="sec-title"><h2>قراءة تنافسية لكل موقع</h2></div>
  <div class="cards" id="cards"></div>
</section>

<section>
  <div class="sec-title"><h2>حصر المنشآت المحيطة</h2><span>تأجير السيارات · مكاتب الحج والعمرة · الشركات الحكومية والخاصة</span></div>
  <div id="inv"></div>
</section>

</div>
<footer>درب · وثيقة داخلية للتخطيط التشغيلي والتجاري — مكة المكرمة</footer>

<script>
const DATA = __DATA__;
const G = DATA.geo, POIS = DATA.pois || {};
const S = G.stations, L = G.landmarks;
const CLUSTER = new Set(S.filter(s => s.nearest_km < 5).map(s => s.code));
let radius = 3, active = S[0].code;

/* ---------- المؤشرات ---------- */
const minPair = Math.min(...S.map(s => s.nearest_km));
const avgHaram = (S.reduce((a,s)=>a+s.landmarks[0].km,0)/S.length).toFixed(1);
document.getElementById('kpis').innerHTML = [
  [S.length, 'مواقع تشغيلية'],
  [CLUSTER.size, 'مواقع ضمن تجمّع متداخل'],
  [minPair.toFixed(2)+' كم', 'أقصر مسافة بين محطتين'],
  [avgHaram+' كم', 'متوسط البعد عن الحرم'],
].map(([b,s])=>`<div class="kpi"><b class="tnum">${b}</b><span>${s}</span></div>`).join('');

/* ---------- الإسقاط الجغرافي ---------- */
const pts = S.concat(L);
const latC = pts.reduce((a,p)=>a+p.lat,0)/pts.length;
const kx = 111.320*Math.cos(latC*Math.PI/180), ky = 110.574;   // كم لكل درجة
const X = p => p.lng*kx, Y = p => -p.lat*ky;                    // كم مستوية
const xs = pts.map(X), ys = pts.map(Y);
const pad = 6.5;                                                 // هامش بالكيلومتر
const x0 = Math.min(...xs)-pad, x1 = Math.max(...xs)+pad;
const y0 = Math.min(...ys)-pad, y1 = Math.max(...ys)+pad;
const W = 900, H = 700;
const scale = Math.min(W/(x1-x0), H/(y1-y0));                    // بكسل لكل كم
const ox = (W-(x1-x0)*scale)/2, oy = (H-(y1-y0)*scale)/2;
const px = p => (X(p)-x0)*scale + ox, py = p => (Y(p)-y0)*scale + oy;
const esc = t => String(t).replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));

/* ---------- رسم الخريطة ---------- */
function draw(){
  const r = radius*scale;
  let g = '';
  // شبكة خلفية
  g += `<rect width="${W}" height="${H}" fill="var(--paper-2)" rx="12"/>`;
  for(let i=0;i<=W;i+=45) g += `<line x1="${i}" y1="0" x2="${i}" y2="${H}" stroke="var(--line)" stroke-width=".6"/>`;
  for(let i=0;i<=H;i+=45) g += `<line x1="0" y1="${i}" x2="${W}" y2="${i}" stroke="var(--line)" stroke-width=".6"/>`;

  // نطاقات الخدمة
  S.forEach(s=>{
    const hot = S.some(o=>o.code!==s.code && dist(s,o) < radius*2);
    g += `<circle cx="${px(s)}" cy="${py(s)}" r="${r}" fill="${hot?'rgba(198,72,107,.13)':'rgba(232,118,12,.11)'}"
            stroke="${hot?'#C6486B':'#E8760C'}" stroke-width="1.1" stroke-dasharray="5 4"/>`;
  });
  // خطوط الربط داخل التجمّع
  S.forEach((a,i)=>S.slice(i+1).forEach(b=>{
    const d = dist(a,b);
    if(d < 5) g += `<line x1="${px(a)}" y1="${py(a)}" x2="${px(b)}" y2="${py(b)}"
        stroke="#C6486B" stroke-width="1.6" stroke-dasharray="3 3" opacity=".75"/>
      <text x="${(px(a)+px(b))/2}" y="${(py(a)+py(b))/2-7}" fill="#C6486B" font-size="12"
        text-anchor="middle">${d.toFixed(2)} كم</text>`;
  }));
  // المعالم
  L.forEach(l=>{
    const c = l.kind==='haram' ? '#1B7A4B' : '#C79A3A';
    g += `<g><rect x="${px(l)-7}" y="${py(l)-7}" width="14" height="14" rx="3" transform="rotate(45 ${px(l)} ${py(l)})"
        fill="${c}" opacity=".92"/>
      <text x="${px(l)}" y="${py(l)+25}" fill="var(--ink-2)" font-size="13" text-anchor="middle">${esc(l.name)}</text></g>`;
  });
  // المحطات — مع توزيع التسميات لتفادي التراكب عند تقارب المواقع
  const placed = [];
  const fits = (x,y,w) => !placed.some(b =>
    Math.abs(b.x-x) < (b.w+w)/2 + 4 && Math.abs(b.y-y) < 19);
  S.forEach(s=>{
    const on = s.code===active;
    const cx = px(s), cy = py(s);
    const w = s.name.length*8.6 + 10;
    // نجرّب: أعلى، ثم أسفل، ثم إزاحات متدرجة
    let ly = null;
    for(const dy of [-21, 40, -44, 63, -67, 86]){
      if(fits(cx, cy+dy, w)){ ly = cy+dy; break; }
    }
    if(ly === null) ly = cy - 21;
    placed.push({x:cx, y:ly, w});
    const codeY = ly < cy ? ly + 15 : ly + 15;   // الرمز أسفل الاسم دائماً
    placed.push({x:cx, y:codeY, w:56});
    g += `<g class="stn" data-code="${s.code}" style="cursor:pointer">
      ${on?`<circle cx="${cx}" cy="${cy}" r="19" fill="#E8760C" opacity=".22"/>`:''}
      <line x1="${cx}" y1="${cy}" x2="${cx}" y2="${ly < cy ? ly+5 : ly-11}"
        stroke="var(--ink-3)" stroke-width="1" opacity=".55"/>
      <circle cx="${cx}" cy="${cy}" r="${on?10:8}" fill="#E8760C" stroke="#fff" stroke-width="2.4"/>
      <text x="${cx}" y="${ly}" fill="var(--ink)" font-size="14" font-weight="700"
        text-anchor="middle">${esc(s.name)}</text>
      <text x="${cx}" y="${codeY}" fill="var(--ink-3)" font-size="11.5"
        text-anchor="middle">${s.code}</text></g>`;
  });
  // مقياس الرسم + اتجاه الشمال
  const bar = 5*scale;
  g += `<g transform="translate(38,${H-42})">
    <line x1="0" y1="0" x2="${bar}" y2="0" stroke="var(--ink-2)" stroke-width="2.4"/>
    <line x1="0" y1="-5" x2="0" y2="5" stroke="var(--ink-2)" stroke-width="2.4"/>
    <line x1="${bar}" y1="-5" x2="${bar}" y2="5" stroke="var(--ink-2)" stroke-width="2.4"/>
    <text x="${bar/2}" y="-11" fill="var(--ink-2)" font-size="12.5" text-anchor="middle">٥ كم</text></g>`;
  g += `<g transform="translate(${W-46},44)">
    <path d="M0,-19 L7,9 L0,3 L-7,9 Z" fill="var(--ink-2)"/>
    <text x="0" y="25" fill="var(--ink-2)" font-size="12.5" text-anchor="middle">ش</text></g>`;
  document.getElementById('svg').innerHTML = g;
  document.querySelectorAll('.stn').forEach(el =>
    el.addEventListener('click', () => { active = el.dataset.code; draw(); panel(); }));
}
function dist(a,b){
  const R=6371.0088, t=x=>x*Math.PI/180;
  const dp=t(b.lat-a.lat), dl=t(b.lng-a.lng);
  const h=Math.sin(dp/2)**2+Math.cos(t(a.lat))*Math.cos(t(b.lat))*Math.sin(dl/2)**2;
  return 2*R*Math.asin(Math.sqrt(h));
}

/* ---------- اللوحة الجانبية ---------- */
function panel(){
  const s = S.find(x=>x.code===active);
  const inv = POIS[s.code] || null;
  document.getElementById('panel').innerHTML = `
    <div class="code">${s.code}</div><h3>${esc(s.name)}</h3>
    <dl>
      <dt>الإحداثيات</dt><dd>${s.lat.toFixed(5)}, ${s.lng.toFixed(5)}</dd>
      <dt>أقرب محطة</dt><dd>${esc(s.nearest)} — ${s.nearest_km} كم</dd>
      <dt>تداخل ${radius} كم</dt><dd>${s.overlap[radius]}%</dd>
      ${s.landmarks.map(l=>`<dt>${esc(l.name)}</dt><dd>${l.km} كم ${esc(l.dir)}</dd>`).join('')}
      ${inv ? Object.entries(inv.counts||{}).map(([k,v])=>`<dt>${esc(k)}</dt><dd>${v}</dd>`).join('')
            : '<dt>الحصر الميداني</dt><dd>—</dd>'}
    </dl>
    <a class="go" href="${s.maps_url}" target="_blank" rel="noopener">فتح في خرائط جوجل ↗</a>
    ${inv ? '' : '<p class="hint">بيانات المنشآت المحيطة لم تُجمَع بعد — انظر قسم الحصر أدناه.</p>'}`;
}

/* ---------- مصفوفة المسافات ---------- */
(function(){
  const codes = S.map(s=>s.code);
  let h = '<thead><tr><th>من \\ إلى</th>' + S.map(s=>`<th>${esc(s.name)}<br><span class="self">${s.code}</span></th>`).join('') + '</tr></thead><tbody>';
  S.forEach(a=>{
    h += `<tr><th>${esc(a.name)} <span class="self">${a.code}</span></th>`;
    codes.forEach(c=>{
      if(c===a.code){ h += '<td class="num self">—</td>'; return; }
      const d = G.matrix[a.code+'|'+c];
      h += `<td class="num"><span class="${d<5?'hot':''}">${d.toFixed(2)}</span></td>`;
    });
    h += '</tr>';
  });
  document.getElementById('matrix').innerHTML = h + '</tbody>';
})();

/* ---------- بطاقات القراءة التنافسية ---------- */
document.getElementById('cards').innerHTML = S.map(s=>{
  const isC = CLUSTER.has(s.code);
  const ov = s.overlap['3'];
  return `<div class="card">
    <div class="code">${s.code}</div><h3>${esc(s.name)}</h3>
    <span class="chip ${isC?'cluster':'solo'}">${isC?'ضمن تجمّع متنافس':'موقع منفرد النطاق'}</span>
    <div class="bar"><i style="width:${ov}%"></i></div>
    <div style="font-size:12.5px;color:var(--ink-3)">تداخل نطاق ٣ كم مع أقرب محطة: <b class="tnum">${ov}%</b></div>
    <ul>
      <li>أقرب محطة: ${esc(s.neighbors[0].name)} (${s.neighbors[0].km} كم ${esc(s.neighbors[0].dir)})</li>
      <li>المسجد الحرام: ${s.landmarks[0].km} كم ${esc(s.landmarks[0].dir)}</li>
      <li>أقرب مشعر: ${esc(s.landmarks.slice(1).sort((a,b)=>a.km-b.km)[0].name)}
          (${s.landmarks.slice(1).sort((a,b)=>a.km-b.km)[0].km} كم)</li>
      <li>${isC
        ? 'يتطلب تمييزاً في الخدمات لتفادي تآكل الحصة مع المحطات المجاورة.'
        : 'يخدم نطاقاً حصرياً دون منافسة داخلية من محطات درب.'}</li>
    </ul></div>`;
}).join('');

/* ---------- قسم الحصر ---------- */
(function(){
  const cats = ['محطات وقود منافسة','تأجير السيارات','مكاتب الحج والعمرة','الشركات الحكومية والخاصة'];
  const has = Object.keys(POIS).length > 0;
  const el = document.getElementById('inv');
  if(has){
    let h = '<div class="tablewrap"><table><thead><tr><th>المحطة</th>' +
      cats.map(c=>`<th>${c}</th>`).join('') + '<th>الإجمالي</th></tr></thead><tbody>';
    S.forEach(s=>{
      const c = (POIS[s.code]||{}).counts || {};
      const tot = cats.reduce((a,k)=>a+(c[k]||0),0);
      h += `<tr><th>${esc(s.name)} <span class="self">${s.code}</span></th>` +
        cats.map(k=>`<td class="num">${c[k]||0}</td>`).join('') +
        `<td class="num"><b>${tot}</b></td></tr>`;
    });
    el.innerHTML = h + '</tbody></table></div>';
  } else {
    el.innerHTML = `<div class="note">
      <b>الحصر الميداني لم يُنفَّذ بعد — مصدر البيانات غير متاح حالياً.</b>
      <p style="margin:9px 0 0">تعذّر سحب بيانات المنشآت المحيطة (تأجير السيارات، مكاتب الحج والعمرة،
      الشركات الحكومية والخاصة) لسببين تقنيين خارج نطاق هذا التقرير:</p>
      <ol>
        <li>حساب Apify تجاوز الحد الشهري للاستخدام (Monthly usage hard limit exceeded).</li>
        <li>نطاق <span dir="ltr">overpass-api.de</span> (بيانات OpenStreetMap) محجوب بسياسة الشبكة للجلسة.</li>
      </ol>
      <p style="margin:9px 0 0">جميع الأدوات جاهزة: بمجرد رفع حد الاستخدام، يُشغَّل
      <span dir="ltr"><code>collect_pois.py</code></span> فيُنتج <span dir="ltr"><code>pois.json</code></span>
      وتُملأ هذه الجداول وبطاقات المحطات وملف الإكسل تلقائياً دون أي تعديل يدوي.</p></div>`;
  }
})();

/* ---------- التفاعل ---------- */
document.querySelectorAll('.ctrls button[data-r]').forEach(b =>
  b.addEventListener('click', () => {
    radius = +b.dataset.r;
    document.querySelectorAll('.ctrls button[data-r]').forEach(x =>
      x.setAttribute('aria-pressed', x===b ? 'true' : 'false'));
    draw(); panel();
  }));
document.getElementById('reset').addEventListener('click', () => {
  const s = document.getElementById('svg');
  s.setAttribute('viewBox', '0 0 900 700'); active = S[0].code; draw(); panel();
});

/* سحب وتكبير الخريطة */
(function(){
  const svg = document.getElementById('svg');
  let vb = [0,0,900,700], drag = null;
  const apply = () => svg.setAttribute('viewBox', vb.join(' '));
  svg.addEventListener('pointerdown', e => {
    if(e.target.closest('.stn')) return;          // لا نبدأ السحب فوق دبوس محطة حتى لا نبتلع النقرة
    drag = {x:e.clientX, y:e.clientY, vb:vb.slice()};
    svg.setPointerCapture(e.pointerId);
  });
  svg.addEventListener('pointermove', e => {
    if(!drag) return;
    const k = vb[2]/svg.clientWidth;
    vb = [drag.vb[0]-(e.clientX-drag.x)*k, drag.vb[1]-(e.clientY-drag.y)*k, vb[2], vb[3]];
    apply();
  });
  ['pointerup','pointercancel','pointerleave'].forEach(t => svg.addEventListener(t, () => drag = null));
  svg.addEventListener('wheel', e => {
    e.preventDefault();
    const f = e.deltaY > 0 ? 1.12 : 1/1.12;
    vb = [vb[0]+vb[2]*(1-f)/2, vb[1]+vb[3]*(1-f)/2, vb[2]*f, vb[3]*f];
    apply();
  }, {passive:false});
})();

/* السمة */
document.getElementById('tg').addEventListener('click', () => {
  const cur = document.documentElement.getAttribute('data-theme') ||
    (matchMedia('(prefers-color-scheme:dark)').matches ? 'dark' : 'light');
  document.documentElement.setAttribute('data-theme', cur==='dark' ? 'light' : 'dark');
  draw();
});

draw(); panel();
</script>"""

open("index.html", "w", encoding="utf-8").write(HTML.replace("__DATA__", DATA))
print("index.html written:", len(HTML))
