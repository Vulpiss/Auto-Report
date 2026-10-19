const {chromium}=require('C:/Users/kompu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs');
(async()=>{
 const out=process.argv[3];
 const browser=await chromium.launch({channel:'msedge',headless:true});
 const page=await browser.newPage({acceptDownloads:true,viewport:{width:1440,height:1050}});
 page.setDefaultTimeout(60000);
 const evidence={};
 const pdf=page.getByRole('button',{name:'Pobierz gotowy raport PDF',exact:true});
 async function expand(name){const s=page.locator('summary').filter({hasText:name}).first();await s.waitFor();if(!await s.evaluate(el=>el.parentElement.open))await s.click();}
 try {
  await page.goto(process.argv[2]);
  await page.locator('.st-key-easy_upload input[type=file]').setInputFiles(out+'/over-five-years.csv');
  await expand('Mam zapisane ustawienia z poprzedniego raportu');
  await page.locator('.st-key-easy_saved_profile input[type=file]').setInputFiles(out+'/synthetic-profile.json');
  await page.getByRole('button',{name:'Zastosuj zapisane ustawienia',exact:true}).click();
  await page.getByText('Ustawienia zastosowane.',{exact:false}).waitFor();
  await page.getByRole('button',{name:'Utwórz raport',exact:true}).click();
  await page.getByText('Maksymalny okres raportu to 5 lat kalendarzowych.',{exact:true}).waitFor();
  if(await pdf.count())throw Error('PDF available for excessive range');
  evidence.extraDayBlocked=true;
  await page.screenshot({path:out+'/five-year-limit.png'});
  await page.getByText('Ostatnie 5 lat w pliku',{exact:true}).click();
  await pdf.waitFor();
  const total=(await page.locator('[data-testid="stMetricValue"]').first().innerText()).replace(/\s/g,' ');
  if(total!=='1 826,00')throw Error('Unexpected five-year total: '+total);
  if(!((await page.locator('[data-testid="stMetricValue"]').nth(1).innerText()).replace(/\s/g,'')==='1826'))throw Error('Wrong count');
  await page.getByText('Raport obejmie 02.10.2021 – 01.10.2026.',{exact:false}).waitFor();
  const pending=page.waitForEvent('download');await pdf.click();await(await pending).saveAs(out+'/five-year-exe.pdf');
  evidence.fiveYearTotal='1826.00';evidence.fiveYearRows=1826;
  evidence.period=['2021-10-02','2026-10-01'];
  await page.screenshot({path:out+'/five-year-report.png'});
  for(const name of ['Kategorie i źródła zmiany','Jakość i pokrycie danych','Wynik i trend']){
   await page.getByText(name,{exact:true}).click();
   await page.locator('[data-testid="stStatusWidget"]').waitFor({state:'hidden'});
   if(await page.locator('[data-testid="stException"]').count())throw Error('Dashboard exception');
  }
  evidence.allThreeViews=true;
  await expand('Plik i ustawienia');
  await page.locator('.st-key-easy_upload input[type=file]').setInputFiles(out+'/invalid.csv');
  await page.getByText('invalid.csv',{exact:true}).waitFor();
  await pdf.waitFor({state:'hidden'});
  await page.getByRole('button',{name:'Utwórz raport',exact:true}).click();
  await page.getByText('Nie przygotowaliśmy raportu, ponieważ dane wymagają poprawy.',{exact:true}).waitFor();
  if(await pdf.count())throw Error('Stale PDF retained for invalid data');
  evidence.invalidAmountBlocked=true;evidence.oldPdfRemoved=true;
  await page.screenshot({path:out+'/invalid-amount.png'});
  fs.writeFileSync(out+'/period-browser-evidence.json',JSON.stringify(evidence,null,2));
  console.log(JSON.stringify(evidence));
 }catch(e){await page.screenshot({path:out+'/period-failure.png',fullPage:true});throw e;}
 finally{await browser.close();}
})();
