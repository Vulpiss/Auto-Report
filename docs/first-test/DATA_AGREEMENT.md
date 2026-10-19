# Kontrakt jednego eksportu — do wypełnienia

Status: UNKNOWN. Brak rzeczywistego eksportu i zatwierdzenia właściciela danych.
Identyfikator firmy/procesu: ______. Osoba potwierdzająca i data: ______.

## Jeden odbiorca i raport

- Kto przygotowuje raport, kto go odbiera, do jakiej decyzji służy: ______.
- Źródłowy system, wersja, kroki eksportu i częstotliwość: ______.
- Jeden raport: wymagane liczby, okres i format przekazania: ______.
- Obecny poprawny raport odniesienia i jego autor: ______.
- Co dokładnie mierzymy jako rezultat pracy: ______.

## Definicje

| Ustalenie | Wartość potwierdzona przez właściciela danych |
|---|---|
| Jeden wiersz oznacza | ______ |
| Kolumna daty; znaczenie daty i format, reguła godziny | ______ |
| Kolumna kwoty; kwota pozycji albo cena × ilość | ______ |
| Waluta; netto/brutto; separator liczb; zaokrąglanie | ______ |
| Kolumna kategorii i jej znaczenie | ______ |
| Ilość i wspólna jednostka, jeśli używane | ______ |
| Dokument/produkt/klient/koszt albo zysk, jeśli używane | ______ |
| Zwroty i ujemne kwoty/ilości | ______ |
| Powtórzenia; sposób wyjaśnienia rzeczywistych duplikatów | ______ |
| Separator CSV i kodowanie | ______ |
| Zakres raportu i filtry | ______ |
| Pełny zakres eksportu; kto i na jakiej podstawie go potwierdza | ______ |

Aktualne ograniczenia programu: [DATA_CONTRACT.md](../DATA_CONTRACT.md).
Nie mieszamy walut, znaczeń kwot ani dat w jednym imporcie.

## Braki i błędy

- Błędne wymagane pola: raport zablokowany, poprawia osoba ______.
- Puste pola dodatkowe: ostrzeżenie; zależna miara niedostępna/ograniczona.
- Niejasne znaczenie danych: wstrzymanie odbioru do wyjaśnienia.
- Brak rekordów nie stanowi potwierdzenia zerowej sprzedaży.
- Program zachowuje źródło i powtórzenia, nie uzupełnia kwot średnią ani medianą.
- Każda uzgodniona korekta poza programem: osobna kopia, autor, powód, zakres,
  SHA-256 przed/po i wpływ na wynik. Odbiorca zatwierdza ograniczenia raportu.

## Wzorzec i odbiór

CSV / data eksportu / SHA-256: ______.
Wzorzec policzony niezależnie przez / metoda / plik odniesienia: ______.
Suma / liczba pozycji / średnia / wszystkie kategorie: ______.
Osobne wzorce opcjonalnych KPI, porównań i ich mianowników: ______.
Akceptowany sposób zaokrągleń i dopuszczalna różnica: ______.
Potwierdzenie zgodności liczb, zakresu i czytelności PDF: ______.

Kolejny eksport wymaga zgodnego znaczenia, nie tylko takich samych nagłówków.
Zmiana systemu, waluty, definicji lub reguł oznacza ponowną kontrolę profilu.
