import common_data as cd
import json
from PyQt5.QtWidgets import (QApplication)


class TypeObject:
    id = None
    sh_name = ''
    code = ''
    description = ''
    sort = None
    parent_id = None
    parent_code = ''
    isbaseclass = 0
    parent = None
    masspaces = []
    amasspaces = []
    # app_id = None

    def __init__(self, fcode='', fid=None, fsh_name=None, fsort=None, fparent_id=None, fparent_code='',
                 fdescription='', fisbaseclass="False", fisrelation="False"):
        # super(object, self).__init__()
        # if (fisbaseclass == False) or (fisbaseclass.lower() == 'false'):
        #     fisbaseclass = 0
        self.id = fid
        self.code = fcode
        self.description = cd.translate_from_base(fdescription)
        self.sh_name = fsh_name
        self.sort = fsort
        self.parent_id = fparent_id
        self.parent_code = fparent_code
        self.isbaseclass = fisbaseclass.upper() == 'TRUE'
        self.isrelation = fisrelation.upper() == 'TRUE'
        # self.app_id = cd.get_app_id(cd.schemaname)
        self.masspaces = []
        self.amasspaces = []
    # сохранить исходные значения
        self.aid = fid
        self.acode = fcode
        self.adescription = cd.translate_from_base(fdescription)
        self.ash_name = fsh_name
        self.asort = fsort
        self.aparent_id = fparent_id
        self.aparent_code = fparent_code
        self.aisbaseclass = self.isbaseclass
        self.aisrelation = self.isrelation
        self.amasspaces = list(self.masspaces)

    def refresh(self):
        self.id = self.aid
        self.description = self.adescription
        self.sh_name = self.ash_name
        self.sort = self.asort
        self.code = self.acode
        self.parent_id = self.aparent_id
        self.parent_code = self.aparent_code
        self.isbaseclass = self.aisbaseclass
        self.isrelation = self.aisrelation
        self.masspaces = list(self.amasspaces)

    def update(self):
        self.aid = self.id
        self.adescription = self.description
        self.ash_name = self.sh_name
        self.asort = self.sort
        self.acode = self.code
        self.aparent_id = self.parent_id
        self.aisbaseclass = self.isbaseclass
        self.aisrelation = self.isrelation
        self.amasspaces = list(self.masspaces)

    def make_namespaces(self, namespaces):
        self.masspaces = []
        self.amasspaces = []
        for mas in namespaces:
            self.masspaces.append(str(mas['code']))
        self.amasspaces = list(self.masspaces)

    def inc_namespace(self, code):
        if code not in self.masspaces:
            self.masspaces.append(code)

    def del_namespace(self, code):
        if code in self.masspaces:
            for j in range(0, len(self.masspaces)):
                if self.masspaces[j] == code:
                    self.masspaces.pop(j)
                    break

    def is_namespace(self, ns_id, mas):
        return str(ns_id) in mas

    def isNeedToSave(self):
        if not self.id:
            result = cd.get_text('Нов', id_text=34, key='main')
        elif (self.description != self.adescription) or \
                (self.sh_name != self.ash_name) or \
                (self.code != self.acode) or \
                (self.isbaseclass != self.aisbaseclass) or \
                (self.isrelation != self.aisrelation) or \
                (self.parent_id != self.aparent_id) or \
                (self.sort != self.asort) or \
                (self.what_change_ns() != ''):
            result = cd.get_text('Изм', id_text=31, key='main')
        else:
            result = ''
        return result

    def whatChange(self):
        result = ''
        LF = '\n'
        if self.sh_name != self.ash_name:
            result = result + cd.get_text('Название', id_text=2, key='object') + ': ' + \
                     cd.isNull(self.ash_name, '') + ' --> ' + self.sh_name + LF
        if self.description != self.adescription:
            result = result + cd.get_text('Комментарий', id_text=26, key='main') + ': ' + \
                     ' --> ' + self.description + LF
        if self.code != self.acode:
            result = result + cd.get_text('Код', id_text=1, key='object') + ': ' + \
                     cd.isNull(self.acode, '') + ' --> ' + self.code + LF
        if self.isbaseclass != self.aisbaseclass:
            result = result + cd.get_text('Базовый класс', id_text=3, key='object') + ': ' + \
                     cd.valueBoolean(self.aisbaseclass) + ' --> ' + cd.valueBoolean(self.isbaseclass) + LF
        if self.isrelation != self.aisrelation:
            result = result + cd.get_text('Отказ от фиксации изменений', id_text=4, key='object') + ': ' + \
                     cd.valueBoolean(self.aisrelation) + ' --> ' + cd.valueBoolean(self.isrelation) + LF
        if self.parent_id != self.aparent_id:
            result = result + cd.get_text('Родитель', id_text=5, key='object') + ': ' + \
                     str(cd.isNull(self.aparent_id, 0)) + ' --> ' + str(self.parent_id) + LF
        if self.sort != self.asort:
            result = result + cd.get_text('Сортировка', id_text=6, key='param') + ': ' + \
                     str(cd.isNull(self.asort, 0)) + ' --> ' + str(self.sort) + LF
        result = result + self.what_change_ns()
        return result

    def what_change_ns(self):
        LF = '\n'
        result = ''
        for j in range(0, len(self.masspaces)):
            if not self.is_namespace(self.masspaces[j], self.amasspaces):
                result = result + 'insert namespace: ' + self.masspaces[j] + LF
        for j in range(0, len(self.amasspaces)):
            if not self.is_namespace(self.amasspaces[j], self.masspaces):
                result = result + 'DELETE namespace: ' + self.amasspaces[j] + LF
        return result

    def whatError(self):
        result = ''
        LF = '\n'
        if self.code == '':
            result = result + cd.get_text('Необходимо задание кода типа объекта', id_text=9, key='object') + LF
        if not self.sh_name or (self.sh_name == ''):
            result = result + cd.get_text('Необходимо задание имени типа объекта', id_text=10, key='object') + LF
        return result

    def save(self):
        param = {}
        param['code'] = self.code.lower()
        param['name'] = self.sh_name
        param['description'] = cd.translate_to_base(self.description)
        param['is_base_class'] = str(self.isbaseclass)
        param['is_relation'] = str(self.isrelation)
        param['ordering_index'] = self.sort
        param['parent_code'] = self.parent_code
        param['object_code'] = self.code
        param['app_code'] = cd.schemaname
        nss = []
        for i in range(0, len(self.masspaces)):
            ns = {}
            ns['code'] = str(self.masspaces[i])
            nss.append(ns)
        param['namespaces'] = nss
        ans, result = cd.send_rest('v1/MDM/objects', 'POST', params=param)
        if result:
            js = json.loads(ans)[0]
            if 'id' in js:
                self.id = int(js['id'])
        return result
