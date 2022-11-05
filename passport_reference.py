from PyQt5.QtGui import *
from PyQt5 import (QtWidgets, QtCore)
from PyQt5.QtWidgets import (QWidget, QLabel, QTextEdit)
import common_data as cd
import json
import fields


class PassportReference(QWidget):
    caption = ''
    exist = False
    form_parent = None
    parameter = None
    fields = list()
    parent_layout = None

    def __init__(self, parent, form_parent, caption):
        super(QWidget, self).__init__()
        self.form_parent = form_parent
        self.caption = caption
        self.layout = QtWidgets.QVBoxLayout()
        parent.setLayout(self.layout)

    def define_reference(self, parameter):
        def get_unit(object_code):
            data, result = cd.send_rest('v1/MDM/params/' + cd.schema_name + '?object_code=' + object_code,
                                        show_error=False)
            if result:
                js = json.loads(data)
                for unit in js:
                    if unit['data_code'].upper() == 'REFERENCE':
                        return {"object_code": unit['code_ref'], "code": unit['code']}

        self.parameter = parameter
        array_reference = list()
        unit = {"object_code": parameter['code_ref'], "code": parameter['code']}
        code_parent = ''
        out_number = 0
        while unit is not None:
            array_reference.append(unit)
            unit = get_unit(unit["object_code"])
        i = len(array_reference) - 1
        while i >= 0:
            unit = array_reference[i]
            unit["code_parent"] = code_parent
            field = fields.FieldInform()
            field.out_number = out_number
            field.reference = unit
            out_number += 1
            field.add_combo(self.layout, parameter, unit["code"], unit["object_code"], code_parent, self)
            self.fields.append(field)
            code_parent = unit["code"]
            i -= 1

    def show_data(self, parameter):
        self.fields = []
        self.define_reference(parameter)

    def what_changed(self):
        result = ''
        field = self.fields[-1]
        if field.value != field.initial_value:
            result = field.reference['code'] + ': ' + str(field.initial_value) + ' -> ' + str(field.value)
        return result

    def reference_changed(self):
        if not self.exist:
            return
        out_number = None
        id_parent = None
        for field in self.fields:
            ind = field.object_m.currentIndex()
            data = field.object_m.itemData(ind)
            if data is None or str(data['id']) != str(field.value):  # нашли combobox с изменениями
                out_number = field.out_number
                if data is None:
                    id_parent = -1
                else:
                    id_parent = data['id']
                field.value = id_parent
                break
        if out_number is not None:
            self.exist = False
            for field in self.fields:
                if field.out_number > out_number:
                    field.object_m.clear()
                    field.value = -1
            for field in self.fields:
                if field.out_number == out_number + 1:
                    field.fill_combo('v1/list/' + cd.schema_name + '/' + field.reference['object_code'] +
                             '?usl=' + field.reference['code_parent'] + '=' + str(id_parent))
                field.id_parent = id_parent
        self.exist = True
        self.form_parent.is_need_to_save()

    def set_value_reference(self, js):
        for key in js.keys():
            if key + '_reference' in js:
                for field in self.fields:
                    if field.reference['code'] == key:
                        field.reference['value'] = js[key]
                        self.set_value_reference(js[key + '_reference'])

    def show_references(self, index=None, id_parent=None):
        self.exist = False
        if index is None:
            index = 0
        reference = self.fields[index].reference
        if id_parent is not None:
            # загрузить
            for field in self.fields:
                if field.object_code == reference['object_code']:  # нашли поле
                    field.fill_combo('v1/list/' + cd.schema_name + '/' + reference['object_code'] +
                                     '?usl=' + reference['code_parent'] + '=' + str(id_parent))
                    field.id_parent = id_parent
                    break
        for field in self.fields:
            if field.object_code == reference['object_code']:
                if 'value' in reference:
                    for i in range(field.object_m.count()):
                        if field.object_m.itemData(i) is not None and \
                                str(field.object_m.itemData(i)['id']) == str(reference['value']):
                            field.object_m.setCurrentIndex(i)
                            field.value = reference['value']
                            field.initial_value = field.value
                            break
                else:
                    field.object_m.setCurrentIndex(-1)
                    field.value = None
                    field.initial_value = field.value

                if index != len(self.fields) - 1:
                    self.show_references(index + 1, field.value)
                break
        self.exist = True

    def get_id(self):
        if int(self.fields[-1].value) > 0:
            return self.fields[-1].value
        else:
            return 'null'

    def refresh(self):
        for field in self.fields:
            field.value = field.initial_value
        self.show_references()