#!/usr/bin/env python 
#coding=utf-8
from setuptools import setup , find_packages
setup(
	name = 'gflux',
	version = "0.1.0",
	packages = find_packages('gflux'),
	package_dir = {'':'gflux'},
	zip_safe = False,

	description = "gflux project", 
	long_description = "gflux project", 
	author = "niyoufa", 
	author_email = "niyoufa@tmlsystem.com", 
	include_package_data=True,

	license = "GPL", 
	keywords = ("gflux", "egg"), 
	platforms = "Independant", 
	url = "", 
) 