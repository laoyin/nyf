//dom ready
$(function(){
  //从cookie中取得用户名和保存标签
  var username=$.cookie('username');
  var rmb = $.cookie('rmb');

  //判断cookie中用户名和标签是否为空,如果存在就填充在页面中
  if(username!==null && rmb==1){
    $("#username").val(username)
    $('input:checkbox').each(function() {
      $(this).attr('checked', true);
    });
  }
})

function login() {

   //
  //取得页面上的属性值
  var username=$('#username').val();
  var pass=$('#password').val();
  var language = $("#language").val()
  if(language == ""){
      alert(gettext("请选择语言!"));
      return 
  }

  //判断用户输入信息的完整性
  if(username==""){
    alert(gettext("请输入用户名"));
    return;
  }
  if(pass==""){
    alert(gettext("请输入密码"));
    return;
  }
  if($('#rmb').prop('checked') == true){
    var tag = 1;
    $.cookie('rmb',1,{path:'/'},{expires:7})
  }

  //新建字典用来保存用户输入的信息
  dict = {};
  dict["username"] = username;
  dict["password"] = pass;
  dict["language"] = Number(language);

  //发送ajax请求,验证用户信息真实性
  $.post('/gcustomer/ajax/check_login/',dict,
    function(data){
      if (data['ret'] =='0001') {
            $.cookie('username',username,{path:'/'})
            parent.location.href="/gcustomer/";
      }
      else{
        alert(data['info']);
      }
    },'json')
return true;
}

//当点击注册页面时将跳转到注册页面
function register() {
  parent.location.href="/gcustomer/register.html";
}
//当键盘敲击回车时出发login()
function enter_login(e) {
  var e = e || window.event;
  var keynum = e.keyCode || e.which;
  if (keynum == 13) {
    login();
  }
}
