var FILES_TO_SUBMIT = []; // 2D index-->file
var ALLOWED_FILES_TYPES = ["image/jpeg"]; //contain only allowed file's type
var file_number = 0; //the count of all files
var uploaded_file_count = 0; // how much files are already in the upload field
var all_context = [];
var all_images = [];
var all_src = [];
var deleted_items = []; // contain the deleted elements


$("#ginit").on("change", function(){
	previewImage(this);
});

//reendering all images
	function drawImages(){
		for(var y=0; y<(file_number); y++){
			if (deleted_items.indexOf(y) == -1){
				var canvas = document.getElementById("pic_" + y);
				var context = canvas.getContext('2d');
				var img_obj = new Image();
				img_obj.src = all_src[y];
				all_images.push(img_obj);
				all_context.push(context);
			}
		}
		image_to_display = file_number-deleted_items.length-1

		all_images[image_to_display].onload = function() {
			for(var i=0; i<=image_to_display; i++){
				all_context[i].drawImage(all_images[i], 0, 0, all_images[i].width, all_images[i].height, 0, 0, 180, 101);
			}
			all_context = [];
			all_images = [];
		}
	}

//add element to #uploaded
	function displayElements(){
		for (var i = uploaded_file_count; i < file_number; i++) 
		{
			var element_id = 'pic_' + i; 
			var html_el = '<li data-send="'+ i +'"><canvas id="' + element_id + '" width="180" height="101"/><a class="cancel_button"></a></li>'
			$ ("#gallery_preview").html($ ("#gallery_preview").html() + html_el);
			uploaded_file_count++;
		}
		drawImages();
	}

//on input change
	function previewImage(input){
		$(input).after('<input type="file" name="pictures" id="ginit" class="custom_button active_input" multiple onchange="previewImage(this)"/>')
			.removeAttr("onchange").removeClass("active_input").hide();

		files = input.files;

		for (var i = 0; i < files.length; i++)
		{

			if(isValid(files[i]))
			{

				FILES_TO_SUBMIT.push([file_number, files[i]])
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
		if(all_src.length == file_number)
			{
				displayElements();
				clearInterval(timeId);
			}
		},500)
	}

//make validation
	function isValid(file)	{
		// var extension = file.type.toLowerCase();
		// if (ALLOWED_FILES_TYPES.indexOf(extension) == -1)
		// 	return false;
		// else return true;
		return true;
	}


// delete img from the #uploaded
$("#gallery_preview").on("click", ".cancel_button", function(){
	var file_index = $(this).closest("li").data("send");
	$(this).closest("li").hide(600, function() {
		$(this).remove()
	});

	for(var i = 0; i<FILES_TO_SUBMIT.length; i++)
		if (file_index == FILES_TO_SUBMIT[i][0]){
			deleted_items.push(FILES_TO_SUBMIT[i][0]);
			FILES_TO_SUBMIT.splice(i, 1)
		}
});

//Upload picture
$('#step_4').submit(function(e) {

	$('body').append("<div class='uploading waiting'></div>")
	$('.uploading').css({
		"height": $(document).height(),
		"width": $(document).width()
	});

	var data, xhr;
	data = new FormData();

	data.append("csrfmiddlewaretoken", $(this).find("[name='csrfmiddlewaretoken']").val());
	
	xhr = new XMLHttpRequest();
	
	xhr.open( 'POST', '/salons/gallery/', true );

	for (var i = 0; i < FILES_TO_SUBMIT.length; i++)
	{
		data.append('file', FILES_TO_SUBMIT[i][1]);
	}

	xhr.onreadystatechange = function ( response ) { window.location.replace('http://' + window.location.host + '/salons/settings/profile') };

	xhr.send( data );

	e.preventDefault();

	});