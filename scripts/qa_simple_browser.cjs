const {chromium}=require('C:/Users/kompu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs');
(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 const page=await browser.newPage({acceptDownloads:true,viewport:{width:1366,height:900}});
 const out='build/simple-qa';fs.mkdirSync(out,{recursive:true});
 page.setDefaultTimeout(30000);
 const evidence={};
 async function idle(){await page.locator('[data-testid="stStatusWidget"]').waitFor({state:'hidden'});}
 async function expand(name){const summary=page.locator('summary').filter({hasText:name}).first();await summary.waitFor({state:'visible'});if(!await summary.evaluate(el=>el.parentElement.open))await summary.click();}
 async function download(name,path){const next=page.waitForEvent('download');await page.getByRole('button',{name,exact:true}).click();await(await next).saveAs(path);await idle();}
 try{
  await page.goto(process.argv[2]);
  await page.getByRole('heading',{name:'Twój raport w trzech krokach'}).waitFor();await idle();
  await page.screenshot({path:out+'/start.png',fullPage:true});
  await page.getByText('Chcę najpierw wypróbować program na przykładzie',{exact:true}).click();await idle();
  await page.getByRole('button',{name:'Pokaż mój raport',exact:true}).click();
  await page.getByText('Plik sprawdzony:',{exact:false}).waitFor();await idle();
  if(await page.locator('[data-testid="stMetricValue"]').first().innerText()!=='1 250,00')throw Error('Wrong demo sum');
  await page.screenshot({path:out+'/demo.png',fullPage:true});
  await page.getByRole('button',{name:'Przygotuj raport PDF',exact:true}).click();
  await download('Pobierz gotowy raport PDF',out+'/demo.pdf');
  evidence.demoTotal='1250.00';evidence.pdfDownloaded=true;
  await page.getByText('Ostatnie 30 dni w pliku',{exact:true}).click();
  await page.getByText('Raport obejmie 15.08.2026',{exact:false}).waitFor();await idle();
  if(await page.getByRole('button',{name:'Pobierz gotowy raport PDF',exact:true}).count())throw Error('Stale PDF after period change');
  evidence.periodInvalidatesPdf=true;
  await page.getByText('Chcę najpierw wypróbować program na przykładzie',{exact:true}).click();
  await page.getByText('Zacznij od wybrania pliku',{exact:false}).waitFor();await idle();
  await page.locator('input[type=file]').first().setInputFiles('sample_data/wholesale_business.csv');
  await page.getByRole('button',{name:'Pokaż mój raport',exact:true}).waitFor({state:'attached'});await idle();
  await expand('2. Sprawdź ustawienia pliku');
  await expand('Mam zapisane ustawienia z poprzedniego raportu');
  await page.locator('input[type=file]').nth(1).setInputFiles('sample_data/wholesale_business.profile.json');await idle();
  await page.getByRole('button',{name:'Zastosuj zapisane ustawienia',exact:true}).click();await idle();
  await page.getByRole('button',{name:'Pokaż mój raport',exact:true}).click();
  await page.getByText('Plik sprawdzony:',{exact:false}).waitFor();await idle();
  if(await page.locator('[data-testid="stMetricValue"]').first().innerText()!=='600,00')throw Error('Wrong saved-profile sum');
  if(!(await page.locator('[data-testid="stMetricLabel"]').first().innerText()).includes('PLN'))throw Error('Profile currency not restored');
  await page.getByRole('button',{name:'Przygotuj raport PDF',exact:true}).click();
  await download('Pobierz gotowy raport PDF',out+'/business.pdf');
  evidence.savedProfileTotal='600.00';
  await page.screenshot({path:out+'/business.png',fullPage:true});
  await page.locator('input[type=file]').first().setInputFiles('sample_data/internal_acceptance/mixed_valid_invalid.csv');
  await page.getByRole('button',{name:'Pobierz gotowy raport PDF',exact:true}).waitFor({state:'hidden'});await idle();
  if(await page.getByRole('button',{name:'Pobierz gotowy raport PDF',exact:true}).count())throw Error('Stale PDF after source change');
  evidence.sourceInvalidatesPdf=true;
  if(await page.locator('[data-testid="stException"]').count())throw Error('Unhandled Streamlit exception');
  fs.writeFileSync(out+'/browser-evidence.json',JSON.stringify(evidence,null,2));
  console.log(JSON.stringify(evidence));
 }catch(e){await page.screenshot({path:out+'/failure.png',fullPage:true});throw e;}
 finally{await browser.close();}
})();
