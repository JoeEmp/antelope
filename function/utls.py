import hashlib
from time import time_ns


def run_lambda(case_value, lambda_str):
    """执行 lambda表达式"""
    case_value['lambda_result'] = eval(lambda_str)
    return case_value['lambda_result']