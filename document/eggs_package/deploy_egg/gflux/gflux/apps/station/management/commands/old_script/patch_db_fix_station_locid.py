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
from sqlalchemy import update
from optparse import make_option
import sys,pdb,re

#每个加油站对应的locid
Site_loc_dic={
    "JQ_GAOTA": 1,
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

class Command(BaseCommand):
    def handle(self,  *args, **options):
        create_session = get_dash_session_maker()
    	s = create_session()

        for name in Site_loc_dic:
            stmt = update(Station).where(Station.name==name).\
                    values(locid=Site_loc_dic[name])
            try:
                s.execute(stmt)
                s.commit()
            except Exception,e:
                s.rollback()
                print e

        s.close()
