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
│  │  app_local.py / app.py                                   │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐  │    │
│  │  │  Routes      │  │  Sessions    │  │  Database      │  │    │
│  │  │  (routes)    │  │  (session)   │  │  (SQLite/MySQL)│  │    │
│  │  └──────┬───────┘  └──────┬───────┘  └────────────────┘  │    │
│  │         │                 │                               │    │
│  └─────────┼─────────────────┼───────────────────────────────┘    │
│            │                 │                                     │
│       HTTP Response    Session Cookie                      DB     │
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

### Корневая структура

```
├── mysql_version/              # Версия с MySQL (и SQLite для локальной работы)
│   ├── app_local.py            # Главный файл Flask ( SQLite)
│   ├── .env.example            # Пример конфигурации
│   ├── templates/              # HTML-шаблоны
│   │   ├── authorization.html  # Страница входа (с вкладками)
│   │   └── chat.html           # Страница чата 1-на-1
│   ├── static/
│   │   └── style.css           # CSS-стили (современный дизайн)
│   └── chat_1to1.db            # База данных SQLite (файл)
│
├── sqlite_version/             # Упрощенная SQLite-версия
│   ├── app.py                  # Главный файл Flask
│   ├── templates/
│   │   ├── index.html          # Страница входа
│   │   ├── registration.html   # Страница регистрации
│   │   └── chat.html           # Страница чата
│   ├── static/
│   │   └── style.css           # CSS-стили
│   └── chat.db                 # База данных SQLite (файл)
│
├── ARCHITECTURE.md             # Документация архитектуры
├── README.md                   # Общая инструкция
└── .gitignore
```

**Архитектура:**
- **2-tier** архитектура (Flask + Database)
- Обе версии используют SQLite для локальной разработки
- `mysql_version` содержит код для подключения к MySQL (можно перенастроить)
- `sqlite_version` — упрощенная версия с отдельными страницами входа/регистрации

---

## 3️⃣ Модульная структура app_local.py

```
app_local.py
│
├── Import statements          # Импорты Flask, sqlite3, os
│
├── Flask app initialization   # app = Flask(__name__)
│
├── Configuration              # SECRET_KEY
│   │
│   └── get_db()              # Подключение к SQLite (chat_1to1.db)
│   └── close_db()            # Закрытие соединения
│
├── Helper functions           # Вспомогательные функции
│   │
│   └── init_db()             # Создание таблиц при первом запуске
│   └── get_greeting()        # Приветствие по времени
│
├── Routes (MVC Controller)    # Маршруты (контроллеры)
│   │
│   ├── /                      # Главная страница (перенаправление)
│   ├── /login                 # Вход (POST/GET) — JSON API
│   ├── /register              # Регистрация (POST/GET) — перенаправление
│   ├── /chat                  # Страница чата (GET)
│   ├── /send_message          # Отправка сообщения (POST JSON)
│   ├── /get_messages          # Получение сообщений (GET JSON)
│   └── /logout                # Выход (GET)
│
└── Main block                 # Запуск сервера
    │
    └── if __name__ == "__main__":
        └── app.run(debug=True, port=5001)
```

---

## 4️⃣ Модульная структура app.py (sqlite_version)

```
app.py
│
├── Import statements          # Импорты Flask, sqlite3, os
│
├── Flask app initialization   # app = Flask(__name__)
│
├── Configuration              # SECRET_KEY
│   │
│   └── get_db()              # Подключение к SQLite (chat.db)
│   └── close_db()            # Закрытие соединения
│
├── Helper functions           # Вспомогательные функции
│   │
│   └── init_db()             # Создание таблиц при первом запуске
│   └── get_greeting()        # Приветствие по времени
│
├── Routes (MVC Controller)    # Маршруты (контроллеры)
│   │
│   ├── /                      # Главная страница (перенаправление)
│   ├── /index                 # Страница входа (GET)
│   ├── /login                 # Вход (POST JSON)
│   ├── /register              # Регистрация (POST/GET)
│   ├── /chat                  # Страница чата (GET)
│   ├── /send_message          # Отправка сообщения (POST JSON)
│   ├── /get_messages          # Получение сообщений (GET JSON)
│   └── /logout                # Выход (GET)
│
└── Main block                 # Запуск сервера
    │
    └── if __name__ == "__main__":
        └── app.run(debug=True, port=5000)
```

---

## 5️⃣ Модели данных (Database Schema)

### Таблица users

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| id | INTEGER | Уникальный ID | PRIMARY KEY, AUTOINCREMENT |
| name | TEXT | Имя | NOT NULL |
| surname | TEXT | Фамилия | NOT NULL |
| login | TEXT | Логин | UNIQUE, NOT NULL |
| password | TEXT | Пароль (plaintext) | NOT NULL |

### Таблица messages

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| id | INTEGER | Уникальный ID | PRIMARY KEY, AUTOINCREMENT |
| sender_id | INTEGER | ID отправителя | NOT NULL, FOREIGN KEY |
| receiver_id | INTEGER | ID получателя | NOT NULL, FOREIGN KEY |
| text | TEXT | Текст сообщения | NOT NULL |
| created_at | TEXT | Дата и время | NOT NULL |

---

## 6️⃣ Поток данных (Data Flow)

```
┌─────────────┐
│  Browser    │
└──────┬──────┘
       │ 1. GET /login
       ├──────────────►
       │                 Flask
       │ 2. POST /login  ┌─────────────────┐
       ├────────────────►│  app_local.py   │
       │                 │  - check login  │
       │                 │  - check pwd    │
       │                 └─────────┬───────┘
       │                           │
       │                 ┌─────────▼───────┐
       │                 │  SQLite DB      │
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
       │                 │  SQLite DB      │
       │                 │  - messages     │
       │                 └─────────────────┘
       │
       │ 6. HTML page with chat
       │◄──────────────────
```

---

## 7️⃣ Системные требования

### SQLite-версия (mysql_version)
- Python 3.12+
- Flask 2.3+
- werkzeug 3.0+

### SQLite-версия (sqlite_version)
- Python 3.12+
- Flask 2.3+
- werkzeug 3.0+

---

## 8️⃣ Проблемы безопасности

### 🔴 КРИТИЧЕСКИЕ (ИСПРАВЛЕНО):

1. **Файл `.env` в репозитории** — Contains real database credentials
   - **Решение**: Добавлен `.gitignore` и файл извлечён из Git history

2. **Файл `chat.db`/`chat_1to1.db` в репозитории** — Contains user data
   - **Решение**: Добавлен в `.gitignore`

### 🟡 ВАЖНЫЕ:

1. **Пароли в plaintext** — Не рекомендуется
   - **Рекомендация**: В продакшне использовать `werkzeug.security` для хэширования

2. **Сессии** — Использование Flask session
   - **Рекомендация**: В продакшне использовать `flask-login`

3. **SQL Injection** — Использование parameterized queries
   - **Решение**: Все запросы используют `?` placeholders (SQLite)

4. **SECRET_KEY** — Должен быть уникальным для каждого окружения
   - **Решение**: Хранится в `.env` файле

---

## 9️⃣ Рекомендации по безопасному развертыванию

### При любом развертывании:

1. **НЕ коммитьте** файлы с конфиденциальными данными:
   - `.env`
   - `*.db` (chat.db, chat_1to1.db)
   - `__pycache__/`

2. **Создайте `.env.example`** с пустыми значениями:
   ```env
   SECRET_KEY=your_random_secret_key_here
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

6. **Хэшируйте пароли** (рекомендуется):
   ```python
   from werkzeug.security import generate_password_hash, check_password_hash
   
   # При регистрации:
   user['password'] = generate_password_hash(password)
   
   # При входе:
   check_password_hash(user['password'], password)
   ```

---

## 🔟 Варианты развёртывания

### 1. Локальный (для разработки)
```
SQLite + Flask + localhost:5001 (mysql_version)
SQLite + Flask + localhost:5000 (sqlite_version)
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
- [Werkzeug Security](https://werkzeug.palletsprojects.com/security/)
- [OWASP Flask Guidelines](https://cheatsheetseries.owasp.org/cheatsheets/Flask_Cheat_Sheet.html)

---

## 📝 Заметки по запуску

### mysql_version (рекомендуемая версия)
1. Скопируйте `.env.example` в `.env` и настройте параметры (если нужен MySQL)
2. Запустите: `python app_local.py`
3. Откройте браузер: `http://localhost:5001`

### sqlite_version (простая версия)
1. Запустите: `python app.py`
2. Откройте браузер: `http://localhost:5000`

---

*Архитектура создана 13.06.2026. Дисциплина "Современные способы программирования".*

