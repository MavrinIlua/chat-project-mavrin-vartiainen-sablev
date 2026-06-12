from flask import Flask, render_template, request, jsonify, session, redirect, url_for, g
import mysql.connector
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "секрет123")


def get_db():
    """Подключается к MySQL"""
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        g.db.autocommit = True
    return g.db


@app.teardown_appcontext
def close_db(error):
    """Закрывает соединение с БД"""
    db = g.pop('db', None)
    if db is not None:
        db.close()


# ---------------------------------------------------------------
# МАРШРУТЫ — ВХОД И РЕГИСТРАЦИЯ
# ---------------------------------------------------------------

@app.route("/")
def index():
    """Главная страница — перенаправляем на страницу входа"""
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """Страница и логика регистрации"""
    if request.method == "POST":
        data = request.json
        
        name = data.get("name", "").strip()
        surname = data.get("surname", "").strip()
        login = data.get("login", "").strip()
        password = data.get("password", "").strip()

        if not name or not surname or not login or not password:
            return jsonify({"result": False, "message": "Заполните все поля!", "code": 400})

        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Проверяем, есть ли уже такой логин
        cursor.execute("SELECT * FROM users WHERE login = %s", (login,))
        user = cursor.fetchone()
        
        if user:
            cursor.close()
            return jsonify({"result": False, "message": "Такой логин уже занят!", "code": 400})

        # Создаем нового пользователя
        cursor.execute(
            "INSERT INTO users (name, surname, login, password) VALUES (%s, %s, %s, %s)",
            (name, surname, login, password)
        )
        new_user_id = cursor.lastrowid
        cursor.close()

        # Автоматически авторизуем пользователя
        session['user_id'] = new_user_id
        session['user_login'] = login
        session['user_name'] = f"{name} {surname}"
        
        return jsonify({"result": True, "message": "Регистрация успешна!", "code": 200})

    return render_template("registration.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Страница и логика входа"""
    if request.method == "POST":
        data = request.json
        
        login = data.get("login", "").strip()
        password = data.get("password", "").strip()

        if not login or not password:
            return jsonify({"result": False, "message": "Введите логин и пароль!", "code": 400})

        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE login = %s", (login,))
        user = cursor.fetchone()
        cursor.close()

        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['user_login'] = user['login']
            session['user_name'] = f"{user['name']} {user['surname']}"
            return jsonify({"result": True, "message": "Вход выполнен!", "code": 200})
        else:
            return jsonify({"result": False, "message": "Неверный логин или пароль!", "code": 400})

    return render_template("authorization.html")


@app.route("/chat")
def chat():
    """Страница чата. Если пользователь не вошёл — отправляем на главную."""
    if 'user_id' not in session:
        return redirect(url_for("index"))

    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Получаем текущего пользователя
    cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
    current_user = cursor.fetchone()
    
    # Получаем всех пользователей (для списка справа)
    cursor.execute("SELECT * FROM users WHERE id != %s", (session['user_id'],))
    all_users = cursor.fetchall()
    
    # Получаем chosen_user_id из параметров запроса (кто выбран для чата)
    chosen_user_id = request.args.get('user_id', type=int)
    
    chosen_user = None
    messages = []
    
    if chosen_user_id:
        # Получаем информацию о выбранном собеседнике
        cursor.execute("SELECT * FROM users WHERE id = %s", (chosen_user_id,))
        chosen_user = cursor.fetchone()
        
        # Получаем сообщения между текущим пользователем и выбранной темой
        cursor.execute("""
            SELECT * FROM messages 
            WHERE (sender_id = %s AND receiver_id = %s) 
               OR (sender_id = %s AND receiver_id = %s)
            ORDER BY created_at ASC
        """, (session['user_id'], chosen_user_id, chosen_user_id, session['user_id']))
        messages = cursor.fetchall()
    
    cursor.close()
    
    return render_template(
        "chat.html",
        current_user=current_user,
        all_users=all_users,
        chosen_user=chosen_user,
        messages=messages
    )


@app.route("/send_message", methods=["POST"])
def send_message():
    """Отправка сообщения"""
    if 'user_id' not in session:
        return jsonify({"result": False, "message": "Сначала авторизуйтесь!", "code": 401})

    data = request.json
    
    receiver_id = data.get("receiver_id", type=int)
    text = data.get("text", "").strip()

    if not receiver_id or not text:
        return jsonify({"result": False, "message": "Неверные данные!", "code": 400})

    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute(
        "INSERT INTO messages (sender_id, receiver_id, text, created_at) VALUES (%s, %s, %s, NOW())",
        (session['user_id'], receiver_id, text)
    )
    new_message_id = cursor.lastrowid
    cursor.close()

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
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT m.*, u.login as sender_login, u.name as sender_name
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE (m.sender_id = %s AND m.receiver_id = %s) 
           OR (m.sender_id = %s AND m.receiver_id = %s)
        ORDER BY m.created_at ASC
    """, (session['user_id'], receiver_id, receiver_id, session['user_id']))
    
    messages = cursor.fetchall()
    cursor.close()

    return jsonify(messages)


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
    app.run(debug=True)
