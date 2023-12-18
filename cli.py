import shutil
import sys
import fire
from modules.case import Case
from com.macro import GLOBAL_VALUE_FILENAME
import json
import os
import yaml
from com.file import YamlReader
from modules.step import STEP_TYPE
import xml.etree.ElementTree as et

def gen_case_value_context(global_value_file=GLOBAL_VALUE_FILENAME):
    all_env_conf = YamlReader.load_yaml_file(global_value_file)
    env_value_str = ':\n\n'.join(list(all_env_conf.keys())) + ':\n\n'
    return env_value_str + "value:\n  - title: '冒烟测试'"


def gen_case_template_context(path, url='', method='', host='', level='', headers='', body='', module=''):
    # TODO 直接与实现类关联
    d = {
        'request': {
            "method": method,
            'host': host,
            'url': url,
            'response_value_name': 'response'
        },
        'case': {"test_step": [{'request': 'request'}]},
        '_version': 2.0
    }
    if isinstance(level, int):
        d['level'] = level
    try:
        if body:
            body = json.loads(body.replace('\n', ''))
            d['request']['body'] = body
    except json.JSONDecodeError as e:
        print('%s文件请求体json转化错误' % path)
    try:
        if headers:
            headers = json.loads(headers.replace('\n', ''))
            d['request']['headers'] = headers
    except json.JSONDecodeError as e:
        print('%s文件请求体json转化错误,生成失败' % path)
    return yaml.dump(d, allow_unicode=True)


def gen_file(file, context):
    if os.path.exists(file):
        print('文件已存在无法写入')
        return
    with open(file, 'w', encoding='utf-8') as f:
        f.write(context)
        f.close()


def gen_template(path, module='', t=False, *args, **kwargs):
    """生成接口配置"""
    case_root = 'tests' if t else 'case'
    module_path = case_root + os.path.sep + module
    if module:
        full_path = module_path + os.path.sep + path
    else:
        full_path = module_path + path
    # 生成模板文件夹
    os.system('mkdir {}'.format(full_path))
    full_perfix = full_path + os.path.sep + path
    full_template_path = '{}{}{}_template.yaml'.format(
        full_path, os.path.sep, path)
    full_value_path = '{}{}{}_value.yaml'.format(
        full_path, os.path.sep, path)
    # 生成模板
    context = gen_case_template_context(full_template_path, *args, **kwargs)
    with open(full_template_path, 'w') as f:
        f.write(context)
    # 生成用例变量的内容
    context = gen_case_value_context()
    with open(full_value_path, 'w') as f:
        f.write(context)
    # NOTE 和接口测试耦合，故注释
    # os.system('touch {}'.format(Case.check_file_name.format(full_perfix)))
    # os.system('touch {}'.format(Case.schema_file_name.format(full_perfix)))


def show_yaml_dict(yaml_file):
    with open(yaml_file, encoding='utf-8') as f:
        d = yaml.safe_load(f.read())
        f.close()
        ds = json.dumps(d, sort_keys=True, indent=4, separators=(',', ':'))
        print(ds)


def gen_code_snippet(filename='antelope.json.code-snippets'):
    if 'darwin' == sys.platform.lower():
        home = os.popen('echo $HOME').read().replace('\n', '')
        filename = os.path.join(
            '%s/Library/Application Support/Code/User/snippets/' % home, filename)
    # NOTE windows 标准太多，这段代码写的太烂
    elif 'win32' == sys.platform.lower():
        shell = os.popen('echo $SHELL').read()
        is_unix_style = os.popen('pwd').read().startswith('/')
        # bash
        if is_unix_style:
            home = os.environ['HOME']
            filename = home + '/AppData/Roaming/Code/User/snippets/%s' % filename
        else:
            # cmd
            if '$SHELL' in shell:
                home = os.popen('echo %USERPROFILE%').read().replace('\n', '')
            # power shell
            else:
                home = os.popen('echo $HOME').read().replace('\n', '')
            # NOTE os.path.join 有问题，以后研究
            filename = home + '\\AppData\\Roaming\\Code\\User\\snippets\\%s' % filename
    print(filename)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(gen_snippet())


def gen_pychram_live_template(filename='antelope.xml'):
    # https://www.jetbrains.com/help/pycharm/sharing-live-templates.html
    # pycharm 每个版本都有自己的配置，采取全部更新策略
    xml_tree = gen_live_template()
    if 'darwin' == sys.platform.lower():
        # MacOS
        home = os.popen('echo $HOME').read().replace('\n', '')
        perfix = f'{home}/Library/Application Support/JetBrains'
        for root, dirs, file in os.walk(perfix):
            for d in dirs:
                full_template_path = os.path.join(perfix, d, 'templates')
                if 'pycharm' in d.lower() and os.path.exists(full_template_path):
                    filename = os.path.join(full_template_path, filename)
                    xml_tree.write(filename, 'utf-8', xml_declaration=True)
                    print(filename)
            break
    elif 'win32' == sys.platform.lower():
        # window
        # C:\Users\aitest\AppData\Roaming\JetBrains\PyCharmCE2023.1\templates
        # C:\Users\aitest\AppData\Roaming\JetBrains\PyCharmxxx\templates
        print('windows')
        shell = os.popen('echo $SHELL').read()
        is_unix_style = os.popen('pwd').read().startswith('/')
        # bash
        if is_unix_style:
            home = os.environ['HOME']
            perfix = f'{home}/AppData/Roaming/JetBrains'
            for root, dirs, file in os.walk(perfix):
                for d in dirs:
                    full_template_path = os.path.join(perfix, d, 'templates')
                    if 'pycharm' in d.lower() and os.path.exists(full_template_path):
                        filename = os.path.join(full_template_path, filename)
                        xml_tree.write(filename, 'utf-8', xml_declaration=True)
                        print(filename)
        else:
            # cmd
            if '$SHELL' in shell:
                home = os.popen('echo %USERPROFILE%').read().replace('\n', '')
            # power shell
            else:
                home = os.popen('echo $HOME').read().replace('\n', '')
            perfix = f'{home}\\AppData\\Roaming\\JetBrains'
            for root, dirs, file in os.walk(perfix):
                for d in dirs:
                    full_template_path = f'{perfix}\\{d}\\templates'
                    if 'pycharm' in d.lower() and os.path.exists(full_template_path):
                        filename = f'{full_template_path}\\{filename}'
                        xml_tree.write(filename, 'utf-8', xml_declaration=True)
                        print(filename)
    else:
        print('该系统未支持')
    xml_tree.write('antelope_live_template.xml', 'utf-8', xml_declaration=True)


def gen_live_template():
    """生成IDEA的live template
    结构例子:
    <templateSet group="user">
      <template name="set_step" value="- set_step:&#10;    name:&#10;    value:" description="" toReformat="false" toShortenFQNames="true">
        <context>
          <option name="OTHER" value="true" />
        </context>
      </template>
      <template name="set_value" value="- set_value:&#10;    name:&#10;    value:" description="" toReformat="false" toShortenFQNames="true">
        <context>
          <option name="OTHER" value="true" />
        </context>
      </template>
    </templateSet>
    """

    def gen_template_ele(parent: et.Element, name: str, value: str) -> et.ElementTree:
        if value:
            body_lines = value.split('\n')
            body_lines = [body_line for body_line in body_lines if body_line]
            unuse_sep_len = len(body_lines[0]) - len(body_lines[0].lstrip(' '))
            value = value.replace(' '*unuse_sep_len, '').lstrip(os.linesep)
        template = et.SubElement(parent, 'template', {
            'name': name,
            'value': value,
            'description': '',
            'toReformat': 'false',
            'toShortenFQNames': 'true'
        })
        return template

    template_set = et.Element('templateSet')
    template_set.set('group', 'antelope')
    for name, body_text, desc in get_snippet():
        template = gen_template_ele(template_set, name, body_text)
        context = et.SubElement(template, 'context')
        option = et.SubElement(context, 'option', {
            'name': 'OTHER',
            'value': 'true'
        })
    return et.ElementTree(template_set)


def gen_snippet():
    snippet_dict = {}
    for prefix, body_text, desc in get_snippet():
        desc = desc if desc else ''
        body_lines = body_text.split('\n')
        body_lines = [body_line for body_line in body_lines if body_line]
        if body_lines:
            unuse_sep_len = len(body_lines[0]) - len(body_lines[0].lstrip(' '))
            body_lines = [body_line[unuse_sep_len:] for body_line in body_lines if body_line]
        snippet_dict[prefix] = {
            'prefix': prefix,
            "scope": 'yaml',
            'body': body_lines,
            'description': desc
        }
    return json.dumps(snippet_dict, ensure_ascii=False, indent=4, separators=(',', ': '))


def get_snippet() -> tuple:
    for i in STEP_TYPE:
        if hasattr(i.value, 'snippet') and i.value.snippet():
            yield i.name, *i.value.snippet()


def clear_data():
    shutil.rmtree(os.path.join('report'), ignore_errors=FileNotFoundError)
    shutil.rmtree(os.path.join('suite'), ignore_errors=FileNotFoundError)
    shutil.rmtree(os.path.join('log'), ignore_errors=FileNotFoundError)
    os.mkdir('report')
    os.mkdir('suite')
    os.mkdir('log')


gt = gen_template
gs = gen_snippet
lt = gen_live_template
gsvscode = gen_code_snippet
gspycha = gen_pychram_live_template

if "__main__" == __name__:
    fire.Fire()