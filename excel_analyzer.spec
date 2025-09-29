# -*- mode: python ; coding: utf-8 -*-

import sys
from PyInstaller.utils.hooks import collect_data_files

# Streamlit ve plotly için gerekli data dosyaları
datas = []
datas += collect_data_files('streamlit')
datas += collect_data_files('plotly')
datas += collect_data_files('st_aggrid')

# Hidden imports - Streamlit'in çalışması için gerekli
hiddenimports = [
    'streamlit.runtime.scriptrunner.magic_funcs',
    'streamlit.runtime.caching',
    'streamlit.runtime.caching.cache_data_api',
    'streamlit.runtime.caching.cache_resource_api',
    'streamlit.runtime.secrets',
    'streamlit.web.server.server',
    'streamlit.web.server.server_util',
    'streamlit.web.bootstrap',
    'streamlit.logger',
    'streamlit.proto',
    'streamlit.components.v1.components',
    'altair',
    'plotly.graph_objs',
    'plotly.express',
    'plotly.offline',
    'st_aggrid.shared',
    'st_aggrid.grid_options_builder',
    'pandas._libs.tslibs.timedeltas',
    'pandas._libs.tslibs.np_datetime',
    'pandas._libs.tslibs.nattype',
    'pandas._libs.properties',
    'openpyxl.cell._writer',
    'xlrd.biffh',
]

block_cipher = None

a = Analysis(
    ['excel_analyzer.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ExcelAnalyzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None
)