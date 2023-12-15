from abc import ABCMeta, abstractmethod
import yaml
import json
from json.decoder import JSONDecodeError
from genson import SchemaBuilder
from com.error import YamlSyntaxException, AutoTestException
from jsonschema.exceptions import ValidationError
from jsonschema.validators import validate
from com.macro import ERROR_SUITE
from com.log import auto_logger, time_str
import os
import re


class JsonCheck(metaclass=ABCMeta):

    def json_to_schema(self, to_schema_json, model='normal') -> dict:
        """json 转 json schema"""
        return json_to_schema(to_schema_json, model)

    @abstractmethod
    def data_check(self, value, template, msg=''):
        """参数校验"""
        template_schema = self.json_to_schema(template)
        auto_logger.debug(f'schema by templdate: {template_schema}')
        auto_logger.debug(f'validate value: {value}')
        try:
            result = validate(instance=value, schema=template_schema)
        except ValidationError as e:
            msg = msg or 'json错误'
            raise AutoTestException(msg)


class YamlReader(JsonCheck):

    def data_check(self, value, template, msg=''):
        return super().data_check(value, template, msg=msg)

    @staticmethod
    def load_yaml_file(file: str) -> object:
        """获取yaml文件内容并返回。"""
        try:
            with open(file, encoding='utf-8') as f:
                file_str = f.read().replace('\t', '')
                result = yaml.safe_load(file_str)
                f.close()
                return result
        except FileNotFoundError:
            raise FileNotFoundError('文件%s未找到' % file)
        except yaml.reader.ReaderError:
            raise YamlSyntaxException('%s文件解码错误' % file)
        except UnicodeDecodeError as e:
            raise YamlSyntaxException('%s文件编码错误' % file)
        except yaml.parser.ParserError as e:
            raise YamlSyntaxException('yaml语法错误,文件为[%s]' % file)
        except Exception as e:
            auto_logger.error('%s:%s' % (type(e), e))
            raise AutoTestException('未定义异常,请联系开发者,异常文件[%s]' % file)


def load_json(file):
    result = None
    try:
        with open(file, 'r', encoding='utf-8') as f:
            result = json.loads(f.read())
    except FileNotFoundError:
        auto_logger.error('{}文件路径错误'.format(file))
    except JSONDecodeError:
        auto_logger.error('%s,文件格式错误' % file)
    except Exception as e:
        auto_logger.error(e)
    finally:
        return result


def get_dir_case(dir_path) -> list:
    """
    找出文件夹内的用例
    case
      - a
        - a.yaml
        - a_value.yaml
      -b
        - b_value.yaml
        - b_value_value.yaml
      -c
        - c.yaml
      -d
        - d_value.yaml
    return ['case/a/a.yaml','case/b/b_value.yaml','case/c/c.yaml']
    """
    yaml_case, py_case = [], []
    yaml_suffix = '_template.yaml'
    py_suffix = '.py'
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            fullname = os.path.join(root, file)
            if fullname.endswith(yaml_suffix):
                yaml_case.append(fullname)
            elif fullname.endswith(py_suffix):
                py_case.append(fullname)
    return yaml_case, py_case


def get_suite_case(suite_file):
    cases = YamlReader.load_yaml_file(suite_file)
    yaml_case, py_case = [], []
    for case in cases:
        yaml_case1, py_case1 = get_case_file_case(case)
        yaml_case += yaml_case1
        py_case += py_case1
    return yaml_case, py_case


def get_case_file_case(case_file):
    yaml_case, py_case = [], []
    if os.path.isfile(case_file):
        if case_file.endswith('.py'):
            py_case.append(case_file)
        else:
            yaml_case.append(case_file)
    elif os.path.isdir(case_file):
        yaml_case, py_case = get_dir_case(case_file)
    return yaml_case, py_case


def is_valid_regex(pattern):
    try:
        re.compile(pattern)
        return True
    except re.error:
        return False


def json_to_schema(to_schema_json, model='normal') -> dict:
    """
    将 JSON 转换为 JSON Schema

    参数：
    - to_schema_json：待转换的 JSON 数据
    - model：模式选择，可选值为 'normal'（默认）或 'pattern'(正则)

    返回：
    生成的 JSON Schema
    """

    builder = SchemaBuilder('http://json-schema.org/draft-07/schema#')
    builder.add_object(to_schema_json)
    sch = builder.to_schema()
    if 'pattern' == model:
        sch['patternProperties'] = sch.pop('properties')
        sch['required'] = [key for key in sch['required']
                           if not is_valid_regex(key)]
    return sch


def gen_yaml(filename, content):
    yaml_str = yaml.dump(content, default_flow_style=True)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(yaml_str)
        f.close()
    return filename


def write_error_suite(case_file_name, filename=''):
    filename = filename or ERROR_SUITE % time_str
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            content = yaml.safe_load(f.read())
            f.close()
        if case_file_name not in content:
            content.append(case_file_name)
    else:
        content = [case_file_name]
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(yaml.dump(content, default_flow_style=True))