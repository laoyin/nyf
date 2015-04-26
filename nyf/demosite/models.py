from django.db import models
from django import forms
import datetime

class customer(models.Model):
	name=models.CharField(max_length=30)
	password=models.CharField(max_length=50)
	sex=models.CharField(max_length=5)
	age=models.CharField(max_length=5)
	tel=models.CharField(max_length=11)
	address = models.CharField(max_length=50)
	city = models.CharField(max_length=60)
	authority=models.CharField(max_length=10)
	def __unicode__(self):
		return self.name

class  File(models.Model):
	title=models.CharField(max_length=50)
	time=models.CharField(max_length=50)
	filesrc=models.CharField(max_length=128)
	# 0: article 1: image
	file_type = models.IntegerField()
	def __unicode__(self):
		return self.title
	class Meta:
		unique_together=(('title','file_type'),)

class uploadFileForm(forms.Form):
	title = forms.CharField(max_length=50)
	file_data = forms.FileField()
	def __unicode__(self):
		return self.title

class Links(models.Model):
	title=models.CharField(max_length=255)
	url=models.CharField(max_length=255)
	time=models.DateField(auto_now=True)
	def __unicode__(self):
		return self.title
            
class Image(models.Model):
	name=models.CharField(max_length=255)
	binary_data=models.TextField()
	def __unicode__(self):
		return self.name

class Ques(models.Model):
	question=models.TextField()
	answer=models.TextField()
	date=models.DateField()  
