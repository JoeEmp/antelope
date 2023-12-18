from com.error import FunctionException


def mysql_page(case_value, page, page_size):
    if not page and not page_size:
        case_value['page_sql'] = 'limit 0'
    offset, size = page_size*page-page_size, page_size
    case_value['page_sql'] = 'limit %s,%s' % (offset, size)


def pg_page(case_value, page, page_size):
    if not page and not page_size:
        case_value['page_sql'] = 'limit 0'
    offset, size = page_size*page-page_size, page_size
    case_value['page_sql'] = 'limit %s offset %s' % (size, offset)


def gen_where_sql(case_value, wheres, result_name) -> str:
    """生成where的条件语句
    demo:
        whers = [
            ('where','name','like'),
            ('and','env_id','='),
            ('and','env_id','=','aa)
        ]
        where_str = gen_where_sql(whers)
        " where name like :name and env_id = :env_id and env_id = :aa "
    """
    where_sql = ''
    for rel, col, option, *option_key in wheres:
        if option_key:
            key = f":{option_key[0]}"
        else:
            key = f":{col}"
        where_sql += f'{rel} {col} {option} {key} '
    case_value[result_name] = where_sql
    return where_sql


def in_sql(case_value, items, item_type, result_name):
    """
    case1:
    call in_sql([1,2,4],'int') 
    in (1,2,4)

    case2
    call in_sql(['1','3'],'str') 
    in ('1','3')
    """
    in_str = ''
    if 'int' == item_type:
        items = [str(i) for i in items]
        in_str += '(' + ','.join(items) + ')'
    elif 'str' == item_type:
        in_str += '("' + '","'.join(items) + '")'
    else:
        raise FunctionException('in_sql方法异常')
    case_value[result_name] = in_str
    return in_str
