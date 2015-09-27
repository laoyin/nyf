# coding=utf-8
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')

import sys
import re
import copy
from abc import ABCMeta
from dash.core.types import Singleton

__all__ = ['Extractor', 'RegexExtractorRule']

class RegexExtractorRule(object):
    def __init__(self, pattern, callback=None, exclusive=False):

        try:
            if isinstance(pattern, (str, unicode)):
                self.pattern = re.compile(pattern)
            else:
                raise TypeError
        except Exception, e:
            #print >> sys.stderr, '[ERROR] the pattern of ExtractorRule cannot be compiled: %s' % str(e)
            sys.exit(1)
        self.callback = callback
        self.exclusive = exclusive


class ExtractorDefiningClass(ABCMeta, Singleton):
    def __new__(cls, name, bases, attrs):
        new_class = super(ExtractorDefiningClass, cls).__new__(cls, name, bases, attrs)
        new_class.rules.sort(key=lambda x: x.exclusive, reverse=True)
        return new_class

class Extractor(object):
    __metaclass__ = ExtractorDefiningClass
    rules = []

    def __init__(self, stream):
        self.stream = stream
        self._rules = [copy.copy(r) for r in self.rules]

        def get_method(method):
            if callable(method):
                return method
            elif isinstance(method, str):
                return getattr(self, method, None)

        for rule in self._rules:
            rule.callback = get_method(rule.callback)
        self._lock = False

    def lock(self):
        self._lock = True

    def unlock(self):
        self._lock = False

    def islocked(self):
        return self._lock

    def extract(self):
        if self.islocked():
            #print >> sys.stderr, '[ERROR] Extractor is locked, so return None and exit'
            return
        try:
            self.lock()
            for line in self.stream:
                line = line.strip()
                if line == "":
                    continue
                # yielded = False
                for rule in self._rules:
                    result = rule.pattern.findall(line)
                    if len(result) == 0:
                        continue
                    yield rule.callback(result)
                    # yielded = True
                    if rule.exclusive:
                        break
                # if not yielded:
                #     print line
        finally:
            self.unlock()
