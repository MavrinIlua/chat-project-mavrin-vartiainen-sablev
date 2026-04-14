# chat-project-mavrin-vartiainen-sablev

Пользователь открывает сайт
        ↓
    index.html — вводит ник + пароль
        ↓
    /login — Flask проверяет БД
        ↓
  Новый ник?          Ник есть + пароль верный?      Пароль неверный?
     ↓                        ↓                            ↓
Регистрируем         Авторизуем                   Ошибка на index.html
     ↓                        ↓
  Сессия["nickname"] = "Илья"
     ↓
  chat.html — страница чата
  