from flask import Flask, render_template, request, jsonify, session, redirect, url_for, g
import mysql.connector
import os
import datetime
from datetime import timedelta

app = Flask(__name__)
app.config["SECRET_KEY"] = "super_secret_key_2024"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=31)

# MySQL connection parameters
DB_CONFIG = {
    "host": "185.114.247.43",
    "database": "sch688_maga1",
    "user": "sch688_maga1",
    "password": "Fqx8irSU",
    "port": 3306
}


def get_db():
    """Получение подключения к MySQL."""
    if "db" not in g:
        try:
            g.db = mysql.connector.connect(**DB_CONFIG)
            g.db.autocommit = True
        except mysql.connector.Error as err:
            print(f"Ошибка подключения к MySQL: {err}")
            raise
    return g.db


@app.teardown_appcontext
def close_db(error):
    """Закрытие подключения к MySQL."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.route("/")
def index():
    """Редирект на страницу входа."""
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """Страница входа."""
    if request.method == "POST":
        data = request.json
        login = data.get("login", "").strip()
        password = data.get("password", "").strip()
        
        if not login or not password:
            return jsonify({"result": False, "message": "Введите логин и пароль!", "code": 400})
        
        try:
            db = get_db()
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE login = %s", (login,))
            user = cursor.fetchone()
            cursor.close()
            
            if user and user["password"] == password:
                session["user_id"] = user["id"]
                session["user_login"] = user["login"]
                session["user_name"] = f"{user['name']} {user['surname']}"
                session.permanent = True
                return jsonify({"result": True, "message": "Вход выполнен!", "code": 200})
            else:
                return jsonify({"result": False, "message": "Неверный логин или пароль!", "code": 400})
        except mysql.connector.Error as err:
            return jsonify({"result": False, "message": f"Ошибка базы данных: {err}", "code": 500})
    
    return render_template("authorization.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Страница регистрации."""
    if request.method == "POST":
        data = request.json
        name = data.get("name", "").strip()
        surname = data.get("surname", "").strip()
        login = data.get("login", "").strip()
        password = data.get("password", "").strip()
        
        # Валидация
        if not name or not surname or not login or not password:
            return jsonify({"result": False, "message": "Заполните все поля!", "code": 400})
        
        if len(login) < 3 or len(login) > 30:
            return jsonify({"result": False, "message": "Логин должен быть от 3 до 30 символов!", "code": 400})
        
        if len(password) < 6:
            return jsonify({"result": False, "message": "Пароль должен быть минимум 6 символов!", "code": 400})
        
        try:
            db = get_db()
            cursor = db.cursor(dictionary=True)
            
            # Проверка существования логина
            cursor.execute("SELECT * FROM users WHERE login = %s", (login,))
            if cursor.fetchone():
                cursor.close()
                return jsonify({"result": False, "message": "Этот логин уже занят!", "code": 400})
            
            # Регистрация
            cursor.execute(
                "INSERT INTO users (name, surname, login, password) VALUES (%s, %s, %s, %s)",
                (name, surname, login, password)
            )
            db.commit()
            cursor.close()
            
            return jsonify({"result": True, "message": "Регистрация успешна!", "code": 200})
        except mysql.connector.Error as err:
            return jsonify({"result": False, "message": f"Ошибка базы данных: {err}", "code": 500})
    
    return render_template("registration.html")


@app.route("/chat")
def chat():
    """Страница чата."""
    if "user_id" not in session:
        return redirect(url_for("index"))
    
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Получаем текущего пользователя
        cursor.execute("SELECT * FROM users WHERE id = %s", (session["user_id"],))
        current_user = cursor.fetchone()
        
        # Получаем всех других пользователей
        cursor.execute("SELECT * FROM users WHERE id != %s ORDER BY name, surname", (session["user_id"],))
        all_users = cursor.fetchall()
        
        # Получаем chosen_user_id из параметров запроса
        chosen_user_id = request.args.get("user_id", type=int)
        chosen_user = None
        messages = []
        
        if chosen_user_id:
            cursor.execute("SELECT * FROM users WHERE id = %s", (chosen_user_id,))
            chosen_user = cursor.fetchone()
            
            # Получаем сообщения между пользователями
            cursor.execute(
                """SELECT m.*, u.login as sender_login, u.name as sender_name, u.surname as sender_surname 
                   FROM messages m 
                   JOIN users u ON m.sender_id = u.id 
                   WHERE (m.sender_id = %s AND m.receiver_id = %s) 
                      OR (m.sender_id = %s AND m.receiver_id = %s) 
                   ORDER BY m.created_at ASC""",
                (session["user_id"], chosen_user_id, chosen_user_id, session["user_id"])
            )
            messages = cursor.fetchall()
        
        cursor.close()
        
        return render_template(
            "chat.html",
            current_user=current_user,
            all_users=all_users,
            chosen_user=chosen_user,
            messages=messages
        )
    except mysql.connector.Error as err:
        return f"Ошибка базы данных: {err}", 500


@app.route("/send_message", methods=["POST"])
def send_message():
    """Отправка сообщения."""
    if "user_id" not in session:
        return jsonify({"result": False, "message": "Сначала авторизуйтесь!", "code": 401})
    
    try:
        data = request.json
        receiver_id = data.get("receiver_id")
        text = data.get("text", "").strip()
        
        if not receiver_id or not text:
            return jsonify({"result": False, "message": "Неверные данные!", "code": 400})
        
        db = get_db()
        cursor = db.cursor()
        
        now = datetime.datetime.now()
        created_at = now.strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute(
            "INSERT INTO messages (sender_id, receiver_id, text, created_at) VALUES (%s, %s, %s, %s)",
            (session["user_id"], receiver_id, text, created_at)
        )
        db.commit()
        cursor.close()
        
        return jsonify({"result": True, "code": 200})
    except mysql.connector.Error as err:
        return jsonify({"result": False, "message": f"Ошибка базы данных: {err}", "code": 500})


@app.route("/get_messages", methods=["GET"])
def get_messages():
    """Получение истории переписки."""
    if "user_id" not in session:
        return jsonify([])
    
    receiver_id = request.args.get("user_id", type=int)
    if not receiver_id:
        return jsonify([])
    
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute(
            """SELECT m.*, u.login as sender_login, u.name as sender_name, u.surname as sender_surname 
               FROM messages m 
               JOIN users u ON m.sender_id = u.id 
               WHERE (m.sender_id = %s AND m.receiver_id = %s) 
                  OR (m.sender_id = %s AND m.receiver_id = %s) 
               ORDER BY m.created_at ASC""",
            (session["user_id"], receiver_id, receiver_id, session["user_id"])
        )
        messages = cursor.fetchall()
        cursor.close()
        
        # Форматируем данные для JSON
        result = []
        for msg in messages:
            result.append({
                "id": msg["id"],
                "sender_id": msg["sender_id"],
                "receiver_id": msg["receiver_id"],
                "text": msg["text"],
                "created_at": str(msg["created_at"]) if msg["created_at"] else None,
                "sender_login": msg["sender_login"],
                "sender_name": msg["sender_name"],
                "sender_surname": msg["sender_surname"]
            })
        
        return jsonify(result)
    except mysql.connector.Error as err:
        return jsonify([])


@app.route("/edit_message", methods=["POST"])
def edit_message():
    """Редактирование сообщения."""
    if "user_id" not in session:
        return jsonify({"result": False, "message": "Сначала авторизуйтесь!", "code": 401})
    
    try:
        data = request.json
        message_id = data.get("message_id")
        new_text = data.get("text", "").strip()
        
        if not message_id or not new_text:
            return jsonify({"result": False, "message": "Неверные данные!", "code": 400})
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Проверяем, что сообщение принадлежит текущему пользователю
        cursor.execute("SELECT * FROM messages WHERE id = %s", (message_id,))
        message = cursor.fetchone()
        
        if not message or message["sender_id"] != session["user_id"]:
            cursor.close()
            return jsonify({"result": False, "message": "Нет прав для редактирования этого сообщения!", "code": 403})
        
        # Редактируем сообщение
        cursor.execute(
            "UPDATE messages SET text = %s WHERE id = %s",
            (new_text, message_id)
        )
        db.commit()
        cursor.close()
        
        return jsonify({"result": True, "code": 200})
    except mysql.connector.Error as err:
        return jsonify({"result": False, "message": f"Ошибка базы данных: {err}", "code": 500})


@app.route("/delete_message", methods=["POST"])
def delete_message():
    """Удаление сообщения."""
    if "user_id" not in session:
        return jsonify({"result": False, "message": "Сначала авторизуйтесь!", "code": 401})
    
    try:
        data = request.json
        message_id = data.get("message_id")
        
        if not message_id:
            return jsonify({"result": False, "message": "Неверные данные!", "code": 400})
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Проверяем, что сообщение принадлежит текущему пользователю
        cursor.execute("SELECT * FROM messages WHERE id = %s", (message_id,))
        message = cursor.fetchone()
        
        if not message or message["sender_id"] != session["user_id"]:
            cursor.close()
            return jsonify({"result": False, "message": "Нет прав для удаления этого сообщения!", "code": 403})
        
        # Удаляем сообщение
        cursor.execute("DELETE FROM messages WHERE id = %s", (message_id,))
        db.commit()
        cursor.close()
        
        return jsonify({"result": True, "code": 200})
    except mysql.connector.Error as err:
        return jsonify({"result": False, "message": f"Ошибка базы данных: {err}", "code": 500})


@app.route("/logout")
def logout():
    """Выход из системы."""
    session.pop("user_id", None)
    session.pop("user_login", None)
    session.pop("user_name", None)
    return redirect(url_for("index"))


@app.route("/get_users")
def get_users():
    """Получение списка всех пользователей (для динамического обновления)."""
    if "user_id" not in session:
        return jsonify([])
    
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id, name, surname, login FROM users WHERE id != %s ORDER BY name, surname", (session["user_id"],))
        users = cursor.fetchall()
        cursor.close()
        
        # Форматируем данные для JSON
        result = []
        for user in users:
            result.append({
                "id": user["id"],
                "name": user["name"],
                "surname": user["surname"],
                "login": user["login"]
            })
        
        return jsonify(result)
    except mysql.connector.Error as err:
        return jsonify([])


@app.route("/get_user_info")
def get_user_info():
    """Получение информации о текущем пользователе."""
    if "user_id" not in session:
        return jsonify({"result": False})
    
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id, name, surname, login FROM users WHERE id = %s", (session["user_id"],))
        user = cursor.fetchone()
        cursor.close()
        
        if user:
            return jsonify({
                "result": True,
                "id": user["id"],
                "name": user["name"],
                "surname": user["surname"],
                "login": user["login"]
            })
        else:
            return jsonify({"result": False})
    except mysql.connector.Error as err:
        return jsonify({"result": False})


if __name__ == "__main__":
    app.run(debug=True, port=5001)
