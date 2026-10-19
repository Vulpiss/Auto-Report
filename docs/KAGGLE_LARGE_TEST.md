# Test dużego Kaggle CSV — 2026-09-23

POTWIERDZONE: pobrano https://www.kaggle.com/datasets/carrie1/ecommerce-data przez publiczny endpoint Kaggle.
Oryginał: data/external/kaggle-large/data.csv, 45 580 638 bajtów, 541 909 rekordów.
SHA256: d07aec9960083af2339975a3f9d3b26313b342dcd9f86cce0b919b1cde639a44.

## Wynik
Pełny CSV odrzucony: limit 20 MiB. Osobny plik po konwersji zawierający 100 001 rekordów odrzucony przez limit 100 000 rekordów. To poprawne działanie zabezpieczeń, ale ograniczenie zastosowania do dużych eksportów.

Pierwsze 100 000 rekordów przekształcono jawnie: daty z godzinami -> daty ISO, wartość pozycji = Decimal(Quantity) × Decimal(UnitPrice), Country jako kategoria. Zachowano zwroty, brakujące identyfikatory i powtórzenia. Waluta XXX, kompletność niepotwierdzona. Nie jest to losowa reprezentatywna próbka całego zbioru. Identyfikatory faktur obejmują anulowania; nie oznaczają wyłącznie zrealizowanych zamówień.

- Import 3,914 s; analiza 0,379 s.
- Modele dashboardów: dzień 0,037 s, tydzień 0,035 s, miesiąc 0,035 s.
- Suma próbki: 1 727 708,42 j.p.; ilość: 889 292; 4657 różnych numerów faktur.
- Niezależne obliczenia Decimal potwierdziły kwoty, liczbę wierszy, ilości, liczbę faktur i filtry wszystkich krajów.
- PPTX: 3 slajdy, integralność ZIP potwierdzona; eksport 0,179 s. Nie testowano otwarcia w PowerPoint ani wyglądu slajdów dla tej próbki.
- PDF: 3 strony, eksport 0,419 s; render wszystkich stron sprawdzony wizualnie, bez obcięć treści.
- To jednorazowe pomiary silnika na tym komputerze, nie benchmark UI, pamięci ani wersji EXE. Nie wykonano testu przeglądarki.
- Brak kosztów/zysku daje N/A; brak potwierdzonego pokrycia blokuje porównanie okresów.

## Istotne ograniczenia
1. Pełne 541 909 rekordów nie zostało przeanalizowane w aplikacji.
2. Surowe daty zawierają godziny, a kwota wymaga mnożenia dwóch kolumn. Obecną konwersję wykonuje skrypt QA, nie importer aplikacji.
3. Źródło ma 135 080 brakujących CustomerID i 10 624 ujemnych ilości.
4. W próbce 34 915 pozycji nie ma CustomerID.
5. Reguła powtórzeń liczy zgodność daty, kwoty i kategorii: 76 711. Identycznych pełnych wierszy po projekcji jest 924. To różne definicje; nie wolno usuwać 76 711 pozycji jako zduplikowanych transakcji. PDF poprawnie opisuje regułę, zachowuje wiersze i zaznacza, że powtórzenia nie dowodzą błędu.

UNKNOWN: kompletność biznesowa, netto/brutto, reprezentatywność dla polskiej hurtowni i wydajność pełnego zbioru po przebudowie importu.
Rekomendowany kolejny krok: import porcjami z kontrolą pamięci i jawne mapowanie ceny jednostkowej × ilości oraz dat z godzinami; osobno rozróżnić powtórzenia podstawowych pól od identycznych transakcji. Samo zwiększenie limitu nie stanowi testu poprawności ani wydajności.

## Odtworzenie
Pobranie: curl.exe -L --fail https://www.kaggle.com/api/v1/datasets/download/carrie1/ecommerce-data -o data/external/kaggle-large/download.zip
Test: venv/Scripts/python.exe scripts/qa_large_kaggle.py
Dowody: build/large-kaggle-qa/evidence.json
Raport: build/large-kaggle-qa/report.pdf
Prezentacja: build/large-kaggle-qa/report.pptx
Próbka do testów: data/external/kaggle-large/sample-100000.csv
Nie zmieniano kodu produkcyjnego ani limitów.
