"""Exercise an isolated frozen server; leave existing app instances untouched."""
import json
import socket
import subprocess
import time
import urllib.request
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
out = ROOT / 'build/simple-qa'
out.mkdir(parents=True, exist_ok=True)
exe = ROOT / 'release/analyst-2026-09-29-simple/AutoReportAnalyst/AutoReportAnalyst.exe'
node = Path('C:/Users/kompu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe')
with socket.socket() as sock:
    sock.bind(('127.0.0.1', 0))
    port = sock.getsockname()[1]
url = f'http://127.0.0.1:{port}'
with (out / 'server.log').open('w', encoding='utf-8') as log:
    process = subprocess.Popen([str(exe), '--serve', str(port), '--log', str(out/'server-child.log')],
        cwd=ROOT, stdout=log, stderr=log, creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        for _ in range(90):
            if process.poll() is not None:
                raise RuntimeError(f'EXE exited: {process.returncode}')
            try:
                with urllib.request.urlopen(url+'/_stcore/health', timeout=1) as response:
                    if response.read() == b'ok': break
            except OSError:
                time.sleep(1)
        else:
            raise RuntimeError('Server startup timeout')
        subprocess.run([str(node), str(ROOT/'scripts/qa_simple_browser.cjs'), url], cwd=ROOT, check=True)
        pages = {}
        for name, expected in [('demo','1 250,00'),('business','600,00')]:
            reader = PdfReader(out/(name+'.pdf'))
            text = '\n'.join(p.extract_text() or '' for p in reader.pages)
            assert expected in text, (name, expected)
            pages[name] = len(reader.pages)
        (out/'pdf-evidence.json').write_text(json.dumps(pages, indent=2), encoding='utf-8')
        print(json.dumps(pages))
    finally:
        process.terminate()
        try: process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill(); process.wait(timeout=10)
