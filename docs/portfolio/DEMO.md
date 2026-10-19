# Demonstracja portfolio

Materiał przedstawia rzeczywiste działanie aplikacji na sztucznych danych.
Nagranie jest bez dźwięku. Nie jest testem samodzielności użytkownika ani
pomiarem oszczędności pracy.

## Scenariusz do pokazania

1. Wybierz przykład w prostym trybie i kliknij „Utwórz raport”.
   Pokaż 2 250,00 PLN, 14 pozycji i średnią 160,71 PLN.
2. Wybierz ostatnie siedem dni. Wynik: 1 250,00 PLN, 7 pozycji,
   średnia 178,57 PLN. Pobierz PDF dla 07–13.09.2026.
3. Przełącz kategorie i jakość danych. Wyjaśnij, dlaczego brak
   potwierdzonej kompletności oznacza niedostępne porównanie.
4. Wybierz przygotowany błędny CSV. Kwota `abc` w linii 10 i brak
   kategorii w linii 14 mają wskazówki; PDF jest zablokowany.
5. Wybierz poprawny CSV i ponów import. Wynik całego pliku wraca
   do 2 250,00 PLN. Poprzednia lista błędów nie pozostaje na ekranie.

Automatyczna demonstracja ma przygotowany profil tego sztucznego formatu
w osobnym katalogu ustawień. Pierwszy nieznany format użytkownik konfiguruje
samodzielnie lub importuje uzgodniony profil.

## Materiały

- `media/demo.mp4`: nagranie interfejsu, nie makieta.
- `media/overview.png`, `media/categories.png`, `media/quality.png`:
  aktualne zrzuty trzech widoków.
- `media/diagnostics.png`: wskazane miejsca do poprawy.
- `demo-report.pdf`: kopia wzorcowego PDF pobranego z aplikacji.
- `expected.json`: oczekiwania obliczone niezależnie przez csv/Decimal.
- `VERIFICATION.md`: zakres, dowody i granice kontroli.
- `bad-example.csv`, `corrected-example.csv`: oba sztuczne pliki używane
  przy demonstracji poprawy danych.

## Odtworzenie materiałów

Skrypt `scripts/prepare_portfolio.py` uruchamia aplikację z kodu albo
wskazanego EXE, w oddzielnym katalogu ustawień. Wymaga Python 3.11
z `requirements-qa.txt`, Node, Playwright z obsługą Edge oraz kodera ffmpeg.
Nie są to dodatkowe zależności aplikacji użytkownika.

```powershell
python scripts/prepare_portfolio.py --exe release/analyst-2026-10-04-portfolio/AutoReportAnalyst/AutoReportAnalyst.exe --ffmpeg ŚCIEŻKA_DO_FFMPEG.exe
```

Bez `--exe` skrypt uruchamia serwer z bieżącego kodu. Ścieżkę do pakietu
Playwright można przekazać zmienną `AUTOREPORT_PLAYWRIGHT_DIR`.
Skrypt nie wysyła danych ani nie dotyka istniejących raportów użytkownika.
Wewnętrzny koder Playwright jest umieszczany w katalogu roboczym projektu.

Nagranie prezentuje kolejność zdarzeń w kontrolowanej sesji. Czas nagrania
obejmuje pauzy do obejrzenia ekranów i nie jest benchmarkiem.
