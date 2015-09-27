#coding=utf-8
from django.core.management.base import BaseCommand
from django.conf import settings
from gcustomer.models import *
from gcustomer.apps.jiachebao import *
from dash.core.backends.sql.models import *
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.orm import sessionmaker
from datetime import *
import sys, pdb
from gcustomer.utils import *


class Command(BaseCommand):
    help = 'Init  server data'

    def handle(self, *args, **options):
    	session = get_dash_session_maker()()
    	user_list = session.query(CustomerAccount).all()
    	for user in user_list :
    		if len(user.password) < 30  and len(user.password)  < 30 :
	    		user.password = md5_data(user.password)
	    		user.pay_password = md5_data(user.pay_password)
    	session.commit()
