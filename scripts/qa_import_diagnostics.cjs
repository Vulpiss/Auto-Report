const {chromium} = require(process.env.AUTOREPORT_PLAYWRIGHT_DIR || 'C:/Users/kompu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const out = process.argv[3];
  const browser = await chromium.launch({channel: 'msedge', headless: true});
  const page = await browser.newPage({acceptDownloads: true, viewport: {width: 1440, height: 1000}});
  page.setDefaultTimeout(30000);
  const evidence = {};
  async function idle() {
    await page.locator('[data-testid="stStatusWidget"]').waitFor({state: 'hidden'});
  }
  async function setMeaning() {
    await page.getByText('Wybierz znaczenie kwoty…', {exact: true}).waitFor();
    await page.getByRole('combobox', {name: 'Co oznacza kwota w jednym wierszu?'}).click();
    await page.getByRole('option', {name: 'Wartość całej pozycji', exact: true}).click();
    await idle();
  }
  try {
    await page.goto(process.argv[2]);
    await page.getByRole('heading', {name: 'Wybierz CSV. Kliknij. Gotowe.'}).waitFor();
    await idle();
    await page.locator('input[type=file]').first().setInputFiles(path.join(out, 'bad.csv'));
    await page.getByRole('combobox', {name: 'Co oznacza kwota w jednym wierszu?'}).waitFor();
    await idle();
    await setMeaning();
    await page.getByRole('button', {name: 'Utwórz raport', exact: true}).click();
    await page.getByRole('heading', {name: 'Miejsca do poprawy w danych'}).waitFor();
    await idle();
    if (await page.getByRole('button', {name: 'Pobierz gotowy raport PDF', exact: true}).count()) throw Error('PDF available for invalid CSV');
    await page.screenshot({path: path.join(out, 'problems-page-1.png'), fullPage: true});
    const nextDownload = page.waitForEvent('download');
    await page.getByRole('button', {name: 'Pobierz listę miejsc do poprawy (CSV)', exact: true}).click();
    await (await nextDownload).saveAs(path.join(out, 'problems.csv'));
    const pageInput = page.getByRole('spinbutton', {name: 'Strona listy problemów'});
    await pageInput.fill('2');
    await pageInput.press('Enter');
    await idle();
    await page.getByText('Pokazano 50 z 150 problemów.', {exact: false}).waitFor();
    await page.locator('[data-testid="stDataFrame"]').last().click({position: {x: 17, y: 84}});
    await page.getByText('Błąd · linia CSV: 52 · kolumna: category', {exact: true}).waitFor();
    await idle();
    evidence.rowSelectionShowsFullHint = true;
    await page.screenshot({path: path.join(out, 'problems-page-2.png'), fullPage: true});
    evidence.paginationSurvivesRerun = true;
    evidence.invalidCsvBlocksPdf = true;
    await page.locator('input[type=file]').first().setInputFiles(path.join(out, 'corrected.csv'));
    await page.getByRole('combobox', {name: 'Co oznacza kwota w jednym wierszu?'}).waitFor();
    await idle();
    await setMeaning();
    await page.getByRole('button', {name: 'Utwórz raport', exact: true}).click();
    await page.getByText('Plik sprawdzony: 3 pozycji.', {exact: true}).waitFor();
    await idle();
    const value = await page.locator('[data-testid="stMetricValue"]').first().innerText();
    if (value !== '60,00') throw Error('Incorrect total after repair: ' + value);
    if (await page.getByRole('heading', {name: 'Miejsca do poprawy w danych'}).count()) throw Error('Stale repair list');
    if (await page.locator('[data-testid="stException"]').count()) throw Error('Unhandled app exception');
    evidence.correctedTotal = '60.00';
    evidence.repairClearsProblems = true;
    await page.screenshot({path: path.join(out, 'corrected.png'), fullPage: true});
    fs.writeFileSync(path.join(out, 'browser-evidence.json'), JSON.stringify(evidence, null, 2));
    console.log(JSON.stringify(evidence));
  } catch (error) {
    fs.writeFileSync(path.join(out, 'failure-ui.txt'), await page.locator('body').innerText());
    await page.screenshot({path: path.join(out, 'failure.png'), fullPage: true});
    throw error;
  } finally {
    await browser.close();
  }
})();
