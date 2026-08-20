const {chromium} = require('playwright-core');
(async () => {
  const b = await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    args:['--no-sandbox','--disable-dev-shm-usage','--font-render-hinting=none']});
  const p = await b.newPage();
  await p.goto('file://' + process.cwd() + '/' + process.argv[2], {waitUntil:'networkidle'});
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(1200);
  const bad = await p.evaluate(() => {
    const el=document.body; const r=el.getBoundingClientRect();
    return {w: document.documentElement.scrollWidth, dir: getComputedStyle(el).direction,
            font: getComputedStyle(document.querySelector('h1')).fontFamily};
  });
  console.log('render check:', JSON.stringify(bad));
  await p.pdf({path: process.argv[3], format:'A4', printBackground:true,
    margin:{top:'15mm',bottom:'16mm',left:'14mm',right:'14mm'},
    displayHeaderFooter:true,
    headerTemplate:'<div></div>',
    footerTemplate:`<div style="width:100%;font-size:7.5pt;color:#9A8674;padding:0 14mm;
      font-family:sans-serif;display:flex;justify-content:space-between;direction:rtl">
      <span>درب · كراسة مواقع المحطات</span>
      <span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>`});
  await b.close();
})();
