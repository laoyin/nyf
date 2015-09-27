//dom ready，初始化
$(function(){
    //初始化页面显示
    initPage()

    //初始化标签
    initTags()
})

//初始化页面
function initPage(){
    //隐藏返回按钮和第二屏页面
    $('#second_area').hide()
    $('#back_btn').hide()
}

//初始化用户标签显示
function initTags(){
    $('#tags_area').empty()
    $.post(url_prefix+'ajax/get_user_tags/',function(data){
        if(data['ret']!='1101'){
            errorModal(gettext('获取标签错误！'))
        }else{
            tags = data['tags']
            for(var i=0;i<tags.length;i++){
                tag = tags[i]
                var tmp=String.format('<button type="button" onclick=enterSecondPage({0},"{1}") \
                    class="btn btn-primary" style="margin-left:10px;margin-top:10px;font-size:16px"\
                    id={0}>{1}<span class="glyphicon glyphicon-chevron-right" style="margin-left:10px;"></span></button>',tag['id'],tag['name'])
                $('#tags_area').append(tmp)
            }
        }
    },'json')
}

//新建标签对话框
function newTagDialog(){
    //显示模态框
    $('#myModalLabel').text(gettext('新建标签'))
    $('#name').text(gettext('标签名字'))
    //清空文本框
    $('#add_name').val("")
    $('#myModal').modal('show');
}

//新建标签
function addTag(){

    //名字
    var name=$('#add_name').val()
    //判断名字
    if(name==''){
        errorModal(gettext('名字不能为空！'))
        return
    }
    $.post(url_prefix+'ajax/add_tag/',{'tag_name':name},function(data){
        if(data['ret']=='0006'){
            errorModal(gettext('该标签已存在！'))
            return
        }else if(data['ret']!='1101'){
            errorModal(gettext('创建失败！'))
        }
        initTags()
        //关闭对话框
        $('#myModal').modal('toggle')

    },'json')
}

//进入第二屏显示
function enterSecondPage(tag_id,tag_name){
    $('#first_area').hide()
    $('#second_area').show()
    $('#back_btn').show()
    $('#tag_name').text(tag_name)
    $('#tag_name').val(tag_id)
    $('#select_site').empty()
    $('#sites_area').empty()
    $('#select_site').append("<option value='-1'>请选择油站</option>")
    $.post(url_prefix+'ajax/get_user_tag_sites/',{'tag_id':tag_id},function(data){
        if(data['ret']!='1101'){
            errorModal(gettext('获取关联油站失败！'))
            return
        }
        has_sites = data['has_sites']
        tags = data['tags']

        all_stations = window.all_stations

        //显示可选油站
        for(var i=0;i<all_stations.length;i++){
            var site = all_stations[i]['name']
            var site_desc = all_stations[i]['description']
            if(has_sites.indexOf(site)!=-1){
                continue
            }else{
                $('#select_site').append(String.format('<option value="{0}">{1}</option>',site,site_desc))
            }

        }

        //显示已关联油站
        for(var j=0;j<tags.length;j++){
            var tag = tags[j]
            var tmp=String.format('<button type="button" value="{0}" onclick="removeSiteForTag(this)"\
                class="btn btn-primary" style="margin-left:10px;margin-top:10px;font-size:16px"\
                >{1}<span class="glyphicon glyphicon-remove" style="margin-left:10px;"></span></button>',tag['site'],tag['site_desc'])
            $('#sites_area').append(tmp)
        }

    },'json')
}

//返回选择站点页面
function backFirstPage(){
    //隐藏第二屏,显示第一屏
    $('#second_area').hide()
    $('#first_area').show()
    $('#back_btn').hide()
}

//删除标签
function removeTag(obj){
    tag_id = $('#tag_name').val()
    $.post(url_prefix+'ajax/remove_tag/',{'tag_id':tag_id},function(data){
        if(data['ret']!='1101'){
            errorModal(gettext('删除失败！'))
        }else{
            $('#'+tag_id).remove()
            backFirstPage()
        }
    },'json')
}

//绑定标签油站
function bandSite(){

    //所选站点
    var site=$("#select_site option:selected").val();

    //站点描述信息
    var site_desc = $("#select_site option:selected").text();

    //标签的id
    tag_id = $('#tag_name').val()

    if(site == '-1'){
        errorModal(gettext('请选择要添加的油站！'))
        return
    }

    $.post(url_prefix+'ajax/bind_site_for_tag/',{'tag_id':tag_id,'site':site,'site_desc':site_desc},function(data){
        if(data['ret']!='1101'){
            errorModal(gettext('添加失败！'))
        }else{
            $(String.format('#select_site option[value="{0}"]',site)).remove();
            var tmp=String.format('<button type="button" value="{0}" onclick="removeSiteForTag(this)"\
                class="btn btn-primary" style="margin-left:10px;margin-top:10px;font-size:16px"\
                >{1}<span class="glyphicon glyphicon-remove" style="margin-left:10px;"></span></button>',site,site_desc)
            $('#sites_area').append(tmp)
        }
    },'json')
}

//某标签取消关联油站
function removeSiteForTag(obj){

    //站点名字
    var site = $(obj).val()

    //站点描述
    var site_desc = $(obj).text()

    //标签的id
    tag_id = $('#tag_name').val()

    $.post(url_prefix+'ajax/remove_site_for_tag/',{'tag_id':tag_id,'site':site},function(data){
        if(data['ret']!='1101'){
            errorModal(gettext('删除失败！'))
            return
        }
        $(String.format('#sites_area button[value="{0}"]',site)).remove()
        $('#select_site').append(String.format('<option value="{0}">{1}</option>',site,site_desc))
    },'json')
}
