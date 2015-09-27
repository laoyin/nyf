# coding: utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import pdb,json
from django.conf import settings
from django.core.cache import cache

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm.scoping import scoped_session

from dash.core.types import Singleton

Base = declarative_base()

class ShardStat(Base):
    __tablename__ = 'shard_stat'
    shard_name=Column(String(30), nullable=False, primary_key=True)
    nb_sites=Column(Integer, default=0)
    shard_id=Column(Integer)

class SiteShard(Base):
    __tablename__='site_shard'
    site_name=Column(String(300), nullable=False, primary_key=True)
    shard_id=Column(Integer)

#数据库管理类
class DBManager(object):
    __metadata__=Singleton
    """
    在实例化类时根据setting中的设置来初始化所有的数据库连接和session maker

    提供接口来取得session
    """
    def __init__(self,keep_session=False):
        #cache
        self.dash_engines = []

        #check db
        if len(settings.SQL_BACKENDS)==0:
            raise Exception('Settings SQL_BACKENDS need one db at least!')

        #初始化数据库连接
        #初始化session marker
        for backend in settings.SQL_BACKENDS:
            engine = create_engine(
                backend['db_url'],
                pool_size=backend['db_pool_size'],
                echo=settings.SQL_DEBUG,
                encoding=backend['db_charset'],
                pool_recycle=backend['db_pool_recycle']
            )
            self.dash_engines.append(engine)

        #初始化shardstat
        idx=0
        s=scoped_session(sessionmaker(bind=self.dash_engines[0]))()
        for db_setting in settings.SQL_BACKENDS:
            ss=ShardStat(shard_name=db_setting['db_name'],
                shard_id=idx)
            s.add(ss)
            idx+=1
            try:
                s.commit()
            except:
                s.rollback()

        s.close()

    #读cache中shar id
    def read_shard_id_from_cache(self,site_name):
        key='shard_id_of_site_'+site_name
        value=cache.get(key)
        if value==None:
            data=None
        else:
            data=json.loads(value)
        return data

    #写shared_id缓存
    def write_shard_id_to_cache(self,site_name,shard_id):
        key='shard_id_of_site_'+site_name
        cache.set(key,json.dumps(shard_id),settings.NEVER_MEMCACHED_TIMEOUT)

    #根据对应的site name返回session maker
    def getSessionMaker(self,site_name=None,with_shard_id=False):
        default_shard_id=0
        if site_name==None:
            shard_id=default_shard_id
            engine=self.dash_engines[shard_id]
            if with_shard_id:
                return shard_id,scoped_session(sessionmaker(bind=engine))
            else:
                return scoped_session(sessionmaker(bind=engine))
        else:
            shard_id=self.read_shard_id_from_cache(site_name)

            #get it!
            if shard_id!=None:
                engine=self.dash_engines[shard_id]
                if with_shard_id:
                    return shard_id,scoped_session(sessionmaker(bind=engine))
                else:
                    return scoped_session(sessionmaker(bind=engine))


            #缓存未找到,查询数据库
            s=scoped_session(sessionmaker(bind=self.dash_engines[0]))()
            try:
                obj=s.query(SiteShard).filter_by(site_name=site_name).one()
                shard_id=obj.shard_id

                engine=self.dash_engines[shard_id]
                self.write_shard_id_to_cache(site_name,shard_id)
                if with_shard_id:
                    return shard_id,scoped_session(sessionmaker(bind=engine))
                else:
                    return scoped_session(sessionmaker(bind=engine))
            except:
                shard_id=None

            #数据库没有则新增
            obj=s.query(ShardStat).order_by(ShardStat.nb_sites).first()
            shard_id=obj.shard_id
            min_nb_sites=obj.nb_sites

            #没空间
            if min_nb_sites>=settings.MAX_NB_SITES:
                raise Exception('OUT OF SPACE ON ALL SHARD!')

            new_obj=SiteShard(site_name=site_name,shard_id=shard_id)
            s.add(new_obj)
            obj.nb_sites+=1

            try:
                s.commit()
            except:
                s.rollback()

            s.close()

            # update cache
            self.write_shard_id_to_cache(site_name,shard_id)
            engine=self.dash_engines[shard_id]
            if with_shard_id:
                return shard_id,scoped_session(sessionmaker(bind=engine))
            else:
                return scoped_session(sessionmaker(bind=engine))
    def app_getSessionMaker(self):
        engine=self.dash_engines[1]
        return scoped_session(sessionmaker(bind=engine))

    #关闭所有的数据库连接
    def __del__(self):
        pass

dash_db_manager=DBManager()
get_dash_session_maker=dash_db_manager.getSessionMaker
get_app_session_maker=dash_db_manager.app_getSessionMaker
