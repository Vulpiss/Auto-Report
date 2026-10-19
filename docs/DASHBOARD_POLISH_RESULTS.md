# Dopracowanie dashboardów — 25–26 września 2026

## Wdrożone
- Wyszukiwanie produktów i klientów, wybór spadków/wzrostów, strony po 20 pozycji. Wyszukiwanie zmienia listę, a przycisk szczegółów nakłada filtr całego dashboardu.
- Po wyborze produktu/klienta sekcja pozycji otwiera się automatycznie. Można usunąć filtry jednym przyciskiem.
- Ponowne użycie analizy i modelu dla tych samych danych i filtrów. Zmiana źródła/filtra unieważnia wynik i eksporty.
- Postęp importu co 10 000 pozycji, czas zakończenia, odrębny komunikat błędu. Ponowne wczytanie już zaimportowanego pliku z tym samym profilem nie powtarza parsowania.
- Widoczny okres, jednostki i skrócony zakres filtrów w panelu eksportu i prezentacjach; pełne filtry pozostają w notatkach.
- Długie etykiety zachowują rozpoznawalny początek, pełne nazwy i dokładne liczby są dostępne w tabelach, podpowiedziach lub notatkach.
- Osie dużych kwot w prezentacjach stosują tys./mln/mld; dokładne dane nie są zaokrąglane przez ten zabieg.
- Poprawiono niewidoczne słupki ujemne w PowerPoint i zbyt gęste etykiety osi liczby pozycji.
- Poprawiono reset deklaracji kompletności i kategorii po zmianie CSV. Przeglądarkowy test ujawnił, że samo usunięcie kluczy widgetów nie zawsze usuwało stare wartości.

## Dotychczas potwierdzone
93 testy automatyczne OK: build/dashboard-polish-tests.log.
Sztuczny test: 240 kategorii, 480 wierszy, długie nazwy, duże kwoty i wartości ujemne.
Niezależna suma: 20 520 000 205,20 PLN. Sumy top + pozostałe i wkłady zmian zgodne.
PowerPoint otworzył oba warianty PPTX i wyrenderował po 3 slajdy.
Wariant edytowalny: 3 natywne wykresy. Na kopii zmieniono styl serii, zapisano i potwierdzono zmianę po ponownym otwarciu.
Wyrenderowane slajdy sprawdzono wizualnie; wykryte błędy osi i wypełnienia zostały naprawione i zweryfikowane.
PDF z trudnymi nazwami: 4 strony, zawijanie tekstu i kontynuacja tabeli bez ucięcia.
Dowody: build/dashboard-polish/evidence.json, powerpoint-evidence.json, powerpoint-edit-check.txt, pliki PNG/PPTX/PDF.

## Test z analitykiem
Przygotowano docs/ANALYST_TASK_TEST.md i docs/analyst_task_observations.csv.
Nie przeprowadzono testu z rzeczywistym odbiorcą. Potrzebne: uczestnik i zanonimizowany eksport z niezależnymi oczekiwaniami.
Nie deklarujemy oszczędności czasu, popytu ani gotowości sprzedażowej.

## Wydajność
Końcowy test przeglądarkowy poprawionego EXE przeszedł: wyszukiwanie produktu, automatyczne szczegóły, pusty zakres, zmiana pliku, pełny import 541 909 rekordów i wszystkie trzy widoki.
Import: 39,44 s. Przełączanie widoków: 0,782 / 0,786 / 0,940 s. Ponowne kliknięcie importu: 0,548 s, bez ponownego parsowania.
Szczyt pamięci procesu aplikacji: 826,32 MiB (bez pamięci Edge).
Dowody: build/dashboard-polish/browser-evidence.json i memory-evidence.json.
Są to pojedyncze pomiary na tym komputerze z ograniczeniem aplikacji do jednego procesora logicznego, nie gwarancja czasu dla dowolnego sprzętu.
Ograniczenie do jednego procesora logicznego nie jest równoważne testowi fizycznego słabego laptopa; przeglądarka nie ma tego ograniczenia.
Dane są nadal przechowywane w pamięci. Dalsza redukcja RAM wymagałaby osobnego magazynu dyskowego i agregacji.

## Dostarczenie
Wydanie: release/AutoReportAnalyst-Windows-2026-09-25-dashboard-polish.zip.
Końcowy plik interfejsu w pakiecie ma tę samą sumę SHA256 co kod źródłowy; test przeglądarkowy wykonano po jego aktualizacji. Testowa aplikacja została zamknięta.
