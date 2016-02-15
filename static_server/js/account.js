$(document).ready(function(){
    $("li.left .edit").click(function(){
        $(this).addClass("hidden").closest(".left").find("input")
            .removeAttr("disabled").removeAttr("readonly")
            .end()
            .find(".cancel, .save").removeClass("hidden");
    });

    $("li.right .edit").click(function(){
        $(this).addClass("hidden").closest(".right").find("input")
            .removeAttr("disabled").removeAttr("readonly")
            .end()
            .find(".cancel, .save").removeClass("hidden")
            .end()
            .find(".old_pass").addClass("hidden")
            .end()
            .find("form").removeClass("hidden");
    });

    $(".small_button.cancel").click(function(){location.reload();});
    $(".message .close a").click(function(){
        $("ul.message").remove();
    });
});