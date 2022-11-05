"""
Форма паспорта объекта класса объектов
"""
from PyQt5.QtWidgets import (QWidget, QScrollArea, QTabWidget, QMessageBox)
from PyQt5 import (QtWidgets, QtGui, QtCore)
import common_data as cd
# import typeparam
# import fieldinform
import pagecontrol
# import pasport_relation
# import pasport_historicals
# import pasport_locale
import type_param
import json
import array_json
import passport_main
import passport_locale
import passport_reference
import passport_history
import passport_relation


class PassportEntity(QWidget):
    form_parent = None
    parameters = None  # описание параметров класса объектов
    object_code = None
    obj_id = None
    passport_main = None
    passport_locales = list()
    passport_references = list()
    passport_histories = list()
    passport_relations = list()

    def __init__(self, parent, form_parent):
        super(QWidget, self).__init__()
        self.form_parent = form_parent
        self.setFont(QtGui.QFont('Arial', 11))

        self.widget = QWidget()
        self.page_control = pagecontrol.PageControl(self.widget, QTabWidget.North)
# контейнер для кнопок
        self.layoutButton = QtWidgets.QHBoxLayout()

        self.refresh_button = QtWidgets.QPushButton(cd.iconRefresh, '')
        self.refresh_button.clicked.connect(self.refresh)
        self.layoutButton.addWidget(self.refresh_button)

        self.save_button = QtWidgets.QPushButton(cd.iconSave, '')
        self.save_button.clicked.connect(self.save_click)
        self.layoutButton.addWidget(self.save_button)

        self.what_button = QtWidgets.QPushButton('')
        self.what_button.clicked.connect(self.what_changed_click)
        self.layoutButton.addWidget(self.what_button)

        self.close_button = QtWidgets.QPushButton('Close')
        self.layoutButton.addWidget(self.close_button)
        self.close_button.clicked.connect(self.close_button_click)

# Страница "Main"
        self.tabMain = self.page_control.addTab('')
        self.layout_main = QtWidgets.QVBoxLayout(self.tabMain)
        self.layout = QtWidgets.QVBoxLayout(parent)
        self.layout.addLayout(self.layoutButton)
        self.layout.addWidget(self.page_control)
        self.change_language()
        self.passport_locales = []
        self.passport_references = []

    def change_language(self):
        self.page_control.tabs.setTabText(0, cd.get_text('Main', id_text=1, key='passport'))
        self.refresh_button.setText(cd.get_text('Восстановить', id_text=30, key='main'))
        self.save_button.setText(cd.get_text('Сохранить', id_text=29, key='main'))
        self.what_button.setText(cd.get_text('Изменения', id_text=31, key='main'))

    def load_params(self, object_code):
        # прочитать состав параметров класса объектов (object_code) из приложения (app_code)
        self.object_code = object_code
        data, result = cd.send_rest('v1/MDM/params/' + cd.schema_name + '?object_code=' + object_code)
        if result:
            self.parameters = array_json.TArrayJson(json.loads(data))

    def show_data(self, obj_id):
        self.obj_id = obj_id
        self.passport_histories = []
        self.passport_locales = []
        self.passport_relations = []
        self.passport_references = []
        self.refresh_button.setVisible(obj_id != '0')
        if self.passport_main is not None:
            self.passport_main.clear()
        # прочитать состав объекта
        self.passport_main = passport_main.PassportMain(
            self, self.layout_main, self.parameters, self.object_code, self.obj_id)
        # создать формы LOCALE
        for i in range(self.parameters.get_count()):
            parameter = self.parameters.get_unit(i)
            if parameter['data_code'].upper() == 'LOCALIZEDTEXT':
                tab = self.page_control.addTab('Locale: ' + parameter['code'])
                form = passport_locale.PassportLocale(tab, self, 'Locale: ' + parameter['code'])
                self.passport_locales.append(form)
        # создать формы REFERENCE
        for i in range(self.parameters.get_count()):
            parameter = self.parameters.get_unit(i)
            data = type_param.TTypeParam(parameter)
            if parameter['data_code'].upper() == 'REFERENCE':
                tab = self.page_control.addTab(data.sh_name)
                form = passport_reference.PassportReference(tab, self, parameter['code'])
                form.show_data(parameter)
                self.passport_references.append(form)
        # создать формы истории
        for i in range(self.parameters.get_count()):
            parameter = self.parameters.get_unit(i)
            if parameter['info_code'].upper() == 'HIS':
                data = type_param.TTypeParam(parameter)
                tab = self.page_control.addTab(data.sh_name)
                form = passport_history.PassportHistory(tab, self)
                form.data = data
                form.value_code = obj_id
                form.caption = data.sh_name
                form.typeobj_code = self.object_code  # собственный тип объекта
                form.code = data.code
                self.passport_histories.append(form)
        # создать формы RELATION
        for i in range(self.parameters.get_count()):
            parameter = self.parameters.get_unit(i)
            if parameter["data_code"] == 'Relation':
                data = type_param.TTypeParam(parameter)
                tab = self.page_control.addTab(data.sh_name)
                form = passport_relation.PassportRelation(tab, self)
                form.caption = data.sh_name
                form.rel_typeobj_code = data.code_ref  # тип объекта связи
                form.typeobj_code = self.object_code  # собственный тип объекта
                form.rel_code = data.code
                form.code = 'id'
                form.value_code = obj_id
                form.show_list()
                form.show_data()
                self.passport_relations.append(form)

        self.show_values_object()
        self.passport_main.exist = True

    def show_values_object(self):
        # прочитать значения полей объекта
        data, result = cd.send_rest(
            'Entity.GetValues/' + self.object_code + '/' + str(self.obj_id) + '?schema_name=' + cd.schema_name)
        js = json.loads(data)[0]  # исходные значения
        for key in js.keys():
            self.passport_main.set_value(key, js[key])
        for form in self.passport_references:
            form.set_value_reference(js)
            form.show_references()
        for form in self.passport_histories:
            form.show_data()

        # заполнить Locale
        for i in range(self.parameters.get_count()):
            parameter = self.parameters.get_unit(i)
            if parameter['data_code'].upper() == 'LOCALIZEDTEXT':
                caption = 'Locale: ' + parameter['code']
                for form in self.passport_locales:
                    if form.caption == caption:
                        form.value_code = js[parameter['code']] if parameter['code'] in js else 0
                        form.show_data()
                        break
        self.is_need_to_save()

    def close_button_click(self):
        cd.send_evt({"command": "close_page", "object_code": self.object_code, "obj_id": self.obj_id}, self.form_parent)

    def what_changed_click(self):
        self.what_changed()

    def what_changed(self, show_mes=True):
        result = self.passport_main.what_changed()
        for form in self.passport_locales:
            st = form.what_changed()
            if st != '':
                result = result + st + '\n'
        for form in self.passport_references:
            st = form.what_changed()
            if st != '':
                result = result + st + '\n'
        for form in self.passport_histories:
            st = form.what_changed()
            if st != '':
                result = result + st + '\n'
        for form in self.passport_relations:
            st = form.what_changed()
            if st != '':
                result = result + st + '\n'
        if show_mes:
            if result == '':
                result = cd.get_text('Изменений НЕТ', id_text=13, key='param')
            else:
                result = cd.get_text('Список изменений', id_text=14, key='param') + ':\n' + result
            st_error = self.what_error()
            if st_error != '':
                result = result + '\n\t' + cd.get_text('Ошибки', id_text=4, key='main') + ':\n' + st_error
            if show_mes:
                QMessageBox.information(self, cd.get_text('Изменения и ошибки', id_text=15, key='param'), result,
                                        buttons=QtWidgets.QMessageBox.Close)
        return result

    def is_need_to_save(self):
        """
        Определить необходимость и возможность спасения изменений свойств объекта.
        :return:
        """
        mes_change = self.what_changed(show_mes=False)  # список изменений или пустая строка, если изменений нет
        need_save = mes_change != ''
        if self.what_error() == '':
            if need_save:
                self.what_button.setStyleSheet("color: green;")
            else:
                self.what_button.setStyleSheet("color: black;")
        else:
            self.what_button.setStyleSheet("color: red;")
        self.refresh_button.setEnabled(need_save)
        self.save_button.setEnabled(need_save)
        self.what_button.setEnabled(need_save)

    def what_error(self):
        result = self.passport_main.what_error()
        return result

    def save_click(self):
        txt = ''
        for i in range(self.parameters.get_count()):
            parameter = self.parameters.get_unit(i)
            if parameter['data_code'].upper() == 'LOCALIZEDTEXT':
                for form in self.passport_locales:
                    if form.caption == 'Locale: ' + parameter['code']:
                        form.save()
                        st = str(form.value_code)
                        break
            elif parameter['data_code'].upper() == 'REFERENCE':
                for form in self.passport_references:
                    if form.caption == parameter['code']:
                        st = str(form.get_id())
            else:
                st = self.passport_main.get_text_sql(parameter['code'])
            if st is not None and st != '':
                if txt != '':
                    txt = txt + ", "
                txt = txt + st
        # print(txt)
        data, result = cd.send_rest(
            'v1/object/' + cd.schema_name + '/' + self.object_code + '?param_list=' + txt, 'PUT', show_error=True)
        if result:
            id = int(cd.get_text_from_answer(data))
            # спасти изменения в исторических данных
            for form in self.passport_histories:
                form.value_code = str(id)
                form.save()
            # спасти изменения в RELATION
            for form in self.passport_relations:
                form.value_code = str(id)
                form.save()
            self.obj_id = id
            self.show_values_object()
            cd.send_evt({"command": "new_object", "object_code": self.object_code, "obj_id": self.obj_id},
                        self.form_parent)
        self.form_parent.make_obnov_click()

    def refresh(self):
        self.passport_main.refresh()
        for form in self.passport_locales:
            form.refresh()
        for form in self.passport_references:
            form.refresh()
        for form in self.passport_histories:
            form.refresh()
        for form in self.passport_relations:
            form.refresh()
        self.is_need_to_save()

    def customEvent(self, evt):
        if evt.type() == cd.StatusOperation.idType:  # изменение состояния соединения PROXY
            n = evt.get_data()
            if n == cd.evt_change_language:
                self.change_language()
                for form in self.passport_relations:
                    cd.send_evt(n, form)
                for form in self.passport_locales:
                    cd.send_evt(n, form)
                for form in self.passport_histories:
                    cd.send_evt(n, form)
                for form in self.passport_references:
                    cd.send_evt(n, form)
