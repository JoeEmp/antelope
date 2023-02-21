import sys
import pytest
from unittest import TestCase
from com.error import ReportException, EmailException
from com.log import auto_logger
from com.cli import get_env_by_cli
from com.macro import *
from modules.global_value import GlobalValue
from modules.case import Case
from modules.case_executor import CaseExecutor
import fire
import os
from com.file import get_case_file_case, get_suite_case
from collections import deque
from set_all_by_user import SetUpAllByUser
import allure
from modules.report import MyReport
import shutil


class TestYamlCase():
    pass

def gen_all_case(cases, global_value, is_test, env, level):
    # TODO is_test 语法校验
    all_cases = []
    for case in cases:
        all_cases += Case(case, env, global_value=global_value, level=level)
    return all_cases


def show_all_cases(cases, logger):
    for case in cases:
        logger.info(case)


def ins_case_to_class(cases: list, test_case_class: TestCase, level):
    q = deque(cases)
    length = len(cases)

    def func(self):
        case = q.popleft()
        case_template, case_value, case_file_name = case
        self.__doc__ = case_file_name
        # 设置用例标题
        title = case_value._value['_title'] or case_file_name.replace('_template.yaml', '')
        allure.dynamic.title(title)
        if case_value['_module_path']:
            allure.dynamic.tag(case_value['_module_path'])
            allure.dynamic.story(case_value['_module_path'])
        else:
            allure.dynamic.tag('未定义模块')
            allure.dynamic.story('未定义模块')
        allure.dynamic.severity(case_value['_level'])
        allure.dynamic.description(case_value['_remark'])
        # 用例开始
        auto_logger.info('case %s' % case_template)
        auto_logger.info('case_value %s' % case_value)
        auto_logger.info('case begin run')
        auto_logger.info('-'*80)
        CaseExecutor(case, level).execute()
        auto_logger.info('-'*80)
        auto_logger.info('case end run')

    for i in range(length):
        setattr(test_case_class, 'test_%s' % (i), func)


def deal_args(reruns=0, reruns_delay=0, py_case=None, *arsg, **kwargs):
    """可选参数处理"""
    args = []
    if py_case:
        args += py_case
    if isinstance(reruns, int) and 0 < reruns:
        args += ['--reruns', reruns]
    if isinstance(reruns_delay, int) and 0 < reruns_delay:
        args += ['--reruns_delay', reruns_delay]
    return args


def main(case_file='', e='', t=False, num=None, g=GLOBAL_VALUE_FILENAME, level=DEF_LEVEL,
         reruns=0, reruns_delay=0, v='', debug=False, server_args=None, suite=None):
    """处理输入参数,并生成用例
    Args:
        case_file (str,optional): 文件或者目录, 运行指定的文件/目录的用例.
        e (str, optional):  环境, 用户指定用例参数的环境.
        t (bool, optional): 测试用例的语法错误和配置项缺失警告
        num (int, optional): 统计某个目录下的用例数量.
        g (str, optional): 环境变量的文件名, 默认为global_value.yaml.
        level (int, optional):优先级, 指定运行小于改优先级的用例.
        reruns (int, optional):  失败用例重跑次数.
        reruns_delay (int, optional): 重跑的间隔时间, 单位为秒. 
        version (str, optional): 版本针对不同版本有不同的用例(待定).
        suite (str, optional): 套件,指定运行用例, 方便部分回归
    """
    pytest_args = [__file__, '-s']
    ENV = e
    # 确认加载用例方式和获取用例路径
    yaml_case, py_case = [], []
    if suite:
        yaml_case, py_case = get_suite_case(suite)
    elif case_file:
        yaml_case, py_case = get_case_file_case(case_file)
    elif not suite and not case_file:
        print('未使用任何用例, 执行退出')
        auto_logger.warning('未使用任何用例, 执行退出')
        sys.exit(0)
    pytest_args += deal_args(
        reruns=reruns,
        reruns_delay=reruns_delay,
        py_case=py_case)
    # 避免pytest重复执行,只返回运行参数
    if "__main__" == __name__:
        # NOTE 删除旧的测试记录
        shutil.rmtree('temp', ignore_errors=FileNotFoundError)
        pytest_args += ['--alluredir', './temp']
        return pytest_args
    # 查找用例文件
    cases = yaml_case
    auto_logger.debug('all yaml cases: %s' % cases)
    # 全局变量初始化
    if os.path.exists(g) and os.path.isfile(g) and e:
        global_value = GlobalValue(g, e)
    else:
        global_value = GlobalValue('', e)
    auto_logger.info(global_value)
    # 用户自定义全局的前置操作
    SetUpAllByUser(global_value).execute()
    auto_logger.debug("after setup by user global value \n%s" %
                      global_value._value)
    # 生成用例
    all_cases = gen_all_case(cases, is_test=t, global_value=global_value, env=e, level=level)
    auto_logger.debug('all cases: %s' % all_cases)
    if 0 == len(all_cases):
        print('\n\n用例数量为0请检查%s(文件/目录)\n' % case_file)
    if num:
        print()
        print('-'*80)
        print('用例数量: ', len(all_cases))
        print('-'*80)
        pytest_args = []
    else:
        ins_case_to_class(all_cases, TestYamlCase, level)
    return pytest_args, server_args


def after_test(pytest_args):
    try:
        # 使用时间做报告文件名
        if '-debug' in pytest_args:
            allure_path, report_path = 'allure', 'debug'
        else:
            allure_path, report_path = 'allure', auto_logger.ts
        if os.path.exists(ERROR_SUITE % auto_logger.ts):
            print('存在错误用例, 回归命令如下')
            env = get_env_by_cli()
            if env:
                print('python3 runner.py -suite %s -e %s' %
                      (ERROR_SUITE % auto_logger.ts, env))
            else:
                print('python3 runner.py -suite %s' %
                      (ERROR_SUITE % auto_logger.ts))
            print('-'*80)
        MyReport(EMAIL_FILENAME, allure_path, report_path).send_mail()
    except ReportException as e:
        auto_logger.warning(e)
    except EmailException as e:
        auto_logger.warning(e)
    except Exception as e:
        auto_logger.error(e)


pytest_args = fire.Fire(main)

if "__main__" == __name__:
    # 执行用例
    pytest.main(pytest_args)
    after_test(pytest_args)