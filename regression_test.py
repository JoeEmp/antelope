# 回归测试脚本
import json
import logging
import os
from pprint import pprint
import sqlite3
import sys
from com.allure_api import AllureApi
from colorama import Fore, init

is_win32 = True if 'win32' == sys.platform.lower() else False

init(autoreset=True)

def pass_print(s, *args, **kwargs):
    print(Fore.GREEN + s, *args, **kwargs)


def error_print(s, *args, **kwargs):
    print(Fore.RED + s, *args, **kwargs)


def normal_print(s, *args, **kwargs):
    print(Fore.CYAN + s, *args, **kwargs)


def warning_print(s, *args, **kwargs):
    print(Fore.YELLOW + s, *args, **kwargs)


module_path_allure_status_map = {
    'abort': 'broken',
    'fail': 'failed',
    'pass': 'passed',
    'skip': 'skipped'
}

allure_status_module_path__map = {v: k for k,
                                  v in module_path_allure_status_map.items()}


def start_http_server():
    if not is_win32:
        os.system(""" ps -ef | grep "simple_server.py" | awk -F " " '{print "kill -9 " $2}' | sh """)
    else:
        os.system('taskkill /pid 10086 -F')

def kill_http_server():
    if not is_win32:
        os.system(""" ps -ef | grep "simple_server.py" | awk -F " " '{print "kill -9 " $2}' | sh """)
    else:
        os.system('taskkill /pid 10086 -F')
        

def init_env():
    normal_print('开启测试服务')
    if 'win32' == sys.platform.lower():
        os.system('start /min python3 simple_server.py')
    else:
        os.system('nohup python3 simple_server.py &')
    normal_print('创建测试数据库')
    conn = sqlite3.connect('regression_test.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE COMPANY
           (ID INT PRIMARY KEY     NOT NULL,
           NAME           TEXT    NOT NULL,
           AGE            INT     NOT NULL,
           ADDRESS        CHAR(50),
           SALARY         REAL);''')
    conn.commit()
    conn.close()


def check(allure_path='allure'):
    error_cases = []
    allure_behaviors = 'report/last/data/behaviors.json'
    if not AllureApi(allure_path).has_env:
        warning_print('未安装allure,需要人工检查测试结果')
        return
    elif not os.path.exists(allure_behaviors):
        raise FileNotFoundError('报告生成异常')
    else:
        with open(allure_behaviors) as f:
            details = json.loads(f.read())
        behaviors = details.get('children', [])
        try:
            for behavior in behaviors:
                status, cases = behavior['name'], behavior['children']
                if status in module_path_allure_status_map:
                    for case in cases:
                        try:
                            assert case['status'] == module_path_allure_status_map[status], ''
                        except AssertionError:
                            error_cases.append('case执行结果为%s不符合预期%s,用例名称为%s' % (
                                case['status'], module_path_allure_status_map[status], case['name']))
                elif status == '未定义模块':
                    for case in cases:
                        try:
                            assert allure_status_module_path__map[case['status']
                                                                  ] in case['name']
                        except AssertionError:
                            error_cases.append('case执行结果为%s不符合预期,用例名称为%s' % (
                                allure_status_module_path__map[case['status']], case['name']))
        except KeyError as e:
            logging.exception(e)
            raise ValueError(f'allure文件解析失败,请检查文件"{allure_behaviors}"')
        return error_cases


def teardown_env():
    normal_print('关闭测试服务', end='、')

    normal_print('清理临时数据库')
    if os.path.exists('regression_test.db'):
        os.remove('regression_test.db')


def flow(allure_path='allure'):

    try:
        normal_print('环境准备')
        init_env()
        normal_print('开始执行测试')
        os.system(
            'source venv/bin/activate && coverage run runner.py tests/interpreter_case/ -e demo')
        normal_print('完成测试')
        print()
        print('-'*100)
        normal_print('开始框架自检:')
        error_cases = check(allure_path)
        if error_cases:
            error_print('存在错误用例')
            pprint(error_cases)
        else:
            pass_print('无错误用例')
    except Exception as e:
        logging.exception(e)
        error_print(e)
    finally:
        normal_print('结束框架自检')
        normal_print('开始环境清理:')
        teardown_env()


flow()
