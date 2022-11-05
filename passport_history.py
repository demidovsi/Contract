"""
Исторические данные в паспорте объекта сущности
"""
from PyQt5.QtGui import *
from PyQt5 import (QtWidgets, QtCore)
from PyQt5.QtWidgets import (QWidget, QLabel, QDateTimeEdit, QDoubleSpinBox, QComboBox, QSpinBox, QCheckBox,
                             QMessageBox, QFrame, QDateEdit, QApplication, QLineEdit)
from PyQt5.QtCore import Qt
import common_data as cd
import json
import time
import datetime
from matplotlib import pyplot as plt
import numpy as np


class PassportHistory(QWidget):
    exist = False
    selected_row = 0
    form_parent = None
    fig = None
    caption = ''
    typeobj_code = ''
    code = ''
    value_code = ''
    value_last = None
    time_last = None
    data = None
    equip = []  # список устройств КСВД c параметрами
    read_discret = 1
    read_eq_id = ''
    read_eq_name = ''
    read_par_id = ''
    read_type_his = ''
    xf = 50
    yf = 100
    dxf = 600
    dyf = 500
    x = []
    y = []
    tt = None
    cid = None
    ymin = None
    ymax = None
    count_row = None
    answer = None
    yes_dict = False
    yes_str = False

    def __init__(self, parent, form_parent):
        super(QWidget, self).__init__()
        self.form_parent = form_parent
        dt = time.localtime()
        # контейнер для таблицы
        layout_table = QtWidgets.QVBoxLayout()

        layout_param = QtWidgets.QHBoxLayout()
        self.type_his_label = QLabel('')
        layout_param.addWidget(self.type_his_label)
        self.type_his = QComboBox()
        self.type_his.setMaxVisibleItems(20)
        self.type_his.currentIndexChanged.connect(self.type_his_change)
        layout_param.addWidget(self.type_his, 2)

        self.equipment_label = QLabel('')
        layout_param.addWidget(self.equipment_label)
        self.equipments = QComboBox()
        self.equipments.setMaxVisibleItems(20)
        self.equipments.currentIndexChanged.connect(self.equipments_change)
        layout_param.addWidget(self.equipments, 2)
        self.parameter_label = QLabel('')
        layout_param.addWidget(self.parameter_label)
        self.parameters = QComboBox()
        self.parameters.setMaxVisibleItems(20)
        layout_param.addWidget(self.parameters, 3)
        self.parameters.currentIndexChanged.connect(self.parameters_change)

        self.discret_label = QLabel('')
        layout_param.addWidget(self.discret_label)
        self.discret = QSpinBox()
        self.discret.setGroupSeparatorShown(True)
        self.discret.setMaximum(86400)
        self.discret.setMinimum(1)
        self.discret.valueChanged.connect(self.discret_change)
        layout_param.addWidget(self.discret, 2)

        layout_table.addLayout(layout_param)

        layout_param1 = QtWidgets.QHBoxLayout()
        self.last_value = QLabel('последнее значение=')
        layout_param1.addWidget(self.last_value)
        layout_table.addLayout(layout_param1)

        layout_param2 = QtWidgets.QHBoxLayout()
        self.label_what_show = QLabel('что выводить=')
        layout_param2.addWidget(self.label_what_show)
        self.what_show = QComboBox()
        self.what_show.currentIndexChanged.connect(self.what_show_change)
        layout_param2.addWidget(self.what_show, 10)
        layout_table.addLayout(layout_param2)

        layout1 = QtWidgets.QHBoxLayout()
        self.prev_button = QtWidgets.QPushButton('')
        self.prev_button.clicked.connect(self.prev_button_click)
        layout1.addWidget(self.prev_button)
        self.dt_beg_label = QLabel('')
        layout1.addWidget(self.dt_beg_label)
        self.dt_beg = QDateTimeEdit()
        self.dt_beg.setDisplayFormat('dd.MM.yyyy hh.mm.ss')
        self.dt_beg.setDate(QtCore.QDate(dt.tm_year, dt.tm_mon, time.gmtime().tm_mday))
        layout1.addWidget(self.dt_beg)
        self.makeObnov_button = QtWidgets.QPushButton(cd.iconRefresh, '')
        self.makeObnov_button.clicked.connect(self.make_obnov_click)
        layout1.addWidget(self.makeObnov_button)
        self.to_day = QtWidgets.QPushButton('')
        self.to_day.clicked.connect(self.to_day_click)
        layout1.addWidget(self.to_day)
        # layout_table.addLayout(layout1)

        layout2 = QtWidgets.QHBoxLayout()
        # self.check_combo_label = QLabel('Graph=')
        # layout2.addWidget(self.check_combo_label)
        # self.check_combo = QComboBox(self)
        # layout2.addWidget(self.check_combo)

        self.show_graf_box = QCheckBox('')
        self.show_graf_box.stateChanged.connect(self.show_graf_changed)
        layout2.addWidget(self.show_graf_box)
        self.dt_end_label = QLabel('')
        layout2.addWidget(self.dt_end_label)
        self.dt_end = QDateTimeEdit()
        self.dt_end.setDisplayFormat('dd.MM.yyyy hh.mm.ss')
        t = self.dt_beg.date().addDays(1)
        self.dt_end.setDate(t)
        layout2.addWidget(self.dt_end)
        self.next_button = QtWidgets.QPushButton('')
        self.next_button.clicked.connect(self.next_button_click)
        layout2.addWidget(self.next_button)
        self.yesterday = QtWidgets.QPushButton('')
        self.yesterday.clicked.connect(self.yesterday_click)
        layout2.addWidget(self.yesterday)
        # layout_table.addLayout(layout2)
        # таблица
        self.root_model = QStandardItemModel()
        self.table = QtWidgets.QTreeView()
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
        header.setSectionsMovable(False)
        self.table.setSelectionBehavior(1)  # выделяется одна строка целиком
        self.table.selectionModel().selectionChanged.connect(self.row_change)
        # выбор строки мышкой
        # self.table.pressed.connect(self.selection_change)
        # self.table.activated.connect(self.selection_change)
        # self.table.clicked.connect(self.selection_change)
        self.table.doubleClicked.connect(self.table_double_click)

        # self.root_model.setHorizontalHeaderLabels(['Value', 'Time'])
        self.table.header().setDefaultSectionSize(120)

        layout3 = QtWidgets.QHBoxLayout()
        self.statusbar = QLabel()
        self.maxmin = QLabel()
        self.maxmin.setFont(self.font())
        self.maxmin.setStyleSheet('color: blue')
        layout3.addWidget(self.statusbar)
        layout3.addWidget(self.maxmin)
        # блок для ввода данного
        layout_frame1 = QtWidgets.QHBoxLayout()
        frame = QFrame()
        frame.setFrameShape(1)  # box
        layout_frame1.addWidget(frame)
        layout4 = QtWidgets.QHBoxLayout()
        self.dt_label = QLabel('')
        layout4.addWidget(self.dt_label)
        self.dt_data = QDateTimeEdit()
        self.dt_data.setDisplayFormat('dd.MM.yyyy hh.mm.ss')
        self.dt_data.setDate(QtCore.QDate(dt.tm_year, dt.tm_mon, dt.tm_mday))
        self.dt_data.setTime(QtCore.QTime(dt.tm_hour, dt.tm_min, dt.tm_sec))
        layout4.addWidget(self.dt_data)
        self.value_label = QLabel('Value=')
        layout4.addWidget(self.value_label)
        self.value = QDoubleSpinBox()
        self.value.setDecimals(3)
        self.value.setMaximum(1000000000)
        self.value.setMinimum(-1000000000)
        layout4.addWidget(self.value)
        self.value_text = QLineEdit()
        layout4.addWidget(self.value_text)

        self.write_button = QtWidgets.QPushButton(cd.iconSave, '')
        self.write_button.clicked.connect(self.write_click)
        layout4.addWidget(self.write_button)
        frame.setLayout(layout4)
        # блок для копирования
        layout_frame = QtWidgets.QHBoxLayout()
        frame = QFrame()
        frame.setFrameShape(1)  # box
        layout_frame.addWidget(frame)
        layout5 = QtWidgets.QHBoxLayout()
        self.make_copy = QtWidgets.QPushButton('')
        self.make_copy.clicked.connect(self.make_copy_click)
        layout5.addWidget(self.make_copy)
        self.label_source = QLabel('')
        layout5.addWidget(self.label_source)
        self.dt_source = QDateEdit()
        self.dt_source.setDisplayFormat('dd.MM.yyyy')
        t = datetime.date.today() + datetime.timedelta(days=-1)
        self.dt_source.setDate(QtCore.QDate(t.year, t.month, t.day))
        layout5.addWidget(self.dt_source, 2)
        self.label_target = QLabel('')
        layout5.addWidget(self.label_target)
        self.dt_target = QDateEdit()
        self.dt_target.setDisplayFormat('dd.MM.yyyy')
        t = datetime.date.today()
        self.dt_target.setDate(QtCore.QDate(t.year, t.month, t.day))
        layout5.addWidget(self.dt_target, 2)
        frame.setLayout(layout5)

        layout_table.addLayout(layout3)
        layout_table.addLayout(layout1)
        layout_table.addLayout(layout2)
        layout_table.addLayout(layout_frame1)
        layout_table.addLayout(layout_frame)

        parent.setLayout(layout_table)
        self.change_language()

    def change_language(self):
        self.type_his_label.setText(cd.get_text('Тип', id_text=1, key='enum') + '=')
        self.discret_label.setText(cd.get_text('Цикл', id_text=42, key='main') + '=')
        self.equipment_label.setText(cd.get_text('Устройство', id_text=3, key='hist') + '=')
        self.parameter_label.setText(cd.get_text('Parameter', id_text=4, key='hist') + '=')
        self.prev_button.setText('-1 ' + cd.get_text('day', id_text=5, key='hist'))
        self.next_button.setText('+1 ' + cd.get_text('day', id_text=5, key='hist'))
        self.dt_beg_label.setText(cd.get_text('Begin', id_text=6, key='hist') + '=')
        self.dt_end_label.setText(cd.get_text('End', id_text=7, key='hist') + '=')
        self.to_day.setText(cd.get_text('Today', id_text=8, key='hist'))
        self.yesterday.setText(cd.get_text('Yesterday', id_text=9, key='hist'))
        self.makeObnov_button.setText(cd.get_text('Read', id_text=10, key='hist'))
        self.show_graf_box.setText(cd.get_text('Show', id_text=11, key='hist'))
        self.dt_label.setText(cd.get_text('Time', id_text=2, key='form') + '=')
        self.write_button.setText(cd.get_text('Save', id_text=29, key='main'))
        self.make_copy.setText(cd.get_text('Copy', id_text=12, key='hist'))
        self.label_source.setText(cd.get_text('Source', id_text=13, key='hist') + '=')
        self.label_target.setText(cd.get_text('Target', id_text=14, key='hist') + '=')
        self.label_what_show.setText(cd.get_text('Что выводить', id_text=18, key='hist') + '=')
        if self.count_row is not None:
            self.statusbar.setText(
                cd.get_text('Строк', id_text=8, key='import') + '= ' + cd.str1000(self.count_row))
        self.show_last_value()

    def time_for_sql(self, dt, convert=True):
        if convert:
            dt = dt.toPyDateTime()
        return str(dt.year) + '-' + str(dt.month) + '-' + str(dt.day) + ' ' + \
               str(dt.hour) + ':' + str(dt.minute) + ':' + str(dt.second)

    def equipments_change(self, newtext=''):
        if self.exist:
            self.define_parameter()
            self.form_parent.is_need_to_save()

    def parameters_change(self, newtext=''):
        if self.exist:
            self.form_parent.is_need_to_save()

    def discret_change(self, newtext=''):
        if self.exist:
            self.form_parent.is_need_to_save()

    def type_his_change(self, newtext=''):
        if self.exist:
            meteo = True
            st = self.type_his.currentText()
            if (st == '') or (st == 'data'):
                meteo = False
                self.equipments.setCurrentText(self.read_eq_name)
                self.parameters.setCurrentText(self.read_par_id)
            self.equipment_label.setVisible(not meteo)
            self.equipments.setVisible(not meteo)
            self.parameter_label.setVisible(not meteo)
            self.parameters.setVisible(not meteo)
            self.form_parent.is_need_to_save()
            self.last_value.setVisible(not meteo)
            self.label_what_show.setVisible(meteo)
            self.what_show.setVisible(meteo)

    def define_parameter(self):
        st_before = self.parameters.currentText()
        self.parameters.clear()
        self.parameters.addItem('')
        self.parameters.addItem('Frequency')
        eq_name = self.equipments.currentText()
        try:
            for j in range(0, len(self.equip)):
                st = self.equip[j]["name"]
                if st == eq_name:
                    params = self.equip[j]['parameters_mapping']
                    for i in range(0, len(params)):
                        st = params[i]["parameter_id"]
                        self.parameters.addItem(st)
                    params = self.equip[j]["data_quality_options"]['computable_parameters']
                    for i in range(0, len(params)):
                        st = params[i]["id"]
                        self.parameters.addItem(st)
                    self.parameters.setCurrentIndex(-1)
                    self.parameters.setCurrentText(st_before)
                    if self.parameters.currentIndex() == -1:
                        self.parameters.setCurrentText(self.read_par_id)
                    break
        except:
            pass

    def get_equipment_id(self):
        result = ''
        eq_name = self.equipments.currentText()
        try:
            for j in range(0, len(self.equip)):
                st = self.equip[j]["name"]
                if st == eq_name:
                    result = self.equip[j]["id"]
        except:
            pass
        return result

    def get_parameter_id(self):
        return self.parameters.currentText()

    def show_data(self):
        self.write_button.setEnabled(self.value_code is not None and self.value_code != 'None')
        self.refresh()
        self.exist = False
        QApplication.setOverrideCursor(Qt.BusyCursor)  # курсор ожидания
        self.type_his.clear()
        data, result = cd.send_rest('v1/enums?enum_name=type_his')
        if result:
            jsLabel = json.loads(data)
            mas_label = jsLabel['labels']
            for mas in mas_label:
                st = mas["label"]
                self.type_his.addItem(st)

        self.read_eq_name = ''
        self.read_discret = 3600
        self.read_eq_id = ''
        self.read_par_id = ''
        self.read_type_his = ''
        self.equipments.clear()
        self.parameters.clear()
        self.discret.setValue(3600)
        caption = 'History_' + self.data.sh_name
        if cd.settings.contains(caption + '_xf'):
            self.xf = int(cd.settings.value(caption + '_xf'))
        if cd.settings.contains(caption + '_yf'):
            self.yf = int(cd.settings.value(caption + '_yf'))
        if cd.settings.contains(caption + '_dxf'):
            self.dxf = int(cd.settings.value(caption + '_dxf'))
        if cd.settings.contains(caption + '_dyf'):
            self.dyf = int(cd.settings.value(caption + '_dyf'))
        ans, result = cd.send_rest("ksvd/equipments", show_error=False)
        if result:
            self.equipments.addItem('')
            try:
                self.equip = json.loads(ans)
                for j in range(0, len(self.equip)):
                    st = self.equip[j]["name"]
                    self.equipments.addItem(st)
            except:
                pass
        # else:
        #     QtWidgets.QMessageBox.critical(self, cd.get_text("Чтение списка объектов", id_text=3, key='relations'),
        #         cd.get_text('Ошибка', id_text=4, key='main') + ' \n' + ans, defaultButton=QtWidgets.QMessageBox.Ok)
        self.equipments.setCurrentIndex(-1)
        if self.value_code != 'None':
            ans, result = cd.send_rest(
                'v1/MDM/his/link/' + cd.schema_name + '/' + self.typeobj_code + '?param_code=' + self.code +
                '&obj_id=' + str(self.value_code))
            if result and ('error' not in ans):
                try:
                    js = json.loads(ans)[0]  # всегда возвращается массив (если без ошибки)
                    self.read_discret = js["discret"]
                    self.read_eq_id = js["equipment_id"]
                    self.read_par_id = js["parameter_id"]
                    type_his = js["type_his"]
                    self.read_type_his = type_his
                    self.type_his.setCurrentText(type_his)

                    self.discret.setValue(js["discret"])
                    eq_id = js["equipment_id"]
                    for j in range(0, len(self.equip)):
                        st = self.equip[j]["id"]
                        if st == eq_id:
                            self.read_eq_name = self.equip[j]["name"]
                            self.equipments.setCurrentText(self.equip[j]["name"])
                            self.define_parameter()
                            self.parameters.setCurrentText(self.read_par_id)
                            break
                except:
                    pass
        if self.data.category == 'fInteger':
            self.value.setDecimals(0)
        self.exist = True
        self.type_his_change()
        self.show_inform()
        QApplication.restoreOverrideCursor()  # восстановление курсора

    def is_bar(self):
        return 86400 // self.discret.value() <= 288

    def add_value_column(self, js, name_val):
        if name_val in js:
            return QStandardItem('  ' + str(js[name_val]))
        else:
            return QStandardItem('')

    def show_inform(self):
        self.exist = False
        self.root_model.setRowCount(0)  # сбросить таблицу
        self.root_model.setColumnCount(0)  # сбросить колонки
        stname = []
        stname.append('время')
        if self.type_his.currentText() == 'data':
            stname.append('value')
        else:
            stname.append('temp\nтемп.')
            stname.append('feels_like\nощущается')
            stname.append("humidity\nвлажность")
            stname.append("pressure\nдавление")
            stname.append("wind_speed\nскорость ветра")
            stname.append("wind_deg\n угол ветра")
            stname.append("wind_gust\nпорыв ветра")
            stname.append("dew_point\nточка росы")
            stname.append("uvi\nсолн. актив")
            stname.append("clouds\nоблачность%")
            stname.append("visibility\nвидимость")
            stname.append("время сайта")
            index = self.what_show.currentIndex()
            self.what_show.clear()
            self.what_show.addItem('temp (темп.)')
            self.what_show.addItem('feels_like (ощущается)')
            self.what_show.addItem("humidity (влажность)")
            self.what_show.addItem("pressure (давление)")
            self.what_show.addItem("wind_speed (скорость ветра)")
            self.what_show.addItem("wind_deg (угол ветра)")
            self.what_show.addItem("wind_gust (порыв ветра)")
            self.what_show.addItem("dew_point (точка росы)")
            self.what_show.addItem("uvi (солн. актив)")
            self.what_show.addItem("clouds (облачность%)")
            self.what_show.addItem("visibility (видимость)")
            if index == -1:
                index = 0
            self.what_show.setCurrentIndex(index)
        self.root_model.setHorizontalHeaderLabels(stname)

        dt_beg = self.time_for_sql(cd.local_utc(self.dt_beg.dateTime().toPyDateTime()), False)
        dt_end = self.time_for_sql(cd.local_utc(self.dt_end.dateTime().toPyDateTime()), False)
        if self.value_code is not None and self.value_code != 'None':
            ans = 'v1/MDM/his/' + cd.schema_name + '/' + self.typeobj_code + '/' + self.code  + \
                  '/' + str(self.value_code) + '?dt_beg=' + dt_beg + '&dt_end=' + dt_end
            self.answer, result = cd.send_rest(ans)
            if result and 'error_sql' not in self.answer:
                self.x = []
                self.y = []
                isbar = self.is_bar()
                imax = 86400 // self.discret.value()
                ishag = self.discret.value() / 3600
                for i in range(0, imax):
                    self.x.append(str(ishag * i))
                    if isbar:
                        self.y.append(0)  # будем выводить bar
                    else:
                        self.y.append(None)  # будем выводить plot
                try:
                    js = json.loads(self.answer)
                    mas_json = js
                    self.ymax = None
                    self.ymin = None
                    av = 0
                    qav = 0
                    self.value_text.setEnabled(self.data.category == 'fString')
                    self.value.setEnabled(not self.value_text.isEnabled())
                    # self.show_graf_box.setEnabled(not self.value_text.isEnabled())
                    for j in range(0, len(mas_json)):  # точки с данными
                        self.yes_str = False
                        self.yes_dict = False
                        if "value" in mas_json[j]:
                            t = mas_json[j]["dt"]
                            t, v = cd.getpole(t, '.')  # отсекли возможные микросекунды
                            self.tt = cd.utc_local(datetime.datetime.strptime(t, '%Y-%m-%d %H:%M:%S'))
                            v = self.tt.second + self.tt.minute * 60 + self.tt.hour * 3600
                            val = mas_json[j]["value"]
                            if type(val) == dict:
                                val = val['temp']
                                self.yes_dict = True
                            else:
                                if type(val) == str:
                                    self.yes_str = True
                                    value = val
                            if not self.yes_str:
                                if not self.ymin:
                                    self.ymin = val
                                    self.ymax = val
                                else:
                                    self.ymin = min(self.ymin, val)
                                    self.ymax = max(self.ymax, val)
                                av = av + val
                                qav = qav + 1
                                self.y[v // self.discret.value()] = val
                                self.x[v // self.discret.value()] = str(int(v // self.discret.value()))
                                value = str(val)
                        else :
                            value = ''
                        row = [
                            QStandardItem(datetime.datetime.strftime(self.tt, ' %d-%m-%Y %H:%M:%S ')),
                            QStandardItem(value)
                        ]
                        if self.yes_dict:
                            row.append(self.add_value_column(mas_json[j]["value"], 'feels_like'))
                            row.append(self.add_value_column(mas_json[j]["value"], 'humidity'))
                            row.append(self.add_value_column(mas_json[j]["value"], 'pressure'))
                            row.append(self.add_value_column(mas_json[j]["value"], 'wind_speed'))
                            row.append(self.add_value_column(mas_json[j]["value"], 'wind_deg'))
                            row.append(self.add_value_column(mas_json[j]["value"], 'wind_gust'))
                            row.append(self.add_value_column(mas_json[j]["value"], 'dew_point'))
                            row.append(self.add_value_column(mas_json[j]["value"], 'uvi'))
                            row.append(self.add_value_column(mas_json[j]["value"], 'clouds'))
                            row.append(self.add_value_column(mas_json[j]["value"], 'visibility'))
                            row.append(QStandardItem('  ' + time.ctime(mas_json[j]["value"]["dt"])))
                        # # только на чтение
                        for c in row:
                            c.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                        self.root_model.appendRow(row)
                        # ширина колонок по содержимому
                    for k in range(0, self.root_model.columnCount()):
                        self.table.resizeColumnToContents(k)
                    self.count_row = len(mas_json)
                    self.statusbar.setText(
                        cd.get_text('Строк', id_text=8, key='import') + '= ' + cd.str1000(self.count_row))
                    if qav != 0:
                        av = av / qav
                    if self.what_show.isVisible():
                        st = self.what_show.currentText() + ': '
                    else:
                        st = ''
                    if self.ymin:
                        self.maxmin.setText(
                            st + "min= %.3f" % self.ymin + '; max= %.3f' % self.ymax + '; av = %.3f' % av)
                    else:
                        self.maxmin.setText('')
                except Exception as e:
                    QtWidgets.QMessageBox.critical(
                        self, cd.get_text("Чтение списка объектов", id_text=3, key='relations'),
                        cd.get_text('Ошибка', id_text=4, key='main') + ' \n' + f"{e}",
                        defaultButton=QtWidgets.QMessageBox.Ok)
            else:
                QtWidgets.QMessageBox.critical(
                    self, cd.get_text("Чтение списка объектов", id_text=3, key='relations'),
                    cd.get_text('Ошибка', id_text=4, key='main') + ' \n' + ans,
                    defaultButton=QtWidgets.QMessageBox.Ok)
            if self.ymin:
                if self.ymin > 0:
                    self.ymin = self.ymin * 0.99
                else:
                    self.ymin = self.ymin * 1.01
                if self.ymax > 0:
                    self.ymax = self.ymax * 1.01
                else:
                    self.ymax = self.ymax * 0.99
            self.show_graf()
        self.exist = True
        ind = self.root_model.index(self.selected_row, 0)
        self.table.setCurrentIndex(ind)  # выделить новую строку

        self.value_last = None
        if self.last_value.isVisible() and self.value_code is not None and self.value_code != 'None':
            ans = 'v1/MDM/his/' + cd.schema_name + '/' + self.typeobj_code + '/' + self.code + \
                  '/' + str(self.value_code) + "?last=1"
            ans, result = cd.send_rest(ans)
            if result:
                ans = json.loads(ans)
                if len(ans) > 0:
                    ans = ans[0]
                    self.value_last = ans['value']
                    t = ans["dt"]
                    t, v = cd.getpole(t, '.')  # отсекли возможные микросекунды
                    tt = cd.utc_local(datetime.datetime.strptime(t, '%Y-%m-%d %H:%M:%S'))

                    self.time_last = str(tt.year) + '.' + str(tt.month) + '.' + str(tt.day) + ' ' + \
                                     str(tt.hour) + ':' + str(tt.minute) + ':' + str(tt.second)
        self.show_last_value()

    def show_last_value(self):
        if self.value_last is not None:
            self.last_value.setText(cd.get_text('Последнее значение', id_text=17, key='hist') + '= ' +
                                    str(self.value_last) + ' (' + self.time_last + ')')
        else:
            self.last_value.setText(cd.get_text('Последнее значение', id_text=17, key='hist') + '= ')

    def show_graf(self):
        caption = self.data.sh_name
        try:
            if self.what_show.isVisible() and self.answer is not None:
                imax = 86400 // self.discret.value()
                ishag = self.discret.value() / 3600
                self.y = []
                self.x = []
                for i in range(0, imax):
                    self.x.append(str(ishag * i))
                    self.y.append(0)  # будем выводить bar
                self.ymin = None
                self.ymax = None
                caption = caption + ' ' + self.what_show.currentText()
                js = json.loads(self.answer)
                self.ymax = None
                self.ymin = None
                av = 0
                qav = 0
                key, j = self.what_show.currentText().split(' (')
                key = key.strip()
                for j in range(0, len(js)):  # точки с данными
                    if "value" in js[j]:
                        t = js[j]["dt"]
                        t, v = cd.getpole(t, '.')  # отсекли возможные микросекунды
                        self.tt = cd.utc_local(datetime.datetime.strptime(t, '%Y-%m-%d %H:%M:%S'))
                        v = self.tt.second + self.tt.minute * 60 + self.tt.hour * 3600
                        val = js[j]["value"]
                        val = val[key]
                        if not self.ymin:
                            self.ymin = val
                            self.ymax = val
                        else:
                            self.ymin = min(self.ymin, val)
                            self.ymax = max(self.ymax, val)
                        av = av + val
                        qav = qav + 1
                        self.y[v // self.discret.value()] = val
                        self.x[v // self.discret.value()] = str(int(v // self.discret.value()))
                if qav != 0:
                    av = av / qav
                if self.ymin is not None:
                    self.maxmin.setText(self.what_show.currentText() + ': ' +
                                        "min= %.3f" % self.ymin + '; max= %.3f' % self.ymax + '; av = %.3f' % av)
                else:
                    self.maxmin.setText('')

            if self.show_graf_box.isChecked():
                if self.fig != None:
                    self.close_fig()
                if len(self.x) > 0:
                    self.fig = self.close_fig()
                    if self.tt:
                        st = ' за [' + str(self.tt.day) + '-' + str(self.tt.month) + '-' + str(self.tt.year) + ']'
                    else:
                        st = ''
                    self.fig = plt.figure(
                        frameon=True, num=caption + st +
                                          ' для [' + self.form_parent.windowTitle() + ']', clear=True)
                    self.cid = self.fig.canvas.mpl_connect('close_event', self.figure_close)
                    self.fig.canvas.mpl_connect('resize_event', self.fig_draw)
                    try:
                        mngr = plt.get_current_fig_manager()
                        mngr.window.setGeometry(self.xf, self.yf, self.dxf, self.dyf)
                    except:
                        pass
                    ax = plt.subplot(1, 1, 1)
                    ax.set_title(caption)
                    ax.set_xlabel('Время суток')
                    n = 86400 // self.discret.value()  # столько точек
                    if self.is_bar():
                        ax.bar(self.x, self.y, 1.0, label=caption)
                    else:
                        ax.plot(self.x, self.y, 1.0)
                    ax.grid(True)
                    xx = np.arange(0, n+1, 3600 // self.discret.value())
                    ax.set_xticks(xx)
                    xticks = ax.get_xticks()
                    xlabels = []
                    for i in range(0, len(xticks)):
                        v = self.discret.value()*xticks[i]
                        st = str(int(v // 3600))
                        if int(v % 3600 // 60) != 0:
                            st = st + '.' + str(int(v % 3600 // 60))
                        xlabels.append(st)
                    ax.set_xticklabels(xlabels)
                    ax.set_ylim(ymin=self.ymin - 0.05, ymax=self.ymax + 0.05)
                    plt.show()
                else:
                    if self.fig != None:
                        plt.close(self.fig)  # все закрывается
                        self.fig = None
            else:
                if self.fig != None:
                    self.close_fig()
        except Exception as e:
            QMessageBox.information(None, cd.get_text('Ошибки', id_text=4, key='main'), f"{e}",
                                    buttons=QtWidgets.QMessageBox.Close)

    def fig_draw(self, event):
        self.fig.tight_layout()

    def figure_close(self, event):
        if self.exist:
            self.exist = False
            self.fig = self.close_fig()
            self.show_graf_box.setChecked(0)
            self.exist = True

    def close_fig(self):
        try:
            if self.fig != None:
                mngr = plt.get_current_fig_manager()
                geom = mngr.window.geometry()
                self.xf, self.yf, self.dxf, self.dyf = geom.getRect()  # расположение фигуры
                self.fig.canvas.mpl_disconnect(self.cid)
                plt.close(self.fig)  # все закрывается
                self.fig = None
        except:
            pass

    def show_graf_changed(self):
        if self.exist:
            if self.show_graf_box.isChecked():
                self.show_graf()
            else:
                if self.fig:
                    self.fig.canvas.mpl_disconnect(self.cid)
                self.fig = self.close_fig()

    def write_click(self):
        t = cd.local_utc(self.dt_data.dateTime().toPyDateTime())
        v = t.second + t.minute * 60 + t.hour * 3600
        v = (v // self.discret.value()) * self.discret.value()
        dt = str(t.year) + '-' + str(t.month) + '-' + str(t.day) + ' ' + \
             str(v // 3600) + ':' + str((v % 3600) // 60) + ':' + str(v % 60)
        if self.data.category == 'fString':
            value = self.value_text.text()
        else:
            value = self.value.value()
            if (value is None) or (value == ''):
                value = 'NULL'
            else:
                if self.data.category == 'fInteger':
                    value = str(int(value))
                if self.data.category == 'fBoolean':
                    if value == 0:
                        value = 'false'
                    else:
                        value = 'true'
                else:
                    value = str(value)
        if self.value_code == 'None':
            ans = 'NULL'
        else:
            ans = "'" + str(self.value_code) + "'"
        ans = 'v1/MDM/his/' + cd.schema_name + '/' + self.typeobj_code + '/' + self.code + '/' + \
              str(self.value_code) + '?value=' + value + '&dt=' + dt
        ans, result = cd.send_rest(ans, 'POST')
        if result:
            ans = cd.getTextfromAnswer(ans)
            if ans == 'ok':
                self.show_inform()
            else:
                QtWidgets.QMessageBox.critical(
                    self, cd.get_text("Запись исторического значения", id_text=15, key='hist'),
                    cd.get_text('Ответ', id_text=4, key='main') + ' \n' + ans, defaultButton=QtWidgets.QMessageBox.Ok)

    def make_obnov_click(self):
        dt = time.localtime()
        self.dt_data.setDate(QtCore.QDate(dt.tm_year, dt.tm_mon, dt.tm_mday))
        self.dt_data.setTime(QtCore.QTime(dt.tm_hour, dt.tm_min, dt.tm_sec))
        self.show_inform()

    def to_day_click(self):
        t = datetime.datetime.now()
        self.dt_beg.setDate(QtCore.QDate(t.year, t.month, t.day))
        t = t + datetime.timedelta(days=1)
        self.dt_end.setDate(QtCore.QDate(t.year, t.month, t.day))
        self.show_inform()

    def yesterday_click(self):
        t = datetime.datetime.now()
        self.dt_end.setDate(QtCore.QDate(t.year, t.month, t.day))
        t = t - datetime.timedelta(days=1)
        self.dt_beg.setDate(QtCore.QDate(t.year, t.month, t.day))
        self.show_inform()

    def prev_button_click(self):
        t = self.dt_beg.dateTime().toPyDateTime() - datetime.timedelta(days=1)
        self.dt_beg.setDate(QtCore.QDate(t.year, t.month, t.day))
        t = self.dt_end.dateTime().toPyDateTime() - datetime.timedelta(days=1)
        self.dt_end.setDate(QtCore.QDate(t.year, t.month, t.day))
        self.show_inform()

    def next_button_click(self):
        t = self.dt_beg.dateTime().toPyDateTime() + datetime.timedelta(days=1)
        self.dt_beg.setDate(QtCore.QDate(t.year, t.month, t.day))
        t = self.dt_end.dateTime().toPyDateTime() + datetime.timedelta(days=1)
        self.dt_end.setDate(QtCore.QDate(t.year, t.month, t.day))
        self.show_inform()

    def what_changed(self):
        if not self.exist:
            return ''
        result = ''
        st = self.type_his.currentText()
        if st != self.read_type_his:
            result = result + self.caption + ': type_his ' + self.read_type_his + ' --> ' + st + '\n'
        if self.equipments.isVisible():
            st = self.equipments.currentText()
            if st != self.read_eq_name:
                result = result + self.caption + ': eq_name ' + self.read_eq_name + ' --> ' + st + '\n'
            st = self.parameters.currentText()
            if st != self.read_par_id:
                result = result + self.caption + ': par_id ' + self.read_par_id + ' --> ' + st + '\n'
        st = self.discret.value()
        if st != self.read_discret:
            result = result + self.caption + ': cycle ' + str(self.read_discret) + ' --> ' + str(st) + '\n'
        return result

    def refresh(self):
        self.exist = False
        self.discret.setValue(self.read_discret)
        if self.read_eq_name == '':
            self.equipments.setCurrentIndex(-1)
        else:
            self.equipments.setCurrentText(self.read_eq_name)
        if self.read_par_id == '':
            self.parameters.setCurrentIndex(-1)
        else:
            self.parameters.setCurrentText(self.read_par_id)
        if self.read_type_his == '':
            self.type_his.setCurrentIndex(-1)
        else:
            self.type_his.setCurrentText(self.read_type_his)
        self.exist = True
        self.type_his_change()

    def update(self):
        self.read_discret = self.discret.value()
        self.read_par_id = self.parameters.currentText()
        self.read_eq_name = self.equipments.currentText()
        self.read_eq_id = self.get_equipment_id()
        self.read_type_his = self.type_his.currentText()

    def save(self):
        if self.what_changed() != '':
            params = {}
            params['schema_name'] = cd.schema_name
            params['object_code'] = self.typeobj_code
            params['param_code'] = self.code
            params['obj_id'] = str(self.value_code)
            params['discret_sec'] = self.discret.value()
            params['type_his'] = self.type_his.currentText()
            params['equipment_id'] = self.get_equipment_id()
            params['parameter_id'] = self.get_parameter_id()
            ans, result = cd.send_rest('v1/MDM/his/link', directive='PUT', params=params)
            if result:
                try:
                    js = json.loads(ans)[0]
                    if 'error' not in js:
                        self.update()
                except:
                    cd.make_question(None, ans, cd.get_text('Ошибка', id_text=4, key='main'), str(params), onlyok=True)
            else:
                cd.make_question(None, ans, cd.get_text('Ошибка', id_text=4, key='main'), str(params), onlyok=True)

    def make_copy_click(self):
        dt_beg = self.time_for_sql(cd.local_utc(self.dt_source.dateTime().toPyDateTime()), False)
        dt_target = self.time_for_sql(cd.local_utc(self.dt_target.dateTime().toPyDateTime()), False)
        dt = self.dt_source.dateTime().toPyDateTime() + datetime.timedelta(days=1)
        dt_end = self.time_for_sql(cd.local_utc(dt), False)
        ans, result = cd.send_rest(
            'v1/MDM/his/copy/' + cd.schema_name + '/' + self.typeobj_code + '/' + self.code + '/' +
            str(self.value_code) + '?dt_beg=' +  dt_beg + '&dt_end=' + dt_end + '&dt_target=' + dt_target, 'POST')
        ans = cd.getTextfromAnswer(ans)
        if ans == 'ok':
            if self.dt_target.date() == self.dt_beg.date():
                self.show_inform()
        else:
            QtWidgets.QMessageBox.critical(
                self, cd.get_text("Копирование исторического значения", id_text=16, key='hist'),
                cd.get_text('Ошибка', id_text=4, key='main') + ' \n' + ans, defaultButton=QtWidgets.QMessageBox.Ok)

    def row_change(self, new, old):
        try:
            self.selection_change(self.table.selectionModel().currentIndex())
        except:
            pass

    def selection_change(self, qmodalindex):
        if self.exist:
            self.selected_row = qmodalindex.row()

    def table_double_click(self, qmodalindex):
        ind = qmodalindex.sibling(qmodalindex.row(), 1)
        value = self.root_model.data(ind)
        if self.data.category == 'fString':
            self.value_text.setText(value)
        else:
            self.value.setValue(float(value))
        ind = qmodalindex.sibling(qmodalindex.row(), 0)
        value = self.root_model.data(ind)
        value, st = cd.getpole(value, '.')  # отсечем микросекунды
        try:
            dt = datetime.datetime.strptime(value.strip(), '%d-%m-%Y %H:%M:%S')
            self.dt_data.setDate(QtCore.QDate(dt.year, dt.month, dt.day))
            self.dt_data.setTime(QtCore.QTime(dt.hour, dt.minute, dt.second))
        except Exception as err:
            QtWidgets.QMessageBox.critical(
                self, cd.get_text("Время", id_text=2, key='form'),
                cd.get_text('Ошибка', id_text=4, key='main') + ' \n' + f"{err}",
                defaultButton=QtWidgets.QMessageBox.Ok)

    def closeEvent(self, evt):
        self.close_fig()
        caption = 'History_' + self.data.sh_name
        cd.settings.setValue(caption + '_xf', self.xf)
        cd.settings.setValue(caption + '_yf', self.yf)
        cd.settings.setValue(caption + '_dxf', self.dxf)
        cd.settings.setValue(caption + '_dyf', self.dyf)
        cd.settings.sync()
        self.exist = False

    def customEvent(self, evt):
        if evt.type() == cd.StatusOperation.idType:  # изменение состояния соединения с PROXY
            n = evt.get_data()
            if n == cd.evt_change_language:
                self.change_language()

    def what_show_change(self):
        if self.exist:
            self.show_graf()