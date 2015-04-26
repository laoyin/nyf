$(function(){
	var message=$("#message").text()
	if(message){
		alert(message)	
		if (message.search("图片") != -1 ){
			window.location.assign("/demosite/uploadFile/")
		}
		else if (message.search("文章") != -1){
			window.location.assign("/demosite/articles/")
		}
		
	}
	setInterval(function () {
		if ( $("#choose").val() != ""){
				if ($("#upload").length != 0){
					$("#upload").click()
					$("#upload").remove()
					$("#choose_image").val("")
				}
  		
  				return 
  			}
	},1000)
	$("#upload_file").on("click",function(){
  		$("#choose").click()	
  	})
  	function upload_event(){
  		$("#upload").click()
  	}
	String.prototype.format= function (src){
		if (arguments.length == 0) return null;
		var args = Array.prototype.slice.call(arguments, 1);
		return src.replace(/\{(\d+)\}/g, function(m, i){
			return args[i];
	});
	}
})