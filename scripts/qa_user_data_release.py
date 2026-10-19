"""Isolated EXE test against the user-authorized local CSV; no external upload."""
import hashlib
import json
import os
import socket
import sys
import subprocess
import tempfile
import time
import urllib.request
from decimal import Decimal
from pathlib import Path
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
out=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'build/five-years-20261001'
expected=json.loads((out/'evidence.json').read_text(encoding='utf-8'))
exe=Path(sys.argv[2]) if len(sys.argv)>2 else ROOT/'release/analyst-2026-10-01-five-years/AutoReportAnalyst/AutoReportAnalyst.exe'
node=Path('C:/Users/kompu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe')
with socket.socket() as sock:
    sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
url=f'http://127.0.0.1:{port}'
with tempfile.TemporaryDirectory(prefix='auto-report-user-data-qa-') as settings, (out/'server.log').open('w',encoding='utf-8') as log:
    process=subprocess.Popen([str(exe),'--serve',str(port),'--log',str(out/'server-child.log')],cwd=ROOT,
        stdout=log,stderr=log,env=dict(os.environ,AUTOREPORT_PROFILE_DIR=settings),creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        for _ in range(90):
            if process.poll() is not None:raise RuntimeError('Server exited')
            try:
                with urllib.request.urlopen(url+'/_stcore/health',timeout=1) as response:
                    if response.read()==b'ok':break
            except OSError:time.sleep(1)
        else:raise RuntimeError('Server timeout')
        if '--period-only' not in sys.argv:
            subprocess.run([str(node),str(ROOT/'scripts/qa_user_data_browser.cjs'),url,str(out)],cwd=ROOT,check=True)
        if len(sys.argv)>3:
            subprocess.run([str(node),sys.argv[3],url,str(out)],cwd=ROOT,check=True)
        reader=PdfReader(out/'exe-report.pdf')
        text='\n'.join(p.extract_text() or '' for p in reader.pages)
        total=f"{Decimal(expected['periods']['whole']['expected']['total']):,.2f}".replace(',',' ').replace('.',',')
        assert total in text,total
        assert 'j.p.' in text
        assert expected['periods']['whole']['start'] in text
        assert expected['periods']['whole']['end'] in text
        assert hashlib.sha256(Path(expected['source']).read_bytes()).hexdigest()==expected['sha256']
        (out/'pdf-evidence.json').write_text(json.dumps(dict(pages=len(reader.pages),total=total,source_unchanged=True),indent=2),encoding='utf-8')
        print('PDF verified:',len(reader.pages),'pages, total',total)
    finally:
        process.terminate()
        try:process.wait(timeout=10)
        except subprocess.TimeoutExpired:process.kill();process.wait(timeout=10)
