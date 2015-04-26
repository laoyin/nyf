#coding=utf-8
#测试django模板,模板定义了占位符以及用于规范文档该如何显示的各部分基本逻辑(模板标签)
#django的框架的大部分子系统,包括模板系统都依赖于配置文件;
#django模板系统的基本规则:写模板;创建Template对象;创建Context;调用render()

#常用模板标签

#{{variable}}

#{% for item in item_list %} {% for %}中有一个forloop的模板变量 forloop.counter表示循环执行次数
#       html内容
#{% endfor %}

#{% if condition %} {%if%}接受and or not,不允许在同一个标签中同时使用and 和 or 可以用嵌套的{%if%}替换
#      html内容
#{% else %}
#      html内容
#{% endif %}

#{% ifequal value1 value2 %}
#{% else %}
#{% endifqequal %}

# {# 注释 #}

#{% comment %}
#多行注释
#{% endcomment %}

#{% include 'nav.html'%}
#{% include template_name%}

#模板继承
#定义base.html,该页面中包含很多{% block blockname %}html内容{% endblock%}标签
#{% extends "base.html"%}

from django import template
t=template.Template('My name is {{name}}.')
c=template.Context({'name':'nyf'})
print t.render(c)

from django.template.loader import get_template
from django.template import Context
t=template.get_template('filename.html')
html=t.render(Context({}))
return HttpResponse(html)

from django.shortcuts import render_to_response
return render_to_response("filemame.html",{})

























