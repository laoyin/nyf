#coding=utf-8
import pdb,sys

class DemositeRouter(object):
    """
    A router to control all database operations on models in the
    demosite application.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read demosite models go to demosite.
        """
        if model._meta.app_label == 'demosite':
            return 'demosite'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write demosite models go to demosite.
        """
        if model._meta.app_label == 'demosite':
            return 'demosite'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the demosite app is involved.
        """
        if obj1._meta.app_label == 'demosite' or \
           obj2._meta.app_label == 'demosite':
           return True
        return None

    def allow_syncdb(self, db, model):
        """
        Make sure the demosite app only appears in the 'demosite'
        database.
        """
        if db == 'demosite':
            return model._meta.app_label == 'demosite'
        elif model._meta.app_label == 'demosite ':
            return False
        return None

class GdesignRouter(object):
    def db_for_read(self, model, **hints):
        """
        Attempts to read gdesign models go to gdesign.
        """
        if model._meta.app_label == 'gdesign':
            return 'gdesign'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write gdesign models go to gdesign.
        """
        if model._meta.app_label == 'gdesign':
            return 'gdesign'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the gdesign app is involved.
        """
        if obj1._meta.app_label == 'gdesign' or \
           obj2._meta.app_label == 'gdesign':
           return True
        return None

    def allow_syncdb(self, db, model):
        """
        Make sure the gdesign app only appears in the 'gdesign'
        database.
        """
        if db == 'gdesign':
            return model._meta.app_label == 'gdesign'
        elif model._meta.app_label == 'gdesign':
            return False
        return None
 

