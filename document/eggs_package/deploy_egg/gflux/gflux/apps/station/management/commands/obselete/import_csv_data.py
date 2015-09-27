from django.core.management.base import BaseCommand
from dash.core.backends.sql.models import Session
from gflux.apps.station.models import Trans, TransType, PaymentType
from datetime import datetime
import sys
import csv

def guess_datetime(s):
    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
        try:
            return datetime.strptime(s, fmt)
        except:
            pass
    return None

class Command(BaseCommand):
    help = 'Import Trans from CSV'

    def handle(self, site, filename, **options):
        site = site.strip().upper()
        trans = []
        with open(filename) as fd:
            reader = csv.reader(fd)
            for row in reader:
                try:
                    timestamp = guess_datetime(row[2])
                    barcode = int(row[3])
                    if barcode < 400000:
                        trans_type = TransType.FUEL
                    else:
                        trans_type = TransType.NON_FUEL
                    cardnum = int(row[1])
                    if cardnum == 0:
                        payment_type = PaymentType.CASH
                    elif str(cardnum).startswith('9'):
                        payment_type = PaymentType.VIP
                    elif str(cardnum).startswith('6'):
                        payment_type = PaymentType.UNION_PAY
                    else:
                        payment_type = PaymentType.CASH

                    qty = int(row[4])
                    weight = float(row[7])
                    tran = {
                        'site': site,
                        'trans_type': trans_type,
                        'trans_id': int(row[0]),
                        'cardnum': cardnum,
                        'payment_type': payment_type,
                        'timestamp': timestamp,
                        'datehour': datetime(timestamp.year, timestamp.month, timestamp.day, timestamp.hour),
                        'barcode': barcode,
                        'pay': float(row[5]) if trans_type == TransType.FUEL else float(row[9]),
                        'quantity': weight if trans_type == TransType.FUEL else qty,
                        'desc': row[6].strip(),
                        'price': row[8].strip(),
                        'unitname': row[10].strip(),
                        'pump_id': int(row[11]),
                    }
                    trans.append(tran)
                except Exception, e:
                    print >> sys.stderr, row
                    raise(e)

        s = Session()
        try:
            if len(trans) > 0:
                s.execute(Trans.__table__.insert(), trans)
                s.commit()
            print 'successfully committed'
        except Exception, e:
            print >> sys.stderr, "failed to commit: ", str(e)
        finally:
            s.close()
