const {chromium}=require('C:/Users/kompu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs');
(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 const out='build/oneclick-qa';fs.mkdirSync(out,{recursive:true});
 let page=await browser.newPage({acceptDownloads:true,viewport:{width:1366,height:1000}});
 const evidence={};
 async function expand(name){const summary=page.locator('summary').filter({hasText:name}).first();await summary.waitFor();if(!await summary.evaluate(el=>el.parentElement.open))await summary.click();}
 async function download(name){const next=page.waitForEvent('download');await page.getByRole('button',{name:'Pobierz gotowy raport PDF',exact:true}).click();await(await next).saveAs(out+'/'+name+'.pdf');}
 async function total(value){await page.locator('[data-testid="stMetricValue"]').first().filter({hasText:value}).waitFor({timeout:30000});if(await page.locator('[data-testid="stMetricValue"]').first().innerText()!==value)throw Error('Unexpected total');await page.getByRole('button',{name:'Pobierz gotowy raport PDF',exact:true}).waitFor();}
 try{
  await page.goto(process.argv[2]);
  await page.getByRole('heading',{name:'Wybierz CSV. Kliknij. Gotowe.'}).waitFor();
  await page.screenshot({path:out+'/start.png'});
  await page.getByText('Chcę najpierw wypróbować program na przykładzie',{exact:true}).click();
  await page.getByRole('button',{name:'Utwórz raport',exact:true}).click();
  await total('2 250,00');await download('demo-full');
  await expand('Zmień okres raportu');
  await page.getByText('Ostatnie 7 dni w pliku',{exact:true}).click();
  await total('1 250,00');await download('demo-week');
  evidence.demoFull='2250.00';evidence.demoWeek='1250.00';evidence.automaticPdf=true;
  await expand('Plik i ustawienia');
  await page.getByText('Chcę najpierw wypróbować program na przykładzie',{exact:true}).click();
  await page.getByText('Zacznij od wybrania pliku',{exact:false}).waitFor();
  await page.locator('input[type=file]').first().setInputFiles(out+'/first.csv');
  await page.getByRole('button',{name:'Utwórz raport',exact:true}).waitFor({state:'attached'});
  await expand('Ustawienia pliku —');
  await page.locator('.st-key-easy_config_meaning').getByRole('combobox').click();
  await page.getByRole('option',{name:'Wartość całej pozycji',exact:true}).click();
  await page.locator('.st-key-easy_config_currency').getByRole('combobox').click();
  await page.getByRole('option',{name:'EUR',exact:true}).click();
  await page.getByRole('button',{name:'Utwórz raport',exact:true}).click();await total('12,00');
  await page.getByText('Ustawienia zapamiętane.',{exact:false}).waitFor({state:'attached'});
  evidence.firstImportConfigured=true;
  await page.close();
  page=await browser.newPage({acceptDownloads:true,viewport:{width:1366,height:1000}});
  await page.goto(process.argv[2]);
  await page.locator('input[type=file]').first().setInputFiles(out+'/second.csv');
  await page.getByText('Zapamiętany układ kolumn.',{exact:false}).waitFor();
  await page.getByText('Raport: EUR',{exact:false}).waitFor();
  const settings=page.locator('summary').filter({hasText:'Ustawienia pliku —'}).first();
  if(await settings.evaluate(el=>el.parentElement.open))throw Error('Known-file settings should be collapsed');
  await page.screenshot({path:out+'/known-file.png'});
  await page.getByRole('button',{name:'Utwórz raport',exact:true}).click();await total('40,00');
  if(!(await page.locator('[data-testid="stMetricLabel"]').first().innerText()).includes('EUR'))throw Error('Wrong remembered currency');
  await download('second');
  await page.getByRole('heading',{name:'Twój raport',exact:true}).scrollIntoViewIfNeeded();
  await page.screenshot({path:out+'/report.png'});
  evidence.newBrowserSessionOneClickTotal='40.00';evidence.rememberedCurrency='EUR';
  await expand('Plik i ustawienia');
  await page.locator('input[type=file]').first().setInputFiles(out+'/invalid.csv');
  await page.getByRole('button',{name:'Pobierz gotowy raport PDF',exact:true}).waitFor({state:'hidden'});
  await page.getByRole('button',{name:'Utwórz raport',exact:true}).click();
  await page.getByText('Nie przygotowaliśmy raportu, ponieważ dane wymagają poprawy.',{exact:true}).waitFor();
  if(await page.getByRole('button',{name:'Pobierz gotowy raport PDF',exact:true}).count())throw Error('Stale PDF retained');
  if(await page.locator('[data-testid="stException"]').count())throw Error('Unhandled exception');
  evidence.invalidCsvBlocked=true;
  fs.writeFileSync(out+'/browser-evidence.json',JSON.stringify(evidence,null,2));console.log(JSON.stringify(evidence));
 }catch(e){await page.screenshot({path:out+'/failure.png',fullPage:true});throw e;}
 finally{await browser.close();}
})();
