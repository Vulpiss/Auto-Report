# Wynik weryfikacji dashboardów — 2026-09-20
## POTWIERDZONE
- 63 testy automatyczne zakończone sukcesem.
- Konflikt etykiet grup zbiorczych z kategoriami źródłowymi naprawiony i objęty testem.
- Miniwykresy obliczane tylko dla aktualnej strony (do 100 kategorii). Przejście na ostatnią stronę i zawężenie filtra przeszły test interfejsu.
- Definicje KPI dostępne w aplikacji, stałe przypisanie kolorów okresom i stanom jakości.
- Trzy widoki działają z nowego EXE. Pobrano PPTX z 3 slajdami i pojedynczy slajd jakości bez błędów aplikacji i JavaScript.
- Obie prezentacje przeszły kontrolę struktury, rozmiaru slajdu i import do renderera. Obejrzano wynik i układ trzech widoków.
- git diff --check bez błędów białych znaków.

## Pomiar na komputerze deweloperskim
Windows 10.0.26200, Python 3.11.3. Jeden przebieg dla każdego syntetycznego pliku; pomiar nie obejmuje ręcznej obsługi.
| Pozycje | Kategorie źródła | Okres bieżący | Analiza | Model + strona tabeli | 3 slajdy PPTX |
|---|---|---|---|---|---|
| 100 000 | 500 | 28 dni | 2,907 s | 0,026 s | 1,740 s |
| 10 000 | 10 000 | 366 dni | 0,501 s | 0,068 s | nie mierzono |
Sumy zweryfikowano niezależnie w całkowitych groszach. To nie jest gwarancja czasu dla wszystkich plików ani test UI na słabszym komputerze.

## Artefakty
- Paczka: release/AutoReportAnalyst-Windows-2026-09-20.zip.
- Log testów: build/analyst-live/hardening-tests-final.log.
- Benchmark: build/analyst-live/hardening/performance.json.
- Przeglądarka EXE: build/analyst-live/hardening/frozen-browser.json.
- Walidacja PPTX: frozen-validation.json i single-validation.json w tym samym katalogu.
- Protokół: ANALYST_ACCEPTANCE.md; formularz: pilot_cycles.csv.
Poprzednie wydanie zachowano.

## UNKNOWN — pozostałe bramki
- Rzeczywiste trzy kolejne eksporty hurtowni i potwierdzenie ich znaczenia.
- Wymaganie edytowalnych wykresów; obecny PPTX zawiera obrazy.
- Test na czystym Windows bez Pythona i otwarcie w PowerPoint odbiorcy.
- Dwa samodzielne cykle analityka, oszczędność czasu i akceptacja zakresu.

## Werdykt
GO do kontrolowanego testu użytkownika. Nie ogłaszamy zakończenia pilota ani gotowości sprzedażowej.
Największe ryzyka: semantyka eksportu, brak potwierdzonej kompletności, potrzeba edytowalnych wykresów, inne środowisko Windows, brak zmierzonej przewagi nad obecnym Excelem.
Najmniejszy kolejny dowód: zanonimizowany eksport z jednej hurtowni, obecna prezentacja i wypełniona karta źródła z ANALYST_ACCEPTANCE.md.
