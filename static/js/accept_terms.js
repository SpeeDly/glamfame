$(document).ready(function(){
    $(".accept_terms").submit(function(e){
        var checkbox = $(this).find("#accept_terms")[0];
        console.log(checkbox.checked);
        if(checkbox.checked){
            return true;
        }
        else{
            $(".terms").prev().append('<ul class="errorlist"><li>This field is required.</li></ul>');
            e.preventDefault;
            return false;
        }
    });
});
