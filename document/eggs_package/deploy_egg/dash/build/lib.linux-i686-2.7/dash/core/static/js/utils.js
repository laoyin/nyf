/*工具方法*/

//取得对象类型
function getTypeOf(x){
    if(x==null){
        return "null";
    }
    var t= typeof x;
    if(t!="object"){
        return t;
    }
    var c=Object.prototype.toString.apply(x);
    c=c.substring(8,c.length-1);
    if(c!="Object"){
        return c;
    }
    if(x.constructor==Object){
        return c
    }
    if("classname" in x.prototype.constructor
            && typeof x.prototype.constructor.classname=="string"){
        return x.constructor.prototype.classname;
    }
    return "<unknown type>";
}

//阻止事件传递
function preventDefault(event) {
    if (event.preventDefault) {
        event.preventDefault();
    } else {
        event.returnValue = false;
    }
}

//模态对话框
var modalhtml='<div class="modal fade">\
  <div class="modal-dialog">\
    <div class="modal-content">\
      <div class="modal-header">\
        <button type="button" class="close" data-dismiss="modal"><span aria-hidden="true">&times;</span><span class="sr-only">Close</span></button>\
        <h4 class="modal-title" id="infoModal_header">Modal title</h4>\
      </div>\
      <div class="modal-body" id="infoModal_body">\
        <p>One fine body&hellip;</p>\
      </div>\
      <div class="modal-footer">\
        <button type="button" class="btn btn-primary" data-dismiss="modal">OK</button>\
      </div>\
    </div><!-- /.modal-content -->\
  </div><!-- /.modal-dialog -->\
</div><!-- /.modal -->';

///* 当有一个modal dialog已经显示时，我们必须将其它的modal dialog加入队列 */
var modal_dialogs=[];
var modal_dialog_shown=false;
var curr_modal_dialog_id=null;
var curr_modal_body=''
var nb_modal_dialogs=0;

///*Modal function*/
function infoModal(body,head,btn_text,callback){
    var body=body||'An error has occurred, Please try again.';
    //get modal and set info
    var modal_id=getModal();
    $(modal_id).find('#infoModal_header').text(head || 'Info');
    $(modal_id).find('#infoModal_body').attr('class',"modal-body alert-info").text(body);
    $(modal_id).find('#infoModal_footer').find('.chookka-ui-btn').text(btn_text || 'Close');
    $(modal_id).one('hidden.bs.modal.bs.modal', function () {
        if(callback)
            callback()
        modalHidden();
    });
    //check to show
    if(modal_dialog_shown){
        if(body!=curr_modal_body)
            modal_dialogs.push(modal_id);
    }
    else{
        modal_dialog_shown=true;
        curr_modal_dialog_id=modal_id;
        curr_modal_body=body
        $(modal_id).modal()
    }
}
function errorModal(body,head,callback){
    var body=body||'An error has occurred, Please try again.';
    //判断是否未登录
    if(body=='Not logged in' || body=='Cookie is expired'){
        body='Your session has expired, or you have logged in from another device.'
        infoModal(body,'Sorry',function(){
            if(callback){
                callback()
            }
            location.href="/chookka/logout";
        })
    }else{
        infoModal(body,'Sorry',callback)
    }
}
function warningModal(body,head,callback){
    var body=body||'An error has occurred, Please try again.';
    //get modal and set info
    var modal_id=getModal();
    $(modal_id).find('#infoModal_header').text(head || 'Warning');
    $(modal_id).find('#infoModal_body').attr('class',"modal-body alert").text(body);
    $(modal_id).one('hidden.bs.modal', function () {
        if(callback)
            callback()
        modalHidden();
    });
    //check to show
    if(modal_dialog_shown){
        if(body!=curr_modal_body)
            modal_dialogs.push(modal_id);
    }
    else{
        modal_dialog_shown=true;
        curr_modal_dialog_id=modal_id;
        curr_modal_body=body;
        $(modal_id).modal();
    }
}
function successModal(body,head,callback){
    var body=body||'Done.';
    //get modal and set info
    var modal_id=getModal();
    $(modal_id).find('#infoModal_header').text(head || 'Success');
    $(modal_id).find('#infoModal_body').attr('class',"modal-body alert-success").text(body);
    $(modal_id).one('hidden.bs.modal', function () {
        if(callback)
            callback()
        modalHidden();
    });
    //check to show
    if(modal_dialog_shown){
        if(body!=curr_modal_body)
            modal_dialogs.push(modal_id);
    }
    else{
        modal_dialog_shown=true;
        curr_modal_dialog_id=modal_id;
        curr_modal_body=body;
        $(modal_id).modal();
    }
}
function modalHidden(){
    modal_dialog_shown=false;
    //remove node
    $(curr_modal_dialog_id).remove();
    //check to show
    if(modal_dialogs.length>0){
        var id=modal_dialogs.shift();
        modal_dialog_shown=true;
        curr_modal_dialog_id=id;
        curr_modal_body=$(id).find('#infoModal_body').attr('class',"modal-body alert-success").text();
        $(id).modal();
    }
}
function getModal(){
    //add node and return id
    nb_modal_dialogs+=1;
    $_new=$(modalhtml);
    var now=new Date();
    var id=nb_modal_dialogs+'_opoa_infoModal_'+now.getTime();
    $_new.attr('id',id);
    $('body').append($_new);
    return '#'+id;
}

//字符串结尾判断
String.prototype.endWith=function(str){
    if(str==null||str==""||this.length==0||str.length>this.length){
        return false;
    }
    if(this.substring(this.length-str.length)==str){
        return true;
    }else{
        return false;
    }
    return true;
}

//字符串开始判断
String.prototype.startWith=function(str){
    if(str==null||str==""||this.length==0||str.length>this.length){
        return false;
    }
    if(this.substr(0,str.length)==str){
        return true;
    }else{
        return false;
    }
    return true;
}

//格式化字符串
String.format = function(src){
    if (arguments.length == 0) return null;
    var args = Array.prototype.slice.call(arguments, 1);
    return src.replace(/\{(\d+)\}/g, function(m, i){
        return args[i];
    });
};

//字符串替换
String.prototype.replaceAll=function(src,des){
    var re=new RegExp(src.replace(/([\(\)\[\]\{\}\^\$\+\-\*\?\.\"\'\|\/\\])/g,"\\$1"),"ig");
    return this.replace(re,des);
}

//resolve ajax post method csrf https://docs.djangoproject.com/en/dev/ref/contrib/csrf/
jQuery(document).ajaxSend(function(event, xhr, settings) {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
    }
    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});


var EventUtil = {
    addHandler: function (element, type, handler) {
        if (element.addEventListener) {
            element.addEventListener(type, handler, false);
        } else if (element.attachEvent) {
            element.attachEvent("on" + type, handler);
        } else {
            element["on" + type] = handler;
        }
    },
    getKeyCode:function (event){
        return event.keyCode ? event.keyCode : event.which ? event.which : event.charCode;
    },
    getEvent: function (event) {
        return event ? event : window.event;
    },
    getClipboardText: function (event) {
        var clipboardData = (event.clipboardData || window.clipboardData);
        var data='',data_type='insertHTML';
        try{
            data=clipboardData.getData("text/html");
        }catch(e){
            //ie
            data=clipboardData.getData("text");
            //使用pre保持格式
            data='<pre>'+data+'</pre>';
        }
        if(data==''){
            data=clipboardData.getData('text/plain')
            data_type='insertTEXT'
        }else{
            data=getCleanHtml(data)
        }
        return [data_type,data];
    },
    setClipboardText: function (event, value) {
        if (event.clipboardData) {
            return event.clipboardData.setData("text/plain", value);
        } else if (window.clipboardData) {
            return window.clipboardData.setData("text", value);
        }
    },
    preventDefault: function (event) {
        if (event.preventDefault) {
            event.preventDefault();
        } else {
            event.returnValue = false;
        }
    }
};
