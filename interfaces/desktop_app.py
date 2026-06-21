import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from app.pipeline import generate_report

# Ensure local project modules are visible both in normal Python and in PyInstaller build
if getattr(sys, "frozen", False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from main import generate_report

class AutoReportApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto-Report Generator")
        self.root.geometry("620x360")
        self.root.resizable(False, False)

        self.selected_csv_path = tk.StringVar()
        self.last_n_days = tk.StringVar(value="60")
        self.status_text = tk.StringVar(value="Ready.")

        self.build_ui()

    def build_ui(self):
        title = tk.Label(
            self.root,
            text="Auto-Report Generator",
            font=("Arial", 18, "bold"),
        )
        title.pack(pady=15)

        description = tk.Label(
            self.root,
            text="Generate a PDF report from a CSV file without using the terminal.",
            font=("Arial", 10),
        )
        description.pack(pady=5)

        frame = tk.Frame(self.root)
        frame.pack(pady=15, fill="x", padx=25)

        csv_label = tk.Label(frame, text="Selected CSV:")
        csv_label.grid(row=0, column=0, sticky="w")

        csv_entry = tk.Entry(
            frame,
            textvariable=self.selected_csv_path,
            width=55,
            state="readonly",
        )
        csv_entry.grid(row=1, column=0, padx=(0, 10), pady=5)

        browse_button = tk.Button(
            frame,
            text="Browse CSV",
            command=self.select_csv,
            width=15,
        )
        browse_button.grid(row=1, column=1, pady=5)

        days_label = tk.Label(frame, text="Reporting period: last N days")
        days_label.grid(row=2, column=0, sticky="w", pady=(15, 0))

        days_entry = tk.Entry(
            frame,
            textvariable=self.last_n_days,
            width=10,
        )
        days_entry.grid(row=3, column=0, sticky="w", pady=5)

        generate_button = tk.Button(
            self.root,
            text="Generate PDF Report",
            command=self.run_report_threaded,
            width=25,
            height=2,
        )
        generate_button.pack(pady=15)

        status_label = tk.Label(
            self.root,
            textvariable=self.status_text,
            font=("Arial", 10),
            fg="blue",
            wraplength=550,
        )
        status_label.pack(pady=10)

    def select_csv(self):
        file_path = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if file_path:
            self.selected_csv_path.set(file_path)
            self.status_text.set(f"Selected file: {file_path}")

    def run_report_threaded(self):
        thread = threading.Thread(target=self.run_report)
        thread.daemon = True
        thread.start()

    def run_report(self):
        csv_path = self.selected_csv_path.get().strip()

        if not csv_path:
            messagebox.showerror("Missing CSV", "Please select a CSV file first.")
            return

        if not os.path.exists(csv_path):
            messagebox.showerror("File not found", "Selected CSV file does not exist.")
            return

        try:
            days = int(self.last_n_days.get())

            if days <= 0:
                raise ValueError("Number of days must be greater than 0.")

        except ValueError:
            messagebox.showerror("Invalid value", "Last N days must be a positive integer.")
            return

        try:
            self.status_text.set("Generating report... Please wait.")

            output_pdf = generate_report(
                input_csv_path=csv_path,
                report_last_n_days=days,
            )

            self.status_text.set(f"Report generated: {output_pdf}")

            open_pdf = messagebox.askyesno(
                "Report generated",
                f"Report generated successfully:\n\n{output_pdf}\n\nOpen it now?"
            )

            if open_pdf:
                os.startfile(output_pdf)

        except Exception as error:
            self.status_text.set("Error while generating report.")
            messagebox.showerror("Error", str(error))


def main():
    root = tk.Tk()
    app = AutoReportApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()