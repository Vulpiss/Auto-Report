"""Package the existing verified application and the first-test materials.

No EXE rebuild, installation, publishing, or overwrite of previous handoffs.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
from urllib.parse import unquote, urlsplit
from zipfile import ZipFile, ZIP_DEFLATED, ZIP_STORED

ROOT = Path(__file__).resolve().parents[1]
APPLICATION = 'AutoReportAnalyst-Windows-2026-10-06-hardening.zip'
APPLICATION_SHA = 'd99a954fc1c3be63c452e0607a6158f99f7196df3754cfa8e2dcadcf71f6f430'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def local_links(folder):
    count = 0
    for file in folder.rglob('*.md'):
        for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', file.read_text(encoding='utf-8')):
            target = target.strip().strip('<>')
            if urlsplit(target).scheme or target.startswith('#'):
                continue
            path = (file.parent / unquote(target.split('#', 1)[0])).resolve()
            if not path.is_relative_to(folder.resolve()) or not path.exists():
                raise ValueError(f'Broken handoff link: {file.relative_to(folder)} -> {target}')
            count += 1
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tag', default='2026-10-14')
    args = parser.parse_args()
    if not re.fullmatch('[a-zA-Z0-9-]+', args.tag):
        parser.error('Invalid tag')
    name = 'AutoReport-FirstTest-Windows-' + args.tag
    target = ROOT / 'release' / name
    archive = target.with_suffix('.zip')
    log_dir = ROOT / 'build/first-test' / ('package-' + args.tag)
    if any(path.exists() for path in (target, archive, log_dir)):
        parser.error('Tag already exists; earlier handoffs are preserved')
    app = ROOT / 'release' / APPLICATION
    if digest(app) != APPLICATION_SHA:
        raise ValueError('The application archive differs from the release tested on 2026-10-06')
    with ZipFile(app) as z:
        if z.testzip() is not None:
            raise ValueError('Application ZIP failed CRC')
        release = json.loads(z.read('AutoReportAnalyst/RELEASE.json'))
        if hashlib.sha256(z.read('AutoReportAnalyst/AutoReportAnalyst.exe')).hexdigest() != release['exe_sha256']:
            raise ValueError('EXE differs from application manifest')
    target.mkdir(parents=True)
    log_dir.mkdir(parents=True)
    shutil.copytree(ROOT / 'docs/first-test', target / 'docs/first-test')
    for filename in ('DATA_CONTRACT.md', 'LOCAL_HARDENING_RESULTS.md', 'LOCAL_HARDENING_EVIDENCE.json'):
        shutil.copy2(ROOT / 'docs' / filename, target / 'docs' / filename)
    (target / 'scripts').mkdir()
    shutil.copy2(ROOT / 'scripts/Test-Workstation.ps1', target / 'scripts/Test-Workstation.ps1')
    (target / 'release').mkdir()
    shutil.copy2(app, target / 'release' / APPLICATION)
    (target / 'README.md').write_text(
        '# Auto-Report — pierwszy test\n\n'
        'Zacznij od [instrukcji](docs/first-test/START_HERE.md). '
        'Paczka zawiera sprawdzony lokalnie EXE, konfigurację VM, sztuczne dane '
        'i niewypełnione protokoły. VM ani pilot nie zostały wykonane.\n', encoding='utf-8')
    manifest = dict(date='2026-10-14', kind='FIRST_TEST_PREPARATION', application=APPLICATION,
                    application_zip_sha256=APPLICATION_SHA, exe_sha256=release['exe_sha256'],
                    source_rebuilt=False, clean_windows='UNKNOWN', user_independence='UNKNOWN',
                    customer_pilot='NOT_STARTED', files={p.relative_to(target).as_posix(): digest(p)
                    for p in sorted(target.rglob('*')) if p.is_file()})
    (target / 'MANIFEST.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    links = local_links(target)
    with ZipFile(archive, 'x', compression=ZIP_DEFLATED) as z:
        for path in sorted(target.rglob('*')):
            if path.is_file():
                z.write(path, name + '/' + path.relative_to(target).as_posix(),
                        compress_type=ZIP_STORED if path.suffix == '.zip' else ZIP_DEFLATED)
    with ZipFile(archive) as z:
        if z.testzip() is not None:
            raise ValueError('Handoff ZIP failed CRC')
        for rel, expected in manifest['files'].items():
            if hashlib.sha256(z.read(name + '/' + rel)).hexdigest() != expected:
                raise ValueError('Handoff file mismatch: ' + rel)
        z.extractall(log_dir / 'unpacked')
    unpacked_links = local_links(log_dir / 'unpacked' / name)
    evidence = dict(result='PASS', release=archive.name, bytes=archive.stat().st_size,
                    sha256=digest(archive), source_rebuilt=False, packaged_files=len(manifest['files']) + 1,
                    local_links=links, unpacked_links=unpacked_links, crc=True,
                    application_zip_sha256=APPLICATION_SHA, clean_windows='UNKNOWN', customer_pilot='NOT_STARTED')
    (log_dir / 'evidence.json').write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(evidence), flush=True)


if __name__ == '__main__':
    main()
