$(document).ready(function(){
    var $cr = $('input:radio[name="cancel_id"]:checked');
    if($cr.val() == '1'){
        $cr.closest("ul").find("span").addClass("hidden").end().end().closest(".settings").find(".bank_trans").addClass("hidden");
        $cr.closest("li").children("span, input[type='text'], .edit").removeClass("hidden");
    }
    else{
        $cr.closest("ul").find("span").addClass("hidden").end().end().closest(".settings").find(".bank_trans").removeClass("hidden");
        $cr.closest("li").find("span").removeClass("hidden").end().prev().find(".save, .edit, .cancel, input[type='text']").addClass("hidden");
    }
    $('input:radio[name="cancel_id"]').change(function(){
        if ($(this).is(':checked') && $(this).val() == '1') {
            $(this).closest("ul").find("span").addClass("hidden").end().end().closest(".settings").find(".bank_trans").addClass("hidden");
            $(this).closest("li").children("span, input[type='text'], .edit").removeClass("hidden");
        }
        else if ($(this).is(':checked') && $(this).val() == '2'){
            $(this).closest("ul").find("span").addClass("hidden").end().end().closest(".settings").find(".bank_trans").removeClass("hidden");
            $(this).closest("li").find("span").removeClass("hidden").end().prev().find(".save, .edit, .cancel, input[type='text']").addClass("hidden");
        }
    });
    $(".small_button.edit").click(function(){
        $(this).addClass("hidden").parent().children(".save, .cancel").removeClass("hidden").end().parent().find("input[type=text]").removeAttr("disabled").removeAttr("readonly");

    });
    
    $(".small_button.cancel").click(function(){
        location.reload();
    });

    $(".message .close a").click(function(){
        $("ul.message").remove();
    });

});