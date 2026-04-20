# Инструкции для разработчиков

> Читай внимательно свой раздел. Здесь написано пошагово что делать,
> какие файлы трогать и что в них менять.

---

## Про ID в комментариях кода

По всему коду встречаются пометки вида `(Илья — ID 3)` или `(Евгений — ID 5)`.
ID — это просто номер задачи из файла `backlog.md`.
Например: ID 5 = строка 5 в backlog = "История БД".
Это помогает понять какой кусок кода за какую задачу отвечает.

---

## Архитектура проекта

```
chat-project/
│
├── app.py                ← главный файл: весь Python, маршруты, логика
├── chat.db               ← база данных (создаётся сама при запуске app.py)
├── README.md             ← описание проекта
├── instructions.md       ← этот файл
├── backlog.md            ← список задач
│
├── templates/            ← HTML-страницы (Flask ищет шаблоны именно здесь)
│   ├── index.html        ← страница входа и регистрации
│   └── chat.html         ← страница самого чата
│
└── static/               ← файлы которые браузер скачивает напрямую
    ├── style.css         ← стили внешнего вида (ЗАДАЧА АННЫ)
    └── chat.js           ← динамика без перезагрузки (ЗАДАЧА АННЫ)
```

---

## Как запустить проект

1. Открыть папку проекта в VS Code
2. Открыть терминал: меню Terminal → New Terminal
3. В терминале должно быть написано `(venv)` в начале строки — это виртуальное окружение
4. Написать команду и нажать Enter:
   ```
   python app.py
   ```
5. Открыть браузер и перейти: `http://127.0.0.1:5000`
6. Остановить сервер: нажать `Ctrl+C` в терминале

---

## Как работает приложение — схема

```
Пользователь в браузере
         │
         │ открывает страницу / отправляет форму
         ▼
      app.py (Flask сервер)
         │
         ├─ маршрут "/"       → показывает index.html (форма входа)
         ├─ маршрут "/login"  → проверяет ник и пароль в БД
         ├─ маршрут "/chat"   → показывает chat.html + сообщения из БД
         ├─ маршрут "/send"   → сохраняет новое сообщение в БД
         └─ маршрут "/logout" → удаляет сессию, возвращает на главную
         │
         ▼
      chat.db (файл базы данных SQLite)
         │
         ├─ таблица users    → id, nickname, password
         └─ таблица messages → id, nickname, text, timestamp
```

---

## Задачи Ильи — ВЫПОЛНЕНО ✅

**ID 4 — Уникальные никнеймы**
Реализовано в `app.py` маршрут `/login` и в `templates/index.html`.

**ID 3 — Отправка сообщений**
Реализовано в `app.py` маршрут `/send` и форма в `templates/chat.html`.

---

## Задачи Евгения

Евгений, база данных уже создаётся автоматически когда запускается `app.py`.
Файл `chat.db` появится в папке проекта при первом запуске — это нормально.
Твоя задача — **убедиться что всё работает правильно и улучшить**.

### Шаг 1 — Разобраться как устроена БД

Открой файл `app.py`. Найди функцию `init_db()` (примерно строка 20).
Там создаются две таблицы:

```
Таблица users (пользователи):
  id       — номер пользователя (1, 2, 3...)
  nickname — никнейм (уникальный)
  password — пароль

Таблица messages (сообщения):
  id        — номер сообщения
  nickname  — кто написал
  text      — текст сообщения
  timestamp — дата и время в формате "15.04.2026|14:30"
```

### Шаг 2 — Проверить работу

Запусти проект, зайди под разными никнеймами, напиши несколько сообщений.
Убедись что:
- история сохраняется после перезапуска сервера
- у каждого сообщения правильно показывается автор и время
- при входе с тем же ником видна вся предыдущая переписка

### Шаг 3 — Ограничить количество сообщений (ID 5)

Сейчас загружаются **все** сообщения из БД.
Если их станет тысячи — страница будет грузиться медленно.
Нужно загружать только последние 100.

Найди в `app.py` маршрут `/chat` (функция `def chat()`).
Найди там эту строку:
```python
messages = conn.execute("SELECT * FROM messages ORDER BY id ASC").fetchall()
```
Замени её на эти две строки:
```python
# Берём последние 100 сообщений (от новых к старым), потом переворачиваем
rows = conn.execute("SELECT * FROM messages ORDER BY id DESC LIMIT 100").fetchall()
messages = list(reversed(rows))  # переворачиваем — теперь от старых к новым
```

### Шаг 4 — Настроить формат времени (ID 7)

Сейчас время хранится в формате `15.04.2026|14:30`.
Если хочешь изменить как показывается дата — найди в `app.py`
маршрут `/send` (функция `def send()`). Там есть строка:
```python
timestamp = now.strftime("%d.%m.%Y|%H:%M")
```
Менять можно только **левую часть до символа |** (это дата).
Правая часть после | — это время, его формат менять не нужно.

Варианты для даты:
```
"%d.%m.%Y"   →  15.04.2026  (текущий вариант)
"%d %B %Y"   →  15 April 2026  (английский месяц)
"%Y-%m-%d"   →  2026-04-15  (международный формат ISO)
```

### Шаг 5 — Сделать коммит в Git

После того как проверил и всё работает:
```
git add .
git commit -m "Евгений: проверил БД, добавил лимит 100 сообщений"
git push
```

---

## Задачи Анны

Анна, твои задачи — **внешний вид** (style.css) и **динамика** (chat.js).
Оба файла уже существуют в папке `static/`, но пока пустые.
Тебе нужно их заполнить.

---

### Часть 1 — Стили (файл `static/style.css`)

#### Что такое CSS и как он работает

CSS — это язык оформления. Ты пишешь правила вида:
```css
селектор {
    свойство: значение;
}
```
Например:
```css
body {
    background-color: #f0f0f0;  /* серый фон у всей страницы */
    font-family: Arial;          /* шрифт Arial везде */
}
```

#### Шаг 1 — Понять что уже есть в HTML

Открой `templates/chat.html`. Там уже прописаны классы (атрибуты `class="..."`):
```
.greeting      — строка "Добрый день, Илья!"
.date-divider  — разделитель с датой между сообщениями разных дней
.message       — один пузырёк сообщения
.message-meta  — строка с автором и временем (мелкая, серая)
.author        — никнейм автора внутри .message-meta
.time          — время внутри .message-meta
.message-text  — текст сообщения
#messages      — весь блок чата (решётка # означает id, не class)
#message-form  — форма отправки
#message-input — поле ввода текста
```

#### Шаг 2 — Начать с простого

Создай базовую структуру в `style.css`:
```css
/* Общие настройки страницы */
body {
    font-family: Arial, sans-serif;
    background-color: #eef2f7;
    margin: 0;
    padding: 20px;
}

/* Блок сообщений */
#messages {
    background: white;
    border-radius: 12px;
    padding: 16px;
    height: 400px;
    overflow-y: scroll;  /* прокрутка */
}

/* Один пузырёк сообщения */
.message {
    background: #f0f0f0;
    border-radius: 10px;
    padding: 8px 14px;
    margin-bottom: 8px;
    max-width: 70%;
}

/* Автор и время — маленькие и серые */
.message-meta {
    font-size: 0.75em;
    color: #aaa;
}
```

#### Шаг 3 — Сделать пузырьки как в мессенджере

В настоящих мессенджерах свои сообщения — справа, чужие — слева.
Для этого нужно знать ник текущего пользователя прямо в CSS —
но CSS этого не умеет, это делается через JavaScript или атрибуты data-.

Пока сделай все пузырьки одного стиля (слева).
Когда Илья добавит `data-owner` атрибут к сообщениям — сможешь сделать деление.

#### Шаг 4 — Адаптация под телефон

Добавь в конец `style.css`:
```css
/* На маленьких экранах (телефон) */
@media (max-width: 600px) {
    body {
        padding: 8px;
    }
    .message {
        max-width: 95%;
    }
}
```

#### Шаг 5 — Коммит
```
git add .
git commit -m "Анна: добавила стили чата"
git push
```

---

### Часть 2 — Динамика (файл `static/chat.js`) — ID 6

#### Что такое "динамическая отправка"

Сейчас: написал сообщение → нажал Отправить → **страница перезагрузилась** → увидел сообщение.

После твоей задачи: написал → нажал Отправить → сообщение **появилось само** без перезагрузки. Как в Telegram.

#### Шаг 1 — Понять как это работает

JavaScript в браузере умеет отправлять данные на сервер **тихо, в фоне**.
Это называется `fetch` (от английского "принести").

```
Браузер                           Сервер (app.py)
   │                                    │
   │  Пользователь нажал Отправить      │
   │  JS перехватывает, НЕ перезагружает│
   │                                    │
   │──── fetch POST /send ─────────────>│
   │                                    │  сохраняет в БД
   │<─── ок ───────────────────────────│
   │                                    │
   │──── fetch GET /messages ──────────>│
   │                                    │  читает из БД
   │<─── JSON со списком сообщений ────│
   │                                    │
   │  JS добавляет новое сообщение      │
   │  в блок #messages                  │
```

#### Шаг 2 — Добавить маршрут в app.py

Сначала скажи Илье добавить в `app.py` новый маршрут:
```python
import json

@app.route("/messages")
def get_messages():
    """Возвращает все сообщения в формате JSON — для JavaScript"""
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
```

#### Шаг 3 — Написать chat.js

```javascript
// Находим форму и поле ввода на странице
const form = document.getElementById("message-form");
const input = document.getElementById("message-input");
const messagesDiv = document.getElementById("messages");

// Функция загружает сообщения с сервера и обновляет блок #messages
function loadMessages() {
    fetch("/messages")                          // тихий запрос к серверу
        .then(response => response.json())      // превращаем ответ в массив
        .then(messages => {
            messagesDiv.innerHTML = "";         // очищаем блок
            let lastDate = "";

            messages.forEach(msg => {
                const parts = msg.timestamp.split("|");
                const date = parts[0];
                const time = parts[1];

                // Показываем разделитель с датой только когда день меняется
                if (date !== lastDate) {
                    const divider = document.createElement("div");
                    divider.className = "date-divider";
                    divider.textContent = date;
                    messagesDiv.appendChild(divider);
                    lastDate = date;
                }

                // Создаём пузырёк сообщения
                const div = document.createElement("div");
                div.className = "message";
                div.innerHTML = `
                    <div class="message-meta">
                        <span class="author">${msg.nickname}</span>
                        <span class="time">${time}</span>
                    </div>
                    <p class="message-text">${msg.text}</p>
                `;
                messagesDiv.appendChild(div);
            });

            // Прокручиваем вниз к последним сообщениям
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        });
}

// Перехватываем отправку формы — не даём странице перезагрузиться
form.addEventListener("submit", function(e) {
    e.preventDefault();  // отменяем стандартное поведение формы

    const text = input.value.trim();
    if (!text) return;

    // Отправляем сообщение на сервер тихо
    fetch("/send", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: "message=" + encodeURIComponent(text)
    }).then(() => {
        input.value = "";    // очищаем поле ввода
        loadMessages();      // обновляем список сообщений
    });
});

// Загружаем сообщения при открытии страницы
loadMessages();

// Обновляем каждые 3 секунды — чтобы видеть сообщения других пользователей
setInterval(loadMessages, 3000);
```

#### Шаг 4 — Коммит
```
git add .
git commit -m "Анна: добавила динамическую отправку сообщений"
git push
```

---

## Git — командная работа

Перед началом работы (получить последние изменения от команды):
```
git pull
```

После своих изменений:
```
git add .
git commit -m "Имя: что именно сделал"
git push
```

Репозиторий: https://github.com/MavrinIlua/chat-project-mavrin-vartiainen-sablev.git

---

## Частые ошибки

| Ошибка | Причина | Решение |
|--------|---------|---------|
| "Не удаётся подключиться" | Сервер не запущен | Запустить `python app.py` |
| TemplateSyntaxError | Пропущен `{% endif %}` или `{% endfor %}` | Проверить HTML |
| Сообщения дублируются | Старые тестовые данные в chat.db | Удалить файл chat.db |
| chat.db выглядит как мусор | Это бинарный файл | Не открывать в редакторе |
