const {chromium}=require('C:/Users/kompu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs');
(async()=>{
 const out=process.argv[3] || 'build/five-years-20261001';
 const expected=JSON.parse(fs.readFileSync(out+'/evidence.json','utf8'));
 const browser=await chromium.launch({channel:'msedge',headless:true});
 let page=await browser.newPage({acceptDownloads:true,viewport:{width:1440,height:1050}});
 page.setDefaultTimeout(180000);
 const evidence={};
 async function expand(name){const s=page.locator('summary').filter({hasText:name}).first();await s.waitFor();if(!await s.evaluate(el=>el.parentElement.open))await s.click();}
 async function waitSum(){
   const text=Number(expected.periods.whole.expected.total).toLocaleString('pl-PL',{minimumFractionDigits:2,maximumFractionDigits:2}).replace(/\s/g,' ');
   await page.locator('[data-testid="stMetricValue"]').first().waitFor();
   const actual=(await page.locator('[data-testid="stMetricValue"]').first().innerText()).replace(/\s/g,' ');
   if(actual!==text)throw Error('Unexpected total: '+actual+' expected '+text);
   const count=(await page.locator('[data-testid="stMetricValue"]').nth(1).innerText()).replace(/\s/g,'');
   if(count!==String(expected.periods.whole.expected.rows))throw Error('Unexpected row count: '+count);
 }
 try{
  await page.goto(process.argv[2]);
  await page.locator('input[type=file]').first().setInputFiles(expected.source);
  await page.getByText('Wybierz trzy kolumny powyżej.',{exact:false}).waitFor();
  evidence.firstFileNeedsConfiguration=true;
  await page.screenshot({path:out+'/first-import.png'});
  await expand('Mam zapisane ustawienia z poprzedniego raportu');
  await page.locator('input[type=file]').nth(1).setInputFiles(out+'/profile.json');
  await page.getByRole('button',{name:'Zastosuj zapisane ustawienia',exact:true}).click();
  await page.getByText('Ustawienia zastosowane.',{exact:false}).waitFor();
  const started=Date.now();
  await page.getByRole('button',{name:'Utwórz raport',exact:true}).click();
  await page.getByRole('button',{name:'Pobierz gotowy raport PDF',exact:true}).waitFor();
  await waitSum();
  evidence.fullUploadImportAndPdfMs=Date.now()-started;
  evidence.wholeFileReportBlocked=false;
  const download=page.waitForEvent('download');
  await page.getByRole('button',{name:'Pobierz gotowy raport PDF',exact:true}).click();
  await(await download).saveAs(out+'/exe-report.pdf');
  await page.getByRole('heading',{name:'Twój raport',exact:true}).scrollIntoViewIfNeeded();
  await page.screenshot({path:out+'/report.png'});
  evidence.views=[];
  for(const view of ['Kategorie i źródła zmiany','Jakość i pokrycie danych','Wynik i trend']){
   await page.getByText(view,{exact:true}).click();
   await page.locator('[data-testid="stStatusWidget"]').waitFor({state:'hidden'});
   await page.getByRole('button',{name:'Pobierz gotowy raport PDF',exact:true}).waitFor();
   evidence.views.push(view);
  }
  if(await page.locator('[data-testid="stException"]').count())throw Error('Unhandled exception');
  await page.close();
  page=await browser.newPage({acceptDownloads:true,viewport:{width:1440,height:1050}});page.setDefaultTimeout(180000);
  await page.goto(process.argv[2]);await page.locator('input[type=file]').first().setInputFiles(expected.source);
  await page.getByText('Zapamiętany układ kolumn.',{exact:false}).waitFor();
  await page.getByRole('button',{name:'Utwórz raport',exact:true}).waitFor();
  const config=page.locator('summary').filter({hasText:'Ustawienia pliku —'}).first();
  if(await config.evaluate(el=>el.parentElement.open))throw Error('Remembered settings expanded');
  evidence.profileRememberedInNewSession=true;
  await page.getByRole('button',{name:'Utwórz raport',exact:true}).click();
  await page.getByRole('button',{name:'Pobierz gotowy raport PDF',exact:true}).waitFor();
  await waitSum();
  evidence.oneClickForWholeFile=true;
  await page.screenshot({path:out+'/remembered-profile.png'});
  fs.writeFileSync(out+'/browser-evidence.json',JSON.stringify(evidence,null,2));console.log(JSON.stringify(evidence));
 }catch(e){await page.screenshot({path:out+'/failure.png',fullPage:true});throw e;}
 finally{await browser.close();}
})();
