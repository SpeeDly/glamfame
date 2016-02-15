$(document).ready(function(){
    $('#id_style').select2({
    minimumResultsForSearch: "3",
    containerCssClass: "location_select2",
    dropdownCssClass: $("#location_select").data("dropdown-class")
});

    $('#id_duration').select2({
        minimumResultsForSearch: "3",
        containerCssClass: "blue",
        dropdownCssClass: 'blue'
    });

    $('#id_tags:not(.listing_edit)').select2({
        tags:[],
        tokenSeparators: [",", " "],
        containerCssClass: 'tags',
        minimumResultsForSearch: "2",
        query: function (query) {
            data = {results:[]};
            if(query.term.length > 2)
            {
                console.log(query);
            $.ajax({
                type: "GET",
                url: "/autocomplete_tags/",
                data: {"q": query.term},
            })
            .done(function(d)
            {
                for(var i = 0; i<d.length; i++){
                    data.results.push({"id": d[i], "text": d[i]});
                }
                data.results.push({"id": query.term, "text": query.term});
                query.callback(data);
            });
            }
        }
    });

    $('#id_tags.listing_edit').select2({
        tags:["red", "green", "blue"],
        data:[{"id": "123", "text": "red"}],
        tokenSeparators: [",", " "],
        containerCssClass: 'tags',
        minimumResultsForSearch: "0",
        query: function (query) {
            data = {results:[]};
            if(query.term.length > 2)
                {
                    console.log(query);
                $.ajax({
                    type: "GET",
                    url: "/autocomplete_tags/",
                    data: {"q": query.term},
                })
                .done(function(d)
                {
                    for(var i = 0; i<d.length; i++){
                        data.results.push({"id": d[i], "text": d[i]});
                    }
                    data.results.push({"id": query.term, "text": query.term});
                    query.callback(data);
                });
            }
        },
        initSelection: function (item, callback) {
            var data = [];
            $.each($(".tags_initial").data("initial").split(","),function(i,e){
                var text = e;
                data.push({ id: text, text: text });
            });
            callback(data);
        }
    });
});

$('#id_picture').change(function(){$(".wrong_picture").fadeOut(750,function(){$(this).remove();});});
$('input:radio').change(function(){
    var $errorlist = $(this).closest(".gender").find(".errorlist");
    $errorlist.remove();
});



var FILES_TO_SUBMIT = []; // 2D index-->file
var ALLOWED_FILES_TYPES = ["image/jpeg"]; //contain only allowed file's type
var file_number = 0; //the count of all files
var all_context = [];
var all_images = [];
var all_src = [];


$("#id_picture").on("change", function(){
    previewImage(this);
});

//reendering all images
    function drawImages(){
        for(var i=0, len=FILES_TO_SUBMIT.length; i<len; i++){
            var canvas = document.getElementById("pic_" + FILES_TO_SUBMIT[i][0]);
            var context = canvas.getContext('2d');
            var img_obj = new Image();
            img_obj.src = all_src[i];
            all_images.push(img_obj);
            all_context.push(context);
        }

        all_images[all_images.length-1].onload = function() {
            for(var i=0, len=all_images.length; i<len; i++){
                if (all_images[i].width>all_images[i].height)
                    all_context[i].drawImage(all_images[i], 0, 0, all_images[i].width, all_images[i].height, 0, 0, 190, 125);
                else{
                    all_context[i].drawImage(all_images[i], 0, 0, all_images[i].width, all_images[i].height, 0, 0, 190, 125);
                }
            }
            all_context = [];
            all_images = [];
        };
    }

//add element to #uploaded
    function displayElements(){
        
        $ ("#gallery_preview .ready_photo:not(.old)").remove();

        for(var i=0, len=FILES_TO_SUBMIT.length; i<len; i++)
        {
            var file = FILES_TO_SUBMIT[i][1];

            var element_id = FILES_TO_SUBMIT[i][0];
            var html_el = '<li class="ready_photo" data-send="'+ element_id +'">';
            html_el += '<canvas id="pic_' + element_id + '" width="190" height="125"/>';
            html_el += '<ul class="action"><li class="delete">DELETE</li><li class="cover_photo">COVER PHOTO</li></ul>';
            $ ("#gallery_preview>ul").html($ ("#gallery_preview>ul").html() + html_el);
        }
        drawImages();
    }

//on input change
    function previewImage(input){

        files = input.files;

        for (var i = 0; i < files.length; i++)
        {

            if(isValid(files[i]))
            {

                FILES_TO_SUBMIT.push([file_number, files[i]]);
                file_number++;

                var reader = new FileReader();
                reader.onload = function(e) {
                    var src = e.target.result;
                    all_src.push(src);
                }
                    reader.readAsDataURL(files[i]);
            }
        }
        drawCanvasImage();
    }

//execute the code when all files are loaded
    function drawCanvasImage(){
        timeId = setInterval(function(){
            if(all_src.length == FILES_TO_SUBMIT.length)
            {
                displayElements();
                clearInterval(timeId);
            }
        },500);
    }

//make validation
    function isValid(file)  {
        // var extension = file.type.toLowerCase();
        // if (ALLOWED_FILES_TYPES.indexOf(extension) == -1)
        //  return false;
        // else return true;
        return true;
    }


// delete img from the #uploaded
$("#gallery_preview").on("click", ".delete", function(){

    var $check = $(this).closest(".ready_photo");

    if($check.data("send") !== undefined){
        var file_index = $check.data("send");
        $(this).closest(".ready_photo").hide(600, function() {
            $(this).remove();
        });

        for(var i=0, len=FILES_TO_SUBMIT.length; i<len; i++){
            if (file_index == FILES_TO_SUBMIT[i][0]){
                FILES_TO_SUBMIT.splice(i, 1);
                all_src.splice(i,1);
            }
        }
    }
    else{
        $('#id_deleted').val($('#id_deleted').val() + $check.data("path") + ',');
        $(this).closest(".ready_photo").hide(600, function() {
            $(this).remove();
        });
    }
});

$("#gallery_preview").on("click", ".cover_photo", function(){
    
    $('#gallery_preview>ul li').removeClass("active");
    var $closest_li = $(this).closest(".ready_photo");
    $closest_li.addClass("active");
    if($closest_li.data("send") !== undefined){
        $('#id_cover').val($closest_li.data("send"));
        console.log($('#id_cover').val());
    }
    else{
        $('#id_cover').val($closest_li.data("path"));
    }
});

//Upload picture
$('.listing_upload').submit(function(e) {

    $('body').append("<div class='uploading waiting'></div>");
    $('.uploading').css({
        "height": $(document).height(),
        "width": $(document).width()
    });

    for(var i=0; i<all_src.length; i++)
        $(".listing_upload").append("<input type='hidden' name='files' value='" + all_src[i] + "'/>");
});