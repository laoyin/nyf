# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from django.core.management.base import BaseCommand
from gflux.apps.station import models
from gflux.apps.station import cubes
from gflux.apps.station.models import TransType, PaymentType, CardType, DayPeriod
from datetime import datetime
from optparse import make_option
import sys,pdb,re,json
from django.core.cache import cache
from django.conf import settings
from gflux.apps.station.models import all_type_args
from gflux.apps.station.sql_utils import get_all_locations, get_all_fuel_types
import itertools,os,datetime

args_values={
    'location':[],
    'barcode':[]
}

cmds=[]

def gen():
    #PYTHON BIN
    python=settings.PYTHON_BIN

    #gen args
    locations=get_all_locations()
    for location in locations:
        args_values['location'].append(location[0])

    fuel_types=get_all_fuel_types()
    for fuel_type in fuel_types:
        args_values['barcode'].append(fuel_type[0])

    #get cmds
    for type in all_type_args:
        args=[]
        for arg in all_type_args[type]:
            args.append(['--%s=%s'%(arg,str(x)) for x in args_values[arg]])

        if len(args)==0:
            cmds.append(python+' manage.py compute_gilbarco_index --type=%s'%(type))
        elif len(args)==1:
            for arg in args[0]:
                cmd=python+' manage.py compute_gilbarco_index --type=%s %s'%(type,arg)
                cmds.append(cmd)
        else:
            #笛卡尔积
            args=tuple(args)
            d_args=itertools.product(*args)

            for arg in d_args:
                cmd=python+' manage.py compute_gilbarco_index --type=%s '%type
                cmd+=' '.join(arg)
                cmds.append(cmd)

gen()

class Command(BaseCommand):
    def handle(self,  *args, **options):
        print 'strart:',str(datetime.datetime.now())
        cmds.sort()
        for cmd in cmds:
            ret=os.system(cmd)
            if ret==0:
                print 'finish compute:'+cmd
            else:
                print 'error compute:'+cmd
        print 'end:',str(datetime.datetime.now())
