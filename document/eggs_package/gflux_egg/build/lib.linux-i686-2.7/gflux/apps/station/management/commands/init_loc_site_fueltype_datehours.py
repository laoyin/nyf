# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from django.core.management.base import BaseCommand
from gflux.apps.station import models
from dash.core.backends.sql.models import get_dash_session_maker
from gflux.apps.common.models import *
from gflux.apps.station.models import *
from datetime import datetime,timedelta
from sqlalchemy.sql import select, and_, or_, func
from sqlalchemy import select as select_directly
from optparse import make_option
import sys,pdb,re

class Command(BaseCommand):
    def handle(self,  *args, **options):
        # 导入加油站
        Stations = [ ('SQ_GUOHUA', 'GUOHUA'), ('SQ_XINCUIWEI', 'XINCUIWEI'), ('SQ_YUETAN', 'YUETAN'),
    				('JQ_JUNPENG', 'JUNPENG'), ('JQ_GAOTA', 'GAOTA'), ('JQ_JINGANG', 'JINGANG'),
    				('CNPC_XA_ZQ','ZQ'),('CNPC_XA_DQL','DQL'),('CNPC_XA_DX','DX'),
    				('CNPC_XA_HB','HB'),('CNPC_XA_HCDL','HCDL'),('CNPC_XA_LDNL','LDNL'),
    				('CNPC_XA_NEH','NEH'),('CNPC_XA_SYXY','SYXY'),('CNPC_XA_XM','XM'),
    				('CNPC_XA_XWL','XWL'),('YCSHELL_XA','RVL'),
    				("BJ-AD","BJ-AD"),("BJ-AX","BJ-AX"),("BJ-AY","BJ-AY"),("BJ-BJS","BJ-BJS"),("BJ-BQL","BJ-BQL"),
    				("BJ-CJXF","BJ-CJXF"),("BJ-CX","BJ-CX"),("BJ-CY","BJ-CY"),("BJ-DBH","BJ-DBH"),("BJ-DJ","BJ-DJ"),
    				("BJ-FDX","BJ-FDX"),("BJ-FT","BJ-FT"),("BJ-GTZY","BJ-GTZY"),("BJ-HTBP","BJ-HTBP"),("BJ-HWL","BJ-HWL"),
    				("BJ-JDTY","BJ-JDTY"),("BJ-JFL","BJ-JFL"),("BJ-JHF","BJ-JHF"),("BJ-JXSX","BJ-JXSX"),
    				("BJ-KDFX","BJ-KDFX"),("BJ-KL","BJ-KL"),("BJ-KX","BJ-KX"),("BJ-LG","BJ-LG"),("BJ-NPZ","BJ-NPZ"),
    				("BJ-NT","BJ-NT"),("BJ-QSY","BJ-QSY"),("BJ-QX","BJ-QX"),("BJ-SG","BJ-SG"),("BJ-SHM","BJ-SHM"),
    				("BJ-SM","BJ-SM"),("BJ-SML","BJ-SML"),("BJ-SSY","BJ-SSY"),("BJ-SXX","BJ-SXX"),("BJ-TCQ","BJ-TCQ"),
    				("BJ-TH","BJ-TH"),("BJ-TZ","BJ-TZ"),("BJ-XC","BJ-XC"),("BJ-XFD","BJ-XFD"),
    				("BJ-XXC","BJ-XXC"),("BJ-YAM","BJ-YAM"),("BJ-YL","BJ-YL"),("BJ-YT","BJ-YT"),
    				("BJ-YZ","BJ-YZ"),("BJ-ZD","BJ-ZD"),("BJ-ZHC","BJ-ZHC"),
    				("YN-BY","YN-BY"),("YN-CD","YN-CD"),("YN-CGLX","YN-CGLX"),
    				("YN-DF","YN-DF"),("YN-DY","YN-DY"),("YN-GX","YN-GX"),
    				("YN-GYL","YN-GYL"),("YN-HC","YN-HC"),("YN-KD","YN-KD"),
    				("YN-LY","YN-LY"),("YN-MB","YN-MB"),("YN-MJ","YN-MJ"),
    				("YN-WJQ","YN-WJQ"),("YN-XCY","YN-XCY"),("YN-XF","YN-XF"),
    				("YN-XL","YN-XL"),("YN-XY","YN-XY"),("YN-YJS","YN-YJS"),("YN-YLGC","YN-YLGC"),
    				("SZ_HUTENGDA","SZ_HUTENGDA"), ("CDGC","CDGC"), ("CDWH","CDWH"),
    				("CCST","CCST"),("CCMF","CCMF"),("CCEML","CCEML"),("CCCC","CCCC"),("CCPQ","CCPQ"),("CCCT","CCCT")
    			]

        #每个加油站对应的locid
        Site_loc_dic={"JQ_GAOTA": 1,
        "JQ_JINGANG": 1,
        "JQ_JUNPENG": 1,
        "SQ_GUOHUA": 2,
        "SQ_XINCUIWEI": 2,
        "SQ_YUETAN": 2,
        "CNPC_XA_ZQ": 3,
        "CNPC_XA_DQL": 3,
        "CNPC_XA_DX": 3,
        "CNPC_XA_HB": 3,
        "CNPC_XA_HCDL": 3,
        "CNPC_XA_LDNL": 3,
        "CNPC_XA_NEH": 3,
        "CNPC_XA_SYXY": 3,
        "CNPC_XA_XM": 3,
        "CNPC_XA_XWL": 3,
        "YCSHELL_XA": 3,
        "BJ-AD":4,
        "BJ-AX":4,
        "BJ-AY":4,
        "BJ-BJS":4,
        "BJ-BQL":4,
        "BJ-CJXF":4,
        "BJ-CX":4,
        "BJ-CY":4,
        "BJ-DBH":4,
        "BJ-DJ":4,
        "BJ-FDX":4,
        "BJ-FT":4,
        "BJ-GTZY":4,
        "BJ-HTBP":4,
        "BJ-HWL":4,
        "BJ-JDTY":4,
        "BJ-JFL":4,
        "BJ-JHF":4,
        "BJ-JXSX":4,
        "BJ-KDFX":4,
        "BJ-KL":4,
        "BJ-KX":4,
        "BJ-LG":4,
        "BJ-NPZ":4,
        "BJ-NT":4,
        "BJ-QSY":4,
        "BJ-QX":4,
        "BJ-SG":4,
        "BJ-SHM":4,
        "BJ-SM":4,
        "BJ-SML":4,
        "BJ-SSY":4,
        "BJ-SXX":4,
        "BJ-TCQ":4,
        "BJ-TH":4,
        "BJ-TZ":4,
        "BJ-XC":4,
        "BJ-XFD":4,
        "BJ-XXC":4,
        "BJ-YAM":4,
        "BJ-YL":4,
        "BJ-YT":4,
        "BJ-YZ":4,
        "BJ-ZD":4,
        "BJ-ZHC":4,
        "YN-BY":5,
        "YN-CD":5,
        "YN-CGLX":5,
        "YN-DF":5,
        "YN-DY":5,
        "YN-GX":5,
        "YN-GYL":5,
        "YN-HC":5,
        "YN-KD":5,
        "YN-LY":5,
        "YN-MB":5,
        "YN-MJ":5,
        "YN-WJQ":5,
        "YN-XCY":5,
        "YN-XF":5,
        "YN-XL":5,
        "YN-XY":5,
        "YN-YJS":5,
        "YN-YLGC":5,
        "SZ_HUTENGDA":6,
        "CDGC": 7,
        "CDWH": 7,
        "CCCC": 8,
        "CCCT": 8,
        "CCEML": 8,
        "CCMF": 8,
        "CCPQ": 8,
        "CCST": 8
        }
        # 每个加油站的油枪数量
    	G = {   "JQ_GAOTA": 13,
		"JQ_JINGANG": 11,
		"JQ_JUNPENG": 8,
		"SQ_GUOHUA": 17,
		"SQ_XINCUIWEI": 17,
		"SQ_YUETAN": 12,
		"CNPC_XA_ZQ": 10,
		"CNPC_XA_DQL": 16,
		"CNPC_XA_DX": 16,
		"CNPC_XA_HB": 10,
		"CNPC_XA_HCDL": 24,
		"CNPC_XA_LDNL": 34,
		"CNPC_XA_NEH": 12,
		"CNPC_XA_SYXY": 8,
		"CNPC_XA_XM": 7,
		"CNPC_XA_XWL": 16,
		"YCSHELL_XA": 12,
		"BJ-AD":16,
		"BJ-AX":8,
		"BJ-AY":16,
		"BJ-BJS":12,
		"BJ-BQL":8,
		"BJ-CJXF":16,
		"BJ-CX":8,
		"BJ-CY":3,
		"BJ-DBH":12,
		"BJ-DJ":14,
		"BJ-FDX":32,
		"BJ-FT":8,
		"BJ-GTZY":23,
		"BJ-HTBP":16,
		"BJ-HWL":4,
		"BJ-JDTY":12,
		"BJ-JFL":3,
		"BJ-JHF":10,
		"BJ-JXSX":23,
		"BJ-KDFX":18,
		"BJ-KL":12,
		"BJ-KX":12,
		"BJ-LG":12,
		"BJ-NPZ":8,
		"BJ-NT":16,
		"BJ-QSY":15,
		"BJ-QX":16,
		"BJ-SG":11,
		"BJ-SHM":8,
		"BJ-SM":12,
		"BJ-SML":5,
		"BJ-SSY":12,
		"BJ-SXX":16,
		"BJ-TCQ":16,
		"BJ-TH":19,
		"BJ-TZ":16,
		"BJ-XC":12,
		"BJ-XFD":16,
		"BJ-XXC":2,
		"BJ-YAM":24,
		"BJ-YL":16,
		"BJ-YT":12,
		"BJ-YZ":12,
		"BJ-ZD":14,
		"BJ-ZHC":12,
		"YN-BY":24,
		"YN-CD":16,
		"YN-CGLX":8,
		"YN-DF":24,
		"YN-DY":8,
		"YN-GX":20,
		"YN-GYL":32,
		"YN-HC":6,
		"YN-KD":10,
		"YN-LY":19,
		"YN-MB":32,
		"YN-MJ":12,
		"YN-WJQ":10,
		"YN-XCY":34,
		"YN-XF":16,
		"YN-XL":10,
		"YN-XY":36,
		"YN-YJS":20,
		"YN-YLGC":8,
		"SZ_HUTENGDA":24,
		"CDGC": 6,
		"CDWH": 20,
		"CCCC": 12,
		"CCCT": 32,
		"CCEML": 14,
		"CCMF": 12,
		"CCPQ": 23,
		"CCST": 8
    	}

        # 创建缺省帐号
        user=User(name="tao",email="taopku@gmail.com",password="pku123", type=4)
        try:
            user.save()
        except Exception, e:
            print e

    	# 导入所有的站点
    	new_sites=[]
    	for site in Stations:
    	    name=site[0]
    	    description=site[1]
    	    if name in G.keys() :
		        nb_guns=G[name]
    	    else:
                nb_guns=0
                print 'faild get guns number for '+name

            site_dic = {
    		'name':name,
    		'description':description,
    		'nb_guns':nb_guns,
    		'locid':Site_loc_dic[name],
    	    }

            # 更新用户站点信息，不然缺省帐号无法看到
            #site=UserStation(user_id=user.id,station=name)
	    try :
		create_session = get_dash_session_maker()
		s = create_session()
		s.query(UserStation).update({
		  UserStation.user_id: int(user.id),
		  UserStation.station:name
		})
		s.commit()
		s.close()
            #try :
            #    site.save()
            except Exception, e:
                print e

    	    new_sites.append(site_dic)

        create_session = get_dash_session_maker()
    	s = create_session()
        if len(new_sites) > 0:
    	    try:
            	s.execute(Station.__table__.insert(), new_sites)
            	s.commit()
            except Exception,e:
                s.rollback()
                print e
    	s.close()

        # 预设地址
    	locs=[]
    	locs.append(('ALL',0, u'全部',len(Stations)))
    	locs.append(('JQ', 1,u'未知', 3))
    	locs.append(('SQ', 2,u'未知', 3))
    	locs.append(('XA_CN', 3,u'西安', 11))
    	locs.append(('BJ_CN', 4,u'北京', 45))
    	locs.append(('YN_CN', 5,u'云南', 19))
    	locs.append(('SZ_CN', 6,u'深圳', 1))
    	locs.append(('SC_CN', 7,u'四川',2))
    	locs.append(('JL_CN', 8,u'吉林', 6))

            # 导入地址
    	new_locs=[]
    	for loc in locs:
    	    name=loc[0]
    	    id=loc[1]
    	    description=loc[2]
    	    nb_sites=loc[3]
    	    loc_dic={
    		'id':id,
    		'name':name,
    		'description':description,
    		'nb_sites':nb_sites
    	    }
    	    new_locs.append(loc_dic)

        create_session = get_dash_session_maker()
    	s = create_session()
    	if len(new_locs) > 0:
            try :
                s.execute(Location.__table__.insert(), new_locs)
                s.commit()
            except Exception,e:
                s.rollback()
                print e
    	s.close()

        # 导入汽油类型
    	FuelTypes = enum(
    	    #北京数据条形码
    	    FUEL_92=(300585, u'92号油'),
    	    FUEL_95=(300586, u'95号油'),
    	    FUEL_DIESEL_0=(300566, u"0号普通柴油"),
    	    FUEL_AUTO_DIESEL_20=(300601, u"-20号车用柴油"),
    	    FUEL_AUTO_DIESEL_10=(300602, u"-10号车用柴油"),
    	    FUEL_AUTO_DIESEL_0=(300603, u"0号车用柴油"),
    	    #西安数据条形码
    	    #select barcode, min("desc") from fact_trans where location=3 and pump_id>0 group by barcode;
    	    CNPC_XA_ZQ_FUEL_93_3=(300060,u'93号 车用汽油(Ⅲ)'),
    	    CNPC_XA_ZQ_FUEL_93_4=(300590,u'93号 车用汽油(Ⅳ)'),
    	    CNPC_XA_ZQ_FUEL_97_3=(300061,u'97号 车用汽油(Ⅲ)'),
    	    CNPC_XA_ZQ_FUEL_0_3=(300472,u'0号 车用柴油(Ⅲ)'),
    	    CNPC_XA_ZQ_FUEL_97_4=(300591,u'97号 车用汽油(Ⅳ)'),
    	    CNPC_XA_ZQ_FUEL_DIESEL_10_3=(300471,u'-10号 车用柴油(Ⅲ)'),
    	    #YCSHELL XIAN
    	    YCSHELL_XA_97=(97,u'97号汽油'),
    	    YCSHELL_XA_93=(93,u'93号汽油'),
    	    #cnpc-beijing
    	    FUEL_AUTO_DIESEL_30=(300401,u'-30号 车用柴油(京Ⅳ)'),
    	    FUEL_90=(300003,u'90号 车用乙醇汽油'),
    	    #hutengda
    	    HUTENGDA_0=(60189274,u'0'),
    	    HUTENGDA_592=(60206059,u'592'),
    	    HUTENGDA_397=(60090936,u'397'),
    	    HUTENGDA_598=(60209058,u'598'),
    	    HUTENGDA_595=(60206060,u'595'),
    	    HUTENGDA_398=(60090937,u'398'),
    	    HUTENGDA_393=(60090935,u'393'),
    	    #SC-CN
    	    SC_CN_98_3=(300314, u'98号 车用汽油(Ⅲ)'),
    	    SC_CN_97_3=(300061, u'97号 车用汽油(Ⅲ)'),
    	    SC_CN_97_4=(300591, u'97号 车用汽油(Ⅳ)'),
    	    SC_CN_93_4=(300590, u'93号 车用汽油(Ⅳ)'),
    	    SC_CN_0_3=(300472, u'0号 车用柴油(Ⅲ)'),
    	    SC_CN_98_4=(300653, u'98号 车用汽油(Ⅳ)'),
    	    #JL-CN
    	    JL_CN_93_E10=(300656, u"93号 车用乙醇汽油(E10) GB18351-2013"),
    	    JL_CN_0=(300566 , u"0号 普通柴油"),
    	    JL_CN_93=(300007, u"93号 车用乙醇汽油"),
    	    JL_CN_97_E10=(300657, u"97号 车用乙醇汽油(E10) GB18351-2013"),
    	    JL_CN_0_3=(300472, u"0号 车用柴油(Ⅲ)"),
    	    JL_CN_35_3=(300550, u"-35号 车用柴油(Ⅲ)"),
    	    JL_CN_20=(300567, u"-20号 普通柴油"),
    	    JL_CN_20_3=(300470, u"-20号 车用柴油(Ⅲ)"),
    	    JL_CN_97=(300014, u"97号 车用乙醇汽油")
    	)

    	# 构建从numid到中文名的映射
        Fuels = FuelTypes.tuples()
        name_descs={}
        for fuel in Fuels:
            name_descs[fuel[0]]=fuel[1]

        # 从JL_CN_97到标号的映射开始列出三元组
        Fuel_keys = FuelTypes.KEYS
        for name in Fuel_keys:
            numid=Fuel_keys[name]
            description=name_descs[numid]
            # 检查是否已经存在
            sql=select_directly([FuelType.id]).where(or_(FuelType.name==name,
                                                         FuelType.numid==str(numid),
                                                         FuelType.description==description)).label('tao-gilbarco')

            rs=s.query(sql)
            ret=rs.first()
            if ret!=None and ret[0]!=None:
                continue

            # 创建不存在的
    	    fuel_dic={
    		'name':name,
    		'numid':str(numid),
    		'description':description
    	    }
            try :
                s.execute(FuelType.__table__.insert(), [fuel_dic])
                s.commit()
            except Exception,e:
                s.rollback()
                print e

        # 获取所有的datehour存入数据库

        start_date=datetime(2013,1,1,0)
        date=start_date
        index=0

        while date.year<2016:

            sql=select_directly([DimDateHour.id]).where(and_(DimDateHour.year==date.year,
                                                             DimDateHour.month==date.month,
                                                             DimDateHour.day==date.day,
                                                             DimDateHour.hour==date.hour)).label('tao-gilbarco')
            rs=s.query(sql)
            ret=rs.first()

            if ret!=None and ret[0]!=None:
                date+=timedelta(hours=1)
                continue

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
                s.commit()

        # 提交

        try :
            s.commit()
        except Exception,e:
            s.rollback()
            print e

        s.close()
