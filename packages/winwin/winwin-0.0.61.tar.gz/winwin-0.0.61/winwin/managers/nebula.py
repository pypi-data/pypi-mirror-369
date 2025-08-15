# -*- coding: utf-8 -*-
# @Time    : 2022-07-22 18:04
# @Author  : zbmain

import json
import logging
import time
from typing import Dict

from ..utils import support

__all__ = ['Client', 'result_to_df', 'print_result', 'print_resp']


#####################################
#           Nebula Client           #
#####################################
class Client:
    def __init__(self, nebula_connect=None):
        self.client = nebula_connect or support.nebula_connect()
        self.space = str(self.client.__getattribute__('space'))
        self.comment = str(self.client.__getattribute__('comment'))
        self.heart_beat = int(self.client.__getattribute__('heart_beat'))
        self.vid_str_fixed_size = int(self.client.__getattribute__('vid_str_fixed_size'))

    def exec_query(self, query: str, heart_beat: int = 0):
        resp = self.client.execute(query)
        time.sleep(heart_beat)
        assert resp.is_succeeded(), resp.error_msg()
        return resp

    def test(self, ):
        resp_json = self.client.execute_json("yield 1")
        json_obj = json.loads(resp_json)
        return json.dumps(json_obj, indent=1, sort_keys=True)

    def create_space(self, space: str = '', comment: str = '', vid_str_fixed_size: int = 0):
        space = space or self.space
        comment = comment or self.comment
        vid_str_fixed_size = vid_str_fixed_size or self.vid_str_fixed_size
        assert space
        nGQL = 'CREATE SPACE IF NOT EXISTS %s(vid_type=FIXED_STRING(%d)) comment="%s";USE %s;' % (
            space, vid_str_fixed_size, comment, space)
        logging.info('please wait for create space:"%s"\tnGQL:%s' % (space, nGQL))
        return self.exec_query(nGQL, self.heart_beat)

    def use_space(self, space: str = ''):
        space = space or self.space
        assert space
        return self.exec_query('USE %s;' % space)

    def drop_space(self, space: str = '', drop: bool = False):
        """谨慎操作。参数必须再设置[drop=True]才有效. drop默认:False"""
        space = space or self.space
        assert space
        return drop and self.exec_query('DROP SPACE IF EXISTS %s;' % space)

    def del_all_tags(self, space: str = '', drop: bool = False):
        """谨慎操作。参数必须再设置[drop=True]才有效. drop默认:False"""
        space = space or self.space
        assert space
        return drop and self.exec_query('DELETE TAG * FROM "%s";' % space)

    def submit_stats(self, space: str = ''):
        self.use_space(space)
        return self.exec_query('SUBMIT JOB STATS;', self.heart_beat << 1)

    def show_stats(self, space: str = ''):
        self.submit_stats(space)
        return self.exec_query('SHOW STATS;')

    def show_indexs(self, space: str = ''):
        self.use_space(space)
        return self.exec_query('SHOW TAG INDEXES;')

    def show_spaces(self):
        return self.exec_query('SHOW SPACES;')

    def show_job(self, space: str = ''):
        self.use_space(space)
        return self.exec_query('SUBMIT JOB COMPACT;')

    def release(self):
        if self.client is not None:
            self.client.release()

    def create_index(self, query: str):
        self.use_space()
        self.exec_query(query, self.heart_beat << 1)

    def rebuild_index(self, query: str):
        self.use_space()
        self.exec_query(query, self.heart_beat)


#####################################
#   Scan Method 1 (Recommended)     #
#####################################
# from nebula3.data.ResultSet import ResultSet
def result_to_df(result):
    """
    build list for each column, and transform to dataframe
    """
    import pandas
    assert result.is_succeeded()
    columns = result.keys()
    d: Dict[str, list] = {}
    for col_num in range(result.col_size()):
        col_name = columns[col_num]
        col_list = result.column_values(col_name)
        d[col_name] = [x.cast() for x in col_list]
    return pandas.DataFrame.from_dict(d)


#####################################
#   Scan Method 2   (Customize)     #
#####################################
# from nebula3.data.DataObject import Value, ValueWrapper
# def customized_cast_with_dict(val: ValueWrapper):
def customized_cast_with_dict(val):
    from nebula3.data.DataObject import Value
    cast_as = {
        Value.NVAL: "as_null",
        Value.__EMPTY__: "as_empty",
        Value.BVAL: "as_bool",
        Value.IVAL: "as_int",
        Value.FVAL: "as_double",
        Value.SVAL: "as_string",
        Value.LVAL: "as_list",
        Value.UVAL: "as_set",
        Value.MVAL: "as_map",
        Value.TVAL: "as_time",
        Value.DVAL: "as_date",
        Value.DTVAL: "as_datetime",
        Value.VVAL: "as_vertex",
        Value.EVAL: "as_edge",
        Value.PVAL: "as_path",
        Value.GGVAL: "as_geography",
        Value.DUVAL: "as_duration",
    }
    _type = val._value.getType()
    method = cast_as.get(_type)
    if method is not None:
        return getattr(val, method, lambda *args, **kwargs: None)()
    raise KeyError("No such key: {}".format(_type))


# def print_resp(resp: ResultSet):
def print_resp(resp):
    import prettytable
    assert resp.is_succeeded()
    output_table = prettytable.PrettyTable()
    output_table.field_names = resp.keys()
    for recode in resp:
        value_list = []
        for col in recode:
            val = customized_cast_with_dict(col)
            value_list.append(val)
        output_table.add_row(value_list)
    print(output_table)


print_result = print_resp
