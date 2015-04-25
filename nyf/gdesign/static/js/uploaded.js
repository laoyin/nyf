$(function(){
    //初始化页面
    uploadedPage()

    //初始化站点以及地点选项
    init_import_data_filter()
})

//初始化已上传文件页面
function uploadedPage() {
    var tbody = $("#uploaded_table");

    //all file下拉框
    var allFilesSelect=$("#select_all_file");

    //card file下拉框
    var cardFilesSelect=$("#select_card_file");

    //all file选项
    var oppAll = new Option(gettext("请选择all文件"),-1);

    //card file选项
    var oppCard = new Option(gettext("请选择card文件"),-1);
    allFilesSelect.append(oppAll);
    cardFilesSelect.append(oppCard);

    //获取已上传的文件
    $.post(url_prefix+'ajax/check_uploaded_files/',function(data){
        if (data['ret']=='1101') {
            datas=data['data'];
            for (var i=0;i<datas.length;i++){
                info=datas[i];
                name=info['name'];
                var opp1 = new Option(name,name);
                var opp2 = new Option(name,name);
                allFilesSelect.append(opp1);
                cardFilesSelect.append(opp2);
                creator=info['creator'];
                time=info['time'];

                //插入新行
                var tmp_row=String.format(
                    '<tr>\
                        <td>{0}</td>\
                        <td>{1}</td>\
                        <td>{2}</td>\
                        <td>\
                        <input onclick="deleteFile(this)" type="submit" \
                        class="btn btn-info" value="{3}"/></td>\
                    </tr>'
                ,name,time,creator,gettext("删除"))
                var $tmp_row=$(tmp_row)
                $tmp_row.data('file_obj_id',info['id'])
                tbody.append($tmp_row)
            }
        }
    },'json')
}

//删除已上传的文件
function deleteFile(obj){
    //根据行删除文件
    var obj_id=$(obj).parents('tr').data('file_obj_id')
    var url_prefix='/'+$('meta[name="url_prefix"]').attr('content')
    $.post(url_prefix+'ajax/deleteFile/',{id:obj_id},function(data){
        if(data.ret!='1101'){
            infoModal(data.info)
            return
        }

        $(obj).parents('tr').remove()
    },'json')
}

//显示数据导入的对话框（已上传文件页面）
function showDataModel() {
  $('#select_all_file option:first').prop('selected',true)
  $('#select_card_file option:first').prop('selected',true)
  $('#select_location option:first').prop('selected',true)
  $('#select_site option:first').prop('selected',true)
  $('#dataModal').modal('show');
}

//导入数据
function importData() {
    //all文件名字
    var all_name=$('#select_all_file').val()

    //未选择all file
    if(all_name=='-1'){
        alert(gettext('请选择all文件名！'))
        return
    }

    //card文件名字
    var card_name=$('#select_card_file').val()

    //未选择card file
    if(card_name=='-1'){
        alert(gettext('请选择card文件名!'))
        return
    }

    //获取地点
    var location_name=$('#select_location option:selected').val()

    //未选择区域
    if(location_name=='-1' || location_name=='+'){
        alert(gettext('请选择正确的区域！'))
        return
    }

    //获取地点描述
    var location_desc=$('#select_location option:selected').text()

    //站点名字
    var site_name=$('#select_site option:selected').val()

    //未选择站点
    if(site_name=='-1' || site_name=='+'){
        alert(gettext('请选择正确的站点！'))
        return
    }

    //获取站点描述
    var site_desc=$('#select_site option:selected').text()

    //send request
    var url_prefix='/'+$('meta[name="url_prefix"]').attr('content')
    $.post(url_prefix+'ajax/importData/',{
        site:site_name,
        site_desc:site_desc,
        location:location_name,
        location_desc:location_desc,
        all_file:all_name,
        card_file:card_name
    },function(data){

        //导入失败
        if(data.ret!='1101'){
            infoModal(data.info)
            return
        }
        $('#dataModal').modal('hide')
        infoModal(gettext('成功导入数据！'))
    },'json')
}

//初始化站点和地区选项
function init_import_data_filter(){

    //站点区域
    var siteSelect = $("#select_site");
    var new_site_opt=new Option(gettext('添加新加油站'),'+')

    //选择+,显示新建站点区域
    $(siteSelect).change(function(){
        var selected=$("#select_site option:selected").val()
        if(selected=='+')
            $('.add_new_site').toggle()
    })

    //初始化所有站点以及新建站点
    siteSelect.append(new_site_opt);
    for (var idx=0;idx<all_stations.length;idx++){
        var key=all_stations[idx].name
        var value=all_stations[idx].description
        var opp = new Option(value,key);
        siteSelect.append(opp);
    }

    //地区区域
    var locationiSelect=$("#select_location");

    //选择+,显示新建地点区域
    var new_location_opt=new Option(gettext('添加新区域'),'+')
    $(locationiSelect).change(function(){
        var selected=$("#select_location option:selected").val()
        if(selected=='+')
            $('.add_new_location').toggle()
    })

    //初始化所有地点以及新建地点
    locationiSelect.append(new_location_opt);
    for (var idx=0;idx<all_locations.length;idx++){
        if(all_locations[idx].id==0)
            continue

        var key=all_locations[idx].name
        var value=all_locations[idx].description
        var opp = new Option(value,key);
        locationiSelect.append(opp);
    }
}


//新建站点
function addSite(){
    var name=$('#add_site_name').val()

    //正则站点名字
    var name_match = /^[A-Z_]+$/;

    //检查站点名字格式
    if(name.length==0){
        alert(gettext('加油站名不能为空!'))
        return
    } else if (name_match.test(name) == false) {
        alert(gettext('站点代码格式错误!'))
        return
    }

    //获取站点描述
    var desc=$('#add_site_description').val()

    //正则站点描述
    var desc_match = /^[\u4e00-\u9fa5a-zA-Z0-9]{1,}$/;

    //检查站点描述格式
    if(desc.length==0){
        alert(gettext('描述不能为空!'))
        return
    } else if (desc_match.test(desc) == false) {
        alert(gettext('站点名称只能包含汉字、字母和数字!'))
        return
}

    var new_site_opt=new Option(desc,name)
    var siteSelect = $("#select_site");
    siteSelect.append(new_site_opt);

    //toggle
    $('.add_new_site').toggle()

    //select
    $(new_site_opt).prop('selected',true)
}

// hide add site area
function hideSite(){
    $('#select_site option:first').attr('selected','selected');
    $('.add_new_site').hide();
}

//隐藏新建location区域
function hideLocation(){
    $('#select_location option:first').attr('selected','selected');
    $('.add_new_location').hide();
}


//新建地区
function addLocation(){

    //获取地区名字
    var name=$('#add_location_name').val()

    //正则地区名字
    var name_match = /^[A-Z_]+$/;

    //检查名字格式
    if(name.length==0){
        alert(gettext('区域名不能为空!'))
        return
    }else if (name_match.test(name) == false) {
        alert(gettext('地区代码格式错误!'))
        return
    }

    //获取描述信息
    var desc=$('#add_location_description').val()

    //正则描述信息
    var desc_match = /^[\u4e00-\u9fa5a-zA-Z0-9]{1,}$/;

    //检查描述信息格式
    if(desc.length==0){
        alert(gettext('描述不能为空!'))
        return
    }else if (desc_match.test(desc) == false){
        alert(gettext('地区名称只能包含汉字、字母和数字!'))
        return
    }

    var new_location_opt=new Option(desc,name)
    var locationiSelect = $("#select_location");
    locationiSelect.append(new_location_opt);

    //toggle
    $('.add_new_location').toggle()

    //select
    $(new_location_opt).prop('selected',true)
}


//检查站点唯一性(失去焦点时检测)
function checkStationUnique(){
  var name=$('#add_site_name').val()

  //为空不需要检测
  if (name.length==0){
    return
  }

  //发送请求
  $.post(url_prefix+'ajax/check_unique/',{"type":1,"name":name},function(data){

      //已经存在,显示提示信息
      if (data['ret']=='1111') {
        $('#input-check-site-message').show();
        $('#add_site_name').val("")
        $('#add_site_name').focus().select();

      }else{
        $('#input-check-site-message').hide();
      }
  },'json')
}

//检查地点唯一性(失去焦点时候检查)
function checkLocationUnique(){
  //获取名字
  var name=$('#add_location_name').val()

  //为空不进行检查
  if (name.length==0){
    return
  }

  //发送请求
  $.post(url_prefix+'ajax/check_unique/',{"type":2,"name":name},function(data){

      //地点信息已经存在,显示提示信息
      if (data['ret']=='1111') {
        $('#input-check-location-message').show();
        $('#add_location_name').val("")
        $('#add_location_name').focus().select();

      }else{
        $('#input-check-location-message').hide();
      }
  },'json')
}
