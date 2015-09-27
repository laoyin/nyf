/**
 * This is the Message server
 */
var net = require('net');
var server = net.createServer();
var SHA1 = require('sha1');
var async = require('async');
var mysql = require('mysql');
var gearman = require('node-gearman');
var router = require('./message_router');
var manager = require('./client_manager');

// 加载配置文件
var cfg = require("./config");
var port = cfg.server.port;
var port = parseInt(process.argv[2]) || port;

var host = cfg.server.host;

var logger = require('./logger_client');

// 这是protobuf的的文件读取
var fs = require('fs');
var Schema = require('protobuf').Schema;
var schema = new Schema(fs.readFileSync('protobuf_message.desc'));

// 配置redis的信息,并创建一个redis的链接
var redis = require('redis');
var redis_cli = redis.createClient(cfg.redis.port,cfg.redis.host);

// 配置mysql的信息
var mysql_conn = mysql.createConnection(cfg.mysql);

// 开始监听
server.on('listening',function(){
   logger.info("Server is listening on prot",port)
});

// 建立连接
server.on("connection",function(socket){
    logger.info("receive a connection");

    // 构造和存储socket的信息
    var date = new Date().getTime();
    var socketID = SHA1(date);
    socket.id = socketID;

    //每一个链接都有一个自己的buffer，用来存储消息。
    socket.buffer_start_pos=0;
    socket.buffer_end_pos=0;
    socket.buffer_max_size=4096;
    socket.buffer=new Buffer(socket.buffer_max_size);

    // 用来管理所有socket的队列
    manager.sockets.push(socket);

    // 用来根据socket id快速查找socket的信息
    manager.sockets_hash[socketID] = socket;
     
    // 在redis里面存储用户和message server之间的关联，用于分布式数据共享
    var server_info = host+":"+port;
    redis_cli.hset("USER_INFO_STORE",socketID,server_info,function(err){
        if (err){
            logger.error("Save user message server info error:",err)
        }
    });

    // 监听socket的data事件
    socket.on("data",function(message){
        logger.trace(message);
        if (typeof message === 'string') {
            logger.info('string');
            var buf = new Buffer(message,'base64');
            logger.trace('received string [%s bytes] from websocket %s.'
                , buf.length, socket.id);
            dataReceived(buf,socket);
        }
        else if(typeof message === 'object'){
            logger.info('object');
            if (!message.hasOwnProperty('length')){
                message.length=getMessageLength(message);
            }
            logger.trace('received object [%s bytes] from websocket %s.'
                , message.length, socket.id);
            dataReceived(message,socket);
        }
        //dataReceive(socket,data);
        console.log(socketID)

    });

    // socket 断开连接之后,删除socket信息
    socket.on('close',function(){
        logger.info('disconnect from server')
        // 删除socket的信息
        var index = manager.sockets.indexOf(socket);
        manager.sockets.splice(index,1);
        delete manager.sockets_hash[socket.id];
    })
});

// 连接关闭
server.on("close",function(){
   logger.info("connection closed")

});

// 连接出错
server.on("error",function(err){
    logger.error("Error in connecion",err)
});


server.listen(port);

function getMessageLength(ar){
    var count=0;
    for(var key in ar){
        count++;
    }
    return count;
}


// 处理异步IO方式下获得数据的主流程函数
function dataReceived(message,client){

    // 如果缓存起始或结束偏移量不对
    if(client.buffer_end_pos<0||client.buffer_start_pos<0){
        logger.error("wrong data buffer starting or ending position, and we need clear them.");
        client.buffer_end_pos=0;
        client.buffer_start_pos=0;
    }

    // 如果当前缓存的长度加消息长度超过了缓存的最大长度
    while(client.buffer_end_pos+message.length>client.buffer_max_size){
        //差多少？
        var offset=client.buffer_end_pos+message.length-client.buffer_max_size

        //补双倍
        var new_buffer = new Buffer(offset*2);
        var arr = new Array();
        arr[0] = client.buffer;
        arr[1] = new_buffer;
        client.buffer = Buffer.concat(arr,client.buffer_max_size+offset*2);
        client.buffer_max_size += offset*2;
    }

    // 将新来的消息追加到缓存尾部
    for (var i = 0; i < message.length ; i++) {
        client.buffer[client.buffer_end_pos+i] = message[i];
    }

    // 更新当前的缓存大小
    client.buffer_end_pos+=message.length;

    // 循环执行工作逻辑
    async.whilst(
        // 条件判断逻辑
        // return true 继续执行工作逻辑
        // return false 退出循环并执行错误处理逻辑
        function() {
            //修正缓冲区指针
            // 缓存错误
            if(client.buffer_end_pos<0||client.buffer_start_pos<0){
                logger.error("wrong data buffer starting or ending position, and we need clear them.");
                client.buffer_end_pos=0;
                client.buffer_start_pos=0;
            }

            //有消息头吗？
            var got_head=(client.buffer_end_pos-client.buffer_start_pos)>12;
            if(!got_head)
                return false;

            // 获取消息头
            var headers = client.buffer.slice(client.buffer_start_pos,client.buffer_start_pos+12);
            var message_head = require('binary')
                .parse(headers)
                .word32lu('type')
                .word32lu('version')
                .word32lu('size')
                .vars;

            var type=message_head.type;
            var version=message_head.version;
            var size=message_head.size;
            var buff_size=client.buffer_end_pos-client.buffer_start_pos;

            //有完整的消息吗？
            var got_body=buff_size>=(size+12)
            if(!got_body){
                process_message(message,client);
                return false;
            }
                

            //有一条完整的消息，准备处理
            return true;
        },

        // 工作逻辑，被执行前会进行条件判断
        // return 任意值直接退出whilest
        // 调用callback（）执行工作逻辑
        // 调用callback（err）执行错误处理逻辑
        // 请使用setTimeout来调用callback防止栈溢出
        function(callback){
            // 获取消息头
            var headers = client.buffer.slice(
                client.buffer_start_pos,client.buffer_start_pos+12);
            var message_head = require('binary')
                .parse(headers)
                .word32lu('type')
                .word32lu('version')
                .word32lu('size')
                .vars;

            var type=message_head.type;
            var version=message_head.version;
            var size=message_head.size;

            // 读取消息体
            client.buffer_start_pos+=12;
            var message_body=client.buffer.slice(
                client.buffer_start_pos,client.buffer_start_pos+size);

            // 处理读到的消息
            try{
                //无论process message中有多少异步操作
                //都不会，也不应该影响到工作逻辑
                //因为我们需要同步的逻辑只是对缓冲区的读写操作
                //没有必要将工作逻辑的callback一层层的传递下去
                process_message(message_body,client);
            }catch(err){
                callback(err)
            }

            // 缓存指针前移
            client.buffer_start_pos+=size;
            if(client.buffer_start_pos>=(client.buffer_max_size*0.75)){
                client.buffer.copy(client.buffer,0,client.buffer_start_pos,client.buffer_end_pos);
                client.buffer_end_pos-=client.buffer_start_pos;
                client.buffer_start_pos=0;
            }

            // 循环
            setTimeout(callback,0)
        },

        // 出错处理逻辑
        function(err) {
            if(err){
                if(err.stack)
                    logger.error(''+err.stack);
                else
                    logger.error(''+err);
            }
        }
    );
}


// 消息的处理函数
function process_message(data,socket){
    logger.debug("receive protobuf message",data.toString());
    // 解析data的里面的数据
    var App_Message = schema['app.AppMessage'];
    logger.error("proto message",data)

    try{
        var proto_message = App_Message.parse(data)
    }catch(e){
        logger.error("prase message error",e)
    }

    var message_type = proto_message.type;
    var message_data = proto_message.buff;
    console.log(message_type);

    // 所有类型的消息都交给消息路由函数处理
    router[message_type](socket,message_data);

    // 如果是广播信息，发送给所有的客户端

    // 如果是指定的消息，先查询socket信息，然后发送消息
}
