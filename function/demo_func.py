from com.log import auto_logger


def hello_world():
    auto_logger.info('test func')


def echo_name(name, **kwargs):
    auto_logger.info('someone call {}'.format(name))


def echo_case_value1(**kwargs):
    auto_logger.info("echo case_value %s" % kwargs['case_value'])


def echo_case_value2(case_value, **kwargs):
    auto_logger.info("echo case_value %s" % case_value)


def echo_strcat_name(first, second, name, case_value):
    auto_logger.info("%s-%s-%s" % (first, name, second))
    return "%s-%s-%s" % (first, name, second)