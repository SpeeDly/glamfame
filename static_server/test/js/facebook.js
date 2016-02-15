function register_me(where){

    FB.init({
        appId      : '771259596233505',
        status     : true,
        cookie     : true,
        xfbml      : true
    });

    FB.login(function(response) {
        testAPI();
    },{scope: 'email'});


    function testAPI() {
        FB.api('/me', function(response) {
            console.log(response);
            var data = {};
            var url = "";

            if(where == 'user')
                url = "/users/sign_up/facebook";
            else if(where == 'artist')
                url = "/artists/sign_up/facebook";
            else if(where == 'salon')
                url = "/salons/sign_up/facebook";

            data['facebook_id'] = response.id;
            data['name'] = response.name;
            data['email'] = response.email;
            data['csrfmiddlewaretoken'] = $("input[name='csrfmiddlewaretoken']").val();
            FB.api('/me/picture', {"redirect": false, "height": "160", "type": "normal", "width": "160"}, function(response) {
                data['avatar'] = response.data.url;
                $.ajax({
                    url: url,
                    data: data,
                    type: "POST"
                })
                .done(function(){
                    if(where == 'user')
                        document.location.href="/";
                    else if(where == 'artist')
                        document.location.href="/artists/sign_up?step=2";
                    else if(where == 'salon')
                        document.location.href="/salons/sign_up?step=2";
                })
                .fail(function(){
                    console.log("error");
                });
            });
        });
    }
}


function log_me(){

    FB.init({
        appId      : '771259596233505',
        status     : true,
        cookie     : true,
        xfbml      : true
    });

    FB.login(function(response) {
        testAPI();
    },{scope: 'email'});


    function testAPI() {
        FB.api('/me', function(response) {
            var data = {};
            data['email'] = response.email;
            data['csrfmiddlewaretoken'] = $("input[name='csrfmiddlewaretoken']").val();
            $.ajax({
                url: "/users/login/facebook",
                data: data,
                type: "POST"
            })
            .done(function(){
                document.location.href="/";
            })
            .fail(function(){
                $("#form_1 ul:eq(0)").before('<ul class="errorlist"><li><ul class="errorlist"><li>Invalid login details</li></ul></li></ul>');
            });
        });
    }
}