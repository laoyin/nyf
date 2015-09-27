//const var
var user_source_map={1:gettext("中石油"),2:gettext("中石化"),3:gettext("中海油"),4:gettext("壳牌"),5:gettext("中化")}
var best_promotion_mode_map={0:gettext("改善运营效率"),1:gettext("油品优惠"),2:gettext("非油品优惠"),3:gettext("定额优惠"),4:gettext("忠诚客户优惠")}
var prefer_time_map={0:gettext("无规律"),1:gettext("早上"),2:gettext("中午"),3:gettext("晚上"),4:gettext("午夜")}
var prefer_pump_type_map={0:gettext("无规律"),1:gettext("加满"),2:gettext("定额")}
var prefer_fuel_cost_map={0:gettext("无规律"),1:gettext("加很多"),2:gettext("加很少"),3:gettext("一般")}
var prefer_nonfuel_cost_map={0:gettext("无规律"),1:gettext("买很多"),2:gettext("买很少"),3:gettext("一般")}
var efficiency_map={0:gettext("无影响"),1:gettext("一般"),2:gettext("严重")}
var already_inited_grouped=false
var already_inited_user_profile=false

//dom ready
$(function () {
    //bind left navigation
    $('#sidebar').find('a').on('click',function(event){
        EventUtil.preventDefault(event)

        if($('#sidebar a.active').attr('right-container-id')==$(this).attr('right-container-id'))
            return

        //remove navigator active
        $('#sidebar a.active').removeClass('active')
        $(this).addClass('active')

        //hide all right container except current
        $('.right-container').hide()

        //get right container id
        var container_id=$(this).attr('right-container-id')
        $('#'+container_id).removeClass('hide').show()

        //reinit right container
        eval($('#'+container_id).attr('init-func'))()
    })

    //init over view container
    initOverviewContainer()
});

//init user profile right container
function initUserProfileContainer(){
    if(already_inited_user_profile)
        return

    already_inited_user_profile=true
    $('#search_user_profile button').on('click',function(){
        //get user card num
        var user_card_num=$('#search_user_profile input').val().trim()

        if(user_card_num.length==0){
            $("#alert_modal_body").html(gettext("请输入用户卡号，不能为空！"));
            $("#alert_modal").modal("show");
            return
        }

        if(isNaN(parseInt(user_card_num))){
            $("#alert_modal_body").html(gettext("请输入用户卡号，必须全为数字"));
            $("#alert_modal").modal("show");
            return
        }

        $.get('/gcustomer/ajax/get_user_profile',
            {user_source:1,profiling_area:'CCPQ',cardnum:user_card_num},
            function(data){
                if(data.ret!='0001'){
                    $("#alert_modal_body").html(data.info);
                    $("#alert_modal").modal("show");
                    return
                }

                //clear container
                $('#user_profile_feature').empty()
                $('#user_profile_grouped').empty()

                //render user feature
                $('#user_profile_feature').append(String.format('<li>gettext("属于%s集团" % {0})</li>',
                    user_source_map[data.user_source]))
                $('#user_profile_feature').append(String.format('<li>gettext("属于%s站点" % {0})</li>',
                    data.site))
                $('#user_profile_feature').append(String.format('<li>gettext("加油时间倾向：%s" % {0})</li>',
                    prefer_time_map[data.prefer_time]))
                $('#user_profile_feature').append(String.format('<li>gettext("加油方式倾向：%s" % {0})</li>',
                    prefer_pump_type_map[data.prefer_pump_type]))
                $('#user_profile_feature').append(String.format('<li>gettext("单次油品消费倾向：%s" % {0})</li>',
                    prefer_fuel_cost_map[data.prefer_fuel_cost]))
                $('#user_profile_feature').append(String.format('<li>gettext("单次非油品消费倾向：%s" % {0})</li>',
                    prefer_nonfuel_cost_map[data.prefer_nonfuel_cost]))
                $('#user_profile_feature').append(String.format('<li>gettext("加油间隔：%s天" % {0})</li>',
                    data.avg_charge_period))
                $('#user_profile_feature').append(String.format('<li>gettext("对油站运营效率影响：%s" % {0})</li>',
                    efficiency_map[data.efficiency]))
                $('#user_profile_feature').append(String.format('<li>gettext("系统综合打分：%s" % {0})</li>',
                    data.prominence))
                $('#user_profile_feature').append(String.format('<li>gettext("最佳营销模式：%s" % {0})</li>',
                    best_promotion_mode_map[data.best_promotion_mode]))

                //render gruoped info
                for(var idx=0;idx<data.grouped.length;idx++){
                    $('#user_profile_grouped').append(String.format('<li grouped_id="{1}">gettext("人群%s" % {0})</li>',
                        data.grouped[idx],data.grouped[idx]))
                }

                //render items
                var user_like_items=data.favourite_nonfuel_products.slice(0,10)
                $('#user_profile_feature').append(String.format('<li>gettext("喜爱的非油品")：<ul><li>{0}</li></ul></li>',
                    user_like_items.join('</li><li>')))
                var recommend_user_items=data.recommended_nonfuel_products.slice(0,10)
                $('#user_profile_feature').append(String.format('<li>gettext("推荐购买的非油品")：<ul><li>{0}</li></ul></li>',
                    recommend_user_items.join('</li><li>')))

            }
        )
    })
}

//init lookupgrop container
function initLookupGroupContainer(){

}

//init grouped right container
function initGroupedContainer(){
    if(already_inited_grouped)
        return

    already_inited_grouped=true
    $.get('/gcustomer/ajax/get_user_group/',{user_source:1},function(data){
        if(data.ret!='0001'){
            $("#alert_modal_body").html(data.info);
            $("#alert_modal").modal("show");
            return
        }

        //render
        var t_node=$('.group_template').clone().removeClass('group_template')
        for(var idx=0;idx<data.groups.length;idx++){
            var node=t_node.clone()
            var group=data.groups[idx]
            node.find('.title').text(String.format('gettext("人群%s：共%s人,共%s种喜爱商品" % {0},{1},{2})',
                idx+1,group.users.length,group.items.length))

            //render user
            for(var ydx=0;ydx<group.users.length;ydx++){
                node.find('.group_users').append(String.format('<li>{0}</li>',
                    group.users[ydx]))
                if(ydx==9)
                    break
            }

            //render items
            for(var ydx=0;ydx<group.items.length;ydx++){
                node.find('.group_items').append(String.format('<li>{0}</li>',
                    group.items[ydx]))
                if(ydx==9)
                    break
            }

            $('#grouped_right_container').append(node)
        }
    })
}
