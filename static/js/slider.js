$(function() {
    if (window.location.search.indexOf('budget') != -1){
        values = getUrlVars()["budget"].split('-')
    }
    else{
        values = [0,500]
    }
    $( "#slider-range" ).slider({
        range: true,
        min: 0,
        max: 500,
        values: [ parseInt(values[0]), parseInt(values[1]) ],
        slide: function( event, ui ) {
            $( "#amount" ).val( ui.values[ 0 ] + "-" + ui.values[ 1 ] );
            $( "a.ui-slider-handle" ).eq(0).find("span").text("$" + ui.values[ 0 ]);
            $( "a.ui-slider-handle" ).eq(1).find("span").text("$" + ui.values[ 1 ]);
        },
        stop: function( event, ui ) {
            apply_changes()
        }
    });
    
    $( "a.ui-slider-handle" ).eq(0).append('<span>' + "$" + $( "#slider-range" ).slider( "values", 0 ) + '</span>');
    $( "a.ui-slider-handle" ).eq(1).append('<span>' + "$" + $( "#slider-range" ).slider( "values", 1 ) + '</span>');
    $( "#amount" ).val( $( "#slider-range" ).slider( "values", 0 ) + "-" + $( "#slider-range" ).slider( "values", 1 ) );
});