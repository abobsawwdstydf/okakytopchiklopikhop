import asyncio
import logging
import os
from datetime import datetime
import random

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from aiogram.filters import Command
from aiogram.enums import ParseMode

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Конфигурация бота из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN', '8524355119:AAExHf5r0GZQxXiB58S95nOaqdS9DfyfYWI')
ADMIN_ID = int(os.getenv('ADMIN_ID', '7215210750'))

# Хранилище данных пользователей (в памяти)
user_data = {}

# Планы обучения
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
<code>
name = "Твое_имя"
age = 25
print(f"Привет, меня зовут {name} и мне {age} лет!")
</code>

⚡️ <b>ДЕЛАЙ СЕЙЧАС!</b> Не откладывай!""",
            2: """🔥 <b>ДЕНЬ 2: УСЛОВИЯ И ЛОГИКА!</b> 🧠

🎯 <b>ЗАДАНИЕ:</b>
• Напиши скрипт, который проверяет твой возраст
• Если больше 18 - 'Доступ разрешен', иначе - 'Доступ запрещен'
• Добавь проверку на пустой ввод

💻 <b>Пример кода:</b>
<code>
age_input = input("Сколько тебе лет? ")
if age_input.strip() == "":
    print("Ошибка: пустой ввод!")
else:
    age = int(age_input)
    if age >= 18:
        print("Доступ разрешен! 🎉")
    else:
        print("Доступ запрещен! ⚠️")
</code>

🎯 <b>ВПЕРЕД КОДИТЬ!</b>""",
            3: """⚡️ <b>ДЕНЬ 3: ЦИКЛЫ И СПИСКИ!</b> 🔄

🎯 <b>ЗАДАНИЕ:</b>
• Создай список из 5 чисел
• Напиши цикл, который выводит каждый элемент
• Сделай сумму всех чисел в списке

💻 <b>Пример кода:</b>
<code>
numbers = [1, 2, 3, 4, 5]
total = 0

for num in numbers:
    print(f"Число: {num}")
    total += num

print(f"Сумма: {total}")
</code>

💥 <b>РАБОТАЙ БЕЗ ОСТАНОВКИ!</b>""",
            4: """💫 <b>ДЕНЬ 4: ФУНКЦИИ - ТВОЙ НОВЫЙ СУПЕРСИЛА!</b> 🦸

🎯 <b>ЗАДАНИЕ:</b>
• Создай функцию для расчета площади круга
• Создай функцию для проверки четности числа
• Вызови их с разными параметрами

💻 <b>Пример кода:</b>
<code>
import math

def circle_area(radius):
    return math.pi * radius ** 2

def is_even(number):
    return number % 2 == 0

print(f"Площадь круга: {circle_area(5):.2f}")
print(f"Четное число? {is_even(10)}")
</code>

🚀 <b>КОДИМ ДАЛЬШЕ!</b>""",
            5: """🎯 <b>ДЕНЬ 5: РАБОТА С ФАЙЛАМИ!</b> 📁

🎯 <b>ЗАДАНИЕ:</b>
• Создай текстовый файл
• Запиши в него несколько строк
• Прочитай и выведи содержимое

💻 <b>Пример кода:</b>
<code>
# Запись в файл
with open("дневник.txt", "w", encoding="utf-8") as file:
    file.write("Мой первый файл\\n")
    file.write("Сегодня я изучал Python!\\n")

# Чтение из файла
with open("дневник.txt", "r", encoding="utf-8") as file:
    content = file.read()
    print(content)
</code>

⚡️ <b>НЕ ОСТАНАВЛИВАЙСЯ!</b>""",
            6: """🚀 <b>ДЕНЬ 6: БИБЛИОТЕКИ И API!</b> 🌐

🎯 <b>ЗАДАНИЕ:</b>
• Установи библиотеку requests через pip
• Сделай запрос к какому-нибудь публичному API
• Обработай и выведи результат

💻 <b>Пример кода:</b>
<code>
# Установи requests: pip install requests
import requests

response = requests.get("https://api.github.com")
if response.status_code == 200:
    print(f"Статус: {response.status_code}")
    print(f"Данные: {response.json()}")
else:
    print(f"Ошибка запроса: {response.status_code}")
</code>

💥 <b>ТЫ УЖЕ ПРОГРАММИСТ!</b>""",
            7: """🎉 <b>ДЕНЬ 7: ФИНАЛ! ЗАВЕРШАЮЩИЙ ПРОЕКТ!</b> 🏆

🎯 <b>ЗАДАНИЕ:</b>
Создай простой телеграм бот или парсер сайта!

💻 <b>Пример бота:</b>
<code>
from aiogram import Bot, Dispatcher, types
import asyncio

bot = Bot(token="ТВОЙ_ТОКЕН")
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Привет! Я твой первый бот!")

if __name__ == '__main__':
    asyncio.run(dp.start_polling())
</code>

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
<code>
const http = require('http');

const server = http.createServer((req, res) => {
    res.writeHead(200, {'Content-Type': 'text/plain'});
    res.end('Hello World! 🚀');
});

server.listen(3000, () => {
    console.log('Сервер запущен на порту 3000!');
});
</code>

⚡️ Запусти: <code>node server.js</code>

✨ <b>ВПЕРЕД К СЕРВЕРАМ!</b>"""
        }
    }
}

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Клавиатуры
def get_main_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🐍 Python курсы", callback_data="python_courses"),
            InlineKeyboardButton(text="💚 Node.js курсы", callback_data="nodejs_courses")
        ],
        [
            InlineKeyboardButton(text="🎯 Мой прогресс", callback_data="my_progress"),
            InlineKeyboardButton(text="🚀 Сегодняшнее задание", callback_data="todays_task")
        ],
        [
            InlineKeyboardButton(text="👨‍💻 Разработчик", url="https://t.me/haker_one"),
            InlineKeyboardButton(text="🛠️ Техподдержка", url="https://t.me/dark_heavens_support_bot")
        ]
    ])
    return keyboard

def get_python_courses_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚡ Python за 7 дней", callback_data="start_python_7")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
    ])
    return keyboard

def get_nodejs_courses_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚡ Node.js за 7 дней", callback_data="start_nodejs_7")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
    ])
    return keyboard

def get_day_navigation_keyboard(user_id: int, course_type: str):
    user = user_data.get(user_id, {})
    current_day = user.get('current_day', 1)
    total_days = len(learning_plans.get(course_type, {}).get('days', {}))

    keyboard_buttons = []
    
    if current_day > 1:
        keyboard_buttons.append(InlineKeyboardButton(text="⬅️ Предыдущий день", callback_data=f"prev_day_{course_type}"))
    if current_day < total_days:
        keyboard_buttons.append(InlineKeyboardButton(text="➡️ Следующий день", callback_data=f"next_day_{course_type}"))
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        keyboard_buttons,
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
    ])
    return keyboard

# Обработчики сообщений
@dp.message(Command("start"))
async def send_welcome(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name or "Аноним"
    
    if user_id not in user_data:
        user_data[user_id] = {
            'username': username,
            'current_course': None,
            'current_day': 1,
            'start_date': datetime.now().strftime("%Y-%m-%d"),
            'completed_days': [],
            'total_tasks_completed': 0
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
    
    await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode=ParseMode.HTML)

@dp.message(Command("progress"))
async def send_progress(message: Message):
    user_id = message.from_user.id
    user = user_data.get(user_id, {})
    
    if not user.get('current_course'):
        await message.answer("❗️ <b>Ты еще не начал ни одного курса!</b>\n\nВыбери курс в главном меню, чтобы начать обучение.", parse_mode=ParseMode.HTML)
        return
    
    course_type = user['current_course']
    current_day = user.get('current_day', 1)
    completed_days = user.get('completed_days', [])
    total_days = len(learning_plans.get(course_type, {}).get('days', {}))
    
    progress = len(completed_days)
    percentage = (progress / total_days) * 100 if total_days > 0 else 0
    
    filled_blocks = int(percentage / 10)
    empty_blocks = 10 - filled_blocks
    progress_bar = "█" * filled_blocks + "░" * empty_blocks
    
    course_name = learning_plans.get(course_type, {}).get('name', 'курс')
    
    progress_text = f"""
📊 <b>ТВОЙ ПРОГРЕСС В КУРСЕ</b>
🎓 <b>{course_name}</b>

<b>Прогресс:</b> [{progress_bar}] {percentage:.1f}%

✓ <b>Завершено дней:</b> {len(completed_days)} из {total_days}
🚀 <b>Текущий день:</b> {current_day}
⭐ <b>Выполнено заданий:</b> {user.get('total_tasks_completed', 0)}
📅 <b>Начал обучение:</b> {user.get('start_date', 'Неизвестно')}

💪 <i>Продолжай в том же духе! Каждый день приближает тебя к цели!</i>
"""
    
    await message.answer(progress_text, parse_mode=ParseMode.HTML)

@dp.message(Command("today"))
async def send_todays_task(message: Message):
    user_id = message.from_user.id
    user = user_data.get(user_id, {})
    
    if not user.get('current_course'):
        await message.answer("❗️ <b>Сначала выбери курс в главном меню!</b>", parse_mode=ParseMode.HTML)
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
        
        await message.answer(response_text, reply_markup=get_day_navigation_keyboard(user_id, course_type), parse_mode=ParseMode.HTML)
    else:
        await message.answer("🎉 <b>Поздравляем!</b> Ты завершил все задания курса! 🏆", parse_mode=ParseMode.HTML)

# Обработчики callback-запросов
@dp.callback_query(F.data == "python_courses")
async def python_courses(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "🐍 <b>ВЫБЕРИ СВОЙ PYTHON КУРС</b> 🐍\n\n"
        "<b>⚡ Python за 7 дней</b>\n"
        "Экспресс-курс для быстрого старта",
        reply_markup=get_python_courses_keyboard(),
        parse_mode=ParseMode.HTML
    )

@dp.callback_query(F.data == "nodejs_courses")
async def nodejs_courses(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "💚 <b>ВЫБЕРИ СВОЙ NODE.JS КУРС</b> 💚\n\n"
        "<b>⚡ Node.js за 7 дней</b>\n"
        "Экспресс-курс для быстрого старта",
        reply_markup=get_nodejs_courses_keyboard(),
        parse_mode=ParseMode.HTML
    )

@dp.callback_query(F.data.startswith("start_"))
async def start_course(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    course_type = callback.data.replace('start_', '')
    
    if course_type not in learning_plans:
        await callback.message.answer("❗️ <b>Курс временно недоступен.</b>", parse_mode=ParseMode.HTML)
        return
    
    user_data[user_id]['current_course'] = course_type
    user_data[user_id]['current_day'] = 1
    user_data[user_id]['start_date'] = datetime.now().strftime("%Y-%m-%d")
    
    course_name = learning_plans[course_type]['name']
    course_description = learning_plans[course_type]['description']
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
    
    await callback.message.answer(welcome_text, parse_mode=ParseMode.HTML)
    
    first_task = learning_plans[course_type]['days'][1]
    task_text = f"""
📚 <b>{course_name}</b>
📅 <b>День 1</b> из {total_days}

{first_task}
"""
    
    await callback.message.answer(
        task_text, 
        reply_markup=get_day_navigation_keyboard(user_id, course_type),
        parse_mode=ParseMode.HTML
    )

@dp.callback_query(F.data.startswith("next_day_"))
async def next_day(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    course_type = callback.data.replace('next_day_', '')
    
    user = user_data.get(user_id, {})
    current_day = user.get('current_day', 1)
    total_days = len(learning_plans.get(course_type, {}).get('days', {}))
    
    if current_day < total_days:
        user_data[user_id]['current_day'] = current_day + 1
        if current_day not in user.get('completed_days', []):
            user_data[user_id]['completed_days'] = user.get('completed_days', []) + [current_day]
        user_data[user_id]['total_tasks_completed'] = user.get('total_tasks_completed', 0) + 1
        
        next_task = learning_plans[course_type]['days'][current_day + 1]
        course_name = learning_plans[course_type]['name']
        
        motivation_texts = [
            "🔥 Отличная работа! Продолжай в том же духе!",
            "🚀 Ты на пути к великим свершениям!",
            "🎯 Поздравляю с завершением дня! Впереди еще больше интересного!",
        ]
        
        motivation = random.choice(motivation_texts)
        
        task_text = f"""
{motivation}

📚 <b>{course_name}</b>
📅 <b>День {current_day + 1}</b> из {total_days}

{next_task}
"""
        
        await callback.message.edit_text(
            task_text,
            reply_markup=get_day_navigation_keyboard(user_id, course_type),
            parse_mode=ParseMode.HTML
        )

@dp.callback_query(F.data.startswith("prev_day_"))
async def prev_day(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    course_type = callback.data.replace('prev_day_', '')
    
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
        
        await callback.message.edit_text(
            task_text,
            reply_markup=get_day_navigation_keyboard(user_id, course_type),
            parse_mode=ParseMode.HTML
        )

@dp.callback_query(F.data == "todays_task")
async def todays_task(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    user = user_data.get(user_id, {})
    
    if not user.get('current_course'):
        await callback.message.answer("❗️ <b>Сначала выбери курс в главном меню!</b>", parse_mode=ParseMode.HTML)
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
        
        await callback.message.answer(
            response_text, 
            reply_markup=get_day_navigation_keyboard(user_id, course_type), 
            parse_mode=ParseMode.HTML
        )

@dp.callback_query(F.data == "my_progress")
async def my_progress(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    user = user_data.get(user_id, {})
    
    if not user.get('current_course'):
        await callback.message.answer("❗️ <b>Ты еще не начал ни одного курса!</b>\n\nВыбери курс в главном меню, чтобы начать обучение.", parse_mode=ParseMode.HTML)
        return
    
    course_type = user['current_course']
    current_day = user.get('current_day', 1)
    completed_days = user.get('completed_days', [])
    total_days = len(learning_plans.get(course_type, {}).get('days', {}))
    
    progress = len(completed_days)
    percentage = (progress / total_days) * 100 if total_days > 0 else 0
    
    filled_blocks = int(percentage / 10)
    empty_blocks = 10 - filled_blocks
    progress_bar = "█" * filled_blocks + "░" * empty_blocks
    
    course_name = learning_plans.get(course_type, {}).get('name', 'курс')
    
    progress_text = f"""
📊 <b>ТВОЙ ПРОГРЕСС В КУРСЕ</b>
🎓 <b>{course_name}</b>

<b>Прогресс:</b> [{progress_bar}] {percentage:.1f}%

✓ <b>Завершено дней:</b> {len(completed_days)} из {total_days}
🚀 <b>Текущий день:</b> {current_day}
⭐ <b>Выполнено заданий:</b> {user.get('total_tasks_completed', 0)}
📅 <b>Начал обучение:</b> {user.get('start_date', 'Неизвестно')}

💪 <i>Продолжай в том же духе! Каждый день приближает тебя к цели!</i>
"""
    
    await callback.message.answer(progress_text, parse_mode=ParseMode.HTML)

@dp.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    username = callback.from_user.username or callback.from_user.first_name or "Аноним"
    
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
    
    await callback.message.edit_text(
        welcome_text, 
        reply_markup=get_main_keyboard(), 
        parse_mode=ParseMode.HTML
    )

@dp.message()
async def echo_handler(message: Message):
    """Обработчик всех остальных сообщений"""
    await message.answer("🤖 Используйте команду /start для начала работы с ботом")

async def main():
    print("🚀 Запускаю DH Learning Bot...")
    print(f"✅ Токен бота: {BOT_TOKEN[:10]}...")
    print(f"✅ Admin ID: {ADMIN_ID}")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
