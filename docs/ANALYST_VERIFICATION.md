# Weryfikacja wydania Analityk — 2026-09-19
POTWIERDZONE na komputerze deweloperskim:
- 57 testów automatycznych zakończonych powodzeniem.
- Gotowe AutoReportAnalyst.exe: uruchomienie na 127.0.0.1:8501, wczytanie demo, deklaracja kompletności, trzy widoki, pobranie PPTX; bez wyjątków aplikacji i błędów JavaScript.
- PPTX pobrany z EXE: trzy slajdy, kontrola integralności i geometrii, ponowny import i render, kontrola wizualna wszystkich stron.
- Dodatkowe przypadki eksportu: ujemne kwoty, brak kompletności, długi tytuł i nazwy; eksport pojedynczego widoku sprawdzony testem automatycznym.
- ZIP sprawdzony przez testzip; 92 747 984 bajty.
- SHA-256 ZIP: bdb71fc6ee5dd9961a4e08925a200a41bb29e4535945971a96e492fc77971b1e
- git diff --check: brak błędów białych znaków.
Dowody lokalne: build/analyst-live/tests-final.log, release-evidence.json, browser.json, browser-validation-v2.json i browser-1.png do browser-3.png.
Prezentacja z EXE: output/presentations/AutoReport-analityk-browser-v2.pptx.
UNKNOWN: test czystego Windows, rzeczywisty Microsoft PowerPoint oraz praca realnego klienta. Nie wydajemy werdyktu gotowości sprzedażowej.
