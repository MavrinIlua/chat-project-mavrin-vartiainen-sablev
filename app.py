from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3, datetime

app = Flask(__name__)
app.secret_key = "секрет123"


# ---------------------------------------------------------------
# БАЗА ДАННЫХ
# ---------------------------------------------------------------

def get_db():
    """Открывает соединение с базой данных"""
    conn = sqlite3.connect("chat.db")
    conn.row_factory = sqlite3.Row  # поля доступны по имени: row["nickname"]
    return conn


def init_db():
    """Создаёт таблицы при первом запуске — если их ещё нет"""
    conn = get_db()

    # Таблица пользователей (Илья — ID 4)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Таблица сообщений (Евгений — ID 5, 7)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname  TEXT NOT NULL,
            text      TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ---------------------------------------------------------------
# МАРШРУТЫ — ВХОД И РЕГИСТРАЦИЯ (Илья — ID 4)
# ---------------------------------------------------------------

@app.route("/")
def index():
    """Главная страница — форма входа"""
    return render_template("index.html")


@app.route("/login", methods=["POST"])
def login():
    """
    Обрабатывает форму входа.
    Сценарий 1: новый ник → регистрируем
    Сценарий 2: ник есть + пароль верный → входим
    Сценарий 3: пароль неверный → ошибка
    """
    nickname = request.form.get("nickname", "").strip()
    password = request.form.get("password", "").strip()

    # Защита от пустых полей (на случай если HTML-атрибут required обошли)
    if not nickname or not password:
        return render_template("index.html", error="Заполни оба поля!")

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE nickname = ?", (nickname,)
    ).fetchone()

    if user is None:
        # Новый пользователь — регистрируем
        conn.execute(
            "INSERT INTO users (nickname, password) VALUES (?, ?)",
            (nickname, password)
        )
        conn.commit()
        session["nickname"] = nickname

    elif user["password"] == password:
        # Пароль совпадает — входим
        session["nickname"] = nickname

    else:
        # Пароль неверный
        conn.close()
        return render_template("index.html", error="Неверный пароль!")

    conn.close()
    return redirect(url_for("chat"))


# ---------------------------------------------------------------
# МАРШРУТЫ — ЧАТ (Илья — ID 3, Евгений — ID 5 и 7)
# ---------------------------------------------------------------

@app.route("/chat")
def chat():
    """
    Страница чата.
    Если пользователь не вошёл — отправляем на главную.
    Евгений: здесь читаем сообщения из БД.
    """
    if "nickname" not in session:
        return redirect(url_for("index"))

    conn = get_db()
    # Евгений (ID 5): берём все сообщения, от старых к новым
    messages = conn.execute(
        "SELECT * FROM messages ORDER BY id ASC"
    ).fetchall()
    conn.close()

    return render_template(
        "chat.html",
        nickname=session["nickname"],
        messages=messages
    )


@app.route("/send", methods=["POST"])
def send():
    """
    Принимает сообщение из формы и сохраняет в БД.
    Илья (ID 3): отправка сообщений.
    Евгений (ID 7): timestamp записывается здесь.
    """
    if "nickname" not in session:
        return redirect(url_for("index"))

    text = request.form.get("message", "").strip()

    if text:  # сохраняем только если сообщение не пустое
        # Евгений (ID 7): формат времени можно изменить здесь
        timestamp = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        conn = get_db()
        conn.execute(
            "INSERT INTO messages (nickname, text, timestamp) VALUES (?, ?, ?)",
            (session["nickname"], text, timestamp)
        )
        conn.commit()
        conn.close()

    return redirect(url_for("chat"))


# ---------------------------------------------------------------
# МАРШРУТ — ВЫХОД
# ---------------------------------------------------------------

@app.route("/logout")
def logout():
    """Удаляет сессию и возвращает на главную"""
    session.pop("nickname", None)
    return redirect(url_for("index"))


# ---------------------------------------------------------------
# ЗАПУСК
# ---------------------------------------------------------------

if __name__ == "__main__":
    init_db()            # создаём таблицы если их нет
    app.run(debug=True)  # debug=True — показывает ошибки в браузере
