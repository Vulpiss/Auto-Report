# Kontrakt dashboardu Auto-Report

Wersja kontraktu: 4. Aktualizacja: 2026-09-23.
Status: reguły techniczne wdrożone w app/analysis.py i dashboardach. Historyczne obserwacje kodu w sekcjach 1 i 8 opisują stan z 18.09, sprzed implementacji. Aktualne dowody: ANALYST_ACCEPTANCE.md i ANALYST_HARDENING_RESULTS.md.

Odbiorca wybrany przez właściciela: analityk małej hurtowni. Potwierdzenie procesu i trzech eksportów klienta pozostaje UNKNOWN. Kontrakt obejmuje także PPTX; paginacja tabeli nie zmienia filtrów i eksportu. Agregowane grupy mają etykiety różne od nazw kategorii źródłowych.

## 1. Cel i dowody

- POTWIERDZONE odczytem kodu: `app/queries.py` liczy sumę, liczbę i średnią pozycji, trend dzienny, ranking i porównanie okresów. `app/pipeline.py` łączy analizę z generowaniem PDF. Filtr kategorii nie jest jeszcze zaimplementowany w tych funkcjach.
- HIPOTEZA: odbiorcą jest właściciel małej hurtowni, potrzebujący tygodniowego przeglądu wartości sprzedaży. Znaczenie danych sprzedażowych wymaga potwierdzenia u źródła.
- UNKNOWN: przewaga nad obecnym raportem odbiorcy, oszczędność czasu i popyt. Najmniejszy test: odbiorca pokazuje obecny raport oraz wykonuje trzy zadania na prototypie: wskazuje zmianę sumy, kategorię odpowiadającą za zmianę i ograniczenie jakości danych.
- Cel techniczny: dashboard i PDF pokazują identyczne liczby dla tego samego źródła, profilu, zakresu i filtrów.

Poniższe reguły są decyzjami projektowymi. Nie stanowią potwierdzenia potrzeb klienta.

## 2. Wejście i jednostki

Jeden CSV, jeden profil, jedna jawnie wybrana waluta PLN/USD/EUR/GBP lub nieokreślona jednostka j.p. (XXX). Zachowujemy istniejącą ścisłą walidację, limity 20 MB i 100 000 rekordów oraz okres 1–366 dni.

| Pole | Definicja techniczna | Czego nie zakładamy |
|---|---|---|
| `date` | Data pozycji, bez godziny; jawny format ISO, DD.MM.RRRR, M/D/YYYY lub D/M/YYYY | Data faktury nie musi oznaczać daty sprzedaży ani zapłaty |
| `value` | Kwota pozycji: domyślnie maksymalnie dwa miejsca; opcjonalne jawne HALF_UP każdej pozycji do 2 miejsc; obliczenia w całkowitych setnych jednostki | Nie jest automatycznie przychodem, zyskiem ani ceną jednostkową |
| `category` | Niepusta etykieta po usunięciu skrajnych spacji; wielkość liter pozostaje znacząca | Nie łączymy samoczynnie podobnych nazw |

Nazwy kolumn mogą być mapowane profilem. Netto/brutto/nieokreślona jest deklaracją użytkownika widoczną przy wynikach. Nie przeliczamy podatku. Kwoty ujemne wymagają jawnego dopuszczenia; pozostają w sumie i liczbie pozycji. Nie nazywamy ich automatycznie zwrotami. Powtórzenia pozostają w danych. Błędna kwota blokuje import całego pliku, nigdy nie staje się zerem.

## 3. Jeden zakres analizy

- Daty początku i końca są włączne. Domyślnie ostatnie 7 dni kończące się maksymalną datą pliku, a nie datą komputera.
- Filtr kategorii: `all` oznacza wszystkie kategorie, jawna lista oznacza dokładnie wybrane etykiety, pusta lista oznacza brak wyników. Nie wolno interpretować pustej listy jako wszystkich kategorii.
- Lista dostępnych kategorii pochodzi z całego poprawnego pliku, aby można było wybrać kategorię występującą tylko w poprzednim okresie.
- Ten sam wybór kategorii obowiązuje KPI, trend, ranking, szczegóły, porównanie oraz PDF.
- Grupowanie dzień/tydzień zmienia wyłącznie wykres, nie zakres i nie KPI. Tydzień trwa od poniedziałku do niedzieli; skrajne tygodnie są przycinane do wybranego okresu i oznaczane jako częściowe.
- Poprzedni okres ma tę samą liczbę dni i kończy się dzień przed początkiem bieżącego. Nie oznacza automatycznie poprzedniego tygodnia ani miesiąca kalendarzowego.
- Pełny zakres eksportu jest osobną deklaracją dla źródła. Pierwsza i ostatnia pozycja nie dowodzą kompletności. Oba porównywane okresy muszą mieścić się w zadeklarowanym pełnym zakresie.

Przykład: 07–13.09.2026 porównujemy z 31.08–06.09.2026. Przy wyborze kategorii A oba okresy obejmują tylko A.

## 4. Wskaźniki i zaokrąglenia

Niech R oznacza pozycje po filtrach, N ich liczbę, S sumę ich kwot w groszach. C i P oznaczają wartość wskaźnika w okresie bieżącym i poprzednim.

| Etykieta | Wzór i jednostka | Brak danych / ograniczenia |
|---|---|---|
| Wartość pozycji | S / 100, PLN | Przy N=0 karta pokazuje „Brak pozycji”; techniczna suma pustego zbioru 0 nie dowodzi zerowej sprzedaży |
| Liczba pozycji | N, liczba całkowita | Przy pustym wyborze 0; nigdy etykieta „zamówienia” |
| Średnia wartość pozycji | S / (100 × N), PLN | Przy N=0 niedostępna; nie pokazujemy 0,00 PLN |
| Różnica | C − P, jednostka danego wskaźnika | Dostępna, gdy oba okresy są kompletne i mają pozycje po filtrach |
| Zmiana procentowa | 100 × (C − P) / P | Dodatkowo wymaga P>0; inaczej „N/A” z powodem |

Kwoty wyświetlamy do 2 miejsc, procenty do 1 miejsca, z przecinkiem dziesiętnym i spacjami tysięcy. Zaokrąglenie HALF_UP wyłącznie do prezentacji. Różnice i zmiany średnich liczymy na średnich przed zaokrągleniem. Obliczenia pieniężne pozostają w groszach lub Decimal; konwersja do float może służyć wyłącznie geometrii wykresu, nie uzgadnianiu sum.

Niepełne okresy mogą pokazać opisowe sumy dostępnych pozycji z ostrzeżeniem, lecz bez różnic i zmian porównawczych. Gdy cały poprzedni okres po filtrach nie zawiera pozycji, zachowujemy konserwatywną regułę obecnego produktu: porównanie niedostępne, nawet przy deklaracji kompletności. Wzrost nie generuje zalecenia skalowania.

## 5. Widoki i wykresy

### Przegląd — pierwsza dostarczana wersja

- Nagłówek: okres, PLN i podstawa kwoty, źródło, eksport PDF.
- Filtry dat i kategorii; trzy karty KPI z dostępnymi różnicami i procentami.
- Kolumnowy trend dzienny; tygodniowy po dodaniu reguł z sekcji 3. Oś kwoty obejmuje zero i wartości ujemne. Podpowiedź pokazuje datę lub rzeczywisty zakres oraz dokładną kwotę.
- Dzień bez rekordów: „Brak pozycji”. Przy niepotwierdzonej kompletności luka, nie słupek zerowej sprzedaży. Przy pełnym zakresie można zaznaczyć brak pozycji na poziomie zera, z jawną etykietą. Zerowa suma istniejących rekordów jest osobnym przypadkiem.
- Poziomy ranking Top 5 według sumy malejąco, remisy według nazwy. Pozostałe kategorie w osobnym wierszu „Pozostałe (n kategorii)”; szczegóły dostępne w tabeli. Przy ujemnych sumach etykieta „największe wartości”, nie „najlepsze”.
- Widoczny pasek jakości; diagnostyka nie może być dostępna wyłącznie w innej zakładce.

### Kategorie — rozszerzenie po Przeglądzie

- Pełna tabela kategorii: suma, liczba, średnia, poprzednia suma i różnice.
- Poziome słupki bieżącej i poprzedniej wartości, gdy porównanie jest dostępne.
- Wkład w zmianę: różnica sum dla kategorii, słupki od zera w obu kierunkach. Kategorie stanowią sumę zbiorów etykiet z obu okresów po filtrach.
- Jeśli oba całe okresy spełniają warunki porównania, nieobecna w jednym z nich kategoria ma technicznie sumę 0 i liczbę 0, lecz średnią niedostępną. Pozwala to uzgodnić sumę różnic kategorii z różnicą całkowitą. Procent przy bazie kategorii <=0 pozostaje N/A.
- Wejście w kategorię ustawia wspólny filtr, widoczny także przy eksporcie.
- Bez wykresów kołowych, udziałów procentowych i automatycznych przyczyn biznesowych w pierwszej wersji.

### Jakość danych — podstawowe komunikaty od pierwszej wersji

- Zakres całego źródła: rekordy poprawne/błędne, powtórzenia, kwoty ujemne i profil importu. Powtórzenie oznacza ten sam zestaw znormalizowanych date/value/category, nie potwierdzony błąd biznesowy.
- Zakres widoku: pozycje po filtrach oraz liczba i suma kwot ujemnych po filtrach.
- Rozłączne liczniki: rekordy poza datami + rekordy w datach odrzucone filtrem kategorii + rekordy w widoku = wszystkie poprawne rekordy źródła.
- Deklarowany zakres kompletności i powody niedostępności porównania.
- Przy błędzie importu: przyczyna i dostępne numery wierszy. Jeżeli parser przerwał odczyt, nie przedstawiamy częściowych liczników jako pełnych. Ograniczoną listę błędów opisujemy jako próbkę.

## 6. Stany interfejsu i zgodność PDF

1. Bez pliku: instrukcja wyboru CSV, bez przykładowych liczb udających wynik.
2. Import/obliczenia: stan zajętości, eksport niedostępny do zakończenia.
3. Błąd: brak nowych wyników i eksportu; wcześniejszy zapisany PDF pozostaje na dysku.
4. Pusty wynik filtrów: „Brak pozycji”, liczba 0, średnia i porównania niedostępne, eksport raportu zablokowany.
5. Poprawny wynik: KPI, wykresy i tabela odnoszą się do jednego ukończonego obliczenia.

Zmiana źródła, profilu, filtrów lub deklaracji kompletności unieważnia wynik do czasu ponownego obliczenia. Nie wyświetlamy starego wyniku pod nowymi filtrami. PDF powstaje z tego samego wyniku analizy i zawiera okres, wybór kategorii, podstawę kwoty, ostrzeżenia i identyfikację źródła (SHA-256). PDF nie musi kopiować układu ekranu, ale musi zachować jego liczby i zakres. Kwoty serializujemy bez utraty groszy.

Przetwarzanie lokalne. Nie dodajemy automatycznego zapisu surowych rekordów na dysku ani logowania ich treści. Nazwa pliku może być etykietą w interfejsie; pełna ścieżka użytkownika nie trafia do raportu ani logów.

## 7. Ręczny przykład akceptacyjny

To specyfikacja przyszłego zestawu testowego, nie wynik wykonania dashboardu.

| Data | Kwota PLN | Kategoria |
|---|---:|---|
| 2026-09-01 | 100,00 | A |
| 2026-09-01 | 50,00 | B |
| 2026-09-02 | 200,00 | A |
| 2026-09-03 | 150,00 | A |
| 2026-09-03 | -20,00 | B |
| 2026-09-04 | 250,00 | A |

Profil dopuszcza ujemne kwoty; pełny eksport zadeklarowany na 01–04.09.2026. Okres bieżący 03–04.09, poprzedni 01–02.09.

- Wszystkie kategorie: bieżąca suma 380,00 PLN, N=3, średnia 126,67 PLN; poprzednia suma 350,00 PLN, N=3, średnia 116,67 PLN. Różnica sum +30,00 PLN; zmiana sum i średniej po prezentacji +8,6%; zmiana liczby 0,0%.
- Tylko A: bieżąca suma 400,00 PLN, N=2, średnia 200,00 PLN; poprzednia suma 300,00 PLN, N=2, średnia 150,00 PLN. Zmiana sum i średniej +33,3%.
- Wkład kategorii: A +100,00 PLN, B −70,00 PLN, razem +30,00 PLN. B ma bazę dodatnią 50,00 PLN, więc zmiana −140,0% jest dopuszczalna.
- Trend bieżący: 03.09 = 130,00 PLN; 04.09 = 250,00 PLN. Razem 380,00 PLN.
- Diagnostyka przy filtrze A: 6 poprawnych rekordów źródła = 3 poza datami + 1 odrzucony kategorią + 2 w widoku. Źródło zawiera 1 kwotę ujemną; widok A zawiera 0.
- Bez deklaracji pełnego eksportu: sumy pozostają takie same, porównania niedostępne.
- Pusta lista kategorii: stan pusty, nie powrót do wszystkich kategorii.

## 8. Różnice względem obecnego kodu i ukończenie kroku 1

Do implementacji: oddzielenie analizy od PDF, wspólny filtr kategorii, jawny stan pusty, dokładne różnice, diagnostyka zakresów, grupowanie tygodniowe, pełne agregaty kategorii i uzgodniony eksport.

W szczególności obecne `kpi_summary` zwraca średnią 0 przy braku rekordów; przyszła warstwa analizy ma zwracać niedostępność średniej dla dashboardu. Obecny pipeline już blokuje PDF pustego okresu. Obecne `top_categories` zwraca ograniczony ranking, więc nie wolno traktować jego sumy jako sumy całego zakresu. Bieżące `summary.json` nie zawiera trendu ani tabeli kategorii i nie jest jeszcze kompletnym modelem dashboardu.

DoD kroku 1: określone wejście, wzory, jednostki, zakresy filtrów, reguły N/A, stany interfejsu, wykresy, zgodność PDF i ręczne oczekiwania; rozdzielony stan obecny od projektowanego. Sprawdzono zgodność opisu stanu obecnego z kodem. Nie deklarujemy wykonania nowych testów ani gotowego dashboardu na podstawie tej specyfikacji.

Następny artefakt: pliki wzorcowe i niezależne oczekiwania z sekcji 7, rozszerzone o zerową bazę, brak kategorii w jednym okresie, granice dat i powtórzenia. Następnie wspólny moduł analizy.

## Reguły importu v3
Kodowania: utf-8-sig, cp1250, cp1252. Nie zgadujemy waluty ani kolejności dnia i miesiąca. HALF_UP raportuje liczbę zmienionych pozycji oraz dokładną różnicę sumy przed/po, także po filtrach. Powtórzenia rozpoznajemy po oryginalnej wartości, aby zaokrąglenie nie tworzyło sztucznych powtórzeń. Nie przeliczamy walut. Dowody: KAGGLE_SUPERSTORE_TEST.md.

## Reguły v4
Opcjonalne kolumny i formuły, reguły braków, filtry produktów/klientów, porównania roczne, sesje i natywne wykresy definiuje ANALYST_UPGRADE.md. Jedna waluta i jedna jednostka ilości na profil; koszt/zysk całej pozycji. Braki nie są zerami. Starsze sekcje opisujące wyłącznie trzy kolumny są zakresem podstawowym, nadal obsługiwanym.
