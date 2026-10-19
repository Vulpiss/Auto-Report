# Próba pierwszego użycia — protokół do wypełnienia

Status: niewykonana. Oddziel próbę autora w VM od próby nowego użytkownika.
Obserwator nie podpowiada; każde wyjaśnienie zapisuje jako pomoc.

Tester / obserwator / data: ______. Autor projektu: TAK / NIE.
ZIP i SHA-256: ______. Windows / build / RAM / skala ekranu: ______.
VM / komputer; pochodzenie instalacji i migawka: ______.
Python/Office zainstalowane: ______. Sieć odłączona po instalacji: ______.

## Zadania

1. Rozpakuj cały ZIP aplikacji. Uruchom EXE przez okno launchera, zaznacz demo
   i utwórz raport. Odczytaj 2 250,00 PLN, 14 pozycji, średnią 160,71 PLN
   oraz okres 31.08–13.09.2026. Wskaż, że kompletność eksportu nie jest zadeklarowana.
2. Wybierz ostatnie siedem dni. Odczytaj 1 250,00 PLN, 7 pozycji, średnią
   178,57 PLN i 07–13.09.2026. Pobierz PDF, otwórz go i sprawdź liczby,
   daty, polskie znaki, wykres oraz obie strony.
3. Zamknij program przyciskiem w launcherze. Sprawdź brak działającego serwera
   pod poprzednim adresem. Uruchom ponownie i wybierz `fixtures/corrected-example.csv`.
   Sprawdź konfigurację kolumn/date/value/category, format ISO, kropkę dziesiętną,
   PLN i nieokreślone netto/brutto. Zapisz, czy program przypomniał ustawienia.
4. Wczytaj `fixtures/bad-example.csv`. Znajdź błędną kwotę `abc` w linii 10
   i pustą kategorię w linii 14. Pobierz problemy do CSV. Sprawdź brak przycisku
   pobrania nowego PDF dla błędnego importu.
5. Wczytaj poprawiony plik, utwórz drugi poprawny raport i pobierz jego PDF.
   Sprawdź pełną sumę 2 250,00 PLN, czytelność PDF i zniknięcie wcześniejszych błędów. Nie poprawiaj wejściowego pliku
   referencyjnego; demonstracyjna poprawiona kopia jest już w pakiecie.
6. Wyjaśnij: liczba pozycji nie oznacza liczby zamówień; brak deklaracji
   kompletności uniemożliwia wiarygodne porównanie; sam wzrost sumy nie
   uzasadnia zwiększenia skali działalności. Zakończ program przyciskiem.

| Zadanie | Czas aktywny / oczekiwanie [min] | Wynik i odpowiedź | Pomoc / błąd / dowód |
|---|---|---|---|
| 1 | | UNKNOWN | |
| 2 | | UNKNOWN | |
| 3 | | UNKNOWN | |
| 4 | | UNKNOWN | |
| 5 | | UNKNOWN | |
| 6 | | UNKNOWN | |

DoD: wszystkie liczby i zakresy zgodne, dwa PDF czytelne, poprawa błędu
zrozumiała, zamknięcie i ponowny start działają. Nowy użytkownik wykonuje
drugi raport bez pomocy autora. Próg czasu ustalić przed próbą; puste pole
nie oznacza spełnionego kryterium. Do szerszego testu użyć trzech nowych osób.

Wynik techniczny VM: UNKNOWN. Samodzielność nowego użytkownika: UNKNOWN.
Blokujące przeszkody i poprawki: ______. Powtórna próba po poprawce: ______.
Po próbie demonstracyjnej osobno sprawdzić rzeczywisty eksport według
[DATA_AGREEMENT.md](DATA_AGREEMENT.md) i [NUMBERS.md](NUMBERS.md).
