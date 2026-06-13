from flask import Flask, render_template, request, jsonify, session, redirect, url_for, g
import sqlite3
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = "секрет123local"


def get_db():
    """Подключается к SQLite базе"""
    if 'db' not in g:
        g.db = sqlite3.connect("chat_1to1.db")
        g.db.row_factory = sqlite3.Row  # Доступ по имени: row["nickname"]
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(error):
    """Закрывает соединение с БД"""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Создаёт таблицы при первом запуске"""
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT NOT NULL,
            surname  TEXT NOT NULL,
            login    TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id  INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            text       TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (sender_id) REFERENCES users(id),
            FOREIGN KEY (receiver_id) REFERENCES users(id)
        )
    """)
    db.commit()


# ---------------------------------------------------------------
# ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ — ПРИВЕТСТВИЕ ПО ВРЕМЕНИ СУТОК
# ---------------------------------------------------------------

def get_greeting():
    """
    Возвращает приветствие в зависимости от текущего времени.
    5:00—11:59  → Доброе утро
    12:00—17:59  → Добрый день
    18:00—22:59  → Добрый вечер
    23:00—4:59   → Доброй ночи
    """
    import datetime
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


# ---------------------------------------------------------------
# МАРШРУТЫ — ВХОД И РЕГИСТРАЦИЯ
# ---------------------------------------------------------------

@app.route("/")
def index():
    """Главная страница — перенаправляем на страницу входа"""
    return redirect(url_for("login"))


@app.route("/register")
def register():
    """Перенаправляем на страницу входа с вкладкой регистрации"""
    return redirect(url_for("login") + "?tab=register")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Страница и логика входа"""
    if request.method == "POST":
        print("Received login POST request")
        print("Content-Type:", request.content_type)
        
        if request.is_json:
            data = request.json
            print("JSON data:", data)
        else:
            data = request.form
            print("Form data:", data)
        
        login = data.get("login", "").strip()
        password = data.get("password", "").strip()

        print(f"Login attempt: {login}, password length: {len(password)}")

        if not login or not password:
            return jsonify({"result": False, "message": "Введите логин и пароль!", "code": 400})

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE login = ?", (login,)).fetchone()
        db.close()

        print(f"User found: {user}")

        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['user_login'] = user['login']
            session['user_name'] = f"{user['name']} {user['surname']}"
            return jsonify({"result": True, "message": "Вход выполнен!", "code": 200})
        else:
            return jsonify({"result": False, "message": "Неверный логин или пароль!", "code": 400})

    # Для GET-запроса показываем страницу входа
    return render_template("authorization.html")


@app.route("/chat")
def chat():
    """Страница чата. Если пользователь не вошёл — отправляем на главную."""
    if 'user_id' not in session:
        return redirect(url_for("index"))

    db = get_db()
    
    # Получаем текущего пользователя
    current_user = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    
    # Получаем всех пользователей (для списка справа)
    all_users = db.execute("SELECT * FROM users WHERE id != ?", (session['user_id'],)).fetchall()
    
    # Получаем chosen_user_id из параметров запроса (кто выбран для чата)
    chosen_user_id = request.args.get('user_id', type=int)
    
    chosen_user = None
    messages = []
    
    if chosen_user_id:
        # Получаем информацию о выбранном собеседнике
        chosen_user = db.execute("SELECT * FROM users WHERE id = ?", (chosen_user_id,)).fetchone()
        
        # Получаем сообщения между текущим пользователем и выбранной темой
        messages = db.execute("""
            SELECT m.*, 
                   u.login as sender_login, 
                   u.name as sender_name,
                   u.surname as sender_surname
            FROM messages m 
            JOIN users u ON m.sender_id = u.id
            WHERE (m.sender_id = ? AND m.receiver_id = ?) 
               OR (m.sender_id = ? AND m.receiver_id = ?)
            ORDER BY m.created_at ASC
        """, (session['user_id'], chosen_user_id, chosen_user_id, session['user_id'])).fetchall()
    
    db.close()
    
    return render_template(
        "chat.html",
        current_user=current_user,
        all_users=all_users,
        chosen_user=chosen_user,
        messages=messages,
        greeting=get_greeting()
    )


@app.route("/send_message", methods=["POST"])
def send_message():
    """Отправка сообщения"""
    if 'user_id' not in session:
        return jsonify({"result": False, "message": "Сначала авторизуйтесь!", "code": 401})

    import datetime
    data = request.json
    
    receiver_id = data.get("receiver_id")
    if receiver_id is not None:
        receiver_id = int(receiver_id)
    text = data.get("text", "").strip()

    if not receiver_id or not text:
        return jsonify({"result": False, "message": "Неверные данные!", "code": 400})

    db = get_db()
    
    # Форматируем дату и время
    now = datetime.datetime.now()
    created_at = now.strftime("%Y-%m-%d %H:%M:%S")
    
    db.execute(
        "INSERT INTO messages (sender_id, receiver_id, text, created_at) VALUES (?, ?, ?, ?)",
        (session['user_id'], receiver_id, text, created_at)
    )
    db.commit()
    new_message_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    db.close()

    return jsonify({
        "result": True, 
        "message_id": new_message_id, 
        "code": 200
    })


@app.route("/get_messages", methods=["GET"])
def get_messages():
    """Получение сообщений с другим пользователем"""
    if 'user_id' not in session:
        return jsonify([])

    receiver_id = request.args.get('user_id', type=int)
    
    if not receiver_id:
        return jsonify([])

    db = get_db()
    
    messages = db.execute("""
        SELECT m.*, 
               u.login as sender_login, 
               u.name as sender_name,
               u.surname as sender_surname
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE (m.sender_id = ? AND m.receiver_id = ?) 
           OR (m.sender_id = ? AND m.receiver_id = ?)
        ORDER BY m.created_at ASC
    """, (session['user_id'], receiver_id, receiver_id, session['user_id'])).fetchall()
    db.close()

    # Преобразуем в список словарей для JSON
    result = []
    for msg in messages:
        result.append({
            "id": msg["id"],
            "sender_id": msg["sender_id"],
            "receiver_id": msg["receiver_id"],
            "text": msg["text"],
            "created_at": msg["created_at"],
            "sender_login": msg["sender_login"],
            "sender_name": msg["sender_name"],
            "sender_surname": msg["sender_surname"]
        })
    
    return jsonify(result)


@app.route("/logout")
def logout():
    """Удаляет сессию и возвращает на главную"""
    session.pop('user_id', None)
    session.pop('user_login', None)
    session.pop('user_name', None)
    return redirect(url_for("index"))


# ---------------------------------------------------------------
# ЗАПУСК
# ---------------------------------------------------------------

if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(debug=True, port=5001)
