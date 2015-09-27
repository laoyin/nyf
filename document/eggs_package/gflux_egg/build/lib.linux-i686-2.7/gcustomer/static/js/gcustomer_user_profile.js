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
//init user profile right container
                //获得消费预测
                $('#get_user_profile_forecase').on('click',function(){
                    //get user card num
                    var user_card_num=$('#search_user_profile_forecase input').val().trim()

                    if(user_card_num.length==0){
                        $("#alert_modal_body").html(gettext("请输入用户卡号，不能为空！"));
                        $("#alert_modal").modal("show");
                        return
                    }

                    if(isNaN(parseInt(user_card_num))){
                        $("#alert_modal_body").html(gettext("请输入正确的用户卡号，必须全是数字！"));
                        $("#alert_modal").modal("show");
                        return
                    }
                    $('#profile_feature_table').html('<tr><th colspan="4" style="text-align: center">gettext("正在加载数据...")</th></tr>');
                    $.get('/gcustomer/ajax/get_user_profile',
                        {user_source:1,profiling_area:'CCPQ',cardnum:user_card_num},
                        function(data){
                            if(data.ret!='0001'){
                                $("#alert_modal_body").html(data.info);
                                $("#alert_modal").modal("show");
                                return
                            }

                            //clear container
                            $('#profile_feature_table').empty()
                           // $('#information_recommand').empty()
                          //  $('#profile_feature_grouped').empty()

                            //render user feature

                            $('#profile_feature_table').append(String.format('<tr><td>gettext("油站所属集团公司")</td><td>{0}</td></tr>',
                                user_source_map[data.user_source]))
                            $('#profile_feature_table').append(String.format('<tr><td>gettext("属于站点")</td><td>{0}</td></tr>',
                                data.profiling_area))
                            $('#profile_feature_table').append(String.format('<tr><td>gettext("加油时间倾向")</td><td>{0}</td></tr>',
                                prefer_time_map[data.prefer_time]))
                            $('#profile_feature_table').append(String.format('<tr><td>gettext("加油方式倾向")</td><td>{0}</td></tr>',
                                prefer_pump_type_map[data.prefer_pump_type]))
                            $('#profile_feature_table').append(String.format('<tr><td>gettext("单次油品消费倾向")</td><td>{0}</td></tr>',
                                prefer_fuel_cost_map[data.prefer_fuel_cost]))
                            $('#profile_feature_table').append(String.format('<tr><td>gettext("单次非油品消费倾向")</td><td>{0}</td></tr>',
                                prefer_nonfuel_cost_map[data.prefer_nonfuel_cost]))
                            $('#profile_feature_table').append(String.format('<tr><td>gettext("加油间隔")</td><td>{0}</td></tr>',
                                data.avg_charge_period))
                            $('#profile_feature_table').append(String.format('<tr><td>gettext("对油站运营效率影响")</td><td>{0}</td></tr>',
                                efficiency_map[data.efficiency]))
                            $('#profile_feature_table').append(String.format('<tr><td>gettext("系统综合打分")</td><td>{0}</td></tr>',
                                data.prominence))
                            $('#profile_feature_table').append(String.format('<tr><td>gettext("最佳营销模式")</td><td>{0}</td></tr>',
                                best_promotion_mode_map[data.best_promotion_mode]))

                            //render gruoped info
                            for(var idx=0;idx<data.grouped.length;idx++){
                                $('#profile_feature_grouped').append(String.format('<li grouped_id="{1}">gettext("人群%s", {0})</li>',
                                    data.grouped[idx],data.grouped[idx]))
                            }

                            //render items
                            var user_like_items=data.favourite_nonfuel_products.slice(0,10)
                            $('#profile_feature_table').append(String.format('<tr><td>gettext("喜爱的非油品")</td><td>{0}</td></tr>',
                                user_like_items.join(';')))
                            var recommend_user_items=data.recommended_nonfuel_products.slice(0,10)
                            $('#profile_feature_table').append(String.format('<tr><td>gettext("推荐购买的非油品")</td><td>{0}</td></tr>',
                                recommend_user_items.join(';')))

                        },'json')
            })

            //获得消费习惯
             $('#get_user_profile_habits').on('click',function(){
                    //get user card num
                    var user_card_num=$('#search_user_profile_habits input').val().trim()

                    if(user_card_num.length==0){
                        $("#alert_modal_body").html(gettext("请输入用户卡号，不能为空"));
                        $("#alert_modal").modal("show");
                        return
                    }

                    if(isNaN(parseInt(user_card_num))){
                        $("#alert_modal_body").html(gettext("请输入正确的用户卡号，必须全是数字！"));
                        $("#alert_modal").modal("show");
                        return
                    }
                    $('#customer_habits').html('<tr><th colspan="4" style="text-align: center">gettext("正在加载数据...")</th></tr>');
                    $.get('/gcustomer/ajax/get_user_profile',
                        {user_source:1,profiling_area:'CCPQ',cardnum:user_card_num},
                        function(data){
                            if(data.ret!='0001'){
                                $("#alert_modal_body").html(data.info);
                                $("#alert_modal").modal("show");
                                return
                            }gettext

                            //clear container
                            $('#customer_habits').empty()

                            //render user feature
                            $('#customer_habits').append(String.format('<tr><td>1</td><td>gettext("加油地点范围")</td><td>{0}</td></tr>',
                                data.profiling_area))
                            $('#customer_habits').append(String.format('<tr><td>2</td><td>gettext("加油时间倾向")</td><td>{0}</td></tr>',
                                prefer_time_map[data.prefer_time]))
                            $('#customer_habits').append(String.format('<tr><td>3</td><td>gettext("加油方式倾向")</td><td>{0}</td></tr>',
                                prefer_pump_type_map[data.prefer_pump_type]))

                            var fuel_products=data.fuel_products.slice(0,10)
                            $('#customer_habits').append(String.format('<tr><td>4</td><td>gettext("油品消费倾向")</td><td>{0}</td></tr>',
                                fuel_products.join(";")))
                            var favourite_nonfuel_products=data.favourite_nonfuel_products.slice(0,10)
                            $('#customer_habits').append(String.format('<tr><td>5</td><td>gettext("购买最多的非油品")</td><td>{0}</td></tr>',
                                favourite_nonfuel_products.join(";")))
                        },'json')
            })

})
