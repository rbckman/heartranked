$(window).on("scroll", function() {
  $.cookie("tempScrollTop", $(window).scrollTop());
});
$(function() {
  if ($.cookie("tempScrollTop")) {
    $(window).scrollTop($.cookie("tempScrollTop"));
    alert("loaded postion : " + $.cookie("tempScrollTop"));
  }
});
