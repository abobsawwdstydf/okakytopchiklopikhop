import asyncio
import logging
import sys
import subprocess
import importlib
import os
from datetime import datetime
import json
import random
from typing import Dict, Any, Optional

# Авто-установка необходимых библиотек
def install_required_packages():
    required_packages = [
        'aiogram==2.25.1',
        'aiohttp==3.8.4',
        'pytz==2022.7'
    ]
    
    print("🔧 Проверка зависимостей...")
    for package in required_packages:
        try:
            package_name = package.split('==')[0]
            importlib.import_module(package_name)
            print(f"✅ {package_name} уже установлен")
        except ImportError:
            print(f"📦 Устанавливаю {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} успешно установлен")

# Устанавливаем библиотеки
install_required_packages()

# Теперь импортируем установленные библиотеки
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import pytz

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Конфигурация бота
BOT_TOKEN = "8524355119:AAExHf5r0GZQxXiB58S95nOaqdS9DfyfYWI"
ADMIN_ID = 7215210750

# Хранилище данных пользователей
user_data = {}

# Планы обучения с ежедневными заданиями
learning_plans = {
    "python_7": {
        "name": "🐍 Python за 7 дней",
        "description": "Экспресс-курс для быстрого старта в Python",
        "days": {
            1: """🚀 <b>ДЕНЬ 1: УСТАНОВКА И ПЕРВЫЙ СКРИПТ!</b> 💥

🎯 <b>ЗАДАНИЕ:</b>
1️⃣ Установи Python с python.org
2️⃣ Напиши скрипт который выводит твое имя и возраст
3️⃣ Запусти его через терминал

💻 <b>Пример кода:</b>
<pre>
name = "Твое_имя"
age = 25
print(f"Привет, меня зовут {name} и мне {age} лет!")
</pre>

⚡️ <b>ДЕЛАЙ СЕЙЧАС!</b> Не откладывай!""",
            2: """🔥 <b>ДЕНЬ 2: УСЛОВИЯ И ЛОГИКА!</b> 🧠

🎯 <b>ЗАДАНИЕ:</b>
• Напиши скрипт, который проверяет твой возраст
• Если больше 18 - 'Доступ разрешен', иначе - 'Доступ запрещен'
• Добавь проверку на пустой ввод

💻 <b>Пример кода:</b>
<pre>
age_input = input("Сколько тебе лет? ")
if age_input.strip() == "":
    print("Ошибка: пустой ввод!")
else:
    age = int(age_input)
    if age >= 18:
        print("Доступ разрешен! 🎉")
    else:
        print("Доступ запрещен! ⚠️")
</pre>

🎯 <b>ВПЕРЕД КОДИТЬ!</b>""",
            3: """⚡️ <b>ДЕНЬ 3: ЦИКЛЫ И СПИСКИ!</b> 🔄

🎯 <b>ЗАДАНИЕ:</b>
• Создай список из 5 чисел
• Напиши цикл, который выводит каждый элемент
• Сделай сумму всех чисел в списке

💻 <b>Пример кода:</b>
<pre>
numbers = [1, 2, 3, 4, 5]
total = 0

for num in numbers:
    print(f"Число: {num}")
    total += num

print(f"Сумма: {total}")
</pre>

💥 <b>РАБОТАЙ БЕЗ ОСТАНОВКИ!</b>""",
            4: """💫 <b>ДЕНЬ 4: ФУНКЦИИ - ТВОЙ НОВЫЙ СУПЕРСИЛА!</b> 🦸

🎯 <b>ЗАДАНИЕ:</b>
• Создай функцию для расчета площади круга
• Создай функцию для проверки четности числа
• Вызови их с разными параметрами

💻 <b>Пример кода:</b>
<pre>
import math

def circle_area(radius):
    return math.pi * radius ** 2

def is_even(number):
    return number % 2 == 0

print(f"Площадь круга: {circle_area(5):.2f}")
print(f"Четное число? {is_even(10)}")
</pre>

🚀 <b>КОДИМ ДАЛЬШЕ!</b>""",
            5: """🎯 <b>ДЕНЬ 5: РАБОТА С ФАЙЛАМИ!</b> 📁

🎯 <b>ЗАДАНИЕ:</b>
• Создай текстовый файл
• Запиши в него несколько строк
• Прочитай и выведи содержимое

💻 <b>Пример кода:</b>
<pre>
# Запись в файл
with open("дневник.txt", "w", encoding="utf-8") as file:
    file.write("Мой первый файл\\n")
    file.write("Сегодня я изучал Python!\\n")

# Чтение из файла
with open("дневник.txt", "r", encoding="utf-8") as file:
    content = file.read()
    print(content)
</pre>

⚡️ <b>НЕ ОСТАНАВЛИВАЙСЯ!</b>""",
            6: """🚀 <b>ДЕНЬ 6: БИБЛИОТЕКИ И API!</b> 🌐

🎯 <b>ЗАДАНИЕ:</b>
• Установи библиотеку requests через pip
• Сделай запрос к какому-нибудь публичному API
• Обработай и выведи результат

💻 <b>Пример кода:</b>
<pre>
# Установи requests: pip install requests
import requests

response = requests.get("https://api.github.com")
if response.status_code == 200:
    print(f"Статус: {response.status_code}")
    print(f"Данные: {response.json()}")
else:
    print(f"Ошибка запроса: {response.status_code}")
</pre>

💥 <b>ТЫ УЖЕ ПРОГРАММИСТ!</b>""",
            7: """🎉 <b>ДЕНЬ 7: ФИНАЛ! ЗАВЕРШАЮЩИЙ ПРОЕКТ!</b> 🏆

🎯 <b>ЗАДАНИЕ:</b>
Создай простой телеграм бот или парсер сайта!

💻 <b>Пример бота:</b>
<pre>
# Установи aiogram: pip install aiogram==2.25.1
from aiogram import Bot, Dispatcher, executor, types

bot = Bot(token="ТВОЙ_ТОКЕН")
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Привет! Я твой первый бот!")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
</pre>

🔥 <b>ПОЗДРАВЛЯЕМ!</b> Ты прошел курс! МОЛОДЕЦ!"""
        }
    },
    "nodejs_7": {
        "name": "💚 Node.js за 7 дней",
        "description": "Быстрый старт в серверном JavaScript",
        "days": {
            1: """🚀 <b>ДЕНЬ 1: УСТАНОВКА И ПЕРВЫЙ СЕРВЕР!</b> 💥

🎯 <b>ЗАДАНИЕ:</b>
1️⃣ Установи Node.js с nodejs.org
2️⃣ Создай файл server.js
3️⃣ Запусти простой HTTP сервер

💻 <b>Пример кода (server.js):</b>
<pre>
const http = require('http');

const server = http.createServer((req, res) => {
    res.writeHead(200, {'Content-Type': 'text/plain'});
    res.end('Hello World! 🚀');
});

server.listen(3000, () => {
    console.log('Сервер запущен на порту 3000!');
});
</pre>

⚡️ Запусти: <pre>node server.js</pre>

✨ <b>ВПЕРЕД К СЕРВЕРАМ!</b>""",
            2: """🔥 <b>ДЕНЬ 2: МОДУЛИ И NPM!</b> 📦

🎯 <b>ЗАДАНИЕ:</b>
• Инициализируй npm проект
• Установи через npm библиотеку express
• Создай простой роут

💻 <b>Пример кода:</b>
<pre>
// Инициализация проекта: npm init -y
// Установка express: npm install express

const express = require('express');
const app = express();

app.get('/', (req, res) => {
    res.send('Привет от Express! 🎉');
});

app.listen(3000, () => {
    console.log('Сервер Express запущен на порту 3000!');
});
</pre>

🎯 <b>КОДИ СЕРВЕРА!</b>""",
            3: """⚡️ <b>ДЕНЬ 3: EXPRESS.JS - ТВОЙ ФРЕЙМВОРК!</b> 🛠️

🎯 <b>ЗАДАНИЕ:</b>
• Настрой базовое Express приложение
• Создай несколько GET роутов
• Добавь простой HTML шаблон

💻 <b>Пример кода:</b>
<pre>
const express = require('express');
const app = express();

app.get('/', (req, res) => {
    res.send('<h1>Главная страница</h1>');
});

app.get('/about', (req, res) => {
    res.send('<h1>О нас</h1>');
});

app.get('/contact', (req, res) => {
    res.send('<h1>Контакты</h1>');
});

app.listen(3000, () => {
    console.log('Express сервер запущен!');
});
</pre>

💥 <b>СЕРВЕРА ЖДУТ!</b>""",
            4: """💫 <b>ДЕНЬ 4: MIDDLEWARE И POST ЗАПРОСЫ!</b> 📨

🎯 <b>ЗАДАНИЕ:</b>
• Добавь middleware для логирования
• Создай форму и обрабатывай POST запросы
• Научись работать с body-parser

💻 <b>Пример кода:</b>
<pre>
const express = require('express');
const app = express();

// Middleware для парсинга JSON
app.use(express.json());

// Middleware для логирования
app.use((req, res, next) => {
    console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
    next();
});

// Обработка POST запросов
app.post('/api/users', (req, res) => {
    const user = req.body;
    console.log('Получен пользователь:', user);
    res.json({message: 'Пользователь успешно создан!', user});
});

app.listen(3000, () => {
    console.log('Сервер с middleware запущен!');
});
</pre>

🚀 <b>ДАЛЬШЕ В БЭКЕНД!</b>""",
            5: """🎯 <b>ДЕНЬ 5: БАЗЫ ДАННЫХ!</b> 🗄️

🎯 <b>ЗАДАНИЕ:</b>
• Подключи MongoDB или SQLite
• Создай простую модель
• Реализуй CRUD операции

💻 <b>Пример с MongoDB:</b>
<pre>
const { MongoClient } = require('mongodb');

// Подключение к MongoDB
async function main() {
    const uri = "mongodb://localhost:27017";
    const client = new MongoClient(uri);
    
    try {
        await client.connect();
        const database = client.db('testdb');
        const users = database.collection('users');
        
        // Создание документа
        const result = await users.insertOne({
            name: "Иван",
            email: "ivan@example.com"
        });
        
        console.log(`Документ создан: ${result.insertedId}`);
    } finally {
        await client.close();
    }
}

main().catch(console.error);
</pre>

⚡️ <b>БД ТЕБЯ ЖДУТ!</b>""",
            6: """🚀 <b>ДЕНЬ 6: API И АУТЕНТИФИКАЦИЯ!</b> 🔐

🎯 <b>ЗАДАНИЕ:</b>
• Создай REST API
• Добавь JWT аутентификацию
• Сделай защищенные роуты

💻 <b>Пример:</b>
<pre>
const express = require('express');
const jwt = require('jsonwebtoken');
const app = express();
app.use(express.json());

const SECRET_KEY = 'your_secret_key';

// Моковая база пользователей
let users = [];

// Регистрация
app.post('/api/register', (req, res) => {
    const { username, password } = req.body;
    users.push({ username, password });
    res.json({ message: 'Пользователь создан!' });
});

// Логин и получение токена
app.post('/api/login', (req, res) => {
    const { username, password } = req.body;
    const user = users.find(u => u.username === username && u.password === password);
    
    if (user) {
        const token = jwt.sign({ username }, SECRET_KEY, { expiresIn: '1h' });
        res.json({ token });
    } else {
        res.status(401).json({ message: 'Неверные данные' });
    }
});

app.listen(3000, () => {
    console.log('API сервер запущен!');
});
</pre>

💥 <b>СТАНЬ ФУЛЛСТЕК!</b>""",
            7: """🎉 <b>ДЕНЬ 7: ДЕПЛОЙ И ФИНАЛ!</b> ☁️

🎯 <b>ЗАДАНИЕ:</b>
• Задеплой приложение на Railway/Heroku
• Настрой домен и SSL
• Протестируй все endpoints

🚀 <b>Инструкция по деплою на Railway:</b>
1️⃣ Создай аккаунт на railway.app
2️⃣ Нажми "New Project" → "Deploy from GitHub repo"
3️⃣ Подключи свой GitHub репозиторий
4️⃣ Настрой переменные окружения (например, PORT=3000)
5️⃣ Нажми "Deploy" и жди завершения

💻 <b>package.json для деплоя:</b>
<pre>
{
  "name": "my-node-app",
  "version": "1.0.0",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js"
  },
  "dependencies": {
    "express": "^4.18.2"
  }
}
</pre>

🔥 <b>ПОЗДРАВЛЯЕМ!</b> Ты стал Node.js разработчиком!"""
        }
    },
    "python_30": {
        "name": "🐍 Python за 1 месяц",
        "description": "Полный базовый курс Python",
        "days": {
            1: """📊 <b>НЕДЕЛЯ 1: ОСНОВЫ PYTHON</b> 🐍

🎯 <b>Темы:</b>
• Переменные и типы данных
• Условные операторы (if/else)
• Циклы (for/while)
• Функции и их параметры
• Списки, словари, кортежи и множества

💻 <b>Проект: Консольный калькулятор</b>

⚡️ <b>ЗАДАНИЕ:</b>
Создай калькулятор, который может:
✓ Складывать, вычитать, умножать, делить
✓ Работать с дробными числами
✓ Обрабатывать ошибки ввода (деление на ноль, некорректные символы)

💡 <b>Подсказка:</b> Используй try/except для обработки ошибок и цикл while для многократного использования.

<pre>
# Пример каркаса калькулятора
def calculator():
    while True:
        try:
            num1 = float(input("Введите первое число: "))
            operation = input("Выберите операцию (+, -, *, /): ")
            num2 = float(input("Введите второе число: "))
            
            if operation == '+':
                result = num1 + num2
            elif operation == '-':
                result = num1 - num2
            # Добавь остальные операции...
            
            print(f"Результат: {result}")
        except ValueError:
            print("Ошибка: введите корректное число!")
        except ZeroDivisionError:
            print("Ошибка: деление на ноль!")
            
        if input("Продолжить? (y/n): ").lower() != 'y':
            break
</pre>

🔥 Не откладывай! Начни кодить прямо сейчас!""",
            2: """🔥 <b>НЕДЕЛЯ 2: ООП И МОДУЛИ</b> 💻

🎯 <b>Темы:</b>
• Классы и объекты
• Наследование и полиморфизм
• Инкапсуляция и абстракция
• Импорт модулей и создание своих
• Виртуальное окружение

💻 <b>Проект: Текстовая RPG игра</b>

⚡️ <b>ЗАДАНИЕ:</b>
Создай простую RPG игру с:
✓ Базовым классом Character и наследниками (Warrior, Mage)
✓ Системой характеристик (здоровье, атака, защита)
✓ Простым боем с противником (Enemy)
✓ Инвентарем для хранения предметов
✓ Возможностью сохранения прогресса в файл

💡 <b>Подсказка:</b> Используй модуль random для генерации характеристик и урона.

<pre>
# Пример класса персонажа
import random

class Character:
    def __init__(self, name, health, attack, defense):
        self.name = name
        self.health = health
        self.attack = attack
        self.defense = defense
    
    def take_damage(self, damage):
        actual_damage = max(0, damage - self.defense)
        self.health -= actual_damage
        return actual_damage
    
    def is_alive(self):
        return self.health > 0

class Warrior(Character):
    def __init__(self, name):
        super().__init__(name, 
                        health=100, 
                        attack=15,
                        defense=10)
    
    def special_attack(self):
        return self.attack * 1.5
</pre>

🎯 Продолжай в том же духе!""",
            3: """⚡️ <b>НЕДЕЛЯ 3: РАБОТА С ДАННЫМИ</b> 📊

🎯 <b>Темы:</b>
• Работа с файлами (txt, json, csv)
• SQLite базы данных
• HTTP запросы к API
• Парсинг веб-страниц
• Обработка и визуализация данных

💻 <b>Проект: Парсер новостей</b>

⚡️ <b>ЗАДАНИЕ:</b>
Напиши парсер, который:
✓ Собирает заголовки новостей с сайта
✓ Сохраняет их в базу данных SQLite
✓ Позволяет искать новости по ключевым словам
✓ Экспортирует результаты в JSON файл
✓ Отображает статистику по новостям

💡 <b>Подсказка:</b> Используй библиотеки requests, beautifulsoup4 и sqlite3.

<pre>
# Установи зависимости: pip install requests beautifulsoup4

import requests
from bs4 import BeautifulSoup
import sqlite3
import json
from datetime import datetime

# Подключение к базе данных
conn = sqlite3.connect('news.db')
cursor = conn.cursor()

# Создание таблицы
cursor.execute('''
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        url TEXT,
        date TEXT
    )
''')

# Парсинг новостей
def parse_news():
    url = "https://news.ycombinator.com"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    for item in soup.select('.titleline'):
        title = item.text
        link = item.find('a')['href']
        
        cursor.execute(
            "INSERT INTO articles (title, url, date) VALUES (?, ?, ?)",
            (title, link, datetime.now().strftime('%Y-%m-%d'))
        )
    
    conn.commit()
    print("Новости успешно сохранены!")
</pre>

💥 Не сдавайся! Ты на правильном пути!""",
            4: """💫 <b>НЕДЕЛЯ 4: ВЕБ-РАЗРАБОТКА</b> 🌐

🎯 <b>Темы:</b>
• Фреймворк Flask
• Шаблоны Jinja2
• Формы и валидация
• Базы данных с SQLAlchemy
• Деплой приложения

💻 <b>Проект: Веб-приложение блог</b>

⚡️ <b>ЗАДАНИЕ:</b>
Создай блог на Flask с:
✓ Регистрацией и авторизацией пользователей
✓ Созданием, редактированием и удалением постов
✓ Комментариями к постам
✓ Админ-панелью для управления контентом
✓ Деплоем на бесплатной платформе

💡 <b>Подсказка:</b> Используй Flask-Login для аутентификации и Flask-WTF для форм.

<pre>
# Установи зависимости: pip install flask flask-sqlalchemy flask-login flask-wtf

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SECRET_KEY'] = 'your-secret-key'
db = SQLAlchemy(app)

# Модель для постов
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@app.route('/')
def home():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('home.html', posts=posts)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
</pre>

🚀 Отличная работа! Готов к следующему уровню!"""
        }
    }
}

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Клавиатуры
def get_main_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🐍 Python курсы", callback_data="python_courses"),
        InlineKeyboardButton("💚 Node.js курсы", callback_data="nodejs_courses")
    )
    keyboard.row(
        InlineKeyboardButton("👨‍💻 Разработчик", url="https://t.me/haker_one"),
        InlineKeyboardButton("🛠️ Техподдержка", url="https://t.me/dark_heavens_support_bot")
    )
    keyboard.add(
        InlineKeyboardButton("🎯 Мой прогресс", callback_data="my_progress"),
        InlineKeyboardButton("🚀 Сегодняшнее задание", callback_data="todays_task")
    )
    keyboard.add(
        InlineKeyboardButton("📊 Статистика", callback_data="stats"),
        InlineKeyboardButton("ℹ️ О боте", callback_data="about")
    )
    return keyboard

def get_python_courses_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("⚡ Python за 7 дней", callback_data="start_python_7"),
        InlineKeyboardButton("🔥 Python за 1 месяц", callback_data="start_python_30"),
        InlineKeyboardButton("🏆 Python за 6 месяцев", callback_data="start_python_180"),
        InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
    )
    return keyboard

def get_nodejs_courses_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("⚡ Node.js за 7 дней", callback_data="start_nodejs_7"),
        InlineKeyboardButton("🔥 Node.js за 1 месяц", callback_data="start_nodejs_30"),
        InlineKeyboardButton("🏆 Node.js за 6 месяцев", callback_data="start_nodejs_180"),
        InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
    )
    return keyboard

def get_day_navigation_keyboard(user_id: int, course_type: str) -> InlineKeyboardMarkup:
    user = user_data.get(user_id, {})
    current_day = user.get('current_day', 1)
    total_days = len(learning_plans.get(course_type, {}).get('days', {}))

    keyboard = InlineKeyboardMarkup(row_width=2)
    row_buttons = []

    if current_day > 1:
        row_buttons.append(InlineKeyboardButton("⬅️ Предыдущий день", callback_data=f"prev_day_{course_type}"))
    if current_day < total_days:
        row_buttons.append(InlineKeyboardButton("➡️ Следующий день", callback_data=f"next_day_{course_type}"))
    if current_day == total_days:
        row_buttons.append(InlineKeyboardButton("🎉 Завершить курс!", callback_data="finish_course"))
    
    keyboard.row(*row_buttons)
    keyboard.add(InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main"))
    return keyboard

# Обработчики сообщений
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name or "Аноним"
    
    if user_id not in user_data:
        user_data[user_id] = {
            'username': username,
            'current_course': None,
            'current_day': 1,
            'start_date': datetime.now().strftime("%Y-%m-%d"),
            'completed_days': [],
            'total_tasks_completed': 0,
            'joined_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        logger.info(f"Новый пользователь: {username} (ID: {user_id})")
    
    welcome_text = f"""
👋 <b>ДОБРО ПОЖАЛОВАТЬ В DH LEARNING, {username}!</b> 🚀

<i>Твоя персональная платформа для освоения программирования</i>

🔥 <b>ЧТО МЫ ПРЕДЛАГАЕМ:</b>
✓ Структурированные курсы от новичка до профи
✓ Ежедневные практические задания
✓ Персональный прогресс и статистика
✓ Постоянная поддержка и мотивация

🎯 <b>ЧТО ТЕБЕ НУЖНО СДЕЛАТЬ:</b>
1. Выбери интересующий курс
2. Выполняй задание каждый день
3. Отслеживай свой прогресс
4. Стань востребованным разработчиком!

<b>Готов начать путь к новой профессии?</b> 👇
"""
    
    await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode="HTML")

@dp.message_handler(commands=['today'])
async def send_todays_task(message: types.Message):
    user_id = message.from_user.id
    user = user_data.get(user_id, {})
    
    if not user.get('current_course'):
        await message.answer("❗️ <b>Сначала выбери курс в главном меню!</b>", parse_mode="HTML")
        return
    
    course_type = user['current_course']
    current_day = user['current_day']
    
    if course_type in learning_plans and current_day in learning_plans[course_type]['days']:
        task = learning_plans[course_type]['days'][current_day]
        course_name = learning_plans[course_type]['name']
        total_days = len(learning_plans[course_type]['days'])
        
        response_text = f"""
📖 <b>{course_name}</b>
📅 <b>День {current_day}</b> из {total_days}

{task}
"""
        
        await message.answer(response_text, reply_markup=get_day_navigation_keyboard(user_id, course_type), parse_mode="HTML")
    else:
        await message.answer("🎉 <b>Поздравляем!</b> Ты завершил все задания курса! 🏆", parse_mode="HTML")

@dp.message_handler(commands=['progress'])
async def send_progress(message: types.Message):
    user_id = message.from_user.id
    user = user_data.get(user_id, {})
    
    if not user.get('current_course'):
        await message.answer("❗️ <b>Ты еще не начал ни одного курса!</b>\n\nВыбери курс в главном меню, чтобы начать обучение.", parse_mode="HTML")
        return
    
    course_type = user['current_course']
    current_day = user.get('current_day', 1)
    completed_days = user.get('completed_days', [])
    total_days = len(learning_plans.get(course_type, {}).get('days', {}))
    
    progress = len(completed_days) + 1  # Включая текущий день
    percentage = (progress / total_days) * 100 if total_days > 0 else 0
    
    # Создаем прогресс-бар
    filled_blocks = int(percentage / 10)
    empty_blocks = 10 - filled_blocks
    progress_bar = "█" * filled_blocks + "░" * empty_blocks
    
    course_name = learning_plans.get(course_type, {}).get('name', 'курс')
    
    progress_text = f"""
📊 <b>ТВОЙ ПРОГРЕСС В КУРСЕ</b>
🎓 <b>{course_name}</b>

<b>Прогресс:</b> [{progress_bar}] {percentage:.1f}%

✓ <b>Завершено дней:</b> {len(completed_days)} из {total_days-1}
🚀 <b>Текущий день:</b> {current_day}
⭐ <b>Выполнено заданий:</b> {user.get('total_tasks_completed', 0)}
📅 <b>Начал обучение:</b> {user.get('start_date', 'Неизвестно')}

💪 <i>Продолжай в том же духе! Каждый день приближает тебя к цели!</i>
"""
    
    await message.answer(progress_text, parse_mode="HTML")

@dp.message_handler(commands=['stats'])
async def send_stats(message: types.Message):
    user_id = message.from_user.id
    
    total_users = len(user_data)
    active_users = len([u for u in user_data.values() if u.get('current_course')])
    
    # Статистика по курсам
    courses_stats = {}
    for user in user_data.values():
        course = user.get('current_course')
        if course:
            courses_stats[course] = courses_stats.get(course, 0) + 1
    
    if user_id == ADMIN_ID:
        # Детальная статистика для админа
        stats_text = f"""
📊 <b>ДЕТАЛЬНАЯ СТАТИСТИКА БОТА</b>

👥 <b>Пользователи:</b>
• Всего: {total_users}
• Активных учеников: {active_users}

📈 <b>Популярность курсов:</b>
"""
        for course, count in courses_stats.items():
            course_name = learning_plans.get(course, {}).get('name', course)
            stats_text += f"• {course_name}: {count} чел.\n"
        
        stats_text += f"""
⏰ <b>Время работы:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}
🤖 <b>Версия:</b> 2.0
"""
    else:
        # Стандартная статистика для пользователей
        stats_text = f"""
📊 <b>СТАТИСТИКА СООБЩЕСТВА</b>

👥 <b>Всего учеников:</b> {total_users}
🔥 <b>Активных учеников:</b> {active_users}

🏆 <b>Топ-3 курса:</b>
1. Python за 7 дней
2. Node.js за 7 дней
3. Python за 1 месяц

🌟 <i>Ты часть сообщества из {total_users} разработчиков, которые меняют свою жизнь!</i>
"""
    
    await message.answer(stats_text, parse_mode="HTML")

# Обработчики callback-запросов
@dp.callback_query_handler(lambda c: c.data == 'python_courses')
async def python_courses(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(
        callback_query.from_user.id,
        "🐍 <b>ВЫБЕРИ СВОЙ PYTHON КУРС</b> 🐍\n\n"
        "<b>⚡ Python за 7 дней</b>\n"
        "Экспресс-курс для быстрого старта\n\n"
        "<b>🔥 Python за 1 месяц</b>\n"
        "Полный базовый курс с проектами\n\n"
        "<b>🏆 Python за 6 месяцев</b>\n"
        "Профессиональная подготовка (скоро)",
        reply_markup=get_python_courses_keyboard(),
        parse_mode="HTML"
    )

@dp.callback_query_handler(lambda c: c.data == 'nodejs_courses')
async def nodejs_courses(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(
        callback_query.from_user.id,
        "💚 <b>ВЫБЕРИ СВОЙ NODE.JS КУРС</b> 💚\n\n"
        "<b>⚡ Node.js за 7 дней</b>\n"
        "Экспресс-курс для быстрого старта\n\n"
        "<b>🔥 Node.js за 1 месяц</b>\n"
        "Полный базовый курс с проектами\n\n"
        "<b>🏆 Node.js за 6 месяцев</b>\n"
        "Профессиональная подготовка (скоро)",
        reply_markup=get_nodejs_courses_keyboard(),
        parse_mode="HTML"
    )

@dp.callback_query_handler(lambda c: c.data.startswith('start_'))
async def start_course(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user_id = callback_query.from_user.id
    course_type = callback_query.data.replace('start_', '')
    
    # Проверка существования курса
    if course_type not in learning_plans:
        await bot.send_message(
            user_id, 
            "❗️ <b>Выбранный курс временно недоступен.</b>\n\n"
            "Попробуй выбрать другой курс из списка.", 
            parse_mode="HTML"
        )
        return
    
    user_data[user_id]['current_course'] = course_type
    user_data[user_id]['current_day'] = 1
    user_data[user_id]['start_date'] = datetime.now().strftime("%Y-%m-%d")
    user_data[user_id]['completed_days'] = []
    
    course_name = learning_plans.get(course_type, {}).get('name', 'курс')
    course_description = learning_plans.get(course_type, {}).get('description', '')
    total_days = len(learning_plans[course_type]['days'])
    
    welcome_text = f"""
🎉 <b>ПОЗДРАВЛЯЕМ! ТЫ НАЧАЛ КУРС:</b> {course_name}

📖 <b>Описание:</b> {course_description}
📅 <b>Продолжительность:</b> {total_days} дней

🔥 <b>ПРАВИЛА УСПЕХА:</b>
✓ Выполняй задание каждый день
✓ Не пропускай дни без уважительной причины
✓ Экспериментируй с кодом из примеров
✓ Не бойся делать ошибки - это часть обучения

🚀 <b>ГОТОВ НАЧАТЬ? ПЕРВОЕ ЗАДАНИЕ ЖДЕТ!</b>
"""
    
    await bot.send_message(user_id, welcome_text, parse_mode="HTML")
    
    first_task = learning_plans[course_type]['days'][1]
    
    task_text = f"""
📚 <b>{course_name}</b>
📅 <b>День 1</b> из {total_days}

{first_task}
"""
    
    await bot.send_message(
        user_id, 
        task_text, 
        reply_markup=get_day_navigation_keyboard(user_id, course_type),
        parse_mode="HTML"
    )

@dp.callback_query_handler(lambda c: c.data.startswith('next_day_'))
async def next_day(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user_id = callback_query.from_user.id
    course_type = callback_query.data.replace('next_day_', '')
    
    user = user_data.get(user_id, {})
    current_day = user.get('current_day', 1)
    total_days = len(learning_plans.get(course_type, {}).get('days', {}))
    
    if current_day < total_days:
        # Обновляем прогресс пользователя
        user_data[user_id]['current_day'] = current_day + 1
        if current_day not in user.get('completed_days', []):
            user_data[user_id]['completed_days'] = user.get('completed_days', []) + [current_day]
        user_data[user_id]['total_tasks_completed'] = user.get('total_tasks_completed', 0) + 1
        
        next_task = learning_plans[course_type]['days'][current_day + 1]
        course_name = learning_plans[course_type]['name']
        
        # Случайное мотивационное сообщение
        motivation_texts = [
            "🔥 Отличная работа! Продолжай в том же духе!",
            "🚀 Ты на пути к великим свершениям!",
            "🎯 Поздравляю с завершением дня! Впереди еще больше интересного!",
            "✨ Твой прогресс впечатляет! Не останавливайся!",
            "💪 С каждым днем ты становишься сильнее в программировании!"
        ]
        
        motivation = random.choice(motivation_texts)
        
        task_text = f"""
{motivation}

📚 <b>{course_name}</b>
📅 <b>День {current_day + 1}</b> из {total_days}

{next_task}
"""
        
        await bot.send_message(
            user_id, 
            task_text,
            reply_markup=get_day_navigation_keyboard(user_id, course_type),
            parse_mode="HTML"
        )
    else:
        await bot.send_message(
            user_id, 
            "🎉 <b>Ты уже достиг конца курса!</b>\n\n"
            "Используй кнопку 'Завершить курс', чтобы получить сертификат и рекомендации.",
            parse_mode="HTML"
        )

@dp.callback_query_handler(lambda c: c.data.startswith('prev_day_'))
async def prev_day(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user_id = callback_query.from_user.id
    course_type = callback_query.data.replace('prev_day_', '')
    
    user = user_data.get(user_id, {})
    current_day = user.get('current_day', 1)
    
    if current_day > 1:
        user_data[user_id]['current_day'] = current_day - 1
        prev_task = learning_plans[course_type]['days'][current_day - 1]
        course_name = learning_plans[course_type]['name']
        total_days = len(learning_plans[course_type]['days'])
        
        task_text = f"""
🔄 <b>ПОВТОРЕНИЕ МАТЕРИАЛА</b> 🔄

📚 <b>{course_name}</b>
📅 <b>День {current_day - 1}</b> из {total_days}

{prev_task}
"""
        
        await bot.send_message(
            user_id, 
            task_text,
            reply_markup=get_day_navigation_keyboard(user_id, course_type),
            parse_mode="HTML"
        )
    else:
        await bot.send_message(user_id, "❗️ <b>Это первый день курса. Нельзя вернуться назад.</b>", parse_mode="HTML")

@dp.callback_query_handler(lambda c: c.data == 'todays_task')
async def todays_task(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user_id = callback_query.from_user.id
    user = user_data.get(user_id, {})
    
    if not user.get('current_course'):
        await bot.send_message(user_id, "❗️ <b>Сначала выбери курс в главном меню!</b>", parse_mode="HTML")
        return
    
    course_type = user['current_course']
    current_day = user['current_day']
    
    if course_type in learning_plans and current_day in learning_plans[course_type]['days']:
        task = learning_plans[course_type]['days'][current_day]
        course_name = learning_plans[course_type]['name']
        total_days = len(learning_plans[course_type]['days'])
        
        response_text = f"""
📖 <b>{course_name}</b>
📅 <b>День {current_day}</b> из {total_days}

{task}
"""
        
        await bot.send_message(user_id, response_text, reply_markup=get_day_navigation_keyboard(user_id, course_type), parse_mode="HTML")
    else:
        await bot.send_message(user_id, "🎉 <b>Поздравляем!</b> Ты завершил все задания курса! 🏆", parse_mode="HTML")

@dp.callback_query_handler(lambda c: c.data == 'my_progress')
async def my_progress(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user_id = callback_query.from_user.id
    user = user_data.get(user_id, {})
    
    if not user.get('current_course'):
        await bot.send_message(user_id, "❗️ <b>Ты еще не начал ни одного курса!</b>\n\nВыбери курс в главном меню, чтобы начать обучение.", parse_mode="HTML")
        return
    
    course_type = user['current_course']
    current_day = user.get('current_day', 1)
    completed_days = user.get('completed_days', [])
    total_days = len(learning_plans.get(course_type, {}).get('days', {}))
    
    progress = len(completed_days) + 1  # Включая текущий день
    percentage = (progress / total_days) * 100 if total_days > 0 else 0
    
    # Создаем прогресс-бар
    filled_blocks = int(percentage / 10)
    empty_blocks = 10 - filled_blocks
    progress_bar = "█" * filled_blocks + "░" * empty_blocks
    
    course_name = learning_plans.get(course_type, {}).get('name', 'курс')
    
    progress_text = f"""
📊 <b>ТВОЙ ПРОГРЕСС В КУРСЕ</b>
🎓 <b>{course_name}</b>

<b>Прогресс:</b> [{progress_bar}] {percentage:.1f}%

✓ <b>Завершено дней:</b> {len(completed_days)} из {total_days-1}
🚀 <b>Текущий день:</b> {current_day}
⭐ <b>Выполнено заданий:</b> {user.get('total_tasks_completed', 0)}
📅 <b>Начал обучение:</b> {user.get('start_date', 'Неизвестно')}

💪 <i>Продолжай в том же духе! Каждый день приближает тебя к цели!</i>
"""
    
    await bot.send_message(user_id, progress_text, parse_mode="HTML")

@dp.callback_query_handler(lambda c: c.data == 'stats')
async def stats_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user_id = callback_query.from_user.id
    
    total_users = len(user_data)
    active_users = len([u for u in user_data.values() if u.get('current_course')])
    
    # Статистика по курсам
    courses_stats = {}
    for user in user_data.values():
        course = user.get('current_course')
        if course:
            courses_stats[course] = courses_stats.get(course, 0) + 1
    
    if user_id == ADMIN_ID:
        # Детальная статистика для админа
        stats_text = f"""
📊 <b>ДЕТАЛЬНАЯ СТАТИСТИКА БОТА</b>

👥 <b>Пользователи:</b>
• Всего: {total_users}
• Активных учеников: {active_users}

📈 <b>Популярность курсов:</b>
"""
        for course, count in courses_stats.items():
            course_name = learning_plans.get(course, {}).get('name', course)
            stats_text += f"• {course_name}: {count} чел.\n"
        
        stats_text += f"""
⏰ <b>Время работы:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}
🤖 <b>Версия:</b> 2.0
"""
    else:
        # Стандартная статистика для пользователей
        stats_text = f"""
📊 <b>СТАТИСТИКА СООБЩЕСТВА</b>

👥 <b>Всего учеников:</b> {total_users}
🔥 <b>Активных учеников:</b> {active_users}

🏆 <b>Топ-3 курса:</b>
1. Python за 7 дней
2. Node.js за 7 дней
3. Python за 1 месяц

🌟 <i>Ты часть сообщества из {total_users} разработчиков, которые меняют свою жизнь!</i>
"""
    
    await bot.send_message(user_id, stats_text, parse_mode="HTML")

@dp.callback_query_handler(lambda c: c.data == 'about')
async def about_bot(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    about_text = f"""
🤖 <b>DH LEARNING BOT</b>

✨ <b>Версия:</b> 2.0
👨‍💻 <b>Создатель:</b> @haker_one
🛠️ <b>Техподдержка:</b> @dark_heavens_support_bot

📚 <b>ДОСТУПНЫЕ КУРСЫ:</b>
• Python за 7 дней
• Python за 1 месяц  
• Node.js за 7 дней
• Node.js за 1 месяц

💡 <b>ВОЗМОЖНОСТИ:</b>
✓ Ежедневные задания с примерами кода
✓ Персональный отслеживание прогресса
✓ Система достижений и мотивации
✓ Автоматические напоминания
✓ Доступ к сообществу разработчиков

🚀 <b>НАША МИССИЯ:</b>
Помочь каждому желающему освоить программирование и изменить свою жизнь к лучшему!

💬 <i>Если у вас есть предложения или проблемы - обращайтесь в техподдержку.</i>
"""
    await bot.send_message(callback_query.from_user.id, about_text, parse_mode="HTML")

@dp.callback_query_handler(lambda c: c.data == 'finish_course')
async def finish_course(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user_id = callback_query.from_user.id
    user = user_data.get(user_id, {})
    
    course_type = user.get('current_course')
    if not course_type or course_type not in learning_plans:
        await bot.send_message(user_id, "❗️ <b>Ошибка завершения курса.</b>\n\nНачните курс заново.", parse_mode="HTML")
        return
    
    course_name = learning_plans.get(course_type, {}).get('name', 'курс')
    total_days = len(learning_plans.get(course_type, {}).get('days', {}))
    completed_days = len(user.get('completed_days', []))
    total_tasks = user.get('total_tasks_completed', 0)
    start_date = user.get('start_date', 'Неизвестно')
    
    completion_text = f"""
🎉 <b>ПОЗДРАВЛЯЕМ С ЗАВЕРШЕНИЕМ КУРСА!</b> 🏆

🎓 <b>Курс:</b> {course_name}
📅 <b>Период обучения:</b> {start_date} - {datetime.now().strftime('%Y-%m-%d')}
📊 <b>Результаты:</b>
✓ Завершено дней: {completed_days} из {total_days-1}
⭐ Выполнено заданий: {total_tasks}
⏱️ Среднее время на задание: ~1-2 часа

🔥 <b>ЧТО ДАЛЬШЕ?</b>
1️⃣ <b>Практика:</b> Создай 2-3 своих проекта на основе полученных знаний
2️⃣ <b>Глубже:</b> Выбери следующий, более сложный курс
3️⃣ <b>Сообщество:</b> Присоединяйся к нашему чату разработчиков
4️⃣ <b>Работа:</b> Начни искать свою первую позицию в IT

💼 <i>Помни: знания без практики бесполезны. Примени их в реальных проектах!</i>

🏆 <b>Ты стал на шаг ближе к профессии мечты!</b>
"""
    
    # Сбрасываем текущий курс пользователя
    user_data[user_id]['current_course'] = None
    
    await bot.send_message(user_id, completion_text, reply_markup=get_main_keyboard(), parse_mode="HTML")

@dp.callback_query_handler(lambda c: c.data == 'back_to_main')
async def back_to_main(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user_id = callback_query.from_user.id
    username = callback_query.from_user.username or callback_query.from_user.first_name or "Аноним"
    
    if user_id not in user_data:
        user_data[user_id] = {
            'username': username,
            'current_course': None,
            'current_day': 1,
            'start_date': datetime.now().strftime("%Y-%m-%d"),
            'completed_days': [],
            'total_tasks_completed': 0,
            'joined_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    welcome_text = f"""
👋 <b>ДОБРО ПОЖАЛОВАТЬ В DH LEARNING, {username}!</b> 🚀

<i>Твоя персональная платформа для освоения программирования</i>

🔥 <b>ЧТО МЫ ПРЕДЛАГАЕМ:</b>
✓ Структурированные курсы от новичка до профи
✓ Ежедневные практические задания
✓ Персональный прогресс и статистика
✓ Постоянная поддержка и мотивация

🎯 <b>ЧТО ТЕБЕ НУЖНО СДЕЛАТЬ:</b>
1. Выбери интересующий курс
2. Выполняй задание каждый день
3. Отслеживай свой прогресс
4. Стань востребованным разработчиком!

<b>Готов начать путь к новой профессии?</b> 👇
"""
    
    await bot.send_message(user_id, welcome_text, reply_markup=get_main_keyboard(), parse_mode="HTML")

# Функция для отправки ежедневных напоминаний
async def send_daily_reminders():
    while True:
        try:
            # Московское время (UTC+3)
            moscow_tz = pytz.timezone('Europe/Moscow')
            moscow_time = datetime.now(moscow_tz)
            
            # Отправляем утренние напоминания в 9:00 по Москве
            if moscow_time.hour == 9 and moscow_time.minute == 0:
                reminder_count = 0
                for user_id, user_data_item in list(user_data.items()):
                    if user_data_item.get('current_course'):
                        try:
                            course_name = learning_plans.get(user_data_item['current_course'], {}).get('name', 'курс')
                            current_day = user_data_item.get('current_day', 1)
                            total_days = len(learning_plans.get(user_data_item['current_course'], {}).get('days', {}))
                            
                            reminder_text = f"""
🌅 <b>ДОБРОЕ УТРО, РАЗРАБОТЧИК!</b> ☕

📅 <b>Сегодня:</b> День {current_day} в курсе {course_name}

🎯 <b>ТВОЕ ЗАДАНИЕ НА СЕГОДНЯ:</b>
• Выполни задание дня {current_day}
• Потрать на это минимум 1 час
• Не откладывай на вечер!

💡 <i>Помни: регулярность важнее интенсивности. Лучше 1 час каждый день, чем 7 часов раз в неделю.</i>

🚀 <b>ПОКАЖИ, НА ЧТО ТЫ СПОСОБЕН!</b>
"""
                            
                            await bot.send_message(user_id, reminder_text, parse_mode="HTML")
                            reminder_count += 1
                            await asyncio.sleep(0.5)  # Задержка для избежания лимитов Telegram
                        except Exception as e:
                            logger.error(f"Не удалось отправить напоминание пользователю {user_id}: {e}")
                
                logger.info(f"Отправлено утренних напоминаний: {reminder_count}")
                await asyncio.sleep(60)  # Ждем минуту, чтобы не отправлять напоминание повторно
            
            # Отправляем вечерние напоминания в 20:00 по Москве
            elif moscow_time.hour == 20 and moscow_time.minute == 0:
                reminder_count = 0
                for user_id, user_data_item in list(user_data.items()):
                    if user_data_item.get('current_course'):
                        try:
                            course_name = learning_plans.get(user_data_item['current_course'], {}).get('name', 'курс')
                            current_day = user_data_item.get('current_day', 1)
                            
                            # Проверяем, выполнено ли сегодняшнее задание
                            last_completed = user_data_item.get('completed_days', [])[-1] if user_data_item.get('completed_days') else 0
                            
                            if last_completed < current_day:
                                reminder_text = f"""
🌙 <b>ВЕЧЕРНЕЕ НАПОМИНАНИЕ</b> ⭐

📚 <b>Курс:</b> {course_name}
📅 <b>Сегодняшний день:</b> {current_day}

❗️ <b>ТЫ ЕЩЕ НЕ ВЫПОЛНИЛ СЕГОДНЯШНЕЕ ЗАДАНИЕ!</b>

⏰ <b>У тебя еще есть время до конца дня.</b>
💡 Совет: даже 30 минут качественной работы лучше, чем ничего.

🔥 <b>ЗАВТРА НОВЫЙ ДЕНЬ И НОВЫЕ ЗНАНИЯ!</b>
"""
                            else:
                                reminder_text = f"""
🌙 <b>ОТЛИЧНЫЙ ВЕЧЕР, РАЗРАБОТЧИК!</b> 🌟

✅ <b>Поздравляем!</b> Ты выполнил сегодняшнее задание по курсу {course_name}!

📈 <b>Твой прогресс:</b> День {current_day}
🎯 <b>Завтра:</b> Новое интересное задание

💤 <b>Отдохни и наберись сил к новому дню!</b>
<i>Твой мозг обрабатывает новую информацию во сне.</i>

🚀 <b>Продолжай в том же духе!</b>
"""
                            
                            await bot.send_message(user_id, reminder_text, parse_mode="HTML")
                            reminder_count += 1
                            await asyncio.sleep(0.5)
                        except Exception as e:
                            logger.error(f"Не удалось отправить вечернее напоминание пользователю {user_id}: {e}")
                
                logger.info(f"Отправлено вечерних напоминаний: {reminder_count}")
                await asyncio.sleep(60)  # Ждем минуту, чтобы не отправлять напоминание повторно
            
            await asyncio.sleep(30)  # Проверяем каждые 30 секунд
            
        except Exception as e:
            logger.error(f"Ошибка в daily reminders: {e}")
            await asyncio.sleep(60)

# Функция при запуске бота
async def on_startup(dp):
    asyncio.create_task(send_daily_reminders())
    logger.info("🤖 Бот запущен и готов к работе!")
    logger.info("⏰ Ежедневные напоминания активированы!")
    logger.info(f"👥 Загружено пользователей: {len(user_data)}")

if __name__ == '__main__':
    print("🚀 Запускаю DH Learning Bot...")
    print("✅ Все зависимости проверены и установлены")
    print("🤖 Бот запускается с токеном: 8524355119:AAExHf5r0GZQxXiB58S95nOaqdS9DfyfYWI")
    print("👑 Админ ID: 7215210750")
    
    # Запускаем бота 
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
