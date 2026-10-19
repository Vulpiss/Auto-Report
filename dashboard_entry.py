"""Desktop launcher with an owned local server and an explicit Stop button."""
import os
import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]

def serve(port):
    from streamlit.web import cli
    root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    sys.argv = ["streamlit", "run", str(root / "interfaces/simple_app.py"),
        "--global.developmentMode=false", "--server.address=127.0.0.1", f"--server.port={port}",
        "--server.headless=true", "--server.maxUploadSize=100", "--browser.gatherUsageStats=false",
        "--server.fileWatcherType=none", "--theme.base=light", "--theme.primaryColor=#237b86"]
    cli.main()

def main():
    if "--serve" in sys.argv:
        if sys.stdout is None or sys.stderr is None:
            destination = sys.argv[sys.argv.index("--log") + 1] if "--log" in sys.argv else os.devnull
            sys.stdout = sys.stderr = open(destination, "a", encoding="utf-8", buffering=1)
        serve(int(sys.argv[sys.argv.index("--serve") + 1]))
        return
    import tkinter as tk
    from tkinter import ttk
    import urllib.request
    window = tk.Tk()
    window.title("Auto-Report")
    window.geometry("520x245")
    window.resizable(False, False)
    status = tk.StringVar(value="Uruchamiam program. Za chwilę otworzy się przeglądarka…")
    ttk.Label(window, text="Auto-Report", font=("Segoe UI", 20, "bold")).pack(pady=(18, 10))
    ttk.Label(window, textvariable=status, wraplength=470, justify="center").pack(pady=8)
    port = free_port()
    url = f"http://127.0.0.1:{port}"
    log_dir = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "AutoReport" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"start-{os.getpid()}.log"
    log = log_path.open("w", encoding="utf-8")
    command = [sys.executable] + ([] if getattr(sys, "frozen", False) else [str(Path(__file__).resolve())]) + ["--serve", str(port), "--log", str(log_path)]
    process = None
    def stop():
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=3)
        log.close()
        window.destroy()
    def open_browser():
        if not webbrowser.open(url):
            status.set("Otwórz przeglądarkę i wpisz adres: " + url)
    open_button = ttk.Button(window, text="Otwórz raport w przeglądarce", command=open_browser, state="disabled")
    open_button.pack(pady=5)
    ttk.Button(window, text="Zakończ program", command=stop).pack(pady=5)
    window.protocol("WM_DELETE_WINDOW", stop)
    try:
        process = subprocess.Popen(command, stdout=log, stderr=log,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
    except OSError as exc:
        status.set(f"Nie udało się uruchomić programu: {exc}")
    started = time.monotonic()
    def poll():
        if process is None:
            return
        if process.poll() is not None:
            open_button.configure(state="disabled")
            status.set("Program został zatrzymany. Jeśli to błąd, przekaż plik: " + str(log_path))
            return
        if str(open_button["state"]) == "normal":
            window.after(1000, poll)
            return
        try:
            with urllib.request.urlopen(url + "/_stcore/health", timeout=.3) as response:
                ready = response.status == 200 and response.read() == b"ok"
        except OSError:
            ready = False
        if ready:
            open_button.configure(state="normal")
            status.set("Program działa. Możesz wrócić do raportu przyciskiem poniżej. Po pracy kliknij „Zakończ program”.")
            open_browser()
        elif time.monotonic() - started > 90:
            status.set("Uruchomienie trwa dłużej. Możesz zakończyć program i uruchomić go ponownie. Zapis diagnostyczny: " + str(log_path))
        window.after(1000, poll)
    window.after(500, poll)
    window.mainloop()

if __name__ == "__main__":
    main()
