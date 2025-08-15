# -*- coding: utf-8 -*-
# @Time    : 2022-09-13 11:38
# @Author  : zbmain
import time as t
from datetime import datetime, timedelta


def currentDateDS(span_days_num: int = 0, format: str = "%Y%m%d"):
    """
    获取当前日期的ds
    @param span_days_num: 过去则负天数。以后则正天数。
    @param format：时间格式。（默认：ds格式）
    """
    now = datetime.now()
    _ = now + timedelta(days=span_days_num)
    return _.strftime(format)


def cuttentDateTime():
    '''2020-01-01 00:00:00'''
    return t.strftime("%Y-%m-%d %H:%M:%S")


def cuttentTime():
    '''00:00:00'''
    return t.strftime("%H:%M:%S")


# 作用：减少主函数import time
def time():
    return t.time()


def timeSince(since):
    '''
    阶段耗时
    :param since: 开始时间( 获取由:time.time() )
    :return: 开始 >> 此刻
    返回格式：?m ?s
    '''
    s = t.time() - since
    m = int(s / 60)
    s -= m * 60
    return '%dm %ds' % (m, s)


def timeSince2(since: float):
    '''
    阶段耗时2
    :param since: 开始时间( 获取由:time.time() )
    :return: 开始 >> 此刻
    返回格式：?d ?h ?m ?s ?ms
    '''
    s = t.time() - since
    return timeFormat2Label(s)


def timingVal(func):
    '''计算耗时装饰器'''

    def wrapper(*arg, **kw):
        t1 = t.time()
        res = func(*arg, **kw)
        t2 = t.time()
        return (format(t2 - t1, '.4f')), res, func.__name__

    return wrapper


__propertys = {'d': "day", 'h': "hour", 'm': "minute", 's': "second", 'ms': "microsecond"}


def timeFormat(sec: float):
    '''
    时间格式化
    :param sec: 秒（小于30天）
    :return:
    Object{d,h,m,s,ms}
    '''
    sec = timedelta(seconds=sec)
    __date = datetime(1, 1, 1) + sec
    o = {}

    def get_func(func_name):
        res = getattr(__date, func_name)
        if func_name == 'day':
            res -= 1
        elif func_name == 'microsecond':
            res /= 1000
        return int(res)

    for k, v in __propertys.items():
        o[k] = get_func(v)
    return o


def timeFormat2Label(sec: float) -> str:
    '''
    时间格式化
    :param sec: 秒（小于30天）
    :return:  字符: d:h:m:s:ms
    '''
    res = timeFormat(sec)
    res_str = ''
    step = ''
    for k in __propertys.keys():
        value = res[k]
        if not value and (k == 'd' or k == 'h' or k == 'ms'):
            continue
        res_str += step + str(value) + k
        step = ':'
    return res_str


if __name__ == "__main__":
    since = t.time() - 9.9 * 60
    print(timeSince(since))
    print(timeSince2(since))

    t.sleep(1)

    print(cuttentTime())
    print(t.strftime("%Y-%m-%d %H:%M:%S"))
    print(cuttentDateTime())

    print(timeFormat(3456000))
    print(timeFormat2Label(20.123))
    print(currentDateDS(1))
