# Trzy dashboardy analityka i eksport prezentacji
Data: 2026-09-18. Etap 1–2: specyfikacja i makieta, przed wdrożeniem nowego układu.

## Status i odbiorca
POTWIERDZONE: istniejący silnik analizuje date/value/category i wspiera wspólne filtry oraz PDF.
HIPOTEZA: analityk potrzebuje przełączania pomiędzy wynikiem, źródłami zmiany i jakością, a potem prezentacji tego samego zakresu.
UNKNOWN: rzeczywiste zadania odbiorcy, preferowana gęstość informacji i oszczędność czasu.
Najmniejszy test: wskazanie zmiany, kategorii z największym wkładem oraz ograniczenia danych, a następnie wyeksportowanie 3 slajdów. Czas mierzyć, próg uzgodnić przed próbą.

## Wspólne zasady
- Ten sam plik, profil, daty, kategorie i deklaracja kompletności we wszystkich widokach i eksporcie.
- Przełączanie widoku nie resetuje filtrów.
- Suma, liczba i średnia zachowują definicje DASHBOARD_CONTRACT.md. Zmiany średnich liczone przed zaokrągleniem.
- Brak danych, brak pozycji i suma zero są odrębnymi stanami.
- Porównania wymagają kompletnego zakresu obu okresów i pozycji w obu. Procent wymaga dodatniej bazy.
- Kwoty ujemne w strukturze są prezentowane osobno poniżej zera. Bez pierścienia dla ujemnych agregatów lub sumy <=0.
- Pierwsza implementacja: dzień/tydzień. Miesiąc tylko dla dłuższych zakresów, z oznaczeniem częściowych miesięcy.
- Źródła, konfiguracja importu i szczegółowa diagnostyka w osobnym panelu. Na każdym ekranie widoczny skrócony status jakości.
- Ekran 1280×800: KPI i główny wykres bez przewijania. Szczegółowe tabele mogą być niżej.

## Widok 1 — Wynik i trend
Pytanie: co zmieniło się w wybranym okresie?
KPI: suma PLN, liczba pozycji, średnia PLN; poprzednia wartość i procent zmiany.
Główne panele: dwa szeregi bieżącego/poprzedniego okresu oraz ranking wartości kategorii.
Drugie panele: struktura kategorii w czasie oraz tabela z różnicą i miniwykresem.
Porównanie osi X: kolejny dzień okresu, nie nakładanie różnych dat jako tej samej daty. Tooltip i eksport podają oba zakresy.
DoD: suma bieżących dni = suma KPI; porównanie ma identyczny filtr kategorii; luka nie tworzy fikcyjnej zerowej wartości.

## Widok 2 — Kategorie i źródła zmiany
Pytanie: które kategorie odpowiadają za zmianę wartości?
KPI: różnica całkowita PLN, największy bezwzględny wkład kategorii (z zachowaniem znaku), liczba kategorii.
Główne panele: rozbieżne słupki różnic od zera oraz struktura w czasie.
Drugie panele: bieżący/poprzedni okres w kategorii i tabela z miniwykresami.
Przy wyborze kategorii aktualizujemy wspólny filtr; widoczny reset do wszystkich.
Kategorie pochodzą z sumy zbiorów obu okresów. Top N grupuje resztę jawnie; pełna tabela dostępna.
DoD: suma wkładów = zmiana KPI, również dla kategorii występującej tylko w jednym okresie. Brak wniosku o przyczynie biznesowej.

## Widok 3 — Jakość i pokrycie
Pytanie: jakie są ograniczenia wyniku?
KPI: rekordy źródła, powtórzenia i kwoty ujemne, status deklarowanej kompletności.
Główne panele: kalendarz obecności oraz rozliczenie filtrów.
Drugie panele: liczba rekordów w czasie oraz jawne reguły interpretacji.
Powtórzenia liczone po normalizacji date/value/category; nie są automatycznie błędem.
DoD: licznik źródła = poza datami + wykluczone kategorią w datach + w widoku.
Nie wprowadzamy procentowego „wyniku jakości”. Deklaracja kompletności nie staje się dowodem dostarczonym przez program.

## Kontrakt eksportu PPTX
Format 16:9. Bieżący widok = 1 slajd, wszystkie = 3 slajdy w kolejności 1–3; bez automatycznej okładki.
Eksport korzysta z niezmiennej migawki ukończonej analizy. Zmiana filtrów unieważnia przygotowany plik.
Każdy slajd zawiera tytuł, zakres, jednostkę, wybór kategorii i istotne ograniczenia.
SHA-256 źródła, profil, dokładne filtry i wersja szablonu w notatkach slajdu.
Tytuł i opcjonalny komentarz są edytowalne; pierwsza wersja może zawierać wykresy jako obrazy.
Podział pełnych tabel: slajd pokazuje jawne Top N i pozostałe, a nie nieczytelne tysiące wierszy. Pełny raport nadal dostępny w aplikacji.
Brak eksportu błędnego albo pustego wyniku.
Makieta: gotowy PPTX przedstawia trzy stałe widoki demo. To próbka formatu, nie implementacja eksportera dowolnych danych.

## Artefakty pierwszego etapu
- design/analyst-dashboard.html — samodzielna makieta z działającą nawigacją trzech widoków.
- design/analyst-dashboard.template.html — szablon makiety.
- scripts/prepare_analyst_design.py — dane demo liczone istniejącym silnikiem, z niezależnymi oczekiwaniami.
- output/presentations/AutoReport-koncepcja-3-widokow-v3.pptx — trzy odpowiadające widokom slajdy.
- build/analyst-design — dane, rendery i dowody kontroli.

Wzorzec: suma 1250,00 PLN / 7 / 178,57 PLN; baza 1000,00 PLN; różnica 250,00 PLN; +25%.
Kategorie: Papier 550,00 (+100,00), Teczki i segregatory 450,00 (+150,00), Środki czystości 250,00 (+0,00).
Kompletność zadeklarowana w scenariuszu demonstracyjnym, nie zweryfikowana u klienta.

## Następne zadania
| Zadanie / artefakt | Zależność | Test / DoD | Ryzyko |
|---|---|---|---|
| Szeregi porównawcze i agregacje w silniku | Kontrakt widoków | Wzorce granic dat, braków, ujemnych kwot i częściowych okresów | Rozbieżne zakresy |
| Wspólna nawigacja i filtry aplikacji | Makieta | Zmiana widoku zachowuje filtry; zmiana źródła usuwa stare wyniki | Stare dane pod nowym nagłówkiem |
| Wdrożenie trzech widoków | Analiza i nawigacja | Liczby zgodne z niezależnym wzorcem; test 1280×800 | Gęstość i nieczytelność |
| Produkcyjny eksporter PPTX | Gotowe widoki | 1/3 slajdy, te same filtry, poprawny render każdego slajdu | Rozjazd ekranu i prezentacji |
| Paczka Windows i test użytkownika | Eksporter | Eksport z EXE i samodzielne 3 zadania analityka | Zależności i brak wartości |
