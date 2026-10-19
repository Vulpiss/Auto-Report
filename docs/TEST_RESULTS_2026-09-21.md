# Test Auto-Report — 2026-09-21

## Zakres i wynik
POTWIERDZONE: uruchomiono istniejące wydanie release/analyst-2026-09-20/AutoReportAnalyst/AutoReportAnalyst.exe na komputerze deweloperskim.
63 testy automatyczne przeszły (14,523 s). Sprawdzono trzy widoki w przeglądarce, import demo i CSV 187 pozycji oraz eksport jednego i trzech slajdów. Bez wyjątków aplikacji i błędów JavaScript w tych scenariuszach.
Nie modyfikowano kodu produktu.

## CSV 187 pozycji
Źródło: outputs/01a0afd4-dashboard-test-02/dashboard_test_02.csv, dane syntetyczne.
Profil: UTF-8, przecinek CSV, kropka dziesiętna, PLN netto, kwoty ujemne dopuszczone.
Bieżący okres: 2026-09-05–2026-09-18. Poprzedni: 2026-08-22–2026-09-04.
Pełny eksport zadeklarowany: 2026-08-22–2026-09-18.
- Wartość bieżąca: 21 431,67 PLN.
- Poprzednia: 22 317,53 PLN.
- Różnica: -885,86 PLN; zmiana po zaokrągleniu: -4,0%.
- Pozycje bieżące: 89, poprzednie: 98.
- Średnia bieżąca: 240,81 PLN.
- Źródło: 187 rekordów, 1 powtórzenie, 3 kwoty ujemne.
- Największy bezwzględny wkład w zmianę: Nowa kolekcja +5 095,64 PLN.
Wartości sum, liczników, profilu oraz jakości w notatkach każdego eksportowanego slajdu sprawdzono wobec zapisanych niezależnych oczekiwań.

## Eksport
PPTX: jeden i trzy slajdy; integralność archiwum, poprawność pakietu, geometria, ponowny import i render przeszły. Obejrzano wszystkie trzy rodzaje widoku. Nie jest to próba otwarcia w Microsoft PowerPoint.
Pliki wynikowe: output/presentations/AutoReport-analityk-test187-2026-09-21.pptx oraz AutoReport-analityk-test187-single-2026-09-21.pptx.

## Wydajność — jeden lokalny przebieg
100 000 pozycji, 500 kategorii, 28 dni: analiza 3,934 s, model i strona tabeli 0,032 s, trzy slajdy 2,463 s.
10 000 pozycji, 10 000 kategorii, 366 dni: analiza 0,678 s, model i strona tabeli 0,100 s. Eksportu tego drugiego zestawu nie mierzono.
Pomiar nie obejmuje całego czasu obsługi użytkownika ani pobierania w przeglądarce.

## Uwagi wizualne
- Na slajdach legenda struktury nakłada się na górną część wykresu słupkowego. Przy większej liczbie kategorii warto zarezerwować dla niej osobną przestrzeń.
- Pełna tabela ma więcej kolumn niż mieści się w panelu i wymaga przewijania poziomego. Przyjęty układ nie zapewnia jednoczesnej widoczności wszystkich kolumn.
Nie wykryto błędnych liczb w sprawdzonych scenariuszach. Nie oznacza to braku błędów dla wszystkich możliwych danych.

## UNKNOWN
Czysty Windows, rzeczywisty PowerPoint odbiorcy i dwa cykle pracy realnego analityka.
GO do kontrolowanego pilota; brak podstaw do deklaracji gotowości sprzedażowej.

Dowody: build/qa-2026-09-21/tests.log, performance.json, frozen-browser.json, test187-browser.json, pptx-numbers.json, test187-validation.json, test187-single-validation.json oraz zrzuty PNG w tym samym katalogu.
