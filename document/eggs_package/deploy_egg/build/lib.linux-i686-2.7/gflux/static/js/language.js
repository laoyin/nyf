//初始化
$(function(){
    //初始化页面
    initUserInfo()
})

//保存新密码
function savePassword(){
    //取得所有值
    var old_value=$('#old_password').val().trim()
    var new_value=$('#new_password').val().trim()
    var repeat_new_value=$('#repeat_new_password').val().trim()

    //check
    if(old_value.length==0 || new_value.length==0 || repeat_new_value.length==0){
        errorModal('输入框不能为空')
        return
    }
    if(new_value!=repeat_new_value){
        errorModal('两次输入的新密码不相同')
        return
    }

    //check password format
    if(new_value.length<6 || new_value.length>16){
        errorModal('请输入长度在6到16位之间的密码')
        return
    }

    //send to server
    $.post(url_prefix+'ajax/update_password/',
        {old_password:old_value,new_password:new_value},
        function(data){
            if(data.ret!='1101'){
                errorModal(data.info)
                return
            }

            infoModal('修改密码成功')
        }
    )
}

//初始化用户信息
function initUserInfo(){
    $.post(url_prefix+'ajax/get_user_info/',function(data){
            if(data.ret!='1101'){
              alert(data.info)
              return
            }
            $('#user_name').text(data.username)
            var provinces = data['provinces']
            var districts = data['districts']
            var citys = data['citys']

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
}

//设置多语言
function setLanguage(){
  //获取要设置的语言类型
  var language_type=$('#select_language option:selected').val()
  var url_prefix='/'+$('meta[name="url_prefix"]').attr('content')
  $.post(url_prefix+'ajax/set_language/',{
    type:language_type,
    },function(data){
          if(data.ret!='1101'){
            alert(data.info)
            return
          }
            alert(data.info)
            location.href='/gflux/'

      },'json')
}

//保存对用户类型的修改
function saveUserInfo(){
    //获取更改类型
    var user_name=$('#user_name').text()

    //取得省县代码
    var province=$('#shengcode').val()

    //取得市县代码
    var city=$('#shicode').val()

    //取得区县代码
    var district=$('#xiancode').val()

    //开始检查
    if(district.length==0){
        alert(gettext('请选择区县'))
        return
    }

    //发送请求
    $.post(url_prefix+'ajax/update_user_info/',
        {user_name:user_name,
         district:district},
    function(data){
        if(data['ret']=='1101'){
            alert(gettext('保存成功!'))
        }else{
            alert(data.info)
        }
    },'json')
}
