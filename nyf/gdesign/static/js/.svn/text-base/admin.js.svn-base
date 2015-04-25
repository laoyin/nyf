//初始化
$(function(){
    //初始化页面
    admin_request_user()
})

//初始化用户管理页面
function admin_request_user() {
  var tbody = $("#request_user_table");
  $('#request_user_table').find('tr').not('.active').remove()

  //根据类型查找相应的用户信息
  var type=$('meta[name="filter_user_type"]').attr('content');
  $.post(url_prefix+'ajax/check_users/',{"type":type},function(data){
      if (data['ret']=='1101') {
            datas=data['data'];
            for (var i=0;i<datas.length;i++) {
              info=datas[i];
              name=info['name'];
              time=info['time']
              company=info['company']
              type=info['type']

              //获取用户类型
              var typeText=gettext("待审核用户");
              if (type==1) {
                typeText=gettext("试用版用户")
              }
              else if (type==2) {
                 typeText=gettext("普通版用户")
              }
              else if(type==3){
                typeText=gettext("专业版用户")
              }
              else if(type==4){
                  typeText=gettext("管理员账户")
              }
              else{
                typeText=gettext("待审核用户")
              }

              //插入行
              var tmp_row=String.format(
                  '<tr>\
                     <td>{0}</td>\
                     <td>{1}</td>\
                     <td>{2}</td>\
                     <td>{3}</td>\
                     <td><input type="submit" class="btn btn-info" \
                     onclick="editUserType(this)" value="{4}"</td>'
                     ,name,typeText,time,company,gettext("处理"))
              var $tmp_row=$(tmp_row)
              tbody.append($tmp_row)
            }
          }
  },'json')
}

//保存对用户类型的修改
function saveUserType(){
    //获取更改类型
    var user_type=$('select[name="account_type"]').val()

    //获取更改用户的名字
    var user_name=$('#myModal').modal('hide').data('username')
    var url_prefix='/'+$('meta[name="url_prefix"]').attr('content')
    $.post(url_prefix+'ajax/update_user_type/',{user_name:user_name,user_type:user_type},
    function(data){
        if(data['ret']=='ok'){

            //更新界面
            admin_request_user()
        }else{
            alert(data.info)
        }
    },'json')
}

//显示编辑权限对话框
function editUserType(obj){
    //获取要编辑的用户名字
    var user_name=$(obj).parents('tr').find('td:first').text()
    $('#user_name').text(user_name)
    $('#myModal').modal('show').data('username',user_name)
}
