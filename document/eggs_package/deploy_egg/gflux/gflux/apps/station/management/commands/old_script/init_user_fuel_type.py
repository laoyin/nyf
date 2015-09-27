from django.core.management.base import BaseCommand
from gflux.apps.station import models
from gflux.apps.common import models as common_models
from dash.core.backends.sql.models import get_dash_session_maker
import sys, pdb
from gflux.apps.station import sql_utils
from gflux.apps.station.models import User
from sqlalchemy.sql import select

class Command(BaseCommand):
    help = 'Initialize the SQL models of station schema'

    def handle(self, *args, **options):
        try:
            #all_user=User.objects.all()
            create_session = get_dash_session_maker()
            s = create_session()
            sql=select([User.name]).select_from(User.__table__)
            rs=s.execute(sql)
            all_user=rs.fetchall()
            s.close()
            for user in all_user:
                sql_utils.update_station_fuel_types_from_fact_trans(user.name)

        except Exception, e:
            print >> sys.stderr, "Exception: ", str(e)
