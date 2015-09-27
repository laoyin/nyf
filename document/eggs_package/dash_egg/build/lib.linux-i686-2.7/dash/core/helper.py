# coding=utf-8
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')
from . import reports
from dash.core.types import overrides
import pdb

class CubePlanarReport(reports.Report):
    __abstract__ = True

    cube = None
    conditions = []
    vertical = []
    horizonal = []
    details = []
    series = None
    series_options = {}
    chart_options = {}

    def __init__(self,*args,**kwargs):
        super(CubePlanarReport, self).__init__(*args,**kwargs)
        #print 'init ',self.uid,' report...'

    def init_conditions(self):
        raise NotImplementedError

    def post_init_conditions(self,**kwargs):
        pass

    def build_categories(self,**kwargs):
        raise NotImplementedError

    def build_result(self, result, stat,**kwargs):
        raise NotImplementedError

    def series_name(self, series=None):
        raise NotImplementedError

    def build_extra(self, data):
        pass

    @overrides(reports.Report)
    #整理plot 数据
    def report(self, request, *args, **kwargs):
        conditions = self.init_conditions(**kwargs) + self.conditions
        self.post_init_conditions(**kwargs)
        if self.series:
            drilldown = [self.series] + self.horizonal
        else:
            drilldown = self.horizonal

        results = self.cube.aggregate(
            session_factory=request.get_session,
            measures=self.vertical,
            drilldown=drilldown,
            conditions=conditions,
            details=self.details)
        stats = {}
        if self.series:
            for result in results:
                stats.setdefault(result[self.series], {})
                self.build_result(result, stats[result[self.series]])
        else:
            stats.setdefault(None, {})
            for result in results:
                self.build_result(result, stats[None],**kwargs)

        items = stats.items()

        categories = self.build_categories(items,**kwargs)
        data = {
            "categories": categories,
            "dataset": []
        }
        if self.chart_options:
            data['opts'] = self.chart_options
        for series, stat in items:
            opt = {"data": [], "name": self.series_name(series)}
            opt.update(self.series_options)
            for cat in categories:
                try:
                    value = stat[cat]
                except:
                    value = 0
                opt["data"].append(value)
            data["dataset"].append(opt)
        self.build_extra(data)
        return data
