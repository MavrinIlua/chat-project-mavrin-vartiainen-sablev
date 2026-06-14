#!/usr/bin/env python
# -*- coding: utf-8 -*-

code = '''from flask import Flask, render_template, request, jsonify, session, redirect, url_for, g
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "secret123")


def get_db():
    if "db" not in g:
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
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
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
        if user and user["password"] == password:
            session["user_id"] = user["id"]
            session["user_login"] = user["login"]
            session["user_name"] = f"{user['name']} {user['surname']}"
            return jsonify({"result": True, "message": "Вход выполнен!", "code": 200})
        else:
            return jsonify({"result": False, "message": "Неверный логин или пароль!", "code": 400})
    return render_template("authorization.html")


@app.route("/chat")
def chat():
    if "user_id" not in session:
        return redirect(url_for("index"))
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (session["user_id"],))
    current_user = cursor.fetchone()
    cursor.execute("SELECT * FROM users WHERE id != %s", (session["user_id"],))
    all_users = cursor.fetchall()
    chosen_user_id = request.args.get("user_id", type=int)
    chosen_user = None
    messages = []
    if chosen_user_id:
        cursor.execute("SELECT * FROM users WHERE id = %s", (chosen_user_id,))
        chosen_user = cursor.fetchone()
        cursor.execute("SELECT m.*, u.login as sender_login, u.name as sender_name, u.surname as sender_surname FROM messages m JOIN users u ON m.sender_id = u.id WHERE (m.sender_id = %s AND m.receiver_id = %s) OR (m.sender_id = %s AND m.receiver_id = %s) ORDER BY m.created_at ASC", (session["user_id"], chosen_user_id, chosen_user_id, session["user_id"]))
        messages = cursor.fetchall()
    cursor.close()
    return render_template("chat.html", current_user=current_user, all_users=all_users, chosen_user=chosen_user, messages=messages)


@app.route("/send_message", methods=["POST"])
def send_message():
    if "user_id" not in session:
        return jsonify({"result": False, "message": "Сначала авторизуйтесь!", "code": 401})
    import datetime
    data = request.json
    receiver_id = data.get("receiver_id")
    text = data.get("text", "").strip()
    if not receiver_id or not text:
        return jsonify({"result": False, "message": "Неверные данные!", "code": 400})
    db = get_db()
    cursor = db.cursor()
    now = datetime.datetime.now()
    created_at = now.strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO messages (sender_id, receiver_id, text, created_at) VALUES (%s, %s, %s, %s)", (session["user_id"], receiver_id, text, created_at))
    cursor.close()
    return jsonify({"result": True, "code": 200})


@app.route("/get_messages", methods=["GET"])
def get_messages():
    if "user_id" not in session:
        return jsonify([])
    receiver_id = request.args.get("user_id", type=int)
    if not receiver_id:
        return jsonify([])
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT m.*, u.login as sender_login, u.name as sender_name, u.surname as sender_surname FROM messages m JOIN users u ON m.sender_id = u.id WHERE (m.sender_id = %s AND m.receiver_id = %s) OR (m.sender_id = %s AND m.receiver_id = %s) ORDER BY m.created_at ASC", (session["user_id"], receiver_id, receiver_id, session["user_id"]))
    messages = cursor.fetchall()
    cursor.close()
    return jsonify(messages)


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("user_login", None)
    session.pop("user_name", None)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, port=5001)
'''

with open('app_local.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("File app_local.py created successfully!")
