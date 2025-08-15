# -*- coding: utf-8 -*-
# @Time    : 2022-08-12 10:58
# @Author  : zbmain
import logging
import os

from .. import env
from ..utils import support

__all__ = ['oss_get_object_cache', 'oss_get_object_topath', 'oss_get_object_stream', 'oss_upload_object',
           'oss_stream2DF', 'oss_file2DF']


def oss_get_object_cache(url, bucket=None, CACHE_DIR: str = env.CACHE_PROJECT_HOME):
    """下载 OSS文件到缓存目录"""
    bucket = bucket or support.oss_connect()
    cache_file = os.path.join(CACHE_DIR, os.path.basename(url))
    if not os.path.isfile(cache_file) or os.path.getsize(cache_file) == 0:
        parsed = support.urlparse(url)
        bucket.get_object_to_file(parsed.scheme and parsed.path[1:] or parsed.path, cache_file)
    return cache_file


def oss_get_object_topath(url, save_path='./', bucket=None):
    """下载 OSS文件到指定目录"""
    bucket = bucket or support.oss_connect()
    if save_path[-1] == '/' and not os.path.exists(save_path):
        os.makedirs(save_path)
    save_path = not os.path.basename(save_path) and os.path.join(save_path, os.path.basename(url)) or save_path
    if not os.path.isfile(save_path) or os.path.getsize(save_path) == 0:
        parsed = support.urlparse(url)
        bucket.get_object_to_file(parsed.scheme and parsed.path[1:] or parsed.path, save_path)
    return save_path


def oss_get_object_stream(url, bucket=None):
    """下载 OSS文件流"""
    bucket = bucket or support.oss_connect()
    parsed = support.urlparse(url)
    oss_url = parsed.scheme and parsed.path[1:] or parsed.path
    return bucket.get_object(oss_url).read()


def oss_upload_object(file_url, oss_url, bucket=None):
    """上传 本地文件到OSS"""
    bucket = bucket or support.oss_connect()
    file_name = os.path.basename(file_url)
    parsed = support.urlparse(oss_url)
    oss_url = parsed.scheme and parsed.path[1:] or parsed.path
    oss_url = not os.path.basename(oss_url) and (os.path.join(oss_url, file_name)) or oss_url
    bucket.put_object_from_file(oss_url, file_url)
    return '%s%s/%s' % ('oss://', bucket.bucket_name, oss_url)


def oss_stream2DF(oss_url: str, bucket=None, sep: str = None, names: list = None):
    """注意文件必须是表格文件"""
    import pandas
    suffix = os.path.splitext(oss_url)[1]
    content = oss_get_object_stream(oss_url, bucket)
    if suffix == '.xlsx':
        return pandas.read_excel(content, names)
    else:
        sep = sep or (',' if suffix == '.csv' else '\t' if suffix == '.tsv' else ',')
        try:
            lines = str(content.decode()).strip().split('\n')
            header = names or lines[0].split(sep)
            data = list(map(lambda x: str(x).split(sep), lines[names and 1 or 0:]))
            return pandas.DataFrame(data, columns=header)
        except ValueError as err:
            tmp_file = oss_get_object_cache(oss_url)
            df = pandas.read_csv(tmp_file, sep=sep, names=names)
            os.remove(tmp_file)
            logging.warning('Decoding error(row contains sep char). So temporary download method.')
            return df


def oss_file2DF(oss_url: str, bucket=None, sep: str = None, names: list = None):
    """注意文件必须是表格文件"""
    import pandas
    suffix = os.path.splitext(oss_url)[1]
    tmp_file = oss_get_object_cache(oss_url, bucket)
    if suffix == '.xlsx':
        df = pandas.read_excel(tmp_file, names)
    else:
        sep = sep or (',' if suffix == '.csv' else '\t' if suffix == '.tsv' else ',')
        df = pandas.read_csv(tmp_file, sep=sep, names=names)
    os.remove(tmp_file)
    return df
