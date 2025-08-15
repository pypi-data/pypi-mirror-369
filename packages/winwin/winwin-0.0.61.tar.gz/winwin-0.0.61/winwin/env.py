# -*- coding: utf-8 -*-
# @Time    : 2022-07-20 09:42
# @Author  : zbmain
"""
HOME                -> 环境变量目录
├── MODULE_HOME     -> 模型
├── DATA_HOME       -> 数据集
├── CACHE_HOME      -> 缓存目录
├── CONF_HOME       -> 配置目录
├── TMP_HOME        -> 临时文件
├── LOG_HOME        -> 日志
├── SOURCES_HOME    -> 代码
└── RESOURCES_HOME  -> 资源
"""
import os

__all__ = ['USER_HOME', 'HUB_HOME', 'MODULE_HUB_HOME', 'DATASET_HUB_HOME', 'CACHE_HUB_HOME', 'CONF_HUB_HOME',
           'TMP_HUB_HOME', 'LOG_HUB_HOME', 'SOURCES_HUB_HOME', 'RESOURCES_HUB_HOME', 'PROJECT_HOME',
           'CACHE_PROJECT_HOME', 'HUB_HOME_DIR']

__HUB_HOME_ENV_KEY = 'WINWIN_HUB_HOME'
"""WINWIN_HOME - 环境变量Key"""

HUB_HOME_DIR = '.winwin_hub'
"""WINWIN_HOME - 本地HUB目录名"""


def _get_user_home():
    return os.path.expanduser('~')


def _get_project_home():
    return os.path.abspath('')


def _get_hub_home():
    if __HUB_HOME_ENV_KEY in os.environ:
        home_path = os.environ[__HUB_HOME_ENV_KEY]
        if os.path.exists(home_path):
            if os.path.isdir(home_path):
                return home_path
            else:
                raise RuntimeError('The environment variable WINWIN_HOME {} is not a directory.'.format(home_path))
        else:
            return home_path
    os.environ[__HUB_HOME_ENV_KEY] = os.path.join(_get_user_home(), HUB_HOME_DIR)
    return os.environ[__HUB_HOME_ENV_KEY]


def _get_sub_home(directory, root):
    home = os.path.join(root, directory)
    os.makedirs(home, exist_ok=True)
    return home


# HUB.跟目录 & 子目录
USER_HOME = _get_user_home()
HUB_HOME = _get_hub_home()
MODULE_HUB_HOME = _get_sub_home('modules', HUB_HOME)
DATASET_HUB_HOME = _get_sub_home('dataset', HUB_HOME)
CACHE_HUB_HOME = _get_sub_home('cache', HUB_HOME)
CONF_HUB_HOME = _get_sub_home('conf', HUB_HOME)
TMP_HUB_HOME = _get_sub_home('tmp', HUB_HOME)
LOG_HUB_HOME = _get_sub_home('log', HUB_HOME)
SOURCES_HUB_HOME = _get_sub_home('sources', HUB_HOME)
RESOURCES_HUB_HOME = _get_sub_home('resources', HUB_HOME)

# 项目.跟目录
PROJECT_HOME = _get_project_home()
CACHE_PROJECT_HOME = _get_sub_home('.cache', PROJECT_HOME)
