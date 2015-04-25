/*
 *
 * Load data and render dashlet
 * Rely on: jquery, jquery.blockUI highcharts
 **/

var cachedDash = {};

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
            title: "",
            min: 0
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
        tooltip: {
            enabled: true,
            formatter: function() {
              if (this.point.name) { // the pie chart
                return '' + this.point.name + ' : ' + this.y;
              } else {
                return '' + this.x + ' : '+ this.y;
              }
            }
        },
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
        } else { // chart is the default renderer
          // destroy existing chart
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
        if(lazy_dash_loaders.length){
            var that=lazy_dash_loaders.shift();
            $(that).children().eq(0).click();
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
                if(data['diff_time']){
                    //获取各个时段的值
                    crest=data['diff_time']['crest']
                    valley=data['diff_time']['valley']
                    high=data['diff_time']['high']
                    low=data['diff_time']['low']
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
                    series: series
                }, opts);
            }

            //缓存数据
            dashlet.data(cacheID, options);
            dashlet.data(cacheID + '_rawdata', json);
            dashlet.data(cacheID + '_color', Highcharts.getOptions().colors);

            //开始绘图
            if(renderer == "table") {
              $('#' + dashletID).html(jsonToTable(json, title));
            } else { // chart is the default renderer
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
    $('.dash-submit').each(function() {
      $(this).click();
    });
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
              }
          }
    }

      $(this).children().eq(0).click();
  });
});
