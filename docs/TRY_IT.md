# Wypróbuj Auto-Report 2 na Windows

Status: publiczna beta `v0.2.0-beta.1`. Użyj najpierw sztucznych danych.
Paczka nie wymaga instalacji Pythona. Przetwarzanie danych odbywa się lokalnie.

## Pobierz

1. Pobierz [Windows ZIP](https://github.com/Vulpiss/Auto-Report/releases/download/v0.2.0-beta.1/AutoReportAnalyst-Windows-2026-10-06-hardening.zip).
2. Sumę pliku możesz porównać z [SHA256SUMS.txt](https://github.com/Vulpiss/Auto-Report/releases/download/v0.2.0-beta.1/SHA256SUMS.txt).
   W PowerShell: `Get-FileHash -Algorithm SHA256 -LiteralPath '.\AutoReportAnalyst-Windows-2026-10-06-hardening.zip'`.
3. Rozpakuj cały ZIP do osobnego folderu. Zachowaj `_internal` obok `AutoReportAnalyst.exe`.
4. Uruchom `AutoReportAnalyst.exe`. Małe okno launchera otworzy lokalny interfejs w przeglądarce.

## Pierwszy raport

1. Zaznacz „Chcę najpierw wypróbować program na przykładzie”.
2. Kliknij „Utwórz raport”.
3. Sprawdź: **2 250,00 PLN**, **14 pozycji**, średnia **160,71 PLN**.
4. Obejrzyj trzy widoki i pobierz gotowy PDF. Dane są sztuczne; wartości nie opisują firmy.
5. W „Zmień okres raportu” wybierz ostatnie 7 dni. Oczekiwanie: **1 250,00 PLN**,
   **7 pozycji**, średnia **178,57 PLN**.
6. Zakończ program przyciskiem „Zakończ program” w małym oknie. Ponownie go uruchom.

## Błąd i ponowienie

Wybierz [bad-example.csv](portfolio/bad-example.csv), odznaczając przykład
wbudowany. Program powinien wskazać błędy w linii **10** (`value`) i **14**
(`category`) oraz zablokować PDF. Następnie wczytaj
[corrected-example.csv](portfolio/corrected-example.csv): suma powinna
wrócić do **2 250,00 PLN**, a komunikaty o błędach zniknąć.
Oba pliki są także w folderze `portfolio` paczki Windows.

Poprawna suma nie potwierdza kompletności eksportu. W prostym trybie
porównanie pozostaje niedostępne bez potwierdzenia pełnych okresów.

## Własny eksport i zgłoszenie wyniku

Przy pierwszym własnym pliku sprawdź znaczenie wiersza, daty i kwoty, walutę,
netto/brutto oraz kompletność. Reguły: [kontrakt danych](DATA_CONTRACT.md).
Instrukcja: [ANALYST_QUICKSTART.md](ANALYST_QUICKSTART.md).

Zapisz wersję Windows, nazwę ZIP, krok próby, oczekiwany i rzeczywisty wynik,
komunikat błędu oraz potrzebną pomoc. Do zgłoszenia użyj sztucznego przykładu
lub zanonimizowanej próbki. Pomiar czasu obejmuje eksport, kontrolę i zapis
raportu, a nie samo kliknięcie przycisku.

POTWIERDZONE: opisane lokalne kontrole programu. UNKNOWN: działanie na czystym
Windowsie, obsługa przez nowego użytkownika i korzyść w rzeczywistym procesie.
[Pełny pakiet pierwszej próby](first-test/START_HERE.md).

Archiwalna wersja 1 ma [osobną instrukcję](LEGACY_MVP.md).
