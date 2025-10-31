from flask import Flask, jsonify, request, send_file
import urllib.parse
import requests
import time
import logging
import os
import uuid
import random

# ======================
# Configuration
# ======================
app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Folders for files
IMAGES_DIR = "images"
os.makedirs(IMAGES_DIR, exist_ok=True)

# ======================
# Helper Functions
# ======================

def translate_to_english(text):
    """Переводит текст на английский"""
    try:
        url = "https://api.mymemory.translated.net/get"
        params = {'q': text, 'langpair': 'ru|en'}
        response = requests.get(url, params=params, timeout=10)
        translation = response.json()
        return translation['responseData']['translatedText'] if translation['responseStatus'] == 200 else text
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return text

def download_image(url, filename):
    """Скачивает изображение и сохраняет на сервер"""
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            filepath = os.path.join(IMAGES_DIR, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return filepath
        return None
    except Exception as e:
        logger.error(f"Error downloading image: {e}")
        return None

def generate_random_number():
    """Генерирует уникальное случайное число для вариативности"""
    return random.randint(1, 999999999)

# ======================
# Text Generation with Pollinations.ai
# ======================

def generate_text_with_pollinations(prompt):
    """Генерация текста через Pollinations.ai"""
    try:
        # Добавляем случайное число для вариативности
        random_suffix = generate_random_number()
        enhanced_prompt = f"{prompt} {random_suffix}"
        
        # Кодируем промт для URL
        encoded_prompt = urllib.parse.quote(enhanced_prompt)
        url = f"https://text.pollinations.ai/{encoded_prompt}"
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Получаем чистый текст ответа
        text_response = response.text.strip()
        
        # Очищаем ответ от возможных артефактов
        if text_response.startswith('"') and text_response.endswith('"'):
            text_response = text_response[1:-1]
        
        return True, text_response
        
    except Exception as e:
        logger.error(f"Text generation error: {e}")
        return False, "Сервис временно недоступен. Попробуйте позже."

# ======================
# Image Generation with g4f
# ======================

from g4f.client import Client

def generate_image_with_g4f(prompt):
    """Генерация изображения через g4f с моделью flux"""
    try:
        # Добавляем случайное число для вариативности
        random_suffix = generate_random_number()
        enhanced_prompt = f"{prompt} {random_suffix}"
        
        client = Client()
        response = client.images.generate(
            model="flux",
            prompt=enhanced_prompt,
            response_format="url"
        )
        return True, response.data[0].url
    except Exception as e:
        logger.error(f"Image generation error: {e}")
        return False, "Сервис генерации изображений временно недоступен."

# ======================
# Flask Routes
# ======================

@app.route('/v1/image/<path:prompt>')
def generate_image(prompt):
    """Генерация изображения через g4f"""
    start_time = time.time()

    try:
        decoded = urllib.parse.unquote(prompt)
        english_prompt = translate_to_english(decoded)

        # Генерируем изображение через g4f
        success, image_url = generate_image_with_g4f(english_prompt)
        
        if success:
            # Скачиваем изображение на сервер
            image_id = str(uuid.uuid4())[:12]
            filename = f"{image_id}.jpg"
            filepath = download_image(image_url, filename)

            if filepath:
                server_url = f"https://apiai.darkheavens.ru/image/{image_id}"

                logger.info(f"Image saved to server: {filename}")

                return jsonify({
                    'status': 'success',
                    'image_id': image_id,
                    'image_url': server_url,
                    'original_prompt': decoded,
                    'english_prompt': english_prompt,
                    'processing_time': f"{time.time() - start_time:.2f}s"
                })
            else:
                return jsonify({'status': 'error', 'message': 'Ошибка загрузки изображения'}), 500
        else:
            return jsonify({'status': 'error', 'message': 'Ошибка генерации изображения'}), 500

    except Exception as e:
        logger.error(f"Error in generate_image: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/image/<image_id>')
def get_image(image_id):
    """Просмотр изображения по ID"""
    try:
        filename = f"{image_id}.jpg"
        filepath = os.path.join(IMAGES_DIR, filename)

        if os.path.exists(filepath):
            return send_file(filepath, mimetype='image/jpeg')
        else:
            return jsonify({'status': 'error', 'message': 'Изображение не найдено'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/v1/text/<path:prompt>')
def generate_text(prompt):
    """Генерация текста через Pollinations.ai"""
    start_time = time.time()
    
    try:
        decoded_prompt = urllib.parse.unquote(prompt)
        
        # Генерируем текст через Pollinations.ai
        success, result = generate_text_with_pollinations(decoded_prompt)

        if success:
            return jsonify({
                'status': 'success',
                'response': result,
                'processing_time': f"{time.time() - start_time:.2f}s"
            })
        else:
            return jsonify({
                'status': 'error', 
                'message': result,
                'processing_time': f"{time.time() - start_time:.2f}s"
            }), 500

    except Exception as e:
        logger.error(f"Unexpected error in generate_text: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/v1/status/')
def server_status():
    """Статус сервера"""
    image_count = len([f for f in os.listdir(IMAGES_DIR) if f.endswith('.jpg')])
    return jsonify({
        'status': 'running',
        'service': 'DHA AI API Server',
        'images_stored': image_count,
        'performance': 'high'
    })

@app.route('/')
def home():
    """Главная страница с документацией"""
    return '''
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DHA AI - Мощный API для AI</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            :root {
                --primary: #8a2be2;
                --primary-glow: #9d4edd;
                --secondary: #4a00e0;
                --dark: #1a1a2e;
                --darker: #0f0f1a;
                --light: #e2e2e2;
                --neon-glow: 0 0 10px var(--primary), 0 0 20px var(--primary), 0 0 30px var(--primary);
                --card-bg: rgba(30, 30, 46, 0.8);
            }
            
            body {
                background: linear-gradient(135deg, var(--darker) 0%, var(--dark) 50%, #16213e 100%);
                color: var(--light);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                min-height: 100vh;
                overflow-x: hidden;
            }
            
            .container {
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
            }
            
            .header {
                text-align: center;
                margin-bottom: 60px;
                padding: 60px 0;
                position: relative;
            }
            
            .glow-text {
                font-size: 4.5rem;
                font-weight: 800;
                background: linear-gradient(45deg, var(--primary), var(--primary-glow), #00d4ff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-shadow: var(--neon-glow);
                margin-bottom: 20px;
                animation: glow-pulse 3s ease-in-out infinite alternate;
                letter-spacing: 2px;
            }
            
            @keyframes glow-pulse {
                0% { 
                    text-shadow: 0 0 10px var(--primary), 0 0 20px var(--primary);
                    transform: scale(1);
                }
                100% { 
                    text-shadow: 0 0 20px var(--primary-glow), 0 0 40px var(--primary-glow), 0 0 60px var(--primary-glow);
                    transform: scale(1.02);
                }
            }
            
            .tagline {
                font-size: 1.6rem;
                color: #b19cd9;
                margin-bottom: 15px;
                font-weight: 300;
            }
            
            .endpoints {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
                gap: 40px;
                margin-bottom: 60px;
            }
            
            .endpoint-card {
                background: var(--card-bg);
                border-radius: 25px;
                padding: 40px;
                border: 1px solid rgba(138, 43, 226, 0.4);
                backdrop-filter: blur(20px);
                transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                position: relative;
                overflow: hidden;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            }
            
            .endpoint-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(138, 43, 226, 0.2), transparent);
                transition: left 0.7s;
            }
            
            .endpoint-card:hover::before {
                left: 100%;
            }
            
            .endpoint-card:hover {
                transform: translateY(-15px) scale(1.03);
                border-color: var(--primary);
                box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5), var(--neon-glow);
            }
            
            .endpoint-header {
                display: flex;
                align-items: center;
                margin-bottom: 25px;
            }
            
            .method {
                padding: 10px 25px;
                border-radius: 30px;
                font-weight: bold;
                margin-right: 20px;
                font-size: 1rem;
                background: linear-gradient(45deg, var(--primary), var(--secondary));
                color: white;
                box-shadow: 0 0 20px rgba(138, 43, 226, 0.6);
            }
            
            .endpoint-title {
                font-size: 1.8rem;
                color: #ffffff;
                font-weight: 700;
            }
            
            .endpoint-description {
                color: #d0d0d0;
                margin-bottom: 30px;
                font-size: 1.1rem;
                line-height: 1.7;
            }
            
            .code-tabs {
                background: rgba(20, 20, 35, 0.95);
                border-radius: 20px;
                overflow: hidden;
                margin-bottom: 25px;
                border: 1px solid rgba(138, 43, 226, 0.3);
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            }
            
            .tab-buttons {
                display: flex;
                background: rgba(35, 35, 55, 0.95);
                padding: 20px;
                gap: 10px;
                border-bottom: 1px solid rgba(138, 43, 226, 0.3);
            }
            
            .tab-button {
                padding: 12px 25px;
                background: transparent;
                border: none;
                color: #aaaaaa;
                cursor: pointer;
                border-radius: 12px;
                transition: all 0.3s ease;
                font-size: 1rem;
                display: flex;
                align-items: center;
                gap: 10px;
                font-weight: 600;
            }
            
            .tab-button.active {
                background: linear-gradient(45deg, var(--primary), var(--secondary));
                color: white;
                box-shadow: 0 0 20px rgba(138, 43, 226, 0.5);
            }
            
            .tab-content {
                display: none;
                padding: 30px;
            }
            
            .tab-content.active {
                display: block;
            }
            
            pre {
                background: rgba(10, 10, 20, 0.95);
                padding: 30px;
                border-radius: 15px;
                overflow-x: auto;
                border: 1px solid rgba(138, 43, 226, 0.4);
                color: #f8f8f2;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 0.95rem;
                line-height: 1.6;
                position: relative;
            }
            
            .copy-btn {
                background: linear-gradient(45deg, var(--primary), var(--secondary));
                color: white;
                border: none;
                padding: 14px 28px;
                border-radius: 10px;
                cursor: pointer;
                margin-top: 20px;
                transition: all 0.3s ease;
                font-size: 1rem;
                font-weight: 700;
                display: flex;
                align-items: center;
                gap: 10px;
                box-shadow: 0 5px 20px rgba(138, 43, 226, 0.4);
            }
            
            .copy-btn:hover {
                transform: translateY(-3px);
                box-shadow: 0 8px 25px rgba(138, 43, 226, 0.6);
            }
            
            .telegram-section {
                background: var(--card-bg);
                border-radius: 25px;
                padding: 50px;
                margin: 60px 0;
                border: 1px solid rgba(138, 43, 226, 0.4);
                text-align: center;
                box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
            }
            
            .telegram-title {
                font-size: 2.8rem;
                margin-bottom: 30px;
                background: linear-gradient(45deg, var(--primary), #0088cc);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-weight: 800;
            }
            
            .telegram-description {
                color: #d0d0d0;
                margin-bottom: 40px;
                font-size: 1.2rem;
                line-height: 1.7;
            }
            
            .model-container {
                text-align: center;
                margin: 80px 0;
                padding: 70px 0;
                background: rgba(30, 30, 46, 0.6);
                border-radius: 35px;
                border: 1px solid rgba(138, 43, 226, 0.3);
                position: relative;
                overflow: hidden;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
            }
            
            .model-title {
                font-size: 3rem;
                margin-bottom: 40px;
                background: linear-gradient(45deg, var(--primary), #00d4ff, #ff00ff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-weight: 900;
                text-shadow: 0 0 30px rgba(138, 43, 226, 0.5);
            }
            
            .model-3d {
                width: 350px;
                height: 350px;
                margin: 0 auto;
                background: linear-gradient(135deg, var(--primary), var(--secondary), #00d4ff);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 5rem;
                color: white;
                box-shadow: var(--neon-glow), 0 0 50px rgba(138, 43, 226, 0.5);
                animation: rotate-3d 25s linear infinite;
                cursor: grab;
                user-select: none;
                transition: all 0.3s ease;
                font-weight: 900;
                text-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
            }
            
            @keyframes rotate-3d {
                0% { transform: rotateY(0deg) rotateX(15deg) scale(1); }
                50% { transform: rotateY(180deg) rotateX(15deg) scale(1.05); }
                100% { transform: rotateY(360deg) rotateX(15deg) scale(1); }
            }
            
            .model-3d:active {
                cursor: grabbing;
                animation-play-state: paused;
            }
            
            .footer {
                text-align: center;
                margin-top: 100px;
                padding: 50px 0;
                color: #888;
                border-top: 1px solid rgba(138, 43, 226, 0.4);
                position: relative;
            }
            
            .copyright {
                font-size: 1.3rem;
                margin-bottom: 15px;
                color: #b19cd9;
                font-weight: 600;
            }
            
            .by-line {
                font-size: 1.1rem;
                font-style: italic;
                color: #777;
            }
            
            .feature-badge {
                display: inline-block;
                background: linear-gradient(45deg, var(--primary), var(--secondary));
                color: white;
                padding: 8px 20px;
                border-radius: 20px;
                margin: 5px;
                font-size: 0.9rem;
                font-weight: 600;
                box-shadow: 0 0 15px rgba(138, 43, 226, 0.4);
            }
            
            @media (max-width: 768px) {
                .endpoints {
                    grid-template-columns: 1fr;
                }
                
                .glow-text {
                    font-size: 2.8rem;
                }
                
                .endpoint-card {
                    padding: 30px;
                }
                
                .model-3d {
                    width: 250px;
                    height: 250px;
                    font-size: 3.5rem;
                }
                
                .telegram-section {
                    padding: 30px;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="glow-text">DHA AI</div>
                <p class="tagline">Продвинутый AI API для генерации текстов и изображений</p>
                <div>
                    <span class="feature-badge"><i class="fas fa-bolt"></i> Быстро</span>
                    <span class="feature-badge"><i class="fas fa-shield-alt"></i> Надежно</span>
                    <span class="feature-badge"><i class="fas fa-infinity"></i> Масштабируемо</span>
                </div>
            </div>
            
            <div class="endpoints">
                <!-- Генерация текста -->
                <div class="endpoint-card">
                    <div class="endpoint-header">
                        <span class="method get">GET</span>
                        <h2 class="endpoint-title">Генерация текста</h2>
                    </div>
                    <p class="endpoint-description">
                        Создание текстовых ответов на любые запросы. Поддержка русского и английского языков. Идеально для чат-ботов, контент-генерации и аналитики.
                    </p>
                    
                    <div class="code-tabs">
                        <div class="tab-buttons">
                            <button class="tab-button active" onclick="switchTab(this, 'text-python')">
                                <i class="fab fa-python"></i> Python
                            </button>
                            <button class="tab-button" onclick="switchTab(this, 'text-curl')">
                                <i class="fas fa-terminal"></i> cURL
                            </button>
                            <button class="tab-button" onclick="switchTab(this, 'text-node')">
                                <i class="fab fa-node-js"></i> Node.js
                            </button>
                        </div>
                        
                        <div id="text-python" class="tab-content active">
                            <pre><code>import requests

prompt = "Расскажи о искусственном интеллекте"
url = f"https://apiai.darkheavens.ru/v1/text/{requests.utils.quote(prompt)}"

response = requests.get(url)
if response.json()['status'] == 'success':
    print(response.json()['response'])
else:
    print("Ошибка:", response.json()['message'])</code></pre>
                            <button class="copy-btn" onclick="copyCode('text-python')">
                                <i class="fas fa-copy"></i> Копировать код
                            </button>
                        </div>
                        
                        <div id="text-curl" class="tab-content">
                            <pre><code>curl -X GET \\
  "https://apiai.darkheavens.ru/v1/text/Расскажи%20о%20искусственном%20интеллекте" \\
  -H "Content-Type: application/json"</code></pre>
                            <button class="copy-btn" onclick="copyCode('text-curl')">
                                <i class="fas fa-copy"></i> Копировать код
                            </button>
                        </div>
                        
                        <div id="text-node" class="tab-content">
                            <pre><code>const https = require('https');

const prompt = "Расскажи о искусственном интеллекте";
const encodedPrompt = encodeURIComponent(prompt);
const url = `https://apiai.darkheavens.ru/v1/text/${encodedPrompt}`;

https.get(url, (resp) => {
    let data = '';
    resp.on('data', (chunk) => data += chunk);
    resp.on('end', () => {
        const result = JSON.parse(data);
        if (result.status === 'success') {
            console.log(result.response);
        } else {
            console.log('Ошибка:', result.message);
        }
    });
});</code></pre>
                            <button class="copy-btn" onclick="copyCode('text-node')">
                                <i class="fas fa-copy"></i> Копировать код
                            </button>
                        </div>
                    </div>
                </div>
                
                <!-- Генерация изображений -->
                <div class="endpoint-card">
                    <div class="endpoint-header">
                        <span class="method get">GET</span>
                        <h2 class="endpoint-title">Генерация изображений</h2>
                    </div>
                    <p class="endpoint-description">
                        Создание уникальных изображений по текстовому описанию. Автоматический перевод на английский. Высокое качество и быстрая генерация.
                    </p>
                    
                    <div class="code-tabs">
                        <div class="tab-buttons">
                            <button class="tab-button active" onclick="switchTab(this, 'image-python')">
                                <i class="fab fa-python"></i> Python
                            </button>
                            <button class="tab-button" onclick="switchTab(this, 'image-curl')">
                                <i class="fas fa-terminal"></i> cURL
                            </button>
                            <button class="tab-button" onclick="switchTab(this, 'image-node')">
                                <i class="fab fa-node-js"></i> Node.js
                            </button>
                        </div>
                        
                        <div id="image-python" class="tab-content active">
                            <pre><code>import requests

prompt = "космонавт в стиле поп-арт"
url = f"https://apiai.darkheavens.ru/v1/image/{requests.utils.quote(prompt)}"

response = requests.get(url)
result = response.json()
if result['status'] == 'success':
    print(f"ID изображения: {result['image_id']}")
    print(f"URL: {result['image_url']}")
else:
    print("Ошибка:", result['message'])</code></pre>
                            <button class="copy-btn" onclick="copyCode('image-python')">
                                <i class="fas fa-copy"></i> Копировать код
                            </button>
                        </div>
                        
                        <div id="image-curl" class="tab-content">
                            <pre><code>curl -X GET \\
  "https://apiai.darkheavens.ru/v1/image/космонавт%20в%20стиле%20поп-арт" \\
  -H "Content-Type: application/json"</code></pre>
                            <button class="copy-btn" onclick="copyCode('image-curl')">
                                <i class="fas fa-copy"></i> Копировать код
                            </button>
                        </div>
                        
                        <div id="image-node" class="tab-content">
                            <pre><code>const https = require('https');

const prompt = "космонавт в стиле поп-арт";
const encodedPrompt = encodeURIComponent(prompt);
const url = `https://apiai.darkheavens.ru/v1/image/${encodedPrompt}`;

https.get(url, (resp) => {
    let data = '';
    resp.on('data', (chunk) => data += chunk);
    resp.on('end', () => {
        const result = JSON.parse(data);
        if (result.status === 'success') {
            console.log('ID изображения:', result.image_id);
            console.log('URL:', result.image_url);
        } else {
            console.log('Ошибка:', result.message);
        }
    });
});</code></pre>
                            <button class="copy-btn" onclick="copyCode('image-node')">
                                <i class="fas fa-copy"></i> Копировать код
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Telegram Bot Section -->
            <div class="telegram-section">
                <h2 class="telegram-title">
                    <i class="fab fa-telegram"></i> Telegram Бот Примеры
                </h2>
                <p class="telegram-description">
                    Готовые примеры кода для создания Telegram бота с командами /text и /image
                </p>
                
                <div class="code-tabs">
                    <div class="tab-buttons">
                        <button class="tab-button active" onclick="switchTab(this, 'telegram-python')">
                            <i class="fab fa-python"></i> Python + Aiogram
                        </button>
                        <button class="tab-button" onclick="switchTab(this, 'telegram-js')">
                            <i class="fab fa-js"></i> Node.js
                        </button>
                        <button class="tab-button" onclick="switchTab(this, 'telegram-php')">
                            <i class="fab fa-php"></i> PHP
                        </button>
                    </div>
                    
                    <div id="telegram-python" class="tab-content active">
                        <pre><code>from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import requests
import asyncio

API_TOKEN = 'YOUR_BOT_TOKEN'
API_URL = 'https://apiai.darkheavens.ru/v1/'

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer(
        "🤖 Привет! Я AI бот DHA\\n"
        "Доступные команды:\\n"
        "/text [запрос] - генерация текста\\n"
        "/image [описание] - генерация изображения"
    )

@dp.message_handler(commands=['text'])
async def generate_text(message: types.Message):
    prompt = message.get_args()
    if not prompt:
        await message.answer("📝 Использование: /text [ваш запрос]")
        return
    
    try:
        encoded_prompt = requests.utils.quote(prompt)
        response = requests.get(f"{API_URL}text/{encoded_prompt}", timeout=30)
        data = response.json()
        
        if data['status'] == 'success':
            await message.answer(f"🤖 {data['response']}")
        else:
            await message.answer(f"❌ Ошибка: {data['message']}")
            
    except Exception as e:
        await message.answer("⚠️ Сервис временно недоступен")

@dp.message_handler(commands=['image'])
async def generate_image(message: types.Message):
    prompt = message.get_args()
    if not prompt:
        await message.answer("🎨 Использование: /image [описание изображения]")
        return
    
    try:
        encoded_prompt = requests.utils.quote(prompt)
        response = requests.get(f"{API_URL}image/{encoded_prompt}", timeout=60)
        data = response.json()
        
        if data['status'] == 'success':
            await message.answer(
                f"🖼️ Изображение готово!\\n"
                f"📎 ID: {data['image_id']}\\n"
                f"🔗 URL: {data['image_url']}"
            )
        else:
            await message.answer(f"❌ Ошибка: {data['message']}")
            
    except Exception as e:
        await message.answer("⚠️ Сервис временно недоступен")

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)</code></pre>
                        <button class="copy-btn" onclick="copyCode('telegram-python')">
                            <i class="fas fa-copy"></i> Копировать код
                        </button>
                    </div>
                    
                    <div id="telegram-js" class="tab-content">
                        <pre><code>const TelegramBot = require('node-telegram-bot-api');
const https = require('https');
const { URL } = require('url');

const BOT_TOKEN = 'YOUR_BOT_TOKEN';
const API_URL = 'https://apiai.darkheavens.ru/v1/';

const bot = new TelegramBot(BOT_TOKEN, { polling: true });

bot.onText(/\\/start/, (msg) => {
    const chatId = msg.chat.id;
    bot.sendMessage(chatId,
        "🤖 Привет! Я AI бот DHA\\n" +
        "Доступные команды:\\n" +
        "/text [запрос] - генерация текста\\n" +
        "/image [описание] - генерация изображения"
    );
});

bot.onText(/\\/text (.+)/, (msg, match) => {
    const chatId = msg.chat.id;
    const prompt = match[1];
    
    const encodedPrompt = encodeURIComponent(prompt);
    const url = `${API_URL}text/${encodedPrompt}`;
    
    https.get(url, (resp) => {
        let data = '';
        resp.on('data', (chunk) => data += chunk);
        resp.on('end', () => {
            try {
                const result = JSON.parse(data);
                if (result.status === 'success') {
                    bot.sendMessage(chatId, `🤖 ${result.response}`);
                } else {
                    bot.sendMessage(chatId, `❌ Ошибка: ${result.message}`);
                }
            } catch (e) {
                bot.sendMessage(chatId, '⚠️ Сервис временно недоступен');
            }
        });
    }).on('error', () => {
        bot.sendMessage(chatId, '⚠️ Сервис временно недоступен');
    });
});

bot.onText(/\\/image (.+)/, (msg, match) => {
    const chatId = msg.chat.id;
    const prompt = match[1];
    
    const encodedPrompt = encodeURIComponent(prompt);
    const url = `${API_URL}image/${encodedPrompt}`;
    
    https.get(url, (resp) => {
        let data = '';
        resp.on('data', (chunk) => data += chunk);
        resp.on('end', () => {
            try {
                const result = JSON.parse(data);
                if (result.status === 'success') {
                    bot.sendMessage(chatId,
                        `🖼️ Изображение готово!\\n` +
                        `📎 ID: ${result.image_id}\\n` +
                        `🔗 URL: ${result.image_url}`
                    );
                } else {
                    bot.sendMessage(chatId, `❌ Ошибка: ${result.message}`);
                }
            } catch (e) {
                bot.sendMessage(chatId, '⚠️ Сервис временно недоступен');
            }
        });
    }).on('error', () => {
        bot.sendMessage(chatId, '⚠️ Сервис временно недоступен');
    });
});

bot.on('message', (msg) => {
    if (!msg.text.startsWith('/')) {
        bot.sendMessage(msg.chat.id, 
            "Используйте команды:\\n" +
            "/text [запрос] - для генерации текста\\n" +
            "/image [описание] - для генерации изображения"
        );
    }
});</code></pre>
                        <button class="copy-btn" onclick="copyCode('telegram-js')">
                            <i class="fas fa-copy"></i> Копировать код
                        </button>
                    </div>
                    
                    <div id="telegram-php" class="tab-content">
                        <pre><code>&lt;?php
$botToken = 'YOUR_BOT_TOKEN';
$apiUrl = 'https://api.telegram.org/bot' . $botToken . '/';
$apiBase = 'https://apiai.darkheavens.ru/v1/';

$update = json_decode(file_get_contents('php://input'), true);

if (!$update) {
    exit;
}

$chatId = $update['message']['chat']['id'] ?? null;
$text = $update['message']['text'] ?? '';
$messageId = $update['message']['message_id'] ?? null;

if (strpos($text, '/start') === 0) {
    sendMessage($chatId,
        "🤖 Привет! Я AI бот DHA\\n" .
        "Доступные команды:\\n" .
        "/text [запрос] - генерация текста\\n" .
        "/image [описание] - генерация изображения"
    );
} elseif (strpos($text, '/text') === 0) {
    $prompt = trim(substr($text, 6));
    if (empty($prompt)) {
        sendMessage($chatId, "📝 Использование: /text [ваш запрос]");
    } else {
        $encodedPrompt = urlencode($prompt);
        $response = file_get_contents($apiBase . 'text/' . $encodedPrompt);
        $data = json_decode($response, true);
        
        if ($data && $data['status'] == 'success') {
            sendMessage($chatId, "🤖 " . $data['response']);
        } else {
            $error = $data['message'] ?? 'Неизвестная ошибка';
            sendMessage($chatId, "❌ Ошибка: " . $error);
        }
    }
} elseif (strpos($text, '/image') === 0) {
    $prompt = trim(substr($text, 7));
    if (empty($prompt)) {
        sendMessage($chatId, "🎨 Использование: /image [описание изображения]");
    } else {
        $encodedPrompt = urlencode($prompt);
        $response = file_get_contents($apiBase . 'image/' . $encodedPrompt);
        $data = json_decode($response, true);
        
        if ($data && $data['status'] == 'success') {
            sendMessage($chatId,
                "🖼️ Изображение готово!\\n" .
                "📎 ID: " . $data['image_id'] . "\\n" .
                "🔗 URL: " . $data['image_url']
            );
        } else {
            $error = $data['message'] ?? 'Неизвестная ошибка';
            sendMessage($chatId, "❌ Ошибка: " . $error);
        }
    }
} elseif (!empty($text) && !str_starts_with($text, '/')) {
    sendMessage($chatId,
        "Используйте команды:\\n" .
        "/text [запрос] - для генерации текста\\n" .
        "/image [описание] - для генерации изображения"
    );
}

function sendMessage($chatId, $text) {
    global $apiUrl;
    $url = $apiUrl . 'sendMessage';
    $data = [
        'chat_id' => $chatId,
        'text' => $text,
        'parse_mode' => 'HTML'
    ];
    
    $options = [
        'http' => [
            'header' => "Content-type: application/x-www-form-urlencoded\\r\\n",
            'method' => 'POST',
            'content' => http_build_query($data),
        ],
    ];
    
    $context = stream_context_create($options);
    file_get_contents($url, false, $context);
}
?&gt;</code></pre>
                        <button class="copy-btn" onclick="copyCode('telegram-php')">
                            <i class="fas fa-copy"></i> Копировать код
                        </button>
                    </div>
                </div>
            </div>
            
            <!-- 3D Model Section -->
            <div class="model-container">
                <h2 class="model-title">DHA AI ТЕХНОЛОГИИ</h2>
                <div class="model-3d" id="model3d" onmousedown="startRotation(event)" ontouchstart="startRotation(event)">
                    <span>DHA</span>
                </div>
            </div>
            
            <div class="footer">
                <p class="copyright">© 2025 Dark Heavens Corporate. Все права защищены.</p>
                <p class="by-line">by haker_one</p>
            </div>
        </div>
        
        <script>
            function switchTab(button, tabId) {
                const tabContents = button.parentElement.parentElement.querySelectorAll('.tab-content');
                tabContents.forEach(tab => tab.classList.remove('active'));
                
                const buttons = button.parentElement.querySelectorAll('.tab-button');
                buttons.forEach(btn => btn.classList.remove('active'));
                
                document.getElementById(tabId).classList.add('active');
                button.classList.add('active');
            }
            
            function copyCode(tabId) {
                const codeElement = document.getElementById(tabId).querySelector('code');
                const textArea = document.createElement('textarea');
                textArea.value = codeElement.textContent;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                
                const button = document.getElementById(tabId).querySelector('.copy-btn');
                const originalText = button.innerHTML;
                button.innerHTML = '<i class="fas fa-check"></i> Скопировано!';
                setTimeout(() => button.innerHTML = originalText, 2000);
            }
            
            // 3D Model Rotation
            let isRotating = false;
            let startX, startY;
            let rotationX = 15, rotationY = 0;
            
            function startRotation(e) {
                isRotating = true;
                startX = e.clientX || e.touches[0].clientX;
                startY = e.clientY || e.touches[0].clientY;
                e.preventDefault();
            }
            
            function rotateModel(e) {
                if (!isRotating) return;
                
                const currentX = e.clientX || e.touches[0].clientX;
                const currentY = e.clientY || e.touches[0].clientY;
                
                const deltaX = currentX - startX;
                const deltaY = currentY - startY;
                
                rotationY += deltaX * 0.5;
                rotationX += deltaY * 0.5;
                
                const model = document.getElementById('model3d');
                model.style.transform = `rotateY(${rotationY}deg) rotateX(${rotationX}deg) scale(1.05)`;
                
                startX = currentX;
                startY = currentY;
            }
            
            function stopRotation() {
                isRotating = false;
                const model = document.getElementById('model3d');
                model.style.transform = `rotateY(${rotationY}deg) rotateX(${rotationX}deg) scale(1)`;
            }
            
            document.addEventListener('mousemove', rotateModel);
            document.addEventListener('touchmove', rotateModel);
            document.addEventListener('mouseup', stopRotation);
            document.addEventListener('touchend', stopRotation);
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=71203, debug=True, threaded=True)
