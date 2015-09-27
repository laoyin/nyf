#coding=utf-8
from django.core.management.base import BaseCommand
from dash.core.backends.sql.models import get_dash_session_maker
import sys, pdb
from gcustomer.utils import cal_station_items_bottom_10


class Command(BaseCommand):
    help = 'compute stations botton items'

    def handle(self, *args, **options):
    	try :
    		cal_station_items_bottom_10()
        except Exception,e:
    		print e
