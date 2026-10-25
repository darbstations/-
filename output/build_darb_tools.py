import json
O='/home/user/-/output/'
pages=[('explorer','مستكشف المحطات','darb_station_explorer.html'),('packages','الباقات','darb_packages_plain.html'),('restaurants','الباقات مع خصومات المطاعم','darb_packages_restaurants.html')]
HEAD='<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><style>html{color-scheme:light}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style></head><body>'
docs={k:HEAD+open(O+f).read()+'</body></html>' for k,_,f in pages}
js_docs=json.dumps(docs,ensure_ascii=False).replace('</','<\\/')
tabs=''.join(f'<button type="button" role="tab" id="t-{k}" data-k="{k}" aria-selected="false">{n}</button>' for k,n,_ in pages)
frames=''.join(f'<iframe id="f-{k}" title="{n}" hidden></iframe>' for k,n,_ in pages)
html=f'''<title>أدوات درب</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@500;600&family=Readex+Pro:wght@600&display=swap">
<style>
/* Layout: one tab bar on top, each tool in its own full-height frame below */
:root{{--bg:#F6F5F3;--surface:#FFFFFF;--ink:#24201C;--ink2:#6B645C;--line:#E4E0DA;--accent:#E8631A;
  --display:'Readex Pro','IBM Plex Sans Arabic',Tahoma,sans-serif;--body:'IBM Plex Sans Arabic',Tahoma,sans-serif}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#181614;--surface:#221F1C;--ink:#F1ECE6;--ink2:#A89F95;--line:#3A3530;--accent:#F38A4A;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#181614;--surface:#221F1C;--ink:#F1ECE6;--ink2:#A89F95;--line:#3A3530;--accent:#F38A4A;color-scheme:dark}}
html,body{{height:100%}}
body{{background:var(--bg);color:var(--ink);font-family:var(--body);direction:rtl;display:flex;flex-direction:column}}
.bar{{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:8px 16px;padding-inline:16px;padding-block:10px;border-bottom:1px solid var(--line);background:var(--surface)}}
.bar h1{{font-family:var(--display);font-size:18px;margin:0}}
.tabs{{display:flex;flex-wrap:wrap;gap:4px;background:var(--bg);border:1px solid var(--line);border-radius:9px;padding:3px}}
.tabs button{{font:inherit;font-weight:600;border:none;background:transparent;color:var(--ink2);padding:6px 14px;border-radius:7px;cursor:pointer}}
.tabs button[aria-selected="true"]{{background:var(--accent);color:#fff}}
.tabs button:focus-visible{{outline:2px solid var(--accent);outline-offset:1px}}
.stage{{flex:1;min-height:0;position:relative}}
iframe{{position:absolute;inset:0;width:100%;height:100%;border:0;background:var(--bg)}}
</style>
<header class="bar"><h1>أدوات درب</h1><nav class="tabs" role="tablist">{tabs}</nav></header>
<main class="stage">{frames}</main>
<script>
const DOCS={js_docs};
const KEYS={json.dumps([k for k,_,_ in pages])};
function syncTheme(f){{try{{const t=document.documentElement.getAttribute('data-theme');const r=f.contentDocument&&f.contentDocument.documentElement;if(!r)return;t?r.setAttribute('data-theme',t):r.removeAttribute('data-theme');}}catch(e){{}}}}
function show(k){{
  if(!KEYS.includes(k))k=KEYS[0];
  KEYS.forEach(x=>{{const f=document.getElementById('f-'+x),b=document.getElementById('t-'+x),on=x===k;f.hidden=!on;b.setAttribute('aria-selected',on);
    if(on&&!f.dataset.loaded){{f.dataset.loaded='1';f.addEventListener('load',()=>syncTheme(f));f.srcdoc=DOCS[x];}}}});
  try{{history.replaceState(null,'','#'+k)}}catch(e){{}}
  try{{localStorage.setItem('darb-tools-tab',k)}}catch(e){{}}
}}
document.querySelectorAll('.tabs button').forEach(b=>b.addEventListener('click',()=>show(b.dataset.k)));
new MutationObserver(()=>KEYS.forEach(x=>syncTheme(document.getElementById('f-'+x)))).observe(document.documentElement,{{attributes:true,attributeFilter:['data-theme']}});
let start=(location.hash||'').slice(1);if(!KEYS.includes(start)){{try{{start=localStorage.getItem('darb-tools-tab')||''}}catch(e){{start=''}}}}
show(start);
</script>
'''
open(O+'darb_tools.html','w').write(html)
print(len(html))
