# Prosty tryb — 2026-09-29

Zakres: prowadzenie użytkownika od CSV do dashboardu i PDF, bez zmiany wspólnych obliczeń.

Nowe elementy: prosty ekran startowy, podgląd 5 wierszy, propozycja separatora i kodowania,
mapowanie nazw kolumn, przykłady dat zamiast kodów formatu, jawny wybór znaczenia kwoty,
kalendarz, zwijanie konfiguracji po imporcie, zapis/odczyt profilu oraz wskazówki po błędzie.
Niejednoznaczne daty wymagają wyboru. Cały CSV nadal przechodzi dotychczasową walidację.
Brak waluty nie staje się automatycznie PLN. Brak wierszy nie potwierdza kompletności.
Po zmianie pliku, ustawień lub okresu stary PDF nie jest dostępny do pobrania.

Nowy launcher: małe okno, automatyczny wybór portu, przeglądarka otwierana po gotowości
serwera, ponowne otwieranie i zakończenie własnego procesu serwera. Log lokalny w
LOCALAPPDATA/AutoReport/logs. EXE budowane bez konsoli.

UNKNOWN: samodzielność osoby nietechnicznej i czysty Windows. Nie ma dowodu, że program
obsłuży „każdy”. Pierwszy eksport nadal wymaga potwierdzenia znaczenia kolumn i kwot.
Profile są przenoszone plikiem JSON, nie zapamiętywane automatycznie między uruchomieniami.
PowerPoint i porównania pozostają w trybie zaawansowanym.

Test użytkownika: rozpakowanie → przykład → własny CSV → PDF → drugi CSV z zapisanym
profilem → zamknięcie programu. Obserwator nie podpowiada; zapisuje miejsca zatrzymania.
Warunek akceptacji: zgodne liczby i ukończenie drugiego raportu bez pomocy autora.

## POTWIERDZONE — kontrola techniczna
- 103/103 testów przeszło: build/simple-regression-final.log.
- Test cyklu launchera z atrapą okna/procesu: otwarcie przeglądarki raz po gotowości,
  zakończenie własnego procesu przy zamykaniu. Nie jest to test klikania w prawdziwe EXE.
- Nowe EXE uruchomiono jako izolowany serwer lokalny; rzeczywisty Edge pobrał oba PDF-y.
- Demo: 1 250,00 PLN i 7 pozycji. Profil hurtowni: 600,00 PLN, netto, zysk 230,00 PLN.
- Przeglądarka: import, zapisany profil, PDF oraz unieważnianie pobrania po zmianie dat/pliku.
- PDF-y pobrane z EXE: 2 i 3 strony; sumy sprawdzone tekstowo, wszystkie 5 stron
  wyrenderowane i obejrzane. Brak widocznych ucięć lub nakładania treści.
- Ekran startowy i dashboardy obejrzane na zrzutach z przeglądarki.
- git diff --check: bez błędów białych znaków.

Znaleziono i naprawiono zachowywanie wcześniejszej wartości waluty po odtworzeniu profilu.
Usunięcie klucza widgetu nie resetowało wartości w rzeczywistej przeglądarce. Odtwarzanie
teraz jawnie ustawia wszystkie pola; test przeglądarkowy wymaga etykiety PLN.
Scenariusz testowy również poprawiono: czeka na nowy zakres dat i gotowy panel,
zamiast sprawdzać ekran przed zakończeniem przeliczenia.

Artefakty: build/simple-qa/browser-evidence.json, pdf-evidence.json, demo.pdf,
business.pdf, zrzuty PNG i rendery. Skrypty: scripts/qa_simple_release.py,
scripts/qa_simple_browser.cjs.

Paczka: release/AutoReportAnalyst-Windows-2026-09-29-simple.zip. Zbudowano nowy launcher
i biblioteki, po korekcie profilu zaktualizowano zewnętrzny plik simple_app.py i ponownie
przetestowano ten sam folder EXE przed końcowym spakowaniem.

UNKNOWN: rzeczywiste kliknięcie w okno launchera i automatyczne otwarcie przeglądarki
z normalnie uruchomionego EXE — narzędzia kontroli Windows i przeglądarki nie uruchomiły
się z błędem sandboxa `apply deny-read ACLs`. Test przeglądarkowy wykonano lokalnym
Playwright/Edge; test launchera jest testem z atrapami. Czysty Windows i nowy użytkownik
pozostają nieprzetestowane.
