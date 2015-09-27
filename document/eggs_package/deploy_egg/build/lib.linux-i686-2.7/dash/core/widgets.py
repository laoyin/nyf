# -*- coding: utf-8 -*-

from django import forms

class DateInput(forms.DateInput):
    def __init__(self, attrs=None, format=None):
        final_attrs = {
            'data-provide': 'datepicker',
            'data-date-format': 'yyyy-mm-dd',
            'class': 'dash-control form-control',
            'style': 'width:100px;',
        }
        if isinstance(attrs, dict):
            final_attrs.update(attrs)
        super(DateInput, self).__init__(attrs=final_attrs, format=format)
        
    class Media:
        js = ['bootstrap-datepicker/js/bootstrap-datepicker.js']
        css = {'all': ('bootstrap-datepicker/css/datepicker.css', )}

        
class NumberInput(forms.NumberInput):
    def __init__(self, attrs=None):
        final_attrs = {
            'class': 'dash-control form-control',
            'style': 'width:80px;',
        }
        if isinstance(attrs, dict):
            final_attrs.update(attrs)
        super(NumberInput, self).__init__(attrs=final_attrs)
    
        
class Select(forms.Select):
    def __init__(self, attrs=None, choices=()):
        final_attrs = {
            'class': 'dash-control form-control',
            'style': 'width:100px;',
        }
        if isinstance(attrs, dict):
            final_attrs.update(attrs)
        super(Select, self).__init__(attrs=final_attrs, choices=choices)

