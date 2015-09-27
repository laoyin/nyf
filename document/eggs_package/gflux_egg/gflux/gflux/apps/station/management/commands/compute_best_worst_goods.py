# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from django.core.management.base import BaseCommand
import logging,pdb
from django.conf import settings
import django_gearman_commands
from gcustomer.utils import get_none_fuel_last_10,get_none_fuel_top_10,cal_station_items_top_bottom_10

class Command(BaseCommand):
    help = 'compute_all_loss_customer'

    def handle(self,  *args, **options):
        cal_station_items_top_bottom_10()
