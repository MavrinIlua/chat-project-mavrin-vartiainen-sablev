from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3  # встроенная библиотека Python для работы с базой данных

app = Flask(__name__)

# Секретный ключ — нужен Flask чтобы шифровать сессию (данные о том кто вошёл).
# В реальном проекте это длинная случайная строка, но для учёбы так сойдёт
app.secret_key = "мой_секретный_ключ_123"

# --- ФУНКЦИЯ ДЛЯ ПОДКЛЮЧЕНИЯ К БАЗЕ ДАННЫХ ---
# Каждый раз когда нам нужна БД — вызываем эту функцию
# Она возвращает объект соединения с файлом chat.db
def get_db():
    conn = sqlite3.connect("chat.db")       # создаёт файл chat.db если его нет
    conn.row_factory = sqlite3.Row          # чтобы данные возвращались как словарь, а не просто список
    return conn

# --- СОЗДАНИЕ ТАБЛИЦ ПРИ ПЕРВОМ ЗАПУСКЕ ---
# Эта функция создаёт таблицу пользователей если её ещё нет
def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname TEXT    UNIQUE NOT NULL,
            password TEXT    NOT NULL
        )
    """)
    # CREATE TABLE IF NOT EXISTS — создай таблицу ТОЛЬКО если её ещё нет
    # id — уникальный номер каждого пользователя, растёт автоматически
    # nickname TEXT UNIQUE — никнейм, тип "текст", и обязательно уникальный
    # password TEXT NOT NULL — пароль, не может быть пустым
    conn.commit()   # сохраняем изменения в файл
    conn.close()    # закрываем соединение

# --- ГЛАВНАЯ СТРАНИЦА — форма входа/регистрации ---
@app.route("/")
def index():
    return render_template("index.html")

# --- МАРШРУТ ВХОДА/РЕГИСТРАЦИИ ---
# method=["POST"] — эта страница принимает данные из формы
@app.route("/login", methods=["POST"])
def login():
    # Берём никнейм и пароль из формы которую отправил пользователь
    nickname = request.form.get("nickname")
    password = request.form.get("password")

    conn = get_db()

    # Ищем пользователя с таким никнеймом в базе данных
    # ? — это защита от SQL-инъекций (хакерских атак через форму)
    user = conn.execute(
        "SELECT * FROM users WHERE nickname = ?", (nickname,)
    ).fetchone()  # fetchone — берём одну запись (или None если не нашли)

    if user is None:
        # Такого никнейма нет → РЕГИСТРАЦИЯ нового пользователя
        conn.execute(
            "INSERT INTO users (nickname, password) VALUES (?, ?)",
            (nickname, password)
        )
        conn.commit()
        # Запоминаем в сессии что этот пользователь вошёл
        session["nickname"] = nickname

    elif user["password"] == password:
        # Ник найден и пароль совпадает → АВТОРИЗАЦИЯ
        session["nickname"] = nickname

    else:
        # Ник найден но пароль неверный → показываем ошибку
        conn.close()
        # render_template с параметром error — передаём текст ошибки в HTML
        return render_template("index.html", error="Неверный пароль!")

    conn.close()
    # redirect — перенаправляем на страницу чата
    # url_for("chat") — Flask сам строит адрес для функции chat()
    return redirect(url_for("chat"))

# --- СТРАНИЦА ЧАТА ---
@app.route("/chat")
def chat():
    # Проверяем что пользователь вошёл (его ник есть в сессии)
    if "nickname" not in session:
        # Если не вошёл — отправляем обратно на главную
        return redirect(url_for("index"))

    # Передаём никнейм в шаблон чтобы отобразить "Привет, Илья!"
    return render_template("chat.html", nickname=session["nickname"])

# --- ВЫХОД ИЗ ЧАТА ---
@app.route("/logout")
def logout():
    session.pop("nickname", None)   # удаляем никнейм из сессии
    return redirect(url_for("index"))

# Запускаем сервер
if __name__ == "__main__":
    init_db()           # сначала создаём таблицы в БД
    app.run(debug=True)
