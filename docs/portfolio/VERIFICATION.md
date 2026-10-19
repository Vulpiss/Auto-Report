# Weryfikacja portfolio — 2026-10-04

Zakres: lokalne portfolio techniczne Auto-Report 0.2.0 na Windows.
GO do demonstracji projektu. Ocena nie dotyczy gotowości sprzedażowej.

## Kryteria zamknięcia

| Element | Wynik | Dowód |
|---|---|---|
| Aktualne wejście i instrukcja | Gotowe | README, START_HERE, ANALYST_QUICKSTART, kontrakt danych |
| Opis problemu i decyzji | Gotowe | [CASE_STUDY.md](CASE_STUDY.md) |
| Rzeczywista demonstracja | PASS | [MP4](media/demo.mp4), 41,76 s, 1440 × 1050, bez dźwięku |
| Sumy, średnie i kategorie | PASS | [expected.json](expected.json), niezależny csv/Decimal |
| Błędny import i poprawa | PASS | Linie 10 i 14 w pobranym CSV; brak PDF przy błędzie; poprawiony import 2 250,00 |
| Przykładowy PDF | PASS | [demo-report.pdf](demo-report.pdf), 2 strony: treść, render i kontrola wizualna |
| Instalacja z kodu i regresja | PASS | Nowe środowisko Python 3.11, requirements-qa, 129 testów, 20,484 s |
| Paczka Windows z materiałami | PASS | Nowy ZIP; CRC i skróty zgodne, EXE rozpakowany z ZIP przeszedł scenariusz |

## Potwierdzone wyniki

POTWIERDZONE: cały sztuczny przykład ma 14 pozycji, sumę 2 250,00 PLN
i średnią 160,71 PLN. Zakres 07–13.09.2026 ma 7 pozycji, sumę 1 250,00 PLN
i średnią 178,57 PLN. Kategorie w tym tygodniu: Papier 550,00,
Teczki i segregatory 450,00, Środki czystości 250,00 PLN.

Scenariusz przeglądarkowy potwierdził trzy widoki, pobranie PDF, jawną
informację o niepotwierdzonej kompletności, dwa wskazane błędy, pobranie
listy CSV, wybór pełnej wskazówki i usunięcie listy po poprawnym imporcie.
Źródłowy przykład zachował ten sam SHA-256. Profile demonstracji są osobne
i nie zastępują ustawień użytkownika.

PDF pobrano z rzeczywistego EXE. Kontrola treści obejmuje daty, walutę,
sumę, średnią, liczbę pozycji i kategorie. Porównanie jest niedostępne:
nie potwierdzono kompletności obu okresów. Obie strony wyrenderowano
Popplerem w 120 dpi i obejrzano. Polskie znaki, tabela, wykres i stopki są
czytelne; nie stwierdzono uciętego tekstu ani nakładania elementów.

MP4 pochodzi z nagrania interfejsu Edge, bez podmieniania jego treści.
Cały plik został zdekodowany bez błędu; obejrzano reprezentatywne kadry
i zrzuty ekranów. Pauzy służą pokazaniu ekranów, nie pomiarowi wydajności.

129 testów przeszło po nowej instalacji `requirements-qa.txt` w oddzielnym
środowisku. Dokładne wersje: [verified-environment.txt](verified-environment.txt).
Wynik nie zależy od zainstalowanych wcześniej pakietów projektowego venv.

Maszynowe dowody demonstracji: [VERIFICATION.json](VERIFICATION.json).
Ten sam scenariusz przeszła aplikacja uruchomiona z kodu w świeżym środowisku:
[SOURCE_VERIFICATION.json](SOURCE_VERIFICATION.json). Program rozpakowany
z nowego ZIP także przeszedł kontrolę:
[PACKAGE_VERIFICATION.json](PACKAGE_VERIFICATION.json).
Scenariusz i odtworzenie: [DEMO.md](DEMO.md). Skrypty w repozytorium:
`scripts/prepare_portfolio.py`, `scripts/qa_portfolio_browser.cjs`,
`scripts/package_portfolio.py`, `scripts/verify_portfolio_package.py`
i `scripts/verify_portfolio_links.py`.

## Wydanie

Jedno bieżące wydanie: `AutoReportAnalyst-Windows-2026-10-04-portfolio.zip`.
Zawiera niezmieniony runtime z wydania diagnostyki 2026-10-03 oraz nowe
materiały portfolio. Ta aktualizacja nie kompiluje ponownie kodu aplikacji.

SHA-256 EXE:
`84ad29d5c14d6bc39cef05f36329cf201d7f94e57b347caf0a38df9d24255cd4`.
`RELEASE.json` w paczce identyfikuje wydanie, runtime i skróty materiałów.
CRC i zgodność spakowanych plików kontroluje skrypt pakowania.
Po sprawdzeniu EXE z ZIP odświeżono wyłącznie dokumenty i dowody, ponownie
kontrolując CRC i skróty materiałów. Runtime i SHA-256 EXE pozostały identyczne.
Końcowy skrót ZIP jest zapisany lokalnie w `build/portfolio/package-evidence.json`;
nie jest umieszczany wewnątrz samego archiwum.

Dowody robocze: `build/portfolio/regression.log`, izolowane `session-*`,
`build/portfolio/pdf-render`, `build/portfolio/package-evidence.json`.
Pliki robocze i ZIP są lokalnymi artefaktami, poza Git. Materiały portfolio
w `docs/portfolio` są przygotowane do przechowywania razem z kodem.

## Granice

HIPOTEZA: zastosowanie do raportowania w małej hurtowni.

UNKNOWN: samodzielność nowego użytkownika, uruchomienie na czystym Windowsie,
rzeczywista obsługa okna launchera przez odbiorcę, popyt, kompletność eksportu
klienta, oszczędność czasu i opłacalność wdrożenia. Automatyczna sesja używa
EXE jako lokalnego serwera i przygotowanego profilu sztucznego formatu.

Znane granice: import zależy od dostępnej pamięci; brak przeliczania walut;
nie każdy skrajny PDF ma optymalną gęstość układu lub oś wykresu. Ten
dwustronicowy przykład został sprawdzony oddzielnie. Nie utworzono publicznego
GitHub Release ani nie opublikowano lub wysłano oferty.

Najmniejszy kolejny test produktu: inna osoba na innym Windowsie przygotowuje
drugi raport bez pomocy autora, a wynik porównuje z uzgodnionym wzorcem.
