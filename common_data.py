import json
import PyQt5
from PyQt5 import (QtWidgets,QtCore)
from PyQt5.QtWidgets import (QMessageBox, QApplication, QCheckBox, QPushButton, QSpinBox, QDoubleSpinBox, QComboBox)
import requests
from requests.exceptions import HTTPError
import base64
import time
import datetime

kirill = 'Kirill!981'
version = ' (v1.1.1 2022-10-) '
settings = None

app_lang = 'en'
texts = dict()
width_form = 1200
height_form = 800

iconDelete = None
iconCreate = None
iconUp = None
iconDown = None
iconOpen = None
iconSave = None
iconRefresh = None
icon_font = None
icon_minus = None
icon_left = None
icon_right = None
icon_do = None

txt_error_connection = ''
inform_from_proxy = ''
token = ''
user_role = None
expires = None
schema_name = None
url = None
HOST = None
PORT = None
username = None
password = None
interval_connection = None  # Интервал в секундах контроля соединения с PROXY
info_code = 'NSI'

evt_change_language = -1001  # сменен язык
evt_cancel_connect = 0  # нарушение связи
evt_refresh_connect = 1  # восстановление связи
evt_change_mdm = 2  # изменения МДМ
evt_change_database = 3  # изменение базы данных
evt_change_config_modeler = 5  # изменения в настройке моделера
evt_delete_table_entity = 6  # удалена таблица сущности

mas_json_objects = []


class StatusOperation(QtCore.QEvent):
    idType = QtCore.QEvent.registerEventType()

    def __init__(self, data):
        QtCore.QEvent.__init__(self, StatusOperation.idType)
        self.data = data

    def get_data(self):
        return self.data


def load_texts(language_id):
    """
    Чтение текстов диалекта.
    :return:
    """
    global texts
    file_name = 'languages/texts_' + language_id + '.json'
    try:
        f = open(file_name, 'rt', encoding='utf-8')  # только чтение и текстовый файл
        with f:
            texts = f.read()
            texts = json.loads(texts.replace('\n', ' '))
    except Exception as err:
        txt = f'Other error occurred: {err}'
        make_question(None, txt + '\n' + file_name, 'Ошибка чтения файла', onlyok=True)


def make_question(self, txt, informative_text=None, detailed_text=None, onlyok=False):
    message_box = QMessageBox(self)
    message_box.setText(txt)
    message_box.setIcon(4)
    if informative_text:
        message_box.setWindowTitle(informative_text)
    if detailed_text:
        message_box.setDetailedText(detailed_text)
    if onlyok:
        message_box.setStandardButtons(QMessageBox.Yes)
        message_box.setDefaultButton(QMessageBox.Yes)
    else:
        message_box.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
        message_box.setDefaultButton(QMessageBox.No)
    result = message_box.exec()
    return result == QMessageBox.Yes


def get_value_dic(user_dict, code, default):
    """
    Выборка значения из словаря по ключу и ли значение по умолчанию, если ключ в словаре отсутствует.
        :param user_dict: словарь.
    :param code: ключ
    :param default: значение по умолчанию.
    :return: значение ключа словаря или значение по умолчанию (если ключа нет).
    """
    if code in user_dict:
        return user_dict[code]
    else:
        return default


def get_text(value=None, key=None, id_text=None, first_upper=False, first_low=False, delete_lf=False):
    """
    Получение значения текста для текущего диалекта.
        :param value: текст эталонный.
        :param key:
        :param id_text:
        :param first_upper: первый символ должен быть на верхнем регистре.
        :param first_low: первый символ должен быть на нижнем регистре.
        :param delete_lf: заменять перевод строки на пробел.
        :return: текст, приведенный к диалекту или эталонный текст, если в словаре трансляция эталона отсутствует.
    """
    global texts
    result = value
    if key is None:
        result = get_value_dic(texts, value, value)
    elif id is not None and key in texts:
        for unit in texts[key]:
            if 'id' in unit and unit['id'] == id_text and 'text' in unit:
                result = unit['text']
                break
    if first_low:
        result = result[0].lower() + result[1:len(result)]

    if first_upper:
        result = result[0].upper() + result[1:len(result)]
    if delete_lf:
        result = result.replace('\n', ' ')
    return result


def login(show_error=True):
    global token, expires, app_lang, user_role
    txt = ''
    result = False
    txt_z = {"login": username, "password": password, "rememberMe": True}
    try:
        headers = {"Accept": "application/json"}
        response = requests.request(
            'POST', url + 'v1/login', headers=headers,
            json={"params": txt_z}
            )
    except HTTPError as err:
        txt = f'HTTP error occurred: {err}'
        if show_error:
            make_question(None, txt, 'Ошибка LOGIN', str(txt_z), onlyok=True)
    except Exception as err:
        txt = f'Other error occurred: : {err}'
        if show_error:
            make_question(None, txt, 'Ошибка LOGIN', str(txt_z), onlyok=True)
    else:
        try:
            txt = response.text
            result = response.ok
            if result:
                js = json.loads(txt)
                if "accessToken" in js:
                    token = js["accessToken"]
                if "expires" in js:
                    expires = time.mktime(time.strptime(js["expires"], '%Y-%m-%d %H:%M:%S'))
                if 'lang' in js:
                    app_lang = js['lang']
                if 'role' in js:
                    user_role = js['role']
            else:
                return txt, result
        except Exception as err:
            txt_error = f'Error occurred: : {err}'
            if show_error:
                make_question(None, txt_error, 'Ошибка LOGIN', str(txt_z) + '\n' + txt, onlyok=True)
    return txt, result


def send_evt(number, form_parent, time_out_sleep=0):
    if form_parent is not None:
        evt = StatusOperation(number)
        QtCore.QCoreApplication.postEvent(form_parent, evt)
        if time_out_sleep > 0:
            time.sleep(time_out_sleep)


def send_rest_full(mes, dir="GET", params=None, lang='', show_error=True, tokenuser=None):
    js = {}
    if tokenuser is not None:
        js['token'] = tokenuser
    else:
        js['token'] = token  # токен при login
    if lang == '':
        lang = app_lang
    if dir == 'GET' and 'lang=' not in mes:
        if '?' in mes:
            mes = mes + '&lang=' + lang
        else:
            mes = mes + '?lang=' + lang
    else:
        js['lang'] = lang   # код языка пользователя
    if params:
        if type(params) is not str:
            params = json.dumps(params, ensure_ascii=False)
        js['params'] = params  # дополнительно заданные параметры
    try:
        headers = {"Accept": "application/json"}
        response = requests.request(dir, url + mes, headers=headers, json=js)
    except HTTPError as err:
        txt = f'HTTP error occurred: {err}'
        if show_error:
            make_question(None, txt, 'Ошибка запроса к RESTProxy', mes, onlyok=True)
        return txt, False, None
    except Exception as err:
        txt = f'Other error occurred: {err}'
        if show_error:
            make_question(None, txt, 'Ошибка запроса к RESTProxy', mes, onlyok=True)
        return txt, False, None
    else:
        if not response.ok and show_error:
            if params:
                params = json.loads(params)
                params = json.dumps(params, indent=4, ensure_ascii=False, sort_keys=True)
            else:
                params = ''
            make_question(None, response.text, str(response.status_code) + ' ' + response.reason,
                          mes + ' ' + dir + '\n' + str(params), onlyok=True)
        return response.text, response.ok, '<' + str(response.status_code) + '> - ' + response.reason


def send_rest(mes, directive="GET", params=None, lang='', show_error=True, tokenuser=None):
    txt, result, status_code = send_rest_full(
        mes, dir=directive, params=params, lang=lang, show_error=show_error, tokenuser=tokenuser)
    return txt, result


def row_only_read(row, mas_change=[]):
    for jj in range(0, len(row)):
        ind = row.__getitem__(jj)
        if ind and not (jj in mas_change):  # колонка не CHOOS
            ind.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)


def set_align(table, a_row, mas_fixed=[], align=QtCore.Qt.AlignRight):
    """
    установка выравнивания текста в колонках строки таблицы 0-го уровня
        :param table: таблица
    :param a_row: строка таблицы
    :param mas_fixed: массив индексов колонок, у которых выравнивание не меняется (остается left)
    :param align: тип выравнивания QtCore.Qt.AlignRight (по умолчанию) или QtCore.Qt.AlignCenter
    :return:
    """
    if type(table) == PyQt5.QtWidgets.QTreeView:
        model = table.model()
    else:
        model = table
    if a_row is not None:
        for j in range(model.columnCount()):
            if not (j in mas_fixed):  # колонка не меняет ориентации
                ind = model.index(a_row, j)
                model.setData(ind, align, QtCore.Qt.TextAlignmentRole)


def set_width_columns(table, mas_fixed_width=[], increment=20, last_column=False):
    """
    Задание ширины колонок
        :param table: таблица
        :param mas_fixed_width: индексы колонок, для которых ширина не устанавливается по размеру
        :param increment: добавка к ширине колонки по размеру
        :param last_column: признак наличия невидимой последней колонки
        :return:
    """
    for j in range(table.model().columnCount()):
        if not (j in mas_fixed_width):  # колонка не фиксированной ширины
            table.resizeColumnToContents(j)
            w = table.header().sectionSize(j)
            table.setColumnWidth(j, w + increment)
    if last_column:
        table.setColumnWidth(table.model().columnCount() - 1, 0)
    table.header().setStretchLastSection(False)


def get_index_row_in_table(model, value, col, value_child=''):  # model это  QStandardItemModel
    result = model.index(0, 0)
    try:
        for i in range(0, model.rowCount()):
            ind = model.index(i, col)
            if model.data(ind) == value:
                result = ind
                if value_child != '':
                    ind = model.index(i, 0)
                    item = model.itemFromIndex(ind)  # 0-го уровня заданной колонки (или 0-й колонки)
                    if item.hasChildren():  # найден 0-ой уровень и есть дети
                        for j in range(0, item.rowCount()):
                            ind = item.child(j).index()
                            if model.data(ind.sibling(ind.row(), col)) == value_child:
                                result = ind
                                break
                break
    except:
        pass
    return result


def show_message(self, txt, informative_text=None, detailed_text=None, onlyok=False, back_color=None):
    message_box = QMessageBox(self)
    if back_color is not None:
        message_box.setStyleSheet('background-color: ' + back_color + ';')
    message_box.setText(str(txt))
    if onlyok:
        message_box.setIcon(QMessageBox.Information)
    else:
        message_box.setIcon(QMessageBox.Question)
    if informative_text:
        message_box.setWindowTitle(informative_text)
    if detailed_text:
        message_box.setDetailedText(detailed_text)
    if onlyok:
        message_box.setStandardButtons(QMessageBox.Ok)
        message_box.setDefaultButton(QMessageBox.Ok)
    else:
        message_box.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
        message_box.setDefaultButton(QMessageBox.No)
    result = message_box.exec()
    return result == QMessageBox.Yes


def define_object(obj, layout, connect=None, enabled=True, icon=None, minimum=None, maximum=None, value=None, k=None):
    if connect is not None:
        if type(obj) == QPushButton:
            obj.clicked.connect(connect)
            if icon is not None:
                obj.setIcon(icon)
        elif type(obj) in [QSpinBox, QDoubleSpinBox]:
            obj.valueChanged.connect(connect)
        elif type(obj) == QCheckBox:
            obj.stateChanged.connect(connect)
        elif type(obj) == QComboBox:
            obj.currentIndexChanged.connect(connect)
            obj.setSizeAdjustPolicy(0)  # ширина по максимуму текстов
            obj.setMaxVisibleItems(20)
    if value is not None:
        if type(obj) in [QSpinBox, QDoubleSpinBox]:
            if value is not None:
                obj.setValue(value)
        elif type(obj) == QCheckBox:
            if value is not None:
                obj.setChecked(value)
        elif type(obj) == QComboBox:
            if value is not None:
                obj.setCurrentIndex(value)

    if minimum is not None:
        obj.setMinimum(minimum)
    if maximum is not None:
        obj.setMaximum(maximum)
    obj.setEnabled(enabled)
    if k is None:
        layout.addWidget(obj)
    else:
        layout.addWidget(obj, k)
    return obj


def valueBoolean(value, val1='true', val0='false'):
    if value:
        st = val1
    else:
        st = val0
    return st


def get_index(model, val, col, value_child=''):  # model это  QStandardItemModel
    result = model.index(0, 0)
    try:
        for i in range(0, model.rowCount()):
            ind = model.index(i, col)
            if model.data(ind) == val:
                result = ind
                if value_child != '':
                    ind = model.index(i, 0)
                    item = model.itemFromIndex(ind)  # 0-го уровня заданной колонки (или 0-й колонки)
                    if item.hasChildren():  # найден 0-ой уровень и есть дети
                        for j in range(0, item.rowCount()):
                            ind = item.child(j).index()
                            if model.data(ind.sibling(ind.row(), col)) == value_child:
                                result = ind
                                break
                break
    except:
        pass
    return result


def load_objects():
    global txt_error_connection, mas_json_objects
    data = None
    result = False
    if txt_error_connection == '':
        try:
            data, result = send_rest("v1/MDM/objects?usl=app_code='" + schema_name + "'")
            if result:
                mas_json_objects = json.loads(data)
            else:
                mas_json_objects = []
        except:
            pass
    return result, data


def get_text_from_answer(txt):
    result = txt.replace('[', '').replace(']', '').replace('"', '')
    return result.strip()


def value_from_array(value, mas_json):
    if not (value in mas_json):
        return None
    else:
        return mas_json[value]


def get_value_time(t):
    return t.hour * 3600 + t.minute * 60 + t.second + t.microsecond // 1000 / 1000


def translate_from_base(st):
    if st is not None:
        if type(st) == str:
            st = st.replace('~LF~', '\n').replace('~A~', '(').replace('~B~', ')').replace('~a1~', '@')
            st = st.replace('~a2~', ',').replace('~a3~', '=').replace('~a4~', '"').replace('~a5~', "'")
            st = st.replace('~a6~', ':').replace('~b1~', '/')
        return str(st)
    else:
        return ''


def translate_to_base(st):
    if st is not None:
        if type(st) == str:
            st = st.replace('\n', '~LF~').replace('(', '~A~').replace(')', '~B~').replace('@', '~a1~')
            st = st.replace(',', '~a2~').replace('=', '~a3~').replace('"', '~a4~').replace("'", '~a5~')
            st = st.replace(':', '~a6~').replace('/', '~b1~')
        return str(st)
    else:
        return ''


def decode(key, enc):
    dec = []
    enc = base64.urlsafe_b64decode(enc).decode()
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)


def is_user_admin():
    rights = decode(kirill, token)
    rights = json.loads(rights)
    if '***' in rights:
        return True
    else:
        return 'admin' in rights[schema_name]


def is_null(val, default=0):
    if not val:
        return default
    else:
        return val


def show_error_answer(ans, caption_text, detail_text='', onlyok=False):
    # определение ошибки в {"error": , "text": } и ее вывод
    result = True
    try:
        js = json.loads(ans)
        if 'error' in js:
            if js['error'] == 1:
                result = False
                QApplication.restoreOverrideCursor()  # вернуть нормальный курсор
                make_question(None, caption_text + ': ' + detail_text, caption_text, js['text'], onlyok)
        elif 'detail' in js:
            result = False
            QApplication.restoreOverrideCursor()  # вернуть нормальный курсор
            make_question(None, caption_text + ': ' + detail_text, caption_text, str(js), onlyok)
        elif 'error_sql' in js:
            result = False
            QApplication.restoreOverrideCursor()  # вернуть нормальный курсор
            make_question(None, caption_text + ': ' + detail_text, caption_text, str(js), onlyok)
    except Exception as err:
        result = False
        detail_text = detail_text + '\n' + f"{err}"
        QApplication.restoreOverrideCursor()  # вернуть нормальный курсор
        make_question(None, caption_text + ': ' + detail_text, caption_text, ans, onlyok)
    return result


def valFromMas(value, mas_json):
    if value in mas_json:
        return mas_json[value]


def get_boolean_from_dict(key, dict):
    """
    перевод величины из словаря (True, False или 1,0 или "True', "False") в булево значение
    :param key: - ключ параметра словаря со значением
    :param dict: - словарь
    :return: - значение указанного ключа словаря или False
    """
    if key in dict:
        value = dict[key]
        if type(value) == int:
            return value == 1
        elif type(value) == bool:
            return value
        elif type(value) == str:
            return value.upper() == 'TRUE'
        else:
            return False
    else:
        return False


def local_utc(local: datetime) -> datetime:
    """  Перевод local: datetime из локального времени в UTC: datetime """
    epoch = time.mktime(local.timetuple())
    offset = datetime.datetime.fromtimestamp(epoch) - datetime.datetime.utcfromtimestamp(epoch)
    return local - offset


def utc_local(utc: datetime) -> datetime:
    epoch = time.mktime(utc.timetuple())
    offset = datetime.datetime.fromtimestamp(epoch) - datetime.datetime.utcfromtimestamp(epoch)
    return utc + offset


def getTextfromAnswer(txt):
    result = txt.replace('[', '').replace(']', '').replace('"', '')
    return result.strip()


def getpole(txt, separator=';'):
    k = txt.partition(separator)
    return k[0], k[2]


def str1000(number, sep=' '):
    """
    вывод целого значения числа с разделением по тысячам (три знака) через указанную строку (по умолчанию - пробел)
        :param number: значение целого числа
    :param sep: - разделитель между тройками цифр
    :return: возвращается строка, типа 123 456 789
    """
    if number is None:
        return ''
    if type(number) == int or type(number) == str or type(number) == numpy.int32:
        n = str(number)[::-1]
        return sep.join(n[i:i+3] for i in range(0, len(n), 3))[::-1]
    return str(number)


def getInd(model, val, col, value_child=''):  # model это  QStandardItemModel
    result = model.index(0, 0)
    try:
        for i in range(0, model.rowCount()):
            ind = model.index(i, col)
            if model.data(ind) == val:
                result = ind
                if value_child != '':
                    ind = model.index(i, 0)
                    item = model.itemFromIndex(ind)  # 0-го уровня заданной колонки (или 0-й колонки)
                    if item.hasChildren():  # найден 0-ой уровень и есть дети
                        for j in range(0, item.rowCount()):
                            ind = item.child(j).index()
                            if model.data(ind.sibling(ind.row(), col)) == value_child:
                                result = ind
                                break
                break
    except:
        pass
    return result
