# MySQL-версия ChatApp

> Чат в реальном времени с базой данных MySQL и чатом 1-на-1.

---

## Что это такое?

**ChatApp MySQL** — веб-чат, где пользователи могут переписываться в реальном времени между собой (1-на-1). Использует MySQL для хранения данных.

---

## Возможности

- **Вход по логину и паролю** — авторизация через MySQL
- **Чат 1-на-1** — выбор собеседника из списка пользователей
- **История переписки** — сообщения сохраняются в базе данных MySQL
- **Умное приветствие** — "Доброе утро", "Добрый день", "Добрый вечер" или "Доброй ночи" в зависимости от времени
- **Автоматическое обновление** — новые сообщения появляются каждые 3 секунды
- **Разделители даты** — дата показывается один раз при переходе на новый день

---

## Технологии

| Что | Зачем |
|-----|-------|
| Python 3.12 + Flask | Сервер, маршруты, логика |
| MySQL | База данных (пользователи и сообщения) |
| HTML + Jinja2 | Страницы сайта |
| CSS | Внешний вид |
| JavaScript (fetch) | Динамика без перезагрузки |

---

## Структура проекта

```
mysql_version/
│
├── app.py                ← главный файл: весь Python, маршруты, логика
├── .env                  ← переменные окружения для MySQL
├── README.md             ← описание проекта
├── backlog_mysql.md      ← список задач для MySQL-версии
│
├── templates/            ← HTML-страницы (Flask ищет шаблоны здесь)
│   ├── authorization.html ← страница входа
│   ├── registration.html ← страница регистрации
│   └── chat.html         ← страница чата
│
└── static/               ← файлы, которые браузер скачивает напрямую
    └── style.css         ← стили внешнего вида
```

---

## База данных MySQL

### Таблица users (пользователи)

| Поле | Тип | Описание |
|------|-----|----------|
| id | INT (PK, AUTO_INCREMENT) | Уникальный ID пользователя |
| name | VARCHAR(100) | Имя пользователя |
| surname | VARCHAR(100) | Фамилия пользователя |
| login | VARCHAR(50) | Логин (уникальный) |
| password | VARCHAR(255) | Пароль (хешированный) |

### Таблица messages (сообщения)

| Поле | Тип | Описание |
|------|-----|----------|
| id | INT (PK, AUTO_INCREMENT) | Уникальный ID сообщения |
| sender_id | INT (FK) | ID отправителя |
| receiver_id | INT (FK) | ID получателя |
| text | TEXT | Текст сообщения |
| created_at | DATETIME | Дата и время создания |

---

## Как запустить проект

1. **Установить MySQL и XAMPP** (если ещё не установлен)

2. **Создать базу данных и таблицы**
   ```sql
   CREATE DATABASE chat_app;
   USE chat_app;
   
   CREATE TABLE users (
       id INT PRIMARY KEY AUTO_INCREMENT,
       name VARCHAR(100) NOT NULL,
       surname VARCHAR(100) NOT NULL,
       login VARCHAR(50) UNIQUE NOT NULL,
       password VARCHAR(255) NOT NULL
   );
   
   CREATE TABLE messages (
       id INT PRIMARY KEY AUTO_INCREMENT,
       sender_id INT NOT NULL,
       receiver_id INT NOT NULL,
       text TEXT NOT NULL,
       created_at DATETIME NOT NULL,
       FOREIGN KEY (sender_id) REFERENCES users(id),
       FOREIGN KEY (receiver_id) REFERENCES users(id)
   );
   ```

3. **Настроить .env файл** в папке `mysql_version/`
   ```
   DB_HOST=localhost
   DB_NAME=chat_app
   DB_USER=root
   DB_PASSWORD=ваш_пароль_от_mysql
   SECRET_KEY=любой_секретный_ключ
   ```

4. **Установить зависимости**
   ```bash
   pip install flask mysql-connector-python python-dotenv
   ```

5. **Запустить сервер**
   ```bash
   cd mysql_version
   python app.py
   ```

6. **Открыть браузер** и перейти: `http://127.0.0.1:5000`

7. **Остановить сервер**: нажать `Ctrl+C` в терминале

---

## API endpoints

### Вход
```
POST /login
{
    "login": "user_login",
    "password": "user_password"
}
```

### Регистрация
```
POST /register
{
    "name": "Иван",
    "surname": "Иванов",
    "login": "ivan123",
    "password": "qwerty"
}
```

### Чат
```
GET /chat?user_id=5
```

### Отправка сообщения
```
POST /send_message
{
    "receiver_id": 5,
    "text": "Привет!"
}
```

### Получение сообщений
```
GET /get_messages?user_id=5
```

---

## Команда

| Участник | Роль | Задачи |
|----------|------|--------|
| Илья | Backend | Вход, регистрация, отправка сообщений |
| Евгений | База данных | Структура MySQL, история сообщений |
| Анна | Frontend | Стили, чат 1-на-1, динамика |

---

## Отличия от SQLite-версии

| Особенность | SQLite | MySQL |
|-------------|--------|-------|
| База данных | Файл `chat.db` | Сервер MySQL |
| Поля пользователя | `nickname`, `password` | `name`, `surname`, `login`, `password` |
| Чат | Групповой | 1-на-1 |
| Сессии | `session["nickname"]` | `session["user_id"]`, `session["user_login"]` |
| Маршруты | `/login`, `/register`, `/chat`, `/send`, `/messages` | `/login`, `/register`, `/chat`, `/send_message`, `/get_messages` |

---

*Учебный проект. Дисциплина "Современные способы программирования". Магистратура 2026.*
