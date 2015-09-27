# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from django.core.management.base import BaseCommand
from dash.core.backends.sql.models import get_dash_session_maker
from optparse import make_option
from gflux.apps.station.models import User
from gflux.apps.station.sql_utils import *
import sys,pdb,os,re,datetime
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Import Ycshell Trans from CSV ALL+CARD'

    option_list = BaseCommand.option_list + (
        make_option('--dir',help="set file dir",type="string"),
        make_option('--user',help="set username",type="string"),
        make_option('--location_name',help="set location name like SC_CN",type="string"),
        make_option('--site',help="set site name",type="string"),
    )

    def handle(self,  *args, **options):
        #get args
        location=options['location_name'].upper()

        plocation=re.compile(r'^[A-Z_]+$')
        plocation_desc=re.compile(u'^[\u4e00-\u9fa5a-zA-Z0-9_]{1,}$')

        #check
        if plocation.match(location)==None:
            print 'location only in A-Z_'
            sys.exit(-1)


        file_dir=options['dir']
        username=options['user']

        sm=get_dash_session_maker()
        s=sm()
        user=s.query(User).filter_by(name=username).one()
        user_id=user.id
        s.close()

        #start
        for parent,dirnames,filenames in os.walk(file_dir):

            #get all card file and site name
            all_file=os.path.join(parent,'all.txt')
            card_file=os.path.join(parent,'card.txt')

            #check
            if os.path.exists(all_file) and os.path.exists(card_file):
                pass
            else:
                continue

            site=options['site'].upper()
            site_desc=get_site_desc_by_name(site)

            if site_desc==None:
                site_desc = site

            #check
            if plocation.match(site)==None:
                print 'site only in A-Z_'
                continue

            args = {'need_update_station_info':False}
            #save location and station
            location_desc = get_location_desc_by_id(location)
            if location_desc == None:
                location_desc = location
            locid=get_location_id(location,location_desc)
            station_id,created=get_station_id(site,user_id=user_id,site_desc=site_desc,
                with_created_status=True)

            args['need_update_station_info']=True

            #gearman 参数
            args['locid']=locid
            args['station_id']=station_id
            args["site"] = site
            args['site_desc']=site_desc
            args['location']=location
            args['location_desc']=location_desc
            args['log_file']=settings.BASE_DIR+'/file/'+username+'/process.log'
            args['userid']=user_id
            args['username']=username
            args['station_id']=station_id

            args['all_file']=all_file
            args['card_file']=card_file

            #检查是否导入完成
            args['import_flag_string']=location+'@'+site+'@'+str(
                datetime.datetime.now().microsecond)

            result=call_command('gearman_submit_job', 'import_yc_data',
                json.dumps(args), foreground=False)
