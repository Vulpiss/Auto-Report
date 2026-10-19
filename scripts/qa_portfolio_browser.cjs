/* Actual synthetic app session; never modifies the rendered interface. */
const {chromium} = require(process.env.AUTOREPORT_PLAYWRIGHT_DIR || 'C:/Users/kompu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const [url, out, media, mode] = process.argv.slice(2);
  const record = mode === 'record';
  const browser = await chromium.launch({channel: 'msedge', headless: true});
  const context = await browser.newContext({acceptDownloads: true, viewport: {width: 1440, height: 1050},
    ...(record ? {recordVideo: {dir: path.join(out, 'video'), size: {width: 1440, height: 1050}}} : {})});
  const page = await context.newPage();
  page.setDefaultTimeout(30000);
  const evidence = {};
  const video = page.video();
  async function idle() {
    await page.locator('[data-testid="stStatusWidget"]').waitFor({state: 'hidden'});
  }
  async function pause(ms = 2500) {if (record) await page.waitForTimeout(ms);}
  async function expander(name, open) {
    const label = page.getByText(name, {exact: true});
    const isOpen = await label.evaluate(el => el.closest('details').open);
    if (isOpen !== open) await label.click();
  }
  async function screenshot(name) {
    await idle();
    if (name === 'overview') {
      await page.getByText('Co chcesz zobaczyć?', {exact: true}).evaluate(el => el.scrollIntoView({block: 'start'}));
      await page.mouse.wheel(0, -90);
      await pause(1600);
    }
    if (name === 'categories' || name === 'diagnostics') {
      const title = name === 'categories' ? 'Struktura wartości w czasie' : 'Miejsca do poprawy w danych';
      await page.getByRole('heading', {name: title, exact: true}).evaluate(el => el.scrollIntoView({block: 'start'}));
      await page.mouse.wheel(0, -100);
      await pause(1600);
    }
    if (record) await page.screenshot({path: path.join(media, name + '.png')});
  }
  async function metrics(expected) {
    await page.waitForFunction(wanted => {
      const actual = Array.from(document.querySelectorAll('[data-testid="stMetricValue"]')).slice(0, 3).map(el => el.textContent);
      return JSON.stringify(actual) === JSON.stringify(wanted);
    }, expected);
    const values = (await page.locator('[data-testid="stMetricValue"]').allTextContents()).slice(0, 3);
    if (JSON.stringify(values) !== JSON.stringify(expected)) throw Error('Wrong metrics: ' + JSON.stringify(values));
    return values;
  }
  async function load() {
    await page.getByRole('button', {name: 'Utwórz raport', exact: true}).click();
    await page.getByText('Plik sprawdzony: 14 pozycji.', {exact: true}).waitFor();
    await page.getByRole('button', {name: 'Pobierz gotowy raport PDF', exact: true}).waitFor();
    await idle();
  }
  try {
    await page.goto(url);
    await page.getByRole('heading', {name: 'Wybierz CSV. Kliknij. Gotowe.'}).waitFor();
    await idle();
    await pause(1800);
    await page.getByText('Chcę najpierw wypróbować program na przykładzie', {exact: true}).click();
    await idle();
    await pause(1800);
    await load();
    await expander('Plik i ustawienia', false);
    await page.getByRole('heading', {name: 'Twój raport', exact: true}).scrollIntoViewIfNeeded();
    evidence.full_metrics = await metrics(['2 250,00', '14', '160,71']);
    await pause(3500);
    await screenshot('overview');
    await expander('Zmień okres raportu (opcjonalnie)', true);
    await page.getByText('Ostatnie 7 dni w pliku', {exact: true}).click();
    await page.getByText('Raport obejmie 07.09.2026 – 13.09.2026.', {exact: false}).waitFor();
    await idle();
    evidence.weekly_metrics = await metrics(['1 250,00', '7', '178,57']);
    await expander('Zmień okres raportu (opcjonalnie)', false);
    await page.getByRole('heading', {name: 'Twój raport', exact: true}).scrollIntoViewIfNeeded();
    await pause(3000);
    const pdfDownload = page.waitForEvent('download');
    await page.getByRole('button', {name: 'Pobierz gotowy raport PDF', exact: true}).click();
    await (await pdfDownload).saveAs(path.join(out, 'weekly.pdf'));
    await page.getByText('Kategorie i źródła zmiany', {exact: true}).click();
    await idle();
    await page.getByRole('heading', {name: 'Struktura wartości w czasie', exact: true}).scrollIntoViewIfNeeded();
    await pause(3200);
    await screenshot('categories');
    await page.getByText('Jakość i pokrycie danych', {exact: true}).click();
    await idle();
    await page.getByRole('heading', {name: 'Obecność pozycji', exact: true}).scrollIntoViewIfNeeded();
    await pause(3200);
    await screenshot('quality');
    await page.getByRole('heading', {name: 'Reguły interpretacji', exact: true}).scrollIntoViewIfNeeded();
    await page.getByText('Pełny eksport: nie podano / nie podano', {exact: true}).waitFor();
    evidence.missing_completeness_declared = true;
    await pause(2800);
    await expander('Plik i ustawienia', true);
    await page.getByText('Chcę najpierw wypróbować program na przykładzie', {exact: true}).click();
    await page.getByText('Zacznij od wybrania pliku albo zaznacz przykład powyżej.', {exact: false}).waitFor();
    await page.locator('.st-key-easy_upload input[type=file]').setInputFiles(path.join(out, 'bad.csv'));
    await page.getByText('Zapamiętany układ kolumn.', {exact: false}).waitFor();
    await idle();
    await page.getByRole('button', {name: 'Utwórz raport', exact: true}).click();
    await page.getByRole('heading', {name: 'Miejsca do poprawy w danych', exact: true}).waitFor();
    await page.getByText('Błędne: 2. Problemów w polach: 2.', {exact: false}).waitFor();
    await idle();
    if (await page.getByRole('button', {name: 'Pobierz gotowy raport PDF', exact: true}).count()) throw Error('PDF available for invalid CSV');
    await page.getByRole('heading', {name: 'Miejsca do poprawy w danych', exact: true}).scrollIntoViewIfNeeded();
    await pause(3200);
    await screenshot('diagnostics');
    const csvDownload = page.waitForEvent('download');
    await page.getByRole('button', {name: 'Pobierz listę miejsc do poprawy (CSV)', exact: true}).click();
    await (await csvDownload).saveAs(path.join(out, 'problems.csv'));
    await page.locator('[data-testid="stDataFrame"]').last().click({position: {x: 17, y: 84}});
    await page.getByText('Błąd · linia CSV: 14 · kolumna: category', {exact: true}).waitFor();
    await pause(2500);
    evidence.invalid_csv_blocks_pdf = true;
    evidence.row_selection_shows_hint = true;
    await page.locator('.st-key-easy_upload input[type=file]').setInputFiles(path.join(out, 'corrected.csv'));
    await page.getByRole('heading', {name: 'Miejsca do poprawy w danych', exact: true}).waitFor({state: 'hidden'});
    await page.getByText('Zapamiętany układ kolumn.', {exact: false}).waitFor();
    await idle();
    await load();
    await page.getByText('Wynik i trend', {exact: true}).click();
    await idle();
    evidence.corrected_metrics = await metrics(['2 250,00', '14', '160,71']);
    if (await page.getByRole('heading', {name: 'Miejsca do poprawy w danych', exact: true}).count()) throw Error('Stale diagnostic list');
    if (await page.locator('[data-testid="stException"]').count()) throw Error('Unhandled app exception');
    await expander('Plik i ustawienia', false);
    await page.getByRole('heading', {name: 'Twój raport', exact: true}).scrollIntoViewIfNeeded();
    await pause(3500);
    evidence.repaired_import_clears_errors = true;
    fs.writeFileSync(path.join(out, 'browser-evidence.json'), JSON.stringify(evidence, null, 2));
    console.log(JSON.stringify(evidence));
  } catch (error) {
    fs.writeFileSync(path.join(out, 'failure-ui.txt'), await page.locator('body').innerText());
    await page.screenshot({path: path.join(out, 'failure.png'), fullPage: true});
    throw error;
  } finally {
    await context.close();
    if (video) fs.writeFileSync(path.join(out, 'video.json'), JSON.stringify({path: await video.path()}));
    await browser.close();
  }
})().catch(error => {console.error(error); process.exitCode = 1;});
