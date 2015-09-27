# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from django.core.management.base import BaseCommand
import logging,pdb,json
from django.conf import settings
import django_gearman_commands
from gflux.apps.station.sql_utils import compute_health_result
from django.core.management import call_command


class Command(BaseCommand):
    help = 'compute_health_status'

    def handle(self,  *args, **options):
        args = {'log_file':settings.BASE_DIR+'/file/tao/process.log'}
        call_command('gearman_submit_job','compute_health_status',json.dumps(args), foreground=False)
