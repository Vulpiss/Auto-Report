# Raport jednym przyciskiem — 2026-09-30

Przebieg: CSV → „Utwórz raport” → dashboard i gotowy PDF. Dotyczy wcześniej
skonfigurowanego układu eksportu. Nowy układ nadal wymaga potwierdzenia znaczenia kwoty
i niejednoznacznych ustawień. Nie deklarujemy obsługi dowolnego CSV bez konfiguracji.

Domyślny zakres to cały plik, maksymalnie 366 dni. Dłuższy zakres wymaga jawnego wyboru
dat. Nie pomijamy wierszy, nie zgadujemy waluty ani nie potwierdzamy kompletności.
Po zmianie dat PDF przygotowuje się ponownie. Zmiana pliku lub ustawień usuwa stare wyniki.
Jeśli PDF nie powstanie, raport ekranowy pozostaje dostępny i jest przycisk ponowienia.

Pamięć ustawień: lokalne JSON w LOCALAPPDATA/AutoReport/profiles, po poprawnej walidacji
całego CSV. Zapis atomowy; bez rekordów CSV i deklaracji pokrycia. Dopasowanie wymaga
identycznych nazw/kolejności kolumn, kodowania i separatora. Ten sam układ może mieć
inne znaczenie biznesowe — użytkownik widzi walutę, netto/brutto i znaczenie kwoty,
a przy zmianie eksportu musi poprawić ustawienia. Uszkodzony profil nie jest stosowany.

UNKNOWN: samodzielność początkującego użytkownika, czysty Windows, popyt i oszczędność
czasu. Launcher nie zmieniał się względem poprzedniego wydania; ograniczenia jego
testu opisuje SIMPLE_MODE_RESULTS.md.

## POTWIERDZONE
- 109 testów przeszło: build/oneclick-regression-final.log. Obejmują pamięć między
  sesjami, różne kodowania, kilka pasujących profili, uszkodzony zapis, ponawianie
  PDF po błędzie, unieważnianie starych wyników i dotychczasowe obliczenia.
- EXE i Edge: pierwszy CSV skonfigurowano raz; następnie nowa sesja przeglądarki
  odtworzyła EUR i utworzyła raport 40,00 jednym przyciskiem. Bez importowania JSON.
- Demo całego pliku: 2 250,00 / 14 pozycji. Ostatni tydzień: 1 250,00 / 7 pozycji.
- PDF-y automatycznie pobrane z EXE są zgodne z niezależnymi oczekiwaniami liczbowymi.
- Błędny kolejny CSV blokuje raport i usuwa poprzedni PDF z interfejsu.
- Formularz zwija się po imporcie; wynik jest na pierwszym planie.

Kontrola wizualna wykryła nakładające się końcowe daty na wykresie PDF dla całego
przykładu. Zmieniono rozmieszczenie etykiet według rozpiętości dat; ostatnia etykieta
zastępuje zbyt bliską poprzednią. Nie zmienia to danych ani wysokości słupków.

Artefakty: build/oneclick-qa/browser-evidence.json, pdf-evidence.json, trzy PDF-y,
zrzuty i rendery. Powtarzalna kontrola: scripts/qa_oneclick_release.py oraz
scripts/qa_oneclick_browser.cjs. Testy używają sztucznych CSV i osobnego tymczasowego
folderu ustawień, nie biblioteki użytkownika.

Paczka docelowa: release/AutoReportAnalyst-Windows-2026-09-30-oneclick.zip.
