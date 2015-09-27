# coding=utf-8
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')

import sys
from sqlalchemy.sql import select, func, and_
from django.utils.datastructures import SortedDict
from dash.core.backends.sql.models import get_dash_session_maker
from dash.core.types import Singleton
from django.core.cache import cache
from . import models
import pdb,hashlib,json
from django.conf import settings

class CubeException(Exception):
    "Cube Exception"

class CubeDefiningClass(Singleton):
    def __new__(cls, name, bases, attrs):
        new_class = super(CubeDefiningClass, cls).__new__(cls, name, bases, attrs)
        if new_class.__name__ not in ['Cube']:
            if not issubclass(new_class.fact_table, models.Base):
                raise CubeException("Cube class '%s' failed to be created due to unrecognized type of fact table"
                                    % new_class.__name__)

        new_class.d = type('Dim', (object, ), {})()
        new_class.d.__dict__ = new_class.dims
        new_class.m = type('Measures', (object, ), {})()
        measures = {}
        for m, agg in new_class.measures.items():
            measures[m] = agg.func(agg.col)
        new_class.m.__dict__ = measures

        if new_class.fact_table is not None:
            new_class.fact_table = new_class.fact_table.__table__
        new_joins = {}
        for table, clause in new_class.joins.items():
            new_joins[table.__table__] = clause
        new_class.joins = new_joins
        # TODO: more checks
        return new_class

class Aggregation(object):

    def __init__(self, _func, _col):
        self.func = _func
        self.col = _col

    @staticmethod
    def count(col):
        return Aggregation(func.count, col)

    @staticmethod
    def sum(col):
        return Aggregation(func.sum, col)

    @staticmethod
    def max(col):
        return Aggregation(func.max, col)

    @staticmethod
    def min(col):
        return Aggregation(func.min, col)

    @staticmethod
    def avg(col):
        return Aggregation(func.avg, col)


class Cube(object):
    __metaclass__ = CubeDefiningClass
    fact_table = None
    joins = {}
    measures = {}
    dims = {}
    details = {}

    def __init__(self):
        self.session = None

    def __del__(self):
        if self.session!=None:
            self.session.close()

    def aggregate(self,session_factory=None, measures=None, drilldown=[],
                  conditions=[], details=[],
                  having=None, order=None, limit=None, session=None):
        # choose which session to use by conditions
        if session is None:
            site_name=None
            for cond in conditions:
                if hasattr(cond,'left')==False:
                    continue
                if cond.left.name=='site':
                    if hasattr(cond.right,'value'):
                        site_name=cond.right.value
                        break
            if session_factory!=None:
                session=session_factory(site_name)
            else:
                create_session=get_dash_session_maker(site_name)#got
                self.session = create_session()
                session = self.session

        columns = []
        if measures is None:
            measures = self.measures.keys()

        for c in measures:
            agg = self.measures[c]
            columns.append(agg.func(agg.col).label(c))

        for c in details:
            try:
                columns.append(func.max(self.details[c]).label(c))
            except:
                pass
                #print >> sys.stderr, 'ERROR: %s is not defined in details' % c

        table_to_join = set()
        drilldown_columns = []
        for c in drilldown:
            dim = self.dims[c]
            columns.append(dim.label(c))
            drilldown_columns.append(dim)
            table = dim.class_.__table__
            if table != self.fact_table:
                table_to_join.add(table)

        for condition in conditions:
            if hasattr(condition,'left'):
                table = condition.left.table
                if table != self.fact_table:
                    table_to_join.add(table)

        join_expr = self.fact_table
        for table in table_to_join:
            join_expr = join_expr.join(table, onclause=self.joins[table])

        sql = select(columns).select_from(join_expr)

        if conditions:
            sql = sql.where(and_(*conditions))

        if drilldown_columns:
            sql = sql.group_by(*drilldown_columns)

        if having is not None:
            sql = sql.having(having)

        if order:
            sql = sql.order_by(order)

        if isinstance(limit, int):
            sql = sql.limit(limit)

        results = []
        sql = sql.apply_labels()
        try:
            #check cache
            cache_sha1=hashlib.sha1()

            sql_params_dict=sql.compile().params
            from sqlalchemy.dialects import postgresql
            dialect = postgresql.dialect()
            raw_sql=unicode(sql.compile(dialect=dialect))%sql_params_dict
            print '\n\n%s\n\n'%raw_sql
            cache_sha1.update(raw_sql)
            cache_key=cache_sha1.hexdigest()

            cache_value=cache.get(cache_key)

            if cache_value!=None:
                try:
                    results=json.loads(cache_value)
                except Exception,e:
                    results=[]

            if results==[]:
                rows = session.execute(sql)
                for row in rows:
                    d = SortedDict()
                    for c in drilldown:
                        d[c] = row[c]
                    for c in measures:
                        if row[c]==None:
                            d[c] = 0
                        else:
                            d[c] = row[c]
                    for c in details:
                        d[c] = row[c]
                    results.append(d)
                rows.close()

                #set in cache
                try:
                    from gflux.util import json_encoder
                    cache.set(cache_key,json.dumps(results,default=json_encoder),settings.CUBES_MEMCACHED_TIMEOUT)
                except Exception,e:
                    pass

        except Exception, e:
            session.rollback()

        return results

    def error(self, msg):
        raise CubeException("<%s> %s" % (self.__class__.__name__, msg))
