from PyQt5.QtGui import QIcon
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import (QMainWindow, QWidget, QAction, QComboBox, QPushButton,
                             QStyle, QTabWidget, QLabel, QApplication, QFontDialog, QInputDialog)
import time
import json
import os
import common_data as cd
import pagecontrol
import clock
import choos_language
import check_connect_DB
import config_modeler
import entities
# import one_day
# import summary
# import common_db


class Form(QMainWindow):
    exist = False
    cn = None
    configModeler = None
    config_modeler = None
    # one_day_form = None
    # summary_form = None
    name_config = 'Contract'
    stylesheet = """ 
        QTabBar::tab:selected {background: salmon;}
        """

    def __init__(self):
        super().__init__()
        self.setFont(QtGui.QFont('Arial', 11))
        cd.iconRefresh = self.style().standardIcon(QtWidgets.QStyle.SP_BrowserReload)
        cd.iconDelete = self.style().standardIcon(QtWidgets.QStyle.SP_DialogCancelButton)
        cd.iconUp = self.style().standardIcon(QtWidgets.QStyle.SP_ArrowUp)
        cd.iconDown = self.style().standardIcon(QtWidgets.QStyle.SP_ArrowDown)
        cd.icon_left = self.style().standardIcon(QtWidgets.QStyle.SP_ArrowLeft)
        cd.icon_right = self.style().standardIcon(QtWidgets.QStyle.SP_ArrowRight)
        cd.iconCreate = QIcon()
        cd.iconCreate.addFile('icons/Добавить.bmp')
        cd.icon_font = QIcon()
        cd.icon_font.addFile('icons/font.bmp')
        cd.icon_do = QIcon()
        cd.icon_do.addFile('icons/tick.bmp')
        cd.icon_minus = QIcon()
        cd.icon_minus.addFile('icons/удалить.bmp')
        cd.iconSave = self.style().standardIcon(QtWidgets.QStyle.SP_DialogSaveButton)
        cd.iconOpen = self.style().standardIcon(QtWidgets.QStyle.SP_DialogOpenButton)

        # определить адресацию RestProxy
        try:
            f = open('config.json', 'r', encoding='utf-8')
            with f:
                datas = f.read()
                datas = json.loads(datas)
                if cd.settings.contains("config_modeler_name"):
                    self.name_config = cd.settings.value("config_modeler_name")
                else:
                    self.name_config = datas[0]['name']
                for data in datas:
                    if data['name'] == self.name_config:
                        cd.interval_connection = data['interval']
                        cd.info_code = data['info_code']
                        cd.schema_name = data['schema_name']
                        cd.url = data['url']
                        cd.username = data['user_name']
                        cd.password = data['password']
                        break
        except Exception as e:
            cd.txt_error_connection = cd.get_text('Ошибка', id_text=4, key='main') + '\n' + f"{e}"
            QtWidgets.QMessageBox.critical(
                self, cd.get_text("Чтение конфигурации", id_text=1, key='form'),
                cd.txt_error_connection + '\n' + ' file configurations= ' + os.getcwd() + '/config.json',
                defaultButton=QtWidgets.QMessageBox.Ok)
        self.set_window_title(cd.version + ' [' + cd.url + ']')
        cd.login(show_error=False)
        print('form', cd.expires, time.ctime(cd.expires), cd.token)

        # common_db.make_change_in_db()

        # поток с таймером для вывода времени в Statusbar
        self.labelConnect = QLabel('')
        self.labelConnect.setStyleSheet("color: red")
        self.statusBar().addPermanentWidget(self.labelConnect)  # постоянная часть справа

        self.labelTime = QLabel('')
        self.statusBar().addPermanentWidget(self.labelTime)  # постоянная часть справа
        self.statusBar().addWidget(QLabel('  '))
        self.label_app = QLabel('schema_name= ' + cd.schema_name)
        self.statusBar().addWidget(self.label_app)
        self.statusBar().addWidget(QLabel(''), 3)
# запустим проверку соединения с PROXY
        self.start_check_connection()

        self.setObjectName('MainWindow')

        self.widget = QWidget()
        self.page_control = pagecontrol.PageControl(self.widget, QTabWidget.West)
        self.page_control.tabs.currentChanged.connect(self.page_control_changed)
# Страница "Сущности"
        self.tabEntities = self.page_control.addTab('')
        self.entities = entities.Entities(self.tabEntities)
        self.entities.form_parent = self
#         self.tabSummary = self.page_control.addTab('')
        # self.summary_form = summary.Form(self.tabSummary)
        # self.summary_form.form_parent = self

# Страница "Одни сутки"
#         self.tabOneDay = self.page_control.addTab('')
        # self.one_day_form = one_day.Form(self.tabOneDay)
        # self.one_day_form.form_parent = self
# окончание программы
        self.exitaction = QAction(self.style().standardIcon(QStyle.SP_DialogCancelButton), '', self)
        self.exitaction.setShortcut('Alt+X')
        self.exitaction.triggered.connect(self.closeEvent)
# сменить язык
        self.language = QAction('', self)
        self.language.triggered.connect(self.language_click)
# выбрать фонт
        self.choosfont = QAction(cd.icon_font, '', self)
        self.choosfont.setShortcut('Ctrl+F')
        self.choosfont.triggered.connect(self.choos_font)
# реконнект с БД
        self.reconnect = QAction('Reconnect', self)
        self.reconnect.triggered.connect(self.reconnect_click)
# XML для Modeler
        self.configModeler = QAction('', self)
        self.configModeler.triggered.connect(self.xml_modeler)
# меню
        menubar = self.menuBar()
        self.menuConsol = menubar.addMenu('')

        self.menuConsol.addAction(self.choosfont)  # выбрать фонт
        self.menuConsol.addAction(self.language)  # выбрать язык
        self.menuConsol.addAction(self.reconnect)
        self.menuConsol.addSeparator()
        self.menuConsol.addAction(self.exitaction)  # menuStop

        self.menuDop = menubar.addMenu('')
        self.menuDop.addAction(self.configModeler)
# запустим таймер для вывода времени
        t = clock.ClockThread(1, self.labelTime)
        t.start()
        time.sleep(1)

# запомненные настройки
        try:
            if cd.settings.contains("Contract"):
                self.setGeometry(cd.settings.value("Contract"))
            else:
                self.resize(cd.width_form, cd.height_form)
            if cd.settings.contains("Contract_Font"):
                self.setFont(cd.settings.value("Contract_Font"))
        except Exception:
            self.resize(cd.width_form, cd.height_form)
        if cd.settings.contains("Contract_SchemaName"):
            cd.schema_name = cd.settings.value("Contract_SchemaName")

        # перейти на страницу одних суток
        try:
            if cd.settings.contains("Contract_page_index"):
                index = int(cd.settings.value("Contract_page_index"))
            else:
                index = 1
            self.page_control.tabs.setCurrentIndex(index)
        except Exception:
            index = 1
        self.setCentralWidget(self.page_control)
        if cd.txt_error_connection != '':
            self.labelConnect.setText('No connection with PROXY')

        self.exist = True
        self.set_font()
        self.change_language()
        # self.one_day_form.load_category()
        # self.one_day_form.define_rashod_id()
        self.page_control_changed(index)
        self.show()

    def set_window_title(self, version):
        self.setWindowTitle(cd.get_text('Контракты', id_text=-1, key='main') + version)

    def change_language(self):
        self.choosfont.setText(cd.get_text('Font', key='main', id_text=1))
        self.choosfont.setStatusTip(cd.get_text('Font', key='main', id_text=1))
        self.language.setText(cd.get_text("Choice of language", key='main', id_text=2))
        self.language.setStatusTip(cd.get_text("Choice of language", key='language', id_text=1))
        self.page_control.tabs.setTabText(0, cd.get_text('Сущности', id_text=7, key='form'))
        self.reconnect.setText(cd.get_text("Reconnect", id_text=27, key='form'))
        self.reconnect.setStatusTip(cd.get_text("Reconnect", id_text=27, key='form'))
        # self.page_control.tabs.setTabText(1, cd.get_text('Суточные расходы', id_text=8, key='form'))
        self.exitaction.setText(cd.get_text('Exit', id_text=6, key='main'))
        self.exitaction.setStatusTip(cd.get_text('Exit application', id_text=7, key='main'))
        self.menuConsol.setTitle(cd.get_text('Консоль', id_text=8, key='main'))
        self.menuDop.setTitle(cd.get_text('Дополнительно', id_text=9, key='main'))
        self.configModeler.setText(cd.get_text('Настройки связи с БД', id_text=11, key='form'))
        self.configModeler.setStatusTip(cd.get_text('XML for Modeler', id_text=12, key='form'))
        self.set_window_title(
            cd.version + cd.url + ' ' + cd.inform_from_proxy.replace("'", '"') +
            ' System=' + cd.schema_name)

    def language_click(self):
        language = choos_language.Language(self)
        language.exec_()

    def start_check_connection(self):
        if self.cn:
            self.cn.needStop = True
        self.set_window_title(cd.version + ' [' + cd.url + ']')
        self.cn = check_connect_DB.ClockThread(self, self.labelConnect)
        self.cn.start()

    def choos_font(self):
        font, ok = QFontDialog.getFont(self.font())
        if ok:
            self.setFont(font)
            self.entities.set_font(font)
            # self.summary_form.set_font(font)

    def page_control_changed(self, index):
        if self.exist:
            if index == 0:
                self.entities.make_obnov_click()
                self.entities.make_inform()
                pass
            elif index == 1:
                # self.modeler.make_obnov()
                pass

    def customEvent(self, evt):
        if evt.type() == cd.StatusOperation.idType:  # изменение состояния соединения с PROXY
            n = evt.get_data()
            if n == cd.evt_cancel_connect:  # пропадание связи REST
                pass
            elif n == cd.evt_refresh_connect:  # восстановление связи REST
                pass
            elif n == cd.evt_change_database:  # сменилась информация от Proxy
                self.set_window_title(
                    cd.version + cd.url + ' ' + cd.inform_from_proxy.replace("'", '"') + ' System=' + cd.schema_name)
            elif n == cd.evt_change_mdm:  # изменения в метаданных
                self.set_window_title(
                    cd.version + cd.url + ' ' + cd.inform_from_proxy.replace("'", '"') +
                    ' System=' + cd.schema_name)
                self.entities.make_obnov_click()
                # self.one_day_form.define_rashod_id()
                # self.one_day_form.read_data()
                # self.summary_form.read_data()
                self.page_control_changed(self.page_control.tabs.currentIndex())
            elif n == cd.evt_change_config_modeler:  # изменения в настройке моделера
                self.set_window_title(
                    cd.version + cd.url + ' ' + cd.inform_from_proxy.replace("'", '"') + ' System=' + cd.schema_name)
                self.entities.close_all_forms()
                self.entities.make_obnov_click()
                # cd.send_evt(n, self.one_day_form)
                # self.one_day_form.read_data()
                # self.summary_form.read_data()
            elif n == cd.evt_change_language:
                self.change_language()
                cd.send_evt(n, self.config_modeler)
                self.entities.change_language()
                # cd.send_evt(n, self.one_day_form)
                # cd.send_evt(n, self.summary_form)
            elif type(n) == dict:
                # cd.send_evt(n, self.one_day_form)
                self.page_control.setCurrentIndex(1)

# закрыть программу
    def closeEvent(self, evt):
        self.entities.close()
        # self.summary_form.close()
        cd.settings.setValue("Contract_page_index", self.page_control.tabs.currentIndex())
        cd.settings.setValue("Contract", self.geometry())
        cd.settings.setValue("Contract_Font", self.font())
        cd.settings.setValue("Contract_SchemaName", cd.schema_name)
        # cd.settings.setValue("app_language", cd.app_lang)
        cd.settings.sync()
        QApplication.quit()

    def set_font(self):
        self.labelTime.setFont(self.font())
        self.labelTime.setStyleSheet("color: blue")
        self.page_control.tabs.setFont(self.font())
        # self.tabOneDay.setFont(self.font())
        # self.tabSummary.setFont(self.font())
        # self.entities.set_font(self.font())
        # self.summary_form.set_font(self.font())

    def xml_modeler(self):
        if self.config_modeler:
            self.config_modeler.bring_to_front()
        else:
            self.config_modeler = config_modeler.Form(self.name_config)
            self.config_modeler.form_parent = self

    def reconnect_click(self):
        self.entities.make_obnov_click()
        self.page_control_changed(self)
