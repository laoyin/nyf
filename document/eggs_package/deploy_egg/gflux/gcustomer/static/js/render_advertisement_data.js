$(function(){
	//dom ready
	if($('#advert-list').length != 0){
		//get advertisement list
	 //缓冲提示
        	$.blockUI({"message":gettext("正在加载...")});
	$.get('/gcustomer/ajax/get_advertisement_list/',{},function(data){
                    if(data.ret !="0001"){
						$("#alert_modal_body").html(gettext("当前没有在播广告！"));
                        $("#alert_modal").modal("show");
                        return
                    }
                    $.blockUI({"message":gettext("加载完成")});
            	       $.unblockUI();
                    $("#advert-list").empty()
                    advet_str=''+
                    	'<li class="item">'+
            			'<div style="float:left;">'+
                            		'<img src="/gcustomer/ajax/render_image?name={2}" width=100px height=100px style="position: absolute;"/>'+
                        		'</div>'+
            			'<div class="detail" style="float:left;">'+
                    		'<h4>{0}</h4>'+
                    		'<div sha1="{3}">'+
                    			'<span class="glyphicon glyphicon-remove" aria-hidden="true" style="cursor:pointer;position:relative;left:600px;top:-30px;" title="删除">'+
                    			'</span>'+
                    		'</div>'+
                    		'{1}'+
                		'</div>'+
                		'<div style="clear:both"></div>'+
						'</li>'+
            			''
                    for(var i=0 ; i<data.obj.length ;i++){
                    	$("#advert-list").append(String.format(advet_str,data.obj[i].name,data.obj[i].abstract,data.obj[i].image_name,data.obj[i].sha1))
                    	item_class_opt=".item-"+(i+1)+"-1"
                    	//image_url=data.obj[i].image_src
                    	//url=String.format('url(http://127.0.0.1:8000{0})',image_url)
                    	//$(item_class_opt).css('background-image',url)
                    }

                    //删除广告
              $("span.glyphicon-remove").on('click', function () {
		var sha1 = $(this).parent().attr("sha1");
		var ad_item = $(this).parents('.item');
		var params = {'sha1':sha1};
		if(confirm(gettext("确定要删除吗？"))){
				$.post("/gcustomer/ajax/delete_advertisement/", params, function (data) {
				if(data.ret == '0001'){
					ad_item.remove();
				}
				else if(data.ret != '0001'){
					$("#alert_modal_body").html(data.info);
					$("#alert_modal").modal("show");
				}
			}, 'json');
		}
		else {
			return
		}
	})
                },'json');
	}
	//render advertisement Panel
	if($("#advert_count_panel").length !=0){
	//get advertisement list
	 $.get('/gcustomer/ajax/get_advertisement_list/',{},function(data){
                    if(data.ret !='0001'){
						$("#alert_modal_body").html(gettext("当前没有在播广告！"));
				     	$("#alert_modal").modal("show");
                        return
                    }
                    $("#advert_count_panel").empty()
                	for(var i=0;i<data.obj.length;i++){
                    $('#advert_count_panel').append(String.format(''+
                    	'<div class="col-lg-4" style="margin-top:5px;">'+
	                    	'<div class="item"  onclick="get_advertisement_information()">'+
	                    	'<a name="/gcustomer/ajax/get_advertisement_information" href="#">{0}</a>'+
	                    	'</div>'+
                    	'</div> ',data.obj[i].title))
                }
                },'json');
	}
	//render advertisement Panel
	if($("#advert_convert_panel").length !=0){
		//get advertisement list
		$.get('/gcustomer/ajax/get_advertisement_list/',{},function(data){
                    if(data.ret !='0001'){
						$("#alert_modal_body").html(gettext("当前没有在播广告！"));
					    $("#alert_modal").modal("show");
                        return
                    }
                    $("#advert_convert_panel").empty()
                	for(var i=0;i<data.obj.length;i++){
                    $('#advert_convert_panel').append(String.format(''+
                    	'<div class="col-lg-4" style="margin-top:5px;">'+
                    	'<div class="item" onclick="get_advertisement_information()">'+
                    	'<a name="/gcustomer/ajax/get_advertisement_information" href="#">{0}</a>'+
                    	'</div>'+
                    	'</div> ',data.obj[i].title))
                }
                },'json');
	}
})
//get advertisement information
function get_advertisement_information(){
        var url=$(window.event.srcElement)
        $.get(''+url.attr('name')+'',{'name':url.html()},
            function(data){
                if(data.ret !='0001'){
					$("#alert_modal_body").html(data.info);
					$("#alert_modal").modal("show");
                    return
                }
		$("#the_advert_visited_count").show()
		$("#the_advert_visited_map").show()
		$("#the_advert_convert_count").show()
        		$("#the_advert_convert_map").show()
        		$("#advert_visited_map").show()
        		$("#advert_visited_map").hide()
        		$("#advert_convert_map").hide()
        		$("#the_advertisement_information_list").hide()
        		$("#the_launch_advertisement_information").hide()

				advert_name=data.obj[0].name
				$("#current_advertisement").html("");
				$("#current_advertisement").html(data.obj[0].title);
				if($("#advert_visited_count").length !=0){
					$('#advert_visited_count').highcharts({
						                chart: {
						                    type: 'line'
						                },
						                title: {
						                    text: gettext('所有投放广告最近一个月的访问量')
						                },
						                credits: {
					                             	enabled: false
				                        		  },
						                subtitle: {
						                    text: ''
						                },
						                xAxis: {
						                    categories: data.advertisement_dash.count.categories
						                },
						                yAxis: {
						                    title: {
						                        text: gettext('访问量')
						                    }
						                },
						                tooltip: {
						                    enabled: false,
						                    formatter: function() {
						                        return '<b>'+ this.series.name +'</b><br/>'+this.x +': '+ this.y +'°C';
						                    }
						                },
						                plotOptions: {
						                    line: {
						                        dataLabels: {
						                            enabled: true
						                        },
						                        enableMouseTracking: false
						                    }
						                },
						                series: [{
						                    name: advert_name,
						                    data: data.advertisement_dash.count.data
						                }]
						            });
				}


				if($("#advert_convert_count").length !=0){
					$('#advert_convert_count').highcharts({
							            chart: {
							                type: 'column'
							            },
							            title: {
							                text: gettext('所有广告转化销量统计图')
							            },
							            credits: {
						                             enabled: false
						                        },
							            subtitle: {
							                text: ''
							            },
							            xAxis: {
							                categories: data.advertisement_dash.count.categories
							            },
							            yAxis: {
							                min: 0,
							                title: {
							                    text: gettext('RMB(万元)')
							                }
							            },
							            tooltip: {
							                headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
							                pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
							                        '<td style="padding:0"><b>万</b></td></tr>',
							                footerFormat: '</table>',
							                shared: true,
							                useHTML: true
							            },
							            plotOptions: {
							                column: {
							                    pointPadding: 0.3,
							                    borderWidth: 0
							                }
							            },
							            series: [{
							                name: advert_name,
							                data: data.advertisement_dash.count.data
							            }]
							        });
				}

		},"json");
}
    

function get_back () {
	$("#the_advert_visited_count").hide();
	$("#the_advert_visited_map").hide();
	$("#the_advertisement_information_list").show();
	$("#the_advert_convert_count").hide();
	$("#the_advert_convert_map").hide();
	$("#the_launch_advertisement_information").show();
}
