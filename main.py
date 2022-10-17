import sys
from PyQt5 import QtWidgets, QtGui
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
import common_data as cd
import form

app = QtWidgets.QApplication(sys.argv)

cd.settings = QtCore.QSettings("Демидов", "Контракты")
if cd.settings.contains("app_language"):
    cd.app_lang = cd.settings.value("app_language", "ru")
if cd.app_lang == '':
    cd.app_lang = 'en'
cd.load_texts(cd.app_lang)

splash = QtWidgets.QSplashScreen(QtGui.QPixmap("icons/DSC05235.JPG"))
splash.showMessage(
    cd.get_text('Инициация программы "Контракты"', id_text=0, key='main'), QtCore.Qt.AlignTop, QtCore.Qt.red)
splash.show()

win = form.Form()
win.setWindowIcon(QIcon('icons/wConstructor_Icon.ico'))
win.show()

splash.finish(win)
sys.exit(app.exec())
