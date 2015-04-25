//dom ready
$(function(){
    //取得url前缀
    window.url_prefix='/'+$('meta[name="url_prefix"]').attr('content')

    //判断是否是standalone
    window.on_standalone=false
    if(location.href.indexOf('__dash__')!=-1)
        window.on_standalone=true

    //下面的函数是将排名表中的日期选择的精确度调整为月
    if($("form[value='multi_oil_trend_sort_dash']").length>0){

        //选择年月的
        $("form[value='multi_oil_trend_sort_dash']").children('div')
            .children('input[name="date"]').datepicker({
                 format: 'yyyy-mm',
                 viewMode:"months",
                 minViewMode:"months"
            });
    }
    if($("form[value='multi_v_i_p_pay_percent_trend_sort_dash']").length>0){

        //选择年月的
        $("form[value='multi_v_i_p_pay_percent_trend_sort_dash']").children('div')
            .children('input[name="date"]').datepicker({
              format: 'yyyy-mm',
              viewMode:"months",
              minViewMode:"months"
            });
    }

    if($("form[value='multi_oil_money_sort_trend_dash']").length>0){

        //选择年月的
        $("form[value='multi_oil_money_sort_trend_dash']").children('div')
            .children('input[name="date"]').datepicker({
              format: 'yyyy-mm',
              viewMode:"months",
              minViewMode:"months"
            });
    }

    if($("form[value='multi_none_oil_sales_trend_sort_dash']").length>0){

        //选择年月的
        $("form[value='multi_none_oil_sales_trend_sort_dash']").children('div')
            .children('input[name="date"]').datepicker({
              format: 'yyyy-mm',
              viewMode:"months",
              minViewMode:"months"
            });
    }

    if($("form[value='multi_oil_time_trend_sort_dash']").length>0){

        //选择年月的
        $("form[value='multi_oil_time_trend_sort_dash']").children('div')
            .children('input[name="date"]').datepicker({
              format: 'yyyy-mm',
              viewMode:"months",
              minViewMode:"months"
            });
    }

    if($("form[value='multi_fill_out_percent_trend_sort_dash']").length>0){

        //选择年月的
        $("form[value='multi_fill_out_percent_trend_sort_dash']").children('div')
            .children('input[name="date"]').datepicker({
              format: 'yyyy-mm',
              viewMode:"months",
              minViewMode:"months"
            });
    }

    if($("form[value='multi_oil_mo_m_trend_sort_dash']").length>0){

        //选择年月的
        $("form[value='multi_oil_mo_m_trend_sort_dash']").children('div')
            .children('input[name="date"]').datepicker({
              format: 'yyyy-mm',
              viewMode:"months",
              minViewMode:"months"
            });
    }

    if($("form[value='multi_oil_peak_fuel_avg_gun_trend_sort_dash']").length>0){

        //选择年月的
        $("form[value='multi_oil_peak_fuel_avg_gun_trend_sort_dash']").children('div')
            .children('input[name="date"]').datepicker({
              format: 'yyyy-mm',
              viewMode:"months",
              minViewMode:"months"
            });
    }

    if($("form[value='multi_single_customer_pay_trend_sort_dash']").length>0){

        //选择年月的
        $("form[value='multi_single_customer_pay_trend_sort_dash']").children('div')
            .children('input[name="date"]').datepicker({
              format: 'yyyy-mm',
              viewMode:"months",
              minViewMode:"months"
            });
    }

    if($("form[value='multi_none_oil_mo_m_trend_sort_dash']").length>0){

        //选择年月的
        $("form[value='multi_none_oil_mo_m_trend_sort_dash']").children('div')
            .children('input[name="date"]').datepicker({
              format: 'yyyy-mm',
              viewMode:"months",
              minViewMode:"months"
            });
    }

    if($("form[value='multi_none_oil_sales_trend_sort_dash']").length>0){

        //选择年月的
        $("form[value='multi_none_oil_sales_trend_sort_dash']").children('div')
            .children('input[name="date"]').datepicker({
              format: 'yyyy-mm',
              viewMode:"months",
              minViewMode:"months"
            });
    }

    //read site select from cookie then set
    initSiteSelect()

    //bind site select change event then save to cookie
    bindSiteSelect()

    //always show masking, remove it after load complete
    $(window).load(function(){
        $('#init-masking').hide()
    })

    //左侧导航点击保护
    bindLeftNavigator()

    //右侧内容区高度调节
    initRightContainerHeight()

    //date过滤器初始化和改变监听
    initDateSelect()
    bindDateSelect()

    //区域过滤器初始化和改变监听
    initLocationSelect()
    bindLocationSelect()

    //检查所有过滤器
    allFilters()

    //取得省的信息
    init_china_location_sheng()

    //取得城市和区县的信息
    init_china_location()

    //全局处理ajax
    $( document ).ajaxComplete(function( event, xhr, settings ) {
        //检查当前用户是否已注销或在其他地方登陆
        console.log(arguments)
        if(settings.dataType=='json'){
            if(xhr.responseJSON.ret){
                if(xhr.responseJSON.ret=='0000'||
                xhr.responseJSON.ret=='0007'){
                    window.location.href=url_prefix+'login.html'
                }
            }
        }
    });
})

//退出
function logout(){
    $.post(url_prefix+'ajax/logout/').complete(function(){
        window.location.href="/marketcloud/";
    })
}

//初始化date过滤器
function initDateSelect(){

    //如果是standalone就不动态更改过滤器
    if(on_standalone)
        return

    var option=$.cookie('date-select')
    if(option){

        //从cookie中取得各个排名的时间
        $("input[name='date']").prop('value',option)

        //建立臨時時間變量
        var datemoth = new Date(Date.parse(option)).getFullYear()+'-'+(new Date(Date.parse(option)).getMonth()+1)

        //將時間中特斯的時間格式化爲只有年月的格式
        $("form[value='multi_oil_trend_sort_dash']").children('div')
            .children('input[name="date"]').prop('value',datemoth)
        $("form[value='multi_oil_money_sort_trend_dash']").children('div')
            .children('input[name="date"]').prop('value',datemoth)
        $("form[value='multi_none_oil_sales_trend_sort_dash']").children('div')
            .children('input[name="date"]').prop('value',datemoth)
        $("form[value='multi_oil_time_trend_sort_dash']").children('div')
            .children('input[name="date"]').prop('value',datemoth)
        $("form[value='multi_fill_out_percent_trend_sort_dash']").children('div')
            .children('input[name="date"]').prop('value',datemoth)
        $("form[value='multi_oil_mo_m_trend_sort_dash']").children('div')
            .children('input[name="date"]').prop('value',datemoth)
        $("form[value='multi_oil_peak_fuel_avg_gun_trend_sort_dash']").children('div')
            .children('input[name="date"]').prop('value',datemoth)
        $("form[value='multi_single_customer_pay_trend_sort_dash']").children('div')
            .children('input[name="date"]').prop('value',datemoth)
        $("form[value='multi_none_oil_mo_m_trend_sort_dash']").children('div')
            .children('input[name="date"]').prop('value',datemoth)
        $("form[value='multi_none_oil_sales_trend_sort_dash']").children('div')
            .children('input[name="date"]').prop('value',datemoth)
        $("form[value='multi_v_i_p_pay_percent_trend_sort_dash']").children('div')
            .children('input[name="date"]').prop('value',datemoth)
    }

    var start_date=$.cookie('start-date-select')
    if(start_date){
        $("input[name='start_date']").prop('value',start_date)
    }
    var end_date=$.cookie('end-date-select')
    if(end_date){
        $("input[name='end_date']").prop('value',end_date)
    }

    var start_year_date=$.cookie('start-year-date-select')
    if(start_year_date){
        $("form[value='customer_v_i_p_monthly_loyalty_dash']").children('div')
            .children('input[name="start_date"]').prop('value',start_year_date)
    }
    var start_quarter_date=$.cookie('start-quar-date-select')
    if(start_quarter_date){
        $("form[value='oil_quarter_trend_dash']").children('div')
            .children('input[name="start_date"]').prop('value',start_quarter_date)
        $("form[value='goods_quarter_trend_dash']").children('div')
            .children('input[name="start_date"]').prop('value',start_quarter_date)
    }
}

//监视date过滤器的改变
function bindDateSelect(){

    //下面的代码判断排名表中是否存在,并保存中cookie中
    $("input[name='date']").on('changeDate',function(ev){

        //建立數組用來保存class
        var valuedash = [
            "multi_oil_trend_sort_dash",
            "multi_oil_money_sort_trend_dash",
            "multi_none_oil_sales_trend_sort_dash",
            "multi_oil_time_trend_sort_dash",
            "multi_fill_out_percent_trend_sort_dash",
            "multi_oil_mo_m_trend_sort_dash",
            "multi_oil_peak_fuel_avg_gun_trend_sort_dash",
            "multi_single_customer_pay_trend_sort_dash",
            "multi_none_oil_mo_m_trend_sort_dash",
            "multi_none_oil_sales_trend_sort_dash",
            "multi_v_i_p_pay_percent_trend_sort_dash",
        ];

        //判斷日期是由誰發出的,如果是list中的就不保存
        if(valuedash.indexOf($(this.form).attr("value"))){
          return
        }

        var option=$("input[name='date']").val()
        $.cookie('date-select',option,{path: '/' })
    })

    $("input[name='start_date']").on('changeDate',function(){
        var option=$("input[name='start_date']").val()
        $.cookie('start-date-select',option,{path: '/' })
    })

    $("input[name='end_date']").on('changeDate',function(){
        var option=$("input[name='end_date']").val()
        $.cookie('end-date-select',option,{path: '/' })
    })
}

//初始化右侧容器高度
function initRightContainerHeight() {
    var node_num = parseInt($('#right_container').children().length)
    console.log(node_num)
    $('#right_container').css('min-height',node_num*400)
}

//监视左侧导航按钮
function bindLeftNavigator(){
    $('#left_container').find('a').not('.list-subgroup').click(function(){
        $('#init-masking').show()
    })
}

//初始化site过滤器
function initSiteSelect(){

    //当前是standalone则不在初始化时纠正
    if(on_standalone)
        return

    var site=$.cookie('site-select')
    if(site){
        $('#id_site').find('option[value="'+site+'"]').prop('selected',true)

        //取得站点的油品
        //取得站点的油品类型
        if($('button[value="fuel_type"]').length>0){
            $.get(url_prefix+'ajax/get_station_fuel_type/',{site:site},
            function(data){
                //出错
                if(data.ret!='1101'){
                    errorModal(data.info)
                    return
                }

                //渲染
                $('#id_fuel_type').empty()
                var option=new Option(gettext('任意'),0)
                $('#id_fuel_type').append(option)
                for(var idx=0;idx<data.fuel_types.length;idx++){
                    var fuel_type=data.fuel_types[idx]
                    var option=new Option(fuel_type.name,fuel_type.barcode)
                    $('#id_fuel_type').append(option)
                }
            },'json')
        }

        //取得站点的最新最旧时间
        if($('button[value="date"]').length>0||$('button[value="start_date"]').length>0){
            $.get(url_prefix+'ajax/get_station_latest_earliest_date/',{site:site},
            function(data){
                if(data.ret!='1101'){
                    console.log(data.info)
                }else{
                    //没有数据
                    if(!data.latest_date){
                        //...
                    }else{
                        //取得最近查看时间
                        var date=$("input[name='date']").val()

                        //如果最近查看时间落在区间外
                        //则需要修正
                        if(!date){
                            //...
                        }else if(date>data.latest_date || date<data.earliest_date){
                            if(data.latest_date==data.earliest_date){
                                $.cookie('date-select',data.latest_date,{path:'/'})
                                $("input[name='date']").prop('value',data.latest_date)
                            }else{
                                $.cookie('date-select',data.lastest_second_date,{path:'/'})
                                $("input[name='date']").prop('value',data.lastest_second_date)
                            }
                        }
                        var start_date=$("input[name='start_date']").val()
                        var end_date=$("input[name='end_date']").val()
                        if(!end_date||!start_date){
                            //...
                        }else if((end_date>data.latest_date || end_date<data.earliest_date)&&(start_date>data.latest_date || start_date<data.earliest_date)){
                            if(data.latest_date==data.earliest_date){
                                $("input[name='end_date']").val(data.latest_date)
                                $.cookie('end-date-select',data.latest_date,{path:'/'})
                            }else{
                                $("input[name='end_date']").val(data.lastest_second_date)
                                $.cookie('end-date-select',data.lastest_second_date,{path:'/'})
                            }
                            $("input[name='start_date']").val(data.latest_month_date)
                            $.cookie('start-date-select',data.latest_month_date,{path:'/'})
                        }
                        $("form[value='customer_v_i_p_monthly_loyalty_dash']").children('div')
                            .children('input[name="start_date"]').prop('value',data.latest_year_date)
                        $.cookie('start-year-date-select',data.latest_year_date,{path:'/'})
                        $("form[value='oil_quarter_trend_dash']").children('div')
                            .children('input[name="start_date"]').prop('value',data.latest_quarter_date)
                        $("form[value='goods_quarter_trend_dash']").children('div')
                            .children('input[name="start_date"]').prop('value',data.latest_quarter_date)
                        $.cookie('start-quar-date-select',data.latest_quarter_date,{path:'/'})
                    }
                }
            }).always(function(){
                $.cookie('site-select',site,{path: '/' })
            })
        }
    }else{
        var option=new Option('---','---')
        $('#id_site').prepend(option)
        $(option).prop('selected',true)
    }
}

//监视site过滤器的改变
function bindSiteSelect(){
    $('#id_site').change(function(){
        var option=$("#id_site option:selected").val()

        //取得站点的最新最旧时间
        if($('button[value="date"]').length>0||$('button[value="start_date"]').length>0){
            $.get(url_prefix+'ajax/get_station_latest_earliest_date/',
            {site:option},function(data){
                if(data.ret!='1101'){
                    console.log(data.info)
                }else{
                    //没有数据
                    if(!data.latest_date){
                        //...
                    }else{
                        //取得最近查看时间
                        var date=$("input[name='date']").val()

                        //如果最近查看时间落在区间外
                        //则需要修正
                        if(!date){
                            //...
                        }else if(date>data.latest_date || date<data.earliest_date){
                            if(data.latest_date==data.earliest_date){
                                $.cookie('date-select',data.latest_date,{path:'/'})
                                $("input[name='date']").prop('value',data.latest_date)
                            }else{
                                $.cookie('date-select',data.lastest_second_date,{path:'/'})
                                $("input[name='date']").prop('value',data.lastest_second_date)
                            }
                        }
                        if(data.latest_date==data.earliest_date){
                            $("input[name='end_date']").val(data.latest_date)
                            $.cookie('end-date-select',data.latest_date,{path: '/' })
                        }else{
                            $("input[name='end_date']").val(data.lastest_second_date)
                            $.cookie('end-date-select',data.lastest_second_date,{path: '/' })
                        }
                        $("input[name='start_date']").val(data.latest_month_date)
                        $.cookie('start-date-select',data.latest_month_date,{path: '/' })
                        $("form[value='customer_v_i_p_monthly_loyalty_dash']").children('div')
                            .children('input[name="start_date"]').prop('value',data.latest_year_date)
                        $.cookie('start-year-date-select',data.latest_year_date,{path:'/'})
                        $("form[value='oil_quarter_trend_dash']").children('div')
                            .children('input[name="start_date"]').prop('value',data.latest_quarter_date)
                        $("form[value='goods_quarter_trend_dash']").children('div')
                            .children('input[name="start_date"]').prop('value',data.latest_quarter_date)
                        $.cookie('start-quar-date-select',data.latest_quarter_date,{path:'/'})
                    }
                }
            }).always(function(){
                $.cookie('site-select',option,{path: '/' })
            })
        }

        //取得站点的油品
        //取得站点的油品类型
        if($('button[value="fuel_type"]').length>0){
            $.get(url_prefix+'ajax/get_station_fuel_type/',{site:option},
            function(data){
                //出错
                if(data.ret!='1101'){
                    errorModal(data.info)
                    return
                }

                //渲染
                $('#id_fuel_type').empty()
                var option=new Option(gettext('任意'),0)
                $('#id_fuel_type').append(option)
                for(var idx=0;idx<data.fuel_types.length;idx++){
                    var fuel_type=data.fuel_types[idx]
                    var option=new Option(fuel_type.name,fuel_type.barcode)
                    $('#id_fuel_type').append(option)
                }
            },'json')
        }
    })
}

//初始化location过滤器
function initLocationSelect(){

    //如果是standalone就不更改
    if(on_standalone)
        return

    var option=$.cookie('location-select')
    if(option){
        $('#id_location').find('option[value="'+option+'"]').prop('selected',true)
    }
}

//监视location过滤器改变
function bindLocationSelect(){
    $('#id_location').change(function(){
        var option=$("#id_location option:selected").val()
        $.cookie('location-select',option,{path: '/' })
    })
}

//所有过滤器
function allFilters(){
    //加油站tab时,进行过滤器检查
    if($('li[class="active"]').children('a[href="/gflux/station_portal"]').length>0){
        if($('#creator_view').css('display')){
            if($('#creator_view').css('display')!='none'){
                return
            }

        }
        //date过滤器
        var dateFilter=String.format("<div class='btn-group' style='margin-right: 5px; '> \
                            <button type='button' class='btn btn-default'>{0}</button> \
                            <input class='dash-control form-control' style='width:100px;' type='text' disabled='true'> \
                          </div>",gettext('日期'))

        //油品过滤器
        var fuelFilter=String.format("<div class='btn-group' style='margin-right: 5px'> \
                            <button type='button' class='btn btn-default'>{0}</button> \
                            <select class='dash-control form-control'  style='width:100px;' disabled='true'></select> \
                          </div>",gettext('油品'))

        //站点过滤器
        var siteFilter=String.format("<div class='btn-group' style='margin-right: 5px'> \
                            <button type='button' class='btn btn-default' >{0}</button> \
                            <select class='dash-control form-control' style='width:100px;' disabled='true'></select> \
                          </div>",gettext('站点'))

        //支付过滤器
        var payFilter =String.format("<div class='btn-group' style='margin-right: 5px'> \
                            <button type='button' class='btn btn-default'>{0}</button> \
                            <select class='dash-control form-control' style='width:100px;' disabled='true'></select> \
                          </div>",gettext('支付方式'))

        //没有日期过滤器
        if($('.dash-top-form').children('.btn-group').children('button[value="date"]').length==0){
            $('.dash-top-form').prepend(dateFilter)
        }

        //没有油品过滤器
        if($('.dash-top-form').children('.btn-group').children('button[value="fuel_type"]').length==0){
            $('.dash-top-form div:eq(0)').after(fuelFilter)
        }

        //没有站点过滤器
        if($('.dash-top-form').children('.btn-group').children('button[value="site"]').length==0){
            $('.dash-top-form div:eq(1)').after(siteFilter)
        }

        //没有支付过滤器
        if($('.dash-top-form').children('.btn-group').children('button[value="payment_type"]').length==0){
            $('.dash-top-submit').before(payFilter)
        }
    }
}

//取得城市和区县的信息
function init_china_location(){
    //监听选择市/县的事件
    $('#shengcode').change(function(){
        var parent = $('#shengcode').val()

        //通过ajax请求取得城市的信息
        $.post(url_prefix+'ajax/get_china_location/',
           {"parent":parent,"level":2},
            function(data){

                //判断返回值是否正确
                if (data.ret!=1101){
                    alert(data.info)
                    return
                }
                var all_ps=data['dict_city']
                var $shicode = $('#shicode').empty();
                $shicode.append('<option selected value="">请选择</option>')
                var $xiancode = $('#xiancode').empty();
                $xiancode.append('<option selected value="">请选择</option>')

                //循环遍历出城市的id和name,并填充到页面中
                for(var i=0;i<all_ps.length;i++){
                    var $html=String.format('<option value="{0}">{1}</option>',all_ps[i][0],all_ps[i][1])
                    $('#shicode').append($html)
                }
            },
        "json");
    })

    $('#shicode').change(function(){
      var parent = $('#shicode').val()

      //通过ajax请求取得区县的信息
      $.post(url_prefix+'ajax/get_china_location/',
         {"parent":parent,"level":3},
          function(data) {

              //判断返回值是否正确
              if (data.ret!=1101){
                  alert(data.info)
                  return
              }
              var all_ps = data['dict_city']
              var $xiancode = $('#xiancode').empty();
              $xiancode.append('<option selected value="">请选择</option>')

              //循环遍历出城市的id和name,并填充到页面中
              for (var i = 0; i < all_ps.length; i++) {
                   var $html = String.format('<option value="{0}">{1}</option>', all_ps[i][0], all_ps[i][1])
                   $('#xiancode').append($html)
              }
          },
      "json");
      })
}

//取得省的信息
function init_china_location_sheng(){
  if($('#shengcode').length===0)
    return

  //发送ajax请求取得省的信息
  $.post(url_prefix+'ajax/get_china_location/',
    {"parent":0,"level":1},
    function(data){

      //判断返回值是否正确
      if (data.ret!=1101){
        alert(data.info)
        return
      }
      var all_ps=data['dict_city']

      //循环遍历出城市的id和name,并填充到页面中
      for(var i=0;i<all_ps.length;i++){
        var $html=String.format('<option value="{0}">{1}</option>',all_ps[i][0],all_ps[i][1])
        $('#shengcode').append($html)
      }
    },"json");
}
