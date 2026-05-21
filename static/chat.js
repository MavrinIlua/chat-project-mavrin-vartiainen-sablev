// Находим форму и поле ввода на странице
const form = document.getElementById("message-form");
const input = document.getElementById("message-input");
const messagesDiv = document.getElementById("messages");

// Получаем никнейм текущего пользователя из data-атрибута в HTML
const currentUserNickname = document.body.dataset.nickname;

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

                // Если автор сообщения — текущий пользователь, добавляем класс "mine"
                if (msg.nickname === currentUserNickname) {
                    div.classList.add("mine");
                }

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
