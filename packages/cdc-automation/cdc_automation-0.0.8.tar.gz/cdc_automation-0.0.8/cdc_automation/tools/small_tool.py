from threading import Timer
from functools import reduce
import operator
import jsonschema
import re
import random
import string


def json_schema_validate(data: dict, schema: dict, index=""):
    """
    Validate an instance data under the given schema

    :param data: response json as dict
    :param schema: api json schema as dict
    :param index: input data index for trace used, example: userId
    """
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())

    errors = validator.iter_errors(data)
    schema_errors = ""
    for error in errors:
        schema_errors += f"\n{error.absolute_path}, {error.message}, {index}"
    if schema_errors:
        # raise jsonschema.ValidationError(schema_errors)
        raise AssertionError(schema_errors)


def find_column(sheet, index_row, find_str):
    for cell in sheet[str(index_row)]:
        if find_str == cell.value:
            return cell


def str_gen(char=string.ascii_letters + string.digits, size=20):
    return ''.join(random.choices(char, k=size))


class RepeatingTimer(Timer):
    def run(self):
        self.finished.wait(self.interval)
        while not self.finished.is_set():
            self.function(*self.args, **self.kwargs)
            self.finished.wait(self.interval)


class DictTool:
    @staticmethod
    def transfer_json_path(path: str):
        """
        transfer json path to list
        :param path: json path, ex: "TRANRS[0].district[0].districtName"
        :return: list of json path , ex: ['TRANRS', 0, 'district', 0, 'districtName']
        """
        return [int(s) if s.isdigit() else s for s in re.split(r"\.", re.sub(r"\[(\d+)]", r".\g<1>", path))]

    @classmethod
    def get_by_path(cls, root: dict, items: list):
        """
        Access a nested object in root by item sequence.
        :param root: api request payload as dict format
        :param items: key path, ex: ['TRANRS', 0, 'district', 0, 'districtName']
        :return:
        """
        return reduce(operator.getitem, items, root)

    @classmethod
    def set_by_path(cls, root: dict, items: list, value):
        """
        Set a value in a nested object in root by item sequence.
        :param root: api request payload as dict format
        :param items: key path, ex: ['TRANRS', 0, 'district', 0, 'districtName']
        :param value: value of key that you want to set
        :return:
        """
        cls.get_by_path(root, items[:-1])[items[-1]] = value
