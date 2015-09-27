/**
 *  消息路由模块是为了处理不同类型的消息，使得消息处理从message server的主函数中分离出来
 *  使之成为独立的模块,在这里可以完成参数解析，消息转发等功能
 **/

var fs = require('fs');
var Schema = require('protobuf').Schema;
var schema = new Schema(fs.readFileSync('protobuf_message.desc'));
var logger = require('./logger_client');
var manager = require('./client_manager');


var router = {};

// 登陆请求
var LOGIN = function(socket,data){
    logger.debug('=================================');
    logger.debug('login data is :',data);
    var LoginRequest = schema['app.LoginRequest'];
    var login_data = LoginRequest.parse(data);
    var userSha1 = login_data.userSha1;
    /*logger.info(manager.sockets)*/
    // 缓存用户的信息
    manager.userSha1s_hash[userSha1] = socket.id
    logger.info(login_data)
    logger.info(manager.userSha1s_hash)
    // 缓存用户登陆message server的信息
    var App_Message = schema['app.AppMessage'];
    var LoginResponse = schema['app.LoginResponse'];
    var responseObj = {"status":"1","cltId":'1111'};
    var response_proto = LoginResponse.serialize(responseObj);
    var messageObj = {"type":"LOGINRESPONSE","buff":response_proto};
    var message_proto = App_Message.serialize(messageObj);
    logger.debug("response data is :",message_proto);



    // 构造响应的消息
    var head = new Buffer(12);
    head.writeUInt32LE(0, 0);
    head.writeUInt32LE(0, 4);
    head.writeUInt32LE(message_proto.length, 8);
    socket.write(head,'binary');
    socket.write(message_proto,'binary');
};

var ROADMESSAGE = function(socket,data){
    logger.debug('roadmessage data is :',data);
    //解析消息数据
    var RoadMessage = schema['app.RoadMessage'];
    var message_data = RoadMessage.parse(data);
    var authorSha1 = message_data.authorSha1;
    var messagesha1 = message_data.messagesha1;
    var longitude = message_data.longitude;
    var latitude = message_data.latitude;

    //推送给移动端的的路况消息
    var App_Message = schema['app.AppMessage'];
    var RoadMessage = schema['app.RoadMessage'];
    var pushRoadmessageObj = {"authorSha1":authorSha1,"messagesha1":messagesha1,
                                "longitude":longitude,"latitude":latitude}
    var push_proto = RoadMessage.serialize(pushRoadmessageObj)
    var messageObj = {"type":"ROADMESSAGE","buff":push_proto};
    var message_proto = App_Message.serialize(messageObj);
    logger.debug("push message data is :",message_proto);

    // 推送路况消息给移动端
    var head = new Buffer(12);
    head.writeUInt32LE(0, 0);
    head.writeUInt32LE(0, 4);
    head.writeUInt32LE(message_proto.length, 8);


    //给所有的以建立的socket连接推送消息
    /*manager.sockets.forEach(function(socket){
        socket.write(head,'binary');
        socket.write(message_proto,'binary');
    });*/

    //给指定用户推动消息
    sha1_list = [authorSha1];
    socketId_list = get_socketId_list(sha1_list);
    socketId_list.forEach(function(socket){
        socket = manager.sockets_hash[socketId]
        socket.write(head,'binary');
        socket.write(message_proto,'binary');
    });
};
    
//获取推送连接列表
var  get_socketId_list = function(sha1_list){
    var socketId_list = []
    for(var i = 0,len = sha1_list.length;i<len;i++){
        socketId = manager.userSha1s_hash[sha1_list[i]]
        if(socketId){
                socketId_list.push(socketId)
        }
    }
    return socketId_list
};


var MYSALESMESSAGE = function(socket,data){
    logger.debug('=================================');
    logger.debug('my_sale_message data is :',data);
    //获取推送数据
    var MySalesMessage = schema['app.MySalesMessage'];
    var my_sale_data = MySalesMessage.parse(data);
    var promotion_title = my_sale_data.promotionTitle
    var promotion_content = my_sale_data.promotionContent
    var promotion_sha1 = my_sale_data.promotionSha1
    var promotion_type = my_sale_data.promotionType
    var user_sha1 = my_sale_data.userSha1
    //推送给移动端的我的专享消息
    var App_Message = schema['app.AppMessage'];
    var MySalesMessage = schema['app.MySalesMessage'];
    var mySalesMessageObj = {
                                                "promotionTitle":promotion_title,
                                                "promotionContent":promotion_content,
                                                "promotionSha1":promotion_sha1,
                                                "promotionType":promotion_type,
                                                "userSha1":user_sha1
                                            }
    var push_proto = MySalesMessage.serialize(mySalesMessageObj)
    var messageObj = {"type":"MYSALESMESSAGE","buff":push_proto};
    var message_proto = App_Message.serialize(messageObj);
    logger.debug("push message data is :",message_proto);

    //推送消息给移动端
    var head = new Buffer(12);
    head.writeUInt32LE(0, 0);
    head.writeUInt32LE(0, 4);
    head.writeUInt32LE(message_proto.length, 8);

    //给指定用户推动消息
    socketId = manager.userSha1s_hash[user_sha1]
    if(socketId){
        my_socket = manager.sockets_hash[socketId]
        my_socket.write(head,'binary');
        my_socket.write(message_proto,'binary');
    }

};

var COMPLETETRANSMESSAGE = function(socket,data){
    logger.debug('=================================');
    logger.debug('complete_trans_message data is :',data);
    //获取推送数据
    var ComleteTransMessage = schema['app.CompleteTransMessage'];
    var complete_trans_data = ComleteTransMessage.parse(data);
    var order_sha1 = complete_trans_data.promotionTitle
    var status = complete_trans_data.status
    var user_sha1 = complete_trans_data.userSha1
    //推送给移动端的我的专享消息
    var App_Message = schema['app.AppMessage'];
    var CompleteTransMessage = schema['app.CompleteTransMessage'];
    var completeTransMessage = {
                                                "promotionTitle":order_sha1,
                                                "status":status,
                                                "userSha1":user_sha1
                                            }
    var push_proto = CompleteTransMessage.serialize(completeTransMessage)
    var messageObj = {"type":"COMPLETETRANSMESSAGE","buff":push_proto};
    var message_proto = App_Message.serialize(messageObj);
    logger.debug("push message data is :",message_proto);

    //推送消息给移动端
    var head = new Buffer(12);
    head.writeUInt32LE(0, 0);
    head.writeUInt32LE(0, 4);
    head.writeUInt32LE(message_proto.length, 8);

    //给指定用户推动消息
    socketId = manager.userSha1s_hash[user_sha1]
    if(socketId){
        socket = manager.sockets_hash[socketId]
        socket.write(head,'binary');
        socket.write(message_proto,'binary');
    }
};

//消息发送路由
router["LOGIN"] = LOGIN;
router['ROADMESSAGE'] = ROADMESSAGE;
router['MYSALESMESSAGE'] = MYSALESMESSAGE;
router['COMPLETETRANSMESSAGE'] = COMPLETETRANSMESSAGE;
//消息路由器
module.exports = router;


