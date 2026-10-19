const {chromium}=require('C:/Users/kompu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs');
(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 const page=await browser.newPage({acceptDownloads:true,viewport:{width:1440,height:1050}});
 page.setDefaultTimeout(60000);
 const out='build/internal-acceptance', fixtures='sample_data/internal_acceptance';
 const evidence={cycles:[]};
 async function idle(){await page.locator('[data-testid="stStatusWidget"]').waitFor({state:'hidden'});}
 async function download(name,file){
  const promise=page.waitForEvent('download');
  await page.getByRole('button',{name,exact:true}).click();
  await (await promise).saveAs(file);await idle();
 }
 try{
 await page.goto('http://127.0.0.1:8501');
 for(const i of [1,2]){
  await page.locator('input[type=file]').nth(0).setInputFiles(fixtures+'/cycle'+i+'.csv');await idle();
  await page.locator('input[type=file]').nth(1).setInputFiles(fixtures+'/cycle'+i+'.session.json');
  await page.getByText('cycle'+i+'.session.json',{exact:true}).waitFor();await idle();
  await page.getByRole('button',{name:'Przywróć profil / sesję',exact:true}).click();
  await page.getByText('Ustawienia przywrócone. Wczytaj dane.',{exact:true}).waitFor();
  await page.getByRole('button',{name:'Wczytaj dane',exact:true}).click();
  await page.getByText('Dane sprawdzone. Dashboard gotowy.',{exact:true}).waitFor();await idle();
  if(await page.getByLabel('Pełny eksport od',{exact:true}).inputValue()!=='2026-08-31')throw Error('Restored coverage lost');
  await page.getByText('Wynik i trend',{exact:true}).first().click();await idle();
  const value=await page.locator('[data-testid="stMetricValue"]').first().innerText();
  if(value!==(i===1?'600,00':'700,00'))throw Error('Unexpected KPI '+value);
  for(const view of ['Kategorie i źródła zmiany','Jakość i pokrycie danych','Wynik i trend']){
   await page.getByText(view,{exact:true}).first().click();
   await page.getByRole('heading',{name:view,exact:true}).waitFor();await idle();
  }
  await page.getByRole('button',{name:'Przygotuj PDF z aktualnych filtrów',exact:true}).click();
  await page.getByRole('button',{name:'Pobierz PDF',exact:true}).waitFor();
  await download('Pobierz PDF',out+'/cycle'+i+'/exe.pdf');
  await page.locator('.st-key-pptx_style').getByRole('combobox').click();
  await page.getByRole('option',{name:'Edytowalne wykresy',exact:true}).click();await idle();
  await page.getByRole('button',{name:'Przygotuj PowerPoint',exact:true}).click();
  await page.getByRole('button',{name:'Pobierz PowerPoint',exact:true}).waitFor();
  await download('Pobierz PowerPoint',out+'/cycle'+i+'/exe-native.pptx');
  await page.screenshot({path:out+'/cycle'+i+'/browser.png',fullPage:true});
  evidence.cycles.push({cycle:i,kpi:value,threeViews:true,pdf:true,nativePptx:true});
  console.log('Cycle '+i+' passed');
 }
 if(!await page.getByRole('button',{name:'Przywróć profil / sesję',exact:true}).isVisible())await page.getByText('Dane i konfiguracja',{exact:true}).click();
 await page.locator('input[type=file]').nth(1).setInputFiles(fixtures+'/cycle1.session.json');
 await page.getByText('cycle1.session.json',{exact:true}).waitFor();await idle();
 await page.getByRole('button',{name:'Przywróć profil / sesję',exact:true}).click();
 await page.getByText('Sesja pochodzi z innego CSV.',{exact:false}).waitFor();
 evidence.wrongSessionBlocked=true;
 await page.locator('input[type=file]').nth(0).setInputFiles(fixtures+'/mixed_valid_invalid.csv');await idle();
 await page.getByRole('button',{name:'Wczytaj dane',exact:true}).click();await idle();
 await page.getByText('Brak kolumn:',{exact:false}).waitFor();
 if(await page.getByRole('button',{name:'Pobierz PowerPoint',exact:true}).count())throw Error('Stale PPTX retained');
 if(await page.getByRole('button',{name:'Pobierz PDF',exact:true}).count())throw Error('Stale PDF retained');
 evidence.invalidSourceClearsDownloads=true;
 if(await page.locator('[data-testid="stException"]').count())throw Error('Unhandled exception');
 fs.writeFileSync(out+'/browser-evidence.json',JSON.stringify(evidence,null,2));
 console.log(JSON.stringify(evidence));
 }catch(e){await page.screenshot({path:out+'/failure.png',fullPage:true});throw e;}
 finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
