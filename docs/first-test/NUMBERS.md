# Niezależny wzorzec liczb

Właściciel danych potwierdza definicje i liczy oczekiwania ręcznie lub w
sprawdzonym arkuszu. Nie przepisuj wyniku Auto-Report jako oczekiwania.
Do pierwszego testu używamy jednego eksportu, okresu, waluty i podstawy kwot.

1. Zapisz SHA-256 CSV i profil wyeksportowany z ustawień aplikacji.
2. Wypełnij kopię [expected.template.json](expected.template.json): okres,
   liczbę pozycji, sumę, średnią i wszystkie kategorie w tym okresie.
   Kwoty są tekstem z kropką i dwoma miejscami. `reference_note` opisuje autora,
   metodę i miejsce niezależnego wyliczenia.
3. Sprawdź profil z [DATA_AGREEMENT.md](DATA_AGREEMENT.md). Nie stosuj profilu demo
   do rzeczywistego CSV bez potwierdzenia definicji.
4. W środowisku źródłowym projektu opcjonalnie uruchom:

   ```powershell
   .\build\portfolio\source-venv\Scripts\python.exe scripts/verify_acceptance.py --csv docs/first-test/fixtures/corrected-example.csv --profile docs/first-test/fixtures/profile.json --expected docs/first-test/fixtures/expected.json --output build/first-test/moj-wynik.json
   ```

   Podana komenda korzysta wyłącznie ze sztucznego przykładu. Dla klienta podaj
   trzy jego lokalne pliki i nową ścieżkę wyniku. Istniejący wynik nie jest nadpisywany.
   Weryfikator korzysta z analizy programu, ale oczekiwania pochodzą z osobnego
   dokumentu. Nie tworzy ich automatycznie. Brak wymaganych oczekiwań → kod 2,
   `INCOMPLETE_OR_INVALID`; niezgodne liczby → kod 2, `FAIL`.
5. Osobno otwórz PDF i porównaj liczby oraz daty z tym samym wzorcem. Opcjonalne
   miary biznesowe, porównania i kompletność wymagają osobnych wyliczeń i odbioru.

Kod 0 / `PASS_NUMBERS_ONLY` potwierdza zgodność wskazanych liczb analizy CSV.
Akceptacja klienta pozostaje UNKNOWN do rzeczywistego potwierdzenia.
Blankiet i pliki demonstracyjne nie dowodzą poprawności eksportu klienta.
