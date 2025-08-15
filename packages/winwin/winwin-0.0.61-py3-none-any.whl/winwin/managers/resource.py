# -*- coding: utf-8 -*-
# @Time    : 2022-08-22 23:22
# @Author  : zbmain
"""
资源版本配置文件.yaml

resource:
    common:
        ver: 0.0.1
        url: oss://bucket/xxx.zip
"""
import logging
import os
import shutil

from .. import env
from ..managers.oss import oss_get_object_topath
from ..utils import file_util
from ..utils import os_util


def read_resource_conf(resource_conf_url: str):
    if os.path.exists(resource_conf_url):
        content = file_util.read_yaml(resource_conf_url)
        return content.get('resource')


def upgrade_module_with_conf(conf, module: str, resource_dir: str, del_history: bool = True):
    latest_version = str(conf.get('version') or conf.get('ver'))
    module_dir = os.path.join(resource_dir, module)
    # 最新版本目录
    latest_resource_dir = os.path.join(module_dir, latest_version)
    if os.path.exists(latest_resource_dir):
        # 已经存在&目录大小非0，则跳过更新
        if os_util.dir_size(latest_resource_dir) > 0:
            logging.info('%s already updated latest version:%s' % (module, latest_version))
            return latest_resource_dir
    logging.info('%s resource will upgrade version:%s' % (module, latest_version))
    if del_history:
        logging.info('delete history version')
        os_util.del_dirs(module_dir)
    os.makedirs(latest_resource_dir, exist_ok=True)
    # 解压缩临时目录
    tmp_resource_dir = os.path.join(module_dir, 'tmp')
    os.makedirs(tmp_resource_dir, exist_ok=True)
    # 获取OSS资源文件
    oss_file = conf.get('url') or conf.get('osspath')
    latest_resource_file = os.path.join(latest_resource_dir, os.path.basename(oss_file))
    oss_get_object_topath(oss_file, latest_resource_file)
    # 解压资源包 & 解压后删除
    shutil.unpack_archive(latest_resource_file, tmp_resource_dir, 'zip')
    os.remove(latest_resource_file)
    # 自动识别压缩包是否多一层版本号作为文件夹并忽略。
    tmp_resource_file_dir = os.path.join(tmp_resource_dir, latest_version) \
        if latest_version in map(os.path.basename, os_util.subdir_list(tmp_resource_dir)) else tmp_resource_dir
    os_util.move_dir(tmp_resource_file_dir, latest_resource_dir)
    os_util.remove_dirs(tmp_resource_dir, False)
    logging.info('%s updated complete, current version:%s' % (module, latest_version))
    return latest_resource_dir


def upgrade(conf_file, resource_dir: str = env.CACHE_PROJECT_HOME, del_history: bool = True):
    """
    更新资源文件

    @param conf_file: app.yaml
    @param resource_dir: 资源保存位置
    @param del_history: 删除历史版本
    @return: 各模块资源的最新本地目录路径. eg:{'common':'[dir_path]'}
    """
    conf = read_resource_conf(conf_file)
    return {m: upgrade_module_with_conf(c, m, resource_dir, del_history) for m, c in conf.items()}
