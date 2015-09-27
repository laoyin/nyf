//const var
var user_source_map = {1: gettext("中石油"), 2: gettext("中石化"), 3: gettext("中海油"), 4: gettext("壳牌"), 5: gettext("中化")}
var best_promotion_mode_map = {0: gettext("改善运营效率"), 1: gettext("油品优惠"), 2: gettext("非油品优惠"), 3: gettext("定额优惠"), 4: gettext("忠诚客户优惠")}
var perfer_fuel_cost_option = {0: gettext("消费金额倾向"), 1: gettext("加油时间倾向"), 2: gettext("加满率"), 3: gettext("单次加油额"), 4: gettext("非油品消费类型"), 5: gettext("加油间隔"),6:gettext("最喜爱的非油品"),7:gettext("推荐购买的非油品")}
var prefer_time_map = {0: gettext("无规律"), 1: gettext("早上"), 2: gettext("中午"), 3: gettext("晚上"), 4: gettext("午夜")}
var prefer_pump_type_map = {0: "无规律", 1: "加满", 2: "定额"}
var prefer_cost_map = {0: gettext("无规律"), 1: gettext("加很多"), 2: gettext("加很少"), 3: gettext("一般")}
var prefer_fuel_cost_map = {0: gettext("无规律"), 1: gettext("加很多"), 2: gettext("加很少"), 3: gettext("一般")}
var prefer_nonfuel_cost_map = {0: gettext("无规律"), 1: gettext("买很多"), 2: gettext("买很少"), 3: gettext("一般")}
var efficiency_map = {0: gettext("无影响"), 1: gettext("一般"), 2: gettext("严重")}
var pump_timeout = {0: gettext("间隔几天"), 1: gettext("每天"), 2: gettext("间隔一个月以上")}
var already_inited_grouped = false
var already_inited_user_profile = false


/* 大客户管理  */
$(function () {
    $('#profile_feature_table').empty()
    $('#customer_habits').empty()
    $('#communication_record').empty()
    $('#profile_feature_grouped').empty()
    $('#information_recommand').empty()
    $('#contribution_rank').empty()
    $('#similar_group_distribution').empty()


    //获得消费预测
    $('#get_user_profile_forecase').on('click', function () {
        //get user card num
        var user_card_num = $('#search_user_profile_forecase input').val().trim()

        if (user_card_num.length == 0) {
            $("#alert_modal_body").html(gettext("请输入用户卡号，不能为空！"));
            $("#alert_modal").modal("show");
            $('#profile_feature_table').empty()
            $('#information_recommand').empty()
            $('#profile_feature_grouped').empty()
            return
        }

        if (isNaN(parseInt(user_card_num))) {
            $("#alert_modal_body").html(gettext("请输入正确的用户卡号，必须全是数字"));
            $("#alert_modal").modal("show");
            $('#profile_feature_table').empty()
            $('#information_recommand').empty()
            $('#profile_feature_grouped').empty()
            return
        }

        $("#the_consume_forecase_list").show()
        /*$("#the_information_push_record").show()*/

        $('#profile_feature_table').html('<tr><th colspan="4" style="text-align: center">正在加载数据...</th></tr>');
        $('#profile_feature_grouped').html('<tr><th colspan="4" style="text-align: center">正在加载数据...</th></tr>');
        $('#information_recommand').html('<tr><th colspan="4" style="text-align: center">正在加载数据...</th></tr>');
        $('#contribution_rank').html('<tr><th colspan="4" style="text-align: center">正在加载数据...</th></tr>');
        $.get('/gcustomer/ajax/get_user_profile',
            {user_source: 1, profiling_area: 'CCPQ', cardnum: user_card_num},
            function (data) {
                if (data.ret != '0001') {
                    $("#alert_modal_body").html(data.info);
					$("#alert_modal").modal("show");
                    $('#profile_feature_table').empty()
                    $('#information_recommand').empty()
                    $('#profile_feature_grouped').empty()
                    return
                }

                //clear container
                $('#profile_feature_table').empty()

                //render user feature

                // $('#profile_feature_table').append(String.format('<tr><td>油站所属集团公司</td><td>{0}</td></tr>',
                //     user_source_map[data.user_source]))
                // $('#profile_feature_table').append(String.format('<tr><td>属于站点</td><td>{0}</td></tr>',
                //     data.profiling_area))
                $('#profile_feature_table').append(String.format('<tr><td>{% trans "加油时间倾向" %}</td><td>{0}</td></tr>',
                    prefer_time_map[data.prefer_time]))
                $('#profile_feature_table').append(String.format('<tr><td>加油方式倾向</td><td>{0}</td></tr>',
                    prefer_pump_type_map[data.prefer_pump_type]))
                $('#profile_feature_table').append(String.format('<tr><td>单次油品消费倾向</td><td>{0}</td></tr>',
                    prefer_fuel_cost_map[data.prefer_fuel_cost]))
                $('#profile_feature_table').append(String.format('<tr><td>单次非油品消费倾向</td><td>{0}</td></tr>',
                    prefer_nonfuel_cost_map[data.prefer_nonfuel_cost]))
                $('#profile_feature_table').append(String.format('<tr><td>消费额度偏好</td><td>{0}</td></tr>',
                    '暂无'))
                $('#profile_feature_table').append(String.format('<tr><td>促销接受偏好</td><td>{0}</td></tr>',
                    '暂无'))
                $('#profile_feature_table').append(String.format('<tr><td>加油间隔</td><td>{0}</td></tr>',
                    data.avg_charge_period))
                $('#profile_feature_table').append(String.format('<tr><td>对网络负载的影响</td><td>{0}</td></tr>',
                    efficiency_map[data.efficiency]))
                $('#profile_feature_table').append(String.format('<tr><td>系统综合打分</td><td>{0}</td></tr>',
                    data.prominence))
                $('#profile_feature_table').append(String.format('<tr><td>最佳营销模式</td><td>{0}</td></tr>',
                    best_promotion_mode_map[data.best_promotion_mode]))


                //render gruoped info
                for (var idx = 0; idx < data.grouped.length; idx++) {
                    $('#profile_feature_grouped').append(String.format('<li grouped_id="{1}">人群 {0}</li>',
                        data.grouped[idx], data.grouped[idx]))
                }

                //render items
                var user_like_items = data.favourite_nonfuel_products.slice(0, 10)
                $('#profile_feature_table').append(String.format('<tr><td>喜爱的非油品</td><td>{0}</td></tr>',
                    user_like_items.join(';')))
                var recommend_user_items = data.recommended_nonfuel_products
                $('#profile_feature_table').append(String.format('<tr><td>推荐购买的非油品</td><td>{0}</td></tr>',
                    recommend_user_items.join(';')))


                //render information_recommand
                data['information_recommand'] = []
                if (data['information_recommand'].length == 0) {
                    $('#information_recommand').html('<tr><th colspan="4" style="text-align: center">暂无数据</th></tr>')
                }
                //render profile feature grouped
                data['profile_feature_grouped'] = []
                if (data['profile_feature_grouped'].length == 0) {
                    $('#profile_feature_grouped').html('<tr><th colspan="4" style="text-align: center">暂无数据</th></tr>')
                }

            }, 'json')
    });

    //获得消费习惯
    $('#get_user_profile_habits').on('click', function () {
        //get user card num

        var user_card_num = $('#search_user_profile_habits input').val().trim()

        if (user_card_num.length == 0) {
            $("#alert_modal_body").html(gettext("请输入用户卡号，不能为空！"));
            $("#alert_modal").modal("show");
            return
        }

        if (isNaN(parseInt(user_card_num))) {
            $("#alert_modal_body").html(gettext("请输入正确的用户卡号，必须全是数字"));
            $("#alert_modal").modal("show");
            $('#customer_habits').empty()
            $('#similar_group_distribution').empty()
            $('#people_group_table').empty()
            return
        }
        $("#the_customer_consume_habit_record").show()
        $('#customer_habits').html('<tr><th colspan="4" style="text-align: center">'+gettext("正在加载数据...")+'</th></tr>');
        $('#people_group_table').html('<tr><th colspan="4" style="text-align: center">'+gettext("正在加载数据...")+'</th></tr>');
        $.get('/gcustomer/ajax/get_user_profile',
            {user_source: 1,  cardnum: user_card_num},
            function (data) {
                if (data.ret != '0001') {
                    alert(data.info)
                    $('#customer_habits').empty()
                    $('#similar_group_distribution').empty()
                    $('#people_group_table').empty()
                    return
                }

                //clear container
                $('#customer_habits').empty()
                $('#similar_group_distribution').empty()
                $('#people_group_table').empty()

                //render user feature
                $('#customer_habits').append(String.format('<tr><td>1</td><td>'+gettext("加油地点范围")+'</td><td>{0}</td></tr>',
                    data.profiling_area))
                $('#customer_habits').append(String.format('<tr><td>2</td><td>'+gettext("加油时间倾向")+'</td><td>{0}</td></tr>',
                    prefer_time_map[data.prefer_time]))
                $('#customer_habits').append(String.format('<tr><td>3</td><td>'+gettext("加油方式倾向")+'</td><td>{0}</td></tr>',
                    prefer_pump_type_map[data.prefer_pump_type]))

                var fuel_products = data.fuel_products.slice(0, 10)
                if(fuel_products == ''){
                    fuel_products = gettext('暂无')
                }
                else{
                    fuel_products.join(";")
                }
                $('#customer_habits').append(String.format('<tr><td>4</td><td>'+gettext("油品消费倾向")+'</td><td>{0}</td></tr>',
                    fuel_products))
                var favourite_nonfuel_products = data.favourite_nonfuel_products.slice(0, 10)
                if(favourite_nonfuel_products == ''){
                    favourite_nonfuel_products = gettext('暂无')
                }
                else{
                    favourite_nonfuel_products.join(";")
                }
                $('#customer_habits').append(String.format('<tr><td>5</td><td>'+gettext("购买最多的非油品")+'</td><td>{0}</td></tr>',
                   favourite_nonfuel_products))

                //render similar_group_distribution
                data['similar_group_distribution'] = []
                if (data['similar_group_distribution'].length == 0) {
                    /*  $('#similar_group_distribution').html('<tr><th colspan="4" style="text-align: center">暂无数据</th></tr>')*/
                    similar_group_distribution()
                }


                // 获取用户聚合的数据
                if ($('#people_group_table')) {
                    $('#people_group_table').html('<tr><th colspan="4" style="text-align: center">'+gettext("正在加载数据...")+'</th></tr>');
                    $.get('/gcustomer/ajax/get_user_group/', {user_source: 1}, function (data) {
                        if (data.ret != '0001') {
                            $("#alert_modal_body").html(data.info);
					        $("#alert_modal").modal("show");
                            return
                        }
                        console.log(data)
                        $('#people_group_table').empty();
                        var group_list = data['groups'];
                        if (group_list.length == 0) {
                            $('#people_group_table').html('<tr><th colspan="4" style="text-align: center">'+gettext("暂无数据")+'</th></tr>')
                        }
                        for (var i = 0; i < group_list.length; i++) {
                            var item_list = group_list[i]['items'];
                            var user_list = group_list[i]['users'];
                            var item_string = item_list.slice(0, 10).join(',\n');
                            var user_string = user_list.slice(0, 10).join(',\n');
                            var detail = user_list.length + gettext('个人，购买了') + item_list.length + gettext('种商品');
                            $('#people_group_table').append('<tr><td>' + i + '</td><td>' + item_string + '</td><td>' + user_string + '</td><td>' + detail + '</td></tr>')
                        }
                    });

                }

            }, 'json')


    });

    //big_customer

    $('#big_customer_search').on('click', function () {
        var big_customer_master_cardnum = $('#big_customer input').val().trim();
        if (big_customer_master_cardnum == "") {
            $("#alert_modal_body").html(gettext("请输入客户名"));
            $("#alert_modal").modal("show");
            return
        }
        $('#infornation_survey').html('<tr><th colspan="4" style="text-align: center">'+gettext("正在加载数据...")+'</th></tr>');
        $('#slave_card_information').html('<tr><th colspan="5" style="text-align: center">'+gettext("正在加载数据...")+'</th></tr>');
        $('#communication_record').html('<tr><th colspan="8" style="text-align: center">'+gettext("正在加载数据...")+'</th></tr>');
        $.get('/gcustomer/ajax/big_customer_manage',
            {source_id: 10000, cardnum: big_customer_master_cardnum},
            function (data) {
                if (data.ret != '0001') {
                    $("#alert_modal_body").html(data.info);
					$("#alert_modal").modal("show");
                    $('#infornation_survey').empty()
                    $('#slave_card_information').empty()
                    $('#communication_record').empty()
                    return
                }

                $('#infornation_survey').empty()
                $('#slave_card_information').empty()

                $('#infornation_survey').append(String.format('<tr><td>单位名称</td><td>{0}</td><td>'+gettext("创建时间")+'</td><td>{1}</td></tr>',
                    data.name, data.create_time))
                $('#infornation_survey').append(String.format('<tr><td>已充值量</td><td>{0}</td><td>'+gettext("当前余额")+'</td><td>{1}</td></tr>',
                    data.prepaid_amount, data.current_balance))
                $('#infornation_survey').append(String.format('<tr><td>副卡数量</td><td>{0}</td><td></td><td></td></tr>',
                    data.nb_slave_cards))

                for (var i = 0; i < data.slaveObj.length; i++)
                    $("#slave_card_information").append(String.format('<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td><a href="#">{4}</a></td></tr>',
                        i + 1, data.slaveObj[i].cardnum, data.slaveObj[i].user_name, data.slaveObj[i].curr_balance, gettext('编辑')
                    ))
                //communication_record
                data['communication_record'] = []
                if (data['communication_record'].length == 0) {
                    $('#communication_record').html('<tr><th colspan="8" style="text-align: center">'+gettext("暂无数据")+'</th></tr>')
                }


                //编辑副卡信息
                $("#big_customer_infromation_overview").show()
                main_cardnum = $("#big_customer").find("input").val()
                if (main_cardnum == "") {
                    $("#alert_modal_body").html(gettext("请输入大客户卡号"));
					$("#alert_modal").modal("show");
                    return
                }
                $('#slave_card_list').remove()
                $("#slave_card_list_container").append('<div class="col-lg-12" id="slave_card_list"></div>')
                $('#slave_card_list').jtable({
                    title: gettext('编辑副卡信息'),
                    paging: true,
                    pageSize: 10, //default is 10
                    dialogShowEffect: "slide",
                    messages: {
                        noDataAvailable: gettext("没有数据"),
                        loadingMessage: gettext("数据加载中"),
                        addNewRecord: gettext("添加新的副卡"),
                        serverCommunicationError: 'An error occured while communicating to the server.',
                        editRecord: gettext('编辑副卡'),
                        areYouSure: gettext('确定?'),
                        deleteConfirmation: gettext('该副卡信息会被删除,确定吗?'),
                        save: gettext('保存'),
                        saving: gettext('保存'),
                        cancel: gettext('取消'),
                        deleteText: gettext('删除'),
                        deleting: gettext('删除'),
                        error: gettext('错误'),
                        close: gettext('关闭'),
                        cannotLoadOptionsFor: 'Can not load options for field {0}',
                        pagingInfo: '显示 {0}-{1}',
                        pageSizeChangeLabel: gettext('每页副卡数'),
                        gotoPageLabel: gettext('跳转到'),
                        canNotDeletedRecords: 'Can not deleted {0} of {1} records!',
                        deleteProggress: 'Deleted {0} of {1} records, processing...'
                    },
                    actions: {
                        listAction: '/gcustomer/ajax/get_slave_card/?main_cardnum=' + main_cardnum,
                        createAction: '/gcustomer/ajax/create_slave_card/?main_cardnum=' + main_cardnum,
                        updateAction: '/gcustomer/ajax/update_slave_card/?main_cardnum=' + main_cardnum,
                        deleteAction: '/gcustomer/ajax/delete_slave_card/?main_cardnum=' + main_cardnum
                    },
                    fields: {
                        cardnum: {
                            title: gettext('帐号'),
                            /*  key : true ,*/
                            edit: true
                        },
                        user_name: {
                            title: gettext('姓名'),
                        },
                        car_num: {
                            title: gettext('车牌号'),
                            edit: false

                        },
                        curr_balance: {
                            title: gettext('当前余额'),
                            /*edit:false*/
                        },
                        main_cardnum: {
                            title: gettext('主卡号'),
                            list: false,
                            edit: false,
                            create: false
                        }
                    }
                });
                $('#slave_card_list').jtable("load");
                $(".ui-dialog").css("width", "500px")
                $(".ui-resizable").css("width", "500px")
            }, 'json')


    })


    if ($('#contribution_search') != 0) {
        $('#contribution_search').on('click', function () {
            $("#the_contribution_rank").show()
            $('#contribution_rank').html('<tr><th colspan="4" style="text-align: center">'+gettext("暂无数据")+'</th></tr>')
        })
    }
});
//相似客户分布
function similar_group_distribution() {
    if ($('#similar_group_distribution').length != 0) {
        $('#similar_group_distribution').highcharts({
            chart: {
                type: 'column'
            },
            title: {
                text: gettest('相似客户分布')
            },
            subtitle: {
                text: ''
            },
            xAxis: {
                categories: [
                    ","
                ]
            },
            yAxis: {
                title: {
                    text: gettext('百分比 (%)')
                }
            },

            plotOptions: {
                column: {
                    pointPadding: 0.4,
                    borderWidth: 0
                }
            },
            series: [{
                name: gettext('企业客户'),
                data: [23.0,]

            }, {
                name: gettext('忠实散户'),
                data: [18.0,]

            }, {
                name: gettext('一般客户'),
                data: [49.0,]

            }, {
                name: gettext('其他'),
                data: [10.0,]

            }]
        });
    }
}

/* 新建客户群页面 */

var CreateCustomerGroup = {

    init: function () {
        ////const var
        var user_source_map = {1: gettext("中石油"), 2: gettext("中石化"), 3: gettext("中海油"), 4: gettext("壳牌"), 5: gettext("中化")}
        var best_promotion_mode_map = {0: gettext("改善运营效率"), 1: gettext("油品优惠"), 2: gettext("非油品优惠"), 3: gettext("定额优惠"), 4: gettext("忠诚客户优惠")}
        var perfer_fuel_cost_option = {0: gettext("消费金额倾向"), 1: gettext("加油时间倾向"), 2: gettext("加满率"), 3: gettext("单次加油额"), 4: gettext("非油品消费类型"), 5: gettext("加油间隔"),6:gettext("喜爱的非油品")}
        var prefer_time_map = {0: gettext("无规律"), 1: gettext("早上"), 2: gettext("中午"), 3: gettext("晚上"), 4: gettext("午夜")}
        var prefer_pump_type_map = {0: gettext("无规律"), 1: gettext("加满"), 2: gettext("定额")}
        var prefer_cost_map = {0: gettext("无规律"), 1: gettext("加很多"), 2: gettext("加很少"), 3: gettext("一般")}
        var prefer_fuel_cost_map = {0: gettext("无规律"), 1: gettext("加很多"), 2: gettext("加很少"), 3: gettext("一般")}
        var prefer_nonfuel_cost_map = {0: gettext("无规律"), 1: gettext("买很多"), 2: gettext("买很少"), 3: gettext("一般")}
        var efficiency_map = {0: gettext("无影响"), 1: gettext("一般"), 2: gettext("严重")}
        var pump_timeout = {0: gettext("间隔几天"), 1: gettext("每天"), 2: gettext("间隔一个月以上")}
        var already_inited_grouped = false
        var already_inited_user_profile = false

        $('button.remove').on('click', function (e) {
            if ($(this).attr("name") == "age") {
                $("input[name='start_age']").val("");
                $("input[name='end_age']").val("");
            }
            $(this).remove()
        })
        $('.remove').on('click', function (e) {
            if ($(this).attr("name") == "age") {
                $("input[name='start_age']").val("");
                $("input[name='end_age']").val("");
            }
            $(this).remove()
        });

        if ($("#shengcode").length != 0) {
            init_china_location()
        }

        //加载行为特征
        if ($("select[name='behavior_characteristic']").length != -1) {
            //init behavior option
            /*  $("select[name='behavior_characteristic']").append('<option value="">请选择添加行为特征</option>')*/
            for (type in perfer_fuel_cost_option) {
                $("select[name='behavior_characteristic']").append(String.format('<option value={0}>{1}</option>', type, perfer_fuel_cost_option[type]))
            }
            $($("select[name='behavior_characteristic']").find("option")[1]).hide()
            $("select[name='behavior_characteristic']").change(function () {
                behavior_type = $("select[name='behavior_characteristic']").val()
                if (behavior_type != "") {
                    $("#the_behavior_characteristic_choose").show()
                    $("select[name='behavior_choose']").empty()
                    switch (Number(behavior_type)) {
                        case 0:
                            $("select[name='behavior_choose']").append('<option value="">'+gettext("请选择")+'</option>');
                            for (var type in prefer_cost_map) {
                                $("select[name='behavior_choose']").append(String.format('<option value={0}>{1}</option>', type, prefer_cost_map[type]))
                            }
                            break;

                        case 1:
                            $("select[name='behavior_choose']").append('<option value="">'+gettext("请选择")+'</option>');
                            for (var type in prefer_time_map) {
                                $("select[name='behavior_choose']").append(String.format('<option value={0}>{1}</option>', type, prefer_time_map[type]))
                            }
                            break;

                        case 2:
                            $("select[name='behavior_choose']").append('<option value="">'+gettext("请选择")+'</option>');
                            for (var type in prefer_pump_type_map) {
                                $("select[name='behavior_choose']").append(String.format('<option value={0}>{1}</option>', type, prefer_pump_type_map[type]))
                            }
                            break;

                        case 3:
                            $("select[name='behavior_choose']").append('<option value="">'+gettext("请选择")+'</option>');
                            for (var type in prefer_fuel_cost_map) {
                                $("select[name='behavior_choose']").append(String.format('<option value={0}>{1}</option>', type, prefer_fuel_cost_map[type]))
                            }
                            break;

                        case 4:
                            $("select[name='behavior_choose']").append('<option value="">'+gettext("请选择")+'</option>');
                            for (var type in prefer_nonfuel_cost_map) {
                                $("select[name='behavior_choose']").append(String.format('<option value={0}>{1}</option>', type, prefer_nonfuel_cost_map[type]))
                            }
                            break;

                        case 5:
                            $("select[name='behavior_choose']").append('<option value="">'+gettext("请选择")+'</option>');
                            for (var type in pump_timeout) {
                                $("select[name='behavior_choose']").append(String.format('<option value={0}>{1}</option>', type, pump_timeout[type]))
                            }
                            break;
                        case 6:
                            $("select[name='behavior_choose']").append('<option value="">'+gettext("请选择")+'</option>');
                            $.get("/gcustomer/ajax/get_app_user_favourite_goods/",{},function(data){
                                    if(data.ret != '0001'){
                                            alert(gettext("获取非油品异常"));
                                            return 
                                    }
                                    for(var i=0,len=data.store_good_list.length;i<len;i++){
                                        $("select[name='behavior_choose']").append(String.format('<option value={0}>{1}</option>', data.store_good_list[i].pos_id, data.store_good_list[i].good_name))
                                    }
                            },"json");
                            break;

                    }


                }

            });

            //选择基本特征
            $("select[name='base_characteristic']").change(function () {
                if ($($('select[name="base_characteristic"] > option:selected')[0]).attr("value") == "sex") {
                    $("#customer_age").hide()
                    $("#customer_occupation").hide()
                    $("#customer_sex").show()
                }
                else if ($($('select[name="base_characteristic"] > option:selected')[0]).attr("value") == "age") {
                    $("#customer_occupation").hide()
                    $("#customer_sex").hide()
                    $("#customer_age").show()
                }
                else if ($($('select[name="base_characteristic"] > option:selected')[0]).attr("value") == "occupation") {
                    $("#customer_age").hide()
                    $("#customer_sex").hide()
                    $("#customer_occupation").show()
                }
            })

            //选择行为特征
            $("select[name='behavior_choose']").change(function () {
                var behavior_type = $("select[name='behavior_characteristic']").val()
                var behavior_choose = $("select[name='behavior_choose']").val()
                if(behavior_choose == ''){
                        return
                    }
                if(behavior_type == "6"){
                    if ($("#add_behavior_characteristics").find(String.format("span[name={0}]", behavior_type)).length != 0) {
                        return
                    }
                    behavior_value = $("select[name='behavior_choose']").find(String.format("option[value={0}]",behavior_choose)).text()
                }else{
                        switch (behavior_type) {
                            case "0" :
                                behavior_value = prefer_cost_map[behavior_choose]
                                break;

                            case "1" :
                                behavior_value = prefer_time_map[behavior_choose]
                                break;

                            case "2" :
                                behavior_value = prefer_pump_type_map[behavior_choose]
                                break;

                            case "3" :
                                behavior_value = prefer_fuel_cost_map[behavior_choose]
                                break;

                            case "4" :
                                behavior_value = prefer_nonfuel_cost_map[behavior_choose]
                                break;

                            case "5" :
                                behavior_value = pump_timeout[behavior_choose]
                                break;
                    }
                    if ($("#add_behavior_characteristics").find(String.format("span[name={0}]", behavior_type)).length != 0) {
                        return
                    }
                    
                }
                $("#add_behavior_characteristics").append(String.format('<button type="button" class="btn btn-default btn-sm remove">' +
                '<span class="glyphicon glyphicon-remove-circle" name={2} value={3}></span> {0}:{1}' +
                '</button>', perfer_fuel_cost_option[behavior_type], behavior_value, behavior_type,behavior_choose))
                $('button.remove').on('click', function (e) {
                    if ($(this).attr("name") == "age") {
                        $("input[name='start_age']").val("");
                        $("input[name='end_age']").val("");
                    }
                    $(this).remove()
                })
            })


        }


        //添加基本属性
        add_base_characteristic = function add_base_characteristic(e) {
            obj = window.event.srcElement
            $("#customer_age").hide()
            $("#customer_sex").hide()
            $("#customer_occupation").hide()
            if ($($('select[name="base_characteristic"] > option:selected')[0]).attr("value") == "sex") {
                if ($("#add_base_characteristics span[name='sex']").length == 0) {
                    if ($("input[type='radio']:checked").val() && $("input[type='radio']:checked").parent().attr('name') == 'sex') {
                        $("#add_base_characteristics").append(String.format('<button type="button" class="btn btn-default btn-sm remove" name="sex">' +
                        '<span class="glyphicon glyphicon-remove-circle" name="sex"></span> {0}' +
                        '</button>', $("input[type='radio']:checked").val()))
                    }
                }
            }

            if ($($('select[name="base_characteristic"] > option:selected')[0]).attr("value") == "occupation") {
                if ($("#add_base_characteristics span[name='occupation']").length == 0) {
                    if ($("input[type='radio']:checked").val() && $("input[type='radio']:checked").parent().attr('name') == 'occupation') {
                        $("#add_base_characteristics").append(String.format('<button type="button" class="btn btn-default btn-sm remove" name="occupation">' +
                        '<span class="glyphicon glyphicon-remove-circle" name="occupation"></span> {0}' +
                        '</button>', $("input[type='radio']:checked").val()))
                    }
                }
            }

            if ($($('select[name="base_characteristic"] > option:selected')[0]).attr("value") == "age") {
                if ($("#add_base_characteristics span[name='age']").length == 0) {
                    start_age = $("input[name='start_age']").val();
                    end_age = $("input[name='end_age']").val()
                    if (check(start_age, end_age)) {
                        $("#add_base_characteristics").append(String.format('<button type="button" class="btn btn-default btn-sm remove" name="age">' +
                        '<span class="glyphicon glyphicon-remove-circle" name="age"></span> {0}"岁"~{1}"岁"' +
                        '</button>', $("input[name='start_age']").val(), $("input[name='end_age']").val()))
                    }
                    else {
                        $("#alert_modal_body").html(gettext("请输入正确的年龄范围！"));
					    $("#alert_modal").modal("show");
                        $("select[name='base_characteristic']").val("")
                        $("input[name='start_age']").val("")
                        $("input[name='end_age']").val("")
                    }
                }
            }

            function check(start_age, end_age) {
                if (start_age != "" && end_age != "") {
                    if (start_age.search(/\D/) != -1 || end_age.search(/\D/) != -1) {
                        return false
                    }
                    else if (start_age > end_age) {
                        return false
                    }
                    else {
                        return true
                    }
                }
                else {
                    return false
                }
            }


            $('button.remove').on('click', function (e) {
                if ($(this).attr("name") == "age") {
                    $("input[name='start_age']").val("");
                    $("input[name='end_age']").val("");
                }
                $(this).remove()
            });
        }

        //创建客户群
        create_audience = function create_audience() {
            var group_name = $('#group_name').val()
            var group_location = $('#shicode').val()
            var gender = ""
            var career = ""
            var from_age = ''
            var to_age = ''
            var prefer_cost = ""
            var prefer_time = ""
            var prefer_pump_type = ""
            var prefer_fuel_cost = ""
            var prefer_nonfuel_cost = ""
            var pump_timeout = ""
            var favourite_nonfuel_products = []
            if (group_location == "") {
                group_location = $('#shengcode').val()
            }

            var description = $('#description').val()


            for (var i = 0; i < $('#add_base_characteristics button').length; i++) {
                if ($($('#add_base_characteristics button')[i]).attr('name') == 'sex') {
                    if ($($('#add_base_characteristics button')[i]).text().trim() == gettext('男')) {
                        gender = 0
                    }
                    else {
                        gender = 1
                    }
                }
                if ($($('#add_base_characteristics button')[i]).attr('name') == 'occupation') {
                    career = $($('#add_base_characteristics button')[i]).text().trim()
                }
            }
            var from_age = $('#customer_age input[name="start_age"]').val()
            var to_age = $('#customer_age input[name="end_age"]').val()

            $("#add_behavior_characteristics").each(function () {
                if (prefer_cost == "") {
                    if ($(this).find("span[name=0]").length != 0) {
                        prefer_cost = $(this).find("span[name=0]").attr("value")
                    }
                }

                if (prefer_time == "") {
                    if ($(this).find("span[name=1]").length != 0) {
                        prefer_time = $(this).find("span[name=1]").attr("value")
                    }
                }

                if (prefer_pump_type == "") {
                    if ($(this).find("span[name=2]").length != 0) {
                        prefer_pump_type = $(this).find("span[name=2]").attr("value")
                    }
                }
                if (prefer_fuel_cost == "") {
                    if ($(this).find("span[name=3]").length != 0) {
                        prefer_fuel_cost = $(this).find("span[name=3]").attr("value")
                    }
                }

                if (prefer_nonfuel_cost == "") {
                    if ($(this).find("span[name=4]").length != 0) {
                        prefer_nonfuel_cost = $(this).find("span[name=4]").attr("value")
                    }
                }

                if (pump_timeout == "") {
                    if ($(this).find("span[name=5]").length != 0) {
                        pump_timeout = $(this).find("span[name=5]").attr("value")
                    }
                }

                if ($(this).find("span[name=6]").length != 0) {
                        $(this).find("span[name=6]").each(function(){
                            favourite_nonfuel_products .push($(this).attr("value"))
                        })
                        
                }
            });
            //输入验证
             if(group_name == ''){
                 $("#alert_modal_body").html(gettext("请输入客户群名称"));
                 $("#alert_modal").modal("show");
                 return
            }
            if(group_location == ''){
                $("#alert_modal_body").html(gettext("请输入客户群范围"));
                $("#alert_modal").modal("show");
                return
            }
            if( gender === ''  && career == '' && from_age == '' && to_age == '' ){
                $("#alert_modal_body").html(gettext("请至少选择一个客户群基本属性"));
                $("#alert_modal").modal("show");
                return
            }
            if( prefer_cost === ''  &&  prefer_time == '' && prefer_pump_type =='' && prefer_fuel_cost == '' && prefer_nonfuel_cost == '' && pump_timeout == '' && favourite_nonfuel_products == [] ){
                $("#alert_modal_body").html(gettext("请至少选择一个客户群行为特征"));
                $("#alert_modal").modal("show");
                return
            }
            if(description == ''){
                $("#alert_modal_body").html(gettext("请输入客户群描述"));
                $("#alert_modal").modal("show");
                return
            }

            dict = {
                'group_name': group_name,
                'group_location': group_location,
                'description': description,
                'gender': gender,
                'career': career,
                'from_age': Number(from_age),
                'to_age': Number(to_age),
                'prefer_cost_map': prefer_cost,
                'prefer_time_map': prefer_time,
                'prefer_pump_type_map': prefer_pump_type,
                'prefer_fuel_cost_map': prefer_fuel_cost,
                'prefer_nonfuel_cost_map': prefer_nonfuel_cost,
                'pump_timeout': pump_timeout,
                'favourite_nonfuel_products':JSON.stringify(favourite_nonfuel_products.sort())
            }
            $.get("/gcustomer/ajax/create_group/", dict, function (data) {
                if (data.ret != "0001") {
                    $("#alert_modal_body").html(data.info);
					$("#alert_modal").modal("show");
                }
                else {
                    $("#alert_modal_body").html(data.info);
					$("#alert_modal").modal("show");
                    $("#group_name").val("")
                    $("#add_base_characteristics").empty()
                    $("#add_behavior_characteristics").empty()
                    $("#description").val("")
                    $("#shengcode").val("")
                    $("#shicode").val("")
                    $("select[name='base_characteristic']").val("")
                    $("select[name='behavior_characteristic']").val("")
                    $("select[name='behavior_choose']").val("")
                }
            }, "json")
        }

        //初始化行政区划
        function init_china_location() {

            var url_prefix = "gcustomer/";
            /*$('meta[name="url_prefix"]').attr('content');*/
            ////取得省份的信息
            $.post('/' + url_prefix + 'ajax/get_china_location/', {'parent': 0, 'level': 1}, function (data) {
                //判断返回值是否正确
                if (data.ret != 0001) {
                    $("#alert_modal_body").html(data.info);
					$("#alert_modal").modal("show");
                    return
                }
                var all_ps = data['dict_city']

                //循环遍历出城市的id和name,并填充到页面中
                for (var i = 0; i < all_ps.length; i++) {
                    var $html = String.format('<option value="{0}">{1}</option>', all_ps[i][0], all_ps[i][1])
                    $('#shengcode').append($html)
                }
            }, "json")

            //监听选择市/县的事件

            $('#shengcode').change(function () {
                if ($("#shengcode").val() == "") {
                    $("#alert_modal_body").html("请选择省份！");
					$("#alert_modal").modal("show");
                    return
                }
                //取出url地址
                var url_prefix = "gcustomer/";
                /*$('meta[name="url_prefix"]').attr('content');*/
                var parent = $('#shengcode').val()

                //通过ajax请求取得城市的信息
                $.post('/' + url_prefix + 'ajax/get_china_location/',
                    {"parent": parent, "level": 2},
                    function (data) {

                        //判断返回值是否正确
                        if (data.ret != 0001) {
                            $("#alert_modal_body").html(data.info);
					        $("#alert_modal").modal("show");
                            return
                        }
                        var all_ps = data['dict_city']
                        var $shicode = $('#shicode').empty();
                        $shicode.append('<option selected value="">'+gettext("请选择")+'</option>')
                        var $xiancode = $('#xiancode').empty();
                        $xiancode.append('<option selected value="">'+gettext("请选择")+'</option>')

                        //循环遍历出城市的id和name,并填充到页面中
                        for (var i = 0; i < all_ps.length; i++) {
                            var $html = String.format('<option value="{0}">{1}</option>', all_ps[i][0], all_ps[i][1])
                            $('#shicode').append($html)
                        }
                    },
                    "json");
            })

            $("#shicode").change(function () {
                if ($("#shicode").val() == "") {
                    $("#alert_modal_body").html(gettext("请选择市级名称！"));
					$("#alert_modal").modal("show");
                    return
                }
                //取出url地址
                var url_prefix = "gcustomer/"
                /*$('meta[name="url_prefix"]').attr('content');*/
                var parent = $('#shicode').val()

                //通过ajax请求取得区县的信息
                $.post('/' + url_prefix + 'ajax/get_china_location/',
                    {"parent": parent, "level": 3},
                    function (data) {

                        //判断返回值是否正确
                        if (data.ret != 0001) {
                            $("#alert_modal_body").html(data.info);
					        $("#alert_modal").modal("show");
                            return
                        }
                        var all_ps = data['dict_city']
                        var $xiancode = $('#xiancode').empty();
                        $xiancode.append('<option selected value="">'+gettext("请选择")+'</option>')

                        //循环遍历出城市的id和name,并填充到页面中
                        for (var i = 0; i < all_ps.length; i++) {
                            var $html = String.format('<option value="{0}">{1}</option>', all_ps[i][0], all_ps[i][1])
                            $('#xiancode').append($html)
                        }
                    }, "json");
            })
        }

    }

}

/* 已有客户群 */
var GroupPage = {
    init: function () {
        if ($('#checkCustomerGroupModal').length != 0) {
            $('#checkCustomerGroupModal').on('show.bs.modal', function (event) {
                var button = $(event.relatedTarget) // Button that triggered the modal
                var name = button.data("name") // Extract info from data-* attributes
                var range = button.data("range")
                var info = button.data("info")
                var characteristics = button.data("characteristics")
                var description = button.data("description")
                var modal = $(this)
                modal.find(".modal-title").html(name)
                modal.find("#range").html(gettext("客户群范围：") + range)
                modal.find("#info").html(gettext("基本信息：") + info)
                modal.find("#characteristics").html(gettext("行为特征：") + characteristics)
                modal.find("#description").html(gettext("客户群描：") + description)
            });
            //查询已有的客户群
            $("#group_search").on('click', function () {
                $(".pagination").empty()
                $("#paging_10").hide()
                var customer_group_name = $("#customer_group_name").val().trim()
                var startIndex = 0
                var endIndex = 10
                get_customer_group(customer_group_name,startIndex,endIndex);
            });

        }

    }
}

function get_customer_group(customer_group_name,startIndex,endIndex){
                dict = {
                                "customer_group_name" : customer_group_name,
                                "startIndex" : startIndex ,
                                "endIndex": endIndex
                            }
                $("#the_customer_group_details").show()
                $.get("/gcustomer/ajax/get_customer_group_info", dict,
                function (data) {
                    if (data.ret != "0001") {
                        $("#alert_modal_body").html(data.info);
					    $("#alert_modal").modal("show");
                    }
                    //显示客户群
                    $("#contribution_infornation_survey").empty()
                    if (data.objs.length == 0) {
                        $("#contribution_infornation_survey").append("<tr><th colspan='7' style='text-align:center;'>"+gettext("没有客户群")+"</th></tr>")
                    }
                    //显示分页
                    if($("#paging_10").css('display') != "block"){
                            var length = data.length
                            if( length >10){
                                var pageSize = parseInt(length /10)
                                $("#group_count").html(pageSize)
                                if(pageSize > 10){
                                    pageSize = 9
                                }
                                var pageCount = length % 10
                                $(".pagination").append('<li>'+
                                        '<a  onclick="get_customer_group_pagination(this);" aria-label="Previous" class="previous">'+
                                        '<span aria-hidden="true">&laquo;</span>'+
                                        '</a>'+
                                        '</li>'+
                                '')
                                for(var i = 1;i<=pageSize;i++){
                                    $(".pagination").append(String.format(''+
                                            '<li><a onclick="get_customer_group_pagination(this);" class="page_button">{0}</a></li>'+
                                        '',i))
                                }
                                if(pageCount > 0){
                                    $("#group_count").html(parseInt(length /10)+1)
                                    $(".pagination").append(String.format(''+
                                            '<li><a onclick="get_customer_group_pagination(this);" class="page_button">{0}</a></li>'+
                                        '',i))
                                }
                                $(".pagination").append('<li>'+
                                    '<a onclick="get_customer_group_pagination(this);" aria-label="Next" class="next">'+
                                    '<span aria-hidden="true">&raquo;</span>'+
                                    '</a>'+
                                    '</li>'+
                                '')
                                page_list = $("#paging_10").find("a.page_button")
                                $(page_list[0]).css("background-color",'aliceblue');
                                $(page_list[0]).addClass("page_active");
                                $("#paging_10").show()
                            }
                        }
                    i = 0
                    if(data.objs.length < 10){
                            for(var i = 0;i<data.objs.length;i++){
                                var obj = data.objs[i]
                                $("#contribution_infornation_survey").append(String.format('' +
                                '<tr>' +
                                '<td style="display:none;">{0}</td>' +
                                '<td>{3}</td>' +
                                '<td>{1}</td>' +
                                '<td>{2}</td>' +
                                '<td><button class="get-detials">'+gettext("查看")+'</button></td>' +
                                '<td><button class="get-group-info">'+gettext("查看")+'</button></td>' +
                                '<td><button class="delete-group">'+gettext("删除")+'</button></td>' +
                                '</tr>' +
                                '', i + 1, obj.group_name, obj.group_creator_name,obj.group_id));
                            }
                    }
                    else{
                            for(var i = 0;i<10;i++){
                                var obj = data.objs[i]
                                $("#contribution_infornation_survey").append(String.format('' +
                                '<tr>' +
                                '<td style="display:none;">{0}</td>' +
                                '<td>{3}</td>' +
                                '<td>{1}</td>' +
                                '<td>{2}</td>' +
                                '<td><button class="get-detials">'+gettext("查看")+'</button></td>' +
                                '<td><button class="get-group-info">'+gettext("查看")+'</button></td>' +
                                '<td><button class="delete-group">'+gettext("删除")+'</button></td>' +
                                '</tr>' +
                                '', i + 1, obj.group_name, obj.group_creator_name,obj.group_id));
                            }
                    }
                    $("#customer_group_name").val(customer_group_name);
                    //获取用户群详情
                    $(".get-detials").on("click", function () {
                        $("#checkCustomerGroupModal").modal("show");
                        $(".modal-body").find('table').empty();
                        group_id = $($(this).parent().parent().find("td")[1]).html().trim();
                        $.get('/gcustomer/ajax/get_customer_group_detail/', {'group_id': group_id},
                            function (data) {
                                var obj = data.obj[0]
                                var group_location = obj.group_location;
                                var gender = obj.gender;
                                if (gender == "0") {
                                    gender = gettext("性别：男");
                                } else if (gender == "1") {
                                    gender = gettext("性别：女");
                                }else  if(gender == "-1") {
                                    gender = gettext("性别：无限制");
                                }
                                var from_age = obj.from_age;
                                var to_age = obj.to_age;
                                if (from_age != 0 && to_age != 0) {
                                    var age = gettext("年龄段：") + from_age + "~" + to_age;
                                } else {
                                    var age = "";
                                }
                                var career = obj.career;
                                if(career != ""){
                                        career = gettext("职业:")+career
                                }
                                var favourite_nonfuel_products = obj.favourite_nonfuel_products
                                if(favourite_nonfuel_products != ""){
                                    favourite_nonfuel_products = gettext("最喜爱的非油品:") +  favourite_nonfuel_products;
                                }
                                var prefer_cost  = obj.prefer_cost_map == '' ? obj.prefer_cost_map :gettext('消费金额倾向:')+prefer_cost_map[Number(obj.prefer_cost_map)];
                                var prefer_time = obj.prefer_time_map == '-1' ? gettext('加油时间倾向:无限制') : gettext('加油时间倾向:')+prefer_time_map[Number(obj.prefer_time_map)];
                                var prefer_pump_type = obj.prefer_pump_type_map == '-1' ? gettext('加满率:无限制') : gettext('加满率:')+prefer_pump_type_map[Number(obj.prefer_pump_type_map)];
                                var prefer_fuel_cost = obj.prefer_fuel_cost_map == '' ? obj.prefer_fuel_cost_map : gettext('单次加油额:')+prefer_fuel_cost_map[Number(obj.prefer_fuel_cost_map)];
                                var prefer_nonfuel_cost = obj.prefer_nonfuel_cost_map == '' ? obj.prefer_nonfuel_cost_map : gettext('非油品消费类型:')+prefer_nonfuel_cost_map[Number(obj.prefer_nonfuel_cost_map)];
                                var pump_timeout_trend = obj.pump_timeout == '' ? obj.pump_timeout : gettext('加油间隔:')+pump_timeout[Number(obj.pump_timeout)];
                                var description = obj.description;
                                if (data.ret == "0001") {
                                    $(".modal-title")
                                        .append(String.format('' +
                                            gettext("客户群名称") +'：{0}',obj.group_name
                                        ));
                                    $("#customer_group_detail")
                                        .append(String.format('' +
                                            '<tr>' +
                                            '<td>客户群范围：{0}</td>' +
                                            '</tr>' +
                                            '<tr>' +
                                            '<td>{1}</td>' +
                                            '</tr>' +
                                            '<tr>' +
                                            '<td>{2}</td>' +
                                            '</tr>' +
                                            '<tr>' +
                                            '<td>{10}</td>' +
                                            '</tr>' +
                                            '<tr>' +
                                            '<td>{3}</td>' +
                                            '</tr>' +
                                            '<tr>' +
                                            '<td>{4}</td>' +
                                            '</tr>' +
                                            '<tr>' +
                                            '<td>{5}</td>' +
                                            '</tr>' +
                                            '<tr>' +
                                            '<td>{6}</td>' +
                                            '</tr>' +
                                            '<tr>' +
                                            '<td>{7}</td>' +
                                            '</tr>' +
                                            '<tr>' +
                                            '<td>{8}</td>' +
                                            '</tr>' +
                                            '<tr>' +
                                            '<td>{11}</td>' +
                                            '</tr>' +
                                            '<tr>' +
                                            '<td>客户群描述：{9}</td>' +
                                            '</tr>' + '',
                                            group_location,              //客户群范围
                                            gender,                     //性别
                                            age,                        //年龄段
                                            prefer_cost,            //消费金额倾向
                                            prefer_time,            //加油时间倾向
                                            prefer_pump_type,       //加满率
                                            prefer_fuel_cost,       //单次加油额
                                            prefer_nonfuel_cost,    //非油品消费类型
                                            pump_timeout_trend,               //加油间隔
                                            description   ,              //描述
                                            career,
                                            favourite_nonfuel_products
                                        ));
                                } else if (data.ret != "0001") {
                                    $("#alert_modal_body").html(gettext("查询失败！"));
					                $("#alert_modal").modal("show");
                                }
                            }, "json");
                    })

                    //查询聚合信息
                    $(".get-group-info").on("click", function () {
                        group_id = Number($($(this).parent().parent().find("td")[1]).html().trim())
                        $.get("/gcustomer/ajax/get_customer_group_detail/",{"group_id":group_id},
                            function(data){
                                user_list = data.obj[0].user_list
                                if (user_list.length == 0){
                                    $("#alert_modal_body").html(gettext("没有客户属于该群！"));
					                $("#alert_modal").modal("show");
                                    return
                                }
                                users_string = gettext('用户列表')+'\n'
                                for(var i = 0,len = user_list.length;i < len; i ++){
                                    users_string = users_string + '\n' + user_list[i]
                                }
                                alert(users_string)
                            },"json")
                    })
                    //删除群组
                    $(".delete-group").on("click", function () {
                        group_id = $($(this).parent().parent().find("td")[1]).html().trim()
                        $(this).parent().parent().remove()
                        $("#contribution_infornation_survey").empty()
                        $.get('/gcustomer/ajax/delete_customer_group/', {'group_id': group_id},
                            function (data) {
                                if (data.ret != "0001") {
                                    $("#alert_modal_body").html(data.info);
	                      $("#alert_modal").modal("show");
                                }
                                $("#group_search").click();
                            }, "json")
                    })

                }, "json")
}

function get_customer_group_pagination(obj){
    var pagination = $(obj);

    if(pagination.hasClass("page_button")){
        pagination.parent().parent().find("a").css("background-color","white");
        pagination.parent().parent().find("a").removeClass("page_active");
        pagination.css("background-color",'aliceblue');
        pagination.addClass("page_active");
        var page_count = Number(pagination.html())
        var customer_group_name = $("#customer_group_name").val().trim()
        var startIndex = (page_count -1)* 10
        var endIndex = page_count * 10
        get_customer_group(customer_group_name,startIndex,endIndex);
    }
    else if($(obj).hasClass("previous")){
        var current_page = $(pagination.parent().parent().find(".page_active"))
        var page_count = Number(current_page.html()) -1
        if(page_count <= 0){
            return
        }
        page_list = pagination.parent().parent().find("a.page_button")
        if(Number(current_page.html()) == Number($(page_list[0]).html())){
                $(pagination.parent().parent().find("a.page_button")).each(function(){
                $(this).html(Number($(this).html())-1)
                 });
                pagination.parent().parent().find("a").css("background-color","white");
                pagination.parent().parent().find("a").removeClass("page_active");
                current_page.css("background-color",'aliceblue');
                current_page.addClass("page_active");
        }
        else{
            prev_page = current_page.parent().prev()
            pagination.parent().parent().find("a").css("background-color","white");
            pagination.parent().parent().find("a").removeClass("page_active");
            prev_page.children().css("background-color",'aliceblue');
            prev_page.children().addClass("page_active");
        }
        var customer_group_name = $("#customer_group_name").val().trim()
        var startIndex = (page_count -1)* 10
        var endIndex = page_count * 10
        get_customer_group(customer_group_name,startIndex,endIndex);
    }
    else if($(obj).hasClass("next")){
        var current_page = $(pagination.parent().parent().find(".page_active"))
        var page_count = Number(current_page.html()) + 1
        if(page_count > Number($("#group_count").html())){
            return
        }
        page_list = pagination.parent().parent().find("a.page_button")
        if(Number(current_page.html()) == Number($(page_list[page_list.length-1]).html())){
                $(pagination.parent().parent().find("a.page_button")).each(function(){
                $(this).html(Number($(this).html())+1)
                 });
                pagination.parent().parent().find("a").css("background-color","white");
                pagination.parent().parent().find("a").removeClass("page_active");
                current_page.css("background-color",'aliceblue');
                current_page.addClass("page_active");
        }
        else{
            next_page = current_page.parent().next()
            pagination.parent().parent().find("a").css("background-color","white");
            pagination.parent().parent().find("a").removeClass("page_active");
            next_page.children().css("background-color",'aliceblue');
            next_page.children().addClass("page_active");

        }
        var customer_group_name = $("#customer_group_name").val().trim()
        var startIndex = (page_count -1)* 10
        var endIndex = page_count * 10
        get_customer_group(customer_group_name,startIndex,endIndex);
    }
}

/* 新建大客户页面  */

var CreateBigCustomer = {
    init: function () {
        $('#create_bigcustomer_next').on('click', function () {
            customer_cardnum = $("#customer_cardnum").val()
            customer_name = $("#customer_name").val()
            customer_type = $("select[name='base_characteristic']").val()
            slave_card_nb = $("#sub_card_num").val()
            if (check_create_big_customer_step1()) {
                createBigCustomer(customer_cardnum, customer_name, customer_type, slave_card_nb);
            }
        });

        $("#create_bigcustomer_back").on('click', function () {
            $("#create_big_customer_step2").hide()
            $("#create_big_customer_step1").show()
        });

        $('#create_bigcustomer_ok').on('click', function () {
            window.location.href = "/gcustomer/create_customer/"
        });

        $("select[name='choose_slave_card']").change(function () {
            $("#edit_slave_card_information").hide()
            $("#import_slave_card__file").hide()
            $("#create_bigcustomer_ok").hide()
            if ($("select[name='choose_slave_card']").val() == '1') {
                $("#create_bigcustomer_ok").show()
                $("#edit_slave_card_information").show()
                main_cardnum = $("#customer_cardnum").val()
                $('#edit_slave_card_information').jtable({
                    title: gettext('添加副卡信息'),
                    paging: true,
                    pageSize: 10, //default is 10
                    /*sorting:true,
                     defaultSorting : 'curr_balance DESC',*/
                    dialogShowEffect: "slide",
                    messages: {
                        noDataAvailable: gettext("没有数据"),
                        loadingMessage: gettext("数据加载中"),
                        addNewRecord: gettext("添加新的副卡"),
                        serverCommunicationError: 'An error occured while communicating to the server.',
                        editRecord: gettext('编辑副卡'),
                        areYouSure: gettext('确定?'),
                        deleteConfirmation: gettext('该副卡信息会被删除,确定吗?'),
                        save: gettext('保存'),
                        saving: gettext('保存'),
                        cancel: gettext('取消'),
                        deleteText: gettext('删除'),
                        deleting: gettext('删除'),
                        error: gettext('错误'),
                        close: gettext('关闭'),
                        cannotLoadOptionsFor: 'Can not load options for field {0}',
                        pagingInfo: 'gettext("显示") {0}-{1}',
                        pageSizeChangeLabel: gettext('每页副卡数'),
                        gotoPageLabel: gettext('跳转到'),
                        canNotDeletedRecords: 'Can not deleted {0} of {1} records!',
                        deleteProggress: 'Deleted {0} of {1} records, processing...'
                    },
                    actions: {
                        listAction: '/gcustomer/ajax/get_slave_card/?main_cardnum=' + main_cardnum,
                        createAction: '/gcustomer/ajax/create_slave_card/?main_cardnum=' + main_cardnum,
                        updateAction: '/gcustomer/ajax/update_slave_card/?main_cardnum=' + main_cardnum,
                        deleteAction: '/gcustomer/ajax/delete_slave_card/?main_cardnum=' + main_cardnum
                    },
                    fields: {
                        /*id: {
                         title : "编号",
                         key: true,
                         edit:false
                         },*/
                        cardnum: {
                            title: gettext('帐号'),
                            edit: true,
                            /* key : true*/
                        },
                        user_name: {
                            title: gettext('姓名'),
                        },
                        car_num: {
                            title: gettext('车牌号'),
                            edit: true

                        },
                        curr_balance: {
                            title: gettext('当前余额'),
                            /*edit:false*/
                        },
                        main_cardnum: {
                            title: gettext('主卡号'),
                            list: false,
                            edit: false,
                            create: false
                        }
                    }
                });
                $('#edit_slave_card_information').jtable("load");
            }
            else if ($("select[name='choose_slave_card']").val() == '0') {
                $("#create_bigcustomer_ok").show()
                $("#import_slave_card__file").show()
            }
        });

        function check_create_big_customer_step1() {
            if ($("#create_big_customer_step1").length != 0) {
                if ($("#customer_cardnum").val() == "") {
                    $("#alert_modal_body").html(gettext("请输入主卡号"));
					$("#alert_modal").modal("show");
                    return false
                }
                else if (!($("#customer_cardnum").val().match(/\D/) == null)) {
                    $("#customer_cardnum").val("")
                    $("#alert_modal_body").html(gettext("主卡号格式错误！"));
					$("#alert_modal").modal("show");
                    return false
                }

                if ($("#customer_name").val() == "") {
                    $("#alert_modal_body").html(gettext("请输入大客户名称！"));
					$("#alert_modal").modal("show");
                    return false
                }

                if ($("select[name='base_characteristic']").val() == "") {
                    $("#alert_modal_body").html(gettext("请选择客户来源"));
					$("#alert_modal").modal("show");
                    return false
                }

                if ($("#sub_card_num").val() == "") {
                    $("#alert_modal_body").html(gettext("请输入副卡数量"));
					$("#alert_modal").modal("show");
                    return false
                }
                else if (!($("#sub_card_num").val().match(/\D/) == null )) {
                    $("#alert_modal_body").html(gettext("请输入整数数值"));
					$("#alert_modal").modal("show");
                    $("#sub_card_num").val("")
                    return false
                }
                else if (!($("#sub_card_num").val().match(/\s/) == null )) {
                    $("#alert_modal_body").html(gettext("格式错误"));
					$("#alert_modal").modal("show");
                    $("#sub_card_num").val("")
                    return false
                } else if (!($("#sub_card_num").val().match(/^0/) == null )) {
                    $("#alert_modal_body").html(gettext("格式错误"));
					$("#alert_modal").modal("show");
                    $("#sub_card_num").val("")
                    return false
                }

                return true
            }
        };

        function createBigCustomer(customer_cardnum, customer_name, customer_type, slave_card_nb) {
            dict = {
                "customer_cardnum": customer_cardnum,
                "customer_name": customer_name,
                "customer_type": customer_type,
                "slave_card_nb": slave_card_nb
            }
            $.get("/gcustomer/ajax/create_big_customer/", dict,
                function (data) {
                    if (data.ret == "0001") {
                        $("#alert_modal_body").html("ok");
					    $("#alert_modal").modal("show");
                        if (confirm(gettext("现在就去编辑副卡信息!"))) {
                            $("#create_big_customer_step1").hide();
                            $("#create_big_customer_step2").show();
                        }
                        else {
                            $("#customer_cardnum").val("")
                            $("#customer_name").val("")
                            /*$("select[name='base_characteristic'] option[value='']").selected='selected'*/
                            $("#sub_card_num").val("")
                        }
                    }
                    else {
                        $("#alert_modal_body").html("error");
					    $("#alert_modal").modal("show");
                    }

                }, "json");
        };

        var message = $("#message").text()
        if (message) {
            $("#alert_modal_body").html(message);
            $("#alert_modal").modal("show");
        }

    }

}

/*  大客户统计页面  */

var BigCustomerStatistics = {
    init: function () {
        $.get('/gcustomer/ajax/get_main_customer_list/', {}, function (data) {
            if (data.ret != '0001') {
                $("#alert_modal_body").html(gettext("没有该油站的信息！"));
                $("#alert_modal").modal("show");
                return
            }
            $("#infornation_survey").empty()
            //排名前20的大客户
            i = 0
            $(data.main_customer_list).each(function () {
                obj = this
                $("#infornation_survey").append(String.format('' +
                        "<tr>" +
                        "<td>{0}</td>" +
                        "<td>{1}</td>" +
                        "<td>{2}</td>" +
                        "<td>{3}</td>" +
                        "<td>{4}</td>" +
                        "<td>{5}</td>" +
                        "<td>{6}</td>" +
                        "</tr>" +
                        '', i + 1, obj.name, obj.master_cardnum, obj.create_time,
                        obj.contribution, obj.current_balance, obj.nb_slave_cards)
                )
                i = i + 1
            });


            if ($('#big_customer_contribution_ratio_dash').length != 0) {
                $('#big_customer_contribution_ratio_dash').highcharts({
                    title: {
                        text: gettext('大客户贡献比例图'),
                        x: -20 //center
                    },
                    xAxis: {
                        categories: ['0', '10%', '20%', '30%', '40%', '50%', '60%', '70%', '80%', '90%', '100%'],
                        tickInterval: 0.1
                    },
                    yAxis: {
                        tickPositions: [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
                        title: {
                            text: gettext('贡献量')
                        },
                        plotLines: [{
                            value: 0,
                            width: 1,
                            color: '#808080'
                        }]
                    },
                    plotOptions: {
                        series: {
                            cursor: 'pointer',
                            events: {
                                click: function (event) {
                                    $("#result").html("<b>Result : index = " + event.point.x + " , series = " + this.name + ', x = ' + event.point.category + ' ,y = ' + event.point.y + "</b>");
                                    //alert('index = '+ event.point.x+ 'x = '+event.point.category+' ,y = '+event.point.y);
                                }
                            }
                        }
                    },
                    //不显示Legend
                    legend: {
                        enabled: false
                    },
                    //不显示Credit
                    credits: {
                        enabled: false
                    },

                    series: [{
                        name: gettext('贡献比例'),
                        data: [0.0, 35.9, 66.5, 80.5, 88.2, 91.5, 94.2, 96.5, 98.3, 99.3, 100.0]
                    }]
                });
            }

        }, "json")

    }

}

/*   大客户贡献  */

var BigcustomerContribution = {

    init: function () {
        //初始化界面
        $("#the_big_customer_contribution_information").hide()
        $("#the_near_six_month_sale_trend").hide()

        //查询大客户贡献
        $("#big_customer_contribution_search").on("click", function () {
            master_cardnum = $("#big_customer_cardnum").val()
            //查询大客户信息
            $.get('/gcustomer/ajax/big_customer_manage',
                {source_id: 10000, cardnum: master_cardnum},
                function (data) {
                    if (data.ret != '0001') {
                        $("#alert_modal_body").html(gettext("不存在这个用户！"));
					    $("#alert_modal").modal("show");
                        $("#the_big_customer_contribution_information").hide()
                        $("#the_near_six_month_sale_trend").hide()
                        return
                    }

                    //贡献的概要信息
                    if ($("#the_big_customer_contribution_information").length != 0) {
                        $("#the_big_customer_contribution_information").show()
                        $("#information_survey").empty()
                        $("#information_survey").append(String.format('<tr>' +
                                '<td>{0}</td>' +
                                '<td>{1}</td>' +
                                '<td>{2}</td>' +
                                '<td>{3}</td>' +
                                '<td>{4}</td>' +
                                '<td>{5}</td>' +
                                '</tr>', data.name,
                                data.contribution,
                                data.last_month_sale,
                                data.score,
                                data.score_rank,
                                data.pump_range)
                        )
                    }

                    //近六月消费额度趋势
                    if ($("#the_near_six_month_sale_trend").length != 0) {
                        $("#the_near_six_month_sale_trend").show()
                        $('#big_customer_consume_trend_dash').highcharts({
                            title: {
                                text: gettext('消费额度趋势'),
                                x: -20 //center
                            },
                            credits: {
                                enabled: false
                            },
                            xAxis: {
                                categories: ['2013-03-09', '2013-04-09', '2013-05-09', '2013-06-09', '2013-07-09', '2013-08-09', '2013-09-09', '2013-10-09', '2013-11-09', '2013-12-09', '2014-01-09', '2014-02-09']
                            },
                            yAxis: {
                                title: {
                                    text: gettext('消费额'),
                                },
                                plotLines: [{
                                    value: 0,
                                    width: 1,
                                    color: '#808080'
                                }]
                            },
                            tooltip: {
                                valueSuffix: gettext('万元')
                            },
                            legend: {
                                layout: 'vertical',
                                align: 'center',
                                verticalAlign: 'bottom',
                                borderWidth: 0
                            },
                            series: [{
                                name: gettext('大客户消费额'),
                                data: [7.0, 6.9, 9.5, 14.5, 18.2, 21.5, 25.2, 26.5, 23.3, 18.3, 13.9, 9.6]
                            }]
                        });
                    }

                }, "json")
        })

    }

}

/*   查看加油卡消费记录页面  */

var CustomerConsumeStatics = {

    init: function () {
        $("#main_card_information_statistic").hide()
        $("#slave_card_information_statistic").hide()
        $("#slave_card_account_record").hide()
        //获取大客户消费记录
        $("#main_card_consume_information_record_search").on('click', function () {
            master_cardnum = $("#main_card_search_form").find("input").val()
            $.get('/gcustomer/ajax/get_consume_record/', {"master_cardnum": master_cardnum},
                function (data) {
                    if (data.ret != "0001") {
                        $("#alert_modal_body").html(data.info);
					    $("#alert_modal").modal("show");
                        $("#main_card_information_statistic").hide()
                        return
                    }
                    $("#main_card_information_statistic").show()
                    $("#infornation_survey").empty()
                    var i = 0
                    $(data.objs).each(function () {
                        obj = this
                        $("#infornation_survey").append(String.format('' +
                            "<tr>" +
                            "<td>{0}</td>" +
                            "<td>{1}</td>" +
                            "<td>{2}</td>" +
                            "<td>{3}</td>" +
                            "<td><a href='#' onclick='checkAllSlaveCard(this);'>"+gettext("查看")+"</a></td>" +
                            "</tr>" +
                            '', i + 1, obj.name, obj.master_cardnum, obj.current_balance)
                        )
                        i++
                    });

                }, "json");
        });
        //返回上一级
        $("#back_to_previous").on('click', function () {
            if ($("#slave_card_information_statistic").css("display") == "block") {
                $("#main_card_information_statistic").show()
                $("#slave_card_information_statistic").hide()
                $("#slave_card_account_record").hide()
                $("#back_to_previous").hide()
                $("#main_card_search_form").show()
            }
            else if ($("#slave_card_account_record").css("display") == "block") {
                $("#main_card_information_statistic").hide()
                $("#slave_card_information_statistic").show()
                $("#slave_card_account_record").hide()
            }
        })
        //查看所有副卡
        checkAllSlaveCard = function checkAllSlaveCard(obj) {
            $("#main_card_information_statistic").hide()
            $("#slave_card_information_statistic").show()
            $("#slave_card_account_record").hide()
            $("#main_card_search_form").hide()
            $("#back_to_previous").show()
            get_record_type = $(obj).parents("table").find(".consume_record").attr("name")
            if (get_record_type == "slave_consume_record") {
                master_cardnum = $($(obj).parent().parent().find("td")[2]).html()
                $.get("/gcustomer/ajax/get_slave_consume_record/", {"master_cardnum": master_cardnum},
                    function (data) {
                        if (data.ret != "0001") {
                            $("#alert_modal_body").html(gettext("不存在该副卡信息"));
					        $("#alert_modal").modal("show");
                            return
                        }
                        $("#slave_card_infornation_survey").empty()
                        $("#current_main_card_information").html(String.format('gettext("主卡号"):{0}', master_cardnum))
                        i = 0
                        if (!data.objs.length) {
                            $("#slave_card_infornation_survey").append('<tr><th colspan="4" style="text-align: center">'+gettext("暂无数据")+'</th></tr>')
                        }
                        $(data.objs).each(function () {
                            var obj = this
                            $("#slave_card_infornation_survey").append(String.format('' +
                            '<tr>' + 
                            '<td>{0}</td>' +
                            '<td>{1}</td>' +
                            '<td>{2}</td>' +
                            '<td><a href="#" onclick="checkCurrentSlaveCard(this);">'+gettext("查看")+'</a></td>' +
                            '</tr>' +
                            '', i + 1, obj.slave_cardnum, obj.curr_balance))
                            i++
                        })
                    }, "json")
            }
        };
        //查看当前副卡
        checkCurrentSlaveCard = function checkCurrentSlaveCard(obj) {
            $("#main_card_information_statistic").hide()
            $("#slave_card_information_statistic").hide()
            $("#slave_card_account_record").show()
            $("#main_card_search_form").hide()
            $("#back_to_previous").show()
            get_record_type = $(obj).parents("table").find(".consume_record").attr("name")
            if (get_record_type == "slave_consume_details") {
                slave_cardnum = $($(obj).parent().parent().find("td")[1]).html()
                $("#current_slave_card_information").html(String.format('gettext("副卡号"):{0}', slave_cardnum))
                $("#slave_card_detials").empty()
                $("#slave_card_detials").append('<tr><th colspan="4" style="text-align: center">'+gettext("暂无数据")+'</th></tr>')
                /*$.get("/gcustomer/ajax/get_slave_consume_record/",{"master_cardnum":master_cardnum},
                 function(data){
                 if(data.ret != "1101"){
                 alert("不存在该副卡信息")
                 return
                 }
                 $("#slave_card_infornation_survey").empty()
                 $("#current_main_card_information").html(String.format('主卡号:{0}',master_cardnum))
                 i = 0
                 if(! data.objs.length){
                 $("#slave_card_infornation_survey").append('<tr><th colspan="4" style="text-align: center">暂无数据</th></tr>')
                 }
                 $(data.objs).each(function(){
                 var obj = this
                 $("#slave_card_infornation_survey").append(String.format(''+
                 '<tr>'+
                 '<td>{0}</td>'+
                 '<td>{1}</td>'+
                 '<td>{2}</td>'+
                 '<td><a href="#" onclick="checkCurrentSlaveCard();">查看</a></td>'+
                 '</tr>' +
                 '',i+1,obj.slave_cardnum,obj.curr_balance))
                 i++
                 })
                 },"json")*/
            }
        };

    }

}


//init
$(function () {
    if ($("#create_big_customer_step1").length != 0) {
        CreateBigCustomer.init()
    }
    if ($("#the_big_customer_top_20").length != 0) {
        BigCustomerStatistics.init()
    }
    if ($("#contribution_infornation_survey").length != 0) {
        GroupPage.init()
    }
    if ($("#the_big_customer_contribution_information").length != 0) {
        BigcustomerContribution.init()
    }
    if ($("#main_card_search_form").length != 0) {
        CustomerConsumeStatics.init()
    }
    if ($("#add_base_characteristics").length != 0) {
        CreateCustomerGroup.init()
    }
});
