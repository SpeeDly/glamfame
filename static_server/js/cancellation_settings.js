$(document).ready(function(){
    $('input:radio[name="cancel_id"]').change(function(){
        if ($(this).is(':checked') && $(this).val() == '-1') {
            $("div.custom").removeClass("hidden");
        }
        else{
            $("div.custom").addClass("hidden");
        }
    });

    $(".message .close a").click(function(){
        $("ul.message").remove();
    });
});