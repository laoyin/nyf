# coding=utf-8
from protobuf_message_pb2 import *
import gearman,json,pdb
from message_client import *

def PushMessage(task_name,job_data):
        submit_gearman_job(task_name,job_data)

def submit_gearman_job(task_name,job_data):
    client = gearman.GearmanClient(['127.0.0.1:4730'])
    client.submit_job(task_name,json.dumps(job_data),wait_until_complete=False,background=True)

class JOGTYPE :
    MYSALEMESSAGE = "push_my_sale_message"
    COMPLETETRANSMESSAGE = "complete_trans_message"

class MessageService():

    def __init__(self,factory,socket_type,config,logger):
        self.logger=logger
        self.config=config
        self.socket_type=socket_type
        self.django_ip=config.get('django-server','ip')
        self.username=""
        self.buffer=""
        self.factory=factory
        self.sessionid=""

    @classmethod
    def PushMysaleMessage(cls,message_data):
        task_name = "push_message"
        job_data = {}
        job_data['job_type'] = JOGTYPE.MYSALEMESSAGE
        job_data['message_data'] = message_data
        PushMessage(task_name,job_data)

    @classmethod
    def PushCompleteTransMessage(cls,message_data):
        task_name = "push_message"
        job_data = {}
        job_data['job_type'] = JOGTYPE.COMPLETETRANSMESSAGE
        job_data['message_data'] = message_data
        PushMessage(task_name,job_data)
