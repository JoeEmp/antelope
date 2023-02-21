import pytest
from com.log import auto_logger, get_case_template_name
from com.file import write_error_suite


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    # 获取钩子方法的调用结果
    out = yield
    # print('用例执行结果', out)

    # 3. 从钩子方法的调用结果中获取测试报告
    report = out.get_result()
    if report.when == "call" and report.failed:
        case_template_name = report.fspath if 'runner.py' not in report.fspath else get_case_template_name(
            report.caplog)
        write_error_suite(case_template_name)
        auto_logger.info('case %s runing fail' % case_template_name)
        auto_logger.info('-'*80)
        auto_logger.info('case end run')
    elif report.when == "call" and report.skipped:
        auto_logger.info('case skip')
        auto_logger.info('-'*80)
        auto_logger.info('case end run')
