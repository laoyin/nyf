# coding=utf-8
from protobuf_message_pb2 import *
from socket import *
import pdb

class MessageClient():

    def __init__(self, ip,port,logger=None,timeout=None):
        self.ip=ip
        self.port=port
        self.logger=logger
        # AF_INET 代表是IPv4协议, SOCK_STREAM 代表是TCP连接
        self.conn=socket(AF_INET, SOCK_STREAM)
        self.conn.settimeout(timeout)
        self.conn.connect((self.ip,self.port))

    def __del__(self):
        self.conn.close()

    """
    第一层为Message类进行包装，纪录消息类型
    第二层为LoginRequest这类消息
    """

    # 用户登陆请求主要用户django
    def Login(self,sessionid,userSha1):
        message = AppMessage()
        stub = LoginRequest()
        stub.userSha1 = userSha1
        stub.sessionid = sessionid
        message.buff = stub.SerializeToString()
        message.type = LOGIN
        buff = message.SerializeToString()
        self.conn.sendall(buff)


    #推送路况消息
    def RoadMessage(self,authorSha1,messagesha1,longitude,latitude):
        message = AppMessage()
        stub = RoadMessage()
        stub.authorSha1 = authorSha1
        stub.messagesha1 = messagesha1
        stub.longitude = longitude
        stub.latitude = latitude
        message.buff = stub.SerializeToString()
        message.type = ROADMESSAGE
        buff = message.SerializeToString()
        self.conn.sendall(buff)

    #我的专享优惠通知
    #user_sha1 :指定消息推送的用户sha1
    #promotion_title : 优惠标题 string 
    #promotion_content : 优惠内容 string 
    #promotion_sha1 : 优惠商品的sha1 string 
    #promotion_type : 用户商品类型  int   0 油品，1 非油品，2车后服务
    def MySalesMessage(self,user_sha1,promotion_title,promotion_content,promotion_sha1,promotion_type):
        message = AppMessage()
        stub = MySalesMessage()
        stub.user_sha1 =  user_sha1
        stub.promotion_title =  promotion_title
        stub.promotion_content =  promotion_content
        stub.promotion_sha1 =  promotion_sha1
        stub.promotion_type =  promotion_type
        message.buff = stub.SerializeToString()
        message.type = MYSALESMESSAGE
        buff = message.SerializeToString()
        self.conn.sendall(buff)

    #交易完成通知
    #user_sha1 :指定消息推送的用户sha1
    #order_sha1:订单sha1  string 
    #订单状态:0 代表订单生成  1代表支付完成 2代表交易完成 3代表交易取消 4代表订单已过期 int 
    def CompleteTransMessage(self,user_sha1,order_sha1,status):
        message = AppMessage()
        stub = CompleteTransMessage()
        stub.user_sha1 =  user_sha1
        stub.order_sha1 =  order_sha1
        stub.status =  status
        message.buff = stub.SerializeToString()
        message.type = COMPLETETRANSMESSAGE
        buff = message.SerializeToString()
        self.conn.sendall(buff)



