        $(document).ready(function(){

            autocomplete = new google.maps.places.Autocomplete(
            (document.getElementById('id_address')),
            {
                types: ['geocode'] 
            });
            
            google.maps.event.addListener(autocomplete, 'place_changed', function() {
                lat = autocomplete.getPlace().geometry.location.lat();
                lng = autocomplete.getPlace().geometry.location.lng();
                $("#id_lat").val(lat);
                $("#id_lng").val(lng);
            });

            $.getJSON('http://maps.googleapis.com/maps/api/geocode/json?latlng=' + $("#id_lat").val() +
             ',' + $("#id_lng").val() + '&sensor=false',
            function(data){
                console.log(data);
                $('#id_address').val(data.results['0']['formatted_address']);
            });

            $ ("#artist_profile .bottom_line li").click(function(){
                $(this).parent().children().removeClass("active");
                $(this).addClass("active");
            });

            $('#id_style').select2({
                minimumResultsForSearch: "3",
                containerCssClass: "location_select2",
                dropdownCssClass: $("#location_select").data("dropdown-class")
            });

            $("#settings input, #settings textarea").attr("disabled", "disabled");

            $(".edit").click(function(){
                $(".small_button.change, .small_button.save, .small_button.cancel").removeClass("hidden");
                $(".edit").addClass("hidden");
                $("#settings input, #settings textarea").removeAttr("disabled", "disabled");
            });
            $(".small_button.cancel").click(function(){location.reload();});
        
            $(".message .close a").click(function(){
                $("ul.message").remove();
            });
        });