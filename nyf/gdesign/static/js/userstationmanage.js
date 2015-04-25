//dom ready
$(function(){
    //查看第一个用户
    manageUserStation()

    //取得省/市/區的信息
    init_china_location()
})


//管理用户的站点列表
function manageUserStation(){
    $('.edit_area').show()

    //取得用户id
    var user_id=$('#signal-user-selector').val()

    //清空已拥有列表,重置所有站点列表
    $('#already_got ul').empty()
    $('#all_sites').empty()
    for(var idx=0;idx<all_stations.length;idx++){
        var site=all_stations[idx]
        var option=new Option(site.desc,site.name)
        $('#all_sites').append(option)
    }

    //向后端请求用户的站点列表
    window.user_id=user_id
    $.get(url_prefix+'ajax/get_user_station/',{user_id:user_id},function(data){
        if(data.ret!='1101'){
            alert(data.info)
            return
        }

        //渲染已拥有
        for(var idx=0;idx<data.data.length;idx++){
            var site=data.data[idx]

            //delete from all
            var item=$('#all_sites').find('option[value="'+site.name+'"]').remove()


            //add to alreay
            $('#already_got ul').append(String.format('<div class="got_item" \
                user_id="{2}" site_name="{0}" >\
                {1}\
                <span onclick="editModal(this)" site_name="{0}" \
                class="glyphicon glyphicon-edit" style="margin-left:5px"></span>\
                <span onclick="removeSite(this)" \
                class="glyphicon glyphicon-remove"></span>\
            <div>',site.name,site.desc,user_id))
        }
    },'json')
}

//删除已拥有的站点
function removeSite(that){
    that=$(that).parent().eq(0)
    var user_id=$(that).attr('user_id')
    var site_name=$(that).attr('site_name')
    var site_desc=$(that).text()

    //request
    $.post(url_prefix+'ajax/remove_user_site/',{user_id:user_id,site_name:site_name},function(data){
        if(data.ret!='1101'){
            alert(data.info)
            return
        }

        //remove from dom
        $(that).remove()

        //add to all
        var option=new Option(site_desc,site_name)
        $('#all_sites').append(option)

    },'json')
}

//添加站点
function addNewSite(){
    var site_name=$('#all_sites').val()

    //检查站点
    if(!site_name){
        alert('请选择站点!')
        return
    }

    var site_desc=$('#all_sites').find('option[value="'+site_name+'"]').text()

    //request
    $.post(url_prefix+'ajax/add_user_site/',{user_id:user_id,site_name:site_name},function(data){
        if(data.ret!='1101'){
            alert(data.info)
            return
        }

        //delete from all
        var item=$('#all_sites').find('option[value="'+site_name+'"]').remove()


        //add to alreay
        $('#already_got ul').append(String.format('<div class="got_item" \
            user_id="{2}" site_name="{0}" >\
            {1}\
            <span onclick="editModal(this)" site_name="{0}" \
            class="glyphicon glyphicon-edit" style="margin-left:5px"></span>\
            <span onclick="removeSite(this)" \
            class="glyphicon glyphicon-remove"></span>\
        <div>',site_name,site_desc,user_id))
    },'json')
}


//弹出编辑框
function editModal(that){
    var site_name=$(that).attr('site_name')
    $.post(url_prefix+'ajax/get_info_by_sitename/',{site_name:site_name},function(data){

        //判斷返回值是否正確
        if(data['ret']!=1101){
          alert(data['info'])
          return
        }
        var provinces = data['provinces']
        var districts = data['districts']
        var citys = data['citys']
        var province = data['province']
        var district = data['district']
        var city = data['city']
        $('#add_name').val(data.data)

        $('#shengcode').empty()
        //循环遍历出省的id和name,并填充到页面中
        for(var i=0;i<provinces.length;i++){
          var $html=String.format('<option value="{0}">{1}</option>',
            provinces[i]['id'],provinces[i]['name'])
          $('#shengcode').append($html)
        }

        $('#shicode').empty()
        //循环遍历出市的id和name,并填充到页面中
        for(var i=0;i<citys.length;i++){
          var $html=String.format('<option value="{0}">{1}</option>',
          citys[i]['id'],citys[i]['name'])
          $('#shicode').append($html)
        }

        $('#xiancode').empty()
        //循环遍历出區的id和name,并填充到页面中
        for(var i=0;i<districts.length;i++){
          var $html=String.format('<option value="{0}">{1}</option>',
          districts[i]['id'],districts[i]['name'])
          $('#xiancode').append($html)
        }

        //將當前的站點爲止選出來
        $("#shengcode").find('option[value="'+data.province+'"]')
            .prop('selected',true)
        $("#shicode").find('option[value="'+data.city+'"]')
            .prop('selected',true)
        $("#xiancode").find('option[value="'+data.district+'"]')
            .prop('selected',true)
    },'json')
    $('#myModalLabel').text(gettext('编辑油站'))
    $('#name').text(site_name)
    $('#myModal').modal('show');
}

//修改油站描述信息
function saveStationInfo(that){
    var site_name=$('#name').text()
    var description=$('#add_name').val()

    //描述正确的正则表达式
    var desc_match = /^[\u4e00-\u9fa5a-zA-Z0-9]{1,}$/;

    //取得省县代码
    var province=$('#shengcode').val()

    //取得市县代码
    var city=$('#shicode').val()

    //取得区县代码
    var district=$('#xiancode').val()

    //开始检查
    if(description.length==0){
        alert(gettext('站点名称不能为空!'))
        return
    }
    else if (desc_match.test(description) == false) {
        alert(gettext('站点名称只能包含汉字、字母和数字!'))
        return
    }
    else if(district.length==0){
        alert(gettext('请选择区县'))
        return
    }
    $.post(url_prefix+'ajax/save_station_info/',
      {site_name:site_name,
       description:description,
       province:province,
       city:city,
       district:district
      },
      function(data){
        if(data.ret!='1101'){
            alert(data.info)
            return
        }

        //添加删除和编辑按钮
        $("div[site_name='"+site_name+"']").text(description)
        $("div[site_name='"+site_name+"']").append(String.format('<span onclick="editModal(this)" \
          site_name="{0}" class="glyphicon glyphicon-edit" style="margin-left:5px"></span>',site_name))
        $("div[site_name='"+site_name+"']").append('<span onclick="removeSite(this)" \
          class="glyphicon glyphicon-remove" style="margin-left:5px"></span>')

    },'json')

    $('#myModal').modal('toggle');

}
