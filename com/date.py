from datetime import datetime, timedelta


def date_range(begin_date: str, end_date: str, step=1, unit='days', date_format='%Y-%m-%d'):
    if 'hours' == unit:
        unit, step = 'total_seconds', 3600*step
    elif 'min' == unit:
        unit, step = 'total_seconds', 60*step
    elif 'second' == unit:
        unit, step = 'total_seconds', step
    begin, end = datetime.strptime(
        begin_date, date_format), datetime.strptime(end_date, date_format)
    if 'total_seconds' == unit:
        unit_end = int(getattr(end-begin, unit)())
    else:
        unit_end = getattr(end-begin, unit)
    for i in range(0, unit_end, step):
        if 'total_seconds' == unit:
            yield (begin + timedelta(**{'seconds': i})).strftime(date_format)
        else:
            yield (begin + timedelta(**{'days': i})).strftime(date_format)


if __name__ == "__main__":
    print(list(date_range('2022-09-22', '2022-09-23')))
    print(list(date_range('2022-09-22', '2022-09-27', 2)))
    print(list(date_range('2022-09-22 00:00:00', '2022-09-23 12:00:00',
          6, unit='hours', date_format='%Y-%m-%d %H:%M:%S')))
