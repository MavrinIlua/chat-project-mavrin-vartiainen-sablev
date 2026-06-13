// Обработка формы входа
$(document).ready(function() {
    $('#loginForm').on('submit', function(e) {
        e.preventDefault();
        
        const formData = {
            login: $('#login').val().trim().toLowerCase(),
            password: $('#password').val().trim()
        };
        
        if (!formData.login || !formData.password) {
            showAuthError('Заполните все поля');
            return;
        }
        
        $.ajax({
            url: '/login',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function(response) {
                if (response.success) {
                    window.location.href = response.redirect || '/chat';
                } else {
                    showAuthError(response.error || 'Ошибка при входе');
                }
            },
            error: function(xhr) {
                const response = xhr.responseJSON;
                showAuthError(response?.error || 'Ошибка при входе');
            }
        });
    });
});

// Показ ошибки
function showAuthError(message) {
    $('.error-message').remove();
    $('.auth-card h1').after(`<p class="error-message">${message}</p>`);
}
