"""New frozen build, synthetic CSVs, isolated profile library, actual Edge downloads."""
import json
import os
import socket
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
out = ROOT / 'build/oneclick-qa'
out.mkdir(parents=True, exist_ok=True)
for name, rows in [('first', '2026-09-01,12,A\n'), ('second','2026-10-01,15,A\n2026-10-03,25,B\n'), ('invalid','2026-10-01,broken,A\n')]:
    (out/(name+'.csv')).write_text('data,kwota,kategoria\n'+rows, encoding='utf-8')
exe = ROOT / 'release/analyst-2026-09-30-oneclick/AutoReportAnalyst/AutoReportAnalyst.exe'
node = Path('C:/Users/kompu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe')
with socket.socket() as sock:
    sock.bind(('127.0.0.1', 0))
    port = sock.getsockname()[1]
url = f'http://127.0.0.1:{port}'
with tempfile.TemporaryDirectory(prefix='auto-report-qa-settings-') as settings, (out/'server.log').open('w', encoding='utf-8') as log:
    env = dict(os.environ, AUTOREPORT_PROFILE_DIR=settings)
    process = subprocess.Popen([str(exe), '--serve', str(port), '--log', str(out/'server-child.log')],
        cwd=ROOT, stdout=log, stderr=log, env=env, creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        for _ in range(90):
            if process.poll() is not None: raise RuntimeError(f'EXE exited: {process.returncode}')
            try:
                with urllib.request.urlopen(url+'/_stcore/health', timeout=1) as response:
                    if response.read() == b'ok': break
            except OSError: time.sleep(1)
        else: raise RuntimeError('Server startup timeout')
        subprocess.run([str(node), str(ROOT/'scripts/qa_oneclick_browser.cjs'), url], cwd=ROOT, check=True)
        pages = {}
        for name, expected in [('demo-full','2 250,00'),('demo-week','1 250,00'),('second','40,00')]:
            reader = PdfReader(out/(name+'.pdf'))
            text = '\n'.join(p.extract_text() or '' for p in reader.pages)
            assert expected in text, (name, expected)
            if name == 'second': assert 'EUR' in text
            pages[name] = len(reader.pages)
        (out/'pdf-evidence.json').write_text(json.dumps(pages, indent=2), encoding='utf-8')
        print(json.dumps(pages))
    finally:
        process.terminate()
        try: process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill(); process.wait(timeout=10)
