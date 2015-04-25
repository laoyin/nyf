//dom ready
$(function(){
    //全局变量
    window.cachedDash={}

    //初始化站点过滤器
    initFilterStationSelector()

    //初始化通道油机油位信息
    initPassageMachineLevel()

    //监视站点过滤器
    bindFilterStationSelector()

    //监视时间类型选择器
    bindDateTypeChange()

    //监视时间范围过滤器
    bindFilterRangeDateSelector()

    //监视可选过滤器
    bindFilterOptionCheckBox()

    //监视曲线分类
    bindSeriesCheckBox()

    //监视图表按钮切换事件
    $('.dash-renderer').on('click', function(e) {
        e.preventDefault();
        $(this).parent().children('.btn-info').removeClass('btn-info').addClass('btn-default');
        $(this).addClass('btn-info');
        clickCreateReportButton();
    });

})

//根据json数据生成表格
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

//生成按钮点击事件回调
function clickCreateReportButton(){
    //站点
    var site=$('#filter-site').val()
    if(site=='--'){
        alert(gettext('不存在任何站点,请先上传数据!'))
        return
    }

    //统计量
    var count_type=$('#filter-count-type').val()
    $("#professional_chart").attr('dash-label',$('#filter-count-type').find('option:selected').text())

    //时间类型
    var time_type=$('#filter-time-type').find('input:checked').val()

    //时间
    var date=$('#id_date').val()
    var start_date=$('#id_start_date').val()
    var end_date=$('#id_end_date').val()

    if(time_type!='ONE'){
        if(end_date==start_date){
            alert(gettext('开始日期和结束日期不能相同!'))
            return
        }
        else if(end_date<start_date){
            alert(gettext('结束日期必须大于开始日期!'))
            return
        }
    }

    //时间粒度
    var base_time=$('#filter-base-time').val()

    //可选
    var option_checked=$('form.option-filter').find('input[type="checkbox"]:checked')
        .parents('.checkbox').find('select')
    var option_value=option_checked.map(function(){
        var key=$(this).attr('name')
        var value=$(this).val()
        var ret={}

        //油枪分组
        if(key=='guns_type'){
            //单选按钮的值
            var radio_name=$('form.option-filter')
                .find('input[name="passage-machine-level"]:checked').val()

            ret[radio_name]=value
        }
        else{
            ret[key]=value
        }

        return ret
    }).get()

    //曲线分类
    var series_category=$('form.series-category').find('input:checked')
        .map(function(){
            //油枪分组
            if($(this).val()=='guns-type'){
                return $('#select-guns').val()
            }else{
                return $(this).val()
            }

        })
        .get()

    if(series_category.length==0){
        alert(gettext('请选择曲线分类!'))
        return
    }
    else if(series_category.length>2){
        alert(gettext('曲线分类最多选择两类!'))
        return
    }

    //渲染方式
    window.series_type=$('#id_series_type').val()
    window.stack_type=$('#id_stack_type').val()
    if(stack_type=='null')
        stack_type=null

    //请求数据
    var params={
        site:site,
        count_type:count_type,
        time_type:time_type,
        date:date,
        start_date:start_date,
        end_date:end_date,
        option_value:option_value,
        series_category:series_category,
        base_time:base_time
    }
    var opts={}
    var action=url_prefix+'ajax/professional_analysis/'

    //渲染
    renderReport(action,params,opts)
}

//返回按钮
function returnToCreatorView(){
    $('#reportor_view').hide('drop',function(){
        $('#creator_view').show('drop')
    })
}

//渲染图表
function renderReport(action,params,opts){
    //取得图表容器
    var dashlet=$("#professional_chart")
    var renderer=$('.dash-form').find('.dash-renderer.btn-info').attr('renderer');
    var forceReload=false
    var title = dashlet.attr('dash-label') || '';

    //渲染选项
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
    commonOpts['chart']['defaultSeriesType']=series_type
    commonOpts['plotOptions'][series_type]={}
    commonOpts['plotOptions'][series_type]['stacking']=stack_type

    //cache 特意改造过,适应业务逻辑
    var dashletID = dashlet.attr('id');
    var cacheID = 'dash#' + dashletID;
    $.each(params, function(i, n){

        //是列表
        if(getTypeOf(n)=='Array'){
            cacheID+='_'+i

            $.each(n,function(j,m){
                //是对象
                if(getTypeOf(m)=='Object'){
                    $.each(m,function(k,o){
                        cacheID += '_' + k + ':' + o;
                    })
                }else{
                    cacheID+='_'+j+':'+m
                }
            })
        }

        //是对象
        else if(getTypeOf(n)=='Object'){
            $.each(n,function(j,m){
                cacheID+='_'+j+':'+m
            })
        }
        else{
            cacheID += '_' + i + ':' + n;
        }
    });

    //切换到图表视图
    $('#creator_view').hide()
    $('#reportor_view').show()

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
        //出错
        if(json.ret!='1101'){
            errorModal(json.info)
            return
        }

        //没有数据
        else if(json.dataset.length==0){
            errorModal(gettext('未能查询到相关记录!'))
            return
        }

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
        dashCanvas.unblock();
    });
}

//监视曲线分类
//最多选择两个
function bindSeriesCheckBox(){
    $('form.series-category').find('input[type="checkbox"]').click(function(event){
        //站点
        var site=$('#filter-site').val()

        //当前以选中的数量
        var checked=$('form.series-category').find('input[type="checkbox"]:checked')

        //油枪选项
        var pump_check_box=$('form.series-category').find('input[name="checkbox-pump"]')

        //油枪分组选项
        var guns_check_box=$('form.series-category').find('input[name="checkbox-guns-group"]')

        //油枪选项和油枪分组选项应该是互斥的
        if(pump_check_box.prop('checked')){
            guns_check_box.prop('disabled',true)
        }else if(guns_check_box.prop('checked')){
            var info=$('#select-guns').val()
            if(info=='passages'){
                //获取站点下的通道信息
                var passages=all_passage_machine_level[site]['passages']
                if(!passages||passages.length==0){
                    errorModal(gettext('没有任何通道'))
                    guns_check_box.prop('checked',false)
                    return
                }
            }
            else if(info=='machines'){
                //获取站点下的通道信息
                var machines=all_passage_machine_level[site]['machines']
                if(!machines||machines.length==0){
                    errorModal(gettext('没有任何油机'))
                    guns_check_box.prop('checked',false)
                    return
                }
            }
            else if(info=='levels'){
                //获取站点下的通道信息
                var levels=all_passage_machine_level[site]['level']
                if(!levels||levels.length==0){
                    errorModal(gettext('没有任何油位'))
                    guns_check_box.prop('checked',false)
                    return
                }
            }
            pump_check_box.prop('disabled',true)
        }else{
            pump_check_box.prop('disabled',false)
            guns_check_box.prop('disabled',false)
        }

        //如果已经有两个了,那么事件取消传递
        if(checked.length>2){
            preventDefault(event)
        }
    })

    //油枪分组选择监听
    $('#select-guns').change(function(){
        //站点
        var site=$('#filter-site').val()
        var info=$('#select-guns').val()

        //油枪选项
        var pump_check_box=$('form.series-category').find('input[name="checkbox-pump"]')

        //油枪分组选项
        var guns_check_box=$('form.series-category').find('input[name="checkbox-guns-group"]')
        if(info=='passages'){
            //获取站点下的通道信息
            var passages=all_passage_machine_level[site]['passages']
            if(!passages||passages.length==0){
                errorModal(gettext('没有任何通道'))
                guns_check_box.prop('checked',false)
                pump_check_box.prop('disabled',false)
            }
        }
        else if(info=='machines'){
            //获取站点下的通道信息
            var machines=all_passage_machine_level[site]['machines']
            if(!machines||machines.length==0){
                errorModal(gettext('没有任何油机'))
                guns_check_box.prop('checked',false)
                pump_check_box.prop('disabled',false)
            }
        }
        else if(info=='levels'){
            //获取站点下的通道信息
            var levels=all_passage_machine_level[site]['level']
            if(!levels||levels.length==0){
                errorModal(gettext('没有任何油位'))
                guns_check_box.prop('checked',false)
                pump_check_box.prop('disabled',false)
            }
        }
    })
}

//监视可选过滤器
function bindFilterOptionCheckBox(){
    $('form.option-filter').find('input[type="checkbox"]').change(function(){
        //当前项名字
        var checkbox_name=$(this).attr('name')
        //如果当前项被选择那么曲线分类就不能被勾选
        var des=$('form.series-category').find('input[name="'+checkbox_name+'"]')

        //如果选中油枪分组,那么曲线分类中应该相应删去radio对应的项目
        if(checkbox_name=='checkbox-guns-group'){
            //曲线分类中的油枪分组select选项
            var gunsSelect=$('#select-guns')
            gunsSelect.empty()
            var radio_name=$('form.option-filter').find('input[name="passage-machine-level"]:checked').val()
            var opp1 = new Option(gettext("通道"),"passages");
            var opp2 = new Option(gettext("油机"),"machines");
            var opp3 = new Option(gettext("油位"),"levels");
            gunsSelect.append(opp1);
            gunsSelect.append(opp2);
            gunsSelect.append(opp3);
            if($(this).prop('checked')){
                $('#select-guns option[value="'+radio_name+'"]').remove()
            }
        }else{
            if($(this).prop('checked')){
                des.prop('checked',false)
                des.prop('disabled',true)
            }else{
                des.prop('disabled',false)
            }
        }

    })

    //单选按钮的监听
    $('form.option-filter').find('input[name="passage-machine-level"]').change(function(event){
        var site=$('#filter-site').val()
        var radio_name=$('form.option-filter').find('input[name="passage-machine-level"]:checked').val()
        var gunsSelect = $('#filter-guns');

        var groupSelect=$('#select-guns')

        //可选项中油枪分组如果选中,要将曲线分类中的项目相应去掉
        if($('form.option-filter').find('input[name="checkbox-guns-group"]').prop('checked')){
            groupSelect.empty()
            var opp1 = new Option(gettext("通道"),"passages");
            var opp2 = new Option(gettext("油机"),"machines");
            var opp3 = new Option(gettext("油位"),"levels");
            groupSelect.append(opp1)
            groupSelect.append(opp2)
            groupSelect.append(opp3)
            $('#select-guns option[value="'+radio_name+'"]').remove()
        }

        gunsSelect.empty()

        //根据单选的内容,重置select中的值
        if(radio_name=='passages'){
            var passages=all_passage_machine_level[site]['passages']
            if(!passages||passages.length==0){
                $('form.option-filter').find('input[name="checkbox-guns-group"]').prop('checked',false)
                $('form.option-filter').find('input[name="checkbox-guns-group"]').prop('disabled',true)
                errorModal(gettext('没有任何通道'))
                return
            }
            //添加到选项
            for (var idx=0;idx<passages.length;idx++){
                var key=passages[idx]['name']
                var value=passages[idx]['name']
                var opp = new Option(value,key);
                gunsSelect.append(opp);
            }
            $('form.option-filter').find('input[name="checkbox-guns-group"]').prop('disabled',false)
        }
        else if(radio_name=='machines'){
            var machines=all_passage_machine_level[site]['machines']
            if(!machines||machines.length==0){
                $('form.option-filter').find('input[name="checkbox-guns-group"]').prop('checked',false)
                $('form.option-filter').find('input[name="checkbox-guns-group"]').prop('disabled',true)
                errorModal(gettext('没有任何油机'))
                return
            }
            //添加到选项
            for (var idx=0;idx<machines.length;idx++){
                var key=machines[idx]['name']
                var value=machines[idx]['name']
                var opp = new Option(value,key);
                gunsSelect.append(opp);
            }
            $('form.option-filter').find('input[name="checkbox-guns-group"]').prop('disabled',false)
        }
        else if(radio_name=='levels'){
            var levels=all_passage_machine_level[site]['level']
            if(!levels||levels.length==0){
                $('form.option-filter').find('input[name="checkbox-guns-group"]').prop('checked',false)
                $('form.option-filter').find('input[name="checkbox-guns-group"]').prop('disabled',true)
                errorModal(gettext('没有任何油位'))
                return
            }
            //添加到选项
            for (var idx=0;idx<levels.length;idx++){
                var key=levels[idx]['name']
                var value=levels[idx]['name']
                var opp = new Option(value,key);
                gunsSelect.append(opp);
            }
            $('form.option-filter').find('input[name="checkbox-guns-group"]').prop('disabled',false)
        }
    })
}

//监视时间范围过滤器
function bindFilterRangeDateSelector(){
    //start date filter
    $('#id_start_date').on('changeDate',function(){
        //只有当前时间类型为范围时我们才需要修正粒度过滤器
        var type=$('#filter-time-type').find('input:checked').val()
        if(type=='ONE'){
            //DO NOTHING...
        }else{
            fixBaseTime(type)
        }
    })

    //end date filter
    $('#id_end_date').on('changeDate',function(){
        //只有当前时间类型为范围时我们才需要修正粒度过滤器
        var type=$('#filter-time-type').find('input:checked').val()
        if(type=='ONE'){
            //DO NOTHING...
        }else{
            fixBaseTime(type)
        }
    })
}

//监视时间类型选择器
function bindDateTypeChange(){
    $('#filter-time-type').click(function(){
        //当前类型
        var type=$('#filter-time-type').find('input:checked').val()

        //根据类型显示不同的时间过滤器
        if(type=='ONE'){
            $('#one-date-selector').show()
            $('#multi-date-selector').hide()
        }else{
            $('#one-date-selector').hide()
            $('#multi-date-selector').show()
        }

        //修正时间粒度
        fixBaseTime(type)
    })
}

//根据时间类型和时间过滤器动态修改时间粒度
function fixBaseTime(type){
    if(type=='ONE'){
        //只能是小时
        $('#filter-base-time').empty().append(String.format('<option value="hour">{0}</option>',gettext('小时')))
        return
    }

    //范围需要判断
    var start_date=new Date($('#id_start_date').val())
    var end_date=new Date($('#id_end_date').val())

    var range=end_date.getTime()-start_date.getTime()

    //范围错误
    if(range<=0){
        alert(gettext('时间范围选择错误,结束时间必须要大于开始时间!'))
        return
    }

    //如果>=3个月,可选:月,周
    if(range>=3*30*24*3600*1000){
        $('#filter-base-time').empty().append(String.format(
            '<option value="month">{0}</option>\
            <option value="week">{1}</option>\
            '),gettext('月'),gettext('周'))
    }
    //如果>=3周,可选:周,天
    else if(range>=3*7*24*3600*1000){
        $('#filter-base-time').empty().append(String.format(
            '<option value="week">{0}</option>\
            <option value="day">{1}</option>\
            '),gettext('周'),gettext('天'))
    }
    //其余都是天
    else{
        $('#filter-base-time').empty().append(String.format('<option value="day">{0}</option>',gettext('天')))
    }
}

//监视站点过滤器
function bindFilterStationSelector(){
    $('#filter-site').change(function(){
        //选择的站点
        var site=$('#filter-site').val()

        var radio_name=$('form.option-filter').find('input[name="passage-machine-level"]:checked').val()

        var info=$('#select-guns').val()

        //油枪选项
        var pump_check_box=$('form.series-category').find('input[name="checkbox-pump"]')

        //油枪分组选项
        var guns_check_box=$('form.series-category').find('input[name="checkbox-guns-group"]')
        if(info=='passages'){
            //获取站点下的通道信息
            var passages=all_passage_machine_level[site]['passages']
            if(!passages||passages.length==0){
                guns_check_box.prop('checked',false)
                pump_check_box.prop('disabled',false)
            }
        }
        else if(info=='machines'){
            //获取站点下的通道信息
            var machines=all_passage_machine_level[site]['machines']
            if(!machines||machines.length==0){
                guns_check_box.prop('checked',false)
                pump_check_box.prop('disabled',false)
            }
        }
        else if(info=='levels'){
            //获取站点下的通道信息
            var levels=all_passage_machine_level[site]['level']
            if(!levels||levels.length==0){
                guns_check_box.prop('checked',false)
                pump_check_box.prop('disabled',false)
            }
        }

        //油枪分组
        var gunsSelect = $('#filter-guns');
        gunsSelect.empty()

        //站点变化,相应的重置油枪分组的select内容
        if(radio_name=='passages'){
            var passages=all_passage_machine_level[site]['passages']
            if(!passages||passages.length==0){
                $('form.option-filter').find('input[name="checkbox-guns-group"]').prop('checked',false)
                $('form.option-filter').find('input[name="checkbox-guns-group"]').prop('disabled',true)
                errorModal(gettext('没有任何通道'))
            }else{
                //添加到选项
                for (var idx=0;idx<passages.length;idx++){
                    var key=passages[idx]['name']
                    var value=passages[idx]['name']
                    var opp = new Option(value,key);
                    gunsSelect.append(opp);
                }
                $('form.option-filter').find('input[name="checkbox-guns-group"]').prop('disabled',false)
            }
        }
        else if(radio_name=='machines'){
            var machines=all_passage_machine_level[site]['machines']
            if(!machines||machines.length==0){
                $('form.option-filter').find('input[name="checkbox-guns-group"]').prop('checked',false)
                $('form.option-filter').find('input[name="checkbox-guns-group"]').prop('disabled',true)
                errorModal(gettext('没有任何油机'))
            }else{
                //添加到选项
                for (var idx=0;idx<machines.length;idx++){
                    var key=machines[idx]['name']
                    var value=machines[idx]['name']
                    var opp = new Option(value,key);
                    gunsSelect.append(opp);
                }
                $('form.option-filter').find('input[name="checkbox-guns-group"]').prop('disabled',false)
            }
        }
        else if(radio_name=='levels'){
            var levels=all_passage_machine_level[site]['level']
            if(!levels||levels.length==0){
                $('form.option-filter').find('input[name="checkbox-guns-group"]').prop('checked',false)
                $('form.option-filter').find('input[name="checkbox-guns-group"]').prop('disabled',true)
                errorModal(gettext('没有任何油位'))
            }else{
                //添加到选项
                for (var idx=0;idx<levels.length;idx++){
                    var key=levels[idx]['name']
                    var value=levels[idx]['name']
                    var opp = new Option(value,key);
                    gunsSelect.append(opp);
                }
                $('form.option-filter').find('input[name="checkbox-guns-group"]').prop('disabled',false)
            }
        }


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
                    //取得时间
                    var date=$('#id_date').val()

                    //如果时间落在区间外
                    //则需要修正
                    if(!date){
                        //...
                    }else if(date>data.latest_date || date<data.earliest_date){
                        if(data.latest_date==data.earliest_date){
                            $('#id_date').val(data.latest_date)
                        }else{
                            $('#id_date').val(data.lastest_second_date)
                        }
                    }

                    //修正时间范围
                    var start_date=$('#id_start_date').val()
                    var end_date=$('#id_end_date').val()

                    if(start_date<data.earliest_date){
                        $('#id_start_date').val(data.earliest_date)
                        $('#id_end_date').val(data.latest_date)
                    }

                    if(end_date>data.latest_date){
                        $('#id_start_date').val(data.earliest_date)
                        $('#id_end_date').val(data.latest_date)
                    }

                    //修正时间粒度
                    //当前类型
                    var type=$('#filter-time-type').find('input:checked').val()
                    fixBaseTime(type)
                }
            }
        })

        //取得站点的油品
        //取得站点的油品类型
        $.get(url_prefix+'ajax/get_station_fuel_type/',{site:site},
        function(data){
            //出错
            if(data.ret!='1101'){
                errorModal(data.info)
                return
            }

            //渲染
            $('#filter-fuel-type').empty()
            for(var idx=0;idx<data.fuel_types.length;idx++){
                var fuel_type=data.fuel_types[idx]
                var option=new Option(fuel_type.name,fuel_type.barcode)
                $('#filter-fuel-type').append(option)
            }
        },'json')
    })
}

//初始化站点
function initFilterStationSelector(){
    var siteSelect = $('#filter-site');

    //如果没有任何站点
    if(all_stations.length==0){
        siteSelect.append(new Option('--','--'))
        alert(gettext('不存在任何站点,请先上传数据!'))
        return
    }

    //添加到选项
    for (var idx=0;idx<all_stations.length;idx++){
        var key=all_stations[idx].name
        var value=all_stations[idx].description
        var opp = new Option(value,key);
        siteSelect.append(opp);

        //根据第一个站点初始化时间过滤器
        if(idx==0){
            var site=key
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
                        //取得时间
                        var date=$('#id_date').val()

                        //如果时间落在区间外
                        //则需要修正
                        if(!date){
                            //...
                        }else if(date>data.latest_date || date<data.earliest_date){
                            if(data.latest_date==data.earliest_date){
                                $('#id_date').val(data.latest_date)
                            }else{
                                $('#id_date').val(data.lastest_second_date)
                            }
                        }

                        //修正时间范围
                        $('#id_start_date').val(data.earliest_date)
                        $('#id_end_date').val(data.latest_date)
                    }
                }
            })

            //取得站点的油品类型
            $.get(url_prefix+'ajax/get_station_fuel_type/',{site:site},
            function(data){
                //出错
                if(data.ret!='1101'){
                    errorModal(data.info)
                    return
                }

                //渲染
                $('#filter-fuel-type').empty()
                for(var idx=0;idx<data.fuel_types.length;idx++){
                    var fuel_type=data.fuel_types[idx]
                    var option=new Option(fuel_type.name,fuel_type.barcode)
                    $('#filter-fuel-type').append(option)
                }
            },'json')
        }
    }
}

//初始化通道油机油位信息
function initPassageMachineLevel(){
    //站点
    var site=$('#filter-site').val()

    //获取站点下的通道信息
    var passages=all_passage_machine_level[site]['passages']


    //初始化油枪分组的下拉选项
    var gunsSelect = $('#filter-guns');

    //如果没有任何通道
    if(!passages){
        $('form.option-filter').find('input[name="checkbox-guns-group"]').prop('checked',false)
        $('form.option-filter').find('input[name="checkbox-guns-group"]').prop('disabled',true)
        errorModal(gettext('没有任何通道'))
        return
    }

    //添加到选项
    for (var idx=0;idx<passages.length;idx++){
        var key=passages[idx]['name']
        var value=passages[idx]['name']
        var opp = new Option(value,key);
        gunsSelect.append(opp);
    }

}
