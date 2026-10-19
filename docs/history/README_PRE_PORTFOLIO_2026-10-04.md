Aktualizacja 2026-10-01: raport obsługuje do 5 lat kalendarzowych od wybranej daty końcowej (także dane historyczne). Przykład: 02.10.2021–01.10.2026. Dla końca 29 lutego rocznicę sprzed pięciu lat przyjmujemy jako 28 lutego. Tryb prosty: „Cały plik” lub „Ostatnie 5 lat w pliku”. Dłuższy plik wymaga jawnego wyboru okresu; dane nie są obcinane automatycznie.

# Auto-Report 0.2.0
Nowe wydanie Windows z prostym trybem: `release/AutoReportAnalyst-Windows-2026-09-30-oneclick.zip`.
Rozpakuj cały ZIP i uruchom `AutoReportAnalyst.exe`. Program ma otworzyć przeglądarkę,
pokazać raport po wyborze CSV i kliknięciu „Utwórz raport” oraz automatycznie przygotować PDF.
Pierwszy format eksportu wymaga konfiguracji; ustawienia są zapamiętywane na komputerze.
Przycisk zakończenia znajduje się w osobnym oknie.
Instrukcja: [pierwsze użycie](docs/ANALYST_QUICKSTART.md).
Zakres weryfikacji i ograniczenia: [raport jednym przyciskiem](docs/ONECLICK_RESULTS.md).
Z kodu: `python dashboard_entry.py` po instalacji `requirements-dashboard.txt`.

Lokalny raport PDF z jednego profilu CSV. Kwoty liczone w groszach, błędne rekordy blokują generowanie, porównania wymagają potwierdzenia kompletności eksportu.

Status: wersja techniczna do walidacji. Popyt i oszczędność czasu u klienta nie są jeszcze potwierdzone.

## Uruchomienie z kodu
Python 3.11 na Windows:
```powershell
python -m pip install -r requirements.txt
python -m interfaces.desktop_app
```
Instrukcja i oczekiwany wynik danych syntetycznych: [QUICKSTART_PL](docs/QUICKSTART_PL.md).

Opcjonalny interfejs lokalny:
```powershell
python -m pip install -r requirements-dev.txt
python -m streamlit run interfaces/streamlit_app.py
```
Nie wdrażaj tego interfejsu jako publicznej usługi; nie ma logowania ani izolacji kont.

## Testy i build
```powershell
python -m unittest discover -s tests -v
python scripts/qa_release.py --gui
python scripts/build_windows.py
```
Nowa dystrybucja trafia do release/v0.2.0/AutoReport; wcześniejsze dist pozostaje zachowane.
Build wykonywać na Windows, w środowisku z requirements-dev.txt. Manifest użytego środowiska zapisano w docs/build_environment.txt.
Powtarzalna procedura nie oznacza bitowo identycznego EXE ani potwierdzenia na czystym komputerze.

## Kontrakt i architektura
CSV → jawny profil → wspólna walidacja → całkowite grosze w SQLite w pamięci → wskaźniki → polski PDF → atomowo publikowany katalog przebiegu.
Nie ma sieciowego LLM, retry ani surowej bazy danych klienta na dysku.
Jeden profil PLN: data, wartość pozycji, kategoria. Netto/brutto określa użytkownik. Brak podstawy jest widoczny w PDF.
Limity i zasady: [instrukcja](docs/QUICKSTART_PL.md).
Każdy raport ma osobny PDF, JSON z metrykami i skrótem źródła, oraz wykres. Ścieżka domyślna: %LOCALAPPDATA%/AutoReport/reports.
Historyczny report.db nie jest migrowany ani modyfikowany.

## Produkt i pilot
- [Strategia i hipotezy](docs/PRODUCT_STRATEGY.md)
- [Pierwotny audyt](docs/BASELINE_AUDIT.md) — obserwacje sprzed napraw
- [Plan pozyskania pierwszego klienta](docs/FIRST_CUSTOMER_PLAYBOOK.md)
- [Status 10 kroków](docs/IMPLEMENTATION_STATUS.md)

## Dashboard lokalny

Trzy widoki: Przegląd, Kategorie i Jakość danych; wspólne filtry i eksport PDF.
Uruchomienie: `python dashboard_entry.py` po instalacji `requirements-dashboard.txt`, albo osobny `release/dashboard/AutoReportDashboard/AutoReportDashboard.exe`.
[Instrukcja dashboardu](docs/DASHBOARD_QUICKSTART.md) · [Stan i dowody](docs/DASHBOARD_STATUS.md) · [Protokół próby](docs/DASHBOARD_PILOT.md).
