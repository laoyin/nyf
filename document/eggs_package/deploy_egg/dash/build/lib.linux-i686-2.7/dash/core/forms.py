# -*- coding: utf-8 -*-

from django import forms
from django.forms.fields import Field
from django.utils.datastructures import SortedDict
from django.utils import six

#获得类属性，返回结果为有序字典
def get_declared_fields(bases, attrs, with_base_fields=True):
    """
    Create a list of form field instances from the passed in 'attrs', plus any
    similar fields on the base classes (in 'bases'). This is used by both the
    Form and ModelForm metclasses.

    If 'with_base_fields' is True, all fields from the bases are used.
    Otherwise, only fields in the 'declared_fields' attribute on the bases are
    used. The distinction is useful in ModelForm subclassing.
    Also integrates any additional media definitions
    """
    #取得类属性中，值类型为Field的变量的列表集合
    #下面的逻辑简写可还原为
    """
    fields=[]
    for field_name, obj in list(six.iteritems(attrs)):
        if isinstance(obj, Field):
            fields.append(
                (field_name, attrs.pop(field_name))
            )
    """
    fields = [(field_name, attrs.pop(field_name)) for field_name, obj in list(six.iteritems(attrs)) if isinstance(obj, Field)]

    #对集合排序
    #creation_counter是django内置的记录类变量声明顺序的变量
    fields.sort(key=lambda x: x[1].creation_counter)

    # If this class is subclassing another Form, add that Form's fields.
    # Note that we loop over the bases in *reverse*. This is necessary in
    # order to preserve the correct order of fields.
    #是否合并父类中类变量的声明
    if with_base_fields:
        for base in bases[::-1]:
            if hasattr(base, 'base_fields'):
                fields = list(six.iteritems(base.base_fields)) + fields
    else:
        for base in bases[::-1]:
            if hasattr(base, 'declared_fields'):
                fields = list(six.iteritems(base.declared_fields)) + fields

    return SortedDict(fields)

class DeclarativeFormDefiningClass(type):
    def __new__(cls, name, bases, attrs):
        new_class = super(DeclarativeFormDefiningClass, cls).__new__(cls, name, bases, attrs)
        new_class.Form = type('Form', (forms.BaseForm, ),
                              {'base_fields': get_declared_fields(bases, attrs)})
        return new_class
