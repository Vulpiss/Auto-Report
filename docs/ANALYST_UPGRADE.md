# Ulepszenia analityka — 2026-09-23

## Stan
POTWIERDZONE: 84 testy automatyczne przeszły. Test przeglądarkowy obejmuje import, mapowanie, nowe metryki, trzy widoki, miesiące, tryb prezentacyjny, zapis/odtworzenie sesji i eksport PDF/PPTX.
Nowe testy sprawdzają też odtworzenie sesji na świeżym ekranie oraz blokadę sesji innego CSV.
UNKNOWN: natywne otwarcie i edycja wykresów w PowerPoint odbiorcy, czysty Windows i oszczędność czasu w rzeczywistym procesie hurtowni. GO dotyczy testu technicznego.

## Import i profile
Podgląd pokazuje pierwsze 5 rekordów. Najpierw ustaw kodowanie i separator. Przycisk „Zatwierdź proponowane kolumny” stosuje propozycję opartą wyłącznie o nazwy; format daty, waluta i znaczenie kwoty nadal wymagają decyzji użytkownika.
Kolumny wybiera się z listy. „Zapisz profil” pobiera JSON; „Profil lub sesja JSON” i „Przywróć profil / sesję” pozwalają zastosować go do następnego eksportu.
Profil z trzema kolumnami nadal działa.

## Kontrakt dodatkowych danych
- Ilość: jawna wspólna jednostka (np. szt.), do 6 miejsc dziesiętnych. Nie sumuj różnych jednostek.
- Zamówienie: stabilny identyfikator; liczba = liczba różnych identyfikatorów po filtrach. Nie jest to liczba pozycji.
- Produkt i klient: identyfikator lub nazwa, do 200 znaków.
- Koszt ALBO zysk: kwota całej pozycji, nie koszt jednostkowy. Ta sama waluta i podstawa co wartość pozycji. Koszt jednostkowy należy wcześniej przeliczyć według uzgodnionej reguły; program nie zgaduje.
- Potwierdzenie znaczenia wartości jako sprzedaży umożliwia zysk = wartość - koszt oraz marżę = zysk / wartość sprzedaży. Marża wymaga dodatniego mianownika.
- Zysk podany w kolumnie może być ujemny. Kwoty kosztu i ilość ujemna wymagają dopuszczenia wartości ujemnych.
- Brak w mapowanej kolumnie wyłącza zależną metrykę w danym zakresie (N/A); nie wyłącza metryk niezależnych. Błędna niepusta liczba blokuje import.
- Zaokrąglenie kosztu/zysku jest jawne, zgodne z regułą profilu; diagnostyka pokazuje wpływ na źródło.
- Średnia zamówienia dotyczy tylko pozycji po filtrach. Filtr produktu może obejmować fragment zamówienia.

## Analiza zmian i okresy
Kategorie, produkty i klienci mają wspólne filtry dla metryk i eksportu. Tabele wkładów produktu/klienta pokazują top 20 według bezwzględnej zmiany; suma wszystkich grup jest podana osobno.
Zaznacz wiersz i użyj „Pokaż pozycje wybranego…”; filtr aktualizuje analizę. Sekcja szczegółów zawiera numery wierszy źródłowych.
Wkład w zmianę to rozkład arytmetyczny, nie dowód przyczyn biznesowych.
Dostępne: dzień, tydzień, miesiąc; szybkie zakresy 7/30/90 dni i rok do ostatniej daty pliku.
Rok do roku porównuje analogiczne daty poprzedniego roku. Zakresy o różnej liczbie dni wskutek 29 lutego są jawnie blokowane; wybierz zakres bez tej różnicy lub poprzedni okres. Nie stosujemy cichego wyrównania ani podwójnego liczenia 28 lutego.
Porównania nadal wymagają deklaracji kompletności. Niepełny miesiąc/tydzień ma oznaczenie. Limity 20 MB, 100000 pozycji i okres 1–366 dni pozostają.

## Prezentacja i eksport
Tryb prezentacyjny ukrywa panel boczny i zwiększa wysokość wykresów do 560 px; wyłącz go tym samym przełącznikiem.
Dwa układy PPTX:
- Dashboardy: dotychczasowe trzy plansze (wykresy jako obrazy).
- Edytowalne wykresy: jeden duży natywny wykres na slajd; osadzony XLSX i cache pochodzą z tej samej analizy. Wymiar zmiany wybierz: kategorie, produkty lub klienci. Dostępny eksport jednego lub trzech widoków.
Przy brakujących okresach natywny eksport pokazuje znane wartości słupkami z jawną liczbą pominiętych okresów. Nie zamienia braków w zero. Bez podstaw do wykresu pokazuje komunikat zamiast wymyślonego wykresu.
Filtry, okres, jednostki i reguły są widoczne na slajdach; pełne metadane i komentarz są w notatkach. Skróty komentarza są oznaczone.
PDF zawiera osobną stronę metryk biznesowych i reguł, jeśli dodatkowe metryki są dostępne.
Walidacja OOXML sprawdza zgodność wartości wykresów z osadzonymi arkuszami. Render nie potwierdza działania konkretnej wersji PowerPoint.

## Sesje
„Zapisz sesję” zapisuje profil, filtry, grupowanie, porównanie, widok, tytuł, komentarz i styl eksportu.
CSV nie jest osadzany. Zachowaj go osobno. Przywrócenie sprawdza SHA-256: inny plik nie może odziedziczyć deklaracji kompletności i zakresu. Dla nowego CSV użyj profilu.

## Zestaw kontrolny
sample_data/wholesale_business.csv i wholesale_business.profile.json.
Ustaw 2026-09-01–2026-09-03; dla testu „Rok do roku” deklaracja kompletnego sztucznego eksportu 2025-09-01–2026-09-30.
Oczekiwania: 600 PLN, 3 pozycje, 2 zamówienia, 12 szt., koszt 370 PLN, zysk 230 PLN, średnia zamówienia 300 PLN, marża 38,33%.
Poprzednio 300 PLN; zmiana +300 PLN (+100%). Produkt P1: +400 PLN; P2: -100 PLN. Klienci C1 i C2: po +150 PLN.
Filtry P1 i C1: wartość 150 PLN, 3 szt., 1 zamówienie, zysk 60 PLN.
Dowody lokalne: build/upgrade-20260923/tests-final-v2.log, expected.json, browser/evidence.json oraz pliki walidacji slajdów.

Końcowy test EXE: import, propozycja mapowania, metryki, trzy widoki, miesiące, tryb prezentacyjny, natywne PPTX, PDF, odtworzenie sesji oraz zaznaczenie produktu i filtr źródłowych pozycji przeszły. Dowód: build/upgrade-20260923/delivery/evidence.json. Testy końcowe: tests-delivery.log (84/84). W ZIP plik wholesale_business.csv i jego profil JSON znajdują się obok EXE.
