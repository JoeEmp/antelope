import sys
 
 
def get_param_by_cli(key: str) -> str:
    """获取环境变量"""
    try:
        param = sys.argv[sys.argv.index('-'+key.strip('-')) + 1]
    except ValueError:
        param = ''
    return param
 
 
def get_env_by_cli():
    """获取环境变量"""
    return get_param_by_cli('-e')
 
 
def get_to_addr_by_cli():
    """获取环境变量"""
    to_addrs = get_param_by_cli('-to_addrs')
    if to_addrs:
        return to_addrs.rstrip(',').split(',')
    else:
        return []
 
def get_suite_by_cli():
    """获取环境变量"""
    return get_param_by_cli('-suite')

def get_case_version_by_cli():
    return get_param_by_cli('-case_version')


def get_case_version_by_cli():
    is_api_case = get_param_by_cli('-api_case')
    if is_api_case.lower() in ['false','true']:
        return eval(is_api_case.capitalize())
    else:
        raise ValueError('api_case 命令行参数错误')