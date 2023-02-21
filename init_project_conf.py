
import os
from shutil import copyfile
import fire
from colorama import Fore, init

init(autoreset=True)


def green_print(s):
    print(Fore.GREEN + s)


macro_content = """# 枚举和宏定义
# 默认优先级
DEF_LEVEL = 99
# 全局变量
GLOBAL_VALUE_FILENAME = '%s'
# 邮件配置
EMAIL_FILENAME = '%s'
# 错误用例生成文件名格式
ERROR_SUITE = '%s_error_suite.yaml'
"""


def update_marco(global_value_path, email_conf_path):
    """更新宏"""
    with open(os.path.join('com', "macro.py"), 'w') as f:
        f.write(macro_content % (global_value_path, email_conf_path, '%s'))
        f.close()


def init_new_marco(global_value_path, email_conf_path):
    count = 0
    while True:
        if 0 == count:
            green_print('%s' % macro_content)
        question_str = "输入错误，请重新输入(Y/N)>" if 0 < count else "请确认宏定义内容是否正确,宏定义内容如上\n(Y/N)>"
        ans = input(question_str)
        if 'n' == ans.lower() or 'y' == ans.lower():
            break
        count += 1
    if 'n' == ans.lower():
        print('请手动更新 com/macro.py 文件')
        return
    update_marco(global_value_path, email_conf_path)


def init_dir(dir_name):
    if os.path.exists(dir_name):
        raise UserWarning('文件(夹)%s已存在，初始化失败' % dir_name)
    os.mkdir(dir_name)


def init_project_conf(dir_name):
    """初始化项目配置"""
    if str(dir_name).endswith('_case'):
        dirname = str(dirname)
    else:
        dir_name = str(dir_name) + '_case'
    global_value_path = os.path.join(dir_name, 'global_value.yaml')
    email_conf_path = os.path.join(dir_name, 'email_conf.yaml')
    init_dir(dir_name)
    copyfile('global_value.yaml', global_value_path)
    copyfile('email_conf.yaml', email_conf_path)
    init_new_marco(global_value_path, email_conf_path)
    init_cli(dir_name)


def init_cli(dir_name):
    key_line = "    case_root = 'tests' if t else '{}'"
    with open('cli.py', 'r') as f:
        lines = f.readlines()
    for index, line in enumerate(lines):
        if key_line.format('case') in line:
            lines[index] = key_line.format(dir_name)+'\n'
    with open('cli.py', 'w') as f:
        f.writelines(lines)


def reset_conf():
    update_marco('global_value.yaml', 'email_conf.yaml')


ipc = init_project_conf
reset = reset_conf

if "__main__" == __name__:
    fire.Fire()
