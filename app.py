from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3, datetime, json
from werkzeug.security import generate_password_hash, check_password_hash

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
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
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
# ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ — приветствие по времени суток
# ---------------------------------------------------------------

def get_greeting():
    """
    Возвращает приветствие в зависимости от текущего часа.
    Международный стандарт:
    5:00–11:59  → Доброе утро
    12:00–17:59  → Добрый день
    18:00–22:59  → Добрый вечер
    23:00–4:59   → Доброй ночи
    """
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


@app.route("/register", methods=["GET", "POST"])
def register():
    """Страница и логика регистрации"""
    if request.method == "POST":
        nickname = request.form.get("nickname", "").strip()
        password = request.form.get("password", "").strip()

        if not nickname or not password:
            return render_template("registration.html", error="Заполните все поля!")

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE nickname = ?", (nickname,)).fetchone()

        if user:
            conn.close()
            return render_template("registration.html", error="Такой никнейм уже занят!")

        # Хешируем пароль перед сохранением
        hashed_password = generate_password_hash(password)
        conn.execute(
            "INSERT INTO users (nickname, password) VALUES (?, ?)",
            (nickname, hashed_password)
        )
        conn.commit()
        conn.close()

        session["nickname"] = nickname
        return redirect(url_for("chat"))

    return render_template("registration.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Страница и логика входа"""
    if request.method == "POST":
        nickname = request.form.get("nickname", "").strip()
        password = request.form.get("password", "").strip()

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE nickname = ?", (nickname,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["nickname"] = nickname
            return redirect(url_for("chat"))
        else:
            return render_template("index.html", error="Неверный никнейм или пароль!")

    return render_template("index.html")


# ---------------------------------------------------------------
# МАРШРУТЫ — ЧАТ (Илья — ID 3, Евгений — ID 5 и 7)
# ---------------------------------------------------------------

@app.route("/chat")
def chat():
    """Страница чата. Если пользователь не вошёл — отправляем на главную."""
    if "nickname" not in session:
        return redirect(url_for("index"))

    conn = get_db()
    # Берём последние 100 сообщений (от новых к старым), потом переворачиваем (Евгений - ID 5)
    rows = conn.execute("SELECT * FROM messages ORDER BY id DESC LIMIT 100").fetchall()
    conn.close()
    messages = list(reversed(rows))  # переворачиваем — теперь от старых к новым

    return render_template(
        "chat.html",
        nickname=session["nickname"],
        messages=messages,
        greeting=get_greeting()  # передаём приветствие по времени суток
    )


@app.route("/send", methods=["POST"])
def send():
    """Принимает сообщение из формы и сохраняет в БД."""
    if "nickname" not in session:
        return redirect(url_for("index"))

    text = request.form.get("message", "").strip()

    if text:
        # Сохраняем дату и время отдельно через разделитель |
        # Дата нужна для группировки по дням, время — для отображения у сообщения
        now = datetime.datetime.now()
        timestamp = now.strftime("%d.%m.%Y|%H:%M")  # формат: "15.04.2026|14:30"
        conn = get_db()
        conn.execute(
            "INSERT INTO messages (nickname, text, timestamp) VALUES (?, ?, ?)",
            (session["nickname"], text, timestamp)
        )
        conn.commit()
        conn.close()

    return redirect(url_for("chat"))


# ---------------------------------------------------------------
# МАРШРУТ ДЛЯ JAVASCRIPT (Анна - ID 6)
# ---------------------------------------------------------------

@app.route("/messages")
def get_messages():
    """Возвращает последние 100 сообщений в формате JSON — для JavaScript"""
    if "nickname" not in session:
        return json.dumps([])
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM messages ORDER BY id DESC LIMIT 100"
    ).fetchall()
    conn.close()
    messages = list(reversed(rows))
    # Преобразуем в список словарей — JSON не умеет работать с sqlite3.Row
    result = [{"nickname": m["nickname"],
               "text": m["text"],
               "timestamp": m["timestamp"]} for m in messages]
    return json.dumps(result, ensure_ascii=False)

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
    init_db()
    app.run(debug=True)
