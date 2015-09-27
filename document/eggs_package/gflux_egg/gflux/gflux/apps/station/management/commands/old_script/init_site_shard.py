from django.core.management.base import BaseCommand
from gflux.apps.station import models
from gflux.apps.common import models as common_models
import sys, pdb
from gflux.apps.station import reports
from gflux.apps.station import sql_utils
from gflux.apps.station.models import User
from django.conf import settings
from dash.core.backends.sql.models import get_dash_session_maker

class Command(BaseCommand):
    help = 'Initialize the SQL models of station schema'

    def handle(self, *args, **options):
        try:
            sql_utils.get_all_stations()
            for name in settings.STATION_DESCRIPTIONS:
                get_dash_session_maker(name)
        except Exception, e:
            print >> sys.stderr, "Exception: ", str(e)
