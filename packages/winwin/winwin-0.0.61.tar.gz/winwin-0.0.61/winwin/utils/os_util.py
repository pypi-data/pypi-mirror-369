# -*- coding: utf-8 -*-
# @Time    : 2022-07-20 21:09
# @Author  : zbmain
import logging
import os
import shutil
import time


def get_suffix(path) -> str:
    """路径后缀"""
    return os.path.splitext(path)[1]


def dir2list_with_suffix(dirpath: str, suffix=('.xlsx', '.csv', '.tsv'), ignoring_hidden_file: bool = True) -> list:
    return [os.path.join(dirpath, path) for path in os.listdir(dirpath) if
            get_suffix(path) in suffix and (path[0] != '.' if ignoring_hidden_file else True)]


def mkdir(dirpath: str):
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)


def makedirs(dirpath: str):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)


def subdir_list(dirpath, vextract: str = 'all') -> list:
    """获取目录下所有子目录名
    @param dirname: str 目录路径
    @param vextract: str file、dir、all（获取文件/目录/所有）
    @return:
    """
    return list(filter(os.path.isfile if vextract == 'file' else os.path.isdir if vextract == 'dir' else lambda x: x,
                       map(lambda filename: os.path.join(dirpath, filename), os.listdir(dirpath))))


def remove_dirs(path: str, only_sub_file: bool = True):
    """
    清空目录

    :param path: 待清空的目录
    :param only_sub_file: 只清空子目录和子文件（保留原目录）
    :return:
    """
    if os.path.exists(path):
        if os.path.isdir(path):
            if only_sub_file:
                del_list = os.listdir(path)
                for f in del_list:
                    file_path = os.path.join(path, f)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
            else:
                shutil.rmtree(path)
        else:
            os.remove(path)


# 兼容旧版本
del_dirs = remove_dirs


def move_dir(src_path, dst_path):
    """
    移动目录（移目录下的所有文件）

    @param src_path: str 源目录
    @param dst_path: str 目标目录
    """
    for file in os.listdir(src_path):
        src = os.path.join(src_path, file)
        dst = os.path.join(dst_path, file)
        shutil.move(src, dst)


def dir_size(path: str) -> int:
    """
    文件夹大小

    @param path: str 文件夹目录名
    """
    size = 0
    for root, dirs, files in os.walk(path, True):
        size += sum([os.path.getsize(os.path.join(root, name)) for name in files])
        return size


def parse_filepath(filepath) -> tuple:
    filepath, fullflname = os.path.split(filepath)
    fname, ext = os.path.splitext(fullflname)
    return filepath, fname, ext


def get_modify_time(file: str, format: str = '%Y/%m/%d %H:%M:%S') -> str:
    """文件名的后四位（是日期）"""
    return time.strftime(format, time.localtime(os.stat(file).st_mtime))


def get_create_time(file: str, format: str = '%Y/%m/%d %H:%M:%S') -> str:
    """文件名的后四位（是日期）"""
    return time.strftime(format, time.localtime(os.stat(file).st_ctime))


def network_state() -> bool:
    '''ping 网络状态'''
    logging.info('Check Network...')
    result = os.system(u"ping -c2 baidu.com > /dev/null 2>&1")  # 都丢弃，防止输出到控制台
    return result == 0


if __name__ == '__main__':
    print(parse_filepath('/home/deploy/tmp/'))
    print(get_modify_time('/home/deploy/tmp/'))
    print(get_create_time('/home/deploy/tmp/'))
    print(dir2list_with_suffix('/home/deploy/tmp/', ignoring_hidden_file=False))
    del_dirs('/home/deploy/tmp/tmps/', only_sub_file=True)
