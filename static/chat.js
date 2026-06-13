// Динамический чат через AJAX

$(document).ready(function() {
    let currentDeliverId = null;
    let messageInput = $('#messageInput');
    
    // Выбор собеседника
    $('.user-item').on('click', function() {
        const userId = $(this).data('user-id');
        const userName = $(this).data('user-name');
        
        // Обновление активного пользователя
        $('.user-item').removeClass('active');
        $(this).addClass('active');
        
        // Обновление URL
        const url = new URL(window.location);
        url.searchParams.set('id', userId);
        window.history.pushState({}, '', url);
        
        loadMessages(userId);
    });
    
    // Отправка сообщения
    $('#sendButton').on('click', sendMessage);
    
    messageInput.on('keypress', function(e) {
        if (e.which === 13) {  // Enter
            sendMessage();
        }
    });
    
    // Загрузка сообщений
    function loadMessages(deliverId) {
        currentDeliverId = deliverId;
        
        $.ajax({
            url: '/messages',
            method: 'GET',
            data: { with: deliverId },
            success: function(messages) {
                renderMessages(messages);
            },
            error: function() {
                console.error('Ошибка загрузки сообщений');
            }
        });
    }
    
    // Рендер сообщений
    function renderMessages(messages) {
        const $messagesArea = $('#messagesArea');
        $messagesArea.empty();
        
        if (messages.length === 0) {
            const deliverName = $('.user-item[data-user-id="' + currentDeliverId + '"] .user-name').text();
            $messagesArea.html(`
                <div class="empty-chat">
                    <div class="empty-icon">💬</div>
                    <p>Начните переписку с ${deliverName}</p>
                    <p class="empty-subtitle">Выберите собеседника слева и напишите первым 📩</p>
                </div>
            `);
            return;
        }
        
        messages.forEach(msg => {
            const isSent = msg.owner_id === parseInt(messages[0]?.owner_id) || 
                          msg.owner_id === parseInt($('.chat-container').data('nickname-id'));
            
            // Определение имени автора
            const ownerName = msg.owner_name ? `${msg.owner_name} ${msg.owner_surname}` : 'Пользователь';
            
            const $message = $(`
                <div class="message ${isSent ? 'sent' : 'received'}" data-message-id="${msg.id}">
                    <div class="message-content">
                        <div class="message-text">${escapeHtml(msg.text)}</div>
                        <div class="message-meta">
                            <span class="message-time">${formatTime(msg.timestamp)}</span>
                        </div>
                    </div>
                </div>
            `);
            $messagesArea.append($message);
        });
        
        // Прокрутка вниз
        $messagesArea.scrollTop($messagesArea[0].scrollHeight);
    }
    
    // Отправка сообщения
    function sendMessage() {
        const text = messageInput.val().trim();
        
        if (!text || !currentDeliverId) return;
        
        $.ajax({
            url: '/send',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                deliver_id: currentDeliverId,
                text: text
            }),
            success: function(response) {
                if (response.success) {
                    messageInput.val('');
                    loadMessages(currentDeliverId);
                }
            },
            error: function() {
                console.error('Ошибка отправки сообщения');
            }
        });
    }
    
    // Вспомогательные функции
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    function formatTime(timestamp) {
        if (!timestamp) return '00:00';
        
        const date = new Date(timestamp);
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        return `${hours}:${minutes}`;
    }
    
    // Автоматическая загрузка при открытии чата
    const urlParams = new URLSearchParams(window.location.search);
    const deliverId = urlParams.get('id');
    
    if (deliverId) {
        loadMessages(parseInt(deliverId));
        $('.user-item[data-user-id="' + deliverId + '"]').addClass('active');
    }
});
