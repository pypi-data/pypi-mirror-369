import logging
from typing import Optional

import pandas


def setting(
    max_row: int = 0,
    max_col: int = 0,
    max_col_w: int = 0,
    max_char_size: int = 0,
    float_precision: int = 0,
):
    """
    Pandas 常用设置
    @param max_row: 显示最大行数
    @param max_col: 显示最大列数
    @param max_col_w: 显示列长度
    @param max_char_size: 显示横向最多字符数
    @param float_precision: 显示浮点数最多位数
    @return: None
    """
    max_row and pandas.set_option("display.max_rows", max_row)
    max_col and pandas.set_option("display.max_columns", max_col)
    max_col_w and pandas.set_option("display.max_colwidth", max_col_w)
    max_char_size and pandas.set_option("display.width", max_char_size)
    float_precision and pandas.set_option("precision", float_precision)


def view_df(df, head_num: int = 5, tail_num: int = 5, comment: str = "DataFrame"):
    logging.info(f"{comment} row_size:{df.shape[0]}")

    import pandas as pd

    return (
        None
        if -1 in (head_num, tail_num)
        else pd.concat([df.head(head_num), df.tail(tail_num)], axis=0)
    )


def check_null(x, null_values: Optional[list] = None):
    """
    检测空值

    @param x: 检测值
    @param null_values: list 检测值黑名单表,都作为None.
    """
    import pandas as pd

    if null_values is None:
        null_values = []
    return (
        None
        if (x and str(x).lower() in (z.lower() for z in null_values))
        or pd.isna(x)
        or pd.isnull(x)
        else x
    )


def value_count2df(
    source_df,
    col_name,
    normalize=False,
    ascending=False,
    dropna: bool = True,
    count_alias="count",
):
    """
    pandas value_counts 统计

    @param  source_df:输入
    @param col_name: 统计的列名
    @param normalize: 是否归一化
    @param ascending: 排序
    @param dropna: 是否忽略空值
    @param count_alias: 统计次数的列别名
    """
    return (
        source_df[col_name]
        .value_counts(normalize=normalize, ascending=ascending, dropna=dropna)
        .rename_axis(col_name)
        .reset_index(name=count_alias)
    )


def load_same_csv(*args):
    """
    加载多表格数据(保证数据一样)
    """
    import pandas as pd

    dfs = [pd.read_csv(f) for f in args]
    return pd.concat(dfs, ignore_index=True)
