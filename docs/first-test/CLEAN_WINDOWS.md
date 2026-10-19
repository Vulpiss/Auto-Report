# Przygotowanie czystego Windowsa

Stan: przygotowane, niewykonane. Właściciel potwierdził 2026-10-14 brak ISO i VM.
Odczyt hosta: Windows 11 Home, i5-10400F, ok. 47,9 GiB RAM; wirtualizacja
w firmware dostępna, hypervisor nie działa, VirtualMachinePlatform oraz
HypervisorPlatform mają InstallState=2. W projekcie nie znaleziono obrazu systemu.

## Pobranie i konfiguracja

1. Pobierz instalator Windows x86_64 przez [oficjalną stronę VirtualBox](https://www.virtualbox.org/wiki/Downloads).
   Obsługę Windows 11 na x86_64 opisuje [Oracle](https://docs.oracle.com/en/virtualization/virtualbox/7.2/user/installation.html).
   Zapisz dokładną wersję instalatora. Instalację programu na hoście wykonuje
   właściciel według kreatora; ten pakiet nie zmienia sterowników ani funkcji hosta.
2. Pobierz Windows 11 **x64** z [Microsoft](https://www.microsoft.com/pl-pl/software-download/windows11).
   Użyj edycji, do której masz odpowiednie uprawnienie. Zapisz nazwę i SHA-256 ISO
   i porównaj z bieżącym skrótem publikowanym dla tego języka na stronie Microsoft.
3. W kreatorze nowej VM wybierz Windows 11 64-bit i ręczną instalację.
   Zastosuj przygotowane [vm-config.json](vm-config.json): 8 GiB RAM, 4 vCPU,
   dynamiczny dysk 80 GiB, UEFI, Secure Boot i TPM 2.0. To konfiguracja
   proponowana dla tego hosta, nie pomiar minimalnych wymagań Auto-Report.
   Wymagania systemu gościa opisuje [Microsoft Learn](https://learn.microsoft.com/en-us/windows/whats-new/windows-11-requirements).
4. Uruchom instalację z ISO **wewnątrz VM**. Zakończ konfigurację konta i aktualizacje.
   Pozostaw Edge; nie instaluj Pythona, środowiska projektu ani Office.
5. Zapisz wersję Windows, skalę ekranu, ustawienia VM i ewentualną wersję Guest
   Additions. Wyłącz gościa i utwórz migawkę `00-clean-windows-before-autoreport`.
   Mechanizm migawek opisuje [Oracle](https://docs.oracle.com/en/virtualization/virtualbox/7.2/user/Introduction.html).

## Przekazanie paczki i próba

1. Skopiuj cały pakiet pierwszego testu do lokalnego katalogu gościa, np.
   `C:\AutoReport-test`. Możesz użyć tymczasowego folderu współdzielonego
   tylko do odczytu; w VirtualBox wymaga to Guest Additions. Zapisz metodę
   transferu i odłącz udostępnienie po skopiowaniu.
2. Odłącz sieć VM. Dalsza próba korzysta z lokalnych plików i przeglądarki.
3. W PowerShell przejdź do korzenia rozpakowanego pakietu i uruchom:

   ```powershell
   powershell.exe -NoProfile -ExecutionPolicy RemoteSigned -File .\scripts\Test-Workstation.ps1 -Archive .\release\AutoReportAnalyst-Windows-2026-10-06-hardening.zip -ExpectedZipSHA256 d99a954fc1c3be63c452e0607a6158f99f7196df3754cfa8e2dcadcf71f6f430
   ```

   RemoteSigned dotyczy tylko tego procesu; polecenie nie zmienia polityki
   systemowej. Jeżeli organizacyjna polityka blokuje skrypt, zachowaj komunikat
   i wykonaj ręczną próbę. Nie obchodź polityki organizacji.
4. Skrypt sprawdza skróty ZIP/EXE, rozpakowanie do ścieżki ze spacjami i polskim
   znakiem, dwa starty serwera oraz zatrzymanie własnych procesów. Wynik
   `PASS_SERVER_RESTART` **nie potwierdza** obsługi okna launchera, PDF ani profilu.
   Skrypt celowo pozostawia te pola i czystość Windowsa jako UNKNOWN.
5. Wykonaj pełną ręczną próbę z [FIRST_USE.md](FIRST_USE.md). Odbiór VM wymaga
   protokołu z wersją gościa, migawką, wynikami zadań, PDF i zamknięciem programu.
   Obserwator potwierdza pochodzenie środowiska; sam fakt uruchomienia skryptu
   nie wystarcza do oznaczenia czystego Windowsa jako zaliczonego.

Wyniki zachowaj poza migawką przed jej przywróceniem. Test autora w VM sprawdza
zgodność środowiska. Samodzielność nowej osoby wymaga osobnej próby użytkownika.
