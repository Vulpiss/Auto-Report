# Lokalne zwiększenie odporności — 2026-10-06

Zakres: skrajne PDF, duże CSV, przerwanie pracy, błędy zapisu oraz przygotowanie
nowego wydania. GO do dalszej lokalnej demonstracji. Nie jest to walidacja klienta.

| Krok | Stan | Kryterium zakończenia |
|---|---|---|
| Skrajne PDF | POTWIERDZONE | Niezależne liczby i kontrola wszystkich sześciu stron |
| Duże i trudne CSV | POTWIERDZONE | Dwa importy w EXE, poprawne PDF i odrzucenie przekroczonych limitów w kodzie |
| Awarie i ponowienie | POTWIERDZONE | Zachowane źródło i poprzedni PDF, poprawny ponowny eksport |
| Jedno polecenie wydania | POTWIERDZONE | Lock, 138 regresji, build, ZIP i kontrola rozpakowanego EXE |
| Czysty Windows w VM | UNKNOWN | Brak przygotowanej maszyny; wykonano tylko odczytowy preflight |

## PDF — POTWIERDZONE

Szablon 4 dobiera precyzję osi do skali kwot, usuwa prezentacyjne ujemne zero
po zaokrągleniu, dostosowuje długie tytuły i pozwala treści przepływać między
stronami. Nagłówek kategorii ma zarezerwowane miejsce z etykietami kolumn i
pierwszym wierszem; reszta tabeli może się dzielić. Pojedyncze słowa nie są
przenoszone jako osobny koniec akapitu. Dane źródłowe i sposób liczenia nie zmieniają się.

| Sztuczny przypadek | Niezależny wzorzec | Wynik |
|---|---|---|
| Grosze i zwroty | 7 pozycji, 0,04 PLN, średnia 0,01; poprzednio 0,07 | PASS, 2 strony |
| 36 długich kategorii | 666,00 PLN, średnia 18,50; pozostałe 26 kategorii 351,00 | PASS, 2 strony |
| Dokumenty i rentowność | 600,00 PLN, 6 pozycji, 3 dokumenty, koszt 360, zysk 240, marża 40% | PASS, 2 strony |

Wszystkie sześć stron wyrenderowano Popplerem w 120 dpi i obejrzano. Czytelne
polskie znaki i osie; bez ucięć, nakładania tekstu, samotnego nagłówka tabeli
ani osobnej strony ze słowem/stopką źródła. Nie jest to gwarancja idealnego
układu dla każdego dowolnego eksportu. Przykłady: `output/pdf/local-hardening-2026-10-06`.

## Duże CSV

POTWIERDZONE w kodzie z przypiętych zależności: 100 000 rekordów / 500 kategorii
i 1 000 000 rekordów / 2 000 kategorii / pięć lat. Kwota każdej pozycji 1,01 PLN.
Oczekiwane sumy odpowiednio 101 000,00 i 1 010 000,00 PLN; suma struktury
dashboardu również się zgadza. Duży plik ma 84 000 020 bajtów.

| Kod, osobny proces na przypadek | Analiza | Model i strona tabeli | Szczyt pamięci roboczej | Szczyt prywatnego przydziału |
|---|---:|---:|---:|---:|
| 100 000 rekordów | 4,521 s | 0,035 s | 152,09 MiB | 492,80 MiB |
| 1 000 000 rekordów | 46,669 s | 0,593 s | 1 110,38 MiB | 1 453,64 MiB |

Jeden przebieg dla każdego przypadku. Pomiar kodu nie obejmuje przeglądarki
ani ręcznej pracy. Starszy test 512 MiB dotyczył innego wydania i nie dowodzi
obsługi miliona rekordów w bieżącym dashboardzie przy takim limicie.
POTWIERDZONE: 1 000 001 rekordów oraz plik 100 MiB + 1 bajt zostały odrzucone.
Pierwszy limit wymagał odczytu miliona rekordów; limit bajtów został sprawdzony
przed parsowaniem. To oddzielne procesy na syntetycznych plikach.

Nowy EXE, rozpakowany z ZIP, przeszedł oba importy i pobranie PDF:

| EXE w Edge | Import, analiza i automatyczny PDF wraz z pobraniem |
|---|---:|
| 100 000 rekordów | 6,078 s |
| 1 000 000 rekordów / pięć lat | 55,407 s |

Oba PDF mają po dwie strony. Sumy, średnie, liczby pozycji i szablon 4
sprawdzono w pobranych plikach; wszystkie cztery strony wyrenderowano i
obejrzano. Maksimum dla procesu EXE podczas obu prób: 1 496,30 MiB pamięci
roboczej i 1 860,05 MiB prywatnego przydziału. Pomiar nie obejmuje pamięci
przeglądarki ani Windowsa i nie jest wymaganiem minimalnym dla dowolnego pliku.

## Awaria i ponowienie — POTWIERDZONE

Przerwano wyłącznie własne procesy testowe po 10 000 rekordów importu oraz
po rozpoczęciu zapisu wykresu w katalogu `.pending-*`. Źródło i wcześniejszy
PDF zachowały identyczne bajty. Nie opublikowano częściowego raportu. Ponowny
eksport dał niezależnie oczekiwane 12,34 PLN. Katalog nieudanego eksportu
pozostaje oddzielony od ukończonych raportów.

Regresje sprawdzają odmowę publikacji do katalogu, błąd zapisu podsumowania,
zapełniony dysk przy zapisie diagnostyki, ścieżkę wyjściową będącą plikiem oraz
nieudany zapis profilu. Awarie dysku/uprawnień są wstrzykiwane w izolowanym
teście; nie zapełniano dysku i nie zmieniano ACL. Naprawiono maskowanie
pierwotnego błędu eksportu przez drugi błąd zapisu diagnostyki.

## Powtarzalne wydanie

`requirements-release-lock.txt` przypina zależności bezpośrednie i pośrednie.
Nie obiecuje identycznych bajtów EXE przy każdej kompilacji. Skrypt
`scripts/release_local.py` sprawdza zgodność środowiska z lockiem, uruchamia
regresję i przerwanie pracy, kompiluje EXE, rozpakowuje osobny ZIP i kontroluje
aplikację w Edge. Dopiero po przejściu kontroli tworzy finalny ZIP z metadanymi.
Każdy tag ma osobny katalog; wcześniejsze wydania są zachowywane.

```powershell
python scripts/release_local.py --release-tag moje-wydanie --date RRRR-MM-DD
```

Domyślnie powstaje osobne środowisko Pythona. Wymagane Python 3.11, Node,
Playwright/Edge i dostęp do pakietów. Narzędzia kontroli nie są zależnościami
użytkownika gotowego EXE. `--python` przyjmuje istniejące izolowane środowisko
wyłącznie wtedy, gdy dokładnie zgadza się z lockiem.

POTWIERDZONE: `AutoReportAnalyst-Windows-2026-10-06-hardening.zip` z nowego
builda przeszło pełny proces. 138 testów OK, zgodny lock, przerwanie pracy,
kontrola rozpakowanego EXE w Edge, poprawa CSV i pobranie PDF. CRC oraz SHA-256
EXE są zgodne. Logi i końcowy skrót ZIP: `build/local-releases/2026-10-06-hardening`.
Po zakończeniu kontroli odświeżono wyłącznie dokumenty i dowody w ZIP;
runtime pozostał taki sam. Starsze wydania zachowano.

Dowody przenośne: [LOCAL_HARDENING_EVIDENCE.json](LOCAL_HARDENING_EVIDENCE.json).
Artefakty wykonawcze: `scripts/qa_pdf_hardening.py`, `scripts/benchmark_local.py`,
`scripts/qa_interrupt_recovery.py`, `scripts/release_local.py`. Ich zależności,
kontrole i kryteria zakończenia opisują sekcje powyżej; zmiana kodu wymaga
nowego tagu i ponownej kontroli. Główne ryzyko pomiarów: sztuczne dane i jeden host.

## Czysty Windows

POTWIERDZONE: i5-10400F, ok. 47,9 GiB RAM, wirtualizacja w firmware i SLAT
dostępne. HypervisorPresent=False; nie znaleziono poleceń Get-VM, VBoxManage,
vmrun ani ich typowych instalacji. Nie uruchomiono nowej maszyny wirtualnej.

UNKNOWN: czysty Windows, ręczna obsługa okna launchera i samodzielność nowej
osoby. Najmniejszy kolejny test bez osób trzecich: przygotować czysty lokalny
Windows w VM, skopiować tylko ZIP, uruchomić EXE, utworzyć dwa raporty,
pobrać PDF i zakończyć program przyciskiem. Taki test zgodności nadal nie
potwierdzi samodzielności innego użytkownika.

## Ryzyka i granice

1. Import zajmuje pamięć zależną od liczby oraz szerokości rekordów.
2. Skrajny układ spoza sprawdzonych przykładów może wymagać dodatkowego renderu.
3. System plików może blokować eksport; ponowienie wymaga usunięcia przyczyny.
4. Środowisko innego Windowsa nie zostało jeszcze sprawdzone.
5. Poprawność techniczna nie potwierdza potrzeby klienta ani kompletności jego eksportu.

HIPOTEZA: odbiorca hurtowniany. UNKNOWN: popyt, oszczędność czasu, przydatność
raportu w rzeczywistym procesie i opłacalność usługi. Jeden uzgodniony kontrakt
i raport pozostają zakresem MVP.
