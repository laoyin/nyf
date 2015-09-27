# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from django.core.management.base import BaseCommand
import logging,pdb
from django.conf import settings
import django_gearman_commands
from gcustomer.utils import cal_peak_period_by_sites_group,get_all_site

class Command(BaseCommand):
    help = 'compute_gcustomer_site_peak_peroid'

    def handle(self,  *args, **options):
        try:
            cal_peak_period_by_sites_group()
        except Exception,e :
            print e
