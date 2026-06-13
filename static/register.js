// Обработка формы регистрации (поддержка и JSON и form data)
$(document).ready(function() {
    $('#registerForm').on('submit', function(e) {
        e.preventDefault();
        
        const formData = {
            name: $('#firstName').val().trim(),
            surname: $('#lastName').val().trim(),
            login: $('#login').val().trim().toLowerCase(),
            password: $('#password').val().trim()
        };
        
        // Валидация
        if (!formData.name || !formData.surname || !formData.login || !formData.password) {
            showAuthError('Заполните все поля');
            return;
        }
        
        if (formData.password.length < 6) {
            showAuthError('Пароль должен быть не менее 6 символов');
            return;
        }
        
        $.ajax({
            url: '/register',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            dataType: 'json',
            success: function(response) {
                if (response.status === 'registered') {
                    // Перенаправление на страницу входа
                    window.location.href = '/login';
                } else if (response.error) {
                    showAuthError(response.error);
                }
            },
            error: function(xhr) {
                const response = xhr.responseJSON;
                if (response && response.error) {
                    showAuthError(response.error);
                } else {
                    showAuthError('Ошибка при регистрации: ' + xhr.status);
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
