//dom ready
$(function(){
    //存放点击编辑时的id
    window.fuel_type_id=''

    //存放点击编辑时的name
    window.fuel_type_name=''

    //0:新增  1:编辑
    window.edit_or_add=-1

    //渲染界面
    showAllFuelType()
})

//显示所有油品编号与系统定义油品类型关系
function showAllFuelType(){
    $('.edit_area').show()

    //将所有的名字显示出来
    for(var idx=0;idx<all_fuel_type_relation.length;idx++){
        //add to alreay
        $('#already_got ul').append(String.format('<div class="got_item" \
             name="{0}">\
            {0} \
            <span onclick="editModal(this)" name={0} type_id="{1}" barcodes="{2}" \
            class="glyphicon glyphicon-edit" style="margin-left:5px"></span>\
            <span onclick="removeRelation(this)" name={0} type_id="{1}" barcodes="{2}" \
            class="glyphicon glyphicon-remove"></span>\
            </div>',all_fuel_type_relation[idx].name,all_fuel_type_relation[idx].id,all_fuel_type_relation[idx].barcodes))
    }
}

//编辑油品编号与系统定义油品类型关系
function editModal(that){
    edit_or_add=1

    //清空
    $('#all_barcodes').empty()
    var name=$(that).attr('name')
    var id=$(that).attr('type_id')
    var barcodes=$(that).attr('barcodes')

    //刷新点开编辑框的id和name
    fuel_type_id=id
    fuel_type_name=name
    barcodes=barcodes.split(",")

    //渲染所有barcode
    for(var i=0;i<barcodes.length;i++){
        if(barcodes[i]==""){
            continue
        }
        $('#all_barcodes').append(String.format('<button type="button" class="btn btn-default btn-xs" \
            style="margin-left:5px;margin-top:5px;font-size:8px" name="{0}">\
            {0}\
            <span class="glyphicon glyphicon-minus" onclick="removeOne(this)" name="{0}">\
            </span>\
            </button>',barcodes[i]))
    }
    $('#edit_name').val(name)
    $('#edit_id').val(id)
    $('#myModalLabel').text(gettext('编辑'))
    $('#myModal').modal('show');
}

//添加对话框
function addModal(){
    edit_or_add=0
    $('#all_barcodes').empty()
    fuel_type_id=''
    fuel_type_name=''
    $('#edit_name').val('')
    $('#edit_id').val('')
    $('#myModalLabel').text(gettext('新增'))
    $('#myModal').modal('show');
}

//删除一个barcode
function removeOne(that){
    var barcode=$(that).attr('name')
    $('#all_barcodes').children(String.format('button[name="{0}"]',barcode)).remove()
}

//新增一个barcode
function addNewOne(){
    var barcode=$('#edit_barcodes').val()

    //如果barcode已经存在就不能添加
    if($('#all_barcodes').children(String.format('button[name="{0}"]',barcode)).length>0){
        alert(gettext('已存在!'))
        $('#edit_barcodes').val('')
        return
    }
    if(barcode==''){
        alert(gettext('不能为空!'))
        $('#edit_barcodes').val('')
        return
    }

    //油品编号为纯数字
    var re_barcode='^[0-9]*$'

    if(barcode.match(re_barcode)==null){
        alert(gettext('油品编号必须由数字组成!'))
        $('#edit_barcodes').val('')
        return
    }

    //渲染新添加的barcode
    $('#all_barcodes').append(String.format('<button type="button" class="btn btn-default btn-xs" \
        style="margin-left:5px;margin-top:5px;font-size:8px" name="{0}">\
        {0}\
        <span class="glyphicon glyphicon-minus" onclick="removeOne(this)" name="{0}">\
        </span>\
        </button>',barcode))
   $('#edit_barcodes').val('')
}

//修改信息
function modifyInfo(){
    var name=$('#edit_name').val()
    var id=$('#edit_id').val()

    //名字不能为空
    if(name==''){
        alert(gettext('名字不能为空!'))
        return
    }

    if(id==''){
        alert(gettext('油品类型不能为空!'))
        return
    }

    //油品编号为纯数字
    var re_barcode='^[0-9]*$'

    //油品类型1101+省行政区划代码前2位+标准代数2位+汽油牌号2位 一共10位数
    var re_fuel_type='^1101(00|11|12|13|14|15|21|22|23|31|32|33|34|35|36|37|41|42|43|44|45|46|50|51|52|53|54|61|62|63|64|65|71|81|82{1})([0-9]{4})$'

    //如果油品类型格式不正确
    if(id.match(re_fuel_type)==null){
        alert(gettext('油品类型格式为1101+省行政区划代码前2位+标准代数2位+汽油牌号2位!'))
        return
    }
    var barcodes=[]
    for(var i=0;i<$('#all_barcodes').children().length;i++){

        //油品编号不是纯数字
        if($('#all_barcodes').children()[i].name.match(re_barcode)==null){
            alert(gettext('油品编号必须由数字组成!'))
            break
            return
        }
        barcodes.push($('#all_barcodes').children()[i].name)
    }

    if(barcodes.length==0){
        alert(gettext('油品编号不能为空!'))
        return
    }

    //type:0 id和name都改变了  1:改变了name  2:改变了id  3:新增
    var type=-1
    //新增
    if(edit_or_add==0){
        type=3
    }else if(edit_or_add=1){
        if(name!=fuel_type_name&&id!=fuel_type_id){
            type=0
        }else if(name!=fuel_type_name){
            type=1
        }else if(id!=fuel_type_id){
            type=2
        }
    }

    //发送请求
    $.post(url_prefix+'ajax/edit_fuel_type_relation/',{type:type,pre_id:fuel_type_id,next_id:id,
        next_name:name,next_barcodes:barcodes},function(data){
            if(data.ret!='1101'){
                alert(data.info)
                return
            }
            //type:0 id已存在  1 name已存在  2 更新  3  新增
            if(data.type=='0'){
                alert(gettext('油品类型已存在'))

                //清空id框
                $('#edit_id').val('')
            }else if(data.type=='1'){
                alert(gettext('名字已存在'))

                //清空name框
                $('#edit_name').val('')
            }else if(data.type=='2'){
                $(String.format('.got_item[name="{0}"]',fuel_type_name)).attr('name',name)
                $(String.format('.got_item[name="{0}"]',name)).text(name)
                $(String.format('.got_item[name="{0}"]',name)).append(String.format('<span onclick="editModal(this)" \
                        name="{0}" type_id="{1}" barcodes="{2}" \
                        class="glyphicon glyphicon-edit"></span> \
                        <span onclick="removeRelation(this)" name={0} type_id="{1}" barcodes="{2}" \
                        class="glyphicon glyphicon-remove"></span>',name,id,barcodes.toString()))
                $('#myModal').modal('toggle');
            }else{
                $('#already_got ul').append(String.format('<div class="got_item" \
                    name="{0}">\
                   {0} \
                   <span onclick="editModal(this)" name={0} type_id="{1}" barcodes="{2}" \
                   class="glyphicon glyphicon-edit" style="margin-left:5px"></span>\
                   <span onclick="removeRelation(this)" name={0} type_id="{1}" barcodes="{2}" \
                   class="glyphicon glyphicon-remove"></span>\
               </div>',name,id,barcodes.toString()))
               $('#myModal').modal('toggle');
            }
        },'json')
}

//删除一个关系
function removeRelation(that){
    var type_id=$(that).attr('type_id')
    that=$(that).parent().eq(0)
    $.post(url_prefix+'ajax/remove_fuel_type_relation/',{type_id:type_id},function(data){
        if(data.ret!='1101'){
            alert(data.info)
            return
        }
        that.remove()
    },'json')


}
