"""
init dev env
"""

#django command import
from django.core.management.base import BaseCommand
from django.conf import settings

#all model import
from dash.core.backends.sql.models import *
from gflux.apps.station.models import *
from gflux.apps.common.models import *
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.orm import sessionmaker

#sys lib import
from datetime import *
import sys, pdb

class Command(BaseCommand):
    help = 'Init dev env'

    def handle(self, *args, **options):
        try:
            #create schema
            for engine in dash_db_manager.dash_engines:
                Base.metadata.create_all(bind=engine)

            self.stdout.write('finish create table...')
            
            sm=get_dash_session_maker()
            s=sm()

            #init base data
            user=User(name="tao",email="taopku@gmail.com",password="pku123", type=4)
            s.add(user)
            try:
                s.commit()
            except:
                s.rollback()

            s.close()
            

            #init dim
            for engine in dash_db_manager.dash_engines:
                sm=scoped_session(sessionmaker(bind=engine))
                s=sm()

                date=datetime(2010,1,1,0)
                index=0
                while date.year<2016:
                    tuples=date.timetuple()
                    quarter=int(date.month/3)

                    hour = {
                        'year': date.year,
                        'month': date.month,
                        'day': date.day,
                        'hour' : date.hour,
                        'week' : int(tuples[7]/7),
                        'day_of_week' : tuples[6],
                        'quater' : quarter,
                        'id' : date,
                    }

                    ins=DimDateHour(**hour)
                    s.add(ins)

                    date+=timedelta(hours=1)
                    index+=1
                    if index%1000==0:
                        try:
                            s.commit()
                        except:
                            s.rollback()
                try:
                    s.commit()
                except:
                    s.rollback()
                s.close()

            self.stdout.write('Successfully initialized dev env')
        except Exception, e:
            print >> sys.stderr, "Exception: ", str(e)
