import logging
from datetime import datetime
import sys
from colorama import Fore, init
import re

init(autoreset=True)


def init_logging(perfix: str, level=logging.INFO):
    if not isinstance(perfix, str):
        logging.error('loger init fail')
        return
    if 'debug' not in perfix:
        perfix = 'executor'
    logger = logging.getLogger(perfix)
    logger.ts = time_str
    if logger.handlers:
        return logger
    fh = logging.FileHandler("log/{}.log".format(
        time_str), encoding="utf-8", mode="a")
    formatter = logging.Formatter(
        "%(asctime)s - runner -%(levelname)s %(filename)s:%(lineno)d %(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.setLevel(level)
    logger.info('runner is start')
    return logger


def error_print(s):
    print(Fore.RED + s)


def warning_print(s):
    print(Fore.YELLOW + s)


def get_case_template_name(caplog):
    pattern = re.compile(r"CaseTemplate\('.+?'\)")
    search = pattern.search(caplog)
    if search:
        begin, end = search.span()
        return caplog[begin+len("CaseTemplate('"):end-len("')")]
    else:
        auto_logger.warning('获取用例模版文件名失败')
        return ''


time_str = None
if '-debug' in sys.argv:
    time_str, level = 'debug', logging.DEBUG
elif not time_str:
    time_str, level = datetime.now().strftime('%Y%m%d_%H%M%S'), logging.INFO

# 日志初始化
auto_logger = init_logging(time_str, level)
