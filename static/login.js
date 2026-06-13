// Обработка формы входа (поддержка и JSON и form data)
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
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    window.location.href = response.redirect || '/chat';
                } else {
                    showAuthError(response.error || 'Ошибка при входе');
                }
            },
            error: function(xhr) {
                const response = xhr.responseJSON;
                if (response && response.error) {
                    showAuthError(response.error);
                } else {
                    showAuthError('Ошибка при входе: проверьте логин и пароль');
                }
            }
        });
    });
});

// Показ ошибки
function showAuthError(message) {
    $('.error-message').remove();
    $('.auth-card h1').after(`<p class="error-message">${message}</p>`);
}
