from django.core.management.base import BaseCommand
from gflux.apps.station import models
from gflux.apps.common import models as common_models
import sys, pdb
from gflux.apps.station import reports
from gflux.apps.station import sql_utils
from gflux.apps.station.models import User
from django.core.management import call_command
from django.conf import settings

class Command(BaseCommand):
    help = 'Initialize the SQL models of station schema'

    def handle(self, *args, **options):
        try:
            sql_utils.get_all_stations()

            for name in settings.STATION_DESCRIPTIONS:
                call_command('compute_item_assoc',interactive=False,period=0,site=name)
                call_command('compute_item_assoc',interactive=False,period=1,site=name)
                call_command('compute_item_assoc',interactive=False,period=2,site=name)
                call_command('compute_item_assoc',interactive=False,period=3,site=name)

        except Exception, e:
            print >> sys.stderr, "Exception: ", str(e)
