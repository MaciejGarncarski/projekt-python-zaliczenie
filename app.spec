a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[('constants.py', 'dialog.py', 'ftp.py', 'labeled_input.py', 'login.py', 'select_login_info.py', 'server.py', 'assets/logo.png', 'utils.py')],
    hiddenimports=[],
)