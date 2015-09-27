from django.core.management.base import BaseCommand
from gflux.apps.common import models
from dash.core.backends.sql.models import dash_db_manager
from datetime import datetime, timedelta
import sys

def init_dim_datetime(conn):
    table = models.DimDateHour.__table__
    if dash_db_manager.dash_engines[0].dialect.has_table(conn, table):
        return
    table.create(conn)
    dates = []
    start_date = datetime(2013, 1, 1)
    end_date = start_date + timedelta(days=1826)
    print "The dim_date ranges from %s to %s" % (start_date, end_date)
    while start_date < end_date:
        dates.append({
            'id': start_date,
            'year': start_date.year,
            'month': start_date.month,
            'day': start_date.day,
            'hour': start_date.hour,
            'week': int(start_date.strftime('%W')),
            'day_of_week': start_date.isoweekday(),
            'quater': (start_date.month - 1) / 3 + 1,
        })
        start_date += timedelta(hours=1)

    conn.execute(table.insert(), dates)

class Command(BaseCommand):
    help = 'Initialize the SQL models of common schema'

    def handle(self, *args, **options):
        try:
            conn = dash_db_manager.dash_engines[0].connect()
            init_dim_datetime(conn)
            tables = [
                models.Metadata,
            ]
            for table in tables:
                table = table.__table__
                if not dash_db_manager.dash_engines[0].dialect.has_table(conn, table):
                    table.create(conn)
            self.stdout.write('Successfully initialized SQL models of common schema')
        except Exception, e:
            print >> sys.stderr, "Exception: ", str(e)
        finally:
            conn.close()
