import inspect

import mmcv


class Registry(object):

    def __init__(self, name):
        self._name = name
        self._module_dict = dict()

    def __repr__(self):
        format_str = self.__class__.__name__ + '(name={}, items={})'.format(
            self._name, list(self._module_dict.keys()))
        return format_str

    @property
    def name(self):
        return self._name

    @property
    def module_dict(self):
        return self._module_dict

    def get(self, key):
        return self._module_dict.get(key, None)

    def _register_module(self, module_class):
        """Register a module.

        Args:
            module (:obj:`nn.Module`): Module to be registered.
        """
        if not inspect.isclass(module_class):
            raise TypeError('module must be a class, but got {}'.format(
                type(module_class)))
        module_name = module_class.__name__
        if module_name in self._module_dict:
            raise KeyError('{} is already registered in {}'.format(
                module_name, self.name))
        self._module_dict[module_name] = module_class

    def register_module(self, cls):
        self._register_module(cls)
        return cls


def build_from_cfg(cfg, registry, default_args=None):
    """Build a module from config dict.

    Args:
        cfg (dict): Config dict. It should at least contain the key "type".至少有type的字典
        registry (:obj:`Registry`): The registry to search the type from.类
        default_args (dict, optional): Default initialization arguments.默认字典参数

    Returns:
        obj: The constructed object.
    """
    assert isinstance(cfg, dict) and 'type' in cfg#保证‘type’在字典中
    assert isinstance(default_args, dict) or default_args is None#保证参数是字典
    args = cfg.copy()
    obj_type = args.pop('type')#'FCOS'只是一个字符串名字
    if mmcv.is_str(obj_type):#如果是字符串
        obj_cls = registry.get(obj_type)#获得字符串对应的类
        if obj_cls is None:#不能是空
            raise KeyError('{} is not in the {} registry'.format(
                obj_type, registry.name))
    elif inspect.isclass(obj_type):#如果已经是一个类了，就不用再去调用了
        obj_cls = obj_type
    else:#如果什么都不是就错了
        raise TypeError('type must be a str or valid type, but got {}'.format(
            type(obj_type)))
    if default_args is not None:
        for name, value in default_args.items():#将额外给定的参数也加入到args中，组合后一起给类
            args.setdefault(name, value)
    return obj_cls(**args)#直接构造成FCOS(config)格式，形成model
