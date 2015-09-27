# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from django.core.management.base import BaseCommand
import logging,pdb
from django.conf import settings
import django_gearman_commands
from gcustomer.utils import cal_all_loss_oil_user

class Command(BaseCommand):
    help = 'compute_all_loss_customer'
    
    def handle(self,  *args, **options):
        cal_all_loss_oil_user()
