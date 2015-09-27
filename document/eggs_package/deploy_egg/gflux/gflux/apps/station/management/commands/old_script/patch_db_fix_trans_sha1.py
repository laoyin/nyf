# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from django.core.management.base import BaseCommand
from dash.core.backends.sql.models import get_dash_session_maker
from gflux.apps.station.models import *
from gflux.apps.common.models import *
import pdb

class Command(BaseCommand):
    def handle(self,  *args, **options):
        create_session = get_dash_session_maker()
    	s = create_session()

        #by site
        all_station=s.query(Station).all()

        all_counter=0
        for station in all_station:
            tmp_sm=get_dash_session_maker(site_name=station.name)
            ss=tmp_sm()

            limit=100000
            min_id=0
            while True:
                all_item=ss.query(Trans).filter(Trans.site==station.name,Trans.id>min_id).limit(limit).all()
                if len(all_item)==0:
                    break

                counter=0
                for item in all_item:
                    if item.id>min_id:
                        min_id=item.id

                    counter+=1
                    all_counter+=1
                    item.compute_sha1()

                    #need batch commit?
                    if counter%10000==0:
                        try:
                            ss.commit()
                        except Exception,e:
                            ss.rollback()
                            print e
                        finally:
                            print 'finish %s'%all_counter

                try:
                    ss.commit()
                except Exception,e:
                    ss.rollback()
                    print e
                finally:
                    print 'finish %s'%all_counter
            ss.close()
            print 'finish site %s'%station.name

        s.close()
        print 'finish all'
