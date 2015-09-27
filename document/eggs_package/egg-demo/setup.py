#!/usr/bin/env python 
#coding=utf-8
from setuptools import setup , find_packages
setup(
	name = 'demo',
	version = "0.1.0",
	packages = find_packages('src'),
	package_dir = {'':'/home/nyf/src'},
	zip_safe = False,

	description = "egg test demo.", 
	long_description = "egg test demo, haha.", 
	author = "niyoufa", 
	author_email = "niyoufa@tmlsystem.com", 

	license = "GPL", 
	keywords = ("test", "egg"), 
	platforms = "Independant", 
	url = "", 
) 