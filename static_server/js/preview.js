var iter = true;

$("#id_avatar").change(function(){
    read_url(this);
});


function read_url(input) {

    if (input.files && input.files[0]) {
        var reader = new FileReader();

    if (iter){
        if($('.avatar div').length === 0)
            $('.upload_button').parent().find("#preview").remove().end().prepend("<canvas id='preview' width='165px' height='165px'></canvas>");
        else
            $('.avatar div').append("<canvas id='preview' width='165px' height='165px' style='margin-left:0px'></canvas>");
        iter = false;
    }

        reader.onload=function(e){
            show_image(e.target.result);
        };

        reader.readAsDataURL(input.files[0]);
    }

}


$("#step_2").submit(function(){
    if($('canvas')[0])
        $('#id_cropped_image')[0].value = $('canvas')[0].toDataURL();
});

$("#forms.m_step2").submit(function(){
    if($('canvas')[0])
        $('#id_cropped_image')[0].value = $('canvas')[0].toDataURL();
});

$("#settings").submit(function(e){
    if($('canvas')[0])
        $('#id_cropped_image')[0].value = $('canvas')[0].toDataURL();
});



function show_image(src){
    $("body").append('<div id="img_container"><div class="forms crop_me"><div class="text">Please drag the circle around your face and save your selection</div><img style="width: 100%; height: auto;" id="img_crop" src='+src+' style="position: relative;"></img><input type="button" class="custom_button" onclick="clear_all()" value="Save selection"></div></div>');
    
    $('#img_crop').load(function(){
    });

    // $('#img_container').animate({
    //     height: "+100%"
    //     }, 1000, function() {
    //     alert("me")
    // });

    $('img#img_crop').imgAreaSelect({
        handles: true,
        aspectRatio: '1:1',
        fadeSpeed: 200,
        onSelectEnd: draw_image,
        onInit: draw_image,
        x1: 0,
        y1: 0,
        x2: 170,
        y2: 170
    });
}

function draw_image(img, selection){
    
    src = img.src;

    canvas = document.getElementById("preview");
    var canvas_img=new Image();
    var ctx=canvas.getContext("2d");
    canvas_img.onload=function(){

        wc = this.width/$('#img_crop').width();
        hc = this.height/$('#img_crop').height();

        x1 = selection.x1*wc;
        y1 = selection.y1*hc;

        s_width = selection.width*wc;
        s_height = selection.height*hc;

        ctx.drawImage(canvas_img,x1,y1,s_width,s_height,0,0,165,165);
    };
    canvas_img.src = src;
}

function clear_all(){
    
    $('#img_container').remove();
    $(".avatar div img").remove();
    $('div[class^=imgareaselect-]').hide();
}


$("#id_picture").change(function(){
    read_url2(this);
});


function read_url2(input) {

    if (input.files && input.files[0]) {
        var reader = new FileReader();

    if (iter){
        $('#upload_listing').append("<canvas class='listing' width='492' height='277'></canvas>");
        iter = false;
    }

        reader.onload=function(e){
            draw_image2(e.target.result);
        };

        reader.readAsDataURL(input.files[0]);
    }

}

// Tools for listing edit

var img_canvas = null;
var img_ctx = null;
var rot = $('#id_rotated');
var img_src;

function draw_image2(src){

    canvas = $('.listing')[0];
    var canvas_img = new Image();
    var ctx = canvas.getContext("2d");
    canvas_img.onload=function(){
        ctx.drawImage(canvas_img,0,0,canvas_img.width,canvas_img.height,0,0,492,277);
    };
    canvas_img.src = src;
    img_src = src;

    img_ctx = ctx;
    img_canvas = canvas_img;
}

    var angleInDegrees = 0;
    
    $(".rotate_right").click(function(e){
        angleInDegrees += 90;

        if(parseInt(rot.val()) == 3)
            rot.val(0);
        else
            rot.val(parseInt(rot.val())+1);
        
        drawRotated(angleInDegrees);
    });

    $(".rotate_left").click(function(){
        angleInDegrees -= 90;

        if(parseInt(rot.val()) == 0)
            rot.val(3);
        else
            rot.val(parseInt(rot.val())-1);

        drawRotated(angleInDegrees);
    });

    function drawRotated(degrees){
        canvas = $('.listing')[0]; 
        img_ctx.clearRect(0,0,canvas.width,canvas.height);
        img_ctx.save();
        img_ctx.translate(canvas.width/2,canvas.height/2);
        img_ctx.rotate(degrees*Math.PI/180);
        -img_canvas.width/2,-img_canvas.height/2
        if(rot.val() == 0 || rot.val() == 2)
            img_ctx.drawImage(img_canvas, 0, 0, img_canvas.width, img_canvas.height, -492/2, -277/2, 492, 277);
        else
            img_ctx.drawImage(img_canvas, 0, 0, img_canvas.width, img_canvas.height, -277/2, -492/2, 277, 492);

        img_ctx.restore();
        console.log(rot.val())
    }


$('li.nav.crop').click(function(){
    if($('#upload_listing canvas')[0])
    {
        $("body").append('<div id="img_container" class="second"><div class="forms crop_me"><div class="text">Please drag the circle around your face and save your selection</div><img style="width: 100%; height: auto;" id="img_crop" src='+img_src+' style="position: relative;"></img><input type="button" class="custom_button" onclick="clear_all()" value="Save selection"></div></div>');

        $('img#img_crop').imgAreaSelect({
            handles: true,
            aspectRatio: '16:9',
            fadeSpeed: 200,
            onSelectEnd: draw_image,
        });
    }
});