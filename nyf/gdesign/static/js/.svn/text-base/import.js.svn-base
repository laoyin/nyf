//dom ready，初始化
$(function(){

    //初始化上传按钮
    initFileUploadButton()

    //初始化站点和位置信息
    initLocationSite()
})

//开始导入数据
function startImportData(){

    //location
    var location=$('#select_location option:selected').val()
    var location_desc=$('#select_location option:selected').text()

    //取得省/市/县的信息
    var province = $('#shengcode').val()
    var city = $('#shicode').val()
    var district = $('#xiancode').val()

    //判断数据是否导入完毕的标志
    var import_flag_string=""
    var dim={}
    if(location=='-1'){
        alert(gettext('请选择地区'))
        return
    }

    //site
    var site=$('#select_site option:selected').val()
    var site_desc=$('#select_site option:selected').text()
    if(site=='-1'){
        alert(gettext('请选择站点'))
        return
    }

    //cache site
    $.cookie('last-upload-site',site,{path: '/' })

    //cache time
    $.cookie('last-upload-time',new Date().toLocaleString(),{path:'/'})

    var type=$('#select_type option:selected').val()

    //导入数据的类型,0：sp数据，1：中油数据，2：延长壳牌数据
    if (type==-1) {
        alert(gettext('请选择数据类型'))
        return
    }

    //中油数据
    else if (type==1) {

        //check file
        if(uploaded_all_file==false){
            alert(gettext('请上传ALL文件'))
            return
        }
        if(on_upload_all_file){
            alert(gettext('请耐心等待ALL文件上传完毕'))
            return
        }
        var all_file=uploaded_all_file_name
        if(uploaded_card_file==false){
            alert(gettext('请上传CARD文件'))
            return
        }
        if(on_upload_card_file){
            alert(gettext('请耐心等待CARD文件上传完毕'))
            return
        }
        var card_file=uploaded_card_file_name
        dim['type']=type
        dim['site']=site
        dim['site_desc']=site_desc
        dim['location']=location
        dim['location_desc']=location_desc
        dim['all_file']=all_file
        dim['card_file']=card_file
        dim['province']=province
        dim['city']=city
        dim['district']=district
    }

    //sp
    else if (type==0) {
        if(uploaded_sp_file==false){
            alert(gettext('请上传文件'))
            return
        }
        if(on_upload_sp_file){
            alert(gettext('请耐心等待文件上传完毕'))
            return
        }
        var sp_file=uploaded_sp_file_name
        dim['type']=type
        dim['site']=site
        dim['location']=location
        dim['location_desc']=location_desc
        dim['sp_file']=sp_file
        dim['site_desc']=site_desc
        dim['province']=province
        dim['city']=city
        dim['district']=district
    }

    //ycshell
    else if (type==2) {
        if(uploaded_shell_file==false){
            alert(gettext('请上传文件'))
            return
        }
        if(on_upload_shell_file){
            alert(gettext('请耐心等待文件上传完毕'))
            return
        }
        var ycshell_file=uploaded_shell_file_name
        dim['type']=type
        dim['site']=site
        dim['location']=location
        dim['location_desc']=location_desc
        dim['ycshell_file']=ycshell_file
        dim['site_desc']=site_desc
        dim['province']=province
        dim['city']=city
        dim['district']=district
    }

    //submit task
    $.post(url_prefix+'ajax/importData/',dim,function(data){
        import_flag_string=data.import_flag_string
        if(data.ret!='1101'){
            infoModal(data.info)
            return
        }
        $('#dataModal').modal('hide')
        infoModal(gettext('成功提交导入数据任务！'),null,null,function(){
            //显示当期进程
            $('.process-form').show();
            $('.progress').css('visibility','hidden');
            $('.main-form').slideUp()

            //定时检查进程
            $('#process-log').load(url_prefix+'ajax/show_import_data_process/')
            var upcheck=setInterval(function(){
                $('#process-log').load(url_prefix+'ajax/show_import_data_process/',function(response){
                    if (response.indexOf(import_flag_string)>=0) {
                        $('.image-loading').hide();
                        clearInterval(upcheck)
                    }
                })
            },60*1000)
        })
    },'json');
}

//初始化地区和站点
function initLocationSite(){

    //site
    var siteSelect = $("#select_site");
    for (var idx=0;idx<all_stations.length;idx++){
        var key=all_stations[idx].name
        var value=all_stations[idx].description
        var opp = new Option(value,key);
        siteSelect.append(opp);
    }

    //location
    var locationiSelect=$("#select_location");
    for (var idx=0;idx<all_locations.length;idx++){
        if(all_locations[idx].id==0)
            continue

        var key=all_locations[idx].name
        var value=all_locations[idx].description
        var opp = new Option(value,key);
        locationiSelect.append(opp);
    }

}

//初始化上传按钮
function initFileUploadButton(){
    //先隐藏上传区域
    $('#upload-form-ycshell').hide()
    $('#upload-form-sp').hide()
    $('#upload-form').hide()

    //初始化上传状态
    window.uploaded_all_file=false
    window.uploaded_card_file=false
    window.on_upload_all_file=false
    window.on_upload_card_file=false
    window.on_upload_shell_file=false
    window.uploaded_shell_file=false
    window.uploaded_sp_file=false
    window.on_upload_sp_file=false

    //中油上传区域按钮绑定

    //all file upload button
    var uploader_all = new qq.FileUploader_image({
        action: url_prefix+"ajax/upload_file/",
        element: $('#upload-all')[0],
        allowedExtensions: ['txt','xlsx','xls'],
        multiple: false,
        onSubmit: function (id, fileName) {
            //开始上传
            window.on_upload_all_file=true
        },
        onComplete: function (id, fileName, responseJSON) {
            //上传完成
            window.on_upload_all_file=false

            //check response
            var data=responseJSON
            if(data.ret!='1101'){
                errorModal(gettext(String.format('上传文件{0}失败!{1}',
                    fileName,data.info)))
                return
            }

            //成功上传
            window.uploaded_all_file=true

            //保存文件名
            window.uploaded_all_file_name=fileName

        },
        onProgress :function(id,fileName,loaded,total){
            var percent=loaded*100/total;
            $('.progress.all-file').css('visibility','visible')
                .find('.progress-bar').text(percent+'%').css('width',percent+'%')
        }
    });

    //card file upload button
    var uploader_card = new qq.FileUploader_image({
        action: url_prefix+"ajax/upload_file/",
        element: $('#upload-card')[0],
        allowedExtensions: ['txt','xlsx','xls'],
        multiple: false,
        onSubmit: function (id, fileName) {
            //开始上传
            window.on_upload_card_file=true
        },
        onComplete: function (id, fileName, responseJSON) {
            //上传完成
            window.on_upload_card_file=false

            //check response
            var data=responseJSON
            if(data.ret!='1101'){
                errorModal(gettext(String.format('上传文件{0}失败!{1}',
                    fileName,data.info)))
                return
            }

            //成功上传
            window.uploaded_card_file=true

            //保存文件
            window.uploaded_card_file_name=fileName
        },
        onProgress :function(id,fileName,loaded,total){
            var percent=loaded*100/total;
            $('.progress.card-file').css('visibility','visible')
                .find('.progress-bar').text(percent+'%').css('width',percent+'%')
        }
    });

    //sp集团上传区域按钮绑定

    //shell file upload button
    var uploader_sp= new qq.FileUploader_image({
        action: url_prefix+"ajax/upload_file/",
        element: $('#upload-sp')[0],
        allowedExtensions: ['txt','xlsx','xls'],
        multiple: false,
        onSubmit: function (id, fileName) {
            //开始上传
            window.on_upload_sp_file=true
        },
        onComplete: function (id, fileName, responseJSON) {
            //上传完成
            window.on_upload_sp_file=false

            //check response
            var data=responseJSON
            if(data.ret!='1101'){
                errorModal(gettext(String.format('上传文件{0}失败!{1}',
                    fileName,data.info)))
                return
            }

            //上传成功
            window.uploaded_sp_file=true

            //保存文件名
            window.uploaded_sp_file_name=fileName

        },
        onProgress :function(id,fileName,loaded,total){
            var percent=loaded*100/total;
            $('.progress.sp-file').css('visibility','visible')
                .find('.progress-bar').text(percent+'%').css('width',percent+'%')
        }
    });

    //ycshell上传区域按钮绑定

    //shell file upload button
    var uploader_shell = new qq.FileUploader_image({
        action: url_prefix+"ajax/upload_file/",
        element: $('#upload-ycshell')[0],
        allowedExtensions: ['txt','xlsx','xls'],
        multiple: false,
        onSubmit: function (id, fileName) {
            //开始上传
            window.on_upload_shell_file=true
        },
        onComplete: function (id, fileName, responseJSON) {
            //上传完成
            window.on_upload_shell_file=false

            //check response
            var data=responseJSON
            if(data.ret!='1101'){
                errorModal(gettext(String.format('上传文件{0}失败!{1}'
                    ,fileName,data.info)))
                return
            }

            //上传成功
            window.uploaded_shell_file=true

            //保存文件名
            window.uploaded_shell_file_name=fileName

        },
        onProgress :function(id,fileName,loaded,total){
            var percent=loaded*100/total;
            $('.progress.ycshell-file').css('visibility','visible')
              .find('.progress-bar').text(percent+'%').css('width',percent+'%')
        }
    });
}

//取消添加新站点或新地区
function hideNewArea(obj){
    $(obj).parents('.new-select-option').toggle('slideUp')
}

//显示添加新地区
function showAddLocation(){
    if($('.add_new_location').is(':visible')==false)
        $('.add_new_location').toggle('slideDown')
}

//显示添加新站点
function showAddSite(){
    if($('.add_new_site').is(':visible')==false)
        $('.add_new_site').toggle('slideDown')
}

//添加新站点
function addSite(){
    //取得站点名
    var name=$('#add_site_name').val()

    //站点名正确的正则表达式
    var name_match = /^[A-Z_]+$/;

    //取得县的信息
    var district = $('#xiancode').val()
    //开始检查
    if(name.length==0){
        alert(gettext('站点代码不能为空!'))
        return
    }
    else if (name_match.test(name) == false) {
        alert(gettext('站点代码格式错误!'))
        return
    }

    //取得站点描述
    var desc=$('#add_site_description').val()

    //描述正确的正则表达式
    var desc_match = /^[\u4e00-\u9fa5a-zA-Z0-9]{1,}$/;

    //开始检查
    if(desc.length==0){
        alert(gettext('站点名称不能为空!'))
        return
    }
    else if (desc_match.test(desc) == false) {
        alert(gettext('站点名称只能包含汉字、字母和数字!'))
        return
    }
    else if (district.length==0){
      alert(gettext('请选择区县'))
      return
    }

    //添加到选项中
    var siteSelect = $("#select_site");
    var new_site_opt=new Option(desc,name)
    siteSelect.append(new_site_opt);

    //toggle
    $('.add_new_site').toggle('slideUp')

    //select
    $(new_site_opt).prop('selected',true)
}

//添加新地区
function addLocation(){
    //取得地区名
    var name=$('#add_location_name').val()

    //地区名正确的正则表达式
    var name_match = /^[A-Z_]+$/;

    //开始检查
    if(name.length==0){
        alert(gettext('地区代码不能为空!'))
        return
    }
    else if (name_match.test(name) == false) {
        alert(gettext('地区代码格式错误!'))
        return
    }

    //取得地区描述
    var desc=$('#add_location_description').val()

    //描述正确的正则表达式
    var desc_match = /^[\u4e00-\u9fa5a-zA-Z0-9]{1,}$/;

    //开始检查
    if(desc.length==0){
        alert(gettext('地区名称不能为空!'))
        return
    }
    else if (desc_match.test(desc) == false) {
        alert(gettext('地区名称只能包含汉字、字母和数字!'))
        return
    }

    //添加到选项
    var locationiSelect = $("#select_location");
    var new_location_opt=new Option(desc,name)
    locationiSelect.append(new_location_opt);

    //toggle
    $('.add_new_location').toggle('slideUp')

    //select
    $(new_location_opt).prop('selected',true)
}

//失去焦点时检查站点唯一性
function checkStaionUnique(){
    //取得站点名
    var name=$('#add_site_name').val()

    //为空不用检查
    if (name.length==0){
        return
    }

    //发送请求
    $.post(url_prefix+'ajax/check_unique/',{"type":1,"name":name},function(data){
        //有错误，显示错误消息，站点已存在
        if (data['ret']=='1111') {
          $('#input-check-site-message').show();
          $('#add_site_name').val("")
          $('#add_site_name').focus().select();

        }
        //站点不存在
        else{
          $('#input-check-site-message').hide();
        }
    },'json')
}

//检查地区唯一性
function checkLocationUnique(){
    //取得地区名
    var name=$('#add_location_name').val()

    //为空不用检查
    if (name.length==0){
        return
    }

    //发送请求
    $.post(url_prefix+'ajax/check_unique/',{"type":2,"name":name},function(data){

        //地区已经存在
        if (data['ret']=='1111') {
          $('#input-check-location-message').show();
          $('#add_location_name').val("")
          $('#add_location_name').focus().select();

        }

        //地区不存在
        else{
          $('#input-check-location-message').hide();
        }
    },'json')
}

//检查上传数据类型，根据类型显示区域
function checkDataType(){

    //获取上传数据的类型，0：sp集团数据，1：中油数据，2：延长壳牌数据
    var type=$('#select_type option:selected').val()

    //sp集团显示
    if (type==0) {
        $('#upload-form').hide()
        $('#upload-form-sp').show()
        $('#upload-form-ycshell').hide()
    }

    //中油区域显示
    else if (type==1) {
        $('#upload-form').show()
        $('#upload-form-sp').hide()
        $('#upload-form-ycshell').hide()
    }

    //延长壳牌区域显示
    else if (type==2) {
       $('#upload-form').hide()
        $('#upload-form-sp').hide()
        $('#upload-form-ycshell').show()
    }

    //未选择类型，都隐藏
    else if (type==-1) {
        $('#upload-form').hide()
        $('#upload-form-sp').hide()
        $('#upload-form-ycshell').hide()
    }
}
