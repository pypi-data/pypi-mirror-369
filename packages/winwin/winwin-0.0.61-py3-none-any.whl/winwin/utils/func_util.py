# -*- coding: utf-8 -*-
# @Time    : 2022-07-22 18:20
# @Author  : zbmain

__all__ = ['view_df', 'warning_ignored', 'set_seed', 'delay', 'pandas_set', 'get_attr']

import logging
import warnings

import time
from . import pd_util

view_df = pd_util.view_df
pandas_set = pd_util.setting


def delay(second: int):
    time.sleep(second)

    def wrapper(func):
        def inner(*args, **kwargs):
            ret = func(*args, **kwargs)
            return ret

        return inner

    return wrapper


def warning_ignored():
    """关闭一些警告(不推荐)"""
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", category=ResourceWarning)
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)
    warnings.filterwarnings("ignore", category=UserWarning)


def set_seed(seed: int = 1990):
    import numpy
    import random
    random.seed(seed)
    numpy.random.seed(seed)
    try:
        import tensorflow
        tensorflow.random.set_seed(seed)
        tensorflow.set_random_seed(seed)
    except:
        logging.info("Waring: tensorflow not installed.")

    try:
        import torch
        torch.manual_seed(seed)  # cpu
        torch.cuda.manual_seed(seed)  # gpu
        torch.cuda.manual_seed_all(seed)  # all gpu
    except:
        logging.info("Waring: torch not installed.")


def get_attr(o, key, type=None):
    """
    获取对象的属性值
    :param o: 对象
    :param key: 属性名
    :param type: 以此类型返回（强制转换）默认：空（不转换）
    :return: 属性值
    """
    __value = None
    try:
        if isinstance(o, dict):
            __value = o.get(key)
        elif hasattr(o, "__getitem__"):
            __value = o[key]
        elif hasattr(o, key):
            __value = getattr(o, key)
        else:
            pass
    except (KeyError, TypeError, AttributeError) as e:
        print(f"获取键值失败: {e}")
        __value = None
    if __value is not None and type:
        return type(__value)
    return __value
