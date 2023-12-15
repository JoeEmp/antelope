# 回归测试脚本
import json
import logging
import os
from pprint import pprint
import sqlite3
from time import sleep
from com.allure_api import AllureApi
from colorama import Fore, init

init(autoreset=True)

def pass_print(s):
    print(Fore.GREEN + s)

def error_print(s):
    print(Fore.RED + s)


def normal_print(s):
    print(Fore.BLUE + s)


module_path_allure_status_map = {
    'abort': 'broken',
    'fail': 'failed',
    'pass': 'passed',
    'skip': 'skipped'
}

allure_status_module_path__map = {v: k for k,
                                  v in module_path_allure_status_map.items()}


def init_env():
    # 开启服务
    os.system('nohup python3 simple_server.py &')
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
        print('需要人工检查测试结果')
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
            print(case)
            logging.exception(e)
            raise ValueError(f'allure文件解析失败,请检查文件"{allure_behaviors}"')
        return error_cases


def teardown_env():
    os.system(
        """ ps -ef | grep "simple_server.py" | awk -F " " '{print "kill -9 " $2}' | sh """)
    if os.path.exists('regression_test.db'):
        os.remove('regression_test.db')


def flow(allure_path='allure'):

    try:
        normal_print('环境准备')
        init_env()
        os.system('source venv/bin/activate && python3 runner.py tests/interpreter_case/ -e demo')
        error_cases = check(allure_path)
        print()
        print('-'*100)
        normal_print('开始自检')
        if error_cases:
            error_print('存在错误用例')
            pprint(error_cases)
        else:
            pass_print('无错误用例')
    except Exception as e:
        logging.exception(e)
    finally:
        normal_print('完成测试')
        normal_print('环境清理')
        teardown_env()



flow()
