function supportIE() {
  if ($.browser.msie) {
    $('table.new_silver_table tr th:last-child,table.new_silver_table tr td:last-child').css({ 'border-right': 'none' });
  }
}

$(function() {
  supportIE();
  // setup event listeners
  $('#sidebar > a').on('click', function(e) {
    e.preventDefault();
    if (!$(this).hasClass("active")) {
      var lastActive = $(this).closest("#sidebar").find(".active");
      lastActive.removeClass("active");
      $(this).addClass("active");      
    } else {
      $(this).next('div').slideToggle();
    }
  });
  try {
    if(typeof(eval('init_hook')) == "function") {
      init_hook();
    }
  } catch(e) {}
  
});

function serialize(obj) {
  var str = [];
  for(var p in obj)
     str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
  return str.join("&");
}
