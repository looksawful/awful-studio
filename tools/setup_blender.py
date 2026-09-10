"""Download one exact official Blender build, verify its official SHA-256, unpack locally."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import shutil
import tarfile
import urllib.error
import urllib.request
import zipfile

VERSION = '5.2.1'
BASES = (
    'https://mirror.blender.org/release/Blender5.2/',
    'https://download.blender.org/release/Blender5.2/',
)
USER_AGENT = 'AWFUL-STUDIO-CI/0.0.16 (+https://github.com/looksawful/awful-studio)'


def open_official(path, timeout):
    errors = []
    for base in BASES:
        request = urllib.request.Request(base + path, headers={'User-Agent': USER_AGENT, 'Accept': '*/*'})
        try:
            return urllib.request.urlopen(request, timeout=timeout), base
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            errors.append(f'{base}: {exc}')
    raise RuntimeError('Unable to download Blender from official mirrors: ' + '; '.join(errors))


def install(destination):
    system = platform.system()
    if platform.machine().lower() not in ('amd64', 'x86_64') or system not in ('Linux', 'Windows'):
        raise RuntimeError('This setup script supports Linux/Windows x64 only')
    suffix = 'windows-x64.zip' if system == 'Windows' else 'linux-x64.tar.xz'
    filename = f'blender-{VERSION}-{suffix}'
    destination.mkdir(parents=True, exist_ok=True)

    response, checksum_base = open_official(f'blender-{VERSION}.sha256', 60)
    with response:
        checksum_text = response.read().decode('utf-8')
    matches = [line.split()[0] for line in checksum_text.splitlines()
               if len(line.split()) == 2 and line.split()[1].lstrip('*') == filename]
    if len(matches) != 1 or len(matches[0]) != 64:
        raise RuntimeError('Exact distribution checksum not found in official checksum file')

    archive = destination / filename
    response, archive_base = open_official(filename, 120)
    with response, archive.open('wb') as output:
        shutil.copyfileobj(response, output)
    digest = hashlib.file_digest(archive.open('rb'), 'sha256').hexdigest()
    if digest != matches[0].lower():
        raise RuntimeError('Blender distribution SHA-256 mismatch')

    if system == 'Windows':
        with zipfile.ZipFile(archive) as package:
            for item in package.infolist():
                target = (destination / item.filename).resolve()
                if not target.is_relative_to(destination.resolve()):
                    raise ValueError('Unsafe distribution ZIP path')
            package.extractall(destination)
    else:
        with tarfile.open(archive) as package:
            package.extractall(destination, filter='data')

    executable = destination / f'blender-{VERSION}-{suffix.split(".")[0]}' / ('blender.exe' if system == 'Windows' else 'blender')
    if not executable.is_file():
        raise FileNotFoundError(executable)
    (destination/'distribution.json').write_text(json.dumps({
        'version': VERSION,
        'url': archive_base + filename,
        'checksum_url': checksum_base + f'blender-{VERSION}.sha256',
        'sha256': digest,
        'platform': system,
    }, indent=2))
    return executable


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--destination', type=Path, default=Path('.blender'))
    args = parser.parse_args()
    print(install(args.destination.resolve()))
