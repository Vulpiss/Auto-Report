# Kontrole przygotowania — 2026-10-14

POTWIERDZONE: poniższe kontrole wykonano lokalnie. Dane są sztuczne;
nie wykonano VM, rozmowy ani pilota. Dowody przenośne: [EVIDENCE.json](EVIDENCE.json).

| Kontrola | Rzeczywisty wynik |
|---|---|
| Pełna regresja kodu | 146 testów OK, 26,513 s; osiem nowych testów odbioru |
| Weryfikator liczb, sztuczny CSV | PASS_NUMBERS_ONLY; 2 250,00 PLN, 14 pozycji, średnia 160,71 |
| Pusty wzorzec klienta | INCOMPLETE_OR_INVALID, kod 2; brak fałszywego zaliczenia |
| Istniejący plik wyniku | Odrzucona próba nadpisania, zawartość zachowana |
| PowerShell 5.1 uruchomiony z Pythona | Dwa starty rzeczywistego EXE, oba zdrowe i zatrzymane |
| Ustawienia i PATH serwera | Osobne katalogi; bez Pythona w PATH procesu EXE |
| Niepoprawny SHA-256 ZIP | Odrzucony przed rozpakowaniem i uruchomieniem EXE |
| ZIP z `../escape.txt` | Odrzucony przed rozpakowaniem i uruchomieniem EXE |
| Źródła aplikacji i EXE | Zgodne z zapisanym stanem 2026-10-06; bez zmian runtime |

Poprawiono zgodność PowerShell: SHA-256 liczy bezpośrednio .NET, dzięki czemu
skrypt działa także przy dziedziczonych ścieżkach modułów PowerShell 7 i 5.1.
Po poprawce powtórzono wszystkie trzy próby skryptu. Pierwsze nieudane próby
pozostają w `build/first-test/`; nie są podstawą oznaczenia PASS.

## Co te kontrole potwierdzają

Weryfikator liczb wykrywa niezgodną średnią, okres, walutę/netto-brutto,
źródło oraz podział kategorii przy zgodnej sumie ogólnej. Oczekiwania pochodzą
z oddzielnego, jawnego wzorca; weryfikator ich nie produkuje.
Nie sprawdza opcjonalnych KPI biznesowych, porównań, wyglądu PDF ani akceptacji klienta.

Skrypt Windows sprawdza serwer i ponowny start na tym hoście. Pozostawia
czysty Windows, okno launchera, odczyt profilu w UI i samodzielność człowieka
jako UNKNOWN. Automatyczne zatrzymanie własnego EXE nie zastępuje przycisku w launcherze.

## Pakiet i ograniczenia

Osobny pakiet `AutoReport-FirstTest-Windows-2026-10-14.zip` zawiera konfigurację,
formularze, sztuczne pliki i oryginalny ZIP aplikacji. Skrypt
`scripts/package_first_test.py` sprawdza CRC, skróty plików i odnośniki również
po rozpakowaniu. Końcowy SHA-256 i rezultat pakowania są zapisywane poza ZIP
w `build/first-test/package-2026-10-14/evidence.json`; wewnętrzny manifest
identyfikuje jego zawartość. Brak ponownej kompilacji i publikacji aplikacji.

UNKNOWN: czysty Windows, niezależny użytkownik, rzeczywisty eksport, popyt,
korzyść i koszt obsługi. HIPOTEZA: hurtownia jako odbiorca. Kryteria i zależności:
[ROADMAP.md](ROADMAP.md). Najmniejsza następna próba: utworzyć VM według
[CLEAN_WINDOWS.md](CLEAN_WINDOWS.md) i wykonać [FIRST_USE.md](FIRST_USE.md).
