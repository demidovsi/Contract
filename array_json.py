"""
Использование параметров из массива JSON
"""


class TArrayJson:
    json_array = None

    def __init__(self, json_params):
        self.json_array = json_params

    def get_count(self):
        return len(self.json_array)

    def is_exist(self, index, key):
        return index < self.get_count() and key in self.json_array[index]

    def get_value(self, index, code):
        if self.is_exist(index, code):
            return self.json_array[index][code]

    def get_unit(self, index):
        if index < self.get_count():
            return self.json_array[index]
