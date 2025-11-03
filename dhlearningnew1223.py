import asyncio
import logging
import os
from datetime import datetime
import random

from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

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
            # ... остальные дни курса (для краткости оставлю 2 дня, остальные аналогично)
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
    keyboard.add(
        InlineKeyboardButton("🎯 Мой прогресс", callback_data="my_progress"),
        InlineKeyboardButton("🚀 Сегодняшнее задание", callback_data="todays_task")
    )
    return keyboard

def get_python_courses_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("⚡ Python за 7 дней", callback_data="start_python_7"),
        InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
    )
    return keyboard

def get_day_navigation_keyboard(user_id: int, course_type: str):
    user = user_data.get(user_id, {})
    current_day = user.get('current_day', 1)
    total_days = len(learning_plans.get(course_type, {}).get('days', {}))

    keyboard = InlineKeyboardMarkup(row_width=2)
    row_buttons = []

    if current_day > 1:
        row_buttons.append(InlineKeyboardButton("⬅️ Предыдущий день", callback_data=f"prev_day_{course_type}"))
    if current_day < total_days:
        row_buttons.append(InlineKeyboardButton("➡️ Следующий день", callback_data=f"next_day_{course_type}"))
    
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
            'total_tasks_completed': 0
        }
    
    welcome_text = f"""
👋 <b>ДОБРО ПОЖАЛОВАТЬ В DH LEARNING, {username}!</b> 🚀

<i>Твоя персональная платформа для освоения программирования</i>

🎯 <b>ДОСТУПНЫЕ КУРСЫ:</b>
• Python за 7 дней
• Node.js за 7 дней

<b>Выбери курс чтобы начать обучение:</b> 👇
"""
    
    await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode="HTML")

@dp.message_handler(commands=['progress'])
async def send_progress(message: types.Message):
    user_id = message.from_user.id
    user = user_data.get(user_id, {})
    
    if not user.get('current_course'):
        await message.answer("❗️ <b>Ты еще не начал ни одного курса!</b>", parse_mode="HTML")
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
📊 <b>ТВОЙ ПРОГРЕСС</b>
🎓 <b>{course_name}</b>

<b>Прогресс:</b> [{progress_bar}] {percentage:.1f}%

✓ <b>Завершено дней:</b> {len(completed_days)} из {total_days}
🚀 <b>Текущий день:</b> {current_day}
⭐ <b>Выполнено заданий:</b> {user.get('total_tasks_completed', 0)}
"""
    
    await message.answer(progress_text, parse_mode="HTML")

# Обработчики callback-запросов
@dp.callback_query_handler(lambda c: c.data == 'python_courses')
async def python_courses(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(
        callback_query.from_user.id,
        "🐍 <b>ВЫБЕРИ СВОЙ PYTHON КУРС</b> 🐍\n\n"
        "<b>⚡ Python за 7 дней</b>\n"
        "Экспресс-курс для быстрого старта",
        reply_markup=get_python_courses_keyboard(),
        parse_mode="HTML"
    )

@dp.callback_query_handler(lambda c: c.data.startswith('start_'))
async def start_course(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user_id = callback_query.from_user.id
    course_type = callback_query.data.replace('start_', '')
    
    if course_type not in learning_plans:
        await bot.send_message(user_id, "❗️ <b>Курс временно недоступен.</b>", parse_mode="HTML")
        return
    
    user_data[user_id]['current_course'] = course_type
    user_data[user_id]['current_day'] = 1
    user_data[user_id]['start_date'] = datetime.now().strftime("%Y-%m-%d")
    
    course_name = learning_plans[course_type]['name']
    total_days = len(learning_plans[course_type]['days'])
    
    welcome_text = f"""
🎉 <b>ПОЗДРАВЛЯЕМ! ТЫ НАЧАЛ КУРС:</b> {course_name}
📅 <b>Продолжительность:</b> {total_days} дней

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
        user_data[user_id]['current_day'] = current_day + 1
        if current_day not in user.get('completed_days', []):
            user_data[user_id]['completed_days'] = user.get('completed_days', []) + [current_day]
        user_data[user_id]['total_tasks_completed'] = user.get('total_tasks_completed', 0) + 1
        
        next_task = learning_plans[course_type]['days'][current_day + 1]
        course_name = learning_plans[course_type]['name']
        
        task_text = f"""
🚀 <b>Отличная работа! Продолжаем!</b>

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
🔄 <b>ПОВТОРЕНИЕ МАТЕРИАЛА</b>

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

@dp.callback_query_handler(lambda c: c.data == 'todays_task')
async def todays_task(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user_id = callback_query.from_user.id
    user = user_data.get(user_id, {})
    
    if not user.get('current_course'):
        await bot.send_message(user_id, "❗️ <b>Сначала выбери курс!</b>", parse_mode="HTML")
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
        
        await bot.send_message(
            user_id, 
            response_text, 
            reply_markup=get_day_navigation_keyboard(user_id, course_type), 
            parse_mode="HTML"
        )

@dp.callback_query_handler(lambda c: c.data == 'my_progress')
async def my_progress(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user_id = callback_query.from_user.id
    user = user_data.get(user_id, {})
    
    if not user.get('current_course'):
        await bot.send_message(user_id, "❗️ <b>Ты еще не начал ни одного курса!</b>", parse_mode="HTML")
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
📊 <b>ТВОЙ ПРОГРЕСС</b>
🎓 <b>{course_name}</b>

<b>Прогресс:</b> [{progress_bar}] {percentage:.1f}%

✓ <b>Завершено дней:</b> {len(completed_days)} из {total_days}
🚀 <b>Текущий день:</b> {current_day}
⭐ <b>Выполнено заданий:</b> {user.get('total_tasks_completed', 0)}
"""
    
    await bot.send_message(user_id, progress_text, parse_mode="HTML")

@dp.callback_query_handler(lambda c: c.data == 'back_to_main')
async def back_to_main(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user_id = callback_query.from_user.id
    username = callback_query.from_user.username or callback_query.from_user.first_name or "Аноним"
    
    welcome_text = f"""
👋 <b>ДОБРО ПОЖАЛОВАТЬ В DH LEARNING, {username}!</b> 🚀

🎯 <b>ДОСТУПНЫЕ КУРСЫ:</b>
• Python за 7 дней
• Node.js за 7 дней

<b>Выбери курс чтобы начать обучение:</b> 👇
"""
    
    await bot.send_message(user_id, welcome_text, reply_markup=get_main_keyboard(), parse_mode="HTML")

@dp.message_handler()
async def echo_handler(message: types.Message):
    """Обработчик всех остальных сообщений"""
    await message.answer("🤖 Используйте команду /start для начала работы с ботом")

if __name__ == '__main__':
    print("🚀 Запускаю DH Learning Bot...")
    print(f"✅ Токен бота: {BOT_TOKEN[:10]}...")
    print(f"✅ Admin ID: {ADMIN_ID}")
    executor.start_polling(dp, skip_updates=True)
