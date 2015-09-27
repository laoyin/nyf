# coding=utf-8
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')
import pdb,json,datetime,logging
from django.http import *
from django.conf import settings
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from django.core.management import call_command
from django.core.cache import cache
from django.utils import timezone
from gcustomer.models import *

from django.shortcuts import *
from django.http import *
import app_views
from app_views import *
from gflux import settings
from gflux.util import *
from gcustomer.status  import *
from gcustomer.utils import *
import base64
ajax_logger=logging.getLogger('ajax')

#解密接口
def decrypt_data(request,decrypt_type,context):
    if decrypt_type == "android" :
        rsa_key_android = request.META['rsa_key_android']
        context = base64.b64decode(context)
        context = rsa_key_android.decrypt(context)
        return context
    elif decrypt_type == "ios" :
        rsa_key_ios = request.META['rsa_key_ios']
        context = base64.b64decode(context)
        context = rsa_key_ios.private_decrypt(context,1)
        return context

#解密
def decrypt_data_for_andriod(request,action,data):
    if action == "login" :

            data['password'] = decrypt_data(request,"android",data['password'])

            return  action,data

    elif action == "register" :

            data['password'] = decrypt_data(request,"android",data['password'])

            return action,data

    elif action == "activate_vcard" :

            data['id_card'] = decrypt_data(request,"android",data['id_card'])
            data['pay_password'] = decrypt_data(request,"android",data['pay_password'])
            data['re_pay_password'] = decrypt_data(request,"android",data['re_pay_password'])

            return  action,data

    elif action == "modify_login_password" :

            data['old_pasword'] = decrypt_data(request,"android",data['old_pasword'])
            data['new_password'] = decrypt_data(request,"android",data['new_password'])
            data['re_new_password'] = decrypt_data(request,"android",data['re_new_password'])

            return action,data

    elif action == "modify_pay_password" :

            data['old_pay_password'] = decrypt_data(request,"android",data['old_pay_password'])
            data['new_pay_password'] = decrypt_data(request,"android",data['new_pay_password'])
            data['re_new_pay_password'] = decrypt_data(request,"android",data['re_new_pay_password'])
            data['id_card'] = decrypt_data(request,"android",data['id_card'])

            return action,data

    elif action == "forget_pay_password" :

            data['id_card'] = decrypt_data(request,"android",data['id_card'])

            return action,data

    elif action == "pay_by_oil_card"  :

            data['id_card'] = decrypt_data(request,"android",data['id_card'])
            data['pay_password'] = decrypt_data(request,"android",data['pay_password'])
            data['pay'] = decrypt_data(request,"android",data['pay'])

            return action,data

    elif action == "delete_oil_card_bind" :

            data['pay_password'] = decrypt_data(request,"android",data['pay_password'])

            return action,data

    elif action == "purchase_score_item" :

            data['pay_password'] = decrypt_data(request,"android",data['pay_password'])
            
            return action,data

    elif action == "apply_refund" :

            data['pay_password'] = decrypt_data(request,"android",data['pay_password'])

            return action,data

    elif action == "download_trade_no_with_order" :

            data['order_sha1'] = decrypt_data(request,"android",data['order_sha1'])
            data['vcard_id'] = decrypt_data(request,"android",data['vcard_id'])
            data['out_trade_no'] = decrypt_data(request,"android",data['out_trade_no'])

            return action,data

    elif action == "forget_login_password" :

            data['new_password'] = decrypt_data(request,"android",data['new_password'])

            data['re_new_password'] = decrypt_data(request,"android",data['re_new_password'])

            return action,data

    else :
            return action,data

#解密 ios
def decrypt_data_for_ios(request,action,data):
    if action == "login" :

            data['password'] = decrypt_data(request,"ios",data['password'])

            return  action,data

    elif action == "register" :

            data['password'] = decrypt_data(request,"ios",data['password'])

            return action,data

    elif action == "activate_vcard" :

            data['id_card'] = decrypt_data(request,"ios",data['id_card'])
            data['pay_password'] = decrypt_data(request,"ios",data['pay_password'])
            data['re_pay_password'] = decrypt_data(request,"ios",data['re_pay_password'])

            return  action,data

    elif action == "modify_login_password" :

            data['old_pasword'] = decrypt_data(request,"ios",data['old_pasword'])
            data['new_password'] = decrypt_data(request,"ios",data['new_password'])
            data['re_new_password'] = decrypt_data(request,"ios",data['re_new_password'])

            return action,data

    elif action == "modify_pay_password" :

            data['old_pay_password'] = decrypt_data(request,"ios",data['old_pay_password'])
            data['new_pay_password'] = decrypt_data(request,"ios",data['new_pay_password'])
            data['re_new_pay_password'] = decrypt_data(request,"ios",data['re_new_pay_password'])
            data['id_card'] = decrypt_data(request,"ios",data['id_card'])

            return action,data

    elif action == "forget_pay_password" :

            data['id_card'] = decrypt_data(request,"ios",data['id_card'])

            return action,data

    elif action == "pay_by_oil_card"  :

            data['id_card'] = decrypt_data(request,"ios",data['id_card'])
            data['pay_password'] = decrypt_data(request,"ios",data['pay_password'])
            data['pay'] = decrypt_data(request,"ios",data['pay'])

            return action,data

    elif action == "delete_oil_card_bind" :

            data['pay_password'] = decrypt_data(request,"ios",data['pay_password'])

            return action,data
    elif action == "purchase_score_item":

            data['pay_password'] = decrypt_data(request,"ios",data['pay_password'])

            return action,data

    elif action == "apply_refund" :

            data['pay_password'] = decrypt_data(request,"ios",data['pay_password'])

            return action,data

    elif action == "download_trade_no_with_order" :

            data['order_sha1'] = decrypt_data(request,"ios",data['order_sha1'])
            data['vcard_id'] = decrypt_data(request,"ios",data['vcard_id'])
            data['out_trade_no'] = decrypt_data(request,"ios",data['out_trade_no'])

            return action,data

    elif action == "forget_login_password" :

            data['new_password'] = decrypt_data(request,"ios",data['new_password'])

            data['re_new_password'] = decrypt_data(request,"ios",data['re_new_password'])

            return action,data

    else :
            return action,data

#模拟移动端加密
def simulate_app_encryption(request,action,data):
    rsa_key = request.META['rsa_key']
    if action == "login" :

            password = rsa_key.encrypt(str(data['password']),request.META['rsa_public_key'])[0]

            password = base64.b64encode(password)

            data['password'] = password

            return  data

    elif action == "register" :

            password = rsa_key.encrypt(str(data['password']),request.META['rsa_public_key'])[0]

            password = base64.b64encode(password)

            data['password'] = password

            return data

    elif action == "activate_vcard" :

            id_card = rsa_key.encrypt(str(data['id_card']),request.META['rsa_public_key'])[0]
            pay_password = rsa_key.encrypt(str(data['pay_password']),request.META['rsa_public_key'])[0]
            re_pay_password = rsa_key.encrypt(str(data['re_pay_password']),request.META['rsa_public_key'])[0]

            id_card = base64.b64encode(id_card)
            pay_password = base64.b64encode(pay_password)
            re_pay_password = base64.b64encode(re_pay_password)

            data['id_card'] = id_card
            data['pay_password'] = pay_password
            data['re_pay_password'] = re_pay_password

            return data

    elif action == "modify_login_password" :

            old_pasword = rsa_key.encrypt(str(data['old_pasword']),request.META['rsa_public_key'])[0]
            new_password = rsa_key.encrypt(str(data['new_password']),request.META['rsa_public_key'])[0]
            re_new_password = rsa_key.encrypt(str(data['re_new_password']),request.META['rsa_public_key'])[0]

            old_pasword = base64.b64encode(old_pasword)
            new_password = base64.b64encode(new_password)
            re_new_password = base64.b64encode(re_new_password)

            data['old_pasword'] = old_pasword
            data['new_password'] = new_password
            data['re_new_password'] = re_new_password

            return data

    elif action == "modify_pay_password" :
            old_pay_password = rsa_key.encrypt(str(data['old_pay_password']),request.META['rsa_public_key'])[0]
            new_pay_password = rsa_key.encrypt(str(data['new_pay_password']),request.META['rsa_public_key'])[0]
            re_new_pay_password = rsa_key.encrypt(str(data['re_new_pay_password']),request.META['rsa_public_key'])[0]
            id_card = rsa_key.encrypt(str(data['id_card']),request.META['rsa_public_key'])[0]

            old_pay_password = base64.b64encode(old_pay_password)
            new_pay_password = base64.b64encode(new_pay_password)
            re_new_pay_password = base64.b64encode(re_new_pay_password)
            id_card = base64.b64encode(id_card)

            data['old_pay_password'] = old_pay_password
            data['new_pay_password'] = new_pay_password
            data['re_new_pay_password'] = re_new_pay_password
            data['id_card'] = id_card

            return data

    elif action == "forget_pay_password" :

            id_card = rsa_key.encrypt(str(data['id_card']),request.META['rsa_public_key'])[0]

            id_card = base64.b64encode(id_card)

            data['id_card'] = id_card

            return data

    elif action == "pay_by_oil_card"  :
            id_card = rsa_key.encrypt(str(data['id_card']),request.META['rsa_public_key'])[0]
            pay_password = rsa_key.encrypt(str(data['pay_password']),request.META['rsa_public_key'])[0]
            pay = rsa_key.encrypt(str(data['pay']),request.META['rsa_public_key'])[0]

            id_card = base64.b64encode(id_card)
            pay_password = base64.b64encode(pay_password)
            pay = base64.b64encode(pay)

            data['id_card'] = id_card
            data['pay_password'] = pay_password
            data['pay'] = pay

            return data

    elif action == "delete_oil_card_bind" :

            pay_password = rsa_key.encrypt(str(data['pay_password']),request.META['rsa_public_key'])[0]

            pay_password = base64.b64encode(pay_password)

            data['pay_password'] = pay_password

            return data

    elif action == "purchase_score_item":

            pay_password = rsa_key.encrypt(str(data['pay_password']),request.META['rsa_public_key'])[0]

            pay_password = base64.b64encode(pay_password)

            data['pay_password'] = pay_password

            return data
    elif action == "apply_refund" :

            pay_password = rsa_key.encrypt(str(data['pay_password']),request.META['rsa_public_key'])[0]

            pay_password = base64.b64encode(pay_password)

            data['pay_password'] = pay_password

            return data

    elif action == "download_trade_no_with_order" :

            order_sha1 = rsa_key.encrypt(str(data['order_sha1']),request.META['rsa_public_key'])[0]
            vcard_id = rsa_key.encrypt(str(data['vcard_id']),request.META['rsa_public_key'])[0]
            out_trade_no = rsa_key.encrypt(str(data['out_trade_no']),request.META['rsa_public_key'])[0]

            order_sha1 = base64.b64encode(order_sha1)
            vcard_id = base64.b64encode(vcard_id)
            out_trade_no = base64.b64encode(out_trade_no)

            data['order_sha1'] = order_sha1
            data['vcard_id'] = vcard_id
            data['out_trade_no'] = out_trade_no

            return data

    elif action == "forget_login_password" :
        
            new_password = rsa_key.encrypt(str(data['new_password']),request.META['rsa_public_key'])[0]
            re_new_password = rsa_key.encrypt(str(data['re_new_password']),request.META['rsa_public_key'])[0]

            new_password = base64.b64encode(new_password)
            re_new_password = base64.b64encode(re_new_password)

            data['new_password'] = new_password
            data['re_new_password'] = re_new_password

            return data

    else :
            return data
