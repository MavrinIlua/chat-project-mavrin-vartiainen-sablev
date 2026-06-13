// Обработка формы регистрации
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
                showAuthError(response?.error || 'Ошибка при регистрации');
            }
        });
    });
});

// Показ ошибки
function showAuthError(message) {
    $('.error-message').remove();
    $('.auth-card h1').after(`<p class="error-message">${message}</p>`);
}
