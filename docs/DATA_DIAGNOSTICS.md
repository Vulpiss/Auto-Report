# Miejsca do poprawy w danych — 2026-10-03

Po nieudanym imporcie w trybie prostym albo zaawansowanym program pokazuje tabelę:
typ problemu, linia CSV, kolumna, podgląd wartości, opis i wskazówka poprawy.
Kliknięcie wiersza pokazuje pełny opis i wskazówkę pod tabelą.

1. Wybierz CSV i sprawdź ustawienia odczytu oraz przypisanie kolumn.
2. Kliknij „Utwórz raport” albo „Wczytaj dane”.
3. Przejrzyj „Miejsca do poprawy w danych”. Lista ma strony po 100 problemów.
4. Pobierz „Listę miejsc do poprawy (CSV)”, jeśli potrzebujesz przekazać wykryte miejsca osobie przygotowującej eksport. Program sam niczego nie wysyła.
5. Popraw dane u źródła lub w kopii pliku. Wybierz poprawiony CSV i ponów import.

Linia CSV oznacza fizyczną linię pliku tekstowego; nagłówek ma numer 1.
Pole z przejściem do nowej linii może zajmować kilka linii, np. 2–3.
Numer linii nie musi być numerem wiersza widocznego w Excelu dla pól wieloliniowych.

Błąd wymaganej wartości albo błędna wartość w przypisanej kolumnie dodatkowej
blokuje raport. Puste pola dodatkowe mają typ „Ostrzeżenie” i informują,
których wskaźników lub pełnych podziałów nie można wyliczyć. Ilość jest wymagana
w trybie cena × ilość. Brakujące kwoty nie są uzupełniane zerem ani estymacją.

Plik diagnostyczny zawiera wszystkie wykryte problemy, także poza bieżącą stroną,
zamiast dawnego limitu 50 błędnych rekordów. Podgląd wartości ograniczono do 200
znaków; dłuższe wartości mają oznaczenie skrócenia. CSV diagnostyczny używa UTF-8
z BOM i średnika; teksty przypominające formuły mają apostrof zabezpieczający.

Jeśli struktura CSV, kodowanie lub limit importu uniemożliwia dalszą kontrolę,
program oznacza kontrolę jako niepełną. Lista obejmuje miejsca wykryte do jej
przerwania. Wstępny podgląd może zatrzymać się na pierwszym błędzie struktury;
po jego poprawie należy ponowić import. Przy prawidłowej strukturze walidacja
obejmuje cały plik, a nie tylko pierwsze 100 pozycji podglądu.

POTWIERDZONE: 129 testów automatycznych przeszło, w tym 16 nowych testów
diagnostyki i obu interfejsów. Testowane są m.in. wszystkie błędy w jednym
rekordzie, ponad 50 błędnych rekordów, linie wieloliniowe, przerwanie kontroli,
braki kolumn dodatkowych, zachowanie listy po odświeżeniu i poprawiony import
z niezależnie oczekiwaną sumą 60,00.

POTWIERDZONE: kontrola w Edge przeszła dla wersji źródłowej oraz EXE rozpakowanego
z `release/AutoReportAnalyst-Windows-2026-10-03-diagnostics.zip`. Sztuczny CSV
z 75 błędnymi rekordami dał 150 problemów. Pobranie CSV zawierało wszystkie
150 problemów, z ostatnią lokalizacją w linii 76. Druga strona listy zachowała
diagnostykę po ponownym renderowaniu; kliknięcie wybranego wiersza pokazało
właściwą wskazówkę. Błędny import nie udostępnił PDF. Poprawiony plik dał
oczekiwaną sumę 60,00 i usunął starą listę błędów.

Dowody lokalne: `build/import-diagnostics-regression.log`,
`build/import-diagnostics-source-qa/evidence.json`,
`build/import-diagnostics-exe-qa/evidence.json` oraz zrzuty ekranów w tych
katalogach. Obejrzano ekran listy i pełnej wskazówki. Ustawienia kontroli
przeglądarkowej były oddzielone od ustawień użytkownika; źródła i wcześniejsze
raporty zachowano. Test EXE dotyczy lokalnego serwera w Edge, bez sprawdzania
okna launchera ani czystej instalacji Windows.

UNKNOWN: przydatność komunikatów w rzeczywistym procesie odbiorcy i kompletność
eksportu klienta. Poprawny format i przejście walidacji nie potwierdzają, że
eksport zawiera wszystkie transakcje. Najmniejszy test użyteczności: niezależna
osoba poprawia sztuczny plik na podstawie listy, bez pomocy autora.
