# Okres do pięciu lat — 2026-10-01

POTWIERDZONE: wspólny silnik dashboardu i PDF akceptuje do pięciu lat kalendarzowych. Okres jest liczony od wybranej daty końcowej, nie od dzisiejszej daty. Początek to dzień po rocznicy sprzed pięciu lat; dla końca 29 lutego rocznicę przyjmujemy jako 28 lutego. Przykład: 02.10.2021–01.10.2026. Limit uwzględnia lata przestępne (1826 lub 1827 dni w sprawdzonych przypadkach).

Tryb prosty domyślnie obejmuje cały plik, jeśli mieści się on w limicie. Dostępny jest też wybór „Ostatnie 5 lat w pliku”. Dłuższy zakres wymaga jawnego wyboru okresu; program nie obcina automatycznie danych. Dotychczasowe zasady kompletności i porównań pozostają: brak wierszy nie oznacza zera, a porównanie rok do roku z nierówną liczbą dni wymaga zmiany zakresu lub wyboru poprzedniego okresu.

## Weryfikacja

- Regresja: 112 testów przeszło; następnie dodano i uruchomiono test wszystkich trzech widoków na pięciu latach i pięciu kategoriach. Wszystkie 4 testy w `test_five_years.py` przeszły.
- Granice okresu, przekroczenie o jeden dzień, 29 lutego, niezależne sumy, filtry i poprzedni pięcioletni okres: poprawne.
- Przycisk pięcioletniego okresu w trybie prostym: poprawny zakres i automatyczny PDF.
- Sztuczne dane: 1826 dni, suma 1826,00; PDF wyrenderowany i obie strony sprawdzone wizualnie.
- Rzeczywisty `D:\csv do testów\data.csv`: wszystkie 541 909 pozycji, zakres 01.12.2010–09.12.2011 (374 dni), suma 9 747 747,93 j.p.; ilość 5 176 450, dokumenty 25 900. Wyniki zgodne z niezależnym obliczeniem csv/Decimal, także dla krótszych okresów i 27 filtrów krajów.
- Nowy EXE: pełny import i PDF około 40 sekund na tym komputerze. Trzy widoki dostępne. Nowa sesja odczytuje zapamiętany profil i generuje cały raport jednym przyciskiem.
- PDF z EXE: 3 strony, poprawna suma i daty; wszystkie strony wyrenderowane i sprawdzone wizualnie. Pierwsza strona ma dużo wolnego miejsca, bez uciętej treści.
- Źródłowy CSV niezmieniony, potwierdzony SHA-256. Testy używały osobnego katalogu profili; nie zmieniały ustawień użytkownika.

UNKNOWN: waluta, netto/brutto i kompletność źródłowego eksportu. Pierwszy import tego układu nadal wymaga ustawień (można zastosować zapisany profil JSON). Nie przeprowadzono nowego ręcznego testu okna startowego ani badania obsługi przez początkującego użytkownika. Sprawdzono rzeczywisty serwer nowego EXE w przeglądarce.

Artefakty testu: `build/five-years-20261001/` (evidence.json, browser-evidence.json, pdf-evidence.json, exe-report.pdf i rendery). Paczka: `release/AutoReportAnalyst-Windows-2026-10-01-five-years.zip`.
