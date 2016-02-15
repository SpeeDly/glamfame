var http = require('http');
var server = http.createServer().listen(1332);
var io = require('socket.io').listen(server);

var redis = require('redis');
var sub = redis.createClient();

//Subscribe to the Redis chat channel
sub.subscribe('notification_count');
console.log("Server is running...\nClick on Ctrl+C to exit");

io.sockets.on('connection', function (socket) {
    var user_id = socket["handshake"]["query"]["user_id"];
    
    socket.room = user_id;
    socket.join(user_id);

    socket.on('disconnect', function(){
        socket.leave(socket.room);
    });

    //Grab message from Redis and send to client
});

sub.on('message', function(channel, message){
    var current_room = message.split("___")[0];
    var real_message = message.split("___")[1];
    io.sockets.in(current_room).emit('message', real_message );
});