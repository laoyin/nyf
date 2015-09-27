
# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from dash.core.backends.sql.models import get_dash_session_maker
from gflux.apps.station.sql_utils import get_or_create
from optparse import make_option
from gcustomer.models import *
import pdb,json
from django.core.management.base import BaseCommand
import xml.etree.ElementTree as ET

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--user_source',help="指定集团值，请参考UserCardType的定义"),
        make_option('--file',help='指定xml文件路径')
    )

    def handle(self, **options):
        print 'start...'

        #get file content
        user_source=int(options['user_source'])
        file=open(options['file'],'r')
        file_content=file.read()
        file.close()

        #analyze
        print 'load file content...'
        root=ET.fromstring(file_content)

        #init db session
        print 'init db session....'
        session=get_dash_session_maker()()
        session_counter=0

        #commit tools func
        def submit_data_to_db():
            session_counter=0
            try:
                session.commit()
            except Exception,e:
                print 'submit db transaction faild, error:',str(e)
                session.rollback()

        #聚合情况
        print 'analyze grouped info....'
        grouped_map={}
        groups_node=root.find('groups')
        for group_node in groups_node:
            group_id_flag=group_node.get('id')
            users=[]
            users_node=group_node.find('users')
            for user_node in users_node:
                user_cardnum=user_node.text
                users.append(user_cardnum)
            items=[]
            items_node=group_node.find('items')
            for item_node in items_node:
                item_name=item_node.text
                items.append(item_name)

            #save to db  source_id : 0 系统创建
            obj=CustomerGroup(group_name="系统群",user_source=user_source,source_id = 0,user_list=json.dumps(users),
                favourite_products=json.dumps(items))
            session.add(obj)
            submit_data_to_db()
            grouped_map[group_id_flag]=obj.id

        #经常购买和推荐购买
        print 'analyze favorite and recommend info...'
        users_node=root.find('users')
        for user_node in users_node:
            try :
                    user_cardnum=int(user_node.get('card'))
                    favorite_items=[]
                    favorites_node=user_node.find('fav-items')
                    for favorite_node in favorites_node:
                        item_name=favorite_node.text
                        favorite_items.append(item_name)

                    recommend_items=[]
                    recommends_node=user_node.find('recommend-items')
                    for recommend_node in recommends_node:
                        item_name=recommend_node.text
                        recommend_items.append(item_name)

                    grouped_ids=[]
                    for flag_id_node in user_node.find('groups'):
                        grouped_ids.append(grouped_map[flag_id_node.text])
                    obj,created=get_or_create(session,CustomerProfile,
                        user_source=user_source,cardnum=user_cardnum,
                        defaults=dict(
                            favourite_nonfuel_products=json.dumps(favorite_items),
                            recommended_nonfuel_products=json.dumps(recommend_items),
                            grouped=json.dumps(grouped_ids)
                        )
                    )

                    if not created:
                        obj.favourite_nonfuel_products=json.dumps(favorite_items)
                        obj.recommended_nonfuel_products=json.dumps(recommend_items)
                        obj.grouped=json.dumps(grouped_ids)
            except Exception,e:
                pass

            #using session counter
            session_counter+=1
            if session_counter%1000==0:
                submit_data_to_db()

        #submit remaind data
        submit_data_to_db()

        #close session
        session.close()

        print 'end...'
