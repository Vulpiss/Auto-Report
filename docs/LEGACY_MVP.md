# Auto-Report 1 - archiwalne MVP

Tag: `v0.1.0`. Stan: commit `20f3146` z 21.06.2026. Kod aplikacji pochodzi
z początkowego commita `c62501f`; drugi commit zmieniał tylko dokument postępu.
Oznaczenie wersji nadano podczas porządkowania wydań 19.10.2026.

## Pobranie i uruchomienie

1. Otwórz [wydanie v0.1.0](https://github.com/Vulpiss/Auto-Report/releases/tag/v0.1.0)
   i pobierz **Source code (zip)**.
2. Rozpakuj je do osobnego folderu, poza folderem wersji 2.
3. Utwórz oddzielne środowisko Python 3.11 i zainstaluj historyczne zależności:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Wynik wcześniejszego pipeline trafia do `outputs/report.pdf`. Użyj
dołączonego sztucznego `sample_data/input_with_baseline.csv`.
Ten tag nie zawiera gotowej paczki EXE ani obecnego zestawu testów.
Instalacja historycznych, nieprzypiętych zależności na nowym środowisku
pozostaje UNKNOWN; nie jest częścią kontroli obecnej bety.

## Cel archiwum

To materiał do porównania architektury i rozwoju projektu. Historyczne
problemy liczb, mianowników, kompletności i instrukcji opisuje
[audyt punktu startowego](BASELINE_AUDIT.md). Pracuj wyłącznie na danych
sztucznych i nie traktuj wyników tej wersji jako podstawy decyzji biznesowych.

Do nowych prób wybierz [wersję 2](TRY_IT.md). Pliki i wyniki obu wersji
przechowuj w osobnych folderach.
