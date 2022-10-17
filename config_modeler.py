"""
    Конфигурационные параметры для работы программы
"""
import json
from PyQt5 import QtGui
from PyQt5 import (QtWidgets, QtCore)
from PyQt5.QtWidgets import (QWidget, QLabel, QFontDialog)
from PyQt5.QtGui import *
import common_data as cd
import os
import time


class Form(QWidget):
    select_file = 'config.json'
    exist = False
    old_interval = None
    new_interval = None
    form_parent = None
    selected_ind = None
    name_config = ''

    def __init__(self, name_config):
        super().__init__()
        self.name_config = name_config
        self.setFont(QtGui.QFont('Arial', 9))
# контейнер для кнопок
        layout_button = QtWidgets.QHBoxLayout()

        self.choose_button = QtWidgets.QPushButton(cd.icon_do, '')
        self.choose_button.clicked.connect(self.choose_button_click)
        layout_button.addWidget(self.choose_button)

        self.loadFile_button = QtWidgets.QPushButton(cd.iconOpen, '')
        self.loadFile_button.clicked.connect(self.load_file)
        layout_button.addWidget(self.loadFile_button)

        self.saveFile_button = QtWidgets.QPushButton(cd.iconSave, '')
        self.saveFile_button.clicked.connect(self.save_file)
        layout_button.addWidget(self.saveFile_button)

        layout_button.addWidget(QLabel(), 2)
        self.create_button = QtWidgets.QPushButton(cd.iconCreate, '')
        self.create_button.clicked.connect(self.create_button_click)
        layout_button.addWidget(self.create_button)

        self.delete_button = QtWidgets.QPushButton(cd.iconDelete, '')
        self.delete_button.clicked.connect(self.delete_button_click)
        layout_button.addWidget(self.delete_button)

        layout_button.addWidget(QLabel(), 10)

        self.font_button = QtWidgets.QPushButton(cd.icon_font, '')
        self.font_button.clicked.connect(self.choos_font)
        layout_button.addWidget(self.font_button)

        self.close_button = QtWidgets.QPushButton('')
        self.close_button.clicked.connect(self.close_button_click)
        layout_button.addWidget(self.close_button)

        self.root_model = QStandardItemModel()
        self.table = QtWidgets.QTreeView(self)
        self.table.setRootIsDecorated(True)
        self.table.setAlternatingRowColors(True)
        self.table.setIndentation(20)
        self.table.setUniformRowHeights(False)
        self.table.setSortingEnabled(True)
        self.table.setWordWrap(True)
        self.table.setModel(self.root_model)
        header = self.table.header()
        header.setHighlightSections(True)
        header.setSectionsClickable(True)
        header.setSectionsMovable(True)
        self.table.setSelectionBehavior(1)  # выделяется одна строка целиком
        # выбор строки мышкой
        self.root_model.itemChanged.connect(self.item_changed)  # событие по изменению
        self.table.selectionModel().selectionChanged.connect(self.row_change)
        self.table.header().setDefaultSectionSize(250)

        self.layout_button = QtWidgets.QHBoxLayout()
        self.statusbar = QLabel()
        self.layout_button.addWidget(self.statusbar)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addLayout(layout_button)
        self.layout.addWidget(self.table, 10)
        self.layout.addLayout(self.layout_button)
# запомненные настройки
        if cd.settings.contains("config_modeler"):
            self.setGeometry(cd.settings.value("config_modeler"))
        else:
            self.resize(800, 600)
        if cd.settings.contains("config_modeler_font"):
            self.setFont(cd.settings.value("config_modeler_font"))

        self.exist = True
        if self.select_file:
            self.load_file()
            self.statusbar.setText(os.getcwd() + '//' + self.select_file)
        self.change_language()
        self.set_font()
        self.show()

    def change_language(self):
        self.font_button.setText(cd.get_text('Font', key='main', id_text=1))
        self.font_button.setStatusTip(cd.get_text('Font', key='main', id_text=1))
        self.choose_button.setText(cd.get_text('Выбрать', key='main', id_text=3))
        self.close_button.setText(cd.get_text('Закрыть', key='main', id_text=12))
        self.loadFile_button.setText(cd.get_text('Загрузить из файла', id_text=6, key='rest'))
        self.saveFile_button.setText(cd.get_text('Сохранить в файл', id_text=5, key='rest'))
        self.setWindowTitle(cd.get_text('Конфигурации соединения с REST API', id_text=15, key='rest'))
        self.create_button.setText(cd.get_text('New', key='one', id_text=12))
        self.delete_button.setText(cd.get_text('Delete', key='one', id_text=13))
        self.make_header()

    def make_header(self):
        st_name = list()
        st_name.append('Status')
        st_name.append('Name config/Parameter')
        st_name.append('Value')
        st_name.append('Init value')
        self.root_model.setHorizontalHeaderLabels(st_name)
        self.table.setColumnHidden(3, True)

# сохранить в файл
    def save_file(self):
        try:
            st = list()
            for j in range(self.root_model.rowCount()):
                config = dict()
                ind = self.root_model.index(j, 0)
                if self.root_model.data(ind) == 'Delete':
                    continue
                ind = self.root_model.index(j, 1)
                config['name'] = self.root_model.data(ind)
                ind = ind.sibling(ind.row(), 0)
                item = self.root_model.itemFromIndex(ind)  # 0-го уровня заданной колонки (или 0-й колонки)
                for i in range(item.rowCount()):
                    ind = item.child(i).index()
                    ind2 = ind.sibling(ind.row(), 2)  # колонка с value
                    ind1 = ind.sibling(ind.row(), 1)
                    key = self.root_model.data(ind1)  # key
                    if key == 'interval':
                        config[key] = int(self.root_model.data(ind2))
                    else:
                        config[key] = self.root_model.data(ind2)
                st. append(config)
            st = json.dumps(st, indent=4, ensure_ascii=False)
            f = open(self.select_file, 'w', encoding='utf-8')
            with f:
                f.write(st)
            self.load_file()
        except Exception as e:
            st = " Error: " + f"{e}"
            QtWidgets.QMessageBox.critical(None, "cd.settings", st,
                                           defaultButton=QtWidgets.QMessageBox.Ok)

# определить имя файла и загрузить его
    def load_file(self):
        self.load_from_file(self.select_file)
        self.is_need_to_save()

    def add_row(self, item, data, key, default=None):
        row = list()
        row.append(QStandardItem(''))
        row.append(QStandardItem(key))
        if key in data:
            row.append(QStandardItem(str(data[key])))
            row.append(QStandardItem(str(data[key])))
        else:
            if default is not None:
                row.append(QStandardItem(str(default)))
                row.append(QStandardItem(str(default)))
            else:
                row.append(QStandardItem())
                row.append(QStandardItem())
        item.appendRow(row)
        # только на чтение
        for jj in range(len(row)):
            ind = row.__getitem__(jj)
            if jj in [0, 1]:
                ind.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

# прочитать из указанного файла и вывести его текст и все установить все поля
    def load_from_file(self, filename):
        self.exist = False
        self.root_model.setRowCount(0)
        try:
            f = open(filename, 'r', encoding='utf-8')
            with f:
                datas = f.read()
                datas = json.loads(datas)
                self.make_header()
                for data in datas:
                    row = list()
                    row.append(QStandardItem(''))
                    if 'name' in data:
                        row.append(QStandardItem(data['name']))
                        row.append(QStandardItem())
                        row.append(QStandardItem(data['name']))
                    else:
                        row.append(QStandardItem())
                        row.append(QStandardItem())
                        row.append(QStandardItem())
                    self.root_model.appendRow(row)
                    # только на чтение
                    for jj in range(len(row)):
                        ind = row.__getitem__(jj)
                        if jj not in [0, 1]:
                            ind.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

                    ind = self.root_model.index(self.root_model.rowCount() - 1, 0)
                    model_index = self.root_model.sibling(ind.row(), 0, ind)
                    standard_item = self.root_model.itemFromIndex(model_index)
                    self.add_row(standard_item, data, 'url')
                    self.add_row(standard_item, data, 'schema_name')
                    self.add_row(standard_item, data, 'info_code')
                    self.add_row(standard_item, data, 'interval')
                    self.add_row(standard_item, data, 'user_name')
                    self.add_row(standard_item, data, 'password')
                self.table.expandAll()
                cd.set_width_columns(self.table, increment=10)
        except Exception:
            pass
            # self.text_file.setText('Ошибка \n' + f"{e}")
        self.exist = True
        ind_select = None
        for j in range(self.root_model.rowCount()):
            ind = self.root_model.index(j, 1)
            if self.root_model.data(ind) == self.name_config:
                ind_select = ind
                break
        if ind_select is None:
            ind_select = self.root_model.index(0, 0)
        self.table.setCurrentIndex(ind_select)

# развернуть окно формы
    def bring_to_front(self):
        self.showMinimized()
        self.showNormal()

# изменить шрифт
    def choos_font(self):
        font, ok = QFontDialog.getFont(self.font())
        if ok:
            self.setFont(font)
            self.set_font()

    def set_font(self):
        self.table.setFont(self.font())
        self.table.header().setFont(self.font())
        cd.set_width_columns(self.table, increment=10)
        self.choose_button.setFont(self.font())
        self.choose_button.setStyleSheet("color: green")

    # закрыть окно
    def closeEvent(self, evt):
        cd.settings.setValue("config_modeler", self.geometry())
        cd.settings.setValue("config_modeler_font", self.font())
        cd.settings.sync()

    def customEvent(self, evt):
        if evt.type() == cd.StatusOperation.idType:  # изменение состояния соединения для PROXY
            n = evt.get_data()
            if n == cd.evt_change_language:
                self.change_language()

    def close_button_click(self):
        self.close()

    def is_need_to_save(self):
        if self.exist:
            self.exist = False
            exist_change = False
            for j in range(0, self.root_model.rowCount()):
                value = None
                ind0 = self.root_model.index(j, 0)  # колонка СТАТУС
                if self.root_model.data(ind0) == 'Delete':
                    exist_change = True
                else:
                    ind2 = self.root_model.index(j, 1)  # колонка с value
                    ind3 = self.root_model.index(j, 3)  # колонка с начальным value
                    value = self.root_model.data(ind3)
                    if value is None:
                        self.root_model.setData(ind0, 'Create')
                        exist_change = True
                    elif self.root_model.data(ind2).strip() != value.strip():
                        self.root_model.setData(ind0, 'Changed')
                        exist_change = True
                    else:
                        self.root_model.setData(ind0, '')
                ind = self.root_model.index(j, 0)
                item = self.root_model.itemFromIndex(ind)  # 0-го уровня заданной колонки (или 0-й колонки)
                if item.hasChildren():  # 0-ой уровень и есть дети
                    for i in range(item.rowCount()):
                        ind = item.child(i).index()
                        ind00 = ind.sibling(ind.row(), 0)  # колонка СТАТУС
                        ind2 = ind.sibling(ind.row(), 2)  # колонка с value
                        ind3 = ind.sibling(ind.row(), 3)  # колонка с начальным value
                        if self.root_model.data(ind0) == 'Delete':
                            self.root_model.setData(ind0, 'Delete')
                        else:
                            if self.root_model.data(ind2).strip() != self.root_model.data(ind3).strip():
                                self.root_model.setData(ind00, 'Changed')
                                if value is not None:
                                    self.root_model.setData(ind0, 'Changed')
                                exist_change = True
                            else:
                                self.root_model.setData(ind00, '')
            self.exist = True
            cd.set_width_columns(self.table, increment=10)
            self.saveFile_button.setEnabled(exist_change)
            self.loadFile_button.setEnabled(exist_change)

    def item_changed(self):
        self.is_need_to_save()

    def row_change(self):
        if self.exist:
            ind = self.table.selectionModel().currentIndex()
            self.selected_ind = ind.sibling(ind.row(), 0)
            item = self.root_model.itemFromIndex(self.selected_ind)  # 0-го уровня заданной колонки (или 0-й колонки)
            self.delete_button.setEnabled(item.rowCount() != 0)
            if item.rowCount() == 0:
                self.selected_ind = self.selected_ind.parent()  # индекс родителя

    def choose_button_click(self):
        item = self.root_model.itemFromIndex(self.selected_ind)  # 0-го уровня заданной колонки (или 0-й колонки)
        ind = item.index()
        ind = ind.sibling(ind.row(), 1)
        st = self.root_model.data(ind)
        cd.settings.setValue("config_modeler_name", st)
        cd.settings.sync()
        for i in range(item.rowCount()):
            ind = item.child(i).index()
            ind1 = ind.sibling(ind.row(), 1)  # колонка key
            ind2 = ind.sibling(ind.row(), 2)  # колонка с value
            key = self.root_model.data(ind1)
            value = self.root_model.data(ind2)
            if key == 'interval':
                cd.interval_connection = int(value)
            elif key == 'user_name':
                cd.username = value
            elif key == 'password':
                cd.password = value
            elif key == 'url':
                cd.url = value
            elif key == 'schema_name':
                cd.schema_name = value
        cd.mas_json_objects = []
        self.form_parent.start_check_connection()
        cd.inform_from_proxy = ''
        cd.login()
        print('config_modeler', cd.expires, time.ctime(cd.expires), cd.token)
        cd.send_evt(cd.evt_change_config_modeler, self.form_parent)
        self.close()

    def create_button_click(self):
        row = list()
        row.append(QStandardItem(''))
        st = 'New configuration'
        row.append(QStandardItem(st))
        row.append(QStandardItem())
        row.append(QStandardItem())
        self.root_model.appendRow(row)

        ind = self.root_model.index(self.root_model.rowCount() - 1, 0)
        model_index = self.root_model.sibling(ind.row(), 0, ind)
        standard_item = self.root_model.itemFromIndex(model_index)
        self.add_row(standard_item, {}, 'url', 'http://127.0.0.1:5000/')
        self.add_row(standard_item, {}, 'schema_name', '')
        self.add_row(standard_item, {}, 'info_code', 'nsi')
        self.add_row(standard_item, {}, 'interval', 30)
        self.add_row(standard_item, {}, 'user_name', '')
        self.add_row(standard_item, {}, 'password', '')

        self.table.expandAll()
        cd.set_width_columns(self.table, increment=10)
        self.is_need_to_save()

    def delete_button_click(self):
        self.exist = False
        item = self.root_model.itemFromIndex(self.selected_ind)  # 0-го уровня заданной колонки (или 0-й колонки)
        ind = item.index()
        ind0 = ind.sibling(ind.row(), 0)
        if self.root_model.data(ind0) == 'Delete':  # снятие удаления
            self.root_model.setData(ind0, '')
        elif self.root_model.data(ind0) == 'Create':  # удалить еще не созданный
            self.root_model.removeRow(ind.row())
        else:
            self.root_model.setData(ind0, 'Delete')
        self.exist = True
        self.is_need_to_save()
