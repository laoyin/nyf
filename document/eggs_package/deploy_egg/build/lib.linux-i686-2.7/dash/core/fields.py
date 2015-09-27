# -*- coding: utf-8 -*-

from django import forms
try :
    from . import widgets
except :
    print "没有正确安装Django版本,必须是1.6"

# Dash's fields are just simple wrappers around Django's form fields
class DateField(forms.DateField):
    widget = widgets.DateInput
    def __init__(self,*args,**kwargs):
        #kwargs['localize']=True
        super(self.__class__,self).__init__(*args,**kwargs)

class IntegerField(forms.IntegerField):
    widget = widgets.NumberInput

    def __init__(self, max_value=None, min_value=None, *args, **kwargs):
        super(IntegerField, self).__init__(max_value, min_value, localize=True, *args, **kwargs)


class ChoiceField(forms.ChoiceField):
    widget = widgets.Select
    def __init__(self,*args,**kwargs):
        #kwargs['localize']=True
        super(self.__class__,self).__init__(*args,**kwargs)

class MonthDateField(forms.CharField):
    widget = widgets.DateInput
    def __init__(self,*args,**kwargs):
        #kwargs['localize']=True
        super(self.__class__,self).__init__(*args,**kwargs)
