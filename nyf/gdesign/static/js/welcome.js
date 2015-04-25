//dom ready
$(function(){
    //从cookie中取得上次上传信息
    initUploadHistoryStatus()

    //从cookie中取得上次查看信息
    initLookHistoryStatus()

    //初始化站点和地区选择器
    initLocationSite()

    //绑定站点选择变化
    bindSiteSelect()

})

//渲染上次上传信息
function initUploadHistoryStatus(){
    var site=$.cookie('last-upload-site')
    var time=$.cookie('last-upload-time')

    //render site
    if(site){
        $('#last-upload-site').text(site).show()
    }else{
        $('#last-upload-site').parent().hide()
    }

    //render time
    if(time){
        $('#last-upload-time').text(time).show()
    }else{
        $('#last-upload-time').parent().hide()
    }
}

//渲染上次查看信息
function initLookHistoryStatus(){
    var site=$.cookie('site-select')
    var time=$.cookie('date-select')

    //render site
    if(site){
        $('#last-look-site').text(site).show()
    }else{
        $('#last-look-site').parent().hide()
    }

    //render time
    if(time){
        $('#last-look-time').text(time).show()
    }else{
        $('#last-look-time').parent().hide()
    }
}

//初始化地区和站点
function initLocationSite(){
    //set location and site

    //site
    var siteSelect = $('.site-select');
    for (var idx=0;idx<all_stations.length;idx++){
        var key=all_stations[idx].name
        var value=all_stations[idx].description
      var opp = new Option(value,key);
      siteSelect.append(opp);
    }

    //location
    var locationiSelect=$('.location-select');
    for (var idx=0;idx<all_locations.length;idx++){
        if(all_locations[idx].id==0)
            continue

        var key=all_locations[idx].id
        var value=all_locations[idx].description
      var opp = new Option(value,key);
      locationiSelect.append(opp);
    }

    var site=$('#vs-site-selector').val()
    if(site){
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
                        $.cookie('date-select',data.lastest_second_date,{path:'/'})
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
                        $.cookie('end-date-select',data.latest_date,{path:'/'})
                    }else{
                        $("input[name='end_date']").val(data.lastest_second_date)
                        $.cookie('end-date-select',data.lastest_second_date,{path:'/'})
                    }
                    $("input[name='start_date']").val(data.latest_month_date)
                    $.cookie('start-date-select',data.latest_month_date,{path:'/'})
                }
            }
        }).always(function(){
            $.cookie('site-select',site,{path: '/' })
        })
    }
}

//单站查看
function signalSiteLook(){
    var site=$('#signal-site-selector').val()
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
    })
}

//单区域查看
function signalLocationLook(){
    var site=$('#signal-location-selector').val()
    $.cookie('location-select',site,{path:'/'})
    location.href="/gflux/index_portal"
}

//对比查看
function vsLook(){
    var site=$('#vs-site-selector').val()
    if(!site){
        alert('请选择站点!')
        return
    }
    //update cache
    $.cookie('site-select',site,{path:'/'})

    var type_obj=$('#id_type_obj').val()
    var type_vs=$('#id_type_vs').val()
    var start_date=$('#id_start_date').val()
    var end_date=$('#id_end_date').val()

    $.cookie('start-date-select',start_date,{path:'/'})
    $.cookie('end-date-select',end_date,{path:'/'})
    $("input[name='start_date']").val(start_date)
    $("input[name='end_date']").val(end_date)

    var url=''
    if(type_obj=='FUEL' && type_vs=='HB')
        url+='/gflux/__dash__/oil_mo_m_trend_dash?'
    else if(type_obj=='FUEL' && type_vs=='TB')
        url+='/gflux/__dash__/oil_yo_y_trend_dash?'
    else if(type_obj=='NONE-FUEL' && type_vs=='HB')
        url+='/gflux/__dash__/goods_mo_m_trend_dash?'
    else if(type_obj=='NONE-FUEL' && type_vs=='TB')
        url+='/gflux/__dash__/goods_yo_y_trend_dash?'
    else
        return

    url+='&site='+site
    url+='&start_date='+start_date
    url+='&end_date='+end_date
    location.href=url
}

//监视site过滤器的改变
function bindSiteSelect(){
    $('#vs-site-selector').change(function(){
        var option=$("#vs-site-selector option:selected").val()

        //取得站点的最新最旧时间
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
                        $.cookie('date-select',data.lastest_second_date,{path:'/'})
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
                }
            }
        }).always(function(){
            $.cookie('site-select',option,{path: '/' })
        })
    })
}
