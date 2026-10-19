# Przygotowanie publicznych wydań - 2026-10-19

Zakres: zachowanie archiwalnego MVP `v0.1.0` oraz udostępnienie obecnej
aplikacji jako `v0.2.0-beta.1` w tym samym repozytorium GitHub.
Publikację kodu i wydań zlecił właściciel projektu.

## Kontrole lokalne

- **POTWIERDZONE:** 146 testów przeszło 19.10.2026 w Pythonie 3.11.3,
  na sztucznych danych i w izolowanych katalogach. Przebieg: 21,267 s.
- **POTWIERDZONE:** wszystkie 34 pliki aplikacji wymienione w
  `LOCAL_HARDENING_EVIDENCE.json` zachowały zapisane skróty SHA-256.
  Runtime nie był ponownie kompilowany podczas publikacji.
- **POTWIERDZONE:** oba ZIP-y przeszły kontrolę CRC; paczka aplikacji ma
  zgodny skrót z protokołem 06.10.2026. EXE odpowiada `RELEASE.json`.
- **POTWIERDZONE:** osobny eksport dokładnie przygotowanej zawartości Git
  przeszedł 146 testów w 20,110 s. Wszystkie 34 pliki aplikacji i wzorcowy
  PDF zachowano bajt w bajt; atrybuty Git chronią końce linii i pliki binarne.
- **POTWIERDZONE:** EXE z ponownie rozpakowanego ZIP uruchomił i zakończył
  własny serwer w dwóch sesjach, bez Pythona w PATH i z osobnymi ustawieniami.
  Pierwsze wywołanie pliku PS1 zatrzymała systemowa polityka skryptów;
  przejrzany kod wykonano następnie jako polecenie PowerShell 5.1 bez zmiany
  tej polityki. Nie sprawdza to ręcznej obsługi launchera ani czystego Windowsa.
- **POTWIERDZONE:** 23 pliki pakietu pierwszego testu są zgodne z jego
  manifestem; osadzony ZIP aplikacji ma ten sam SHA-256.
- Przejrzano pliki do publicznego Git: kod, testy, szablony, dane
  demonstracyjne, instrukcje i dowody portfolio. Kontrola znanych formatów
  kluczy prywatnych i tokenów nie wykazała trafień; nie jest to gwarancja
  wykrycia każdego rodzaju sekretu.
- Lokalne bazy, buildy, ZIP-y, wyniki, katalog `tmp`, osobiste notatki,
  lista firm i szkice wiadomości pozostają poza historią kodu.

Szczegóły maszynowe: [GITHUB_RELEASE_2026-10-19.json](GITHUB_RELEASE_2026-10-19.json).
Logi robocze znajdują się lokalnie w `build/github-update-20261019`.

## Paczki wersji 2

| Plik | Bajty | SHA-256 |
|---|---:|---|
| `AutoReportAnalyst-Windows-2026-10-06-hardening.zip` | 97 758 024 | `d99a954fc1c3be63c452e0607a6158f99f7196df3754cfa8e2dcadcf71f6f430` |
| `AutoReport-FirstTest-Windows-2026-10-14.zip` | 97 794 784 | `1ceb1bd89f6297330c6cbb595746021648a310167cfb24cf59c5dd20806dd82c` |

Pierwsza paczka służy do uruchomienia aplikacji. Druga zawiera tę samą
aplikację oraz formularze i instrukcje pierwszego testu. Żadna nie oznacza
wykonanego pilota ani testu na czystym Windowsie.

## Granice

**HIPOTEZA:** hurtownia jako odbiorca. **UNKNOWN:** czysty Windows,
samodzielność nowej osoby, rzeczywisty eksport, popyt, oszczędność czasu
i koszt wdrożenia. Publikacja repozytorium nie zamyka tych bramek.

Wersja 1 jest archiwum historycznej implementacji z opisanymi ograniczeniami.
Instrukcja: [LEGACY_MVP.md](LEGACY_MVP.md). Do nowych kontrolowanych prób
przeznaczona jest [wersja 2](TRY_IT.md).
