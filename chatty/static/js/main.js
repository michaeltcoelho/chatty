(function () {

    var MessageType = {
        JOIN: 0,
        LEAVE: 1,
        PUBLIC: 2,
        PRIVATE: 3,
        AUTH: 4,
        INFO: 5,
        ERROR: 6, 
    };

    var connection = new WebSocket('ws://localhost:8080/chat/');
    connection.onopen = function() {
        connection.send(JSON.stringify({
            type: MessageType.AUTH,
            token: 'xxx',
        }));
    };
    connection.onmessage = function(event) {
        console.log(JSON.parse(event.data));
    };
})();
