# Weryfikacja po przeniesieniu — 2026-09-24

Lokalizacja: D:\python kurs\Auto-Report-v2.

Naprawione:
- Odtworzono 24 launchery pakietów w venv/Scripts na podstawie metadanych już zainstalowanych pakietów; bez pobierania i zmiany ich wersji.
- Naprawiono stare ścieżki w skryptach aktywacji środowiska.
- Zaktualizowano zapamiętaną lokalizację w .idea/workspace.xml.
- Kopie plików sprzed naprawy: build/venv-relocation-backup-20260924-173335.
- Skrypt naprawy: scripts/repair_moved_venv.py.

Potwierdzone:
- Python wskazuje D:\python kurs\Auto-Report-v2\venv\Scripts\python.exe.
- pip, Streamlit i PyInstaller uruchamiają się poprawnie.
- pip check: No broken requirements found.
- Aktywacja PowerShell wskazuje środowisko z dysku D.
- 88 testów regresji OK; log: build/relocation-tests.log.
- Przeniesione EXE z release/analyst-2026-09-24-large-import uruchomiono z osobnym AUTOREPORT_HOME.
- Test przeglądarkowy (Edge headless): dane demonstracyjne, wszystkie trzy widoki, eksport i pobieranie PDF oraz PPTX.
- PDF: 2 strony, render sprawdzony wizualnie. PPTX: 3 slajdy, integralność ZIP poprawna.
- Dowody: build/relocation-qa/browser-evidence.json, report.pdf, report.pptx, dashboard.png.
- Testowa aplikacja została zamknięta po weryfikacji.

Zakres: testy aplikacji i przeniesionego środowiska na tym komputerze. Nie testowano ustawień interpretera w uruchomionym IDE ani ponownego budowania wszystkich historycznych wydań. Stare logi, raporty i generowane pliki build mogą zawierać historyczne ścieżki; nie zmieniano ich treści.
