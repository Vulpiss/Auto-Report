# Przekazanie, ustawienia i ponowienie pracy

Wydanie do próby: `AutoReportAnalyst-Windows-2026-10-06-hardening.zip`.
Potwierdź nazwę i SHA-256 z manifestem pakietu. Zachowaj cały rozpakowany
katalog z `_internal`, instrukcję i oryginalny ZIP.

## Profil i źródło

Po pierwszym poprawnym imporcie ustawienia są zapamiętane lokalnie. Kopię
profilu wyeksportuj do JSON przez „Zapamiętane ustawienia” w panelu bocznym.
Zapisz przy niej wersję źródła i potwierdzone znaczenie kolumn. Profil nie
zawiera wierszy ani potwierdzenia kompletności; nie zastępuje kopii CSV.

Zachowaj oryginalny CSV jako osobny plik. Korekty wykonuj w kopii i zapisuj
ich autorów oraz powody. Raporty z kolejnych cykli trzymaj w osobnych folderach.

## Błąd i odzyskanie

1. Zapisz etap, dokładny komunikat, nazwę wydania i zakres dat.
2. Przy błędnych danych pobierz listę problemów; popraw źródło lub kopię.
3. Po błędzie zapisu sprawdź miejsce i dostęp do wybranego katalogu; wybierz
   nowy dostępny folder. Nie uznawaj katalogu `.pending-*` za gotowy raport.
4. Po usunięciu przyczyny ponów import i porównaj liczby ze wzorcem.
5. Przy utracie ustawień przywróć JSON i ponownie potwierdź walutę, znaczenie
   kwoty, daty i kompletność. Sprawdź nowy wynik przed przekazaniem.

## Zmiana wydania

Rozpakuj nową wersję do osobnego folderu. Zachowaj poprzednią wersję, źródła,
profile i raporty. Sprawdź ten sam wzorcowy CSV i drugi import przed przejściem
na nowe wydanie. Powrót do starego EXE nie cofa zmian w źródle danych.

Osoba odpowiedzialna za obsługę / kontakt / godziny dostępności / limit
wsparcia / reakcja na zmianę eksportu: ______. Te pola uzgodnij przed pilotem.
