# Build on Windows from the Creator repository root:
#   python -m PyInstaller --noconfirm --clean Creator.spec
from pathlib import Path

root = Path(SPECPATH).resolve()

def bundle_dir(name):
    folder = root / name
    return [(str(folder), name)] if folder.is_dir() else []

datas = []
for folder in ('patterns', 'assets', 'images', 'fonts', 'sounds'):
    datas += bundle_dir(folder)
if (root / 'logo.png').is_file():
    datas.append((str(root / 'logo.png'), '.'))

analysis = Analysis(
    [str(root / 'main.py')],
    pathex=[str(root)],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pytest'],
    noarchive=False,
)
pyz = PYZ(analysis.pure)
exe = EXE(
    pyz,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name='Creator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon=str(root / 'Creator.ico'),
)
coll = COLLECT(
    exe,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=False,
    name='Creator',
)
