# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None
project_root = os.path.abspath(".")

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        (os.path.join(project_root, 'app.py'), '.'),
        (os.path.join(project_root, 'templates'), 'templates'),
        (os.path.join(project_root, 'huffman_icon.ico'), '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=['tkinter', 'unittest', 'test', 'pydoc'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='launcher',
    debug=False,
    strip=False,
    upx=True,
    console=False,
    icon='huffman_icon.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='launcher'
)
