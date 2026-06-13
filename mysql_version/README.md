# MySQL-версия ChatApp

> Чат в реальном времени с базой данных MySQL и чатом 1-на-1.

---

## Что это такое?

**ChatApp MySQL** — веб-чат, где пользователи могут переписываться в реальном времени между собой (1-на-1). Использует SQLite (по умолчанию) или MySQL для хранения данных.

---

## Возможности

- **Вход по логину и паролю** — авторизация через БД
- **Чат 1-на-1** — выбор собеседника из списка пользователей
- **История переписки** — сообщения сохраняются в базе данных
- **Умное приветствие** — "Доброе утро", "Добрый день", "Добрый вечер" или "Доброй ночи" в зависимости от времени
- **Автоматическое обновление** — новые сообщения появляются каждые 3 секунды
- **Разделители даты** — дата показывается один раз при переходе на новый день
- **Современный дизайн** — аватарки, градиенты, закругленные элементы

---

## Технологии

| Что | Зачем |
|-----|-------|
| Python 3.12 + Flask | Сервер, маршруты, логика |
| SQLite | База данных (по умолчанию) |
| MySQL | Альтернативная база данных |
| HTML + Jinja2 | Страницы сайта |
| CSS | Внешний вид (современный дизайн) |
| JavaScript (fetch) | Динамика без перезагрузки |

---

## Структура проекта

```
mysql_version/
│
├── app_local.py          ← точка входа ( Flask + SQLite/MySQL)
├── .env.example          ← пример конфигурации (скопируй в .env)
├── .env                  ← переменные окружения (НЕ включён в Git!)
├── README.md             ← описание проекта
├── backlog_mysql.md      ← список задач для MySQL-версии
├── requirements.txt      ← зависимости
│
├── templates/            ← HTML-страницы (Flask ищет шаблоны здесь)
│   ├── authorization.html ← страница входа (с вкладками)
│   └── chat.html         ← страница чата 1-на-1
│
└── static/               ← файлы, которые браузер скачивает напрямую
    └── style.css         ← стили внешнего вида (современный CSS)
```

---

## База данных

### SQLite (по умолчанию)
Файл `chat_1to1.db` создаётся автоматически при первом запуске.

### MySQL (для продакшна)
Если настроить `.env`, будет использоваться MySQL.

#### Таблица users (пользователи)

| Поле | Тип | Описание |
|------|-----|----------|
| id | INT (PK, AUTOINCREMENT) | Уникальный ID пользователя |
| name | VARCHAR(100) | Имя пользователя |
| surname | VARCHAR(100) | Фамилия пользователя |
| login | VARCHAR(50) | Логин (уникальный) |
| password | TEXT | Пароль (plaintext) |

#### Таблица messages (сообщения)

| Поле | Тип | Описание |
|------|-----|----------|
| id | INT (PK, AUTOINCREMENT) | Уникальный ID сообщения |
| sender_id | INT (FK) | ID отправителя |
| receiver_id | INT (FK) | ID получателя |
| text | TEXT | Текст сообщения |
| created_at | TEXT | Дата и время создания (YYYY-MM-DD HH:MM:SS) |

---

## Как запустить проект

### Вариант 1: SQLite (по умолчанию, без установки сервера)

1. **Скопировать `.env.example` в `.env`**
   ```bash
   cd mysql_version
   copy .env.example .env
   ```

2. **Запустить сервер**
   ```bash
   python app_local.py
   ```

3. **Открыть браузер** и перейти: `http://localhost:5001`

4. **Остановить сервер**: нажать `Ctrl+C` в терминале

### Вариант 2: MySQL (для продакшна)

1. **Установить MySQL и XAMPP** (если ещё не установлен)

2. **Создать базу данных и таблицы**
   ```sql
   CREATE DATABASE sch688_maga1;
   USE sch688_maga1;
   
   CREATE TABLE users (
       id INT PRIMARY KEY AUTOINCREMENT,
       name VARCHAR(100) NOT NULL,
       surname VARCHAR(100) NOT NULL,
       login VARCHAR(50) UNIQUE NOT NULL,
       password TEXT NOT NULL
   );
   
   CREATE TABLE messages (
       id INT PRIMARY KEY AUTOINCREMENT,
       sender_id INT NOT NULL,
       receiver_id INT NOT NULL,
       text TEXT NOT NULL,
       created_at TEXT NOT NULL,
       FOREIGN KEY (sender_id) REFERENCES users(id),
       FOREIGN KEY (receiver_id) REFERENCES users(id)
   );
   ```

3. **Настроить `.env` файл** в папке `mysql_version/`
   ```env
   DATABASE_URL=mysql+pymysql://sch688_maga1:пароль@185.114.247.43/sch688_maga1
   SECRET_KEY=секрет123local
   FLASK_RUN_PORT=5001
   ```

4. **Установить зависимости**
   ```bash
   pip install flask python-dotenv pymysql
   ```

5. **Запустить сервер**
   ```bash
   cd mysql_version
   python app_local.py
   ```

6. **Открыть браузер** и перейти: `http://localhost:5001`

---

## .env файл

### SQLite (по умолчанию)
```env
DATABASE_URL=sqlite:///chat_1to1.db
SECRET_KEY=секрет123local
FLASK_RUN_PORT=5001
```

### MySQL (для продакшна)
```env
DATABASE_URL=mysql+pymysql://username:password@host:port/database_name
SECRET_KEY=ваш_случайный_ключ
FLASK_RUN_PORT=5001
```

**Важно:** Не коммитьте `.env` в Git! Он уже добавлен в `.gitignore`.

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
**Ответ:**
```json
{
    "result": true,
    "message": "Вход выполнен!",
    "code": 200
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
**Ответ:**
```json
{
    "result": true,
    "message": "Регистрация успешна!",
    "code": 200
}
```

### Чат
```
GET /chat
```
**Ответ:** HTML-страница чата

### Чат с конкретным пользователем
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
**Ответ:**
```json
{
    "result": true,
    "message_id": 123,
    "code": 200
}
```

### Получение сообщений
```
GET /get_messages?user_id=5
```
**Ответ:**
```json
[
    {
        "id": 1,
        "sender_id": 1,
        "receiver_id": 5,
        "text": "Привет!",
        "created_at": "2026-06-13 17:15:00",
        "sender_login": "user1",
        "sender_name": "Иван",
        "sender_surname": "Иванов"
    }
]
```

---

## Команда

| Участник | Роль | Задачи |
|----------|------|--------|
| Илья | Backend | Вход, регистрация, отправка сообщений |
| Евгений | База данных | Структура БД, история сообщений |
| Анна | Frontend | Стили, чат 1-на-1, динамика |

---

## Отличия от sqlite_version

| Особенность | mysql_version | sqlite_version |
|-------------|---------------|----------------|
| Порт | 5001 | 5000 |
| Точка входа | `app_local.py` | `app.py` |
| База данных | SQLite (по умолчанию) / MySQL | SQLite |
| Структура | Основная (одна точка входа) | Упрощённая (отдельные страницы) |
| Вкладки входа/регистрации | ✅ | ❌ (отдельные страницы) |
| Современный дизайн | ✅ | ⚠️ (более простой) |
| Рекомендуется для | Основной разработки | Быстрого теста |

---

## Как перейти с sqlite_version на mysql_version

1. **Запустите sqlite_version** и зарегистрируйте пользователей
2. **Скопируйте данные из `sqlite_version/chat.db`** (если нужно сохранить историю)
3. **Запустите mysql_version** — она создаст свою БД автоматически
4. **Зарегистрируйте пользователей снова** (если нужно)

**Примечание:** Базы данных несовместимы (разная структура полей).

---

*Учебный проект. Дисциплина "Современные способы программирования". Магистратура 2026.*

