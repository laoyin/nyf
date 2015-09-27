# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from django.core.management.base import BaseCommand
from gflux.apps.station import models
from datetime import datetime
from optparse import make_option
import sys,pdb,re

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--site',help="set site name",type="string"),
    )

    def handle(self,  *args, **options):
        compute_item_items(options['site'])
