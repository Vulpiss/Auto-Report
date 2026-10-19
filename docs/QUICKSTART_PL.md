# Auto-Report 0.2.0 — start
Wersja do prób technicznych. Nie została jeszcze sprawdzona przez niezależnego odbiorcę.

1. Wypakuj cały katalog AutoReport. Plik AutoReport.exe musi pozostać obok katalogu _internal.
2. Uruchom AutoReport.exe. Python nie jest potrzebny w paczce EXE.
3. Wybierz PRZYKLAD.csv (fikcyjne dane) albo własny eksport bez danych osobowych.
4. Ustaw nazwy trzech kolumn. Dla przykładu: date, value, category.
5. Przykład używa przecinka CSV, UTF-8, dat %Y-%m-%d i kropki dziesiętnej. Kwota przykładu: netto w PLN.
6. Dla polskiego eksportu możesz wybrać średnik, przecinek dziesiętny, daty %d.%m.%Y oraz Windows-1250. Nie zgadujemy tych ustawień.
7. Ustaw ostatnie 7 dni lub wpisz obie daty okresu. Ostatnie N dni kończy się na najpóźniejszej dacie z pliku, nie na dzisiaj.
8. Pełny zakres eksportu podaj tylko, jeśli potwierdzisz jego kompletność u źródła. Dla PRZYKLAD.csv: 2026-08-31 do 2026-09-13. Bez tego procenty będą niedostępne.
9. Kliknij Generuj raport PDF, następnie Otwórz ostatni raport.
10. Zapisz profil, aby ponownie użyć ustawień. Zakres kompletności potwierdzaj dla każdego eksportu.

## Oczekiwany wynik przykładu
Okres 2026-09-07 do 2026-09-13: suma 1 250,00 PLN, 7 pozycji, średnia 178,57 PLN.
Poprzedni okres: 1 000,00 PLN. Zmiana sumy: +25%, wyłącznie przy potwierdzonym zakresie.
Kategorie bieżącego okresu: Papier 550,00 PLN; Teczki i segregatory 450,00 PLN; Środki czystości 250,00 PLN.
To dane syntetyczne, nie wynik klienta.

## Reguły danych
Maksymalnie 20 MB i 100 000 rekordów. Jeden wiersz oznacza jedną pozycję, nie zamówienie. Jedna waluta PLN.
Kwoty mają najwyżej 2 miejsca dziesiętne; bez spacji/separatorów tysięcy i notacji naukowej. Nie zaokrąglamy wejścia.
Daty muszą dokładnie pasować do profilu. Wszystkie trzy pola są wymagane.
Błędny rekord blokuje cały raport i wskazuje numer wiersza. Popraw plik źródłowy i ponów.
Powtórzenia pozostają w sumie i są zliczane. Kwoty ujemne wymagają włączenia reguły zwrotów.
Procent przy zerowej albo ujemnej bazie: N/A. Program nie rekomenduje skalowania biznesu.
Raport obejmuje do 366 dni. Tabela kategorii pokazuje najwyżej 10 kategorii.

## Gdzie są wyniki
Domyślnie: %LOCALAPPDATA%/AutoReport/reports. Możesz wybrać inny katalog.
Każdy ukończony przebieg ma osobny katalog z report.pdf, summary.json i trend.png.
Nie nadpisujemy wcześniejszych raportów. Nie zapisujemy surowego CSV ani bazy transakcji na dysku.
PDF i wykres zawierają wartości i kategorie z Twojego pliku. summary.json zawiera metryki, profil i skrót SHA-256. Kwoty w JSON są dokładnymi ciągami dziesiętnymi; total_minor to całkowita liczba groszy. Wykres służy prezentacji przybliżonej, a liczby w PDF i JSON są dokładne.
Nieudane renderowanie pozostawia osobny katalog .pending-... z oznaczeniem błędu, bez publikacji ukończonego przebiegu.
Profil zapisuje się w %LOCALAPPDATA%/AutoReport/profile.json. Nie obejmuje CSV ani potwierdzenia kompletności.
Pliki pozostają lokalnie do ręcznego usunięcia. Narzędzie nie wysyła danych przez sieć.

## Próba samodzielności
Przygotuj drugi raport na kolejnym eksporcie bez pomocy autora. Zmierz cały czas od eksportu do sprawdzonego PDF.
Zapisz błędy i ręczne poprawki. Dopiero ten test u odbiorcy może potwierdzić łatwość wdrożenia.
