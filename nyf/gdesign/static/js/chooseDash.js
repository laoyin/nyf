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
			xAxis: {
			    categories:xAxis_categories
			},
			yAxis: {
			    title: {
				text: '扩散速度m/s'
			    },
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
				xAxis: {
				    categories: xAxis_categories
				},
				yAxis: {
				    title: {
					text: '扩散速度m/s'
				    },
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
		//输入验证
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
		 },'json')
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
			},'json')
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



















