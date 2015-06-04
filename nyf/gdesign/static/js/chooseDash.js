//自定义模拟
         //控制界面的显示
	 function shiftToDefined(){
	    if($("#shiftButtonText").text()=="切换到自定义模拟"){
		    $("#defaultSimulation").hide();
		    $("#definedSimulation").show();
		    $("#definedsimulationCondition").show();
		    $("#shiftButtonText").text("返回到常规模拟")
	    }
	    else{
		    $("#definedSimulation").hide();
		    $("#defaultSimulation").show();
		    $("#definedsimulationCondition").hide();
		    $("#shiftButtonText").text("切换到自定义模拟")
		    $("#definedCondition").hide()
	    }

	 }

	//选择自定义模拟图
	function chooseDash(){
	    var e=event;
	    var id=e.srcElement.id
	    var tempString="#"+id
	    var text=$(tempString).text()
	    $("#chooseDash").text(text)
	    $("#definedCondition").show()
	    if (text=="扩散速度图"){
	  	//初始化变量
                dashId=0
		title_text=text
		//显示用户交互界面
		$("#windSpeed").show()
		$("#dischargeSpeed").hide() 
		requestData()
	    }
	    else if(text=="速度比较图"){
		  //初始化变量
		dashId=1
		title_text=text
	   //显示用户交互界面
		$("#windSpeed").show()
		$("#dischargeSpeed").show()
		requestData()
	    }
	    else if (text=="扩散浓度图"){
	 	 //初始化变量
		dashId=2
		title_text=text
	   //显示用户交互界面
		$("#windSpeed").hide()
		$("#dischargeSpeed").show()
		requestData()
	    }
	    else if(text=="浓度比较图"){
		//初始化变量
                dashId=3
		title_text=text
	   //显示用户交互界面
		$("#windSpeed").show()
		$("#dischargeSpeed").show()
		requestData()
	    }
	}

	  //渲染数据
            
		function  diffusionRate(){

		  //扩散速度图
		     $('#definedDash').highcharts({
			title: {
			    text: title_text,
			    x: -20 //center
			},
			credits: {
                                                 enabled: false
                                       },
			xAxis: {
			    categories:xAxis_categories
			},
			yAxis: {
			    title: {
				text: '扩散速度m/s'
			    },
			      lineWidth:1,
            lineColor:'#C0D0E0',
			    plotLines: [{
				value: 0,
				width: 1,
				color: '#808080'
			    }]
			},
			tooltip: {
			    valueSuffix: 'm/s'
			},
			legend: {
			    align: "center",
			    verticalAlign: "bottom",
			    x: 0,
			    y: 0 ,
			},
			series:full_series
		    });
		   
		}
		function rateCompare(){
		    //速度比较图
			    $("#definedDash").highcharts({
				title: {
				    text: title_text,
				    x: -20 //center
				},
				credits: {
                                                 enabled: false
                                       },
				xAxis: {
				    categories: xAxis_categories
				},
				yAxis: {
				    title: {
					text: '扩散速度m/s'
				    },
				      lineWidth:1,
            lineColor:'#C0D0E0',
				    plotLines: [{
					value: 0,
					width: 1,
					color: '#808080'
				    }]
				},
				tooltip: {
				    valueSuffix: 'm/s'
				},
				legend: {
				    align: "center",
				    verticalAlign: "bottom",
				    x: 0,
				    y: 0 ,
				},
				series: full_series
			    });
		}
		function diffusionConcentration(){
		    //扩散浓度图
		      $('#definedDash').highcharts({
			title: {
			    text: title_text,
			    x: -20 //center
			},
			credits: {
                                                 enabled: false
                                       },
			subtitle: {
			    x: -20
			},
			xAxis: {
			     categories: xAxis_categories
			},
			yAxis: {
			    title: {
				text: '扩散浓度'
			    },
			      lineWidth:1,
                                            lineColor:'#C0D0E0',
			    plotLines: [{
				value: 0,
				width: 1,
				color: '#808080'
			    }]
			},
			tooltip: {
			    valueSuffix: '%'
			},
			legend: {
			    align: "center",
			    verticalAlign: "bottom",
			    x: 0,
			    y: 0 ,
			},
			series:full_series
		    });
		}
		function ConcentrationCompare(){
		   //浓度比较图
		      $('#definedDash').highcharts({
			title: {
			    text: title_text,
			    x: -20 //center
			},
			credits: {
                                                 enabled: false
                                       },
			subtitle: {
			    x: -20
			},
			xAxis: {
			     categories: ['100', '200', '300', '400', '500', '600','700', '800', '900', '1000', '1100', '1200']
			},
			yAxis: {
			    title: {
				text: '扩散浓度'
			    },
			lineWidth:1,
			lineColor:'#C0D0E0',
			    plotLines: [{
				value: 0,
				width: 1,
				color: '#808080'
			    }]
			},
			tooltip: {
			    valueSuffix: ''
			},
			legend: {
			    align: "center",
			    verticalAlign: "bottom",
			    x: 0,
			    y: 0 ,
			},
			 series: full_series
		    });
		}

//向后台请求数据
function requestData(){        
		 requestType=0        
                          windSpeed=null
		 dischargeSpeed=null
		 $("#windSpeed")[0].childNodes[1].value=''
		 $("#dischargeSpeed")[0].childNodes[1].value=''
		 xAxis_categories = []
		 full_series = []
		/*//输入验证
		 dict={'dashId':dashId,'requestType':requestType,'default_windSpeed':default_windSpeed,'default_dischargeSpeed':default_dischargeSpeed}
		 //测试ajax请求
		 $.post('/request_simulaton_data/',dict,
			function(data){
			       if(data){
					xAxis_categories=data.categories
					full_series=data.series
					if(dashId == 0){
						diffusionRate()
					}
					else if(dashId == 1){
						rateCompare()
					}
					else if(dashId == 2){
						diffusionConcentration()
					}
					else if(dashId == 3){
						ConcentrationCompare()
					}
			      }
		 },'json')*/
		obj = {'categories':['100', '200', '300', '400', '500', '600','700', '800', '900', '1000', '1100', '1200'],'series':[{'data':[],'name':''}]}
		if(dashId == 0){
			obj.series[0].data =  cal_single_rate_change(5,110)
			obj.series[0].name = '风速'+5+'m/s'
			xAxis_categories=obj.categories
			full_series=obj.series
			diffusionRate()
		}
		else if(dashId == 1){
			obj.series[0].data =  cal_single_rate_change(5,110)
			obj.series[0].name = '风速'+5+'m/s,泄放速度'+110+'m/s'
			xAxis_categories=obj.categories
			full_series=obj.series
			rateCompare()
		}
		else if(dashId == 2){
			obj.series[0].data =  cal_single_concentration_change(5,110)
			obj.series[0].name = '泄放速度'+110+'m/s'
			xAxis_categories=obj.categories
			full_series=obj.series
			diffusionConcentration()
		}
		else if(dashId == 3){
			obj.series[0].data =  cal_single_concentration_change(5,110)
			obj.series[0].name ='风速'+5+'m/s,泄放速度'+110+'m/s'
			xAxis_categories=obj.categories
			full_series=obj.series
			ConcentrationCompare()
		}
}

function simulationRequestData(){
		requestType=1
		if(check()){
			dict={'dashId':dashId,'requestType':requestType}
			if (simulation_windSpeed){
				dict['simulation_windSpeed']=simulation_windSpeed
			}
		 	if(simulation_dischargeSpeed){
				dict['simulation_dischargeSpeed']=simulation_dischargeSpeed
			}
			/*//测试ajax请求
			$.post('/request_simulaton_data/',dict,
			function(data){
			       if(data){
					xAxis_categories=data.categories
					full_series=data.series
					if(dashId == 0){
						diffusionRate()
					}
					else if(dashId == 1){
						rateCompare()
					}
					else if(dashId == 2){
						diffusionConcentration()
					}
					else if(dashId == 3){
						ConcentrationCompare()
					}
			      }
			},'json')*/
			obj = {'categories':['100', '200', '300', '400', '500', '600','700', '800', '900', '1000', '1100', '1200'],'series':[{'data':[],'name':''}]}
			if(dashId == 0){
				obj.series[0].data =  cal_single_rate_change(simulation_windSpeed,110)
				obj.series[0].name = '风速'+simulation_windSpeed+'m/s'
				xAxis_categories=obj.categories
				full_series.push(obj.series[0])
				diffusionRate()
			}
			else if(dashId == 1){
				obj.series[0].data =  cal_single_rate_change(simulation_windSpeed,simulation_dischargeSpeed)
				obj.series[0].name = '风速'+simulation_windSpeed+'m/s,泄放速度'+simulation_dischargeSpeed+'m/s'
				xAxis_categories=obj.categories
				full_series.push(obj.series[0])
				rateCompare()
			}
			else if(dashId == 2){
				obj.series[0].data =  cal_single_concentration_change(10,simulation_dischargeSpeed)
				obj.series[0].name = '泄放速度'+simulation_dischargeSpeed+'m/s'
				xAxis_categories=obj.categories
				full_series.push(obj.series[0])
				diffusionConcentration()
			}
			else if(dashId == 3){
				obj.series[0].data =  cal_single_concentration_change(simulation_windSpeed,simulation_dischargeSpeed)
				obj.series[0].name = '风速'+simulation_windSpeed+'m/s,泄放速度'+simulation_dischargeSpeed+'m/s'
				xAxis_categories=obj.categories
				full_series.push(obj.series[0])
				ConcentrationCompare()
			}
		}
	}
//输入验证
function check(){
	if(dashId==0){
		simulation_windSpeed=$("#windSpeed")[0].childNodes[1].value
		if(simulation_windSpeed==""){			
			alert("风速不能为空")
			return false
		}
		return true
	}
	else if(dashId==1){
		simulation_windSpeed=$("#windSpeed")[0].childNodes[1].value 
		simulation_dischargeSpeed=$("#dischargeSpeed")[0].childNodes[1].value
		if(simulation_windSpeed=="" || simulation_dischargeSpeed=="" ){
			alert("风速或泄放速度不能为空")
			return false 
		}
		return true
	}
	else if(dashId==2){
		simulation_dischargeSpeed=$("#dischargeSpeed")[0].childNodes[1].value
		if(simulation_dischargeSpeed==""){
			alert("风速不能为空")
			return false
		}
		return true
	}
	else if(dashId==3){
		simulation_windSpeed=$("#windSpeed")[0].childNodes[1].value
		simulation_dischargeSpeed=$("#dischargeSpeed")[0].childNodes[1].value
		if(simulation_windSpeed=="" || simulation_dischargeSpeed=="" ){
			alert("风速或泄放速度不能为空")
			return false 
		}
		return true
	}

}




function cal_syngx(A,B,s){
    return A * Math.log(s) + B
}

//计算扩散速度
function cal_single_rate_change(wing_rate,xiefang_rate){
    Q = wing_rate/xiefang_rate
    A = 0.159874 + 0.960923 * Q -1.24869* Q * Q + 0.3728 * Q * Q * Q
    B = -0.478332 + 0.0418951 * Q + 0.153298 * Q * Q
    data = []
    data = [0,0,0,0,0,0,0,0,0,0,0,0]
    for(var i =1;i <=12;i++){
        data[i-1] = cal_syngx(A,B,i*100)
    }
    return data
}

//计算扩散浓度
function cal_single_concentration_change(wing_rate,xiefang_rate){
    Q = wing_rate/xiefang_rate
    A =  -0.0161965+0.00543481*Q-0.00128631*Q*Q
    B =  0.183894*Math.exp(-0.38484*Q)
    data = []
    data = [0,0,0,0,0,0,0,0,0,0,0,0]
    for(var i =1;i <=12;i++){
        data[i-1] = cal_syngx(A,B,i*100)
    }
    return data
}














