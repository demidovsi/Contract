"""
Форма паспорта объекта класса объектов для страницы MAIN
"""
from PyQt5.QtWidgets import (QWidget, QScrollArea, QTabWidget, QMessageBox, QFrame)
from PyQt5 import (QtWidgets, QtGui, QtCore)
import common_data as cd
# import typeparam
# import fieldinform
import fields
import pagecontrol
# import pasport_relation
# import pasport_historicals
# import pasport_locale
import json
import array_json


def define_reference(parameters, index):
    def get_unit(object_code):
        data, result = cd.send_rest('v1/MDM/params/' + cd.schema_name + '?object_code=' + object_code,
                                    show_error=False)
        if result:
            js = json.loads(data)
            for unit in js:
                if unit['data_code'].upper() == 'REFERENCE':
                    return {"object_code": unit['code_ref'], "code": unit['code']}

    array_reference = list()
    unit = {"object_code": parameters.get_value(index, 'code_ref'), "code": parameters.get_value(index, 'code')}
    while unit is not None:
        array_reference.append(unit)
        unit = get_unit(unit["object_code"])
    return array_reference


class PassportMain(QWidget):
    form_parent = None
    layout = None
    parent_layout = None
    parameters = None  # массив описания параметров класса объектов
    object_code = None
    obj_id = None
    fields = list()
    array_reference = list()
    exist = False

    def __init__(self, form_parent, parent_layout, parameters, object_code, obj_id):
        self.parameters = parameters
        self.form_parent = form_parent
        self.object_code = object_code
        self.obj_id = obj_id
        self.parent_layout = parent_layout
        self.fields = []
        out_number = 0
        for i in range(parameters.get_count()):
            st = parameters.get_value(i, 'data_code')
            if st is not None:
                st = st.upper()
            if st == 'RELATION' or st == 'LOCALIZEDTEXT' or st == 'REFERENCE':
                continue
            st = parameters.get_value(i, 'info_code')
            if st is not None:
                st = st.upper()
            if st != 'NSI':
                continue
            field = fields.FieldInform()
            field.add(parent_layout, parameters.get_unit(i), self)
            self.fields.append(field)

    def clear(self):
        for field in self.fields:
            self.parent_layout.removeItem(field.layout)
        self.fields = []

    def is_need_to_save(self):
        self.form_parent.is_need_to_save()  # passport_entity

    def what_changed(self):
        result = ''
        for field in self.fields:
            st = field.what_changed()
            if st != '':
                result = result + st + '\n'
        return result

    def what_error(self):
        result = ''
        for field in self.fields:
            if field.parameter is None:
                continue
            if field.parameter['not_null'] == 'true':
                if field.value is None:
                    result = result + cd.get_text("не задано значение", id_text=13, key='entities') + " " +\
                             cd.get_text("для", id_text=19, key='import') + " " + field.parameter['code'] + '\n'
        return result

    def get_text_sql(self, code):
        """
        Получить текст параметра с кодом code для записи в БД.
        :param code:
        :return:
        """
        for field in self.fields:
            if field.get_value('code') == code:
                return field.get_txt_value()

    def set_value(self, code, value):
        """
        Заполнение полей объекта из БД.
        :param code:
        :param value:
        :return:
        """
        pass
        for field in self.fields:
            if field.object_code is None and field.get_value('code') == code:
                field.set_value(value)
                break

    def refresh(self):
        self.exist = False
        for field in self.fields:
            if field.data is not None:
                field.refresh()
        self.exist = True

