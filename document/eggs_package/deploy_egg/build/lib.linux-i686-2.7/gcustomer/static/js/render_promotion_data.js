//dom ready
$(function(){
	//init promotion manage page
    $("#activity_survey").empty()
    show_current_activity();

    //render complete activity
    if($('#completed_activity').length !=0){
        //dom ready
            $.get('/gcustomer/ajax/completed_activity/',{},function(data){
                if(data.ret !='0001'){
                    $("#alert_modal_body").html(gettext("当前活动为空"));
                    $("#alert_modal").modal("show");
                    return
                }
                $("#completed_activity").empty()
                for(var i=0;i<data.obj.length;i++){
                    $('#completed_activity').append(String.format('<a style="width:250px;float:left;padding-left:20px;margin-top:5px;"'+
                                                                                                  'draggable="true" ondragstart="drag(event)">'+
                                                                                                '<div class="item" >'+
                                                                                                    '<h4 onclick="get_activity_information()" name="/gcustomer/ajax/get_activity_data/" style="margin-top:30px;">{0}'+
                                                                                                    '</h4>'+
                                                                                                '</div>'+
                                                                                            '</a>',data.obj[i].name))
                }
            },'json');
    }
})

//drag
function allowDrop(ev)
{
    ev.preventDefault();
}

function drag(ev)
{
    ev.dataTransfer.setData("Text",$(ev.target).text());
    $("#the_recover_box").show();
}

function drop(ev)
{
    ev.preventDefault();
    var data=ev.dataTransfer.getData("Text");
    $("#alert_modal_body").html(gettext("成功将活动")+"'"+String(data)+"'"+gettext("放入回收箱!"));
    $("#alert_modal").modal("show");
    $("#the_recover_box").hide();
}
function hide_recover_box(){
    $("#the_recover_box").hide();
}
    
//calculate time
    function cal_day(sec){
        return Math.floor((Math.floor(sec/3600))/24)
    }
    function cal_hour(sec){
        return (Math.floor(sec/3600))%24
    }
    function cal_minute(sec){
        return Math.floor((sec%3600)/60)
    }

//显示当前活动列表
function show_current_activity(){
         if($('#current_activity_list').length !=0){
            $("#the_promotion_activity_list").show()
            $.get('/gcustomer/ajax/show_activity/',{},function(data){
                    if(data.ret !='0001'){
                            $("#alert_modal_body").html(gettext("当前活动为空"));
                            $("#alert_modal").modal("show");
                            return
                    }
                    $('#current_activity_list').empty()
                    for(var i=0;i<data.obj.length;i++){
                        $('#current_activity_list').append(String.format(''+
                            '<div class="col-lg-3">'+
                                '<div class="activity-item">'+
                                    '<span class="glyphicon glyphicon-remove" aria-hidden="true" style="cursor:pointer;margin-left:200px;" title="删除">'+
                                    '</span>'+
                                    '<a href="#" class="show_benefit"><h4>{0}</h4></a>'+
                                    '<p>开始时间: {1}</p>'+
                                    '<p>结束时间: {2}</p>'+
                                    '<p>活动已进行: {3}</p>'+
                                    '<p>参与人数:{4}人)</p>'+
                                    '<p>销售金额:{8}元")</p>'+
                                    '<h5>活动进度</h5>'+
                                    '<h5 class="activity_id" style="display:none;">{9}</h5>'+
                                    '<div class="progress">'+
                                        '<div class="progress-bar progress-bar-success" role="progressbar" aria-valuenow="90" aria-valuemin="90" aria-valuemax="100" style="min-width: 0em;width: {7}%">{6}%</div>'+
                                    '</div>'+
                                    '<h5>剩余时间</h5>'+
                                    '<p style="font-weight: bold;text-align: center;font-size: 18px;">{5}</p>'+
                                '</div>'+
                           ' </div>'+ '',
                            data.obj[i].name,
                            data.obj[i].start_time,
                            data.obj[i].end_time,
                            cal_day(data.obj[i].activity_duration)+gettext("天")+cal_hour(data.obj[i].activity_duration)+gettext("小时")+cal_minute(data.obj[i].activity_duration)+gettext("分钟"),
                            data.obj[i].participant_amount,
                            cal_day(data.obj[i].activity_remain)+gettext("天")+cal_hour(data.obj[i].activity_remain)+gettext("小时")+cal_minute(data.obj[i].activity_remain)+gettext("分钟"),
                            Math.floor(data.obj[i].activity_schedule*100),
                            Math.floor(data.obj[i].activity_schedule*100),
                            data.obj[i].total_fuel_purchase,
                            data.obj[i].id))
                        }
                    $(".glyphicon-remove").on("click",function(){
                            obj = $(this)
                            var activity_id = Number(obj.parent().find(".activity_id").html().trim())
                            $.get("/gcustomer/ajax/delete_promotion_activity/",{"activity_id":activity_id},
                                function(data){
                                    if(data.ret != "0001"){
                                        $("#alert_modal_body").html(data.info);
                                        $("#alert_modal").modal("show");
                                    }
                                    show_current_activity();
                                },"json");
                    });

                    $(".show_benefit").on("click",function(){
                        $("#the_promotion_activity_list").hide()
                        $("#the_benefit_tracking_dash").show()
                        //显示优惠活动的优惠详情
                        var promotion_id = $(this).parent().find(".activity_id").html().trim()
                        $.get("/gcustomer/ajax/promotion_good_list/",{'promotion_id':promotion_id},
                            function(data){
                                    if(data.ret != "0001"){
                                        $("#alert_modal_body").html("data.info");
                                        $("#alert_modal").modal("show");
                                    }
                                    $("#promotion_goods_list").empty()
                                    for (var i =0 ,len=data.promotion_goods.length ;i< len;i++){
                                            site_code = data.promotion_goods[i].site_code
                                            if(site_code == ""){}
                                                site_code = gettext("所有油站")
                                            $('#promotion_goods_list').append(String.format(''+
                                                '<tr>'+
                                                    '<td>{0}</td>'+
                                                    '<td>{1}</td>'+
                                                    '<td>{2}</td>'+
                                                    '<td>{3}</td>'+
                                                '</tr>'+
                                            '',data.promotion_goods[i].promotion_type,
                                                data.promotion_goods[i].name,
                                                data.promotion_goods[i].discount,
                                                data.promotion_goods[i].site_code))
                                    }
                            },"json");

                        $.get('/gcustomer/ajax/get_promotion_goods_lanch_info',{'promotion_id':promotion_id},
                            function(data){
                                if(data.ret != "0001"){
                                    alert()
                                    $("#alert_modal_body").html(data.info);
                                    $("#alert_modal").modal("show");
                                    return
                                }
                                $("#the_promotion_good_lanch_info").empty();
                                for(var i = 0,len = data.objs.length;i< len;i++){
                                        $("#the_promotion_good_lanch_info").append(String.format(''+
                                            '<tr>'+
                                                     '<td>{0}</td>'+
                                                     '<td>{1}</td>'+
                                                     '<td>{2}</td>'+
                                                     '<td>{3}</td>'+
                                              '</tr>'+
                                        '',data.objs[i].user_type,data.objs[i].user_id,data.objs[i].obj_type,data.objs[i].obj_id))
                                }

                            },"json");

                    });

                    $(".back_pre").on("click",function(){
                        $("#the_benefit_tracking_dash").hide()
                        $("#the_promotion_activity_list").show()
                    });
            },'json');

    }
}

// 添加商品优惠信息
function addPromotionInfo() {
    var row_index = $('#promotion_info_table tr').length+1;
    $('#promotion_info_table').append('<tr class="item"><th scope="row">'+row_index+'</th>\
                                       <td><select class="promotion_type" onchange="selectPromotionType(this)">\
                                       <option value="">请选择</option><option value="0">油品</option>\
                                       <option value="1">便利店商品</option>\
                                       <option value="2">车后服务</option>\
                                       </select></td>\
                                       <td><select class="promotion_station_map">\
                                       <option value="">请选择</option></select>\
                                       </td>\
                                       <td><select class="promotion_goods_map">\
                                       <option value="">请选择</option></select>\
                                       </td>\
                                       <td><input class="promotion_goods_discount" type="text"/></td>\
                                       <td><a style="cursor: pointer" onclick="deletePromotionInfo(this)">删除</a></td></tr>');
}

// 删除已经添加的商品优惠
function deletePromotionInfo(obj){
    $(obj).parents('.item').remove()
}


// 选择商品类型之后，设置关联的商品
function selectPromotionType(obj){

    // 获取用户选择的优惠类型
    var promotion_type = $(obj).val()
    var station_group_range = {}
    var auto_create_option = $("#auto_create_option").val()
    if($("#the_promotion_station_range").length != 0){
            if(promotion_type == '0'){
                if($("#activity_range_type :checked").val() == "0"){
                    station_group_range['type'] = promotion_type
                    station_group_range['province'] = Number($("#shengcode").val())
                    station_group_range['city'] = Number($("#shicode").val())
                    station_group_range['district'] = Number($("#xiancode").val())
                    if(!(auto_create_option == '1' || auto_create_option == '3')){
                        if(station_group_range['province'] == 0 &&  station_group_range['city'] == 0 && station_group_range['distinct'] == 0){
                            $("#alert_modal_body").html(gettext("请选择活动范围!"));
                            $("#alert_modal").modal("show");
                            return
                        } 
                    }
                }
                else{
                    station_group_range['type'] = promotion_type
                    station_group_range["group_id"] = Number($("#station_group_name").val())
                    if(!(auto_create_option == '1' || auto_create_option == '3')){
                        if(station_group_range == 0){
                            $("#alert_modal_body").html(gettext("请选择活动范围"));
                            $("#alert_modal").modal("show");
                            return
                        }
                    }
                }
            }
    }

    if(auto_create_option == '1' || auto_create_option == '3'){
        station_group_range = 0
    }
    if(promotion_type == ""){
        $("#alert_modal_body").html(gettext("请选择活动类型"));
        $("#alert_modal").modal("show");
        return
    }

    if(promotion_type == "0"){
            $(obj).parents('.item').find('.promotion_station_map').attr("disabled",false);
    }
    else{
        $(obj).parents('.item').find('.promotion_station_map').attr("disabled",true);
    }
    dict = {"promotion_type":promotion_type,"auto_create_option":auto_create_option,"station_group_range":JSON.stringify(station_group_range)}
    $.get("/gcustomer/ajax/get_promotion_goods_map/",dict,
        function(data){
            if(data.ret != '0001'){
                $("#alert_modal_body").html(data.info);
                $("#alert_modal").modal("show");
                return
            }
            if(data.hasOwnProperty("station_list") == true){
                if(data.station_list.length != 0){
                        var select_goods = $(obj).parents('.item').find('.promotion_station_map');
                        select_goods.empty();
                        select_goods.append("<option name='promotion_station_map' value=''>请选择</option>")
                        select_goods.append("<option name='promotion_station_map' value='0' style='display:none;'>所有油站</option>")
                        $(data.station_list).each(function(){
                                select_goods.append(String.format(''+
                                        '<option name="promotion_station_map" value="{0}">{1}</option>'+
                                            '',this["sha1"],this['name']))
                        });
                        $(select_goods).change(function(){
                                site_code = $(this).val()
                                if(site_code == ""){
                                    $("#alert_modal_body").html(gettext("请选择油站"));
                                    $("#alert_modal").modal("show");
                                    return
                                }
                                if(site_code == '0'){
                                        site_code = []
                                        var station_list = $(select_goods).find("option")
                                        for(var i = 2 ,len=station_list.length;i<len;i++){
                                            site_code.push($(station_list[i]).val())
                                        }
                                        site_code = JSON.stringify(site_code)
                                }
                                else{
                                    temp = site_code
                                    site_code = []
                                    site_code.push(temp)
                                    site_code = JSON.stringify(site_code)
                                }
                                $.get('/gcustomer/ajax/get_station_fuel/',{"site_code":site_code},
                                    function(data){
                                        if(data.ret != "0001"){
                                            $("#alert_modal_body").html(data.info);
                                            $("#alert_modal").modal("show");
                                        }
                                        var select_goods = $(obj).parents('.item').find('.promotion_goods_map');
                                        select_goods.empty();
                                        select_goods.append("<option name='promotion_goods_map' value=''>请选择关联商品</option>")
                                        $(data.good_list).each(function(){
                                            select_goods.append(String.format(''+
                                                    '<option name="promotion_goods_map" value="{0}">{1}</option>'
                                                ,this.barcode,this.name))
                                        })
                                },"json");
                        })
                }
                else{                           
                            $("#alert_modal_body").html(gettext("营销活动范围内没有油站!"));
                            $("#alert_modal").modal("show");
                    }
            }
            else{
                    var select_goods = $(obj).parents('.item').find('.promotion_goods_map');
                    select_goods.empty();
                    select_goods.append("<option name='promotion_goods_map' value=''>请选择关联商品</option>")
                    $(data.goods_list).each(function(){
                        select_goods.append(String.format(''+
                            '<option name="promotion_goods_map" value="{1}">{0}</option>'+
                            '',this.name,this.id))
                    });
            }

        },"json");
}

// 获取用户添加的所有优惠商品的信息
function getSelectedPromotionInfo(){
    // 取得当前添加所有商品的信息
    var goods_list = $('#promotion_info_table .item');
    var goods_info_list = [];

    for(var i=0;i<goods_list.length;i++){
        var obj = goods_list[i];
        var goods_info = {};
        //0:油品 1:便利店商品 2:车后服务
        var promotion_type = $(obj).find('.promotion_type option:selected').val();
        if(promotion_type == '0'){
                site_code = $(obj).find('.promotion_station_map').val()
                if(site_code == ""){
                    $("#alert_modal_body").html(gettext("请选择油站"));
                    $("#alert_modal").modal("show");
                    return
                }
                if(site_code == '0'){
                        site_code = []
                        var station_list = $(".promotion_station_map").find("option")
                        for(var i = 2 ,len=station_list.length;i<len;i++){
                            site_code.push($(station_list[i]).val())
                        }
                }
                else{
                    temp = site_code
                    site_code = []
                    site_code.push(temp)
                }
                goods_info['site_code'] = site_code
        }
        var promotion_goods_name = $(obj).find('.promotion_goods_map').val();
        var promotion_goods_discount = $(obj).find('.promotion_goods_discount').val();
        // 检查参数的合法性
        if(promotion_type != "" && promotion_goods_name != "" && promotion_goods_discount != ""){
            goods_info['type'] = promotion_type;
            goods_info['name'] = promotion_goods_name;
            goods_info['discount'] = promotion_goods_discount;
            goods_info_list.push(goods_info);
        }
    }

    // 返回取得的商品信息列表

    return goods_info_list;
}


function get_activity_information() {
    $("#the_finished_promotion_activity").hide()
    $("#the_promotion_simulation").show()
    url = $(window.event.srcElement)
    $.get('' + url.attr('name') + '', {'name': url.html()},
        function (data) {
            if (data.ret != '0001') {
                $("#alert_modal_body").html(gettext("没有该活动信息"));
                $("#alert_modal").modal("show");
                return
            }

            $("#the_promotion_simulation").show()
            $("#show_type_people").hide()
            dash_title = data.obj[0].name
            $("#activity_people_dimensions").val("")
            $("#activity_survey").empty()
            $("#activity_survey").append(String.format('<tr><td>活动名称</td><td>{0}</td></tr><tr><td>投入成本</td><td>{1}</td></tr><tr><td>参与人数</td><td>{2}</td></tr><tr><td>投入产出</td><td>{3}</td></tr><tr><td>持续时间</td><td>30天</td></tr>', data.obj[0].name, data.obj[0].cost, data.obj[0].nb_participates, data.obj[0].purchase))


            // 显示人群在不同时间点的分布
            $('#show_time_people').highcharts({
                chart: {
                    type: 'column'
                },
                title: {
                    text: gettext("活动参与人数分布图")
                },
                credits: {
                    enabled: false
                },
                subtitle: {
                    text: gettext('注：从活动开始到活动结束期间')
                },
                xAxis: {
                    categories: [

                    ]
                },
                yAxis: {
                    min: 0,
                    title: {
                        text: gettext('人数')
                    }
                },
                tooltip: {
                    headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                    pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                        '<td style="padding:0"><b>{point.y:.1f} 人</b></td></tr>',
                    footerFormat: '</table>',
                    shared: true,
                    useHTML: true
                },
                plotOptions: {
                    column: {
                        pointPadding: 0.2,
                        borderWidth: 0
                    }
                },
                series: [
                    {
                        name: dash_title,
                        data: [0.0, 1.0, 20.0, 50.0, 126.0, 300.0, 310.0, 510.0, 676.0, 535.0, 528.0, 525.0, 450.0, 410.0, 376.0, 335.0, 228.0, 226.0, 225.0, 210.0, 210.0, 176.0, 135.0, 128.0, 125.0, 116.4, 94.1, 95.6, 54.0, 50.0, 23.0, 10.0, 0.0, 0.0]

                    }
                ]
            });

            //活动效益横坐标
            nb_days = data.obj[0].activity_duration
            dash_categories = []
            activity_data = []
            activity_data[0] = Math.floor(Math.random() * 10)
            for (var i = 0; i < nb_days; i++) {
                dash_categories[i] = String.format(gettext('第%d{0}天'), i + 1)
                if (i > 0) {
                    activity_data[i] = i * 0.5 + activity_data[i - 1]
                }
            }

            // 活动效益
            if ($("#show_activity_result").length != 0) {
                $('#show_activity_result').highcharts({
                    title: {
                        text: gettext('营销活动效益累计跟踪图'),
                        x: -20 //center
                    },
                    credits: {
                        enabled: false
                    },
                    xAxis: {
                        categories: dash_categories
                    },
                    yAxis: {
                        title: {
                            text: gettext('效益(元)'),
                        },
                        plotLines: [
                            {
                                value: 0,
                                width: 1,
                                color: '#808080'
                            }
                        ]
                    },
                    tooltip: {
                        valueSuffix: gettext('元')
                    },
                    legend: {
                        layout: 'vertical',
                        align: 'center',
                        verticalAlign: 'bottom',
                        borderWidth: 0
                    },
                    series: [
                        {
                            name: dash_title,
                            data: activity_data
                        }
                    ]
                });

            }

        }, "json");
};

/* 新建营销活动页面 */
$(function(){
    // 初始化datepicker插件
    $('.datepicker').datepicker({});

    $("#the_create_promotion").hide()

    $("#the_choose_auto_type").hide()

    $("#area_select_option").show()

    //清空商品优惠
    $("#area_select_option").change(function(){
        $(".promotion_type").val("")
        $(".promotion_station_map").val("")
        $(".promotion_goods_map").val("")
    });
    $("#station_group_name").change(function(){
        $(".promotion_type").val("")
        $(".promotion_station_map").val("")
        $(".promotion_goods_map").val("")
    });

    //渲染油站群组
    $.get("/gcustomer/ajax/get_station_group_list/",{},
        function(data){
            if(data.ret != '0001'){
                $("#alert_modal_body").html(gettext("获取油站群错误"));
                $("#alert_modal").modal("show");
                return
            }
            $("#station_group_name").append('<option value="">请选择油站群组</option>');
            for(var i = 0 , len = data.objs.length;i<len;i++){
                $("#station_group_name").append(String.format('<option value="{0}">{1}</option>',
                    data.objs[i].id,data.objs[i].group_name));
            }

        },"json");
    //渲染油站群组
    $.get("/gcustomer/ajax/get_station_group_list/",{},
        function(data){
            if(data.ret != '0001'){
                $("#alert_modal_body").html(gettext("获取油站群错误"));
                $("#alert_modal").modal("show");
                return
            }
            $("#choose_station_group_name").append('<option value="">请选择油站群组</option>');
            for(var i = 0 , len = data.objs.length;i<len;i++){
                $("#choose_station_group_name").append(String.format('<option value="{0}">{1}</option>',
                    data.objs[i].id,data.objs[i].group_name));
            }

        },"json");


    $('.radio[name="activity_range"]').change(function(){
            if($("#area_select_option").css("display") == "block" ){
                $("#area_select_option").hide()
                $("#station_group_select_option").show()
                $(".promotion_type").val("")
                $(".promotion_station_map").val("")
                $(".promotion_goods_map").val("")
            }
            else {
                $("#area_select_option").show()
                $("#station_group_select_option").hide()
                $(".promotion_type").val("")
                $(".promotion_station_map").val("")
                $(".promotion_goods_map").val("")
            }
    });

    for (var i=0;i<24;i++){
        $("select[name='start']").append(String.format("<option name='start_time' value={0}>{1}</option>",i,String(i)+gettext("点")))
    }

    $("select[name='start']").change(function(){
        start_time = $("select[name='start']").val()
        $("select[name='end']").empty()
        $("select[name='end']").append("<option name='end' value=''>选择结束时间</option>")
        for(var i=Number(start_time)+1;i<=23;i++){
        $("select[name='end']").append(String.format("<option name='end' value={0}>{1}</option>",i,String(i)+gettext("点")))
        }
    })

    //发布活动
    $("#launch_promotion_activity").on("click",function(){
        create_type = $("#choose_create_promotion_type").val()
        auto_create_option = 0
        if(create_type == "1"){
            auto_create_option = $("#auto_create_option").val()
        }
        name = $("#activity_name").val()
        if(name == ""){
            $("#alert_modal_body").html(gettext("请输入活动名称!"));
            $("#alert_modal").modal("show");
            return ;
        }
        start_time = $("#start_time").val()
        if(start_time == ""){
            $("#alert_modal_body").html(gettext("请输入活动起始时间"));
            $("#alert_modal").modal("show");
            return ;
        }
        end_time = $("#end_time").val()
        if(end_time == ""){
            $("#alert_modal_body").html(gettext("请输入活动结束时间"));
            $("#alert_modal").modal("show");
            return ;
        }
        area_type = $(".radio[name='activity_range'] :checked").val()
        area =  {}
        station_group_id = ""
        if(area_type == "0"){
            area['province'] = Number($("#shengcode").val())
            area['city'] = Number($("#shicode").val())
            area['district'] = Number($("#xiancode").val())
            if(area['province'] == 0 &&  area['city'] == 0 && area['distinct'] == 0){
                    if(auto_create_option != "3"){
                        $("#alert_modal_body").html(gettext("请选择活动范围"));
                        $("#alert_modal").modal("show");
                        return
                    }

            }
        }
        else{
            area  = {}
            station_group_id = $("#station_group_name").val()
            if(station_group_id== "" && $("#the_auto_create_promotion_choose_hide").is(":hidden")==false){
                if(auto_create_option != "3"){
                        $("#alert_modal_body").html(gettext("请选择活动范围"));
                        $("#alert_modal").modal("show");
                        return
                }
            }
        }
        launch_type = $(".radio[name='launch_type'] :checked").val();
        launch_type = 0
        target_audience = $("#target_audience").val();
        if(target_audience == "" && $("#the_auto_create_promotion_choose_hide").is(":hidden")==false){
            $("#alert_modal_body").html(gettext("请选择目标用户群"));
            $("#alert_modal").modal("show");
            return
        }30
        contact_type = $("#communication_type").val();
        if(contact_type == ""){
            $("#alert_modal_body").html(gettext("请选择沟通类型"));
            $("#alert_modal").modal("show");
            return
        }
        description = $("#description_info").val();

        if(description == ""){
            $("#alert_modal_body").html(gettext("描述信息不能为空"));
            $("#alert_modal").modal("show");
            return
        }
        var promotion_goods = getSelectedPromotionInfo();
        if (promotion_goods.length == 0){
            if(auto_create_option != "6" && auto_create_option != "7" && auto_create_option != "3"){
                $("#alert_modal_body").html(gettext("请添加优惠商品"));
                $("#alert_modal").modal("show");
                 return
            }

        }

        dict = {
            'create_type' : create_type,
            'auto_create_option' : auto_create_option,
            'activity_name' : name,
            'start_time' : start_time,
            'end_time' : end_time,
            'activity_range' : area_type,
            'area' : JSON.stringify(area),
            //油站群
            'station_group_id':Number(station_group_id),
            'launch_type' : launch_type,
            //用户群
            'target_audience' : String(target_audience),
            'communication_type' : contact_type,
            'description' : description,
            'promotion_goods' : JSON.stringify(promotion_goods),
	'group_id':$("#choose_station_group_name").val()
        }
        //缓冲提示
        $.blockUI({"message":gettext("正在处理...")});
        $.post("/gcustomer/ajax/create_promotion_activity/",dict,
            function(data){
                if(data.ret != '0001'){
                    $.blockUI({"message":data.info});
                    $.unblockUI();
                    $("#alert_modal_body").html(data.info);
                    $("#alert_modal").modal("show");
                    return
                }
                $.blockUI({"message":gettext("创建成功")});
                $.unblockUI();
                $("#alert_modal_body").html(gettext("创建成功"));
                $("#alert_modal").modal("show");

                $("#choose_create_promotion_type").val("")
                $("#auto_create_option").val("")
                $("#activity_name").val("")
                $("#start_time").val("")
                $("#end_time").val("")
                $("#promotion_type").val("")

                $("#activity_range_type").val("")
                $(".radio[name='activity_range']").val("")
                $("#shengcode").val("")
                $("#shicode").val("")
                $("#station_group_name").val("")
                $("#target_audience").val("")

                $(".radio[name='launch_type']").val("")
                $("input[type='checkbox']").val("")
                $("#communication_type").val("")
                $("#discount_information").val("")
                $("#description_info").val("")
                $("select[name='start']").val("")
                $("select[name='end']").val("")

                $("#promotion_type").val("")
                $("#promotion_goods_map").val("")
                $("#promotion_goods_map").hide()

                $("#add_promotion_goods_map").empty()


                $("#the_create_promotion").hide()
                $("#the_choose_auto_type").hide()
                $("#area_select_option").show()
                $("#station_group_select_option").hide()
                $($("input[name='activity_range']")[1]).attr("checked",false)
                $($("input[name='activity_range']")[0]).attr("checked",true)




            },"json")
    });

    $("#big_image_body").find("select").change(function(){
            if($("#big_image_body").find("select").val() == "1"){
                    $("#the_email_setting_information").show()
                    $("#the_short_message_setting_information").hide()
                      $("#the_contact_setting_ok").show()
            }
            else if ($("#big_image_body").find("select").val() == "2"){
                    $("#the_email_setting_information").hide()
                    $("#the_short_message_setting_information").show()
                      $("#the_contact_setting_ok").show()
            }
    });

    $("#the_contact_setting_ok").on("click",function(){
                $("#Contact_Setting").modal("hide")
                $("#Mail_preview").modal("show")
    });

    $("#launch_ok").on('click',function(){
            $("#Mail_preview").modal("hide")
            $("#alert_modal_body").html("ok");
            $("#alert_modal").modal("show");
    });

    $("#forecast_promotion_activity").on('click',function(){
            $("#ConvertRateModal").modal("show")
    });

    $("#cal_forcase_sale_value").on('click',function(){
            $("#the_sale_forcase").show()
            sale_rate = $("#sale_rate").val()
            $("#pump_amount").html(String(Number(sale_rate)*343)+gettext("升"))
            $("#total_sale_value").html(String(Number(sale_rate)*34230)+gettext("万元"))
            $("#nonfuel_sale_value").html(String(Number(sale_rate)*1423)+gettext("万元"))
            $("#efficiency_value").html(gettext("暂无"))
    });

    $("#choose_create_promotion_type").change(function(){
        $('#promotion_info_table').empty()
        if($(this).val() == ""){
                $("#the_create_promotion").hide()
                $("#the_choose_auto_type").hide()
                $("#alert_modal_body").html(gettext("请选择活动创建方式"));
                $("#alert_modal").modal("show");
            }
            else if ($(this).val() == "0"){
                $("#the_create_promotion").show()
                $("#the_auto_create_promotion_choose_hide").show()
                $("#the_choose_auto_type").hide()
                $("#the_promotion_station_range").show()
                $("#the_promotion_good_list").show()
            }
            else if ($(this).val() == "1"){
                $("#the_choose_auto_type").show()
                $("#the_create_promotion").hide()
                $("#the_auto_create_promotion_choose_hide").hide()
            }
    });
    $("#auto_create_option").change(function(){
        if($("#auto_create_option").val() == '1'){
            $("#the_create_promotion").show()
            $("#the_promotion_station_range").hide()
            $("#the_promotion_good_list").show()
        }
        else if($("#auto_create_option").val() == '3'){
            $("#the_create_promotion").show()
            $("#the_promotion_station_range").hide()
            $("#the_promotion_good_list").show()
        }
        else if($("#auto_create_option").val() == '6' || $("#auto_create_option").val() == '7'){
            $("#the_create_promotion").show()
            $("#the_promotion_station_range").hide()
            $("#the_promotion_good_list").hide()
        }
        else {
            $("#the_create_promotion").hide()
            $("#the_promotion_station_range").hide()
            $("#the_promotion_good_list").hide()
        }
    });

    if ($("#shengcode").length != 0){
                init_china_location();
    }
});

var message=$("#message").text()
if(message){
    $("#alert_modal_body").html(message);
    $("#alert_modal").modal("show");
}

function init_china_location(){

        var url_prefix = "gflux/";/*$('meta[name="url_prefix"]').attr('content');*/
        ////取得省份的信息
        $.post('/'+url_prefix+'ajax/get_china_location/',{'parent':0,'level':1},function(data){
            //判断返回值是否正确
             if (data.ret!='1101'){
                 $("#alert_modal_body").html(data.info);
                 $("#alert_modal").modal("show");
                 return
             }
             var all_ps=data['dict_city']

             //循环遍历出城市的id和name,并填充到页面中
             for(var i=0;i<all_ps.length;i++){
                 var $html=String.format('<option value="{0}">{1}</option>',all_ps[i][0],all_ps[i][1])
                 $('#shengcode').append($html)
             }
        },"json")

        //监听选择市/县的事件

        $('#shengcode').change(function(){
            if($("#shengcode").val() == ""){
                $("#alert_modal_body").html(gettext("请输入省份"));
                $("#alert_modal").modal("show");
                return
            }
            //取出url地址
            var url_prefix = "gflux/";/*$('meta[name="url_prefix"]').attr('content');*/
            var parent = $('#shengcode').val()

            //通过ajax请求取得城市的信息
            $.post('/'+url_prefix+'ajax/get_china_location/',
               {"parent":parent,"level":2},
                function(data){

                    //判断返回值是否正确
                    if (data.ret!='1101'){
                        $("#alert_modal_body").html(data.info);
					    $("#alert_modal").modal("show");
                        return
                    }
                    var all_ps=data['dict_city']
                    var $shicode = $('#shicode').empty();
                    $shicode.append('<option selected value="">请选择市</option>')
                    var $xiancode = $('#xiancode').empty();
                    $xiancode.append('<option selected value="">请选择区/县</option>')

                    //循环遍历出城市的id和name,并填充到页面中
                    for(var i=0;i<all_ps.length;i++){
                        var $html=String.format('<option value="{0}">{1}</option>',all_ps[i][0],all_ps[i][1])
                        $('#shicode').append($html)
                    }
                },
            "json");
        });

        $("#shicode").change(function(){
            if($("#shicode").val() == ""){
                $("#alert_modal_body").html(gettext("请输入市级信息"));
                $("#alert_modal").modal("show");
                return
            }
            //取出url地址
            var url_prefix = "gflux/" /*$('meta[name="url_prefix"]').attr('content');*/
            var parent = $('#shicode').val()

            //通过ajax请求取得区县的信息
            $.post('/'+url_prefix+'ajax/get_china_location/',
               {"parent":parent,"level":3},
                function(data) {

                    //判断返回值是否正确
                    if (data.ret!='1101'){
                        $("#alert_modal_body").html(data.info);
					    $("#alert_modal").modal("show");
                        return
                    }
                    var all_ps = data['dict_city']
                    var $xiancode = $('#xiancode').empty();
                    $xiancode.append('<option selected value="">请选择区/县</option>')

                    //循环遍历出城市的id和name,并填充到页面中
                    for (var i = 0; i < all_ps.length; i++) {
                         var $html = String.format('<option value="{0}">{1}</option>', all_ps[i][0], all_ps[i][1])
                         $('#xiancode').append($html)
                    }
                },
            "json");
        });
};

/*  营销活动结束 */
$(function(){

    $("#the_finished_promotion_activity").show()
    $("#the_promotion_simulation").hide()
    $(".back_pre").on("click",function(){
        $("#the_finished_promotion_activity").show()
        $("#the_promotion_simulation").hide()
        $('#activity_survey').empty()
        $('#show_time_people').empty()
        $('#show_activity_result').empty()
        $('#show_type_people').empty()
    })
    $("#activity_people_dimensions").change(function(){
        if($("#show_type_people").length != 0){
            $("#show_type_people").show()
        }
        if($(this).val() == ""){
            $("#show_type_people").hide()
            $("#alert_modal_body").html(gettext("请选择维度"));
            $("#alert_modal").modal("show");
        }
        else {
            renderActivityPeopleDimensionsDash($(this).val())
            $("body").scrollTop(10000)
        }
});
//根据不同维度显示不同表
function renderActivityPeopleDimensionsDash(dimension){
    if(dimension){
        switch(dimension){
            case "0" :
                data = [
                            [gettext('20岁以下'), 5.8],
                            [gettext('20-40岁'), 54.0],
                            [gettext('40-60岁'), 28.2],
                            [gettext('60岁以上'), 12.0],
                        ]
                activityVisitedMapDash(data)
                break;
            case "1" :
                data = [
                            [gettext('男'),   35.8],
                            [gettext('女'),   64.2],
                        ]
                activityVisitedMapDash(data)
                break;
            case "2" :
                data = [
                            [gettext('学生'),   5.8],
                            [gettext('司机'),   54.0],
                            [gettext('老师'),     28.2],
                            [gettext('其他'),       12.0]
                        ]
                activityVisitedMapDash(data)
                break;
            case "3" :
                data = [
                            [gettext('5次以下'),   5.8],
                            [gettext('5-10次'),   54.0],
                            [gettext('10-15次'),     28.2],
                            [gettext('15次以上'),       12.0]
                        ]
                activityVisitedMapDash(data)
                break;
            default :
                $("#alert_modal_body").html(gettext("该维度信息暂无"));
                $("#alert_modal").modal("show");
        }
    }
};
});

function activityVisitedMapDash(data){
    if($("#show_type_people").length !=0){
        $('#show_type_people').highcharts({
                                chart: {
                                    plotBackgroundColor: null,
                                    plotBorderWidth: null,
                                    plotShadow: false
                                },
                                credits: {
                                     enabled: false
                                },
                                title: {
                                    text: gettext('参与广告人群类型分布图')
                                },
                                tooltip: {
                                    pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
                                },
                                plotOptions: {
                                    pie: {
                                        allowPointSelect: true,
                                        cursor: 'pointer',
                                        dataLabels: {
                                            enabled: true,
                                            color: '#000000',
                                            connectorColor: '#000000',
                                            format: '<b>{point.name}</b>: {point.percentage:.1f} %'
                                        }
                                    }
                                },
                                series: [{
                                    type: 'pie',
                                    name: gettext('比例'),
                                    data: data
                                }]
                            });
    }
};

//活动效益跟踪图
$(function () {
         activity_efficiency_tracking_dash =  function activity_efficiency_tracking_dash(title){
                Highcharts.setOptions({
                    global: {
                        useUTC: false
                    }
                });

                var chart;
                $('#activity_efficiency_tracking_dash').highcharts({
                    chart: {
                        type: 'spline',
                        animation: Highcharts.svg, // don't animate in old IE
                        marginRight: 10,
                        events: {
                            load: function() {

                                // set up the updating of the chart each second
                                var series = this.series[0];
                                z  = Math.log10(25)/10.1
                                setInterval(function() {
                                    var x = (new Date()).getTime();
                                    var y = z + Math.random()/100.1;
                                    z =  y ;
                                    series.addPoint([x,y], true, true);
                                }, 1000);
                            }
                        }
                    },
                    title: {
                        text: '"'+title+'"'+gettext('营销活动效益累计跟踪图')
                    },
                    credits: {
                                enabled: false
                            },
                    xAxis: {
                        type: 'datetime',
                        tickPixelInterval: 100
                    },
                    yAxis: {
                        title: {
                            text: gettext('效益/万元')
                        },
                        plotLines: [{
                            value: 0,
                            width: 1,
                            color: '#808080'
                        }]
                    },
                    tooltip: {
                        formatter: function() {
                                return '<b>'+ this.series.name +'</b><br/>'+
                                Highcharts.dateFormat('%Y-%m-%d %H:%M:%S', this.x) +'<br/>'+
                                Highcharts.numberFormat(this.y, 2)+
                                gettext('万元');
                        }
                    },
                    legend: {
                        enabled: false
                    },
                    exporting: {
                        enabled: false
                    },
                    series: [{
                        name: '"'+title+'"'+gettext('营销活动'),
                        data: (function() {
                            // generate an array of random data
                            var data = [],
                            time = (new Date()).getTime(),
                            i;
                            var  j = 5
                            for (i = -19; i <= 0; i++) {
                                data.push({
                                    x: time + i * 1000,
                                    y: Math.log10(j)/10.1
                                });
                                j++
                            }
                            return data;
                        })()
                    }]
                });
          }
});
