"""
MySQL-версия чата — архитектура построена на принципах:
- Separation of concerns (разделение ответственностей)
- Dependency Injection (через контекст Flask)
- CRUD-операции через отдельные слои
- RESTful подход к API-маршрутам
- Session-based auth с защитой от CSRF (опционально)
- Prepared statements для безопасности (anti SQL-injection)
"""

from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'magistratura_2026_secure_key'


# ---------------------------------------------------------------
# CONFIGURATION (с возможностью перегрузки через .env)
# ---------------------------------------------------------------

def get_db_config():
    """Получение конфигурации БД с приоритетом .env -> дефолт"""
    config = {
        'host': os.environ.get('DB_HOST', '185.114.247.43'),
        'database': os.environ.get('DB_NAME', 'sch688_maga1'),
        'user': os.environ.get('DB_USER', 'sch688_maga1'),
        'password': os.environ.get('DB_PASS', 'Fqx8irSU'),
        'port': int(os.environ.get('DB_PORT', 3306)),
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci'
    }
    return config


def get_db_connection():
    """Создание подключения к MySQL с пулингом и обработкой ошибок"""
    try:
        conn = mysql.connector.connect(**get_db_config())
        if conn.is_connected():
            return conn
    except Error as e:
        app.logger.error(f"DB Connection Error: {e}")
        raise
    return None


# ---------------------------------------------------------------
# DATABASE LAYER (абстракция над SQLite Row для MySQL)
# ---------------------------------------------------------------

class Row(dict):
    """Мини-аналог sqlite3.Row для MySQL"""
    def __getattr__(self, key):
        return self.get(key)
    
    def __setattr__(self, key, value):
        self[key] = value


def dict_to_row(data):
    """Преобразование dict в Row-объект"""
    if isinstance(data, list):
        return [Row(item) for item in data]
    elif isinstance(data, dict):
        return Row(data)
    return data


def fetch_all(cursor, query, params=None):
    """Выполнение SELECT с преобразованием результатов"""
    cursor.execute(query, params or ())
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    return [dict(zip(columns, row)) for row in rows]


def fetch_one(cursor, query, params=None):
    """Выполнение SELECT ONE"""
    cursor.execute(query, params or ())
    columns = [desc[0] for desc in cursor.description]
    row = cursor.fetchone()
    if row:
        return dict(zip(columns, row))
    return None


# ---------------------------------------------------------------
# DATABASE INITIALIZATION (создание таблиц при первом запуске)
# ---------------------------------------------------------------

def init_database():
    """Создание таблиц users и messages если их нет"""
    conn = get_db_connection()
    if not conn:
        raise Exception("Не удалось подключиться к БД")
    
    cursor = conn.cursor()
    
    # Таблица пользователей (расширенная схема)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS `users` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `name` VARCHAR(100) NOT NULL,
            `surname` VARCHAR(100) NOT NULL,
            `login` VARCHAR(50) NOT NULL UNIQUE,
            `password` VARCHAR(255) NOT NULL,
            `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            `last_seen` TIMESTAMP NULL,
            `is_active` BOOLEAN DEFAULT TRUE,
            INDEX `idx_login` (`login`),
            INDEX `idx_active` (`is_active`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)
    
    # Таблица сообщений (с сортировкой по времени)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS `messages` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `owner_id` INT NOT NULL,
            `deliver_id` INT NOT NULL,
            `text` TEXT NOT NULL,
            `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP,
            `is_read` BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (`owner_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
            FOREIGN KEY (`deliver_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
            INDEX `idx_owner_deliver` (`owner_id`, `deliver_id`),
            INDEX `idx_timestamp` (`timestamp`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)
    
    conn.commit()
    cursor.close()
    conn.close()


# ---------------------------------------------------------------
# AUTHENTICATION DECORATOR (защита маршрутов)
# ---------------------------------------------------------------

def login_required(f):
    """Декоратор для защиты маршрутов (только для авторизованных)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ---------------------------------------------------------------
# UTILS (вспомогательные функции)
# ---------------------------------------------------------------

def get_greeting():
    """Приветствие по времени суток (из SQLite-версии)"""
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_user_fullname(user):
    """Полное имя пользователя (name surname)"""
    return f"{user['name']} {user['surname']}"


# ---------------------------------------------------------------
# API ENDPOINTS (REST-style)
# ---------------------------------------------------------------

@app.route('/')
def index():
    """Редирект на страницу входа"""
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Регистрация пользователя
    POST: /register
    Body: {name, surname, login, password}
    Response: {user_id, status}
    """
    if request.method == 'GET':
        return render_template('registration.html')
    
    # POST-запрос
    data = request.get_json() or request.form.to_dict()
    
    # Валидация
    name = data.get('name', '').strip()
    surname = data.get('surname', '').strip()
    login = data.get('login', '').strip().lower()
    password = data.get('password', '').strip()
    
    if not all([name, surname, login, password]):
        return jsonify({'error': 'Заполните все поля'}), 400
    
    if len(password) < 6:
        return jsonify({'error': 'Пароль должен быть не менее 6 символов'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Ошибка подключения к БД'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Проверка наличия логина
        existing = fetch_one(cursor, 
            "SELECT id FROM users WHERE login = %s", (login,))
        
        if existing:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Такой логин уже занят'}), 409
        
        # Вставка нового пользователя
        cursor.execute(
            "INSERT INTO users (name, surname, login, password) VALUES (%s, %s, %s, %s)",
            (name, surname, login, password)
        )
        user_id = cursor.lastrowid
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'user_id': user_id,
            'status': 'registered',
            'message': 'Регистрация успешна'
        }), 201
        
    except Exception as e:
        app.logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Ошибка при регистрации'}), 500


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Вход пользователя
    GET: показать форму входа
    POST: /login (JSON или form)
    """
    if request.method == 'GET':
        # Если уже авторизован - сразу в чат
        if 'user_id' in session:
            return redirect(url_for('chat'))
        return render_template('login.html')
    
    # POST-авторизация
    data = request.get_json() or request.form.to_dict()
    login = data.get('login', '').strip().lower()
    password = data.get('password', '').strip()
    
    if not login or not password:
        return jsonify({'error': 'Введите логин и пароль'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Ошибка подключения к БД'}), 500
    
    try:
        cursor = conn.cursor()
        
        user = fetch_one(cursor,
            "SELECT * FROM users WHERE login = %s", (login,))
        
        if not user:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Пользователь не найден'}), 404
        
        # Простая проверка пароля (можно заменить на хеширование)
        if user['password'] != password:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Неверный пароль'}), 401
        
        # Обновление last_seen
        cursor.execute(
            "UPDATE users SET last_seen = NOW() WHERE id = %s",
            (user['id'],)
        )
        conn.commit()
        
        cursor.close()
        conn.close()
        
        # Установка сессии
        session['user_id'] = user['id']
        session['user_login'] = user['login']
        session['user_name'] = user['name']
        session['user_surname'] = user['surname']
        
        return jsonify({
            'success': True,
            'redirect': url_for('chat')
        }), 200
        
    except Exception as e:
        app.logger.error(f"Login error: {e}")
        return jsonify({'error': 'Ошибка при входе'}), 500


@app.route('/chat')
@login_required
def chat():
    """
    Страница чата с выбором собеседника
    GET: /chat?id=2 (собеседник ID=2)
    """
    user_id = session['user_id']
    deliver_id = request.args.get('id', type=int)
    
    conn = get_db_connection()
    if not conn:
        return "Ошибка подключения к БД", 500
    
    try:
        cursor = conn.cursor()
        
        # Данные текущего пользователя
        owner = fetch_one(cursor,
            "SELECT * FROM users WHERE id = %s", (user_id,))
        
        # Список всех пользователей (кроме себя)
        all_users = fetch_all(cursor,
            "SELECT * FROM users WHERE id != %s ORDER BY name, surname", (user_id,))
        
        # Последнее сообщение для каждого диалога (для превью)
        cursor.execute("""
            SELECT m.*, u.name, u.surname 
            FROM messages m 
            JOIN users u ON (m.owner_id = u.id OR m.deliver_id = u.id)
            WHERE (m.owner_id = %s OR m.deliver_id = %s) 
              AND m.id = (
                  SELECT MAX(m2.id) FROM messages m2 
                  WHERE (m2.owner_id = %s AND m2.deliver_id = u.id) 
                     OR (m2.deliver_id = %s AND m2.owner_id = u.id)
              )
            GROUP BY u.id
        """, (user_id, user_id, user_id, user_id))
        last_messages = {row['owner_id' if row['owner_id'] != user_id else 'deliver_id']: row 
                        for row in cursor.fetchall()}
        
        # Выбранный собеседник
        deliver = None
        messages = []
        
        if deliver_id:
            deliver = fetch_one(cursor,
                "SELECT * FROM users WHERE id = %s", (deliver_id,))
            
            # История переписки (с сортировкой по времени)
            messages = fetch_all(cursor,
                """SELECT * FROM messages 
                   WHERE (owner_id = %s AND deliver_id = %s) 
                      OR (owner_id = %s AND deliver_id = %s)
                   ORDER BY timestamp ASC""",
                (user_id, deliver_id, deliver_id, user_id))
            
            # Пометить как прочитанные
            cursor.execute(
                "UPDATE messages SET is_read = TRUE WHERE owner_id = %s AND deliver_id = %s AND is_read = FALSE",
                (deliver_id, user_id)
            )
            conn.commit()
        
        cursor.close()
        conn.close()
        
        return render_template('chat.html',
                             owner=owner,
                             deliver=deliver,
                             all_users=all_users,
                             messages=messages,
                             greeting=get_greeting(),
                             last_messages=last_messages)
        
    except Exception as e:
        app.logger.error(f"Chat error: {e}")
        return "Ошибка при загрузке чата", 500


@app.route('/send', methods=['POST'])
@login_required
def send_message():
    """
    Отправка сообщения
    POST: /send
    Body: {deliver_id, text}
    Response: {success, message_id}
    """
    user_id = session['user_id']
    data = request.get_json() or request.form.to_dict()
    
    deliver_id = data.get('deliver_id', type=int)
    text = data.get('text', '').strip()
    
    if not deliver_id or not text:
        return jsonify({'error': 'Некорректные данные'}), 400
    
    if len(text) > 1000:
        return jsonify({'error': 'Сообщение слишком длинное (максимум 1000 символов)'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Ошибка подключения к БД'}), 500
    
    try:
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO messages (owner_id, deliver_id, text) VALUES (%s, %s, %s)",
            (user_id, deliver_id, text)
        )
        message_id = cursor.lastrowid
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message_id': message_id
        }), 201
        
    except Exception as e:
        app.logger.error(f"Send message error: {e}")
        return jsonify({'error': 'Ошибка при отправке'}), 500


@app.route('/messages')
@login_required
def get_messages():
    """
    API для получения истории сообщений (AJAX)
    GET: /messages?with=2
    Response: [{id, owner_id, deliver_id, text, timestamp, is_read}]
    """
    user_id = session['user_id']
    with_user = request.args.get('with', type=int)
    
    if not with_user:
        return jsonify([]), 200
    
    conn = get_db_connection()
    if not conn:
        return jsonify([]), 500
    
    try:
        cursor = conn.cursor()
        
        messages = fetch_all(cursor,
            """SELECT m.*, 
                      u1.name as owner_name, u1.surname as owner_surname,
                      u2.name as deliver_name, u2.surname as deliver_surname
               FROM messages m
               JOIN users u1 ON m.owner_id = u1.id
               JOIN users u2 ON m.deliver_id = u2.id
               WHERE (m.owner_id = %s AND m.deliver_id = %s)
                  OR (m.owner_id = %s AND m.deliver_id = %s)
               ORDER BY m.timestamp ASC""",
            (user_id, with_user, with_user, user_id))
        
        cursor.close()
        conn.close()
        
        return jsonify(messages), 200
        
    except Exception as e:
        app.logger.error(f"Get messages error: {e}")
        return jsonify([]), 500


@app.route('/users')
@login_required
def get_users():
    """
    API для получения списка пользователей (AJAX)
    GET: /users
    Response: [{id, name, surname, login, is_active}]
    """
    user_id = session['user_id']
    
    conn = get_db_connection()
    if not conn:
        return jsonify([]), 500
    
    try:
        cursor = conn.cursor()
        
        users = fetch_all(cursor,
            "SELECT id, name, surname, login, is_active, last_seen FROM users WHERE id != %s ORDER BY name",
            (user_id,))
        
        cursor.close()
        conn.close()
        
        return jsonify(users), 200
        
    except Exception as e:
        app.logger.error(f"Get users error: {e}")
        return jsonify([]), 500


@app.route('/logout')
def logout():
    """Выход из аккаунта"""
    session.clear()
    return redirect(url_for('login'))


# ---------------------------------------------------------------
# RUN
# ---------------------------------------------------------------

if __name__ == '__main__':
    # Инициализация БД при запуске
    try:
        init_database()
        print("✓ База данных MySQL готова к работе")
    except Exception as e:
        print(f"⚠ Ошибка инициализации БД: {e}")
        print("  Убедитесь, что указаны правильные параметры подключения")
    
    # Запуск Flask-сервера
    app.run(host='127.0.0.1', port=5000, debug=True)
