/*
 *
 * Load data and render dashlet
 * Rely on: jquery, jquery.blockUI highcharts
 **/

var cachedDash = {};
var healthStatus = ['瓶颈','重复客户率','客单值','92/93#平均单车加油量','95/97#平均单车加油量','高峰期油枪效率','92/93#加满率','95/97#加满率','柴油加满率','日常油非转化率','高峰期油非转化率','非油品相关性']
var healthStatusValue = [0,40,20,20,35,5,50,60,70,8,5,5,5]
var healthStatusScope = ['无','瘦弱:<40%;良好:40%-60%;强壮:>60%','瘦弱:<20元;良好:20-100元;强壮:>100元','瘦弱:<20升;良好:20升-40升;强壮:>40升',
                         '瘦弱:<35升;良好:35升-60升;强壮:>60升','瘦弱:<5分钟;良好:5-8分钟;强壮:>8分钟','瘦弱:<50%;良好:50%-60%;强壮:>60%',
                         '瘦弱:<60%;良好:60%-70%;强壮:>70%','瘦弱:<70%;良好:70%-90%;强壮:>90%','瘦弱:<5%;良好:5%-10%;强壮:>10%',
                         '瘦弱:<8%;良好:8%-12%;强壮:>12%','瘦弱:<0种;良好:5-8种;强壮:>8种','瘦弱:<0种;良好:5-8种;强壮:>8种'
                        ]
$('#id_health_status_y').find("option[value='2']").attr("selected",true);
function jsonToMultitable(json,dashletID, title) {

  $("#"+dashletID).html("<table class='table table-hover table-bordered table-striped table-condensed table-responsive'>"+
                              "<thead id='table_title'>"+
                              "</thead>"+
                              "<tbody id='table_value'>"+
                              "</tbody>"+
                        "</table>"
                        )
  table_title_obj = json.dataset[0];
  $("#table_title").append(String.format(
        "<tr>" +
          "<th>{0}</th>" +
          "<th>{1}</th>" +
          "<th>{2}</th>" +
          "<th>{3}</th>" +
        "</tr>"
    ,table_title_obj.station_name,table_title_obj.data[0].title,table_title_obj.data[0].value,table_title_obj.data[0].status));

  table_body_obj_list = json.dataset.slice(1,json.dataset.length)
  $(table_body_obj_list).each(function(){
      table_body_data_obj = $(this)[0]
      station_name = table_body_data_obj.station_name;
      first_table_body_data_obj = table_body_data_obj.data[0];
      $("#table_value").append(String.format(''+
          '<tr>'+
            '<td rowspan="13" width="20%" onclick=signalSiteLook("{0}")>{0}</td>'+
            '<td>{1}</td>'+
            '<td>{2}</td>'+
            '<td>{3}</td>'+
          '</tr>'
        ,station_name,first_table_body_data_obj.title,first_table_body_data_obj.value,healthStatusScope[first_table_body_data_obj.type]));

      other_table_body_obj_list = table_body_data_obj.data.slice(1,table_body_data_obj.data.length);
      $(other_table_body_obj_list).each(function(){
          obj = $(this)[0];
          $("#table_value").append(String.format(''+
            '<tr>'+
            '<td>{0}</td>'+
            '<td>{1}</td>'+
            '<td>{2}</td>'+
          '</tr>'
        ,obj.title,obj.value,healthStatusScope[obj.type]));
      });

  });
}

function jsonToTable(json, title) {
  var table = new Array(json.categories.length + 1);
  table[0] = new Array();
  table[0].push(title);
  $.each(json.categories, function(i, category) {
    table[i + 1] = new Array();
    table[i + 1].push(category);
  });

  $.each(json.dataset, function(i, data) {
    table[0].push(data['name']);
    $.each(data['data'], function(j, value) {
      table[j + 1].push(value);
    });
  });

  var html = "<table class='table table-hover table-bordered table-striped table-condensed table-responsive'><thead><tr>";
  html += "<th width='35%' class='active'>" + table[0][0] + "</th>";
  $.each(table[0].slice(1), function(i, value) {
    html += "<th>" + value + "</th>";
  });
  html += "</tr></thead><tbody>";

  $.each(table.slice(1), function(i, data) {
    html += "<tr>";
    html += "<th>" + data[0] + "</th>";
    $.each(data.slice(1), function(j, value) {
      html += "<td>" + value + "</td>";
    });
    html += "</tr>";
  });

  html += "<tbody></table>";
  return html;
}

function renderDash(dashlet, renderer, action, params, forceReload, opts) {
    var title = dashlet.attr('dash-label') || '';
    var commonOpts = {
        chart: {
            defaultSeriesType: "spline",
            animation: true
        },
        yAxis: {
            //设置图表纵坐标的间隔为50px
            tickPixelInterval:20,
            title: "",
            min: 0,
            labels: {
                formatter:function(){
                    return this.value;
                },
            }
        },
        credits: {
            "enabled": false
        },
        plotOptions: {
            "area":{
                "stacking": null
            },
            "series":{
                animation: true,
                events: {
                  legendItemClick: function(event) {
                    var legendName = this.name+'_<dot>';
                    var tempSeries = this.chart.series;
                    var seriesLength = tempSeries.length;
                    for (var i=0; i < seriesLength; i++){
                      if (tempSeries[i].name == legendName){
                        tempSeries[i].visible ? tempSeries[i].hide() : tempSeries[i].show();
                      }
                    }
                  }
                }
            }
        },
       /* tooltip: {
            enabled: true,
            formatter: function() {
              if (this.point.name) { // the pie chart
                return '' + this.point.name + ' : ' + this.y;
              } else {
                return '' + this.x + ' : '+ this.y;
              }
            }
        },*/
        legend: {
            margin: 25,
            enabled: true
        },
        subtitle: {}
    };



    var dashletID = dashlet.attr('id');
    var cacheID = 'dash#' + dashletID;
    $.each(params, function(i, n){
        if(n < 0) // fix a wierd bug regarding negative integer
          n = n + '$';
        cacheID += '_' + i + ':' + n;
    });

    // do nothing if the cache is hit
    var cachedOpts = dashlet.data(cacheID);
    var colors=dashlet.data(cacheID+"_color");
    if (!forceReload && cachedOpts != null) {
        Highcharts.getOptions().colors=colors
        // FIXME: memory leaks possible ?
        if(renderer == "table") {
          var cachedJSON = dashlet.data(cacheID + "_rawdata");
          $('#' + dashletID).html(jsonToTable(cachedJSON, title));
        } else if(renderer == "chart"){
           // chart is the default renderer
          try{
            cachedDash[cacheID].destroy();
          } catch(error) {}
          cachedDash[cacheID] = new Highcharts.Chart($.extend(true, {}, commonOpts, cachedOpts));
        }
        //dashlet.trigger('chart_data_loaded', dashlet.data(cacheID + '_rawdata'));
        return;
    }

    // Loading data
    var categories = [];
    var series = [];
    var dashCanvas = dashlet;
    var  tooltip =  {
                                        enabled: true,
                                        formatter: function(){}
                            }
    // TODO: remove hard-coded url prefix '/dash/' from here
    var loading_img = $("<img src='/gflux/static/images/ajax-loader.gif'/>");
    dashCanvas.block({
        message: loading_img,
        css:{
            width:'32px',
            border:'none',
            background: 'none'
        },
        overlayCSS:{
            backgroundColor: '#FFF',
            opacity: 0.8
        },
        baseZ:997
    });

    $.getJSON(action, params, function(json){

//渲染3d鸟瞰图
                if(json.opts){
                    if(json.dataset.data!=undefined){
                           if(json.dataset.data.length == 0){
                                alert("请在油枪分组里面设置站点通道列道")
                                $("#"+dashletID).html("暂无数据")
                                return
                           }
                     }
                                   if (json.opts.chart.type == "threedimensionaldash"){
                                          $("#"+dashletID).parent().parent().siblings().find("button[renderer='table']").hide()
                                          $("#"+dashletID).parent().parent().siblings().find("button[id='export']").hide()
                                          $("#"+dashletID).html("<div><canvas id = 'canvas4' width='540' height='540'></canvas></div>")
                                         var cx4 = new CanvasXpress("canvas4",
                                          {
                                          "z" : {
                                            "Annt1" : ["Desc:1", "Desc:2", "Desc:3", "Desc:4"],
                                            "Annt2" : ["Desc:A", "Desc:B", "Desc:A", "Desc:B"],
                                            "Annt3" : ["Desc:X", "Desc:X", "Desc:Y", "Desc:Y"],
                                            "Annt4" : [5, 10, 15, 20],
                                            "Annt5" : [8, 16, 24, 32],
                                            "Annt6" : [10, 20, 30, 40]
                                          },
                                          "x" : {
                                            "Factor1" : ["Lev:1", "Lev:2", "Lev:3", "Lev:1", "Lev:2", "Lev:3"],
                                            "Factor2" : ["Lev:A", "Lev:B", "Lev:A", "Lev:B", "Lev:A", "Lev:B"],
                                            "Factor3" : ["Lev:X", "Lev:X", "Lev:Y", "Lev:Y", "Lev:Z", "Lev:Z"],
                                            "Factor4" : [5, 10, 15, 20, 25, 30],
                                            "Factor5" : [8, 16, 24, 32, 40, 48],
                                            "Factor6" : [10, 20, 30, 40, 50, 60]
                                          },
                                          "y" : {
                                            "vars" : json.dataset.vars,/*["Variable1", "Variable2", "Variable3", "Variable4"],*/
                                            "smps" : json.dataset.smps, /*["Sample1", "Sample2", "Sample3", "Sample4", "Sample5", "Sample6"],*/
                                            "data" :json.dataset.data,/* [[5, 10, 25, 40, 45, 50], [95, 80, 75, 70, 55, 40], [25, 30, 45, 60, 65, 70], [55, 40, 35, 30, 15, 1]],*/
                                            "desc" : ["油枪效率", "Magnitude2"]
                                          },
                                          "a" : {
                                            "xAxis" : ["Variable1", "Variable2"],
                                            "xAxis2" : ["Variable3", "Variable4"]
                                          },
                                          "t" : {
                                            "vars" : "(((Variable1,Variable3),Variable4),Variable2)",
                                            "smps" : "(((((Sample1,Sample2),Sample3),Sample4),Sample5),Sample6)"
                                          }
                                            },
                                          {"bar3DInverseWeight": 1.2,
                                           "graphType": "Bar",
                                           "is3DPlot": true,
                                           "scatterType": "bar",
                                           "x3DRatio": 0.5
                                          }
                                          );

                                        return
                                    }
                                  else if(json.opts.chart.type == "profile_dash"){
                                        $("#"+dashletID).parent().parent().siblings().find("button[renderer='table']").hide()
                                        $("#"+dashletID).parent().parent().siblings().find("button[id='export']").hide()
                                        $("#"+dashletID).html("<div id = 'container'></div>")
                                        $('#container').highcharts({
                                                    chart: {
                                                        type: 'bubble',
                                                        zoomType: 'xy'
                                                    },
                                                    credits: {
                                                               enabled: false
                                                     },
                                                    title: {
                                                      text: json.dataset.dash_title
                                                    },
                                                    yAxis: {
                                                        plotLines:[{
                                                            color:'red',           //线的颜色，定义为红色
                                                            dashStyle:'solid',     //默认值，这里定义为实线
                                                            value:healthStatusValue[json.opts.chart.y],               //定义在那个值上显示标示线，这里是在x轴上刻度为3的值处垂直化一条线
                                                            width:2,                //标示线的宽度，2px
                                                            label:{
                                                                text:'好',     //标签的内容
                                                                align:'right',                //标签的水平位置，水平居左,默认是水平居中center
                                                                style:{
                                                                    color:'red'
                                                                }
                                                            }
                                                        }],
                                                        title: {
                                                            text: healthStatus[json.opts.chart.y]
                                                        },
                                                        labels:{
                                                            enabled :true
                                                        },
                                                    },
                                                    tooltip: {
                                                            enabled :true
                                                        },
                                                    xAxis: {
                                                        plotLines:[{
                                                            color:'red',            //线的颜色，定义为红色
                                                            dashStyle:'solid',//标示线的样式，默认是solid（实线），这里定义为长虚线
                                                            value:healthStatusValue[json.opts.chart.x],                //定义在那个值上显示标示线，这里是在x轴上刻度为3的值处垂直化一条线
                                                            width:2,                 //标示线的宽度，2px
                                                            label:{
                                                                text:'好',     //标签的内容
                                                                align:'right',                //标签的水平位置，水平居左,默认是水平居中center
                                                                style:{
                                                                    color:'red'
                                                                }
                                                            }
                                                        }],
                                                        title: {
                                                            text: healthStatus[json.opts.chart.x]
                                                        }
                                                    },
                                                    series: json.dataset.series
                                        });
                                        return
                                  }
                 }

   //有说明标识，重新设置提示参数
  if(json.dataset.length>0){
      if(json.tip=='有瓶颈'){
          title='性能瓶颈（有瓶颈）'
      }else if(json.tip=='无瓶颈'){
          title='性能瓶颈（无瓶颈）'
      }
      if (json.dataset[0].flag!=undefined) {
          /*commonOpts.*/tooltip.formatter = function(){

           //获取总的series
            var seriesObjs = this.series.chart.series;
            //当前series
            var curSeries = this.series;
            //所在series数组内的序号
            var index = -1;
            //通过for查找当前series所在序号
            for(var i = 0;i<seriesObjs.length;i++)
            {
                if(curSeries.name == seriesObjs[i].name)
                {
                   index = i;
                    break;
                }
            }
            if (this.point.name) { // the pie chart
              return '' + this.point.name + ' : ' + this.y+' '+json.dataset[index].flag[this.x];
            } else {
              return '' + this.x + ' : '+ this.y+' '+json.dataset[index].flag[this.x];
            }
          }
      }
      else{

         /*commonOpts.*/tooltip.formatter = function(){
                if (this.point.name) { // the pie chart
                              return '' + this.point.name + ' : ' + this.y;
                } else {
                              return '' + this.x + ' : '+ this.y;
                }
         }
      }
}



        //如果有高峰期信息，将其缓存供总体出油效率使用
        if(json.period_value){
            window.period_key=json.period_key
            window.period_value=json.period_value
            console.log('缓存高峰期信息'+json.period_key)
        }

        if(lazy_dash_loaders.length){
            console.log('执行惰性加载。。。')
            var that=lazy_dash_loaders.shift();
            if($(that).attr('type')=='submit'){
                $(that).click()
            }else{
                $(that).children().eq(0).click()
            }
        }

        if(typeof(json.cache_ret)!='undefined'){
            if(json.cache_ret==0){
                alert(gettext('后端数据正在计算之中，请十分钟之后再试！'))
                return
            }
        }

        //数据正确返回
        if(json.status == 'OK') {
            //整理统计步长名
            $.each(json.categories, function(i, category) {
                categories[i] = category;
            });

            //整理曲线数据
            $.each(json.dataset, function(i, data) {

                //当前曲线需要上色处理
                //高峰期效果图
                if(data['render_period_color']){
                    var period_value=null

                    //首选服务器端返回的高峰期
                    if(json.period_value){
                        period_value=json.period_value
                        console.log('服务器端自带高峰期信息'+json.period_key)
                    }
                    //尝试使用客户端缓存高峰期
                    else if(window.period_key==json.period_key){
                        period_value=window.period_value
                        console.log('使用客户端的高峰期信息'+json.period_key)
                    }
                    else{
                        alert('当前图表需要高峰期时段定义信息，请先访问高峰期时段定义图表！')
                    }

                    //开始渲染
                    if(period_value){
                        //获取各个时段的值
                        crest=period_value['crest']
                        valley=period_value['valley']
                        high=period_value['high']
                        low=period_value['low']
                        datalength=data['data'].length

                        color_count=[]

                        //存取每个点的颜色,0:高峰 1:低谷 2:上升 3:下降
                        for(var i=0;i<datalength;i++){
                            if(crest.indexOf(i)>=0){
                                color_count.push(0)
                            }else if(valley.indexOf(i)>=0){
                                color_count.push(1)
                            }else if(high.indexOf(i)>=0){
                                color_count.push(2)
                            }else{
                                color_count.push(3)
                            }
                        }

                        //步长
                        var step_count=1/24
                        series.push($.extend({visible: true}, data));
                        var colors = ['red', 'green', '#a020f0','blue'];
                        var stops=[]
                        var step=0

                        //颜色渐变
                        for(var i=0;i<24;i++){
                            var stop=[]
                            stop.push(step)
                            if(color_count[i]==0){
                                stop.push(Highcharts.Color(colors[0]).setOpacity(1).get('rgba'))
                            }else if(color_count[i]==1){
                                stop.push(Highcharts.Color(colors[1]).setOpacity(1).get('rgba'))
                            }
                            else if(color_count[i]==2){
                                stop.push(Highcharts.Color(colors[2]).setOpacity(1).get('rgba'))
                            }else if(color_count[i]==3){
                                stop.push(Highcharts.Color(colors[3]).setOpacity(1).get('rgba'))
                            }
                            stops.push(stop)
                            step+=step_count
                        }

                        //横向颜色渐变
                        Highcharts.getOptions().colors = Highcharts.map(colors, function (color) {
                            return {
                                linearGradient: { x1: 0, y1: 0, x2: 1, y2: 0 },
                                stops: stops
                            };
                        });
                    }
                }


                //当前曲线需要点击事件处理
                //多站效果图
                else if(data['location_id']){
                    data['events']={
                        click:function(){
                            var exists=$('select[name="china_location"]').find('option[value="'+data['location_id']+'"]')
                            if(exists.length){
                                exists.prop('selected',true)
                            }else{
                                var new_location_option=new Option(data['name'],data['location_id'])
                                $('select[name="china_location"]')
                                    .append(new_location_option)
                                $(new_location_option).prop('selected',true)
                            }
                            $('.dash-top-form').find('button[type="submit"]').click()
                        }
                    }
                    Highcharts.getOptions().colors = ["#2f7ed8", "#0d233a", "#8bbc21", "#910000", "#1aadce", "#492970", "#f28f43", "#77a1e5", "#c42525"]
                    series.push($.extend({visible: true}, data));
                }

                //其他默认处理方法
                else{
                    Highcharts.getOptions().colors = ["#2f7ed8", "#0d233a", "#8bbc21", "#910000", "#1aadce", "#492970", "#f28f43", "#77a1e5", "#c42525"]
                    series.push($.extend({visible: true}, data));
                }
            });

            //整合后端返回的曲线扩展选项
            if(json.extra != undefined) {
              $.each(json.extra, function(i, data) {
                series.push($.extend({visible: true}, data));
              });
            }

            opts = $.extend(opts || {}, json.opts || {});

            //数据中有平均线数据
            //将其渲染出来
            if(json.avrg){
                // initialize options
                var avrg=json.avrg
                var options = $.extend(true, {
                    chart: {
                        renderTo: dashletID
                    },
                    title: {
                        text: title
                    },
                    xAxis: {
                        categories: categories,
                        labels:{
                            align:"right",
                            rotation:-45,
                            step: parseInt(categories.length / 10)
                        }
                    },
                    yAxis: {
                        plotLines: [{
                            value: avrg,
                            width: 2,
                            color: 'red',
                            label:{
        			               text:avrg,
        			               align:'left',
                                   style:{
                                       color:'red'
                                   }
    			             }
                        }]
                        },
                    series: series
                }, opts);
            }

            //当前曲线需要点击事件处理
            //多站最后一层,跳转到单站
            else if(json.go_to_simple){
                // initialize options
                var options = $.extend(true, {
                    chart: {
                        renderTo: dashletID
                    },
                    title: {
                        text: title
                    },
                    xAxis: {
                        categories: categories,
                        labels:{
                            align:"right",
                            rotation:-45,
                            step: parseInt(categories.length / 10)
                        }
                    },
                    plotOptions: {
                        series: {
                            cursor: 'pointer',
                            point: {
                                events: {
                                    click: function (event) {
                                        var site_name=this.series.options.site_name
                                        var current_date=this.category
                                        $.cookie('site-select',site_name,{path: '/' })
                                        $.cookie('date-select',current_date,{path: '/' })
                                        location.href=url_prefix+'station_portal'
                                    }
                                }
                            }
                        }
                    },
                    series: series
                }, opts);
            }

            //默认其他选项
            else{
                // initialize options
                var options = $.extend(true, {
                    chart: {
                        renderTo: dashletID
                    },
                    title: {
                        text: title
                    },
                    xAxis: {
                        categories: categories,
                        labels:{
                            align:"right",
                            rotation:-45,
                            step: parseInt(categories.length / 10)
                        }
                    },
                    series: series,
                    tooltip: tooltip
                }, opts);
            }

            //缓存数据
            dashlet.data(cacheID, options);
            dashlet.data(cacheID + '_rawdata', json);
            dashlet.data(cacheID + '_color', Highcharts.getOptions().colors);

            //开始绘图
            if(renderer == "table") {
              if(json.opts.chart.type == "multi_table") {

                  jsonToMultitable(json,dashletID,title);
              }
              else{
                  $('#' + dashletID).html(jsonToTable(json, title));
              }

            }else { // chart is the default renderer
              // destroy existing chart
              if ( cachedDash[cacheID] != undefined ){
                try{
                  cachedDash[cacheID].destroy();
                }catch(error){}
              }
              // create chart
              cachedDash[cacheID] = new Highcharts.Chart($.extend(true, {}, commonOpts, options));
            }
            //dashlet.trigger('chart_data_loaded', json);
        }
        dashCanvas.unblock();
    });
    /*if("#"){
        renderAerialView()
    }*/
}

function flushDash(){
  cachedDash = {};
}

function buildParams(form) {
  var params = {};
  $('.dash-top-form').find('.dash-control').each(function() {
     if($(this).attr('name')){
        params[$(this).attr('name')] = $(this).val();
    }
  });
  form.find('.dash-control').each(function() {
    if($(this).attr('name')){
        params[$(this).attr('name')] = $(this).val();
    }
  });
  return params;
}

$(function() {
  window.lazy_dash_loaders=[]

  function submit(form, index) {
    var action = form.attr('action');
    var params = buildParams(form);
    var dashlet = form.parents('.dash-header').next('div').children('.dash-body').children().eq(index);
    var opts = {};
    var renderer = form.find('.dash-renderer.btn-info').attr('renderer');
    renderDash(dashlet, renderer, dashlet.attr('report-url') || action, params, false, opts);
  }

  $('.dash-tab').on('click', function(e) {
    e.preventDefault();
    $(this).parent().children('.btn-primary').removeClass('btn-primary').addClass('btn-default');
    var dashBody = $(this).parent().next('div');
    dashBody.children(':visible').hide();
    dashBody.children().eq($(this).index()).show();
    $(this).addClass('btn-primary');
    submit($(this).parents('.dash').find('.dash-form'), $(this).index());
  });

  $('.dash-fold').on('click', function(e) {
    e.preventDefault();
    var panelBody = $(this).parents('.dash').find('.panel-body');
    if($(this).hasClass('glyphicon-chevron-down')) {
      $(this).removeClass('glyphicon-chevron-down').addClass('glyphicon-chevron-up');
      panelBody.hide();
    } else {
      $(this).removeClass('glyphicon-chevron-up').addClass('glyphicon-chevron-down');
      panelBody.show();
    }
  });

  $('.dash-resize-full').on('click', function(e) {
    e.preventDefault();
    var params = buildParams($(this).parent());
    window.open($(this).attr('dash-url') + '?' + serialize(params));
  });

  $('.dash-renderer').on('click', function(e) {
    e.preventDefault();
    $(this).parent().children('.btn-info').removeClass('btn-info').addClass('btn-default');
    $(this).addClass('btn-info');
    $(this).parent().parent().find('.dash-submit').click();
  });

  $('.dash-submit').on('click', function(e) {
    e.preventDefault();
    var index = $(this).parents('.dash-header').next('div').find('.dash-tab.btn-primary').index();
    submit($(this).parents('.dash-form'), index);
  });

  $('.dash-top-submit').on('click', function(e) {
    e.preventDefault();
    $('.dash-submit').each(function(i,n) {
        //如果是高峰期视图,需要先确保高峰期时段返回之后
        //再执行其他操作
        if($('#sidebar').find('a.active').attr('href')){
            if($('#sidebar').find('a.active').attr('href').endWith('station_peak_period_page')){
                if(i>0){
                    lazy_dash_loaders.push(this)
                    return
                }else{
                    return
                }
            }
      }

      $(this).click();

    });

    //如果是高峰期视图,需要先确保高峰期时段返回之后
    //再执行其他操作
    if($('#sidebar').find('a.active').attr('href')){
        if($('#sidebar').find('a.active').attr('href').endWith('station_peak_period_page')){
            $('.dash-submit').eq(0).click()
        }
    }

  });

  $(document.body).on('selectstart', '.dash-header', function() {return false;});
  $(document.body).on('dragstart', '.dash-header', function() {return false;});
  // $(document.body).on('contextmenu', '.dash-header', function() {return false;});

  // set the state of renderer buttons
  $('.dash-body').each(function() {
    var renderer = $(this).children().eq(0).attr('renderer');
    var btn = $(this).parents('.dash').find(".dash-form").find("button[renderer='" + renderer + "']");
    btn.parent().children('.btn-info').removeClass('btn-info').addClass('btn-default');
    btn.addClass('btn-info');
  });

  // trigger the first dash load
  $('.dash-tabbar').each(function(i,n) {

      //如果是高峰期视图,需要先确保高峰期时段返回之后
      //再执行其他操作
      if($('#sidebar').find('a.active').attr('href')){
          if($('#sidebar').find('a.active').attr('href').endWith('station_peak_period_page')){
              if(i>0){
                  lazy_dash_loaders.push(this)
                  return
              }else{
                  return
              }
          }
    }

      $(this).children().eq(0).click();
  });

  //如果是高峰期视图,需要先确保高峰期时段返回之后
  //再执行其他操作
  if($('#sidebar').find('a.active').attr('href')){
      if($('#sidebar').find('a.active').attr('href').endWith('station_peak_period_page')){
          $('.dash-tabbar').children().eq(0).click();
      }
  }
});

function exportToXls(obj){
            // var form=$(event.srcElement).parents('.dash-form')
            var form=$(obj).parents('.dash-form')
            var index = $(this).parents('.dash-header').next('div').find('.dash-tab.btn-primary').index();
            var params = buildParams(form);
            var dashlet = form.parents('.dash-header').next('div').children('.dash-body').children().eq(index);
            var dashletID = dashlet.attr('id');
            var cacheID = 'dash#' + dashletID;
            $.each(params, function(i, n){
                if(n < 0) // fix a wierd bug regarding negative integer
                n = n + '$';
                cacheID += '_' + i + ':' + n;
            });
            var cachedJSON = dashlet.data(cacheID + "_rawdata");
            categories= cachedJSON.categories;
              dataset=cachedJSON.dataset;
              xls_categories=JSON.stringify(categories);
              xls_dataset=JSON.stringify(dataset);
              $.post("/gflux/ajax/export_table_to_xls/",
                    {'categories':xls_categories,'dataset':xls_dataset,"title":"横坐标"},
                    function(data){
                        if(data.message){
                              //以下注释的四种get请求都经过测试，可行
                          window.location.assign("/gflux/ajax/download_xls_file?filename="+data.filename+".xls")
                          //window.location.href="/gflux/ajax/download_xls_file?filename="+data.filename+".xls"
                          //newWindow=window.open("/gflux/ajax/download_xls_file?filename="+data.filename+".xls",'downloadPage','width=200,height=200')
                          //newWindow=window.open("/gflux/ajax/download_xls_file?filename="+data.filename+".xls",'downloadPage','width=200,height=200')
                          //表单提交post请求,待测
                          //var cookie=$.cookie().csrftoken
                          //$("#submit_cookie").val(cookie)
                          //$("#submit_filename").val(data.filename+'.xls')
                          //$("#submit_download").click()
                        }
                        else{alert("没有数据")}
              },"json");

}

//exportXlsFile
function exportXlsFile(obj){
        //var form=$(event.srcElement).parents('.dash-form')
        var form=$(obj).parents('.dash-form')
        var filename=$($($(event.srcElement).parents('.dash-header').children().children()[0]).children()).html().trim()
        var index = $(this).parents('.dash-header').next('div').find('.dash-tab.btn-primary').index();
        var params = buildParams(form);
        var dashlet = form.parents('.dash-header').next('div').children('.dash-body').children().eq(index);
        var dashletID = dashlet.attr('id');
        var cacheID = 'dash#' + dashletID;
        $.each(params, function(i, n){
            if(n < 0) // fix a wierd bug regarding negative integer
            n = n + '$';
            cacheID += '_' + i + ':' + n;
        });
        var cachedJSON = dashlet.data(cacheID + "_rawdata");
        categories= cachedJSON.categories;
        dataset=cachedJSON.dataset;
        xls_categories=JSON.stringify(categories);
        xls_dataset=JSON.stringify(dataset);
        filename=JSON.stringify(filename.trim());
        //以下注释的四种get请求都经过测试，可行
        window.location.assign("/gflux/ajax/downloadXlsFile?xls_categories="+xls_categories+"&"+"xls_dataset="+xls_dataset+'&'+'filename='+filename)
}

//单站查看
function signalSiteLook(site){
    if(!site){
        alert('请选择站点!')
        return
    }
    $.cookie('site-select',site,{path:'/'})

    //取得站点的最新最旧时间
    $.get(url_prefix+'ajax/get_station_latest_earliest_date/',
    {site:site},function(data){
        if(data.ret!='1101'){
            console.log(data.info)
        }else{
            //没有数据
            if(!data.latest_date){
                //...
            }else{
                //取得最近查看时间
                var date=$.cookie('date-select')

                //如果最近查看时间落在区间外
                //则需要修正
                if(!date){
                    //...
                }else if(date>data.latest_date || date<data.earliest_date){
                    if(data.latest_date==data.earliest_date){
                        $.cookie('date-select',data.latest_date,{path:'/'})
                    }else{
                        $.cookie('date-select',data.lastest_second_date,{path:'/'})
                    }
                }
            }
        }
    }).always(function(){
        location.href="/gflux/station_portal"
    });
}
