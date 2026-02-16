# build.spec


block_cipher = None

a = Analysis(
    ['lanc.py', 'launcher.py', 'mods.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('logo.ico', '.'),                     
        ('mods.py', '.'),             
        ('launcher.py', '.'),         
    ],
    hiddenimports=[
        'http.server',
        'socketserver',
        'os',
        'threading',
        'time',
        'sys',
        'json',
        'urllib',
        'uuid',
        'subprocess',

       
        'webview',
        'webview.platforms.winforms',
        'webview.platforms.cef',
        'minecraft_launcher_lib',
        'minecraft_launcher_lib.command',
        'minecraft_launcher_lib.forge',
        'minecraft_launcher_lib.utils',
        'minecraft_launcher_lib.types',
        'minecraft_launcher_lib.exception',
        'requests',

  
        'pynbt',
        'pynbt.tag',
        'pynbt.file',

       
        'urllib3',
        'urllib3.connection',
        'charset_normalizer',
        'idna',
        'certifi',
        'packaging',
        'packaging.version',
        'packaging.specifiers',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='DreamwoodLauncher', 
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='logo.ico',  

)
