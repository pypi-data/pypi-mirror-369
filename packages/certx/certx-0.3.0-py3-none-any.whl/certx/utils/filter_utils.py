from enum import Enum


def build_filters(dict_values: dict, keys: list, filters: dict = None, ignore_empty: bool = True):
    """构建过滤条件字典数据
    :param dict_values: 字典对象
    :param keys: 过滤条件的key列表
    :param filters: 不为空，则在filters中追加过滤条件
    :param ignore_empty: 是否忽略None值
    :return: dict
    """
    if filters is None:
        filters = {}

    if keys is None:
        return filters

    for key in keys:
        if key not in dict_values:
            continue
        value = dict_values.get(key)
        if value is None:
            if not ignore_empty:
                filters[key] = value
        else:
            if isinstance(value, Enum) or issubclass(type(value), Enum):
                filters[key] = value.value
            else:
                filters[key] = value

    return filters
