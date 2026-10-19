# Test ograniczonych zasobów — Auto-Report 0.2.0
Data: 2026-09-14. Werdykt: **GO dla dalszych prób na słabych komputerach; brak dowodu zgodności z dowolnym starym PC.**

## Metoda
Testowano EXE z osobno wypakowanej kopii dostarczanego ZIP, z odizolowanego katalogu roboczego. Zmieniano wyłącznie fikcyjny CSV wewnątrz kopii testowej.
Uruchamianie procesu w stanie wstrzymanym, przypisanie do Windows Job Object i dopiero wznowienie: ograniczenie do 1 procesora logicznego oraz 512 albo 256 MiB pamięci prywatnej procesu. Limity odczytano ponownie z systemu przed uruchomieniem.
Usunięto zmienne środowisk Pythona/venv i pozostawiono tylko System32 w PATH dziecka. To potwierdza niezależność paczki od Pythona w PATH, nie czystość systemu.
Każdy przypadek wykonano 3 razy. Kryteria przed testem: kod 0, zgodna liczba wierszy i suma w groszach, plik PDF oraz czas nieprzekraczający 30 s. Podstawowy limit: 512 MiB; 256 MiB to dodatkowa próba.
Czas obejmuje start EXE i generację PDF, nie ręczny eksport, wybór profilu ani kontrolę użytkownika.
Wszystkie 15 prób przeszło. Nie zmieniono programu ani oryginalnej dystrybucji.

## Wyniki
| Dane | Limit procesu | Czas min–max | Szczyt pamięci roboczej | Szczyt prywatnej pamięci zadeklarowanej |
|---|---:|---:|---:|---:|
| 1 000 prostych wierszy | 512 MiB | 1,54–3,22 s | 94,70 MiB | 108,48 MiB |
| 10 000 prostych wierszy | 512 MiB | 1,69–1,79 s | 94,53 MiB | 107,62 MiB |
| 100 000 prostych wierszy | 512 MiB | 3,90–4,50 s | 126,05 MiB | 139,59 MiB |
| 100 000 prostych wierszy | 256 MiB | 3,78–4,64 s | 125,99 MiB | 139,57 MiB |
| 100 000 różnych długich kategorii, CSV 18 500 021 bajtów | 512 MiB | 5,17–7,19 s | 234,71 MiB | 250,21 MiB |

MiB = 1 048 576 bajtów. Limit prywatnej pamięci procesu nie oznacza komputera z tak małą ilością RAM: Windows i pozostałe aplikacje potrzebują własnej pamięci.
Prosty plik miał jedną datę i kategorię, a trudny 100 000 różnych kategorii o długich nazwach. Nie wyczerpuje to wszystkich możliwych danych.

## Sprzęt i granice wniosku
Host: Intel Core i5-10400F, 6 rdzeni / 12 procesorów logicznych, 51 402 534 912 bajtów RAM (około 47,9 GiB).
Przydział jednego procesora logicznego nie emuluje starszej mikroarchitektury, wolnego dysku, małej pamięci całego systemu ani konfliktów o zasoby.
Windows Sandbox nie jest dostępny. Nie wykonano próby na czystej maszynie wirtualnej ani na fizycznym starym komputerze.
Tryb smoke uruchamia pełną generację raportu, ale nie sprawdza ręcznej obsługi okna w ograniczonym środowisku. Interfejs wcześniej przeszedł osobną próbę automatyczną na hoście.

## GPU i zgodność CPU
POTWIERDZONE w kodzie: wykresy używają programowego renderera Matplotlib Agg. Obliczenia są lokalne, SQLite i CPU; nie wymagają RTX/CUDA.
W paczce nie znaleziono plików o nazwach wskazujących CUDA, cuDNN, PyTorch lub TensorFlow. GPU hosta nie było fizycznie usunięte ani systemowo wyłączone.
POTWIERDZONE w środowisku budowania: NumPy 2.4.4, bazowy zestaw instrukcji X86_V2; opcjonalny X86_V3.
[Oficjalna dokumentacja NumPy](https://numpy.org/doc/2.4/reference/simd/build-options.html) wyjaśnia minimalne instrukcje CPU. Wersja 2.4 podniosła bazowy próg x86 do x86-64-v2.
Nie deklarujemy obsługi procesorów niespełniających tego progu ani Windows 32-bit. Przed obietnicą dla konkretnego starego komputera potrzebny jest jego model CPU i faktyczny test.
Mniejsze zużycie RAM nie usuwa wymagania instrukcji procesora. Jeśli odbiorca ma niezgodny CPU, potrzebna będzie osobna dystrybucja z niższym progiem bibliotek lub zastąpienie warstwy wykresów.

## Powtórzenie
- python scripts/benchmark_low_spec.py — 12 prób; wymaga Pythona tylko do pomiarów na stanowisku testowym.
- python scripts/benchmark_low_spec_stress.py — 3 próby trudnego pliku.
- scripts/Test-CleanWindows.ps1 -Archive ŚCIEŻKA_DO_ZIP — test paczki na innym Windows; nie wymaga zainstalowanego Pythona.
- Po teście na drugim komputerze uruchomić aplikację normalnie i przygotować drugi raport bez pomocy autora.

Pełne wyniki: docs/LOW_SPEC_RESULTS.json.
Nie oznaczamy kroku 8 jako całkowicie zakończonego, dopóki nie przejdzie test na innym komputerze i samodzielne użycie przez nową osobę.
