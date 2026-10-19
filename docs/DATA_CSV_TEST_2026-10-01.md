# Test wskazanego data.csv — 2026-10-01

Werdykt: import i sprawdzone obliczenia poprawne. Wymaganie „wczytaj cały ten CSV,
kliknij i otrzymaj raport” nie jest spełnione: pierwsza konfiguracja jest konieczna,
a zakres 374 dni przekracza limit raportu 366 dni.

## Źródło i zakres kontroli
- Plik wskazany przez użytkownika: `D:\csv do testów\data.csv`.
- 45 580 638 bajtów, 541 909 pozycji.
- SHA-256: `d07aec9960083af2339975a3f9d3b26313b342dcd9f86cce0b919b1cde639a44`.
- Identyczny skrót jak wcześniejszy zbiór kontrolny full-kaggle-qa; test wykonano
  ponownie bezpośrednio na wskazanej ścieżce, nie na wcześniejszej kopii.
- Daty: 01.12.2010–09.12.2011, 374 dni kalendarzowe.
- Test kodu oraz EXE z wydania 2026-09-30-oneclick w lokalnej przeglądarce Edge.
- Źródło sprawdzono skrótem także po testach: bez zmian. Pamięć profili była odizolowana
  w tymczasowym folderze. Nie używano istniejących baz ani raportów użytkownika.

## Konfiguracja testu
Data: InvoiceDate, jawne miesiąc/dzień/rok i godzina. Wartość: UnitPrice × Quantity.
Kategoria: Country. Dokument: InvoiceNo. Produkt: StockCode. Klient: CustomerID.
Kodowanie Windows-1252. Dopuszczone ujemne wartości. Zaokrąglanie każdej pozycji
HALF_UP do dwóch miejsc po mnożeniu. Bez usuwania duplikatów.
Waluta, netto/brutto i kompletność pozostają niepotwierdzone; waluta profilu XXX/j.p.
Nie interpretujemy identyfikatorów dokumentów jako liczby zrealizowanych zamówień.
Konfiguracja do ponownego użycia: `build/data-csv-20261001/profile.json`.

## POTWIERDZONE — niezależne liczby
Wzorzec obliczono osobno przez csv.DictReader, datetime oraz Decimal, bez parsera
i agregacji projektu. Wyniki porównano z importem i analizą aplikacji.

| Zakres | Pozycje | Suma j.p. | Ilość | Unikalne dokumenty |
|---|---:|---:|---:|---:|
| Pełne źródło — wzorzec i suma zaimportowanych pozycji | 541 909 | 9 747 747,93 | 5 176 450 | 25 900 |
| 01.01–09.12.2011 — analiza aplikacji | 499 428 | 8 998 790,91 | 4 834 222 | 23 875 |
| 10.11–09.12.2011 — aplikacja, dashboard EXE i PDF | 88 066 | 1 466 384,77 | 740 703 | 3 499 |

Pełny import: 31,92 s. Kliknięcie importu w EXE do komunikatu ograniczenia okresu:
34,816 s. Wybranie ostatnich 30 dni do dostępnego raportu/PDF: 2,266 s.
To pomiary na tym komputerze, nie gwarancja wydajności u odbiorcy.
Sprawdzono modele dzień/tydzień/miesiąc i sumy wszystkich 27 filtrów krajów w ostatnich
30 dniach. Brak kosztów i zysku pozostał brakiem, a porównanie okresów niedostępne.

## Wynik użytkowy i PDF
- W świeżej sesji prosty interfejs nie mapuje sam nazw InvoiceDate/UnitPrice/Country.
  Wyświetla prośbę o wybór kolumn. W teście zastosowano przygotowany profil JSON.
- Pełny plik importuje się, lecz raport dla całego pliku zatrzymuje komunikat o 366 dniach.
  Nie ma cichego obcinania danych.
- Po wybraniu ostatnich 30 dni dashboard i PDF są zgodne z niezależnym wzorcem.
- Przełączenia trzech widoków nie spowodowały nieobsłużonego wyjątku.
- Nowa sesja przeglądarki rozpoznaje zapamiętany profil i zwija jego ustawienia.
  Nie powtarzano pełnego importu w tej drugiej sesji; nadal wymagany jest wybór okresu.
- PDF pobrany z EXE ma 3 strony. Wszystkie wyrenderowano i obejrzano: tekst, tabele
  i wykres są czytelne, bez widocznych ucięć. Pierwsza strona ma dużo pustego miejsca.
- Na ekranie komunikaty o walucie, zaokrągleniu i podobnych pozycjach zajmują dużo
  miejsca przed wskaźnikami — pozostaje to przeszkodą dla prostoty obsługi.

W danych jest 135 080 pustych CustomerID i 10 624 ujemne ilości. Cztery pozycje wymagają
zaokrąglenia; łączny wpływ na pełną sumę to −0,004 j.p. Importer zgłasza 5 268 identycznych
pełnych wierszy i 416 544 powtórzenia daty/kwoty/kategorii; to różne definicje,
nie podstawa do automatycznego usuwania rekordów.

## Artefakty i następny krok
- `scripts/qa_user_data_csv.py`: pełny import i niezależny wzorzec.
- `scripts/qa_user_data_release.py`, `scripts/qa_user_data_browser.cjs`: EXE i przeglądarka.
- `build/data-csv-20261001/evidence.json`, `browser-evidence.json`, `pdf-evidence.json`.
- `build/data-csv-20261001/exe-report.pdf` oraz zrzuty i rendery w tym samym katalogu.

Najbliższa zmiana do rozważenia: obsługa całego zakresu dłuższego niż rok z czytelną
agregacją oraz gotowa konfiguracja tego formatu. Nie zmieniano programu ani limitów
w ramach tego testu. UNKNOWN: waluta/netto/brutto źródła, kompletność i samodzielność
użytkownika nietechnicznego; test nie potwierdza popytu ani przydatności biznesowej.
