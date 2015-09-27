/**
 * Created by jonny on 14-12-11.
 * Modify by niyoufa on 15-7-17.
 */

$(function(){
    $("#next_step").on("click",function(){
            var register_user_type = $("#register_type").val()
            if(register_user_type == ""){
                alert(gettext("请选择注册类型！"));
                return
            }
            $("#next_step").hide()
            $("#the_register_option").hide()
            $("#pre_step").show()
            $("#the_register_page").show()
            

            if(register_user_type == "0"){
                $("#the_comp_option0").show()
            }
            else{
                $("#the_comp_option1").show()
            }
    });
    $("#pre_step").on("click",function(){
            $("#next_step").show()
            $("#the_register_option").show()
            $("#pre_step").hide()
            $("#the_register_page").hide()
            $("#the_comp_option0").hide()
            $("#the_comp_option1").hide()
    });
});

//取出url地址
var url_prefix = $('meta[name="url_prefix"]').attr('content');
var status_ok = "0001";

//检查email格式
function checkEmail(email){
    var reg = /^([a-zA-Z0-9]+[_|\_|\.|\+|\-|=|%]?)*[a-zA-Z0-9]+@([a-zA-Z0-9]+[_|\_|\.|\-|=|%]?)*[a-zA-Z0-9]+\.[a-zA-Z]{2,3}$/;
    return reg.test(email)
}

//注册
function register()
{
    //注册类型
    var register_type = document.getElementById("register_type");

    //注册公司id
    var comp_id = document.getElementById("company_type1");

    //姓名
    var username = document.getElementById("username");

    //密码
    var pass = document.getElementById("password");

    //二次密码
    var repass = document.getElementById("repassword");

    //电子邮箱
    var email = document.getElementById("email");

    //公司名称
    var company = document.getElementById("company");

    //公司类型
    var comp_type = document.getElementById("company_type");

    //区地址
    var district=document.getElementById("xiancode");

    var name_match = /^[a-zA-Z0-9]{3,16}$/;
    
    //检查公司id
    if(register_type.value == "0" && comp_id.value == ""){
        alert(gettext("请选择公司"))
        return
    }

    //检查用户名是否为空
    if(username.value==""){
        alert(gettext("请输入用户名"));
        username.focus();
        return;
    }
    
    //检查用户名格式是否正确
    else if(!(username.value).match(name_match))
    {
        alert(gettext("用户名格式错误！"));
        username.focus();
        return;
    }
    
    //检查密码是否为空
    if(pass.value=="")
    {
        alert(gettext("请输入密码！"));
        pass.focus();
        return;
    }

    //检查密码长度
    else if (pass.value.length<6 || pass.value.length>16) {
        alert(gettext("请输入长度在6到16位之间的密码"));
        pass.value = "";
        pass.focus();
        return;
    }
  
    //检查两次密码是否相同
    if (pass.value!=repass.value) {
        alert(gettext("两次输入的密码不一样！"));
        return;
    }

    //检查邮箱格式
    if(!checkEmail(email.value)){
        alert(gettext("邮箱格式错误！"));
        return;
    }

    var company_match = /^[\u4e00-\u9fa5a-zA-Z0-9\s]{1,}$/;

    //检查公司名称是否为空
    if (register_type.value == "1"  && company.value == "") {
        alert(gettext("请输入公司名称！"));
        company.focus();
        return;
    }

    //检查公司名称
    if( register_type.value == "1" && comp_type.value == "0"){
        alert(gettext("请选择公司类型！"));
        return;
    }
 
     //检查公司名称格式
     else if (company.value != "" && !(company.value).match(company_match)) {
        alert(gettext("公司名称只能包含汉字、字母和数字"));
        company.focus();
        return;
     }

     //检查是否选择区县
     if(district.value=="")
     {
         alert(gettext("请选择区县"));
         district.focus();
         return;
     }

    dict = {};
    dict["register_type"] = register_type.value;
    dict['comp_id'] = comp_id.value;
    dict["username"] = username.value;
    dict["password"] = pass.value;
    dict["email"] = email.value;
    dict["company"] = company.value;
    dict["comp_type"] = comp_type.value;
    dict["district"] = district.value;

    //提交注册信息
    $.post('/gcustomer/ajax/check_register/', 
        dict,function(data){
            if (data['ret'] !='0001') {
                alert(data['info']);
            }
            else{
                alert(data['info']);
                $(username).val("");
                $(pass).val("");
                $(repass).val("");
                $(email).val("");
                $(company).val("");
                $(comp_type).val("0");
                $(district).val("");
            }
        },"json"
    )
    return true;
}

//Dom ready
$(function(){

    //取得城市和区县的信息
    init_china_location();
    init_comp_type();
    init_comp_info();
})

//取得城市和区县的信息
function init_china_location(){

    //取出url地址
    var url_prefix = $('meta[name="url_prefix"]').attr('content');

    //取得省份的信息
    $.post('/gcustomer/ajax/get_china_location/',
       {"parent":0,"level":1},
        function(data){

             //判断返回值是否正确
             if (data.ret!="0001"){
                 alert(data.info)
                 return
             }
             var all_ps=data['dict_city']

             //循环遍历出城市的id和name,并填充到页面中
             for(var i=0;i<all_ps.length;i++){
                 var $html=String.format('<option value="{0}">{1}</option>',all_ps[i][0],all_ps[i][1])
                 $('#shengcode').append($html)
             }
        },
    "json");

    //监听选择市/县的事件
    $('#shengcode').change(function(){

        //取出url地址
        var url_prefix = $('meta[name="url_prefix"]').attr('content');
        var parent = $('#shengcode').val()

        //通过ajax请求取得城市的信息
        $.post('/gcustomer/ajax/get_china_location/',
           {"parent":parent,"level":2},
            function(data){

                //判断返回值是否正确
                if (data.ret!="0001"){
                    alert(data.info)
                    return
                }
                var all_ps=data['dict_city']
                var $shicode = $('#shicode').empty();
                $shicode.append('<option selected value="">gettext("请选择")</option>')
                var $xiancode = $('#xiancode').empty();
                $xiancode.append('<option selected value="">gettext("请选择")</option>')

                //循环遍历出城市的id和name,并填充到页面中
                for(var i=0;i<all_ps.length;i++){
                    var $html=String.format('<option value="{0}">{1}</option>',all_ps[i][0],all_ps[i][1])
                    $('#shicode').append($html)
                }
            },
        "json");
    })

    $('#shicode').change(function(){

     //取出url地址
    var url_prefix = $('meta[name="url_prefix"]').attr('content');
    var parent = $('#shicode').val()

    //通过ajax请求取得区县的信息
    $.post('/gcustomer/ajax/get_china_location/',
       {"parent":parent,"level":3},
        function(data) {

            //判断返回值是否正确
            if (data.ret!="0001"){
                alert(data.info)
                return
            }
            var all_ps = data['dict_city']
            var $xiancode = $('#xiancode').empty();
            $xiancode.append('<option selected value="">gettext("请选择")</option>')

            //循环遍历出城市的id和name,并填充到页面中
            for (var i = 0; i < all_ps.length; i++) {
                 var $html = String.format('<option value="{0}">{1}</option>', all_ps[i][0], all_ps[i][1])
                 $('#xiancode').append($html)
            }
        },
    "json");
    })
}
//获取公司类型
function init_comp_type(){
    //查询公司类型
    $.get("/gcustomer/ajax/get_comp_type/",{},
        function(data){
            if(data.ret != status_ok){
                alert(data.info)
                return 
            }
            //渲染公司类型
            $("#company_type").empty();
            $("#company_type").append(String.format('<option selected value={0}>{1}</option>',0,gettext("请选择公司类型")));
            $(data.objs).each(function(){
                obj = this;
                $("#company_type").append(String.format('<option  value={0}>{1}</option>',obj.value,obj.name));
            });
            
        },"json");
}

//获取公司数据
function init_comp_info(){
    $.get("/gcustomer/ajax/get_comp_list/",{},
        function(data){
                if(data.ret != "0001"){
                    alert(data.info)
                    return 
                }
                $("#company_type1").empty();
                $("#company_type1").append(String.format('<option selected value={0}>{1}</option>',"",gettext("请选择公司")));
                $(data.objs).each(function(){
                    obj = this;
                    $("#company_type1").append(String.format('<option  value={0}>{1}</option>',obj.value,obj.name));
                });
        },"json");
}
