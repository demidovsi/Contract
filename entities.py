from PyQt5.QtWidgets import (QWidget, QLabel, QApplication, QSpinBox, QComboBox, QPushButton, QLineEdit, QGroupBox,
                             QTabWidget)
from PyQt5.QtGui import *
from PyQt5 import (QtWidgets, QtCore)
from PyQt5.QtCore import Qt
import common_data as cd
import json
import typeobject
import passport_entity
import datetime
import pagecontrol


class Entities(QWidget):
    selected_text0 = None  # sh_name типа объектоа
    selected_text1 = None  # sh_name объектов в типе
    object_code = ''
    exist = False
    exist_table = False
    exist_izm = 0
    level = 0
    forms = list()
    ind0 = None  # QStandardItem строки 0-го уровня для выделенной строки
    ind1 = None
    needMakeObnov = True
    qobject = 0
    count_objects = None
    arow = 0  # индекс строки в списке объектов сущности
    qrow = 0  # количество строк в списке объектов выбранной сущности (кол-во объектов)
    selected_ind = None  # индекс объекта в сущности
    form_parent = None

    def __init__(self, parent):
        super(QWidget, self).__init__()

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.setHandleWidth(3)
        panelLeft = QtWidgets.QFrame(self.splitter)
        # контейнер для кнопок
        layout_button_oper = QtWidgets.QHBoxLayout()
        # создать таблицу в БД
        self.create_table_button = QtWidgets.QPushButton(cd.iconCreate, '')
        self.create_table_button.setEnabled(False)
        self.create_table_button.clicked.connect(self.create_table_click)
        layout_button_oper.addWidget(self.create_table_button)
        # удалить таблицу в БД
        self.delete_table_button = QtWidgets.QPushButton(cd.iconDelete, '')
        self.delete_table_button.setEnabled(False)
        self.delete_table_button.clicked.connect(self.delete_table_click)
        layout_button_oper.addWidget(self.delete_table_button)
        # создать все объекты БД
        self.create_allObjectDB_button = QtWidgets.QPushButton(cd.iconSave, '')
        self.create_allObjectDB_button.setEnabled(False)
        self.create_allObjectDB_button.clicked.connect(self.create_all_click)
        layout_button_oper.addWidget(self.create_allObjectDB_button)
        # удалить все объекты БД
        #     self.delete_allObjectDB_button = QtWidgets.QPushButton('Удалить все объекты БД')
        #     layout_button_oper.addWidget(self.delete_allObjectDB_button)

        # обновить список (с потерей возможных изменений)
        self.makeObnov_button = QtWidgets.QPushButton(cd.iconRefresh, '')
        self.makeObnov_button.clicked.connect(self.make_obnov_click)
        layout_button_oper.addWidget(self.makeObnov_button)
        # создать объект
        self.create_object_button = QtWidgets.QPushButton(cd.iconCreate, '')
        self.create_object_button.clicked.connect(self.create_object)
        layout_button_oper.addWidget(self.create_object_button)
        # контейнер для дерева
        layout_table = QtWidgets.QVBoxLayout()
        self.root_model = QStandardItemModel()
        self.table = QtWidgets.QTreeView(panelLeft)
        self.table.setAlternatingRowColors(True)
        self.table.setIndentation(20)
        self.table.setUniformRowHeights(False)
        self.table.setSortingEnabled(True)
        self.table.setWordWrap(True)
        self.table.setModel(self.root_model)
        layout_table.addWidget(self.table)
        header = self.table.header()
        header.setHighlightSections(True)
        header.setSectionsClickable(True)
        header.setSectionsMovable(True)
        self.table.setSelectionBehavior(1)  # выделяется одна строка целиком
        self.table.selectionModel().selectionChanged.connect(self.row_change)
        # выбор строки мышкой
        self.table.doubleClicked.connect(self.double_click)
        self.table.header().setDefaultSectionSize(250)

        layout_status = QtWidgets.QHBoxLayout()
        self.statusbar = QLabel()
        layout_status.addWidget(self.statusbar)
        self.time_calc = QLabel()
        layout_status.addWidget(self.time_calc)
        cd.define_object(QLabel(), layout_status, 10)
        self.statusbar_count = cd.define_object(QLabel(), layout_status)

# ограничения вывода объектов
        layout_rows = QtWidgets.QHBoxLayout()
        cd.define_object(QLabel("From row="), layout_rows)
        self.previous = cd.define_object(QPushButton(cd.icon_left, ''), layout_rows, self.previous_click)
        self.row_from = cd.define_object(QSpinBox(), layout_rows, self.change_row)
        self.row_from.setMinimum(0)
        self.row_from.setMaximum(1000000000)
        self.next = cd.define_object(QPushButton(cd.icon_right, ''), layout_rows, self.next_click)
        cd.define_object(QLabel("count rows="), layout_rows)
        self.row_count = cd.define_object(QSpinBox(), layout_rows, self.change_row, minimum=1, maximum=1000, value=1000)
        cd.define_object(QLabel("sort by="), layout_rows)
        self.field_sorting = cd.define_object(QComboBox(), layout_rows, self.change_row)
        self.field_sorting.addItem('id')
        self.field_sorting.addItem('sh_name')
        cd.define_object(QLabel('where='), layout_rows)
        self.text_where = QLineEdit()
        self.text_where.textChanged.connect(self.change_row)
        layout_rows.addWidget(self.text_where, 10)

        cd.define_object(QLabel(""), layout_rows, k=2)
        self.refresh = cd.define_object(QPushButton(cd.iconRefresh, ''), layout_rows, self.show_data)

# контейнер левой части (панель кнопок и дерево)
        layout_left = QtWidgets.QVBoxLayout()
        layout_left.addLayout(layout_table)
        panelLeft.setLayout(layout_left)
# панель паспорта
        self.widget = QWidget()
        self.page_control = pagecontrol.PageControl(self.widget, QTabWidget.North)

        self.splitter.addWidget(panelLeft)
        self.splitter.addWidget(self.page_control)

# контейнер левой части (панель кнопок и дерево)
        layout1 = QtWidgets.QVBoxLayout(parent)
        layout1.addLayout(layout_button_oper)
        layout1.addLayout(layout_rows)
        layout1.addLayout(layout_left)
        layout1.layout().addWidget(self.splitter, 10)
        layout1.addLayout(layout_status)

        # self.layout = QtWidgets.QHBoxLayout()
        # self.layout.addLayout(layout_left)
        # self.layout.addWidget(self.splitter)

        self.forms = []
        self.define_visible_button()
        self.change_language()
# запомненные параметры
    # ширина левой и правой части из settings
        w = 400
        h = 400
        try:
            if cd.settings.contains("entities_splitter_width"):
                w = int(cd.settings.value("entities_splitter_width", w))
            if cd.settings.contains("entities_splitter_height"):
                h = int(cd.settings.value("entities_splitter_height", h))
        except Exception as e:
            st = " Error: " + f"{e}"
            QtWidgets.QMessageBox.critical(None, "cd.settings", st,
                                           defaultButton=QtWidgets.QMessageBox.Ok)
        self.splitter.setSizes([w, h])


    def change_language(self):
        self.create_table_button.setText(cd.get_text('Проверить сущность', key='entities', id_text=1))
        self.delete_table_button.setText(cd.get_text('Объект сущности', key='entities', id_text=2))
        self.create_allObjectDB_button.setText(cd.get_text('Проверить все сущности', key='entities', id_text=3))
        self.makeObnov_button.setText(cd.get_text('Обновить', key='main', id_text=13))
        self.refresh.setText(cd.get_text('Обновить', key='hist', id_text=10))
        self.refresh.setToolTip(cd.get_text('Обновить', key='entities', id_text=6))
        self.create_object_button.setText(cd.get_text('Добавить объект', key='entities', id_text=4))
        self.make_header()
        self.show_count_table()

    def show_count_table(self):
        self.statusbar.setText(cd.get_text('Сущностей', id_text=7, key='form') + '= ' + str(self.qobject))
        if self.selected_text0 is not None and self.count_objects is not None:
            self.statusbar_count.setText("Last reading: from " + self.selected_text0 + ' (' + str(self.qrow) +
                                         ') find ' + str(self.count_objects))
        else:
            self.statusbar_count.setText('')

    def make_header(self):
        st_name = list()
        st_name.append(cd.get_text('Имя сущности/параметра', id_text=5, key='entities'))
        st_name.append(cd.get_text('Статус', id_text=15, key='main'))
        st_name.append(cd.get_text('Объект', id_text=16, key='main'))
        st_name.append('ID')  # 3
        st_name.append('Code')
        st_name.append(cd.get_text('Кол-во\nобъектов', id_text=21, key='main'))
        st_name.append(cd.get_text('Форма', id_text=17, key='main'))  # 6
        st_name.append(cd.get_text('Таблица', id_text=18, key='main'))
        st_name.append(cd.get_text('Представление', id_text=19, key='main'))
        st_name.append(cd.get_text('Функция записи', id_text=20, key='main'))
        st_name.append('Total Size')
        st_name.append('')
        self.root_model.setHorizontalHeaderLabels(st_name)
        # ширина колонок по содержимому
        for j in range(0, self.root_model.columnCount()):
            self.table.resizeColumnToContents(j)

    def make_obnov_click(self):
        cd.load_objects()
        for form in self.forms:  # паспорта ENTITY
            form.refresh()
        self.needMakeObnov = True
        self.make_obnov()

    def make_inform(self):
        try:
            data, result = cd.send_rest(
                'NSI.InformObjects/' + cd.schema_name)
            if result:
                js = json.loads(data)
                for mas in js:
                    code = mas["code"]
                    for i in range(0, self.root_model.rowCount()):
                        try:
                            ind = cd.get_index(self.root_model, code, 4, '')  # строка сущности
                            ind6 = ind.sibling(ind.row(), 7)
                            ind10 = ind.sibling(ind.row(), 10)

                            self.root_model.setData(ind6, cd.valueBoolean(
                                mas["table_exist"] == 1,
                                cd.get_text('Есть', id_text=22, key='main'),
                                cd.get_text('Нет', id_text=23, key='main')
                            ))
                            ind6 = ind.sibling(ind.row(), 8)
                            self.root_model.setData(ind6, cd.valueBoolean(
                                mas["view_exist"] == 1,
                                cd.get_text('Есть', id_text=22, key='main'),
                                cd.get_text('Нет', id_text=23, key='main')
                            ))
                            ind6 = ind.sibling(ind.row(), 9)
                            self.root_model.setData(ind6, cd.valueBoolean(
                                mas["function_exist"] == 1,
                                cd.get_text('Есть', id_text=22, key='main'),
                                cd.get_text('Нет', id_text=23, key='main')
                            ))
                            ind6 = ind.sibling(ind.row(), 5)
                            if mas["table_exist"] == 1:
                                self.root_model.setData(ind6, str(mas["qRecord"]))
                            else:
                                self.root_model.setData(ind6, '')
                            if mas["total_size"]:
                                self.root_model.setData(ind10, mas["total_size"])
                            else:
                                self.root_model.setData(ind10, '')
                        except Exception as err:
                            print('Entities', 'make_inform', f"{err}")
            else:
                QtWidgets.QMessageBox.critical(
                    None, cd.get_text("Чтение информации по сущностям", id_text=6, key='entities'),
                    data, defaultButton=QtWidgets.QMessageBox.Ok)
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                None, cd.get_text("Чтение информации по сущностям", id_text=6, key='entities'),
                cd.get_text('Ошибка', id_text=4, key='main') + '\n' + f"{e}" + '\n' +
                cd.get_text('По умолчанию используются', id_text=5, key='main') + ':\n\tHost Proxy=' + cd.HOST +
                '\n\tPortProxy=' + str(cd.PORT), defaultButton=QtWidgets.QMessageBox.Ok)
        # ширина колонок по содержимому
        for j in range(0, self.root_model.columnCount()):
            self.table.resizeColumnToContents(j)
        if not self.selected_text0:
            self.selected_text0 = cd.settings.value("entities_selected_text", '')
        if not self.selected_text1:
            self.selected_text1 = cd.settings.value("entities_selected_text_child", '')

    def make_obnov(self):
        admin = cd.is_user_admin()
        self.create_table_button.setVisible(admin)
        self.delete_table_button.setVisible(admin)
        self.create_allObjectDB_button.setVisible(admin)
        if self.needMakeObnov:
            if not cd.mas_json_objects or (len(cd.mas_json_objects) == 0):
                t_beg = datetime.datetime.now()
                self.time_calc.setText(cd.get_text('чтение информации ...', id_text=24, key='main'))
                self.time_calc.repaint()
                cd.load_objects()
                t_end = datetime.datetime.now()
                dest = cd.get_value_time(t_end) - cd.get_value_time(t_beg)
                self.time_calc.setText(cd.get_text("T чтения = %.3f сек", id_text=25, key='main') % dest)
            self.needMakeObnov = False
            self.exist = False
            self.root_model.setRowCount(0)
            self.table.setColumnHidden(2, True)  # колонка с объектом
            self.table.setColumnHidden(6, True)  # форма
            self.table.setColumnHidden(1, True)  # статус
            if cd.txt_error_connection == '':
                try:
                    for json_unit in cd.mas_json_objects:
                        data = typeobject.TypeObject(
                            fid=json_unit["id"],
                            fdescription=cd.value_from_array("description", json_unit),
                            fsh_name=cd.value_from_array("name", json_unit),
                            fcode=cd.value_from_array("code", json_unit),
                            fsort=cd.value_from_array("ordering_index", json_unit),
                            fparent_id=cd.value_from_array("parent_id", json_unit),
                            fisbaseclass=cd.value_from_array("is_base_class", json_unit))
                        node9 = QStandardItem()
                        node9.setTextAlignment(QtCore.Qt.AlignCenter)
                        node10 = QStandardItem()
                        node10.setTextAlignment(QtCore.Qt.AlignRight)
                        row = [
                            QStandardItem(cd.translateFromBase(json_unit["name"])),
                            QStandardItem(""),
                            QStandardItem(""),
                            QStandardItem(str(json_unit["id"])),
                            QStandardItem(str(json_unit["code"])),
                            QStandardItem(),
                            QStandardItem(),
                            QStandardItem(),
                            QStandardItem(),
                            node9,
                            node10,
                            QStandardItem("")
                        ]
                        # только на чтение
                        for c in row:
                            c.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

                        self.root_model.appendRow(row)
                        row = self.root_model.rowCount() - 1

                        ind = self.root_model.index(row, 2)
                        self.root_model.setData(ind, data)

                    # прочитать информацию по таблицам, представлениям, функциям
                    self.make_inform()
                    # позиционирование на объект для раскрытия сущности
                    #     ind = cd.get_index(self.root_model, self.selected_text0, 0, self.selected_text1)
                    #     ind9 = ind.sibling(ind.row(), 9)
                    #     if self.root_model.data(ind9):
                    #         self.insert_objects(ind)  # раскрытие сущности (вывод всех объектов)
                    # позиционирование возможно и на объект
                    ind = cd.get_index(self.root_model, self.selected_text0, 0, self.selected_text1)
                    self.table.setCurrentIndex(ind)  # сделать строку выбранной
                    self.exist_izm = 0
                    self.exist = True
                    self.selection_change(ind)
                    # ind = self.table.currentIndex()
                    # self.table.expand(ind)  # раскрыть узел дерева
                    # ширина колонок по содержимому
                    for j in range(0, self.root_model.columnCount()):
                        self.table.resizeColumnToContents(j)
                except Exception as err:
                    print('Entities', 'make_obnov', f"{err}")
        if cd.mas_json_objects:
            self.qobject = len(cd.mas_json_objects)
        self.statusbar.setText(cd.get_text('Сущностей', id_text=7, key='form') + '= ' + str(self.qobject))
        self.define_visible_button()

    def double_click(self):
        self.row_change(None, None)

    def define_visible_button(self):
        err_connect = cd.txt_error_connection != ''
        self.makeObnov_button.setEnabled(not err_connect)
        self.create_object_button.setEnabled(not err_connect)
        # self.create_table_button.setEnabled(not err_connect)
        # self.delete_table_button.setEnabled(not err_connect)
        # self.create_allObjectDB_button.setEnabled(not err_connect)
        try:
            if self.ind0 is not None:
                ind = self.ind0.sibling(self.ind0.row(), 6)
                self.exist_table = self.root_model.data(ind)
            if self.exist_table == '':
                self.create_table_button.setIcon(cd.iconCreate)
                self.create_table_button.setText(cd.get_text('Создать сущность', id_text=7, key='entities'))
            else:
                self.create_table_button.setIcon(cd.iconSave)
                self.create_table_button.setText(cd.get_text('Проверить сущность', key='entities', id_text=1))
        except Exception as err:
            print('Entities', 'define_visible_button', f"{err}")

    def row_change(self, new, old):
        try:
            self.selection_change(self.table.selectionModel().currentIndex())
        except Exception as err:
            print('Entities', 'row_change', f"{err}")

    def selection_change(self, modal_index):
        if self.exist:
            if self.root_model.data(modal_index.parent()):  # второй уровень
                ind = modal_index.parent()  # индекс родителя
                self.arow = modal_index.row()  # индекс объекта в сущности
                self.level = 1
            else:
                self.level = 0
                ind = modal_index
            item = self.root_model.item(ind.row(), 5)
            ind = self.root_model.indexFromItem(item)
            self.qrow = int(self.root_model.data(ind))  # количество строк
            self.row_count.setMaximum(self.qrow)
            self.row_from.setMaximum(self.qrow - 1)
            if self.qrow < 100:
                self.row_count.setValue(self.qrow)
            # print(self.root_model.data(ind))
            if self.root_model.data(modal_index.parent()):
                self.ind1 = modal_index
                ind = modal_index.parent()  # индекс родителя
                item = self.root_model.item(ind.row(), 0)  # нулевая колонка родителя
                self.ind0 = self.root_model.indexFromItem(item)  # индекс нулевой колонки родителя
                self.selected_text0 = self.root_model.data(self.ind0)  # нулевой уровень
                self.selected_ind = modal_index.sibling(modal_index.row(), 0)
                self.selected_text1 = self.root_model.data(self.selected_ind)
            else:
                self.ind0 = modal_index.sibling(modal_index.row(), 0)
                if self.selected_text0 != self.root_model.data(self.ind0):
                    self.row_count.setValue(min(100, self.row_count.maximum()))
                    self.row_from.setValue(0)
                    self.text_where.setText('')
                self.selected_text0 = self.root_model.data(self.ind0)
                self.selected_text1 = ''
                ind = modal_index.sibling(modal_index.row(), 5)
                if self.root_model.data(ind) and (cd.txt_error_connection == '') and self.qrow > 0:
                    self.insert_objects(modal_index)
            ind2 = self.root_model.sibling(self.ind0.row(), 4, self.ind0)
            self.object_code = self.root_model.data(ind2)
            self.define_visible_button()
            if self.root_model.data(modal_index.parent()):
                self.create_passport()


    def isTop(self):
        return self.arow == 0

    def isBottom(self):
        return self.arow == self.qrow - 1

    def down_click(self):
        # перейти на следующий объект
        self.selected_ind = self.selected_ind.sibling(self.arow+1, 0)
        self.selection_change(self.selected_ind)
        self.table.setCurrentIndex(self.selected_ind)
        self.create_passport()

    def up_click(self):
        # перейти на предыдущий объект
        self.selected_ind = self.selected_ind.sibling(self.arow-1, 0)
        self.selection_change(self.selected_ind)
        self.table.setCurrentIndex(self.selected_ind)
        self.create_passport()

    def show_data(self):
        if self.exist:
            item = self.root_model.item(self.ind0.row(), 0)
            item.setRowCount(0)
            self.insert_objects(self.ind0)
            self.refresh.setEnabled(False)

    def insert_objects(self, QModalIndex):
        item = self.root_model.item(QModalIndex.row(), 0)  # нулевая колонка родителя
        if not item.hasChildren():
            # надо раскрыть сущность по объектам
            ind2 = self.root_model.sibling(QModalIndex.row(), 4, QModalIndex)
            object_code = self.root_model.data(ind2)
            st = 'v1/content/' + cd.schema_name + '/' + object_code + '?row_from=' + str(self.row_from.value()) + \
                 '&row_count=' + str(self.row_count.value()) + '&column_name=' + self.field_sorting.currentText()
            if self.text_where.text() != '':
                st = st + '&where=' + self.text_where.text()
            ans, result = cd.send_rest(st)
            if result:
                try:
                    self.count_objects = 0
                    js = json.loads(ans)
                    for mas_json in js:
                        node = QStandardItem()
                        if "sh_name" in mas_json:
                            node.setText(cd.translateFromBase(mas_json["sh_name"]))
                        else:
                            node.setText(str(mas_json["id"]))
                        node4 = QStandardItem()
                        if "code" in mas_json:
                            node4.setText(cd.translateFromBase(str(mas_json["code"])))
                        row = [
                            node,
                            QStandardItem(""),
                            QStandardItem(""),
                            QStandardItem(str(mas_json["id"])),
                            node4,
                            QStandardItem()
                        ]
                        # только на чтение
                        for c in row:
                            c.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                        item.appendRow(row)
                        self.count_objects += 1
                    self.refresh.setEnabled(False)
                except Exception as err:
                    print('Entities', 'insert_objects', f"{err}")
            self.table.expand(QModalIndex.sibling(QModalIndex.row(), 0))
            self.show_count_table()

    def create_all_click(self):
        ans, result = cd.send_rest(
            'NSI.Update_MDM/' + cd.schema_name + '/' + cd.info_code, 'PUT')
        if result:
            self.needMakeObnov = True
            self.close_all_forms()
            self.make_obnov()

    def make_passport(self, obj_id):
        QApplication.setOverrideCursor(Qt.BusyCursor)  # курсор ожидания
        try:
            title = self.object_code + ': ' + obj_id
            exist = False
            for i in range(self.page_control.tabs.count()):
                if self.page_control.tabs.tabText(i) == title:
                    exist = True
                    self.page_control.setCurrentIndex(i)
                    break

            if not exist:
                tab = self.page_control.addTab(title)
                form = passport_entity.PassportEntity(tab, self)
                self.forms.append(form)
                form.load_params(self.object_code)
                form.show_data(obj_id)
                self.page_control.setCurrentIndex(self.page_control.tabs.count() - 1)
        except Exception as err:
            print('Entities', 'make_passport', obj_id, f"{err}")
        QApplication.restoreOverrideCursor()  # восстановление курсора

    def create_passport(self):
        self.make_passport(self.root_model.data(self.ind1.sibling(self.ind1.row(), 3)))

    def create_object(self):
        # создание нового объекта
        self.make_passport('0')

    def create_table_click(self):
        data, result = cd.send_rest(
            'NSI.UpdateTable/' + cd.schema_name + '/' + cd.info_code + '/' + self.object_code, 'PUT')
        if result:
            try:
                ind = self.ind0.sibling(self.ind0.row(), 5)
                form = self.root_model.data(ind)
                form.close()
                del form
                self.root_model.setData(ind, None)
            except Exception as err:
                print('Entities', 'create_table_click', f"{err}")
            self.define_visible_button()
            self.make_inform()

    def delete_table_click(self):
        object_code = self.root_model.data(self.root_model.sibling(self.ind0.row(), 4, self.ind0))
        q = cd.make_question(
            self,
            cd.get_text('Удалить таблицу для сущности', id_text=8, key='entities') + ' [' + object_code + '] ?',
            cd.get_text('Удаление таблицы сущности', id_text=9, key='entities'),
            cd.get_text('Удаление таблицы базы данных и всех связанных с ней объектов '
                        'без удаления класса объектов из метаданных', id_text=10, key='entities'))
        if q:
            ans, result = cd.send_rest('NSI.DeleteTable/' + cd.schema_name + '/' + object_code, 'DELETE')
            if cd.show_error_answer(ans, 'NSI.DeleteTable. ' + cd.get_text('Ошибка', id_text=4, key='main'),
                                    onlyok=True):
                ind = self.ind0.sibling(self.ind0.row(), 6)
                self.root_model.setData(ind, '')
                ind = self.ind0.sibling(self.ind0.row(), 7)
                self.root_model.setData(ind, '')
                ind = self.ind0.sibling(self.ind0.row(), 8)
                self.root_model.setData(ind, '')
                self.make_inform()
                self.make_obnov_click()
            self.define_visible_button()
            cd.send_evt(cd.evt_delete_table_entity, self.form_parent)

    def close_all_forms(self):
        i = self.page_control.tabs.count() - 1
        while i >= 0:
            self.page_control.tabs.removeTab(i)
            i -= 1
        i = len(self.forms) - 1
        while i >= 0:
            form = self.forms[i]
            self.forms.pop(i)
            del form
            i -= 1

    def closeEvent(self, evt):
        self.close_all_forms()
        if self.selected_text0:
            cd.settings.setValue("entities_selected_text", self.selected_text0)
        if self.selected_text1:
            cd.settings.setValue("entities_selected_text_child", self.selected_text1)
        spis = self.splitter.sizes()
        cd.settings.setValue("entities_splitter_width", spis[0])
        cd.settings.setValue("entities_splitter_height", spis[1])
        QApplication.quit()

    def customEvent(self, evt):
        if evt.type() == cd.StatusOperation.idType:  # изменение состояния соединения PROXY
            n = evt.get_data()
            if type(n) == dict:
                if "command" in n:
                    if n["command"] == "close_page":
                        title = n["object_code"] + ': ' + str(n["obj_id"])
                        for i in range(self.page_control.tabs.count()):
                            if self.page_control.tabs.tabText(i) == title:
                                self.page_control.tabs.removeTab(i)
                                break
                        for i in range(len(self.forms)):
                            form = self.forms[i]
                            if form.object_code == n["object_code"] and form.obj_id == n['obj_id']:
                                self.forms.pop(i)
                                del form
                                break
                    elif n["command"] == "new_object":
                        title_current = n["object_code"] + ': 0'
                        title = n["object_code"] + ': ' + str(n["obj_id"])
                        for i in range(self.page_control.tabs.count()):
                            if self.page_control.tabs.tabText(i) == title_current:
                                self.page_control.tabs.setTabText(i, title)
                                break
            elif n == cd.evt_change_language:
                self.change_language()
                for form in self.forms:
                    cd.send_evt(n, form)

    def next_click(self):
        if self.exist:
            self.row_from.setValue(self.row_from.value() + self.row_count.value())
            self.change_row()

    def previous_click(self):
        if self.exist:
            QSpinBox(self.row_from).setValue(QSpinBox(self.row_from).value() - QSpinBox(self.row_count).value())
            self.change_row()

    def change_row(self):
        if self.exist:
            self.refresh.setEnabled(True)
