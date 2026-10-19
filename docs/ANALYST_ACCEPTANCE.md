# Domknięcie dashboardów — analityk małej hurtowni
Data: 2026-09-20. Dokument roboczy do pilotażu.

## Odbiorca i wynik
POTWIERDZONE: właściciel wybrał analityka małej hurtowni jako pierwszego odbiorcę.
HIPOTEZA: co tydzień przygotowuje podsumowanie wartości pozycji i trzy slajdy dla właściciela hurtowni.
UNKNOWN: rzeczywisty czas, system źródłowy, znaczenie daty i kwoty, format prezentacji odbiorcy.
Przed: opisać obecny eksport, czyszczenie, obliczenia i skład slajdów; zmierzyć czas.
Po: ten sam poprawny eksport → trzy odpowiedzi → PPTX. Oszczędność pozostaje do pomiaru.

## Trzy zadania
1. Wynik: podaj wartość, liczbę i średnią pozycji oraz zmianę wobec poprzedniego równego okresu. Wskaż oba zakresy i jednostkę.
2. Kategorie: wskaż największy bezwzględny wkład w zmianę. Sprawdź kategorię wspólnym filtrem. Nie utożsamiaj wkładu z przyczyną.
3. Wiarygodność i przekazanie: wskaż ograniczenie kompletności, powtórzenia i kwoty ujemne. Wyeksportuj jeden i trzy slajdy z właściwymi filtrami.
Każde zadanie zaliczone tylko przy poprawnej odpowiedzi i bez obliczeń pomocniczych poza aplikacją.

## Stan siedmiu kroków
| Krok | Artefakt i wykonanie | Zależność / DoD | Ryzyko |
|---|---|---|---|
| 1. Zadania analityka | Karta powyżej; odbiorca wybrany przez właściciela | Potwierdzenie trzech zadań przez odbiorcę: oczekuje | Nietrafny proces |
| 2. Kontrakt | DASHBOARD_CONTRACT.md i karta źródła poniżej | Trzy rzeczywiste eksporty z jednego źródła bez ręcznych zmian: oczekuje | Znaczenie danych |
| 3. Wzorce | test_analyst_acceptance.py + dotychczasowe testy | 63 testy przechodzą; wzorce syntetyczne, nie eksporty odbiorcy | Brak reprezentatywności |
| 4. Widoki | Unikalne grupy agregowane, tabela po 100 kategorii, definicje KPI, stałe kolory porównań | Regresja i test interfejsu; przydatność potwierdza odbiorca | Gęstość widoku |
| 5. PPTX | Eksport 1/3 slajdów, zakres i pełne filtry w notatkach | Otworzenie w PowerPoint odbiorcy: oczekuje | Oczekiwanie edytowalnych wykresów |
| 6. Dostarczenie | Oddzielny ZIP, benchmark_analyst.py, Test-AnalystWindows.ps1 | Test na czystym Windows: oczekuje | Inne środowisko |
| 7. Dwa cykle | Formularz poniżej i pilot_cycles.csv | Dwa rzeczywiste cykle: oczekuje | Brak przewagi nad Excelem |

## Karta jednego źródła do zatwierdzenia
System / wersja / sposób eksportu: ______
Jeden wiersz oznacza: ______
date oznacza (wystawienie, realizację lub inne): ______
value oznacza (wartość całej pozycji, nie cena jednostkowa): ______
Waluta: PLN. Podstawa netto/brutto: ______
category oznacza: ______
Ujemne pozycje oznaczają: ______. Powtórzenia oznaczają: ______
Eksport obejmuje wszystkie pozycje z zakresu: ______. Potwierdza: ______
Obecny raport odniesienia i osoba sprawdzająca: ______
Trzy eksporty: data / SHA-256 / zgodność schematu / zgodność sum: ______
Nie mieszamy walut, podstaw kwot ani różnych znaczeń daty w jednym imporcie.

## Próba PowerPoint i decyzja o edytowalności
Obecny zakres: 16:9, edytowalne tytuły i komentarze, wykresy i tabele jako obrazy.
Odbiorca potwierdza, czy musi zmieniać dane wykresu po eksporcie: TAK / NIE / nie ustalono.
Jeśli TAK: osobna zmiana zakresu na natywne wykresy. Nie uznajemy obecnego eksportu za spełniający tę potrzebę.
Sprawdzić: jeden slajd, trzy slajdy, długi tytuł, komentarz, daty, polskie znaki, filtry w notatkach, czytelność po wyświetleniu na docelowym ekranie.
Wersja PowerPoint / wynik / potrzebne ręczne poprawki: ______

## Kryteria przed pilotem
Propozycje do uzgodnienia z odbiorcą, nie deklaracja osiągnięcia:
- 0,00 PLN różnicy wobec niezależnego wzorca; identyczna liczba pozycji.
- Wszystkie trzy zadania poprawnie i bez pomocy autora w drugim cyklu.
- 0 ręcznych zmian układu slajdów poza treścią komentarza i tytułu.
- Czas aktywnej pracy: uzgodniony maksymalny czas ______ min lub oszczędność ______%.
- Import i analiza na komputerze odbiorcy: próg ______ s; eksport PPTX: ______ s.
- Brak otwartych błędów zmieniających liczby, zakres lub kompletność.
Akceptacja kryteriów, osoba i data: ______

## Dwa cykle
W pilot_cycles.csv wpisuj faktyczne wyniki, nie szacunki. Puste pola oznaczają UNKNOWN.
Osobno zmierz eksport źródła, przygotowanie danych, analizę/kontrolę, ręczne poprawki, eksport slajdów i pomoc autora.
Zachowaj SHA-256 źródła, referencyjne sumy, filtr kategorii, daty oraz wersję programu.
Po cyklu 1 napraw udokumentowane przeszkody. Cykl 2 wykonuje odbiorca samodzielnie.
Deklaracja ponownego użycia ma być poparta drugim wykonanym raportem.

## Decyzja
GO techniczne: można przekazać wydanie do kontrolowanego testu po lokalnej weryfikacji.
GO dla zamknięcia zakresu: dopiero po spełnieniu powyższych kryteriów w dwóch rzeczywistych cyklach.
PIVOT: poprawne wyniki, ale zadania lub eksport nie pasują do procesu.
STOP dla danego wariantu: nierozwiązane błędy liczb albo brak problemu wartego rozwiązania.
Obecnie: brak podstaw do uznania zakresu za ostateczny lub produktu za gotowy do sprzedaży.
