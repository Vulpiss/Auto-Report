# Test Kaggle Superstore — 2026-09-22

## Źródło i zakres
POTWIERDZONE: pobrano oryginalny Sample - Superstore.csv ze zbioru [Superstore Dataset](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final), wersja 1 (aktualizacja 2022-02-17). Plik lokalny: data/external/kaggle-supermarket/superstore/Sample - Superstore.csv.
SHA-256: 58fb59c63089e564d835e4aabe19d371757de1137a5bf1888243ae386c4b7a97.
9994 rekordy, 17 podkategorii, daty 2014-01-03–2017-12-30. Plik źródłowy pozostał niezmieniony.
Metadane: licencja „Other (specified in description)”, opis „For educational purposes only”, wskazane pochodzenie Tableau. CSV nie jest dołączany do dystrybucji programu.

## Blokady i zmiany
- Kodowanie cp1252 blokowało import: dodano jawny wybór cp1252.
- Daty M/D/YYYY były nieobsługiwane: dodano jawne formaty amerykański i D/M/YYYY, bez zgadywania.
- Sales zawiera ponad 2 miejsca dziesiętne: domyślny tryb ścisły nadal blokuje taki import. Użytkownik może jawnie wybrać HALF_UP każdej pozycji do 2 miejsc. Raport pokazuje liczbę zmienionych pozycji i wpływ na sumę.
- Etykieta PLN była nieuzasadniona: profil obsługuje PLN, USD, EUR, GBP oraz nieokreśloną jednostkę XXX, prezentowaną jako j.p. Nie przeliczamy walut.
- Dodano przycisk profilu Superstore: Order Date / Sales / Sub-Category, przecinek, kropka dziesiętna, cp1252, %m/%d/%Y. Przycisk pozostawia tryb ścisły; zaokrąglanie wymaga osobnego wyboru.

## Niezależne oczekiwania i wynik
Suma surowych Sales: 2297200.8603. Suma po zaokrągleniu każdej pozycji: 2297201.07. Zmieniono 4001 pozycji; wpływ +0.2097 j.p.
Okres testowy 2017-10-01–2017-12-30: 1219 pozycji, 280054.08 j.p., średnia 229.74. Zaokrąglono 503 pozycje, wpływ +0.0130 j.p.
Poprzedni równy okres 2017-07-02–2017-09-30: 900 pozycji, 195612.11 j.p.; różnica 84441.97 j.p. (+43.2%).
Kompletność 2014-01-03–2017-12-30 jest WYŁĄCZNIE założeniem testowym. Daty skrajne nie dowodzą kompletności. Bez deklaracji porównanie jest niedostępne.
11 powtórzeń klucza data / oryginalna kwota / podkategoria zachowano; nie oznacza to 11 zdublowanych zamówień.

## Dowody
71 testów automatycznych przeszło (build/kaggle-qa/tests.log).
scripts/qa_kaggle.py sprawdza SHA źródła, niezależne obliczenia Decimal/csv, filtry wszystkich kategorii, dzień/tydzień, brak deklaracji kompletności, odrzucenie w trybie ścisłym oraz PDF/PPTX.
build/kaggle-qa/evidence.json zawiera wyniki i czasy lokalnego testu.
Test przeglądarki na oryginalnym CSV sprawdził import, odrzucenie w trybie ścisłym, trzy widoki i pobranie PDF/PPTX.
PDF: dwie strony wyrenderowane i obejrzane. PPTX: trzy slajdy oraz eksport pojedynczy przeszły import, render i kontrolę wizualną. Wykresy w prezentacji są obrazami; tytuł i komentarz można edytować.

## Granice i werdykt
GO dla obsługi tego pliku w teście technicznym. UNKNOWN: waluta i podstawa netto/brutto źródła, faktyczna kompletność, użycie na czystym Windows i proces klienta.
Limity pozostają: 20 MB, 100000 pozycji, wybrany okres 1–366 dni. Można wczytać wieloletni plik, ale raport wymaga krótszego okresu.
Jedna waluta na plik; nie wolno sumować różnych walut jako jednej. HALF_UP jest świadomą transformacją, nie zachowuje pełnej precyzji źródła. Kwoty błędne nadal blokują import, a nie stają się zerem.
To zbiór edukacyjny. Wynik nie dowodzi popytu ani gotowości do sprzedaży hurtowni. Najmniejszy następny test biznesowy: anonimowy eksport odbiorcy i uzgodnienie znaczenia kwoty, daty, waluty oraz kompletności.

Test EXE na tym komputerze: oryginalny CSV, odrzucenie w trybie ścisłym, trzy dashboardy i pobranie PDF/PPTX przeszły. Paczka: release/AutoReportAnalyst-Windows-2026-09-22-kaggle.zip. Nie zastępuje to próby na czystym Windows.

Końcowa paczka: 71/71 testów (tests-final.log), test przeglądarkowy EXE ponowiony po usunięciu ostrzeżenia profilu. Integralność ZIP poprawna; CSV nieobecny w paczce. Wszystkie trzy rendery slajdów z EXE identyczne z obejrzanymi renderami wersji źródłowej. Dowody: build/kaggle-qa/frozen/release-evidence.json oraz browser-validation.json.
