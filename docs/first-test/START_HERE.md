# Pierwszy test — wersja do pracy i pilot

Stan: 2026-10-14. Przygotowanie do testu; brak uczestnika, rzeczywistego eksportu
i wykonanej próby w VM. Na prośbę właściciela przygotowano konfigurację oraz
instrukcję VM; nie instalowano hypervisora ani Windowsa.

POTWIERDZONE: istnieje sprawdzony lokalnie EXE z 2026-10-06. HIPOTEZA: hurtownia
jako odbiorca. UNKNOWN: czysty Windows, samodzielność użytkownika, korzyść,
akceptacja ceny i ekonomika wdrożenia. Przygotowany formularz nie zamyka tych bramek.

## Zacznij tutaj

1. Przygotuj VM według [CLEAN_WINDOWS.md](CLEAN_WINDOWS.md) i [vm-config.json](vm-config.json).
2. Przejdź próbę techniczną i zadania z [FIRST_USE.md](FIRST_USE.md).
3. Przeprowadź rozmowę z [DISCOVERY.md](DISCOVERY.md).
4. Dla jednego rzeczywistego procesu wypełnij [DATA_AGREEMENT.md](DATA_AGREEMENT.md).
5. Zapisz niezależne oczekiwania według [NUMBERS.md](NUMBERS.md).
6. Uzgodnij dwa cykle i koszty według [PILOT_AND_COSTS.md](PILOT_AND_COSTS.md).
7. Użyj [OPERATIONS.md](OPERATIONS.md) przy przekazaniu i ponowieniu pracy.

Właściciel zapewnia dostęp do rozmówcy i eksportu, ustala cenę oraz zatwierdza
kontakt. Użytkownik wykonuje zadania; właściciel danych potwierdza znaczenie
eksportu i wzorzec liczb. Codex może przygotować profil, sprawdzić liczby i
naprawić znalezione przeszkody po otrzymaniu tych materiałów.

## Zawartość pakietu przenośnego

- [Bieżący ZIP aplikacji](https://github.com/Vulpiss/Auto-Report/releases/download/v0.2.0-beta.1/AutoReportAnalyst-Windows-2026-10-06-hardening.zip).
- [Skrypt kontroli startu](../../scripts/Test-Workstation.ps1) dla PowerShell 5.1+.
- Sztuczne CSV i oczekiwania w podfolderze `fixtures`; bez danych klienta.
- Formularze i konfiguracja VM w tym folderze.
- `MANIFEST.json` w korzeniu paczki identyfikuje pliki i ich SHA-256.

Pakiet nie wymaga Pythona do uruchomienia aplikacji i kontroli serwera.
Opcjonalny weryfikator liczb wymaga środowiska źródłowego projektu; nie jest
wymaganiem użytkownika EXE. Nie znajduje się w przenośnej paczce Windows.

## Stan realizacji

[ROADMAP.md](ROADMAP.md) zawiera zależności, testy i warunki ukończenia.
[TEST_RESULTS.md](TEST_RESULTS.md) opisuje faktycznie wykonane kontrole.
Wcześniejsze dowody aplikacji: [protokół odporności](../LOCAL_HARDENING_RESULTS.md).

GO do przygotowanej próby. STOP dla konkretnego importu przy niewyjaśnionej
różnicy liczb lub definicji. PIVOT, jeżeli rozmowy pokażą inne potrzebne zadanie.
Popyt i gotowość sprzedażowa wymagają dowodów z pilota.
