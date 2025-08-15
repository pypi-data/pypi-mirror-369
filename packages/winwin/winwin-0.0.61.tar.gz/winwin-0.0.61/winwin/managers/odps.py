# -*- coding: utf-8 -*-
# @Time    : 2022-08-12 11:31
# @Author  : zbmain
import csv
import os

from .. import env
from ..utils import support

__all__ = ['odps_download_with_sql', 'download_with_sql']


def download_with_sql(sql, save_path, connect=None, sep=',', tocache: bool = False, hints: dict = None,
                      header: bool = True) -> str:
    """通过SQL下载全量数据"""
    connect = connect or support.odps_connect()
    save_path = os.path.join(tocache and env.CACHE_PROJECT_HOME or env.PROJECT_HOME, save_path)
    if sql.endswith('.sql'):
        with open(os.path.join(env.PROJECT_HOME, sql), 'r') as f:
            fsql = f.read()
    else:
        fsql = sql
    with connect.execute_sql(fsql, hints=hints).open_reader(tunnel=support.ODPS_TUNNEL,
                                                            limit=support.ODPS_LIMIT) as reader:
        headers = reader.schema.names
        with open(save_path, 'w', encoding='utf8') as writefile:
            csv_writer = csv.writer(writefile, delimiter=sep)
            if header:
                csv_writer.writerow(headers)
            for record in reader:
                csv_writer.writerow(dict(record).values())
    return save_path


# 旧方法, 版本兼容
odps_download_with_sql = download_with_sql
