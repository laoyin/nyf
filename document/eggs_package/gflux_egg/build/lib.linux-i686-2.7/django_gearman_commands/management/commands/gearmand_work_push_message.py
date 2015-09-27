#coding=utf-8
import django_gearman_commands,json
from gcustomer.message_server.service.message_client import *

class Command(django_gearman_commands.GearmanWorkerBaseCommand):
   """Gearman worker performing 'push message' job."""

   @property
   def task_name(self):
       return 'push_message'

   #job_data : {"job_type":"push_my_sale_message","messaage_data":{}}
   def do_job(self, job_data):
   	try :
		client = MessageClient('wheel.zcdata.com.cn',8081)
	except Exception,e:
                ajax_logger.error(str(e))
		print "连接消息服务器失败"
		return 
	job_data = json.loads(job_data)
	if job_data['job_type'] ==  JOGTYPE.MYSALEMESSAGE :
		try :
			message_data = job_data['message_data']
			user_sha1 = message_data['user_sha1']
			promotion_title = message_data['promotion_title']
			promotion_content = message_data['promotion_content']
			promotion_sha1 = message_data['promotion_sha1']
			promotion_type = int(message_data['promotion_type'])
			client.MySalesMessage(user_sha1,promotion_title,promotion_content,promotion_sha1,promotion_type)
		except Exception,e:
			print "发送我的专享消息失败"
			return 
	elif job_data['job_type'] ==  JOGTYPE.COMPLETETRANSMESSAGE :
		try :
			message_data = job_data['message_data']
			user_sha1 = message_data['user_sha1']
			order_sha1 = message_data['order_sha1']
			status = message_data['status']
			client.CompleteTransMessage(user_sha1,order_sha1,status)
		except Exception,e:
			print "发送订单完成信息失败!"
			return 
	else :
		try :
			client.RoadMessage('test','test',12.1,12.1)
		except Exception,e:
			print "发送消息失败!"
			return 

class JOGTYPE :
	MYSALEMESSAGE = "push_my_sale_message"
	COMPLETETRANSMESSAGE = "complete_trans_message"
