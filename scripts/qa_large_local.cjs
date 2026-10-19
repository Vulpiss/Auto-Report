const {chromium} = require(process.env.AUTOREPORT_PLAYWRIGHT_DIR || 'C:/Users/kompu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs = require('fs');
const path = require('path');
(async () => {
  const [url, out] = process.argv.slice(2);
  const specs = JSON.parse(fs.readFileSync(path.join(out, 'specs.json'), 'utf8'));
  const browser = await chromium.launch({channel:'msedge', headless:true});
  const results = [];
  try {
    for (const spec of specs) {
      const context = await browser.newContext({acceptDownloads:true, viewport:{width:1440,height:1000}});
      const page = await context.newPage();
      page.setDefaultTimeout(150000);
      try {
        await page.goto(url);
        await page.getByRole('heading',{name:'Wybierz CSV. Kliknij. Gotowe.'}).waitFor();
        await page.locator('.st-key-easy_upload input[type=file]').setInputFiles(path.join(out, spec.name+'.csv'));
        await page.getByText('Zapamiętany układ kolumn.',{exact:false}).waitFor();
        await page.locator('[data-testid="stStatusWidget"]').waitFor({state:'hidden'});
        const started = Date.now();
        await page.getByRole('button',{name:'Utwórz raport',exact:true}).click();
        await page.getByRole('button',{name:'Pobierz gotowy raport PDF',exact:true}).waitFor();
        await page.locator('[data-testid="stStatusWidget"]').waitFor({state:'hidden'});
        const values = (await page.locator('[data-testid="stMetricValue"]').allTextContents()).slice(0,3);
        const actualMinor = Math.round(Number(values[0].replace(/\s/g,'').replace(',','.'))*100);
        if (actualMinor !== spec.expected_minor || Number(values[1].replace(/\s/g,'')) !== spec.rows || values[2] !== '1,01') throw Error('Metrics mismatch '+JSON.stringify(values));
        const download = page.waitForEvent('download');
        await page.getByRole('button',{name:'Pobierz gotowy raport PDF',exact:true}).click();
        await (await download).saveAs(path.join(out, spec.name+'-exe.pdf'));
        results.push({case:spec.name, result:'PASS', import_analysis_pdf_seconds:(Date.now()-started)/1000, metrics:values, pdf_downloaded:true});
        await page.getByRole('heading',{name:'Twój raport',exact:true}).scrollIntoViewIfNeeded();
        await page.screenshot({path:path.join(out,spec.name+'-exe.png')});
        if(await page.locator('[data-testid="stException"]').count()) throw Error('App exception');
      } catch(error) {
        fs.writeFileSync(path.join(out,'failure-ui.txt'),await page.locator('body').innerText());
        await page.screenshot({path:path.join(out,'failure.png')});
        throw error;
      } finally {await context.close();}
    }
    fs.writeFileSync(path.join(out,'exe-browser.json'),JSON.stringify(results,null,2));
    console.log(JSON.stringify(results));
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
