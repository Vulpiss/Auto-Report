# Bieżący kontrakt importu i raportu

Stan: 2026-10-04. Źródłem reguł są `app/validation.py`, `app/analysis.py`
i `app/business.py`. Starszy DASHBOARD_CONTRACT.md dokumentuje także historię.

| Pole | Warunek | Znaczenie |
|---|---|---|
| Data | Wymagana, istniejąca data w wybranym formacie | Data pozycji; znaczenie biznesowe ustala właściciel eksportu |
| Wartość | Wymagana, poprawna liczba | Kwota całej pozycji lub cena mnożona przez ilość |
| Kategoria | Wymagana, niepusta, do 200 znaków, bez znaków sterujących | Etykieta źródłowa; podobne nazwy nie są automatycznie łączone |
| Ilość | Dodatkowa; obowiązkowa dla ceny jednostkowej | Wspólna, jawnie zadeklarowana jednostka |
| Dokument, produkt, klient, koszt albo zysk | Dodatkowe, przypisane profilem | Umożliwiają powiązane wskaźniki; brak nie staje się zerem |

Separator CSV: przecinek, średnik lub tabulator. Kodowanie: UTF-8,
Windows-1250 lub Windows-1252. Nagłówki muszą być niepuste i unikalne.
Nazwy wszystkich przypisanych kolumn muszą być różne i obecne w pliku.

Daty: ISO `RRRR-MM-DD`, polskie `DD.MM.RRRR`, jawne M/D/YYYY lub D/M/YYYY,
także obsługiwane warianty z godziną. Godzina nie zmienia strefy czasowej;
rekord jest grupowany według daty zapisanej w pliku. Kolejności dnia i miesiąca
nie ustalamy na podstawie niejednoznacznego przykładu.

Kwoty: separator dziesiętny kropka albo przecinek, bez separatora tysięcy.
Domyślnie do dwóch miejsc; jawne HALF_UP pozwala zaokrąglić każdą pozycję
do dwóch miejsc, z audytem wpływu na sumę. Ujemne kwoty i ilości wymagają
odpowiedniej reguły; ujemny zysk jest dopuszczany. Jedna pozycja kwotowa
mieści się w granicy bezwzględnej 10 miliardów jednostek.

Jedna waluta profilu: PLN, EUR, USD, GBP albo XXX (j.p.). Netto, brutto
lub nieokreślona podstawa to deklaracja użytkownika, bez przeliczania podatku.

Import: maksymalnie 100 MiB i 1 000 000 rekordów. Zakres raportu jest włącznie
od początku do końca i obejmuje najwyżej pięć lat kalendarzowych: rocznica
daty końcowej pięć lat wcześniej + jeden dzień. Dla 29 lutego rocznicą jest
28 lutego. Przykład: 02.10.2021–01.10.2026.

Błąd wymaganej wartości, błędne dodatkowe pole lub zła struktura blokują
raport. Diagnostyka wskazuje fizyczne linie CSV, kolumny i sposób poprawy.
Przerwana kontrola jest oznaczana; nie udaje sprawdzenia całego pliku.
Puste pola dodatkowe są ostrzeżeniami i wyłączają zależne miary albo
ograniczają kompletność podziału. Powtórzenia pozostają w danych.

Porównanie wymaga deklaracji pełnego zakresu eksportu obejmującego oba
okresy oraz pozycji po filtrach w obu okresach. Procent dodatkowo wymaga
dodatniej bazy; w przeciwnym razie N/A z przyczyną. Pierwsza i ostatnia
data CSV nie dowodzą kompletności. Przy braku jej potwierdzenia suma
opisuje dostępne pozycje, a nie potwierdzony pełny wynik przedsiębiorstwa.

Profil jest ustawieniem odczytu; zgodne nagłówki nie dowodzą zgodnego
znaczenia biznesowego nowego eksportu. Najmniejszy test kontraktu klienta:
uzgodnić znaczenie pól, zakres i niezależny wzorzec sum z właścicielem danych.
