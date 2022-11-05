import common_data as cd


class TTypeParam:
    #  собственные свойства типа параметров
    id = None
    code = ''
    sh_name = ''
    info_code = None

    type_object_id = None
    type_data_id = None
    type_data_code = ''

    max_value = None
    min_value = None
    reference_object = None
    id_reference_object = None
    show_reference_object = None
    sort = None
    default_value = None
    check_text = ''
    category = None
    not_null = False
    description = ''
    code_key = ''
    code_ref = ''
    length = None

    is_private = None
    is_unique_index = None
    is_need_len = False
    is_pk = False

    def __init__(self, unit):
        self.id = unit["id"]
        self.code = unit["code"]
        self.sh_name = cd.valFromMas("name", unit)
        self.info_code = cd.valFromMas("info_code", unit)
        self.type_object_id = cd.valFromMas("object_id", unit)
        self.type_data_id = cd.valFromMas("data_id", unit)
        self.length = cd.valFromMas("len", unit)
        self.min_value = cd.valFromMas("min_val", unit)
        self.max_value = cd.valFromMas("max_val", unit)
        self.id_reference_object = cd.valFromMas("id_ref_object", unit)
        self.reference_object = cd.valFromMas("ref_object", unit)
        self.is_private = cd.get_boolean_from_dict("is_private", unit)
        self.is_pk = cd.get_boolean_from_dict("is_pk", unit)
        self.is_unique_index = cd.get_boolean_from_dict("is_unique_key", unit)
        self.show_reference_object = cd.get_boolean_from_dict("show_ref_object", unit)
        self.sort = cd.valFromMas("ordering_index", unit)
        self.check_text = cd.valFromMas("check_text", unit)
        self.not_null = cd.get_boolean_from_dict("not_null", unit)
        self.category = cd.valFromMas("categor", unit)
        self.code_ref = cd.valFromMas("code_ref", unit)
        self.code_key = cd.valFromMas("code_key", unit)
        self.type_data_code = cd.valFromMas("data_code", unit)
        self.description = cd.translate_from_base(cd.valFromMas("description", unit))
        self.default_value = cd.translate_from_base(cd.valFromMas("default_value", unit))
