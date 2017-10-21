from distutils.core import setup
import py2exe, sys

sys.argv.append('py2exe')

py2exe_options = {
        'includes': ['sip', 'PyQt5.QtCore', 'PyQt5.QtGui'],
        'compressed': 1,
        'optimize': 2,
        'ascii': 0,
        'bundle_files': 2
        }

setup(name='SimpleCard', console=[r'card_server.py'], windows=[r'card_client.py'], zipfile=None, options={'py2exe': py2exe_options})
