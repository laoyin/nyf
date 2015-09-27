
/* =============================油站画像=======================================*/

$(function(){
  $("#the_top_ten_big_customer").hide()
  $("#the_big_customer_contribution").hide()
  $("#the_fuel_sale_summary").hide()
  $("#the_fuel_sale_rank").hide()
  $("#the_nonfuel_sale_summary").hide()
  $("#the_sale_top_ten_of_nonfuel").hide()
  $("#the_sale_bottom_ten_of_nonfuel").hide()
	//油站画
	$("#add_behavior").on("click",function(){
		site=$(".form-group").find("input").val()
		$.get('/gcustomer/ajax/get_main_customer_list/',{'site':site},function(data){
			if(data.ret != '0001'){
                $("#alert_modal_body").html(gettext("没有该油站的信息！"));
                $("#alert_modal").modal("show");
				return
			}

            //排名前10客户
			if($('#the_main_customer_list').length !=0){
                $("#the_top_ten_big_customer").show()
				$('#the_main_customer_list').empty()
				for (var i=0;i<data.obj.length;i++){
					$('#the_main_customer_list').append(String.format(''+
                        '<tr>'+
                        '<td>{0}</td>'+
                        '<td>{1}</td>'+
                        '<td>{2}</td>'+
                        '</tr>'+
                        '',i+1,data.obj[i].name,data.obj[i].prepaid_amount))
				}
			}

            //非油品销售概况
			if($('#nonfuel_survey').length !=0){
                 $("#the_nonfuel_sale_summary").show()
				$('#nonfuel_survey').empty()
				$('#nonfuel_survey').append(String.format(''+
                  '<tr>'+
                      '<td>总销售额</td>'+
                      '<td>{0}万</td>'+
                  '</tr>'+
                  '<tr>'+
                      '<td>非油品销售额</td>'+
                      '<td>{1}万</td>'+
                  '</tr>'+
                  '<tr>'+
                      '<td>油品销售额</td>'+
                      '<td>{2}万</td>'+
                  '</tr>'+
                  '<tr>'+
                      '<td>省内排名</td>'+
                      '<td>{3}/1025</td>'+
                  '</tr>'+
                  '',data.station[0].total_sales_amount,
                  data.station[0].total_nonfuel_sales_amount,
                  data.station[0].fuel_sales,
                  data.station[0].rank))
			}

            //销售额前10的非油品
			if($('#main_nonfuel_purcahse_list').length !=0){
                $("#the_sale_top_ten_of_nonfuel").show()
				$('#main_nonfuel_purcahse_list').empty()
				for (var i=0;i<data.top_100_goods.length;i++){
					$('#main_nonfuel_purcahse_list').append(String.format(''+
                        '<tr>'+
                        '<td>第{0}名</td>'+
                        '<td width="40%">{1}</td>'+
                        '<td>{2}万</td>'+
                        '</tr>'+
                        '',i+1,data.top_100_goods[i].desc,data.top_100_goods[i].sum))
				}
			}

            //销售额倒数10名的非油品
			if($('#reciprocal_nonfuel_list').length !=0){
                $("#the_sale_bottom_ten_of_nonfuel").show()
				$('#reciprocal_nonfuel_list').empty()
				for (var i=0;i<data.bottom_100_goods.length;i++){
					$('#reciprocal_nonfuel_list').append(String.format(''+
                     '<tr>'+
                     '<td>倒数第{0}名</td>'+
                     '<td width="40%">{1}</td>'+
                     '<td>{2}万元</td>'+
                     '</tr>'+
                     '',i+1,data.bottom_100_goods[i].desc,data.bottom_100_goods[i].sum))
				}
			}

            //油品销售概况
            if($('#the_fuel_sale_summary').length !=0){
                $('#the_fuel_sale_summary').show()
                $("#fuel_survey").empty()
                $("#fuel_survey").append(String.format(''+
                            '<tr>'+
                                '<td>总销售额</td>'+
                                '<td>{0}万</td>'+
                            '</tr>'+
                            '<tr>'+
                                '<td>油品销售额</td>'+
                                '<td>{1}万</td>'+
                            '</tr>'+
                            '<tr>'+
                                '<td>非油品销售额</td>'+
                                '<td>{2}万</td>'+
                            '</tr>'+
                            '<tr>'+
                                '<td>省内排名</td>'+
                                '<td>{3}/1025</td>'+
                            '</tr>'+
                    '',data.station[0].total_sales_amount,
                       data.station[0].fuel_sales,
                       data.station[0].total_nonfuel_sales_amount,
                       data.station[0].rank))
            }

            //油品销售排行
            if($('#the_fuel_sale_rank').length !=0){
                $('#the_fuel_sale_rank').show()
                $("#main_fuel_purcahse_list").empty()
                i = 0
                fuel_type = data.station[0].fuel_type
                $(fuel_type).each(function(){
                    $("#main_fuel_purcahse_list").append(String.format(''+
                            '<tr>'+
                                '<td>{0}</td>'+
                                '<td>{1}</td>'+
                                '<td>{2}</td>'+
                            '</tr>'+
                        '',i+1,this.name,gettext("暂无数据")))
                    i++
                })
            }

            if($('#customer_main').length != 0){
                $("#the_big_customer_contribution").show()
                $('#customer_main').highcharts({
                        title: {
                            text: gettext('客户贡献比例图'),
                            x: -20 //center
                        },
                        xAxis: {
                            categories: ['0','10%', '20%', '30%', '40%', '50%', '60%','70%', '80%', '90%', '100%'],
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
                                    click: function(event) {
                                        $("#result").html("<b>Result : index = "+event.point.x+" , series = "+this.name + ', x = '+event.point.category+' ,y = '+event.point.y+"</b>");
                                        //alert('index = '+ event.point.x+ 'x = '+event.point.category+' ,y = '+event.point.y);
                                    }
                                }
                            }
                        },
                        //不显示Legend
                        legend: {
                            enabled:false
                        },
                        //不显示Credit
                        credits:{
                            enabled:false
                        },

                        series: [{
                            name: gettext('贡献比例'),
                            data: [0.0, 35.9, 66.5, 80.5, 88.2, 91.5, 94.2, 96.5, 98.3, 99.3, 100.0]
                        }]
                    });

                        }


            		},"json")
            })
});

/* =============================新建油站群=======================================*/

$(function(){

        //新建客户群
        $("#create_station_group").on("click",function(){
            var dict = {}
            var group_name = $("#group_name").val()
            var group_location = {}
            group_location['province'] = Number($("#shengcode").val())
            group_location['city'] = Number($("#shicode").val())
            group_location['district`'] = Number($("#xiancode").val())
            var total_sales_amount = $("#total_sales_amount").val()
            var rank = $("#rank").val()
            var group_info = $("#group_info").val()
            //验证输入
            if(group_name == {}){
                $("#alert_modal_body").html(gettext("群名称不能为空！"));
                $("#alert_modal").modal("show");
                return
            }
            if(group_location == ""){
                $("#alert_modal_body").html(gettext("请选择油站范围！"));
                $("#alert_modal").modal("show");
                return
            }
            if(total_sales_amount != ""){
                    if(total_sales_amount.search(/[.]/) !=-1 ){
                        item_list = total_sales_amount.split(".")
                        for(var item in item_list){
                            if(item.search(/\D/) != -1){
                                $("#alert_modal_body").html(gettext("销售额必须为数值"));
					            $("#alert_modal").modal("show");
                                $("#total_sales_amount").val("")
                                return
                            }
                        }

                    }
                    else if(total_sales_amount.search(/\D/) != -1){
                        $("#alert_modal_body").html(gettext("销售额必须为数值"));
					    $("#alert_modal").modal("show");
                        $("#total_sales_amount").val("")
                        return
                    }
            }
            else{
                $("#alert_modal_body").html(gettext("油站总销售额不能为空！"));
                $("#alert_modal").modal("show");
            }

            if(rank !=""){
                if(rank.match(/\D/)){
                    $("#alert_modal_body").html(gettext("排名为整数！"));
					$("#alert_modal").modal("show");
                    $("#rank").val("")
                    return
                }
            }

            if(group_info ==""){
                $("#alert_modal_body").html(gettext("群描述不能为空！"));
                $("#alert_modal").modal("show");
                return
            }

            dict = {
                'group_name':group_name,
                'group_location':JSON.stringify(group_location),
                'total_sales_amount':total_sales_amount,
                'rank':rank,
                'group_info':group_info
            }
            $.get("/gcustomer/ajax/create_station_group/",dict,
                function(data){
                    if(data.ret != "0001"){
                        $("#alert_modal_body").html(gettext("创建失败！"));
					    $("#alert_modal").modal("show");
                        return
                    }
                    $("#alert_modal_body").html(gettext("创建成功！"));
					$("#alert_modal").modal("show");
                    $("#group_name").val("")
                    $("#shicode").val("")
                    $("#shengcode").val("")
                    $("#total_sales_amount").val("")
                    $("#rank").val("")
                    $("#group_info").val("")
                },"json")
        })

        //初始化行政区划
        if ($("#shengcode").length != 0){
            init_china_location();
        }
});

//初始化行政区划
function init_china_location(){

    var url_prefix = "gcustomer/";/*$('meta[name="url_prefix"]').attr('content');*/
    ////取得省份的信息
    $.post('/'+url_prefix+'ajax/get_china_location/',{'parent':0,'level':1},function(data){
        //判断返回值是否正确
         if (data.ret!="0001"){
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
            $("#alert_modal_body").html(gettext("请选择省份！"));
            $("#alert_modal").modal("show");
            return
        }
        //取出url地址
        var url_prefix = "gcustomer/";/*$('meta[name="url_prefix"]').attr('content');*/
        var parent = $('#shengcode').val()

        //通过ajax请求取得城市的信息
        $.post('/'+url_prefix+'ajax/get_china_location/',
           {"parent":parent,"level":2},
            function(data){

                //判断返回值是否正确
                if (data.ret!="0001"){
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
            $("#alert_modal_body").html(gettext("请选择市级信息！"));
            $("#alert_modal").modal("show");
            return
        }
        //取出url地址
        var url_prefix = "gcustomer/" /*$('meta[name="url_prefix"]').attr('content');*/
        var parent = $('#shicode').val()

        //通过ajax请求取得区县的信息
        $.post('/'+url_prefix+'ajax/get_china_location/',
           {"parent":parent,"level":3},
            function(data) {

                //判断返回值是否正确
                if (data.ret!="0001"){
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


/* 已有油站群 */
$(function(){
    $('#the_station_group_details').hide()
    $('#myModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget) // Button that triggered the modal
        var name = button.data("name") // Extract info from data-* attributes
        var range = button.data("range")
        var sales = button.data("sales")
        var rank = button.data("rank")
        var description = button.data("description")
        var modal = $(this)
        modal.find('.modal-title').html(name)
        modal.find("#range").html(gettext("油站范围：") + range)
        modal.find("#sales").html(gettext("油站总销售额：") + sales)
        modal.find("#rank").html(gettext("油站排名：") + rank)
        modal.find("#description").html(gettext("油站群描述：") + description)
    });
    $("#group_search").on('click',function(){
        group_name = $("#staion_group_search").val()
        $.get("/gcustomer/ajax/get_station_group_info/",{"group_name":group_name},
            function(data){
                if(data.ret != "0001"){
                    $("#alert_modal_body").html(gettext("没有相关油站群"));
					$("#alert_modal").modal("show");
                    $("#the_station_group_details").hide()
                }
                $("#the_station_group_details").show()
                $("#station_group_submary").empty()
                if(data.objs.length == 0){
                    $("#station_group_submary").append("<tr><th colspan='6' style='text-align:center;'>暂无数据</th></tr>")
                    return
                }
                $("#station_group_submary").empty()
                i = 0
                $(data.objs).each(function(){
                    var obj = this
                    $("#station_group_submary").append(String.format(''+
                        '<tr>'+
                            '<td>{0}</td>'+
                            '<td>{1}</td>'+
                            '<td>{2}</td>'+
                            '<td>{3}</td>'+
                            '<td><button class="station-group-details">查看</button></td>'+
                            '<td><button class="station-list">查看</button></td>'+
                            '<td><button class="station-group-delete">删除</button></td>'+
                        '</tr>'+
                    '',i+1,obj.group_name,obj.group_creator,obj.time))
                    i++
                })

                //绑定button事件
                $("button.station-group-details").on('click',function(){
                    $("#stationGroupModal").modal("show");
                    $(".modal-body").find('table').empty();
                    $("#groupStationModalLabel").empty();
                    station_group_name = $($(this).parent().parent().find("td")[1]).html().trim();
                    var data = {'station_group_name':station_group_name};
                    $.get("/gcustomer/ajax/get_station_group_detail/", data, function (data) {
                        if(data.ret == "0001"){
                            var obj = data.obj;
                            var group_name = obj.group_name;
                            var group_location = obj.group_location;
                            var total_sales_amount = obj.total_sales_amount;
                            var rank = obj.rank;
                            var group_info = obj.group_info;
                            var group_create_time = obj.time;
                            var group_creator = obj.group_creator;
                            $(".modal-title").append(String.format(''+
                                    gettext("油站群名称")+'：{0}',group_name
                            ))
                            $("#stationgroupdetail").append(String.format(''+
                                '<tr>'+
                                    '<td>创建者：</td>'+
                                    '<td>{0}</td>'+
                                '</tr>' +
                                '<tr>'+
                                    '<td>创建时间：</td>'+
                                    '<td>{1}</td>'+
                                '</tr>'+
                                '<tr>'+
                                    '<td>总销售额：</td>'+
                                    '<td>{2}</td>'+
                                '</tr>'+
                                '<tr>'+
                                    '<td>油站排名：</td>'+
                                    '<td>{3}</td>'+
                                '</tr>'+
                                '<tr>'+
                                    '<td>油站群范围：</td>'+
                                    '<td>{4}</td>'+
                                '</tr>'+
                                '<tr>'+
                                    '<td>油站群描述：</td>'+
                                    '<td>{5}</td>'+
                                '</tr>' + '',
                                group_creator, group_create_time, total_sales_amount, rank, group_location, group_info
                            ))
                        }
                        else if(data.ret != "0001"){
                            $("#alert_modal_body").html("error");
	    		 		    $("#alert_modal").modal("show");
                        }
                    }, "json")

                })

                $("button.station-list").on('click',function(){
                        station_group_name = $($(this).parent().parent().find("td")[1]).html().trim();
                    var data = {'station_group_name':station_group_name};
                    $.get("/gcustomer/ajax/get_station_group_detail/", data, function (data) {
                        if(data.ret == "0001"){
                            var obj = data.obj;
                            var station_list = obj.station_list;
                            station_list_string = ""
                            for(var i =0,len=station_list.length;i<len;i++){
                                    station_list_string = station_list_string  + station_list[i] + "\n"
                            }
                            $("#alert_modal_body").html(station_list_string);
					        $("#alert_modal").modal("show");
                        }
                        else if(data.ret != "0001"){
                            $("#alert_modal_body").html("error");
					        $("#alert_modal").modal("show");
                        }
                    }, "json")
                })

                $("button.station-group-delete").on('click',function(){
                    group_name = $($(this).parent().parent().find("td")[1]).html().trim()
                    $(this).parent().parent().remove()
                    $.get("/gcustomer/ajax/delete_station_group/",{"group_name":group_name},
                        function(data){
                            if(data.ret != "0001"){
                                $("#alert_modal_body").html(gettext("删除失败"));
                                $("#alert_modal").modal("show");
                            }
                            $("#group_search").click()
                        },"json")
                })

            },"json")

    })
});
