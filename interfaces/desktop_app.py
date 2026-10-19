import sys
from pathlib import Path
if not getattr(sys, "frozen", False):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import argparse
import json
import os
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from app.config import BASE_DIR, OUTPUT_DIR, VERSION
from app.pipeline import generate_report
from app.profiles import load_profile, save_profile
from app.validation import CsvProfile, CURRENCIES, ENCODINGS, DATE_FORMATS


class AutoReportApp:
    def __init__(self, root):
        self.root = root
        root.title(f"Auto-Report {VERSION}")
        root.geometry("850x760")
        root.minsize(760, 600)
        self.results = queue.Queue()
        self.busy = False
        self.last_output = None
        profile_error = None
        try:
            profile = load_profile()
        except ValueError as exc:
            profile, profile_error = CsvProfile(), str(exc)
        self.vars = {key: (tk.BooleanVar(value=value) if isinstance(value,bool) else tk.StringVar(value=value)) for key, value in profile.to_dict().items() if key != "allow_negative"}
        self.allow_negative = tk.BooleanVar(value=profile.allow_negative)
        self.csv_path = tk.StringVar()
        self.output_dir = tk.StringVar(value=OUTPUT_DIR)
        self.days = tk.StringVar(value="7")
        self.start = tk.StringVar()
        self.end = tk.StringVar()
        self.coverage_start = tk.StringVar()
        self.coverage_end = tk.StringVar()
        self.status = tk.StringVar(value=profile_error or "Wybierz CSV i sprawdź profil danych.")
        shell = ttk.Frame(root)
        shell.pack(fill="both", expand=True)
        canvas = tk.Canvas(shell, highlightthickness=0)
        scroll = ttk.Scrollbar(shell, orient="vertical", command=canvas.yview)
        scroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.configure(yscrollcommand=scroll.set)
        frame = ttk.Frame(canvas, padding=20)
        window = canvas.create_window((0, 0), window=frame, anchor="nw")
        frame.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda event: canvas.itemconfigure(window, width=event.width))
        root.bind("<MouseWheel>", lambda event: canvas.yview_scroll(int(-event.delta / 120), "units"))
        frame.columnconfigure(1, weight=1)
        ttk.Label(frame, text="Raport z Twojego CSV", font=("Segoe UI", 20, "bold")).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 12))
        ttk.Label(frame, text="Dane są przetwarzane lokalnie. Każdy raport ma osobny katalog.").grid(row=1, column=0, columnspan=3, sticky="w")
        self.entry(frame, 2, "Plik CSV", self.csv_path)
        ttk.Button(frame, text="Wybierz", command=self.choose_csv).grid(row=2, column=2, padx=8)
        self.entry(frame, 3, "Katalog raportów", self.output_dir)
        ttk.Button(frame, text="Zmień", command=self.choose_output).grid(row=3, column=2, padx=8)
        ttk.Label(frame, text="Profil eksportu", font=("Segoe UI", 12, "bold")).grid(row=4, column=0, sticky="w", pady=(12, 4))
        for row, key, label in ((5, "date_col", "Kolumna daty"), (6, "value_col", "Kolumna kwoty"), (7, "category_col", "Kolumna kategorii")):
            self.entry(frame, row, label, self.vars[key])
        for row, key, label, values in (
            (8, "delimiter", "Separator CSV", [",", ";", "\t"]),
            (9, "encoding", "Kodowanie", ENCODINGS),
            (10, "date_format", "Daty: %Y=rok, %m=miesiąc, %d=dzień", DATE_FORMATS),
            (11, "decimal_separator", "Separator dziesiętny", [".", ","]),
            (12, "amount_basis", "Podstawa kwoty", ["nieokreślona", "netto", "brutto"]),
            (23, "currency", "Waluta źródła (XXX = nieokreślona)", CURRENCIES),
            (24, "amount_precision", "Precyzja: strict lub HALF_UP do 2 miejsc", ["strict","half_up"]),
        ):
            ttk.Label(frame, text=label).grid(row=row, column=0, sticky="w", pady=3)
            ttk.Combobox(frame, textvariable=self.vars[key], values=values, state="readonly").grid(row=row, column=1, sticky="ew")
        ttk.Checkbutton(frame, text="Dopuszczam kwoty ujemne (np. zwroty); pozostają w sumie", variable=self.allow_negative).grid(row=13, column=0, columnspan=3, sticky="w")
        ttk.Button(frame, text="Zapisz profil na następny raz", command=self.save).grid(row=14, column=1, sticky="w", pady=7)
        self.entry(frame, 15, "Ostatnie N dni (gdy daty poniżej puste)", self.days)
        self.entry(frame, 16, "Okres od (RRRR-MM-DD)", self.start)
        self.entry(frame, 17, "Okres do (RRRR-MM-DD)", self.end)
        ttk.Label(frame, text="Opcjonalnie: potwierdzony PEŁNY zakres eksportu. Nie wpisuj tu tylko dat pierwszej i ostatniej pozycji.", wraplength=735).grid(row=18, column=0, columnspan=3, sticky="w", pady=(10, 4))
        self.entry(frame, 19, "Pełny eksport od", self.coverage_start)
        self.entry(frame, 20, "Pełny eksport do", self.coverage_end)
        self.generate_button = ttk.Button(frame, text="Generuj raport PDF", command=self.run_report_threaded)
        self.generate_button.grid(row=21, column=0, pady=14, sticky="w")
        self.open_button = ttk.Button(frame, text="Otwórz ostatni raport", command=self.open_report, state="disabled")
        self.open_button.grid(row=21, column=1, sticky="w")
        ttk.Label(frame, textvariable=self.status, wraplength=740).grid(row=22, column=0, columnspan=3, sticky="w")
        root.after(100, self.poll)

    def entry(self, frame, row, label, variable):
        ttk.Label(frame, text=label).grid(row=row, column=0, sticky="w", pady=4)
        ttk.Entry(frame, textvariable=variable).grid(row=row, column=1, sticky="ew", pady=3)

    def profile(self):
        return CsvProfile(**{key: value.get() for key, value in self.vars.items()}, allow_negative=self.allow_negative.get())

    def choose_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if path:
            self.csv_path.set(path)

    def choose_output(self):
        path = filedialog.askdirectory()
        if path:
            self.output_dir.set(path)

    def save(self):
        try:
            save_profile(self.profile())
            self.status.set("Profil zapisany. Zakres eksportu potwierdź osobno dla każdego pliku.")
        except (ValueError, OSError) as exc:
            self.status.set(str(exc))

    def run_report_threaded(self):
        if self.busy:
            return
        try:
            if not Path(self.csv_path.get()).is_file():
                raise ValueError("Wybierz istniejący plik CSV.")
            profile = self.profile()
            profile.validate()
            days = int(self.days.get()) if not self.start.get().strip() else None
            kwargs = {"input_csv_path": self.csv_path.get(), "report_last_n_days": days,
                      "profile": profile, "output_dir": self.output_dir.get(),
                      "start_date": self.start.get().strip() or None, "end_date": self.end.get().strip() or None,
                      "coverage_start": self.coverage_start.get().strip() or None,
                      "coverage_end": self.coverage_end.get().strip() or None}
        except (ValueError, OSError) as exc:
            self.status.set(str(exc))
            return
        self.busy = True
        self.generate_button.configure(state="disabled")
        self.status.set("Sprawdzam dane i generuję raport...")
        threading.Thread(target=self.worker, args=(kwargs,), daemon=True).start()

    def worker(self, kwargs):
        # No Tk calls outside the UI thread.
        try:
            self.results.put(("ok", generate_report(**kwargs)))
        except Exception as exc:
            self.results.put(("error", str(exc)))

    def poll(self):
        try:
            kind, result = self.results.get_nowait()
            self.busy = False
            self.generate_button.configure(state="normal")
            if kind == "ok":
                self.last_output = result
                self.open_button.configure(state="normal")
                self.status.set("Gotowe: " + result)
            else:
                self.status.set("Raport nie powstał: " + result)
        except queue.Empty:
            pass
        self.root.after(100, self.poll)

    def open_report(self):
        if self.last_output:
            try:
                os.startfile(self.last_output)
            except OSError as exc:
                self.status.set(str(exc))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke-test", metavar="OUTPUT_DIR")
    args = parser.parse_args()
    if args.smoke_test:
        output = generate_report(str(Path(BASE_DIR) / "sample_data" / "pilot_demo.csv"), 7,
                                 output_dir=args.smoke_test, profile=CsvProfile(amount_basis="netto"),
                                 coverage_start="2026-08-31", coverage_end="2026-09-13",
                                 title="Przykład na danych syntetycznych")
        Path(args.smoke_test, "smoke-result.json").write_text(json.dumps({"output": output, "version": VERSION}), encoding="utf-8")
        return
    root = tk.Tk()
    AutoReportApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
