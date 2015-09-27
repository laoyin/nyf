from django.core.management.base import BaseCommand
from dash.core.backends.sql.models import dash_db_manager
from gcustomer import models
import sys, pdb

class Command(BaseCommand):
    help = 'Initialize the SQL models of station schema'

    def handle(self, *args, **options):
        try:
            conn = dash_db_manager.dash_engines[0].connect()
            tables = [
               models.DimChinaProvinceCityDistrict,
               models.GCompany,
               models.GCompanyMembership,
               models.GCustomerUser,
               models.TargetAudience,
               models.Station,
               models.StationProfile,
               models.StationGroup,
               models.StationGroupMembership,
               models.CustomerAccount,
               models.CustomerCompInfo,
               models.CustomerAccountTransaction,
               models.CustomerProfile,
               models.Promotion,
               models.PromotionInfo,
               models.PromotionEffect,
               models.UserAction,
               models.BigCustomerProfile,
               models.CustomerRelation,
               models.AdminContactInfo,
               models.AdminContactRecord,
               models.Advertisement,
               models.AdvertisementEffect,
               models.AdvertisementLaunchSetting,
               models.StoreItem,
               models.ServiceInformation,
               models.Seller,
               models.UserTargetedPromotion,
               models.UserScoreRecord,
               models.UserScoreRule,
               models.ItemScoreRule,
               models.MemberDiscountInfo,
               models.FileImage,
               models.GasWorker,
            ]
            for table in tables:
                table = table.__table__
                if not dash_db_manager.dash_engines[0].dialect.has_table(conn, table):
                    table.create(conn)
            self.stdout.write('Successfully initialized SQL models of station schema')
        except Exception, e:
            print >> sys.stderr, "Exception: ", str(e)
        finally:
            conn.close()

