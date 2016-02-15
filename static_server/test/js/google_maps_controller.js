if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(success, fail,{timeout:2000});
} else {
    fail();
}

function success(position) {

    // start google maps
    $('#id_address').val(get_current_address(position.coords));

    var map_canvas = document.createElement('div');
    map_canvas.id = 'map_canvas';
    map_canvas.style.height = '336px';
    map_canvas.style.width = '490px';

    document.getElementById('maps').appendChild(map_canvas);

    var coords = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
    
    var options = {
        zoom: 15,
        center: coords,
        mapTypeControl: false,
        navigationControlOptions: {
            style: google.maps.NavigationControlStyle.SMALL
        },
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    
    var map = new google.maps.Map(document.getElementById("map_canvas"), options);

    var marker = new google.maps.Marker({
        position: coords,
        map: map,
        draggable:true,
        title:"You are here!",
        animation: google.maps.Animation.DROP,

    });

    google.maps.event.addListener(marker, 'dragend', 
    function(){
        $.getJSON('http://maps.googleapis.com/maps/api/geocode/json?latlng=' + marker.getPosition().lat() +
         ',' + marker.getPosition().lng() + '&sensor=false',
        function(data){
            $('#id_address').val(data.results['0']['formatted_address']).focus();
        });                                         
    });
    
    $("#maps").closest(".login").submit(function(e){
        $("#id_lat").val(marker.getPosition().lat())
        $("#id_lng").val(marker.getPosition().lng())

    })

    autocomplete = new google.maps.places.Autocomplete(
    (document.getElementById('id_address')),
        { types: ['geocode'] });

    google.maps.event.addListener(autocomplete, 'place_changed', function() {
        set_marker_properly(autocomplete)
    });

    google.maps.event.addListener(map, 'click', function(event) {
        placeMarker(event.latLng);
    });

    function placeMarker(location) {
        if ( marker ) {
            marker.setPosition(location);
        } else {
            marker = new google.maps.Marker({
                position: location,
                map: map
            });
        }

        link = 'http://maps.googleapis.com/maps/api/geocode/json?latlng=' + marker.getPosition().lat() + ',' + marker.getPosition().lng() + '&sensor=false'
        
        $.getJSON(link, function(data){
            $('#id_address').val(data.results['0']['formatted_address']).focus();
            }); 
    }

    function set_marker_properly(autocomplete){
        lat = autocomplete.getPlace().geometry.location.lat();
        lng = autocomplete.getPlace().geometry.location.lng();
        var latlng = new google.maps.LatLng(lat, lng);
        marker.setPosition(latlng);
        map.setCenter(latlng)
    }
}


function get_current_address(position)
{
    $.getJSON(
        'http://maps.googleapis.com/maps/api/geocode/json?latlng=' + position.latitude +
         ',' + position.longitude + '&sensor=false',

        function(data){
            $('#id_address').val(data.results['0']['formatted_address']).focus();
        });
}


function fail(){
    var map_canvas = document.createElement('div');
    map_canvas.id = 'map_canvas';
    map_canvas.style.height = '336px';
    map_canvas.style.width = '490px';

    document.getElementById('maps').appendChild(map_canvas);

    var coords = new google.maps.LatLng(37.09024, -95.712891);
    
    var options = {
        zoom: 3,
        center: coords,
        draggable: true,
        mapTypeControl: false,
        navigationControlOptions: {
            style: google.maps.NavigationControlStyle.SMALL
        },
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    
    var map = new google.maps.Map(document.getElementById("map_canvas"), options);

    google.maps.event.addListener(map, 'click', function(event) {
            placeMarker(event.latLng);
        });

    $("#maps").closest(".login").submit(function(e){
        $("#id_lat").val(marker.getPosition().lat())
        $("#id_lng").val(marker.getPosition().lng())
        console.log($("#id_lat").val())
    })

    var marker;


    function placeMarker(location) {
        if ( marker ) {
            marker.setPosition(location);
        } else {
            marker = new google.maps.Marker({
                position: location,
                map: map,
                draggable: true,
            });
        }

    google.maps.event.addListener(marker, 'dragend', 
    function(){
        $.getJSON('http://maps.googleapis.com/maps/api/geocode/json?latlng=' + marker.getPosition().lat() +
         ',' + marker.getPosition().lng() + '&sensor=false',
        function(data){
            $('#id_address').val(data.results['0']['formatted_address']).focus();
        });                                         
    });

        link = 'http://maps.googleapis.com/maps/api/geocode/json?latlng=' + marker.getPosition().lat() + ',' + marker.getPosition().lng() + '&sensor=false'
        
        $.getJSON(link, function(data){
            $('#id_address').val(data.results['0']['formatted_address']).focus();
            }); 
    }

    $('#id_post_code').keyup(function(){
        $this = $(this).val()

        if($this.length == 5){
            link = 'http://maps.googleapis.com/maps/api/geocode/json?address=' + $this + '&sensor=false'
            $.getJSON(link, function(data){
                lat = data['results'][0]['geometry']['location']['lat']
                lng = data['results'][0]['geometry']['location']['lng']
                LatLng = new google.maps.LatLng(lat, lng);
                map.panTo(LatLng);
                map.setZoom(12);
            });
        }
    });

    autocomplete = new google.maps.places.Autocomplete(
    (document.getElementById('id_address')),
        { types: ['geocode'] });

    google.maps.event.addListener(autocomplete, 'place_changed', function() {
        lat = autocomplete.getPlace().geometry.location.lat();
        lng = autocomplete.getPlace().geometry.location.lng();
        console.log(autocomplete.getPlace())
        var latlng = new google.maps.LatLng(lat, lng);

        if ( marker ) {
            marker.setPosition(latlng);
            
        } else {
            marker = new google.maps.Marker({
                position: latlng,
                map: map,
                draggable: true,
            });
        }
        map.setCenter(latlng);
        map.setZoom(17);

    });

}