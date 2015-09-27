# -*- coding: utf-8 -*-

from . import utils

class DashDefiningClass(type):
    "Metaclass for Dash classes"
    def __new__(cls, name, bases, attrs):
        #给子类添加__abstract__属性，默认子类不是抽象类
        if '__abstract__' not in attrs:
            attrs['__abstract__'] = False
            
        #调用父类
        new_class = super(DashDefiningClass, cls).__new__(cls, name, bases, attrs)
        
        #不是抽象类是需要给子类添加uid属性
        if not new_class.__abstract__:
            if new_class.uid is None:
                new_class.uid = utils.uid(new_class.__name__)
                
        #返回对象
        return new_class

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        #子类只允许有一个实例对象
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        
        #实现了单例模式
        return cls._instances[cls]

def enum(**kwargs):
    enums = {}
    attrs = {}
    keys = {}

    for key, (value, name) in kwargs.items():
        enums[value] = name
        attrs[key] = value
        keys[key] = value

    #声明为类方法，可以取得类属性
    @classmethod
    def tuples(cls):
        return cls.ENUMS.items()

    attrs['ENUMS'] = enums
    attrs['KEYS'] = keys
    attrs['tuples'] = tuples

    #动态生成Enum类，类属性动态变化
    return type('Enum', (object, ), attrs)


#自定义修饰符
#interface_class为父类
def overrides(interface_class):
    #检查子类所重写的方法是否在父类中存在
    def overrider(method):
        # FIXME: need to test whether the class which the method belongs to is the subclass of interface_class
        assert method.__name__ in dir(interface_class), \
            "The method '%s' cannot be overrided because it doesn't exist in the parent class '%s'" \
            % (method.__name__, interface_class.__name__)
        return method
    return overrider
