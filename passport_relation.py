from PyQt5.QtGui import *
from PyQt5 import (QtWidgets, QtCore)
from PyQt5.QtWidgets import (QWidget, QLabel)
import common_data as cd
import json


class PassportRelation(QWidget):
    caption = 'Паспорт отношений многие-к-многим'
    rel_typeobj_code = None  # код класса объектов RELATION
    rel_code = None  # имя поля идентификатора с типом данных RELATION
    typeobj_code = None
    code = None  # имя собственного поля идентификатора
    value_code = None  # значение собственного идентификатора
    delegateCheckBox = None
    exist = False
    qrow = 0
    formaParent = None

    def __init__(self, parent, form_parent):
        super(QWidget, self).__init__()
        self.formaParent = form_parent
    # контейнер для кнопок
        layoutButton = QtWidgets.QHBoxLayout()
        # обновить список (с потерей возможных изменений)
        self.refresh_button = QtWidgets.QPushButton(cd.iconRefresh, '')
        self.refresh_button.clicked.connect(self.refresh_click)
        layoutButton.addWidget(self.refresh_button)
        # создать объект
        self.add_all_button = QtWidgets.QPushButton(cd.iconCreate, '')
        self.add_all_button.clicked.connect(self.add_all_click)
        layoutButton.addWidget(self.add_all_button)
        # удалить объект
        self.delete_all_button = QtWidgets.QPushButton('')
        self.delete_all_button.clicked.connect(self.delete_all_click)
        layoutButton.addWidget(self.delete_all_button)
        # создать параметр
        self.revert_button = QtWidgets.QPushButton('')
        self.revert_button.clicked.connect(self.revert_click)
        layoutButton.addWidget(self.revert_button)
    # контейнер для дерева
        LayoutTable = QtWidgets.QVBoxLayout()
        LayoutTable.addLayout(layoutButton)
        self.root_model = QStandardItemModel()
        self.table = QtWidgets.QTreeView()
        # self.table.setAlternatingRowColors(True)
        self.table.setIndentation(20)
        self.table.setUniformRowHeights(False)
        self.table.setSortingEnabled(True)
        self.table.setWordWrap(True)
        self.table.setModel(self.root_model)
    # выбор строки мышкой
        self.table.pressed.connect(self.choosChange)
        self.table.activated.connect(self.choosChange)
        self.table.clicked.connect(self.choosChange)
        LayoutTable.addWidget(self.table)
        header = self.table.header()
        header.setHighlightSections(True)
        header.setSectionsClickable(True)
        header.setSectionsMovable(True)
        self.table.setSelectionBehavior(1)  # выделяется одна строка целиком

        self.root_model.setHorizontalHeaderLabels(['Status', 'Choos', 'Name', 'ID', 'ChoosInit'])
        self.table.header().setDefaultSectionSize(100)
        # self.root_model.itemChanged.connect(self.choosChange)
    # строка статуса
        layout3 = QtWidgets.QHBoxLayout()
        self.statusbar = QLabel()
        layout3.addWidget(self.statusbar)
        LayoutTable.addLayout(layout3)
        #
        parent.setLayout(LayoutTable)
        self.change_language()

    def change_language(self):
        caption = cd.get_text('Паспорт отношений многие-к-многим', id_text=4, key='relations')
        self.refresh_button.setText(cd.get_text('Восстановить', id_text=30, key='main'))
        self.add_all_button.setText(cd.get_text('Все пометить', id_text=5, key='enum'))
        self.delete_all_button.setText(cd.get_text('Все снять', id_text=6, key='enum'))
        self.revert_button.setText(cd.get_text('Перевернуть', id_text=5, key='relations'))
        self.show_status()

    def add_all_click(self):
        ind = None
        for i in range(0, self.root_model.rowCount()):
            ind = self.root_model.index(i, 1)  # колонка Choos
            item = self.root_model.item(ind.row(), 1)  # нулевая колонка родителя
            item.setCheckState(QtCore.Qt.Checked)
        if ind is not None:
            self.choosChange(ind)

    def choosChange(self, item):
        if self.exist:
            self.formaParent.is_need_to_save()
            self.show_status()

    def delete_all_click(self):
        ind = None
        for i in range(0, self.root_model.rowCount()):
            ind = self.root_model.index(i, 1)  # колонка Choos
            item = self.root_model.item(ind.row(), 1)  # нулевая колонка родителя
            item.setCheckState(QtCore.Qt.Unchecked)
        if ind is not None:
            self.choosChange(ind)

    def refresh(self):
        for j in range(0, self.root_model.rowCount()):
            ind4 = self.root_model.index(j, 4)
            val = self.root_model.data(ind4)  # начальное значение
            ind1 = self.root_model.index(j, 1)  # колонка с новым значением
            item = self.root_model.item(ind1.row(), 1)  # нулевая колонка родителя
            if val == 1:
                item.setCheckState(QtCore.Qt.Checked)
            else:
                item.setCheckState(QtCore.Qt.Unchecked)

    def refresh_click(self):
        ind = None
        for i in range(0, self.root_model.rowCount()):
            ind = self.root_model.index(i, 4)  # колонка Choos
            val = self.root_model.data(ind)
            ind = self.root_model.index(i, 1)  # колонка Choos
            item = self.root_model.item(ind.row(), 1)  # нулевая колонка родителя
            if val == 1:
                item.setCheckState(QtCore.Qt.Checked)
            else:
                item.setCheckState(QtCore.Qt.Unchecked)
        if ind is not None:
            self.choosChange(ind)

    def revert_click(self):
        ind = None
        for i in range(0, self.root_model.rowCount()):
            ind = self.root_model.index(i, 1)  # колонка Choos
            item = self.root_model.item(ind.row(), 1)  # нулевая колонка родителя
            if item.checkState() == QtCore.Qt.Checked:
                item.setCheckState(QtCore.Qt.Unchecked)
            else:
                item.setCheckState(QtCore.Qt.Checked)
        if ind is not None:
            self.choosChange(ind)

    def save(self):
        params = []
        for j in range(0, self.root_model.rowCount()):
            ind0 = self.root_model.index(j, 0)  # колонка статуса
            if self.root_model.data(ind0) != '':
                ind1 = self.root_model.index(j, 1)  # колонка с новым значением
                item = self.root_model.item(ind1.row(), 1)  # нулевая колонка родителя
                if item.checkState() == QtCore.Qt.Checked:
                    val_new = 1
                else:
                    val_new = 0
                ind2 = self.root_model.index(j, 3)  # колонка с идентификатором
                st = self.root_model.data(ind2)
                param = {}
                param['obj_id'] = st
                param['value'] = val_new
                param['id'] = str(self.value_code)
                params.append(param)
        if len(params) > 0:
            txt = 'v1/relations/' + cd.schema_name + '/' + self.typeobj_code + '/' + self.rel_code
            ans, result = cd.send_rest(txt, 'PUT', params=params)
            if result:
                for j in range(0, self.root_model.rowCount()):
                    ind1 = self.root_model.index(j, 1)  # колонка с новым значением
                    item = self.root_model.item(ind1.row(), 1)  # нулевая колонка родителя
                    if item.checkState() == QtCore.Qt.Checked:
                        val_new = 1
                    else:
                        val_new = 0
                    ind4 = self.root_model.index(j, 4)
                    self.root_model.setData(ind4, val_new)

    def show_list(self):
        self.root_model.setRowCount(0)  # сбросить таблицу
        ans, result = cd.send_rest('v1/entities/' + cd.schema_name + '/' + self.rel_typeobj_code)
        if result:
            try:
                mas_json = json.loads(ans)
                for mas in mas_json:
                    node = QStandardItem()
                    node.setCheckable(True)
                    row = [
                        QStandardItem(""),
                        node,
                        QStandardItem(cd.translate_from_base(mas["sh_name"])),
                        QStandardItem(str(mas["id"]))
                    ]
                    for jj in range(0, len(row)):
                        ind = row.__getitem__(jj)
                        if jj != 1:  # колонка не CHOOS
                            ind.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                    self.root_model.appendRow(row)
                self.qrow = len(mas_json)
                self.show_status()
            except:
                QtWidgets.QMessageBox.critical(self, "Pasport_relation: show_list",
                    cd.get_text('Ошибка', id_text=4, key='main') + ' \n' + ans, defaultButton=QtWidgets.QMessageBox.Ok)
    # ширина колонок по содержимому
        for j in range(0, self.root_model.columnCount()):
            self.table.resizeColumnToContents(j)

    def show_data(self):
        self.exist = False
        self.table.setColumnHidden(4, True)  # колонка с объектом
        self.table.setColumnHidden(0, True)  # колонка с объектом
        ans = 'v1/relations/' + cd.schema_name + '/' + self.typeobj_code + '/' + self.rel_code
        if self.value_code is not None:
            ans = ans + '/' + str(self.value_code)
        ans, result = cd.send_rest(ans)
        # выставить птички там где они есть
        if result:
            js = json.loads(ans)
            for j in range(0, self.root_model.rowCount()):
                ind4 = self.root_model.index(j, 4)
                self.root_model.setData(ind4, 0)
                item = self.root_model.item(j, 1)  # колонка choos в найденной строке
                item.setCheckState(QtCore.Qt.Unchecked)
            for j in range(0, len(js)):
                ind = cd.getInd(self.root_model, str(js[j]["id"]), 3)  # строка с нужным ID из json
                ind4 = ind.sibling(ind.row(), 4)
                if ind:
                    item = self.root_model.item(ind.row(), 1)  # колонка choos в найденной строке
                    item.setCheckState(QtCore.Qt.Checked)
                    self.root_model.setData(ind4, 1)
        self.exist = True
        self.show_status()

    def show_status(self):
        q = 0
        for i in range(0, self.root_model.rowCount()):
            ind = self.root_model.index(i, 1)  # колонка Choos
            item = self.root_model.item(ind.row(), 1)  # нулевая колонка родителя
            if item.checkState() == QtCore.Qt.Checked:
                q = q + 1
        self.statusbar.setText(cd.get_text('Объектов', id_text=21, key='main', delete_lf=True) + '= ' +
                               cd.str1000(self.qrow) + '; ' + cd.get_text('Выбрано', id_text=6, key='relations') +
                               '= ' + cd.str1000(q))

    def what_changed(self):
        result = ''
        if self.exist:
            for j in range(0, self.root_model.rowCount()):
                ind0 = self.root_model.index(j, 0)  # колонка СТАТУС
                ind1 = self.root_model.index(j, 1)  # колонка с новым значением
                item = self.root_model.item(ind1.row(), 1)  # нулевая колонка родителя
                ind4 = self.root_model.index(j, 4)  # колонка со старым значением
                ind3 = self.root_model.index(j, 2)  # колонка с именем
                if item.checkState() == QtCore.Qt.Checked:
                    val_new = 1
                else:
                    val_new = 0
                val_old = ind4.data()
                if val_new != val_old:
                    if result != '':
                        result = result + '\n'
                    if val_new == 1:
                        result = result + 'insert: '
                    else:
                        result = result + 'DELETE: '
                    result = result + ind3.data()
                    st = cd.get_text('Изм', id_text=31, key='main')
                else:
                    st = ''
                self.root_model.setData(ind0, st)
            if result != '':
                result = '\t' + self.caption + ':\n' + result
        return result

    def customEvent(self, evt):
        if evt.type() == cd.StatusOperation.idType:  # изменение состояния соединения с PROXY
            n = evt.get_data()
            if n == cd.evt_change_language:
                self.change_language()
