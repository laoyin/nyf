# coding=utf-8
from django.core.management.base import BaseCommand
from gflux.apps.station import models
from gflux.apps.common import models as common_models
import sys, pdb,json
from gflux.apps.station import reports
from gflux.apps.station import sql_utils
from gflux.apps.common.models import Station
from gflux.apps.station.models import Trans
from django.conf import settings
from dash.core.backends.sql.models import get_dash_session_maker
from sqlalchemy.sql import select, and_, or_
from sqlalchemy import update

class Command(BaseCommand):
    help = 'Import the id guns of station'

    def handle(self, *args, **options):
        try:
            stations=sql_utils.get_all_stations()
            for station in stations:
                data=[]
                name=station[0]
                create_session = get_dash_session_maker()
                s = create_session()
                sql = select([ Trans.pump_id]).\
                    where(and_(Trans.site==name,Trans.trans_type==0)).group_by(Trans.pump_id)
                results = s.execute(sql)
                results = results.fetchall()
                for result in results:
                    result=result.pump_id
                    if result in data:
                        continue
                    data.append(result)

                #更新油枪数量和所有油枪号
                ret = update(Station).where(Station.name==name).\
                        values(id_guns=json.dumps(data),nb_guns=len(data))
                s.execute(ret)
                s.commit()
        except Exception, e:
            print >> sys.stderr, "Exception: ", str(e)
