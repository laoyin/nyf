#coding=utf-8
from django.shortcuts import render_to_response,render
from django.conf import settings
from django.http import *
from django.template import Context
import pdb,json
from gdesign.models import SimulationData

#series_object_list
series_object_dict={}
#测试ajax请求
def test_ajax(request):
	rsdic={}
	rsdic['ajax_message']=request.POST['ajax_message']
	return HttpResponse(json.dumps(rsdic))

#请求模拟数据
def request_simulation_data(request):
	rsdic={}
	categories=[]
	series_object={}
	series_object_list=[]
	series=[]
	dashId=request.POST['dashId']
	if request.POST['requestType'] == u'0':
		default_windSpeed=request.POST['default_windSpeed']
		default_dischargeSpeed=request.POST['default_dischargeSpeed']
		if dashId ==u'0':
			series_object['name']=u'扩散速度(风速'+default_windSpeed+u'm/s)'
			series_object['data']=[]
			temp=SimulationData.objects.filter(windSpeed=str(default_windSpeed))
			for temp_object in temp :
				categories.append(temp_object.distance)
				series_object['data'].append(float(temp_object.single_leakage_speed))
			series_object_list.append(series_object)
			series_object_dict['0']=series_object_list
			for data_object in series_object_dict['0']:
				series.append(data_object)
		if dashId == u'1':
			series_object['name']=u'扩散速度(风速'+default_windSpeed+u'm/s;泄放速度'+default_dischargeSpeed+u'm/s)'
			series_object['data']=[]
			temp=SimulationData.objects.filter(windSpeed=str(default_windSpeed)).filter(dischargeSpeed=str(default_dischargeSpeed))
			for temp_object in temp :
				categories.append(temp_object.distance)
				series_object['data'].append(float(temp_object.leakage_speed))
			series_object_list.append(series_object)
			series_object_dict['1']=series_object_list
			for data_object in series_object_dict['1']:
				series.append(data_object)
		if dashId == u'2':
			series_object['name']=u'扩散浓度(泄放速度'+default_dischargeSpeed+u'm/s)'
			series_object['data']=[]
			temp=SimulationData.objects.filter(dischargeSpeed=str(default_dischargeSpeed))
			for temp_object in temp :
				categories.append(temp_object.distance)
				series_object['data'].append(float(temp_object.single_leakage_concentration))
			series_object_list.append(series_object)
			series_object_dict['2']=series_object_list
			for data_object in series_object_dict['2']:
				series.append(data_object)
		if dashId == u'3':
			series_object['name']=u'扩散浓度(风速'+default_windSpeed+u'm/s;泄放速度'+default_dischargeSpeed+u'm/s)'
			series_object['data']=[]
			temp=SimulationData.objects.filter(windSpeed=str(default_windSpeed)).filter(dischargeSpeed=str(default_dischargeSpeed))
			for temp_object in temp :
				categories.append(temp_object.distance)
				series_object['data'].append(float(temp_object.leakage_concentration))
			series_object_list.append(series_object)
			series_object_dict['3']=series_object_list
			for data_object in series_object_dict['3']:
				series.append(data_object)
	if request.POST['requestType']==u'1':
		if request.POST.has_key('simulation_windSpeed'):
			simulation_windSpeed=request.POST['simulation_windSpeed']
		if request.POST.has_key('simulation_dischargeSpeed'):
			simulation_dischargeSpeed=request.POST['simulation_dischargeSpeed']
		if dashId ==u'0':
			series_object['name']=u'扩散速度(风速'+simulation_windSpeed+u'm/s)'
			series_object['data']=[]
			temp=SimulationData.objects.filter(windSpeed=str(simulation_windSpeed))
			for temp_object in temp :
				categories.append(temp_object.distance)
				series_object['data'].append(float(temp_object.single_leakage_speed))
			series_object_dict['0'].append(series_object)
			for data_object in series_object_dict['0']:
				series.append(data_object)
		if dashId == u'1':
			series_object['name']=u'扩散速度(风速'+simulation_windSpeed+u'm/s;泄放速度'+simulation_dischargeSpeed+u'm/s)'
			series_object['data']=[]
			temp=SimulationData.objects.filter(windSpeed=str(simulation_windSpeed)).filter(dischargeSpeed=str(simulation_dischargeSpeed))
			for temp_object in temp :
				categories.append(temp_object.distance)
				series_object['data'].append(float(temp_object.leakage_speed))
			series_object_dict['1'].append(series_object)
			for data_object in series_object_dict['1']:
				series.append(data_object)
		if dashId == u'2':
			series_object['name']=u'扩散浓度(泄放速度'+simulation_dischargeSpeed+u'm/s)'
			series_object['data']=[]
			temp=SimulationData.objects.filter(dischargeSpeed=str(simulation_dischargeSpeed))
			for temp_object in temp :
				categories.append(temp_object.distance)
				series_object['data'].append(float(temp_object.leakage_concentration))
			series_object_dict['2'].append(series_object)
			for data_object in series_object_dict['2']:
				series.append(data_object)
		if dashId == u'3':
			series_object['name']=u'扩散浓度(风速'+simulation_windSpeed+u'm/s;泄放速度'+simulation_dischargeSpeed+u'm/s)'
			series_object['data']=[]
			temp=SimulationData.objects.filter(windSpeed=str(simulation_windSpeed)).filter(dischargeSpeed=str(simulation_dischargeSpeed))
			for temp_object in temp :
				categories.append(temp_object.distance)
				series_object['data'].append(float(temp_object.leakage_concentration))
			series_object_dict['3'].append(series_object)
			for data_object in series_object_dict['3']:
				series.append(data_object)
	rsdic={'categories':categories,'series':series}
	return HttpResponse(json.dumps(rsdic))




