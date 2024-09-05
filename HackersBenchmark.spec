# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['HackersBenchmark.py'],
    pathex=[],
    binaries=[],
    datas=[('resources/sprites/*.png', 'resources/sprites'), ('resources/sprites/Challenges/*.png', 'resources/sprites/Challenges'), ('resources/fonts/*', 'resources/fonts'), ('resources/files/*', 'resources/files')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)
splash = Splash(
    'Honeypot_Logo_BG_Centered.jpg',
    binaries=a.binaries,
    datas=a.datas,
    text_pos=None,
    text_size=12,
    minify_script=True,
    always_on_top=True,
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    splash,
    splash.binaries,
    [],
    name='HackersBenchmark',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['Honeypot.ico'],
)
