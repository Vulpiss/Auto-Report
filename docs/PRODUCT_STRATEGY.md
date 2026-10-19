# Auto-Report — produkt i oferta
Stan 2026-09-14. Szkic do walidacji, nie opublikowana oferta ani deklaracja działających funkcji.

## Punkt wyjścia
POTWIERDZONE: właściciel nie ma dostępu do klienta.
HIPOTEZA: mała hurtownia ręcznie przygotowująca tygodniowy raport sprzedaży dla właściciela. Wybór wynika z podobieństwa do date/value/category w kodzie, nie z dowodu rynkowego.
UNKNOWN: częstotliwość, czas, koszt błędów i chęć zakupu.

## Zastosowanie $100M Offers
Równanie wartości zwiększa wagę wyniku i wiarygodności jego uzyskania, a zmniejsza czas oczekiwania i wysiłek. Źródło: [oficjalna checklista Acquisition.com](https://www.acquisition.com/hubfs/Offer%20Checklists%20-%20PDF%20Downloads/Pricing-Value-Checklist.pdf?hsLang=en).
Nasza adaptacja:
- Wynik: raport gotowy na spotkanie, który odbiorca faktycznie wykorzystuje.
- Wiarygodność: próbka na jego eksporcie, zgodność sum, widoczne błędy.
- Czas: zapisany profil i powtarzalne generowanie, mierzone razem z eksportem i kontrolą.
- Wysiłek: konfiguracja pierwszego formatu po naszej stronie, drugi raport samodzielnie.
- Ryzyko: płatność po spełnieniu jasno ustalonych kryteriów pilota.

Nie traktujemy książek jako gwarancji sprzedaży. Siła oferty wymaga dowodów, nie sztucznych bonusów i zawyżonych wycen.

## Wąskie MVP — hipoteza
Przed: eksport → czyszczenie → grupowanie → kontrola sum → skład raportu.
Po: eksport w ustalonym formacie → wybór pliku → walidacja → raport do kontroli i użycia.
Jeden profil CSV, jawne mapowanie, separator, kodowanie i daty.
Proponowana semantyka: jeden rekord = pozycja sprzedaży, date = data sprzedaży, value = wartość netto pozycji w PLN, category = kategoria. Potwierdzić na eksporcie. Liczba pozycji nie jest liczbą zamówień.
Jedna waluta i definicja netto/brutto; bez danych osobowych. Zwroty i duplikaty wymagają reguł. Identyczne wiersze nie są automatycznie usuwane.
Raport tygodniowy: suma, liczba i średnia pozycji, kategorie, trend, porównanie przy potwierdzonej bazie, zakres i jakość.
Desktop Windows, lokalne przetwarzanie, zapisany profil. Poprawność do grosza.
Poza MVP: SaaS, wiele firm, API, prognozy, LLM i uniwersalny import wszystkiego.

## Oferta pilota — robocza
> Zamienimy Twój powtarzalny eksport sprzedaży w sprawdzalny raport dla właściciela. Ustawimy jeden format i szablon, uzgodnimy sumy z obecnym raportem i przeprowadzimy dwa cykle raportowania. Za wdrożenie zapłacisz po spełnieniu ustalonych kryteriów: poprawne liczby i samodzielne przygotowanie kolejnego raportu w krótszym czasie.

Zakres: jeden eksport, szablon, konfiguracja, instrukcja, dwa cykle i jedna korekta w tym zakresie.
HIPOTEZA ceny testowej: 790 zł za cały pilot, do sprawdzenia w rozmowach. Sposób rozliczenia i podatku doprecyzować w konkretnej ofercie. Dalsze utrzymanie i kolejne formaty osobno.
HIPOTEZA terminu: próbka do 3 dni roboczych od kompletnego eksportu i definicji. Termin można potwierdzić dopiero po naprawie błędów.
Propozycja ograniczenia ryzyka: brak opłaty za niespełnione kryteria, bez nieograniczonej darmowej rozbudowy. Konkretne zobowiązanie klientowi wymaga zatwierdzenia przez właściciela.

## Wartość, pomiar i ekonomika
Proponowany cel pilota: minimum 50% mniej aktywnego czasu w dwóch cyklach; to cel do uzgodnienia, nie zmierzony wynik.
Mierzymy eksport, czyszczenie, obliczenia, kontrolę, poprawki i zapis. Wdrożenie liczymy oddzielnie.
Kryteria: zero niewyjaśnionych różnic sum do 0,01 PLN przy tych samych zasadach zaokrągleń; zgodna liczba pozycji; drugi cykl bez pomocy autora; zapisane poprawki; płatność po akceptacji.
Korzyść miesięczna w godzinach = (minuty przed − po) × liczba raportów / 60.
Stawka czasu pochodzi od klienta; odzyskany czas nie oznacza automatycznie gotówkowej oszczędności.
Mierzymy też godziny naszego wdrożenia i wsparcia × wewnętrzny koszt godziny. Indywidualne programowanie dla każdego klienta oznacza usługę, nie potwierdzony powtarzalny produkt.

## Alternatywy — pytania do klienta
| Alternatywa | Warunek sensu Auto-Report |
|---|---|
| Obecny Excel lub szablon | Mierzalnie mniej pracy niż ponowne użycie obecnego arkusza |
| Raport w systemie sprzedaży | Konkretny brak potrzebnego układu lub dodatkowa ręczna praca |
| Własny skrypt | Wartość samodzielnego użycia i utrzymania |
| BI | Potrzeba niewypełniona przez działający raport klienta |
To hipotezy przewag, nie stwierdzenia o możliwościach konkretnych narzędzi.

## Decyzje
GO do pilota: naprawione ryzyka poprawności, próbka zaakceptowana, realny odbiorca i kryteria.
GO do dalszej sprzedaży: opłacony pilot, ponowne użycie i zmierzony wynik. Powtarzalność sprawdzić następnie w co najmniej drugiej niezależnej firmie.
PIVOT: problem istnieje, ale większą wartość ma inny odbiorca, format albo raport.
STOP wariantu: nieusunięte błędy lub brak problemu wartego rozwiązania w rozmowach. Mała próba nie rozstrzyga całego rynku.
