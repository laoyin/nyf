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
    if (!forceReload && cachedOpts != null) {
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
    var loading_img = $("<img src='/dash/static/images/ajax-loader.gif'/>");
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
        if(json.status == 'OK') {
            $.each(json.categories, function(i, category) {
                categories[i] = category;
            });

            $.each(json.dataset, function(i, data) {
                series.push($.extend({visible: true}, data));
            });

            if(json.extra != undefined) {
              $.each(json.extra, function(i, data) {
                series.push($.extend({visible: true}, data));
              });
            }

            opts = $.extend(opts || {}, json.opts || {});
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
          
            dashlet.data(cacheID, options);
            dashlet.data(cacheID + '_rawdata', json);

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
    params[$(this).attr('name')] = $(this).val();
  });      
  form.find('.dash-control').each(function() {
    params[$(this).attr('name')] = $(this).val();
  });    
  return params; 
}

$(function() {
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
  $('.dash-tabbar').each(function() {
    $(this).children().eq(0).click();
  });
  
});
