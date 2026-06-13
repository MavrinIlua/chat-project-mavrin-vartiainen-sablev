# 🏗️ Архитектура ChatApp

> Подробное описание архитектуры веб-чата с анализом безопасного развертывания.

---

## 1️⃣ Общая архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│                      CLIENT (Браузер)                            │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────────┐   │
│  │   HTML      │  │     CSS      │  │     JavaScript        │   │
│  │  (templates)│  │  (static/)   │  │   (static/)           │   │
│  └──────┬──────┘  └──────┬───────┘  └──────────┬────────────┘   │
│         │                │                       │                │
│         └────────────────┴───────────────────────┘                │
│                            │                                      │
│                       HTTP Requests                               │
└────────────────────────────┼──────────────────────────────────────┘
                             │
┌────────────────────────────┼──────────────────────────────────────┐
│                    FLASK SERVER (Python)                         │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  app.py                                                  │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐  │    │
│  │  │  Routes      │  │  Sessions    │  │  Database      │  │    │
│  │  │  (routes)    │  │  (session)   │  │  (MySQL)       │  │    │
│  │  └──────┬───────┘  └──────┬───────┘  └────────────────┘  │    │
│  │         │                 │                               │    │
│  └─────────┼─────────────────┼───────────────────────────────┘    │
│            │                 │                                     │
│       HTTP Response    Session Cookie                      MySQL  │
└────────────────────────────┼──────────────────────────────────────┘
                             │
┌────────────────────────────┼──────────────────────────────────────┐
│                      DATABASE LAYER                              │
│                                                                  │
│  ┌──────────────────┐              ┌──────────────────────────┐  │
│  │     SQLite       │              │          MySQL           │  │
│  │   (chat.db)      │              │   (sch688_maga1)         │  │
│  │  - users table   │              │  - users table           │  │
│  │  - messages      │              │  - messages table        │  │
│  └──────────────────┘              └──────────────────────────┘  │
└───────────────────────────────────────────────────────────────────┘
```

---

## 2️⃣ Структура приложения

### Вариант 1: SQLite (простой, локальный)

```
sqlite_version/
│
├── app.py                      # Главный файл Flask
│
├── templates/                  # HTML-шаблоны
│   ├── index.html             # Страница входа
│   ├── registration.html      # Страница регистрации
│   └── chat.html              # Страница чата
│
├── static/
│   ├── style.css              # CSS-стили
│   └── chat.js                # JavaScript для AJAX
│
└── chat.db                     # База данных SQLite (файл)
```

**Архитектура:**
- **Single-tier** или **2-tier** архитектура
- Данные хранятся в локальном файле `chat.db`
- Подходит для разработки и тестирования

### Вариант 2: MySQL (продакшн, серверный)

```
mysql_version/
│
├── app.py                      # Главный файл Flask
│
├── templates/                  # HTML-шаблоны
│   ├── authorization.html     # Страница входа
│   ├── registration.html      # Страница регистрации
│   └── chat.html              # Страница чата 1-на-1
│
├── static/
│   └── style.css              # CSS-стили
│
└── .env                        # Конфигурация (НЕ включён в Git!)
```

**Архитектура:**
- **3-tier** архитектура
- **Web Server (Flask)** ←→ **Database Server (MySQL)**
- Подходит для продакшн-развертывания

---

## 3️⃣ Модульная структура app.py

```
app.py
│
├── Import statements          # Импорты Flask, MySQL, datetime
│
├── Flask app initialization   # app = Flask(__name__)
│
├── Configuration              # SECRET_KEY, DB connection
│   │
│   └── get_db()              # Подключение к MySQL
│   └── close_db()            # Закрытие соединения
│
├── Helper functions           # Вспомогательные функции
│   │
│   └── get_greeting()        # Приветствие по времени
│
├── Routes (MVC Controller)    # Маршруты (контроллеры)
│   │
│   ├── /                      # Главная страница
│   ├── /register              # Регистрация (POST/GET)
│   ├── /login                 # Вход (POST/GET)
│   ├── /chat                  # Страница чата
│   ├── /send_message          # Отправка сообщения
│   ├── /get_messages          # Получение сообщений
│   └── /logout                # Выход
│
└── Main block                 # Запуск сервера
    │
    └── if __name__ == "__main__":
        └── app.run(debug=True)
```

---

## 4️⃣ Модели данных (Database Schema)

### Таблица users

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| id | INT | Уникальный ID | PK, AUTO_INCREMENT |
| name | VARCHAR(100) | Имя | NOT NULL |
| surname | VARCHAR(100) | Фамилия | NOT NULL |
| login | VARCHAR(50) | Логин | UNIQUE, NOT NULL |
| password | VARCHAR(255) | Пароль | NOT NULL |

### Таблица messages

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| id | INT | Уникальный ID | PK, AUTO_INCREMENT |
| sender_id | INT | ID отправителя | FK → users.id |
| receiver_id | INT | ID получателя | FK → users.id |
| text | TEXT | Текст сообщения | NOT NULL |
| created_at | DATETIME | Дата и время | NOT NULL |

---

## 5️⃣ Поток данных (Data Flow)

```
┌─────────────┐
│  Browser    │
└──────┬──────┘
       │ 1. GET /login
       ├──────────────►
       │                 Flask
       │ 2. POST /login  ┌─────────────────┐
       ├────────────────►│  app.py         │
       │                 │  - check login  │
       │                 │  - check pwd    │
       │                 └─────────┬───────┘
       │                           │
       │                 ┌─────────▼───────┐
       │                 │  MySQL DB       │
       │                 │  - users table  │
       │                 └─────────┬───────┘
       │                           │
       │ 3. JSON response        │
       │◄──────────────────────────┘
       │
       │ 4. Redirect /chat
       ├──────────────►
       │                 Flask
       │ 5. GET /chat    ┌─────────────────┐
       ├────────────────►│  - create session│
       │                 │  - show chat    │
       │                 └─────────┬───────┘
       │                           │
       │                 ┌─────────▼───────┐
       │                 │  MySQL DB       │
       │                 │  - messages     │
       │                 └─────────────────┘
       │
       │ 6. HTML page with chat
       │◄──────────────────
```

---

## 6️⃣ Системные требования

### SQLite-версия
- Python 3.12+
- Flask 2.3+
- werkzeug 3.0+

### MySQL-версия
- Python 3.12+
- Flask 2.3+
- mysql-connector-python 8.0+
- python-dotenv 1.0+
- MySQL Server 5.7+ или XAMPP

---

## 7️⃣ Проблемы безопасности

### 🔴 КРИТИЧЕСКИЕ (ИСПРАВЛЕНО):

1. **Файл `.env` в репозитории** — Contains real database credentials
   - **Решение**: Добавлен `.gitignore` и файл извлечён из Git history

2. **Файл `chat.db` в репозитории** — Contains user data
   - **Решение**: Добавлен в `.gitignore`

### 🟡 ВАЖНЫЕ:

1. **Пароли в коде** —不应 хранить пароли в plaintext
   - **Решение**: Используется `os.getenv()` для загрузки из `.env`

2. **Сессии** — Использование Flask session
   - **Рекомендация**: В продакшне использовать `flask-login`

3. **SQL Injection** — Использование parameterized queries
   - **Решение**: Все запросы используют `%s` placeholders

4. **SECRET_KEY** — Должен быть уникальным для каждого окружения
   - **Решение**: Загружается из `.env`

---

## 8️⃣ Рекомендации по безопасному развертыванию

### При любом развертывании:

1. **НЕ коммитьте** файлы с конфиденциальными данными:
   - `.env`
   - `*.db`
   - `chat.db`

2. **Создайте `.env.example`** с пустыми значениями:
   ```env
   DB_HOST=localhost
   DB_NAME=chat_app
   DB_USER=
   DB_PASSWORD=
   SECRET_KEY=
   ```

3. **Используйте `.gitignore`** для исключения:
   ```gitignore
   .env
   *.db
   __pycache__/
   .venv/
   ```

4. **Смените пароли** на реальном сервере, если они были скомпрометированы

5. **Используйте HTTPS** в продакшне

---

## 9️⃣ Диаграмма классов (UML)

```
┌─────────────────────────────────────────────────────────────┐
│                     Flask Application                        │
├─────────────────────────────────────────────────────────────┤
│ - app: Flask                                                │
│ - db: MySQLConnection                                       │
│ - session: SessionInterface                                 │
├─────────────────────────────────────────────────────────────┤
│ + get_db(): MySQLConnection                                 │
│ + close_db(error): void                                     │
│ + get_greeting(): String                                    │
│ + index(): Response                                         │
│ + login(method: POST/GET): Response                         │
│ + register(method: POST/GET): Response                      │
│ + chat(): Response                                          │
│ + send_message(): JSON                                      │
│ + get_messages(): JSON                                      │
│ + logout(): Response                                        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                     User Model                               │
├─────────────────────────────────────────────────────────────┤
│ - id: int                                                   │
│ - name: string                                              │
│ - surname: string                                           │
│ - login: string                                             │
│ - password: string (hashed)                                 │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    Message Model                             │
├─────────────────────────────────────────────────────────────┤
│ - id: int                                                   │
│ - sender_id: int (FK)                                       │
│ - receiver_id: int (FK)                                     │
│ - text: string                                              │
│ - created_at: datetime                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔟 Варианты развёртывания

### 1. Локальный (для разработки)
```
SQLite + Flask + localhost:5000
```

### 2. VPS (виртуальный сервер)
```
MySQL + Flask + Nginx + Gunicorn + HTTPS
```

### 3. Docker (контейнеризация)
```
Docker Compose:
  - app: Flask container
  - db: MySQL container
```

---

## 📚 Ссылки

- [Flask Documentation](https://flask.palletsprojects.com/)
- [MySQL Connector/Python](https://dev.mysql.com/doc/connector-python/en/)
- [Werkzeug Security](https://werkzeug.palletsprojects.com/security/)
- [OWASP Flask Guidelines](https://cheatsheetseries.owasp.org/cheatsheets/Flask_Cheat_Sheet.html)

---

*Архитектура создана 13.06.2026. Дисциплина "Современные способы программирования".*
