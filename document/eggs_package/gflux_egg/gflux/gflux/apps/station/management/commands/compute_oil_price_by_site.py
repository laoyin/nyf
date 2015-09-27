# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from django.core.management.base import BaseCommand
from dash.core.backends.sql.models import get_dash_session_maker
from gflux.apps.station.models import Trans,StationFuelType
from gcustomer.models import StationProfile
from gflux.apps.common.models import Station
from datetime import datetime
from optparse import make_option
import sys,pdb,re
from sqlalchemy import update

class Command(BaseCommand):
    help = 'Compute price'
    option_list = BaseCommand.option_list + (
        make_option('--site',help="set site code",type="string"),
    )

    def handle(self,  *args, **options):
	print 'start...'
	site=options['site']
	try:	
	    price_s = get_dash_session_maker()()
	    if site == '' :
		stations = price_s.query(Station).all()
		for station in stations :
		    print station.name +"..."
		    try:
		        create_session_func = get_dash_session_maker(station.name)
	                session = create_session_func()
		    except:
			pass
		    site = station.name
		    results = price_s.query(StationFuelType).filter_by(station=site).all()
		    for result in results:
		        price_sql = 'select price from fact_trans where site=\'%s\' and barcode=%d order by timestamp desc limit(1);'%(site,int(result.barcode))
			price_results = session.execute(price_sql).fetchall()
			if len(price_results) >= 1:
			    stmt = update(StationFuelType).where(StationFuelType.station==site).\
                               values(price=price_results[0].price)
			    price_s.execute(stmt)
            		    price_s.commit()
            else :
		create_session_func = get_dash_session_maker(site)
                session = create_session_func()
	        results = price_s.query(StationFuelType).filter_by(station=site).all()
	        for result in results:
		    price_sql = 'select price from fact_trans where site=\'%s\' and barcode=%d order by timestamp desc limit(1);'%(site,int(result.barcode))
		    price_results = session.execute(price_sql).fetchall()
		    if len(price_results) >= 1:
		        stmt = update(StationFuelType).where(StationFuelType.station==site).\
                               values(price=price_results[0].price)
			price_s.execute(stmt)
            		price_s.commit()
	    price_s.close()
	    session.close()
	except Exception,e:
		print e
	print 'end...'
