# Dashboard — stan implementacji i dowody
Data: 2026-09-18. Werdykt: GO do kontrolowanej demonstracji i próby odbiorcy.

## Zakres wykonany
1. Kontrakt: DASHBOARD_CONTRACT.md.
2. Niezależny wzorzec: sample_data/dashboard_reference.csv i dashboard_expected.json.
3. Wspólna analiza: app/analysis.py; dashboard i pipeline PDF korzystają z tego samego modelu.
4. Daty i kategorie obejmują oba okresy. Pusty wybór nie oznacza wszystkich kategorii.
5. Układ: trzy widoki, wspólne filtry, stonowane kolory, dokładne etykiety, kontrola na 1440×1050 i 1280×800.
6. Przegląd: KPI, różnice, dzień/tydzień, Top 5 i pozostałe, paginowana tabela pozycji.
7. Kategorie: wkład w zmianę, porównanie okresów, tabela i zastosowanie kategorii do całego widoku.
8. Jakość: diagnostyka źródła i filtrów, kompletność, powtórzenia, kwoty ujemne.
9. PDF: eksport ukończonego wyniku bez ponownego importu, jawne kategorie, sumujący się ranking, szablon 3.
10. Dostarczenie: osobny EXE dashboardu, skrypt budowy, instrukcja, protokół drugiego komputera i pilota.

Kroki 2–9 wykonano technicznie. Krok 10 wykonano w zakresie lokalnej paczki i jej kontroli; próba na drugim komputerze i samodzielne użycie przez odbiorcę pozostają UNKNOWN.

## POTWIERDZONE
- 50 testów automatycznych przeszło, bez pominięć. Log: build/dashboard-tests.log.
- Nowe testy obejmują ręczne oczekiwania, ujemną/zerową bazę, puste filtry, granice tygodni, powtórzenia, ostatni grosz dużej sumy, diagnostykę oraz zgodność PDF.
- Test interfejsu sprawdza, że sama analiza nie tworzy pliku i że zmiana dat usuwa stare pobranie.
- PDF syntetyczny dla A: 400,00 PLN / 2 pozycje / średnia 200,00 PLN, baza 300,00 PLN, +33,3%. Długie polskie nazwy sprawdzono na osobnym stresowym raporcie.
- Wyrenderowano i obejrzano 2 strony wzorca oraz 3 strony stresowe. Po dodaniu kolumny różnicy ponownie sprawdzono zmienioną stronę porównania.
- Osobna paczka EXE uruchomiła serwer lokalny. Test w Edge załadował demo, wszystkie trzy widoki, porównanie oraz pobrał PDF; brak wyjątków aplikacji i błędów JavaScript.
- Dane pomiaru: 100 000 syntetycznych pozycji. Import + analiza 1,9231 s; ponowna analiza z filtrem 0,0602 s. Cele przed pomiarem: odpowiednio <=10 s i <=1 s.
- Pomiary dotyczą silnika na tym komputerze, bez czasu renderowania przeglądarki, eksportu źródłowego ani pracy użytkownika.
- Surowe dowody: build/dashboard-qa/evidence.json, browser-evidence.json i zrzuty PNG.

## HIPOTEZA i UNKNOWN
- HIPOTEZA: tygodniowy przegląd dla właściciela małej hurtowni.
- UNKNOWN: oszczędność czasu, przewaga nad obecnym raportem/Excelem, popyt, akceptacja ceny.
- UNKNOWN: start na drugim czystym Windows, zgodność konkretnego starszego CPU, samodzielny drugi raport rzeczywistego użytkownika.
- Minimalny test: docs/DASHBOARD_PILOT.md. Brak tych wyników nie jest dowodem gotowości sprzedażowej.

## Granice i decyzje
- Jedna waluta, jawny format, bez SaaS, ML, LLM i publikacji.
- PDF ma dzienny trend dla tych samych filtrów; przełącznik tygodniowy dotyczy wizualizacji dashboardu.
- Kategorie na wykresach porównawczych ograniczono do 20, z jawną etykietą. Pełna tabela pozostaje dostępna.
- Szukanie kategorii zawęża tabelę, nie zmienia globalnego wyniku. Osobny przycisk stosuje kategorię globalnie.
- Procenty w summary.json zachowują zgodność z dotychczasowym polem liczbowym; obliczenia i wartości pieniężne pozostają dokładne.
- Paczka zawiera lokalny serwer Streamlit i wymaga przeglądarki. Dotychczasowe wydanie Tkinter pozostaje osobnym artefaktem.

Paczka: release/AutoReportDashboard-Windows.zip (92 251 998 bajtów). Hash ZIP i EXE: build/dashboard-qa/package-evidence.json.
