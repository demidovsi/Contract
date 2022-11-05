from PyQt5.QtGui import *
from PyQt5 import (QtWidgets, QtCore)
from PyQt5.QtWidgets import (QWidget, QLabel, QTextEdit)
import common_data as cd
import json


class TextEditDelegate(QtWidgets.QStyledItemDelegate):
    def createEditor(self, parent, options, index):
        return QTextEdit(parent)

    def setEditorData(self, editor, index):
        editor.setText(index.data())

    def setModelData(self, editor, model, index):
        model.setData(index, editor.toPlainText())

    def updateEditorGeometry(self, editor, option, index):
        model = index.model()
        # message = model.data(index, Qt.EditRole)
        new_geometry = option.rect
        new_height = 15 * option.rect.height()
        new_geometry.setHeight(new_height)
        editor.setGeometry(new_geometry)


class PassportLocale(QWidget):
    caption = ''
    code = ''
    value_code = -1  # значение идентификатора локализации
    exist = False
    form_parent = None
    qlanguage = 0

    def __init__(self, parent, form_parent, caption):
        super(QWidget, self).__init__()
        self.form_parent = form_parent
        self.caption = caption
    # контейнер для дерева
        LayoutTable = QtWidgets.QVBoxLayout()
        self.root_model = QStandardItemModel()
        self.table = QtWidgets.QTreeView()
        # self.table.setAlternatingRowColors(True)
        self.table.setIndentation(20)
        self.table.setUniformRowHeights(False)
        self.table.setSortingEnabled(True)
        self.table.setWordWrap(True)
        self.table.setModel(self.root_model)
        self.table.setStyleSheet("*::item{"
                    "    border-top-width: 0px;"
                    "    border-right-width: 1px;"
                    "    border-bottom-width: 1px;"
                    "    border-left-width: 0px;"
                    "    border-style: solid;"
                    "    border-color: green;"
                    "}"
                    "*::item:selected{"
                    "    background: lightblue;"
                    "    color: black;"
                    "}")
        delegate = TextEditDelegate(self.table)
        self.table.setItemDelegateForColumn(3, delegate)
        self.table.resizeColumnToContents(3)
        # выбор строки мышкой
        # self.table.pressed.connect(self.choosChange)
        # self.table.activated.connect(self.choosChange)
        # self.table.clicked.connect(self.choosChange)
        LayoutTable.addWidget(self.table)
        header = self.table.header()
        header.setHighlightSections(True)
        header.setSectionsClickable(True)
        header.setSectionsMovable(True)
        self.table.setSelectionBehavior(1)  # выделяется одна строка целиком

        self.root_model.setHorizontalHeaderLabels(['Status', 'ID', 'Locale', 'Text', 'Text_initial'])
        self.table.header().setDefaultSectionSize(100)
        # self.root_model.item_changed.connect(self.choosChange)
        layout3 = QtWidgets.QHBoxLayout()
        self.statusbar = QLabel()
        layout3.addWidget(self.statusbar)
        LayoutTable.addLayout(layout3)
        #
        parent.setLayout(LayoutTable)

    def show_data(self):
        self.exist = False
        self.root_model.setRowCount(0)  # сбросить таблицу
        self.table.setColumnHidden(4, True)  # начальное значение
        ans, result = cd.send_rest('MDM.LocalesValues/' + str(self.value_code))
        if result:
            try:
                mas_json = json.loads(ans)
                for j in range(0, len(mas_json)):
                    Node = QStandardItem(cd.translate_from_base(mas_json[j]["txt"]))
                    row = [
                        QStandardItem(""),
                        QStandardItem(mas_json[j]["locale_id"]),
                        QStandardItem(mas_json[j]["locale"]),
                        Node,
                        QStandardItem(cd.translate_from_base(mas_json[j]["txt"]))
                    ]
                    # только на чтение
                    # for c in row:
                    #     c.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                    for jj in range(0, len(row)):
                        ind = row.__getitem__(jj)
                        if jj != 3:  # колонка не text
                            ind.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                    self.root_model.appendRow(row)
                if self.value_code:
                    st = str(self.value_code)
                else:
                    st = 'None'
                self.qlanguage = len(mas_json)
                self.statusbar.setText('languages = ' + str(self.qlanguage) + '; ID=' + st)
                self.root_model.itemChanged.connect(self.item_changed)
                # ширина колонок по содержимому
                for j in range(0, self.root_model.columnCount()):
                    self.table.resizeColumnToContents(j)
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Pasport_locale: show_data",
                    cd.get_text('Ошибка', id_text=4, key='main)') + ' \n' + f"{e}" + '\n' + ans,
                                               defaultButton=QtWidgets.QMessageBox.Ok)
        else:
            QtWidgets.QMessageBox.critical(self, "Pasport_locale: show_data",
                    cd.get_text('Ошибка', id_text=4, key='main') + ' \n' + ans,
                                           defaultButton=QtWidgets.QMessageBox.Ok)
        self.exist = True

    def item_changed(self, QStandardItem):
        if self.exist:
            self.form_parent.is_need_to_save()

    def refresh(self):
        for j in range(0, self.root_model.rowCount()):
            ind4 = self.root_model.index(j, 4)
            val = self.root_model.data(ind4)  # начальное значение
            ind3 = self.root_model.index(j, 3)  # колонка с новым значением
            self.root_model.setData(ind3, val)

    def is_need_to_save(self):
        result = False
        for j in range(0, self.root_model.rowCount()):
            ind0 = self.root_model.index(j, 0)  # колонка статуса
            if self.root_model.data(ind0) != '':
                result = True
                break
        return result

    def save(self):
        if self.is_need_to_save():
            if int(self.value_code) <= 0:
                # определить свободный идентификатор Locales
                data, result = cd.send_rest('MDM.LocalesGetID')
                self.value_code = int(cd.get_text_from_answer(data))
            self.statusbar.setText('languages = ' + str(self.qlanguage) + '; ID=' + str(self.value_code))
            for j in range(0, self.root_model.rowCount()):
                ind0 = self.root_model.index(j, 0)  # колонка статуса
                if self.root_model.data(ind0) != '':
                    ind1 = self.root_model.index(j, 1)  # колонка с locale_id
                    ind3 = self.root_model.index(j, 3)  # колонка с txt
                    val_new = cd.translate_to_base(self.root_model.data(ind3))
                    ans, result = cd.send_rest(
                        'MDM.LocalesSetValue/' + self.root_model.data(ind1) + '/' +
                        str(self.value_code) + '/' + val_new, 'POST')
                    if result:
                        ind4 = self.root_model.index(j, 4)
                        self.root_model.setData(ind4, val_new)
                        self.root_model.setData(ind0, '')

    def what_changed(self):
        result = ''
        if self.exist:
            for j in range(0, self.root_model.rowCount()):
                ind0 = self.root_model.index(j, 0)  # колонка СТАТУС
                ind3 = self.root_model.index(j, 3)  # колонка с новым значением
                ind4 = self.root_model.index(j, 4)  # колонка с начальным значением
                ind2 = self.root_model.index(j, 2)  # колонка с именем
                val_new = ind3.data()
                val_old = ind4.data()
                if val_new != val_old:
                    if result != '':
                        result = result + '\n'
                    result = result + ind2.data() + ': ' + val_old + ' --> ' + val_new
                    st = cd.get_text('Изм', id_text=31, key='main')
                else:
                    st = ''
                self.root_model.setData(ind0, st)
            if result != '':
                result = '\t' + self.caption + ':\n' + result
        return result
