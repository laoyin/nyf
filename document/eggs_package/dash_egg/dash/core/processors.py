# coding=utf-8
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')
import sys
from django.utils import six
from datetime import datetime

#将lst为列表，processors为元组，第一个元素为返回的key，第二个元素为方法引用
#批量处理lst，批量返回处理结果
def parse_to_dict(lst, processors):
    ret = {}
    try:
        for (name, processor), value in zip(processors, lst):
            ret[name] = processor(value)
        return ret
    except Exception, e:
        #print >> sys.stderr, 'parse_to_dict: ', str(e)
        return None

def force_utf8(text):
    if isinstance(text, unicode):
        text = text.encode("utf-8")
    return text

#闭包用法
#惰性返回字符串替换后的结果
def str_replace(before, after):
    def convert(value):
        return value.replace(before, after)
    return convert

#闭包用法
#惰性返回按序对某个值处理的结果
def pipeline(*func_list):
    def convert(value):
        for func in func_list:
            value = func(value)
        return value
    return convert

def trim(value):
    if isinstance(value, six.string_types):
        return value.strip()
    else:
        return str(value).strip()

def lower(value):
    if isinstance(value, six.string_types):
        return value.lower()
    else:
        return str(value).lower()

#闭包用法
#惰性返回int
def safe_int(default):
    def convert(value):
        try:
            return int(value)
        except ValueError:
            return default
    return convert

#闭包用法
#惰性返回字典值
def str_to_enum(mapping):
    def convert(value):
        return mapping[value.strip()]
    return convert

#闭包用法
#惰性返回datetime对象
def str_to_datetime(datetime_format):
    def convert(value):
        return datetime.strptime(value.strip(), datetime_format)
    return convert
