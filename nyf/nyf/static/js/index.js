$(
	function(){
		updatePage = null
		if ($("#blog_linklist").length != 0){
		updatePage=function(){
			var $link_list=$("#link_list a")
			var length=$link_list.length
			var dict={'message':'ok'}
			$.post('/demosite/index/requestlinkdata/',dict,
		                        function(data){
						for (var i=0;i<=length-1;i++){
							$link_list[i].href=data['link_href'][i]
						}	
			},'json')
		
	             }
	 }
	 if(updatePage){
	 	 updatePage()	
	 }
	});
	


function insertBlogURL(){
	var blog_name=$('#blog_name').val();
	var blog_url=$('#blog_url').val();
	var dict={'blog_name':blog_name,'blog_url':blog_url}
	if (blog_name || blog_url){
		$.post('/demosite/index/insert_blog_url/',dict,
                        function(data){
				if(data.ret){
					alert(data.message);			
				}
				else {
					alert(data.message);
				}	
	        },'json')
	}
	else {alert("博客标题或地址不能为空!")}
}