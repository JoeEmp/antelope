import sys
import fire
from modules.case import Case
from com.macro import GLOBAL_VALUE_FILENAME
import json
import os
import yaml
from com.file import YamlReader
from modules.step import STEP_TYPE


def gen_case_value_context(global_value_file=GLOBAL_VALUE_FILENAME):
    all_env_conf = YamlReader.load_yaml_file(global_value_file)
    env_value_str = ':\n\n'.join(list(all_env_conf.keys())) + ':\n\n'
    return env_value_str+"value:\n  - title: '冒烟测试'"


def gen_case_template_context(path, url='', method='', host='', level='', headers='', body='', module=''):
    # TODO 直接与实现类关联
    d = {
        'request': {
            "method": method,
            'host': host,
            'url': url,
            'response_value_name': 'response'
        },
        'case': [{'request': 'request'}]
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
    os.system('touch {}'.format(Case.check_file_name.format(full_perfix)))
    os.system('touch {}'.format(Case.schema_file_name.format(full_perfix)))


def show_yaml_dict(yaml_file):
    with open(yaml_file, encoding='utf-8') as f:
        d = yaml.safe_load(f.read())
        f.close()
        ds = json.dumps(d, sort_keys=True, indent=4, separators=(',', ':'))
        print(ds)


def gen_code_snippet(filename='xw_auto_test.json.code-snippets'):
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


def gen_pychram_snippet():
    # https://www.jetbrains.com/help/pycharm/sharing-live-templates.html
    pass


def gen_snippet():
    snippet_dict = {}
    for prefix, body_text, desc in get_snippet():
        desc = desc if desc else ''
        body_lines = body_text.split('\n')
        body_lines = [body_line for body_line in body_lines if body_line]
        if body_lines:
            unuse_sep_len = len(body_lines[0]) - len(body_lines[0].lstrip(' '))
            body_lines = [body_line[unuse_sep_len:]
                          for body_line in body_lines if body_line]
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


gt = gen_template
gs = gen_snippet
gsvscode = gen_code_snippet
gspycha = gen_pychram_snippet

if "__main__" == __name__:
    fire.Fire()
    # show_yaml_dict('./demo_case/aiot_login_min/aiot_login_min_template.yaml')
