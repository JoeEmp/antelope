import sys


def get_env_by_cli():
    """获取环境变量"""
    try:
        env = sys.argv[sys.argv.index('-e') + 1]
    except ValueError:
        env = ''
    return env
