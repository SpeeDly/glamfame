            // start facebook share

            $('.like').click(function(){openWin()})
            function openWin() {
                url = 'http://www.facebook.com/sharer/sharer.php?s=100&p[url]=http://{{ request.get_host }}{{ request.get_full_path }}&p[images][0]=http://{{ request.get_host }}{{listing.picture}}&p[title]={{ listing.title }}&p[summary]={{ listing.description }}'
                myWindow = window.open(url, '', 'width=800,height=500');
                myWindow.focus();
            }

            $.getJSON('http://graph.facebook.com/?id=http://{{ request.get_host }}{{ request.get_full_path }}',
            function(data){
                $('.like').append(data['shares'] ? data['shares']: 0);
            });
            // end facebook share


            // start tweeter
            !function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0];if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src="https://platform.twitter.com/widgets.js";fjs.parentNode.insertBefore(js,fjs);}}(document,"script","twitter-wjs");

            $('.tweet').click(function(){
                url = 'https://twitter.com/share?text=nafsfawf'
                myWindow = window.open(url, '', 'width=800,height=400');
                myWindow.focus();
            });

                $.ajax({
                    url: 'http://urls.api.twitter.com/1/urls/count.json?url=http://{{ request.get_host }}{{ request.get_full_path }}',
                    dataType: 'jsonp',
                    success: function(data){
                        $('.tweet').append(data['count'])
                        }
                });

            // end tweeter


            // start pin section
            $('.pin').click(function(){ 
                $(this).next().click()
                });

            $('.pin').append( $('.pin+a span').text()? $('.pin+a span').text() : 0);

            // end favorite section


            // start google +

            $('.google_plus').click(function(){
                url = 'https://plus.google.com/share?url={{ request.get_host }}{{ request.get_full_path }}'
                myWindow = window.open(url, '', 'width=500,height=400');
                myWindow.focus();
            })


            $('.map div.container').click(function(){
                $('.check_map').show();
                draw_map()
            });

            $('.check_map').click(function(e){
                if($(e.target).hasClass('check_map'))
                    $(this).hide()
            })

            function draw_map(){
                var map_canvas = document.createElement('div');
                map_canvas.id = 'map_canvas';
                map_canvas.style.height = '100%';
                map_canvas.style.width = '100%';

                document.getElementById('location').appendChild(map_canvas);

                var coords = new google.maps.LatLng({{ artist.lat }}, {{ artist.lng }});
                
                var options = {
                    zoom: 17,
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
                    title:"You are here!",
                    animation: google.maps.Animation.DROP,
                });
            }