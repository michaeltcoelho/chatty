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

    var Connection = undefined,
        People = []
        Messages = [];

    function render_users() {
        var element = document.getElementById('users'),
            tags = [];
        for (var i = People.length - 1; i >= 0; i--) {
            tags.push('<li>' + People[i] + '</li>');
        };
        element.innerHTML = tags.join('');
    };

    function render_message(message) {
        var tag = document.createElement('p');
        if (message.type == MessageType.PRIVATE) {
            message = '<i>Private message from <b>@' + message.from + ':</b> ' + message.text + '</i>';
        } else if (message.type == MessageType.PUBLIC) {
            message = '<b>@' + message.from + ':</b> ' + message.text;
        } else if (message.type == MessageType.JOIN) {
            message = message.user + ' joined room';
        } else if (message.type == MessageType.LEAVE) {
            message = message.user + ' leaved room';
        };
        document.getElementById('messages').insertAdjacentHTML('beforeend', '<p>' + message + '</p>');
    };

    function send_message() {
        var text = document.getElementById('message-text').value;
        if (text.startsWith('@')) {
            var username = text.match(/@\w*/g);
            if (username.length != 0) {
                username = username[0].substring(1, username[0].length);
                message = {
                    type: MessageType.PRIVATE,
                    to: username,
                    text: text.substring(username.length + 2, text.length),
                };
                document.getElementById('messages').insertAdjacentHTML('beforeend', '<p><i>Private message to <b>@' + message.to + ':</b> ' + message.text + '</p>');
            };
        } else {
            message = {
                type: MessageType.PUBLIC,
                text: text,
            };
        };
        Connection.send(JSON.stringify(message));
    };

    function join_chat() {

        Connection = new WebSocket('ws://localhost:8080/chat/');
        Connection.onopen = function() {
            Connection.send(JSON.stringify({
                type: MessageType.AUTH,
                token: document.getElementById('access-token').value,
            }));
        };
        Connection.onmessage = function(event) {
            message = JSON.parse(event.data);
            if (message.type == MessageType.ERROR) {
                alert(message.message);
                window.location = '/';
            } else if (message.type == MessageType.INFO) {
                People = message.users;
                render_users();
            } else {
                render_message(message);
            };
        };
        document.getElementById('login').className = 'hidden';
        document.getElementById('chat').className = 'chat-visible';

        document.getElementById('send-message').addEventListener('click', function(event) {
            send_message();
        });

    };

    document.getElementById('join-chat').addEventListener('click', function(event) {
        join_chat();
    });
})();
