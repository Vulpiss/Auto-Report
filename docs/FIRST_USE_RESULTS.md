# Test pierwszego uruchomienia — 2026-09-28

## Wynik
GO dla dalszych testów wewnętrznych. Test nie potwierdza jeszcze działania na czystym Windowsie ani gotowości sprzedażowej.

Paczka: AutoReportAnalyst-Windows-2026-09-28-first-use.zip
SHA256: BEE0FD10DABE40C374191859CEA1FEF7B470F8FCB5A4227B0E596259AB414C10

## POTWIERDZONE
- Uruchomienie świeżo rozpakowanej paczki w folderze ze spacjami i polskimi znakami.
- Nowe katalogi ustawień: AUTOREPORT_HOME, APPDATA i LOCALAPPDATA.
- PATH procesu aplikacji ograniczony do Windows/System32; usunięte PYTHONPATH i PYTHONHOME.
- Serwer odpowiada na health check.
- Wczytanie danych demonstracyjnych i przełączenie wszystkich trzech dashboardów.
- Brak komponentu błędu Streamlit w końcowym widoku.
- Pobranie PDF (2 strony) i PPTX w wariancie Dashboardy (3 slajdy).
- PDF zawiera oczekiwaną sumę 1 250; zrzut dashboardu pokazuje 7 pozycji po filtrach.
- Struktura ZIP prezentacji jest poprawna.
- Instrukcja wewnątrz nowej paczki jest zgodna z poprawionym plikiem źródłowym.

## Poprawka
Zastąpiono sprzeczną, historycznie dopisywaną instrukcję spójnym opisem pierwszego uruchomienia. Poprawiono limity importu, opis edytowalnych wykresów PPTX i rozróżnienie profilu oraz sesji. Kod aplikacji i plik wykonywalny pozostały bez zmian. Nie powtarzano całej regresji kodu.

## Zakres i ograniczenia
UNKNOWN: czysty Windows bez wcześniejszych bibliotek i narzędzi. Nie wykryto Windows Sandbox ani narzędzi VMware/VirtualBox/Hyper-V. Komputer testowy nadal ma zainstalowanego Pythona; ograniczony PATH nie usuwa go z systemu.
Przeglądarkę sterowano narzędziami hosta. To test techniczny, nie obserwacja samodzielnej pracy odbiorcy.
W tej próbie nie testowano własnego CSV, natywnych wykresów PowerPoint ani pełnej poprawności wszystkich liczb. Nie wykonano nowej wizualnej inspekcji każdej strony PDF i każdego slajdu.

## Dowody
- build/first-use-latest.json — środowisko startu i identyfikacja paczki.
- build/first-use-qa/browser.cjs — scenariusz przeglądarkowy.
- build/first-use-qa/browser-evidence.json — wynik testu interfejsu.
- build/first-use-qa/export-evidence.json — kontrole eksportów.
- build/first-use-qa/report.pdf i report.pptx — pobrane pliki.
- build/first-use-qa/dashboard.png — zrzut końcowego widoku.

## Powtórzenie
Uruchom scripts/Test-AnalystFirstUse.ps1 z parametrem -Archive wskazującym ZIP.
Skrypt wymaga wolnego portu 8501 i pozostawia aplikację uruchomioną do testów interfejsu. Po testach zakończ tylko procesy ze ścieżką exe zapisaną w evidence.json.
Następny test bez angażowania osób z zewnątrz: rzeczywisty czysty Windows w maszynie wirtualnej, gdy będzie dostępna.
