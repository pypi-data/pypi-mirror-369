from oslo_utils import importutils


def import_class(class_path, *args, class_map=None, **kwargs):
    """加载类
    :param class_path: 类路径或者别名
    :param class_map: 默认的类字典映射。{'别名': '类路径'}
    :param args: 类参数
    :param kwargs: 类参数
    """
    cp = class_path
    if class_map is not None and class_path in class_map:
        cp = class_map[cp]

    if not cp:
        raise ValueError('class_path is empty')

    return importutils.import_class(cp)(*args, **kwargs)
