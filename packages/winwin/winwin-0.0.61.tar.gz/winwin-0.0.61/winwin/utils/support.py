# -*- coding: utf-8 -*-
# @Time    : 2022-07-10 09:42
# @Author  : zbmain
"""
support: 工具
├── 环境配置.env:   文件目录 > Project目录 > HUB目录[~/.winwin_hub] > USER目录
├── mysql connect
├── odps connect
├── holo connect
├── redis connect
├── oss bucket
├── openseach conf
├── nebula connect.session
├── milvus
├── sentry_dsn
├── openai_key
└── 一些常用功能函数
"""
import os
from urllib.parse import urlparse, parse_qs, unquote_plus

from dotenv import load_dotenv as __load_dotenv

from .. import env


def __get_exists_file(file: str):
    """查找目录优先级: support.py目录 > Project跟目录(./) > HUB目录(~/.winwin_hub) > USER目录(~)"""
    dirs = [os.path.dirname(os.path.abspath(__file__)), env.PROJECT_HOME, env.HUB_HOME, env.USER_HOME]
    for _dir in dirs:
        filepath = os.path.join(_dir, file)
        if os.path.exists(filepath):
            return filepath


# support.py目录、项目跟目录、HUB环境目录、USER目录, 加载.env环境文件
env_file = __get_exists_file('.env')
env_file and __load_dotenv(env_file)


def set_env_file(file: str):
    """设置环境变量文件"""
    global env_file
    env_file = os.path.abspath(file)
    env_file and __load_dotenv(env_file)


# logging.info("current env file path is:[%s]" % env_file)


# MYSQL
def parse_mysql_uri(uri):
    parsed_uri = urlparse(uri)
    query = parse_qs(parsed_uri.query)
    return {
        'host': parsed_uri.hostname,
        'user': parsed_uri.username,
        'password': unquote_plus(parsed_uri.password),
        'port': parsed_uri.port,
        'database': parsed_uri.path[1:],
        'charset': 'utf8mb4' if query.get('charset') is None else query['charset'][0]
    }


def mysql_connect(name: str = "MYSQL_URI"):
    """MYSQL Connect"""
    import pymysql
    return pymysql.connect(**parse_mysql_uri(os.environ[name]), autocommit=True, cursorclass=pymysql.cursors.DictCursor)


# OSS
def parse_oss_uri(uri):
    parsed_uri = urlparse(uri)
    return {
        'endpoint': '{}://{}'.format(parsed_uri.scheme, parsed_uri.hostname),
        'access_key_id': parsed_uri.username,
        'access_key_secret': parsed_uri.password,
        'bucket': parsed_uri.path[1:],
    }


def oss_connect(name: str = "OSS_URI", bucket: str = ''):
    """OSS Bucket"""
    import oss2
    config = parse_oss_uri(os.environ[name])
    return oss2.Bucket(oss2.Auth(config['access_key_id'], config['access_key_secret']), config['endpoint'],
                       bucket or config['bucket'])


# ODPS
ODPS_TUNNEL, ODPS_LIMIT = True, False


def parse_odps_uri(uri):
    parsed_uri = urlparse(uri)
    query = parse_qs(parsed_uri.query)
    global ODPS_TUNNEL, ODPS_LIMIT
    ODPS_TUNNEL = True if query.get('tunnel') is None else bool(eval(query.get('tunnel')[0]))
    ODPS_LIMIT = False if query.get('limit') is None else bool(eval(query.get('limit')[0]))
    return {
        'endpoint': '{}://{}'.format(parsed_uri.scheme, os.path.join(parsed_uri.hostname, parsed_uri.path[1:])),
        'access_id': parsed_uri.username,
        'secret_access_key': parsed_uri.password,
        'project': query.get('project') and query.get('project')[0] or 'zhidou_hz'
    }


def odps_connect(name: str = "ODPS_URI"):
    """ODPS / Maxcompute Connect"""
    from odps import ODPS
    return ODPS(**parse_odps_uri(os.environ[name]))


# OpenSearch
def parse_ops_uri(uri):
    '''
    security_token有值,type=sts;
    security_token无值,type=access_key;
    '''
    parsed_uri = urlparse(uri)
    query = parse_qs(parsed_uri.query)
    security_token = query.get('security_token') and query.get('security_token')[0]
    assert query.get('app_name'), """opensearch-uri have to set 'app_name'"""
    return {
        'protocol': parsed_uri.scheme,
        'endpoint': parsed_uri.hostname,
        'access_key_id': parsed_uri.username,
        'access_key_secret': parsed_uri.password,
        'type': security_token and 'sts' or 'access_key',
        'security_token': security_token,
        'app_name': query.get('app_name') and query.get('app_name')[0] or ''
    }


def ops_connect(name: str = "OPS_URI"):
    """OpenSearch Conf"""
    return parse_ops_uri(os.environ[name])


# Hologres
def parse_holo_uri(uri):
    parsed_uri = urlparse(uri)
    query = parse_qs(parsed_uri.query)
    return {
        'host': parsed_uri.hostname,
        'user': parsed_uri.username,
        'password': parsed_uri.password,
        'port': parsed_uri.port,
        'dbname': query.get('dbname') and query.get('dbname')[0] or 'zhidou_hz'
    }


def holo_connect(name: str = "HOLO_URI"):
    """Holo Connect"""
    import psycopg2
    return psycopg2.connect(**parse_holo_uri(os.environ[name]))


# Redis
def parse_redis_uri(uri):
    parsed_uri = urlparse(uri)
    query = parse_qs(parsed_uri.query)
    return {
        'host': parsed_uri.hostname,
        'username': parsed_uri.username,
        'password': unquote_plus(parsed_uri.password),
        'port': parsed_uri.port,
        'db': query.get('db') and int(query.get('db')[0]) or 0,
        'decode_responses': query.get('decode_responses') and bool(query.get('decode_responses')[0]) or False
    }


__redis_pool = None


def redis_connect(name: str = "REDIS_URI"):
    """Redis Connect"""
    import redis
    global __redis_pool
    redis_uri = parse_redis_uri(os.environ[name])
    if not (__redis_pool and __redis_pool.connection_kwargs['host'] == redis_uri['host'] \
            and __redis_pool.connection_kwargs['db'] == redis_uri['db']):
        __redis_pool = redis.ConnectionPool(**redis_uri)
    return redis.StrictRedis(connection_pool=__redis_pool)


def parse_nebula_uri(uri=None):
    parsed_uri = urlparse(uri)
    query = parse_qs(parsed_uri.query)
    servers = [(parsed_uri.hostname, parsed_uri.port)] + [(server.split(':')[0], int(server.split(':')[1])) for i
                                                          in query.get('server', []) for server in i.split(',')]
    return {
        'servers': servers,
        'username': parsed_uri.username,
        'password': parsed_uri.password,
        'space': query.get('space') and query.get('space')[0] or '',
        'comment': query.get('comment') and query.get('comment')[0] or '',
        'heart_beat': query.get('heart_beat') and int(query.get('heart_beat')[0]) or 10,
        'vid_str_fixed_size': query.get('vid_str_fixed_size') and int(query.get('vid_str_fixed_size')[0]) or 50,
    }


__nebula_pool = None


def nebula_connect(name: str = 'NEBULA_URI'):
    uri = parse_nebula_uri(os.environ[name])
    from nebula3.gclient.net import ConnectionPool
    from nebula3.Config import Config
    global __nebula_pool
    if not __nebula_pool:
        __nebula_pool = ConnectionPool()
        __nebula_pool.init(uri['servers'], Config())
    session = __nebula_pool.get_session(uri['username'], uri['password'])
    session.space, session.comment, session.heart_beat, session.vid_str_fixed_size = uri['space'], uri['comment'], uri[
        'heart_beat'], uri['vid_str_fixed_size']
    return session


def parse_milvus_uri(uri=None):
    parsed_uri = urlparse(uri)
    return {
        'alias': parsed_uri.username,
        'host': parsed_uri.hostname,
        'port': parsed_uri.port
    }


def milvus_connect(name: str = 'MILVUS_URI'):
    from pymilvus import connections
    connections.connect(**parse_milvus_uri(os.environ[name]))


def sentry_dsn(name: str = 'SENTRY_DSN'):
    return os.environ[name]


def openai_api_key(name: str = 'OPENAI_API_KEY'):
    return os.environ[name]


def openai_api(name: str = 'OPENAI_API'):
    return parse_openai_uri(os.environ[name])


# openai
def parse_openai_uri(uri):
    parsed_uri = urlparse(uri)
    query = parse_qs(parsed_uri.query)
    port = f':{parsed_uri.port}' if parsed_uri.port else ''
    api_base = f'{parsed_uri.scheme}://{os.path.join(parsed_uri.hostname + port, parsed_uri.path[1:])}'
    return {
        'api_key': parsed_uri.username,
        'api_base': api_base,
        'type': query.get('type'),
        'version': query.get('version'),
        'organization': query.get('organization'),
    }


def get_environ(name: str):
    return os.environ[name]
