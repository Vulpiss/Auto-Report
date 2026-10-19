# Dashboard Auto-Report — uruchomienie
Data: 2026-09-18. Dashboard lokalny, trzy widoki, wspólny wynik analizy z PDF.

## Gotowa paczka Windows
1. Rozpakuj cały ZIP AutoReportDashboard-Windows.zip. Zachowaj katalog _internal.
2. Uruchom AutoReportDashboard.exe. Pozostaw jego konsolę otwartą.
3. Otwórz http://127.0.0.1:8501 w przeglądarce na tym samym komputerze.
4. W panelu źródła wybierz „Użyj danych demonstracyjnych”, następnie „Wczytaj dane”.
5. W demonstracji domyślny okres to 07–13.09.2026. Suma 1250,00 PLN, liczba 7, średnia 178,57 PLN.
6. Dla porównania zadeklaruj pełny eksport 31.08–13.09.2026: zmiana sumy +25,0%.
7. „Przygotuj PDF z aktualnych filtrów” tworzy dokument. „Pobierz PDF” zapisuje go przez przeglądarkę.
8. Aby zakończyć pracę serwera, użyj Ctrl+C w jego konsoli. Zamknięcie samej karty nie zatrzymuje serwera.

Program nasłuchuje wyłącznie na 127.0.0.1. Nie jest publikowany w sieci.
Jeśli port 8501 jest zajęty, zamknij wcześniejsze uruchomienie dashboardu.
Katalog raportów: %LOCALAPPDATA%\\AutoReport\\reports (lub AUTOREPORT_HOME/reports).
Zmiana źródła, profilu, dat, kategorii albo kompletności usuwa przycisk pobrania starego wyniku; istniejące pliki na dysku pozostają.

## Własny CSV
Wymagane trzy kolumny date,value,category lub ich jawne mapowanie.
Limit: 20 MB, 100 000 pozycji; okres do 366 dni. Jedna waluta PLN.
Wybierz kodowanie, separator, datę, separator dziesiętny i netto/brutto w profilu.
Niepełny eksport pozwala obejrzeć dostępne wartości, ale blokuje porównanie.
Kwoty ujemne wymagają zaznaczenia odpowiedniej reguły.
Błędny rekord blokuje całość. Identyczne pozycje nie są usuwane.

## Widoki
- Przegląd: trzy KPI, trend dzień/tydzień, Top 5 i pozostałe, tabela źródłowa po 100 pozycji na stronę.
- Kategorie: różnice kwotowe, dwa okresy obok siebie, pełna tabela i przejście do kategorii przez wspólny filtr.
- Jakość danych: źródło, profil, kompletność, powtórzenia, ujemne kwoty i rozłączne liczniki odrzuceń przez filtry.
Wyszukiwanie w tabeli kategorii nie zmienia globalnych filtrów; interfejs to opisuje.
Wykresy porównań kategorii pokazują do 20 pozycji; pełne dane są w tabeli.
N/A oznacza brak podstaw do wyliczenia, nie zero. Liczba pozycji nie jest liczbą zamówień.
Grupowanie tygodniowe dotyczy wykresu; PDF prezentuje dzienny trend dla tych samych filtrów.
Kwoty wykresów mogą używać float do geometrii; etykiety, KPI i sumy mają dokładność groszy.

## Uruchomienie z kodu
Python 3.11, w katalogu repozytorium:
```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements-dashboard.txt
.\venv\Scripts\python.exe dashboard_entry.py
```

## Weryfikacja i budowanie
```powershell
.\venv\Scripts\python.exe -m pip install -r requirements-dev.txt -r requirements-qa.txt
.\venv\Scripts\python.exe -m unittest discover -s tests -v
.\venv\Scripts\python.exe scripts\qa_dashboard.py
.\venv\Scripts\python.exe scripts\build_dashboard.py
```
Render QA wymaga pdftoppm (Poppler) w PATH. Skrypt QA korzysta wyłącznie ze sztucznych danych i zapisuje wyniki w build/dashboard-qa.
Zależności dashboardu są przypięte w requirements-dashboard.txt; zależności QA w requirements-qa.txt.
PyInstaller buduje osobny katalog release/dashboard/AutoReportDashboard. Istniejące wydanie desktopowe pozostaje odrębne.
Sam sukces kompilacji nie dowodzi poprawności na innym komputerze. Użyj protokołu DASHBOARD_PILOT.md.
