# Poprawki importu i znaczenia danych — 2026-09-24

## POTWIERDZONE
- Import surowego CSV Kaggle Online Retail: 541 909 rekordów, 45 580 638 bajtów, bez zewnętrznej konwersji.
- Nowy profil w panelu: „Ustaw profil Kaggle Online Retail”. Dla innych źródeł można ręcznie wybrać znaczenie kwoty: wartość pozycji albo cena jednostkowa × ilość.
- Mnożenie Decimal przed zaokrągleniem; brak ilości lub błędna cena blokuje raport. Kwoty ujemne wymagają deklaracji.
- Jawne formaty dat z godzinami; grupowanie według lokalnej daty źródła, bez konwersji stref.
- Odczyt tekstu CSV przez dekoder strumieniowy, bez dodatkowej kopii całego pliku w Unicode. Surowe bajty i sparsowane rekordy pozostają w pamięci. To NIE jest silnik o stałym zużyciu RAM.
- Limity: 100 MiB i 1 000 000 rekordów. Test rzeczywisty dotyczy 541 909 rekordów; nie jest gwarancją wydajności dla dowolnego miliona rekordów.
- Osobne liczniki identycznych pełnych wierszy i zgodności daty/kwoty/kategorii. Brak automatycznego usuwania danych. Puste linie są pomijane i liczone.
- „Unikalne dokumenty” zastąpiły mylącą interpretację numerów faktur jako zrealizowanych zamówień.

## Dowody
88 testów regresji i nowych przypadków przeszło: build/import-tests.log.
Pełny test: scripts/qa_full_kaggle.py -> build/full-kaggle-qa/evidence.json.
Import 37,38 s; analiza 1,93 s; modele 0,18 s; szczyt pamięci procesu 636,25 MiB.
Pełne źródło wczytano; niezależnie sprawdzono okres 2011-01-01–2011-12-09:
499 428 pozycji, 8 998 790,91 j.p., ilość 4 834 222, 23 875 różnych identyfikatorów dokumentów.
Nie deklarowano kompletności; porównanie pozostaje niedostępne.
Pełne źródło: 5268 identycznych pełnych wierszy, 416544 powtórzenia daty/kwoty/kategorii — definicje nie są równoważne.

Interfejs: scripts/qa_full_kaggle_ui.py -> build/full-kaggle-qa/ui-evidence.json.
Streamlit AppTest: wczytanie 37,95 s, przełączanie trzech widoków 0,95–0,97 s (domyślny zakres ostatnich 7 dni).
Eksport PDF przez interfejs działa; wszystkie 3 strony wyrenderowano i sprawdzono wizualnie.
To test interfejsu w AppTest, nie pomiar animacji/przeglądarki ani pełny test EXE.

## UNKNOWN i następna weryfikacja
- Brak testu z rzeczywistym analitykiem hurtowni. Potrzebne: jeden zanonimizowany eksport, oczekiwany raport i obserwacja jednego cyklu pracy.
- Nie potwierdzono przydatności biznesowej, oszczędności czasu ani gotowości sprzedażowej.
- Dla większych zbiorów kolejny etap to magazyn dyskowy i agregacje bez trzymania wszystkich wierszy w RAM.
- Waluta i netto/brutto przykładu pozostają niepotwierdzone; profil nie przypisuje samowolnie PLN.
- Historyczny scripts/qa_large_kaggle.py dokumentował odrzucenie pliku przy starych limitach. Bieżący test pełnego pliku to scripts/qa_full_kaggle.py.

## Użycie
Wybierz data/external/kaggle-large/data.csv, kliknij „Ustaw profil Kaggle Online Retail”, następnie „Wczytaj dane”.
Wszystkie filtry i eksporty pracują na tym samym wyniku obliczeń.

Wydanie Windows: release/AutoReportAnalyst-Windows-2026-09-24-large-import.zip (92 840 209 bajtów). Test uruchomienia EXE: lokalny endpoint zdrowia HTTP 200 / ok. Pełny zbiór sprawdzono w kodzie źródłowym i AppTest; nie wykonano pełnej próby w przeglądarce wydania EXE.
