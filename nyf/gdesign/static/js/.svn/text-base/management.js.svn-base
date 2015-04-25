//dom ready，初始化
$(function(){
    //初始化站点和位置信息
    initSite()

    //初始化页面显示
    initPage()
})

//初始化页面
function initPage(){
    //隐藏返回按钮和第二屏页面
    $('.second_area').hide()
    $('#back_btn').hide()
}

//初始化站点信息
function initSite(){
    //获取用户的所有站点,加入options
    var siteSelect = $("#select_site");
    for (var idx=0;idx<all_stations.length;idx++){
        var key=all_stations[idx].name
        var value=all_stations[idx].description
        var opp = new Option(value,key);
        siteSelect.append(opp);
    }
}

//进入第二屏界面
function enterEditPage(){
    //获取站点名字
    var name=$('#select_site option:selected').val()

    //将通道,油位,油机的显示区域清空
    $('#level_area').empty()
    $('#machine_area').empty()
    $('#channel_area').empty()

    //未选择站点进行提示
    if(name=='-1'){
        alert(gettext('请选择站点！'))
        return
    }

    //发送请求
    $.post(url_prefix+'ajax/get_guns_id/',{"site":name},function(data){
        if(data['ret']=='1101'){
            //隐藏第一屏,显示第二屏以及返回按钮
            $('#first_area').hide()
            $('.second_area').show()
            $('#back_btn').show()

            //该站点所有的油枪号
            var guns=data['data']
            window.guns_id=guns
        }
    },'json')

    //发送请求,获取通道,油位,油机的所有信息
    $.post(url_prefix+'ajax/get_channel_machine/',{"site":name},function(data){
        if(data['ret']=='1101'){
            $('#first_area').hide()
            $('.second_area').show()
            $('#back_btn').show()

            //通道,油位,油机的所有信息
            window.all_channel_machine=data['data']
            var infos=data['data']

            //通道信息
            var passages=infos['passages']

            //通道信息不存在
            if(!passages){
                passages=[]
            }

            //油机信息
            var machines=infos['machines']

            //油机信息不存在
            if(!machines){
                machines=[]
            }

            //油位信息
            var level=infos['level']

            //油位信息不存在
            if(!level){
                level=[]
            }

            //渲染通道区域
            for(var i=0;i<passages.length;i++){
                var name=passages[i]['name']
                var tmp=String.format('<button type="button"\
                name="{0}" class="btn btn-default btn-xs"\
                style="margin-left:10px;margin-top:10px;font-size:16px">{1}\
                         <span class="glyphicon glyphicon-edit" onclick="editModal(this,4);"></span>\
                         <span class="glyphicon glyphicon-minus" onclick="delChannel(this)"></span>\
                 </button>',name,name)
                 $('#channel_area').append(tmp)
            }

            //渲染油机信息
            for(var i=0;i<machines.length;i++){
                var name=machines[i]['name']
                var tmp=String.format('<button type="button"\
                name="{0}" class="btn btn-default btn-xs"\
                style="margin-left:10px;margin-top:10px;font-size:16px">{1}\
                         <span class="glyphicon glyphicon-edit" onclick="editModal(this,5);"></span>\
                         <span class="glyphicon glyphicon-minus" onclick="delMachine(this)"></span>\
                 </button>',name,name)
                 $('#machine_area').append(tmp)
            }

            //渲染油位信息
            for(var i=0;i<level.length;i++){
                var name=level[i]['name']
                var tmp=String.format('<button type="button"\
                name="{0}" class="btn btn-default btn-xs"\
                style="margin-left:10px;margin-top:10px;font-size:16px">{1}\
                         <span class="glyphicon glyphicon-edit" onclick="editModal(this,6);"></span>\
                         <span class="glyphicon glyphicon-minus" onclick="delLevel(this)"></span>\
                 </button>',name,name)
                 $('#level_area').append(tmp)
            }
        }
    },'json')
}

//获取通道油机油位信息
function get_all_channel_machine(){
    //获取站点名字
    var name=$('#select_site option:selected').val()

    //发送请求
    $.post(url_prefix+'ajax/get_channel_machine/',{"site":name},function(data){
        if(data['ret']=='1101'){
            $('#first_area').hide()
            $('.second_area').show()
            $('#back_btn').show()

            //更新通道油机油位信息
            window.all_channel_machine=data['data']

        }
    },'json')
}

//返回选择站点页面
function backFirstPage(){
    //隐藏第二屏,显示第一屏
    $('.second_area').hide()
    $('#first_area').show()
    $('#back_btn').hide()
}

//显示新增/编辑权限对话框
function editModal(obj,type){
    //清空油枪号显示
    $('#all_guns').empty()

    //确认按钮不可点击
    $('#add_item_btn').prop("disabled",true);

    //渲染所有油枪号
    tmp=[]
    $.each(guns_id,function(i,n){
        tmp.push(parseInt(n))
    })
    guns_id=tmp.sort(function(a,b){
        return a - b
    })
    for(var i=0;i<guns_id.length;i++){
        var tmp=String.format('<input style="margin: 9px 10px 0px;" type="checkbox" name="checkbox" value="{0}">\
         {0}</input>',guns_id[i],guns_id[i])
         $('#all_guns').append(tmp)
    }

    //根据类型弹出对话框,1:新增通道,2:新增油机,3:新增油位,4:编辑通道,5:编辑油机,6:编辑油位
    if(type==1){
        $('#myModalLabel').text(gettext('新增通道'))
        $('#name').text(gettext('通道名字'))

        //清空文本框
        $('#add_name').val("")

        //可编辑
        $("#add_name").prop("disabled",false);
    }
    else if(type==2){
        $('#myModalLabel').text(gettext('新增油机'))
        $('#name').text(gettext('油机名字'))

        //清空文本框
        $('#add_name').val("")

        //可编辑
        $("#add_name").prop("disabled",false);
    }
    else if(type==3){
        $('#myModalLabel').text(gettext('新增油位'))
        $('#name').text(gettext('油位名字'))

        //清空文本框
        $('#add_name').val("")

        //可编辑
        $("#add_name").prop("disabled",false);
    }
    else if(type==4){
        $("#add_item_btn").prop("disabled",false);
        var channels=all_channel_machine['passages']

        //获取通道名字
        var name=obj.parentNode.name
        $('#myModalLabel').text(gettext('编辑通道'))
        $('#name').text(gettext('通道名字'))

        //编辑框显示名字
        $('#add_name').val(name)

        //不可编辑
        $('#add_name').prop("disabled",true);

        //编辑时显示已选中的油枪号
        for(var i=0;i<channels.length;i++){
            if(channels[i]['name']==name){
                var guns=channels[i]['value']
                for(var j=0;j<guns.length;j++){
                    $("input[value="+guns[j]+"]").prop("checked",true);
                }
                break
            }
        }
    }
    else if(type==5){
        $("#add_item_btn").prop("disabled",false);
        var machines=all_channel_machine['machines']
        var name=obj.parentNode.name
        $('#myModalLabel').text(gettext('编辑油机'))
        $('#name').text(gettext('油机名字'))

        //编辑框显示名字
        $('#add_name').val(name)

        //不可编辑
        $('#add_name').prop("disabled",true);

        //编辑时显示已选中的油枪号
        for(var i=0;i<machines.length;i++){
            if(machines[i]['name']==name){
                var guns=machines[i]['value']
                for(var j=0;j<guns.length;j++){
                    $("input[value="+guns[j]+"]").prop("checked",true);
                }
                break
            }
        }
    }
    else if(type==6){
        $("#add_item_btn").prop("disabled",false);
        var level=all_channel_machine['level']
        var name=obj.parentNode.name
        $('#myModalLabel').text(gettext('编辑油位'))
        $('#name').text(gettext('油机名字'))

        //编辑框显示名字
        $('#add_name').val(name)

        //不可编辑
        $('#add_name').prop("disabled",true);

        //编辑时显示已选中的油枪号
        for(var i=0;i<level.length;i++){
            if(level[i]['name']==name){
                var guns=level[i]['value']
                for(var j=0;j<guns.length;j++){
                    $("input[value="+guns[j]+"]").prop("checked",true);
                }
                break
            }
        }
    }
    else{
        return
    }

    //$('#guns_id')

    //显示模态框
    $('#myModal').modal('show');
}

//新增信息
function addItem(){
    //站点名
    var site=$('#select_site option:selected').val()

    //名字
    var name=$('#add_name').val()
    var guns_id=new Array();

    //类型
    var title=$('#myModalLabel').text()
    var type=-1

    //判断名字
    if(name==''){
        errorModal(gettext('名字不能为空！'))
        return
    }

    //选中的油枪号
    guns_id=$('input[name="checkbox"]:checked').map(function() {
      return $(this).val();
    }).get();

    //未选择油枪号
    if(guns_id.length==0){
        errorModal(gettext('请选择油枪号!'))
        return
    }

    //type赋值
    if(title=='新增通道'){
        type=0
    }
    else if(title=='编辑通道'){
        type=1
    }
    else if(title=='新增油机'){
        type=2
    }
    else if(title=='编辑油机'){
        type=3
    }
    else if(title=='新增油位'){
        type=4
    }
    else if(title=='编辑油位'){
        type=5
    }
    else{
        return
    }

    //发送请求
    $.post(url_prefix+'ajax/add_channel_machine/',
        {"site":site,"name":name,"guns":guns_id,"type":type},
        function(data){
            if(data['ret']=='1101'){
                //渲染页面,type:0通道,1油机,2油位
                if(type==0){
                    var tmp=String.format('<button type="button"\
                    name="{0}" class="btn btn-default btn-xs"\
                    style="margin-left:10px;margin-top:10px;font-size:16px">{1}\
                             <span class="glyphicon glyphicon-edit" onclick="editModal(this,4);"></span>\
                             <span class="glyphicon glyphicon-minus" onclick="delChannel(this)"></span>\
                     </button>',name,name)
                     $('#channel_area').append(tmp)
                }

                //油机
                else if(type==2){
                    var tmp=String.format('<button type="button"\
                    name="{0}" class="btn btn-default btn-xs"\
                    style="margin-left:10px;margin-top:10px;font-size:16px">{1}\
                             <span class="glyphicon glyphicon-edit" onclick="editModal(this,5);"></span>\
                             <span class="glyphicon glyphicon-minus" onclick="delChannel(this)"></span>\
                     </button>',name,name)
                     $('#machine_area').append(tmp)
                }

                //油位
                else if(type==4){
                    var tmp=String.format('<button type="button"\
                    name="{0}" class="btn btn-default btn-xs"\
                    style="margin-left:10px;margin-top:10px;font-size:16px">{1}\
                             <span class="glyphicon glyphicon-edit" onclick="editModal(this,6);"></span>\
                             <span class="glyphicon glyphicon-minus" onclick="delChannel(this)"></span>\
                     </button>',name,name)
                     $('#level_area').append(tmp)
                }
            }

            //关闭对话框
            $('#myModal').modal('toggle')

            //更新通道,油位,油机信息
            get_all_channel_machine()
        },'json')
}

//删除通道
function delChannel(obj){
    //名字
    var name=$(obj).parents('button').attr('name')

    //站点
    var site=$('#select_site option:selected').val()

    //发送请求
    $.post(url_prefix+'ajax/del_channel/',{"site":site,"name":name},
        function(data){
            if(data['ret']=='1101'){
                //页面移除该项
                $(obj).parents('button').remove()
            }
        },'json')
}

//删除油机
function delMachine(obj){
    //名字
    var name=$(obj).parents('button').attr('name')

    //站点
    var site=$('#select_site option:selected').val()

    //发送请求
    $.post(url_prefix+'ajax/del_machine/',{"site":site,"name":name},
        function(data){
            if(data['ret']=='1101'){
                //页面移除该项
                $(obj).parents('button').remove()
            }
        },'json')
}

//删除油位
function delLevel(obj){
    //名字
    var name=$(obj).parents('button').attr('name')

    //站点
    var site=$('#select_site option:selected').val()

    //发送请求
    $.post(url_prefix+'ajax/del_level/',{"site":site,"name":name},
        function(data){
            if(data['ret']=='1101'){
                //页面移除该项
                $(obj).parents('button').remove()
            }
        },'json')
}

//检查通道油机油位的唯一性
function checkPassageMachineLevelName(){
    var type=-1

    //站点名
    var site=$('#select_site option:selected').val()

    //名字
    var name=$('#add_name').val()

    //类型
    var title=$('#myModalLabel').text()

    //type赋值
    if(title=='新增通道'){
        type=0
    }
    else if(title=='新增油机'){
        type=1
    }
    else if(title=='新增油位'){
        type=2
    }
    else{
        return
    }

    //发送请求
    $.post(url_prefix+'ajax/check_passage_machine_level_name/',{"type":type,
       "name":name,"site":site},function(data){
           if(data['ret']!='1101'){
               errorModal(gettext('名字已存在!'))
               $('#add_item_btn').prop("disabled",true);
           }
           else{
               $("#add_item_btn").prop("disabled",false);
           }
       },'json')
}
