$(document).ready(function(){
    // Форма регистрации
    $('#registerForm').on('submit', function(e){
        e.preventDefault();
        $.ajax({
            url: '/register',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                name: $('#firstName').val(),
                surname: $('#lastName').val(),
                login: $('#login').val(),
                password: $('#password').val()
            }),
            success: function(data){
                if (data.result){
                    // Если регистрация успешна, перенаправляем на чат
                    alert('Регистрация успешна!');
                    window.location.href = '/chat';
                } else {
                    alert(data.message || 'Ошибка регистрации');
                }
            },
            error: function(xhr){
                alert('Ошибка при регистрации');
            }
        });
    });

    // Форма авторизации
    $('#authorizationForm').on('submit', function(e){
        e.preventDefault();
        $.ajax({
            url: '/login',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                login: $('#login').val(),
                password: $('#password').val()
            }),
            success: function(data){
                if (data.result){
                    window.location.href = '/chat';
                } else {
                    alert(data.message || 'Ошибка авторизации');
                }
            },
            error: function(xhr){
                alert('Ошибка при авторизации');
            }
        });
    });

    // Отправка сообщения в чате
    $('#sendButton').on('click', function(){
        var receiverId = $('#receiverId').val();
        var text = $('#messageInput').val().trim();
        
        if (!receiverId || !text) return;
        
        $.ajax({
            url: '/send_message',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                receiver_id: receiverId,
                text: text
            }),
            success: function(data){
                if (data.result){
                    $('#messageInput').val('');
                    loadMessages(receiverId);
                }
            }
        });
    });
    
    // Обработка Enter в поле ввода сообщения
    $('#messageInput').on('keypress', function(e){
        if (e.which === 13) {
            $('#sendButton').click();
        }
    });
    
    // Автоматическая загрузка сообщений каждые 3 секунды
    setInterval(function(){
        var receiverId = $('#receiverId').val();
        if (receiverId) {
            loadMessages(receiverId);
        }
    }, 3000);
});

// Функция загрузки сообщений
function loadMessages(receiverId) {
    $.ajax({
        url: '/get_messages',
        type: 'GET',
        data: { user_id: receiverId },
        success: function(messages){
            var messagesContainer = $('#messagesContainer');
            messagesContainer.empty();
            
            $.each(messages, function(index, msg){
                var messageClass = msg.sender_id == ownerId ? 'sent' : 'received';
                var messageHtml = '<div class="message ' + messageClass + '">' +
                    '<div class="bubble">' + msg.text + '</div>' +
                    '<span class="message-time-small">' + msg.created_at + '</span>' +
                    '</div>';
                messagesContainer.append(messageHtml);
            });
            
            // Прокрутка вниз
            messagesContainer.scrollTop(messagesContainer[0].scrollHeight);
        }
    });
}
