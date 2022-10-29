"""
GUI формы с параметрами объекта классов
"""
from PyQt5.QtWidgets import (QLabel, QLineEdit, QTextEdit, QComboBox, QSpinBox, QCheckBox,
                             QDoubleSpinBox, QDateTimeEdit, QFrame)
from PyQt5 import QtGui
from PyQt5 import (QtWidgets, QtCore)
import common_data as cd
import json
import  datetime
import array_json


class FieldInform():
    object_m = None  # активный элемент
    object_d = None  # неактивный элемент
    field_name = ''  # имя поля данного
    initial_value = None  # начальное значение поля
    value = None  # значение поля
    data = None  # тип параметра TTypeParam
    layout = None
    fparent_layout = None
    mas_reference = None
    exist = True
    parameter = None
    form_parent = None
    object_code = None
    sh_name = None
    code = None

    def is_exist(self, key):
        return key in self.parameter

    def get_value(self, code):
        if self.is_exist(code):
            return self.parameter[code]

    def add(self, parent_layout, parameter, form_parent):
        self.parameter = parameter
        sh_name = self.get_value('name')
        data_code = self.get_value('data_code')
        len = self.get_value('len')
        self.form_parent = form_parent
        if self.is_enum():
            self.layout = QtWidgets.QHBoxLayout()
            self.object_d = QLabel(sh_name)
            self.layout.addWidget(self.object_d)
            self.object_m = QComboBox()
            self.layout.addWidget(self.object_m)
            self.layout.addWidget(QLabel(), 10)
            parent_layout.addLayout(self.layout)
            # заполнить список метками перечисляемого типа
            data, result = cd.send_rest('v1/enums?enum_name=' + data_code, show_error=False)
            if result:
                js = json.loads(data)
                js = js['labels']
                for mas_enum in js:
                    st = mas_enum["label"]
                    self.object_m.addItem(st)
            else:
                QtWidgets.QMessageBox.critical(
                    None, cd.get_text("Чтение меток перечисляемого типа данных", id_text=22, key='enum'),
                    cd.get_text('Ошибка', id_text=4, key='main') + ' \n' + data + '\n' +
                    cd.get_text('По умолчанию используются', id_text=5, key='main') + ':\n\tHost Proxy=' +
                    cd.HOST + '\n\tPortProxy=' + str(cd.PORT),
                    defaultButton=QtWidgets.QMessageBox.Ok)
            self.object_m.currentIndexChanged.connect(self.changed)
        if self.is_line_edit():
            self.layout = QtWidgets.QHBoxLayout()
            self.object_d = QLabel(sh_name)
            self.layout.addWidget(self.object_d)
            self.object_m = QLineEdit()
            if len is not None:
                self.object_m.setMaxLength(len)
            self.layout.addWidget(self.object_m)
            self.layout.addWidget(QLabel(), 10)
            parent_layout.addLayout(self.layout)
            self.object_m.textChanged.connect(self.changed)
            if data_code.lower() == 'uuid':
                self.object_m.setEnabled(False)
        elif self.is_text_edit():
            self.layout = QtWidgets.QFormLayout()
            self.layout.setRowWrapPolicy(2)
            self.object_m = QTextEdit()
            self.object_m.setTabChangesFocus(True)
            self.layout.addRow(sh_name, self.object_m)
            # self.layout.addWidget(QLabel(), 10)
            parent_layout.addLayout(self.layout)
            self.object_m.textChanged.connect(self.changed)
        elif self.is_spin_box():
            if data_code.upper() != 'LOCALIZEDTEXT':
                self.layout = QtWidgets.QHBoxLayout()
                self.object_d = QLabel(sh_name)
                self.layout.addWidget(self.object_d)
                self.object_m = QSpinBox()
                self.set_min_val()
                if self.get_value('code') == 'id':
                    self.object_m.setEnabled(False)
                    self.object_m.setButtonSymbols(2)
                self.layout.addWidget(self.object_m)
                self.layout.addWidget(QLabel(), 10)
                parent_layout.addLayout(self.layout)
                self.object_m.valueChanged.connect(self.changed)
        elif self.is_double_spin_box():
            self.layout = QtWidgets.QHBoxLayout()
            self.object_d = QLabel(sh_name)
            self.layout.addWidget(self.object_d)
            self.object_m = QDoubleSpinBox()
            if len is not None:
                n = len
            else:
                n = 15
            self.object_m.setDecimals(max(0, n))
            self.set_min_val()
            self.layout.addWidget(self.object_m)
            self.layout.addWidget(QLabel(), 10)
            parent_layout.addLayout(self.layout)
            self.object_m.valueChanged.connect(self.changed)
        elif self.is_check_box():
            self.layout = QtWidgets.QVBoxLayout()
            self.object_m = QCheckBox(sh_name)
            self.object_m.setTristate(False)
            self.layout.addWidget(self.object_m)
            parent_layout.addLayout(self.layout)
            self.object_m.stateChanged.connect(self.changed)
        elif self.is_date_time():
            self.layout = QtWidgets.QHBoxLayout()
            self.object_d = QLabel(sh_name)
            self.layout.addWidget(self.object_d)
            self.object_m = QDateTimeEdit()
            self.object_m.setDisplayFormat('dd-MM-yyyy hh.mm.ss')
            self.layout.addWidget(self.object_m)
            self.layout.addWidget(QLabel(), 2)
            parent_layout.addLayout(self.layout)
            self.object_m.dateTimeChanged.connect(self.changed)

        description =  self.get_value('description')
        if self.object_d is not None:
            self.object_d.setToolTip(description)
        if self.object_m is not None:
            self.object_m.setToolTip(description)

        if self.get_value('not_null') == 'TRUE' and self.object_d is not None:
            self.object_d.setStyleSheet("color: red;")
            self.object_d.setFont(QtGui.QFont("Arial", 11))

    def set_min_val(self):
        min_val = self.get_value('min_val')
        max_val = self.get_value('max_val')
        if max_val:
            self.object_m.setMaximum(max_val)
        else:
            self.object_m.setMaximum(1000000000)
        if min_val:
            self.object_m.setMinimum(min_val)
        else:
            self.object_m.setMinimum(-1000000000)

    def fill_combo(self, mes):
        self.object_m.addItem('')
        data, result = cd.send_rest(mes)
        if result:
            js = json.loads(data)
            for unit in js:
                st = cd.translate_from_base(unit["sh_name"])
                self.object_m.addItem(st, unit)

    def add_combo(self, parent_layout, parameter, sh_name, object_code, code, form_parent):
        self.parameter = parameter
        self.form_parent = form_parent
        self.object_code = object_code
        self.code = code  # для запроса v1/reference
        self.sh_name = sh_name + " (" + object_code + "/" + code + ")"
        self.layout = QtWidgets.QHBoxLayout()
        self.object_d = QLabel(self.sh_name)
        self.layout.addWidget(self.object_d)
        self.object_m = QComboBox()
        self.object_m.setMaxVisibleItems(20)
        self.layout.addWidget(self.object_m)
        parent_layout.addLayout(self.layout)
        if code == '':
            self.fill_combo('v1/objects/full_list/' + cd.schema_name + '/' + self.object_code)
        # self.object_m.currentIndexChanged.connect(self.changed)

    def is_line_edit(self):
        # дается ответ нужно ли использовать QLineEdit
        st = self.get_value('data_code').upper()
        categor = self.get_value('categor')
        len = self.get_value('len')
        return (st == 'LTREE') or  (st == 'INT8') or \
               ((categor == 'fString') and (len is not None and (len <= 50) or (st == 'UUID') or (st == 'GUID')))

    def is_text_edit(self):
        # дается ответ нужно ли использовать QTextEdit
        st = self.get_value('data_code').upper()
        categor = self.get_value('categor')
        len = self.get_value('len')
        if st == 'LOCALIZEDTEXT':
            return False
        return (st == 'INET') or \
               (categor == 'fString') or (len is not None and len > 50)

    def is_enum(self):
        return self.get_value('is_enum') == 'TRUE'

    def is_spin_box(self):
        return self.get_value('categor') == 'fInteger'

    def is_double_spin_box(self):
        return self.get_value('categor') == 'fFloat'

    def is_check_box(self):
        return self.get_value('categor') == 'fBoolean'

    def is_date_time(self):
        return self.get_value('categor') == 'fDateTime'

    def changed(self, newText=''):
        if self.exist:
            if self.is_enum():
                self.value = self.object_m.currentText()
            elif self.is_line_edit():
                self.value = newText
            elif self.is_text_edit():
                self.value = self.object_m.toPlainText()
            # elif self.isComboBox():
            #     unit = self.objectm.currentData()
            #     if unit is not None:
            #         self.value = unit['id']
            #     else:
            #         self.value = None
            elif self.is_spin_box():
                self.value = self.object_m.value()
            elif self.is_double_spin_box():
                self.value = self.object_m.value()
            elif self.is_check_box():
                self.value = self.object_m.isChecked()
            elif self.is_date_time():
                self.value = self.object_m.dateTime().toPyDateTime()
            self.form_parent.is_need_to_save()

    def what_changed(self):
        if type(self.value) == str:
            if str(self.value) == str(cd.is_null(self.initial_value, '')):
                return ''
        else:
            if str(self.value) == str(self.initial_value):
                return ''
        st = self.get_value("code") + ': '
        categor = self.get_value("categor")
        if categor == 'fString':
            st = st + str(self.initial_value) + ' --> ' + self.value
        elif categor == 'fInteger':
            st = st + str(self.initial_value) + ' --> ' + str(self.value)
        elif categor == 'fBoolean':
            st = st + str(self.initial_value) + " --> " + cd.valueBoolean(self.value)
        else:
            st = st + str(self.initial_value) + ' --> ' + str(self.value)
        return st

    def txt_json(self):
        if (self.value is not None) and (self.value != ''):
            self.value = self.value.replace(" True", ' true')
            self.value = self.value.replace(":True", ': true')
            self.value = self.value.replace(" False", ' false')
            self.value = self.value.replace(":False", ': false')
            return "'" + cd.translate_to_base(self.value.replace("'", '"')) + "'"
        else:
            return 'NULL'

    def txt_date_time(self):
        if self.value is not None:
            dt = self.object_m.dateTime().toPyDateTime()
            dt = str(dt.year) + '-' + str(dt.month) + '-' + str(dt.day) + ' ' + \
                 str(dt.hour) + ':' + str(dt.minute) + ':' + str(dt.second)
            return '"' + dt + '"'
        else:
            return 'NULL'

    def get_txt_value(self):
        """
        Получение значения свойства в виде текста для формирования строки параметров для PUT v1/object
        :return:
        """
        data_code = self.get_value('data_code')
        categor = self.get_value('categor')
        if (data_code.upper() == 'JSON') or (data_code.upper() == 'JSONB'):
            return self.txt_json()
        elif (categor == 'fString') or self.is_enum():
            return "'" + cd.translate_to_base(self.value) + "'"
        elif self.is_check_box():
            return cd.valueBoolean(self.value, val1='true', val0='false')
        elif self.is_date_time():
            return self.txt_date_time()
        else:
            if self.value is None:
                return 'NULL'
            else:
                if self.value == str(self.value):
                    return "'" + cd.translate_to_base(self.value) + "'"
                else:
                    return str(self.value)

    def set_value_json(self, value):
        self.initial_value = str(value)
        self.initial_value = self.initial_value.replace("'", '"')
        self.initial_value = self.initial_value.replace(" True", ' true').replace(":True", ': true')
        self.initial_value = self.initial_value.replace(" False", ' false').replace(":False", ': false')

    def set_value(self, value):
        data_code = self.get_value('data_code')
        categor = self.get_value('categor')
        if (data_code.upper() == 'JSON') or (data_code.upper() == 'JSONB'):
            self.set_value_json(value)
        if (categor == 'fString') or self.is_enum():
            self.initial_value = cd.translate_from_base(value)
        if self.is_check_box():
            self.initial_value = value.lower() == 'true'
        else:
            self.initial_value = value
        self.value = self.initial_value
        self.show()

    def refresh(self):
        self.value = self.initial_value
        self.show()

    def show(self):
        self.exist = False
        try:
            if self.is_enum():
                if self.value is None:
                    self.object_m.setCurrentIndex(-1)
                else:
                    self.object_m.setCurrentText(self.value)
            elif self.is_line_edit():
                self.object_m.setText(self.value)
            elif self.is_text_edit():
                self.object_m.setText(self.value)
            # elif self.isComboBox():
            #     self.objectm.setCurrentIndex(-1)
            #     for j in range(0, len(self.mas_reference)):
            #         if str(self.value) == self.mas_reference[j]["id"]:
            #             self.objectm.setCurrentIndex(j + 1)  # пустое значение добавляется в начало
            #             break
            elif self.is_spin_box():
                self.object_m.setValue(cd.is_null(self.value, 0))
            elif self.is_double_spin_box():
                self.object_m.setValue(cd.is_null(self.value, 0))
            elif self.is_check_box():
                if self.value:
                    self.object_m.setChecked(1)
                else:
                    self.object_m.setChecked(0)
            elif self.is_date_time():
                dt = datetime.datetime.strptime(self.value, '%Y-%m-%d %H:%M:%S')
                self.object_m.setDateTime(QtCore.QDateTime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second))
        except Exception as err:
            print('fields', 'show', f"{err}")
        self.exist = True
