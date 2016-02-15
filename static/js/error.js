$(function() {
    $("li input, li textarea").each(function(){
        $(this).click(function(){
            $(this).closest("li").prev().find(".errorlist").fadeOut(750,function(){$(this).remove();});
            $(this).closest("li").prev().find(".errorlist").remove();
        });
    });
});