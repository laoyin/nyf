# coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from django.http import *
from gflux.util import *	
import pdb,logging
from Crypto.PublicKey import RSA as RSA_android
from M2Crypto import RSA as RSA_ios
ajax_logger=logging.getLogger('ajax')

class UserOnlineStatusCheck(object):
	def process_view(self, request, view_func, view_args, view_kwargs) :
		keywords = [
			"static",
			"login",
			"register",
			"gflux",
			"jsi18n",
			"get_china_location",
			"api",
			"logo",
			"render_image",
			"get_comp_type",
                       "get_comp_list",
                                       "purchase_complete_by_the_third",
		]
		for keyword in keywords :
			if request.path_info.find(keyword) != -1 :
				return None
			else:
				continue
		ret=checkUserOnlineStatus(request)
		if ret!=Status.LOGINSUCCESS:
			return HttpResponseRedirect('/gcustomer/login/')
		else :
			return None
		
#request extension
class RequestEncryptionMiddleware(object):
    def __init__(self):
        #init rsa
        self.initRSA()

    def initRSA(self):
        """
        首先判断是否有public.pem和private.pem两个文件，第一次时没有，生成pubkey和prikey并存入文件中，
        以后每次都从文件中取这两个key！
        """
        if os.path.exists(settings.SERVER_RSA_PUBLIC_KEY) and os.path.exists(settings.SERVER_RSA_PRIVATE_KEY):
            # load公钥和密钥
            with open(settings.SERVER_RSA_PRIVATE_KEY) as privatefile:
                self.rsa_private_key = privatefile.read()
                self.rsa_key_android =  RSA_android.importKey(self.rsa_private_key)
                self.rsa_key_ios = RSA_ios.load_key(settings.SERVER_RSA_PRIVATE_KEY)
                self.rsa_key = RSA_android.importKey(self.rsa_private_key)
            with open(settings.SERVER_RSA_PUBLIC_KEY) as publickfile:
                self.rsa_public_key = publickfile.read()
        else:
            print "failure to find the private rsa key"
            sys.exit(-1)
            
    def process_request(self, request) :
        ajax_logger.info("request_path:"+request.path)
        ajax_logger.info("request_get:"+str(request.GET))
        ajax_logger.info("request_post:"+str(request.POST))
        #给request 扩展rsa支持
        request.META['rsa_key_android'] =  self.rsa_key_android
        request.META['rsa_key_ios'] = self.rsa_key_ios
        request.META['rsa_key'] = self.rsa_key
        request.META['rsa_public_key']=self.rsa_public_key

    def process_response(self,request,response):
        request.META['rsa_public_key'] = ''
        request.META['rsa_key_ios'] = ''
        request.META['rsa_key_android'] = ''
        request.META['rsa_key'] = ''
        return response

#静态文件请求路径处理
class StaticFileVerionMiddleware(object) :
    def process_request(self, request) :
        if request.path_info.startswith('/gflux/static/js'):
            try :
                if request.path_info.find("render") != -1 and request.path_info.find("_v_") != -1:
                    path = request.path_info.split("_v_")[0] + ".js"
                    request.path_info = path
            except :
                raise Http404
        else :
            pass