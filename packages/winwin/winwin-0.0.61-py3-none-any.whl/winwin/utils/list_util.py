# -*- coding: utf-8 -*-
# @Time    : 2022-07-20 21:00
# @Author  : zbmain

def reverse(arr: list) -> list:
    """反转列表，返回新列表"""
    return arr.reverse() or arr


def append(arr, element) -> list:
    """添加元素，返回新列表"""
    return arr.append(element) or arr


def push(arr, element) -> list:
    """添加元素，返回新列表"""
    return append(arr, element)


def extend(arr1, arr2) -> list:
    """合并两个列表，返回新列表"""
    return arr1.extend(arr2) or arr1


def sort_relative(arr: list, relativeArr: list) -> list:
    """
    列表相对排序
    @param arr: 原列表
    @param relativeArr: 列表值索引相对列表
    @return 新列表（原列表排序）
    """
    ranks = {x: i for i, x in enumerate(relativeArr)}
    arr.sort(key=lambda x: (0, ranks[x]) if x in ranks else (1, x))
    return arr
