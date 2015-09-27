from django.core.management.base import BaseCommand
from gflux.apps.station import models
from gflux.apps.common import models as common_models
from dash.core.backends.sql.models import dash_db_manager
import sys, pdb

class Command(BaseCommand):
    help = 'Initialize the SQL models of station schema'

    def handle(self, *args, **options):
        try:
            conn = dash_db_manager.dash_engines[0].connect()
            tables = [
                models.FuelType,
                models.Location,
                common_models.Station,
                common_models.DimDateHour,
                common_models.Metadata,
                models.Trans,
                models.Card,
                models.ItemAssoc,
                models.Item,
                models.StationItemAssoc,
                models.UserStation,
                models.File,
                models.User,
                models.StationFuelType,
                models.StationNoneFuelTop
            ]
            for table in tables:
                table = table.__table__
                if not dash_db_manager.dash_engines[0].dialect.has_table(conn, table):
                    table.create(conn)
            self.stdout.write('Successfully initialized SQL models of station schema')
        except Exception, e:
            print >> sys.stderr, "Exception: ", str(e)
        finally:
            conn.close()
