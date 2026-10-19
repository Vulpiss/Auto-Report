# Auto-Report Analityk — pierwsze uruchomienie
Aktualizacja: 2026-10-06. Bieżąca paczka: `AutoReportAnalyst-Windows-2026-10-06-hardening.zip`.

## Start
1. Rozpakuj cały ZIP do wybranego folderu. Zachowaj folder `_internal` obok `AutoReportAnalyst.exe`.
2. Uruchom `AutoReportAnalyst.exe`. Przeglądarka otworzy się automatycznie. Małe okno pozwala otworzyć ją ponownie lub zakończyć program. Port jest wybierany automatycznie.
3. W prostym trybie zaznacz „Chcę najpierw wypróbować program na przykładzie” i kliknij „Utwórz raport”.
4. Domyślnie cały przykład daje 2 250,00 PLN i 14 pozycji. Po wybraniu ostatnich 7 dni: 1 250,00 PLN i 7 pozycji.
5. Przełącz trzy dashboardy: „Wynik i trend”, „Kategorie i źródła zmiany”, „Jakość i pokrycie danych”.
6. PDF przygotowuje się automatycznie. Kliknij „Pobierz gotowy raport PDF”, aby go zapisać. PowerPoint i dodatkowe filtry są w trybie „Zaawansowany”; po zmianie trybu wczytaj plik ponownie.
7. Zakończ aplikację przyciskiem „Zakończ program” w małym oknie. Samo zamknięcie karty przeglądarki nie zatrzymuje serwera.

Do uruchomienia paczki i generowania plików nie trzeba instalować Pythona ani PowerPointa. Do przeglądania prezentacji potrzebny jest program obsługujący PPTX.

## Własne dane
W prostym trybie wybierz CSV. Przy znanym układzie kolumn kliknij „Utwórz raport”; cały plik zostanie sprawdzony, a raport ekranowy i PDF powstaną razem. Przy pierwszym pliku sprawdź podgląd pięciu wierszy, kolumny, znaczenie kwoty, walutę i ewentualną niejednoznaczną datę. Podgląd nie zastępuje walidacji całego pliku.

Po poprawnym imporcie program automatycznie zapamiętuje ustawienia w lokalnym folderze `%LOCALAPPDATA%/AutoReport/profiles`. Można odznaczyć zapamiętywanie w ustawieniach przed importem; nie usuwa to wcześniej zapamiętanej konfiguracji. Nie zapisujemy tam wierszy CSV ani deklaracji kompletności. Na innym komputerze można użyć pliku JSON z sekcji „Zapamiętane ustawienia” w panelu bocznym.

Rozpoznanie dotyczy dokładnych nazw i kolejności kolumn, sposobu odczytu liter oraz separatora. Nie dowodzi, że waluta lub znaczenie kwot pozostały takie same. Przy zmianie eksportu sprawdź podsumowanie konfiguracji i popraw ustawienia; udany import zapisze nową konfigurację tego układu. Uszkodzony zapis nie jest stosowany. Niepoprawny CSV nie aktualizuje pamięci ustawień.

Domyślnie raport obejmuje cały plik. W „Zmień okres raportu” można wybrać ostatnie 7/30 dni, ostatnie pięć lat w pliku lub kalendarz; PDF aktualizuje się automatycznie. Jeden raport obejmuje najwyżej pięć lat kalendarzowych, np. 02.10.2021–01.10.2026. Dłuższy zakres wymaga jawnego wyboru okresu; program nie obcina danych samodzielnie. Prosty tryb nie deklaruje kompletności i nie oblicza porównania na podstawie samej obecności wierszy.

Wybierz CSV i przypisz kolumny daty, wartości oraz kategorii. Sprawdź separator, kodowanie, format dat i liczb, walutę oraz znaczenie wartości. Tryb cena × ilość wymaga odpowiednich kolumn i określenia jednostki ilości. Nie ignoruj błędów walidacji.

Dołączony przykład `wholesale_business.csv` ma profil `wholesale_business.profile.json`. Przywróć profil, wczytaj CSV i ustaw okres 01–03.09.2026: oczekiwana suma wynosi 600,00 PLN.

Profil przechowuje konfigurację. Zapis sesji jest powiązany z konkretnym plikiem CSV; kontrola skrótu chroni przed odtworzeniem sesji na innych danych.

## Filtry i porównania
Filtry okresu i kategorii obowiązują dashboardy oraz eksport. Dostępne jest grupowanie dzienne, tygodniowe i miesięczne. Przed porównaniem potwierdź kompletność eksportu obejmującego oba okresy. Brak wierszy nie dowodzi zerowej sprzedaży.
Dla demo można zadeklarować pokrycie 31.08–13.09.2026: tydzień 07–13.09 ma wzrost 25% względem poprzedniego.

## Miejsca do poprawy

Po błędnym imporcie program wskazuje linię CSV, kolumnę, wartość, przyczynę i wskazówkę. Kliknij wiersz tabeli, aby przeczytać pełny opis. Możesz pobrać wszystkie wykryte problemy do CSV; lista ekranowa ma strony po 100 problemów. Popraw dane u źródła albo w kopii pliku, wybierz poprawiony CSV i ponów import.

Linia oznacza fizyczną linię pliku, z nagłówkiem jako linią 1. Pole wieloliniowe może mieć zakres linii. Przerwana kontrola jest oznaczana i nie dowodzi sprawdzenia całego pliku. Braki w dodatkowych kolumnach mają ostrzeżenia i ograniczają zależne wskaźniki. Szczegóły: [DATA_DIAGNOSTICS.md](DATA_DIAGNOSTICS.md).

## Eksport
PowerPoint oferuje wariant z wyglądem dashboardu oraz wariant „Edytowalne wykresy”. Pierwszy zachowuje wykresy jako obrazy, drugi zawiera natywne wykresy PowerPoint. Można eksportować bieżący dashboard lub wszystkie trzy. Pełny zakres danych i filtry są opisane w eksporcie; sprawdź również notatki slajdów.
Po zmianie danych lub filtrów przygotuj eksport ponownie. Pobrane pliki trafiają do miejsca wybranego przez przeglądarkę.

## Limity i rozwiązywanie problemów
- Import: do 100 MiB i 1 000 000 wierszy; okres raportu do pięciu lat kalendarzowych. Reguły: [DATA_CONTRACT.md](DATA_CONTRACT.md).
- Waluta opisuje dane — aplikacja nie przelicza kursów. Nie sumuj różnych walut jako jednej.
- Znaczniki czasu są interpretowane jako lokalne daty, bez konwersji stref czasowych.
- Duży plik wymaga czasu i pamięci; obserwuj postęp importu.
- Brak `_internal`: ponownie rozpakuj całą paczkę.
- Nowa paczka wybiera wolny port. Przy problemie z uruchamianiem małe okno wskazuje plik diagnostyczny.
- Pusty wykres: sprawdź okres i filtry.
- Niedostępne porównanie: sprawdź deklarację pokrycia i obecność odpowiednich danych.
- Jeśli Windows blokuje plik, zanotuj dokładny komunikat; nie wyłączaj zabezpieczeń.

Przy zgłaszaniu błędu podaj nazwę ZIP, etap i komunikat. Użyj danych demonstracyjnych lub zanonimizowanej próbki.

Test na tym samym komputerze z odizolowanymi ustawieniami i ograniczonym PATH nie zastępuje testu na czystym Windowsie.
