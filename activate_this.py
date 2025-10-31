from flask import Flask, jsonify, request, send_file
import urllib.parse
import requests
import time
import logging
import os
import uuid
import base64
import random
import hashlib
from datetime import datetime
from dotenv import load_dotenv
import speech_recognition as sr
from pydub import AudioSegment
import io

# ======================
# Load Environment Variables
# ======================
load_dotenv()

# ======================
# Configuration
# ======================
app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
SERVER_PORT = int(os.getenv('SERVER_PORT', 10000))
SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
DOMAIN = os.getenv('DOMAIN', 'https://apiai.darkheavens.ru')
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'

# Folders for files
IMAGES_DIR = "images"
os.makedirs(IMAGES_DIR, exist_ok=True)

# ======================
# Unique Random Number Generator
# ======================

class UniqueRandomGenerator:
    def __init__(self):
        self.used_numbers = set()
        self.counter = 0
        
    def generate_unique_number(self, prompt):
        """Генерирует уникальное число для промпта"""
        prompt_hash = int(hashlib.md5(prompt.encode()).hexdigest()[:8], 16)
        time_component = int(datetime.now().timestamp() * 1000000) % 1000000
        self.counter += 1
        
        base_number = (prompt_hash + time_component + self.counter) % 1000000
        
        number = base_number
        zeros = 0
        
        while number in self.used_numbers:
            zeros += 1
            number = base_number * (10 ** zeros) + random.randint(0, 9)
            if zeros > 10:
                number = random.randint(1000000, 9999999)
                break
                
        self.used_numbers.add(number)
        return number

unique_generator = UniqueRandomGenerator()

# ======================
# Image Generation with g4f
# ======================

try:
    from g4f.client import Client
    g4f_available = True
except ImportError as e:
    logger.warning(f"g4f not available: {e}")
    g4f_available = False

def generate_image_with_g4f(prompt):
    """Генерация изображения через g4f с моделью flux"""
    if not g4f_available:
        return False, "g4f not available"
    
    try:
        unique_number = unique_generator.generate_unique_number(prompt)
        enhanced_prompt = f"{prompt} {unique_number}"
        
        logger.info(f"Enhanced image prompt with unique number: {unique_number}")
        
        client = Client()
        response = client.images.generate(
            model="flux",
            prompt=enhanced_prompt,
            response_format="url"
        )
        return True, response.data[0].url
    except Exception as e:
        logger.error(f"Image generation error: {e}")
        return False, str(e)

# ======================
# Text Generation with Pollinations.ai
# ======================

def generate_text_with_pollinations(prompt):
    """Генерация текста через Pollinations.ai"""
    try:
        unique_number = unique_generator.generate_unique_number(prompt)
        enhanced_prompt = f"{prompt} {unique_number}"
        
        logger.info(f"Enhanced text prompt with unique number: {unique_number}")
        
        encoded_prompt = urllib.parse.quote(enhanced_prompt)
        url = f"https://text.pollinations.ai/{encoded_prompt}"
        
        logger.info("Making request to text service")
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        
        generated_text = response.text.strip()
        return True, generated_text
        
    except Exception as e:
        logger.error(f"Text API error: {e}")
        return False, f"Ошибка соединения с сервисом: {e}"

# ======================
# Audio Processing Functions
# ======================

def convert_audio_format(audio_data, original_format):
    """Конвертирует аудио в WAV формат"""
    try:
        # Создаем AudioSegment из данных
        if original_format.lower() in ['mp3', 'mpeg']:
            audio = AudioSegment.from_mp3(io.BytesIO(audio_data))
        elif original_format.lower() in ['wav', 'wave']:
            audio = AudioSegment.from_wav(io.BytesIO(audio_data))
        elif original_format.lower() in ['ogg', 'oga']:
            audio = AudioSegment.from_ogg(io.BytesIO(audio_data))
        elif original_format.lower() in ['flac']:
            audio = AudioSegment.from_flac(io.BytesIO(audio_data))
        elif original_format.lower() in ['aac', 'm4a']:
            audio = AudioSegment.from_file(io.BytesIO(audio_data), "aac")
        elif original_format.lower() in ['wma']:
            audio = AudioSegment.from_file(io.BytesIO(audio_data), "wma")
        elif original_format.lower() in ['aiff', 'aif']:
            audio = AudioSegment.from_file(io.BytesIO(audio_data), "aiff")
        else:
            return False, f"Неподдерживаемый формат аудио: {original_format}"
        
        # Конвертируем в WAV
        wav_io = io.BytesIO()
        audio.export(wav_io, format="wav")
        return True, wav_io.getvalue()
        
    except Exception as e:
        logger.error(f"Audio conversion error: {e}")
        return False, f"Ошибка конвертации аудио: {e}"

def speech_to_text(audio_data):
    """Преобразует аудио в текст"""
    try:
        recognizer = sr.Recognizer()
        
        # Используем BytesIO для работы с данными в памяти
        audio_file = sr.AudioFile(io.BytesIO(audio_data))
        
        with audio_file as source:
            # Учитываем фоновый шум
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.record(source)
        
        # Распознаем речь с поддержкой русского языка
        text = recognizer.recognize_google(audio, language="ru-RU")
        return True, text.strip()
        
    except sr.UnknownValueError:
        return False, "Не удалось распознать речь"
    except sr.RequestError as e:
        logger.error(f"Speech recognition API error: {e}")
        return False, f"Ошибка сервиса распознавания речи: {e}"
    except Exception as e:
        logger.error(f"Speech to text error: {e}")
        return False, f"Ошибка обработки аудио: {e}"

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

# ======================
# Flask Routes
# ======================

@app.route('/v1/image/<path:prompt>')
def generate_image(prompt):
    """Генерация изображения"""
    start_time = time.time()

    try:
        decoded = urllib.parse.unquote(prompt)
        english_prompt = translate_to_english(decoded)

        success, image_url = generate_image_with_g4f(english_prompt)
        
        if success:
            image_id = str(uuid.uuid4())[:12]
            filename = f"{image_id}.jpg"
            filepath = download_image(image_url, filename)

            if filepath:
                server_url = f"{DOMAIN}/image/{image_id}"

                logger.info(f"Image saved to server: {filename}")

                return jsonify({
                    'status': 'success',
                    'image_id': image_id,
                    'image_url': server_url,
                    'original_prompt': decoded,
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
    """Генерация текста"""
    start_time = time.time()
    
    try:
        decoded_prompt = urllib.parse.unquote(prompt)
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

@app.route('/v1/aud_promt/text/', methods=['POST'])
def audio_to_text_generation():
    """Генерация текста из аудио"""
    start_time = time.time()

    try:
        if 'audio' not in request.files:
            return jsonify({'status': 'error', 'message': 'Аудио файл не предоставлен'}), 400

        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'status': 'error', 'message': 'Файл не выбран'}), 400

        # Получаем оригинальный формат файла
        original_format = audio_file.filename.split('.')[-1].lower()
        supported_formats = ['mp3', 'wav', 'ogg', 'oga', 'flac', 'aac', 'm4a', 'wma', 'aiff', 'aif', 'mpeg']
        
        if original_format not in supported_formats:
            return jsonify({'status': 'error', 'message': f'Неподдерживаемый формат аудио. Поддерживаемые: {", ".join(supported_formats)}'}), 400

        # Читаем данные файла
        audio_data = audio_file.read()
        
        # Конвертируем в WAV если нужно
        if original_format != 'wav':
            success, converted_data = convert_audio_format(audio_data, original_format)
            if not success:
                return jsonify({'status': 'error', 'message': converted_data}), 400
            audio_data = converted_data

        # Преобразуем речь в текст
        success, recognized_text = speech_to_text(audio_data)
        if not success:
            return jsonify({'status': 'error', 'message': recognized_text}), 400

        logger.info(f"Recognized text from audio: {recognized_text}")

        # Генерируем текст на основе распознанного промпта
        success, generated_text = generate_text_with_pollinations(recognized_text)

        if success:
            return jsonify({
                'status': 'success',
                'recognized_text': recognized_text,
                'generated_text': generated_text,
                'processing_time': f"{time.time() - start_time:.2f}s"
            })
        else:
            return jsonify({
                'status': 'error',
                'recognized_text': recognized_text,
                'message': generated_text,
                'processing_time': f"{time.time() - start_time:.2f}s"
            }), 500

    except Exception as e:
        logger.error(f"Error in audio_to_text_generation: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/v1/aud_promt/image/', methods=['POST'])
def audio_to_image_generation():
    """Генерация изображения из аудио"""
    start_time = time.time()

    try:
        if 'audio' not in request.files:
            return jsonify({'status': 'error', 'message': 'Аудио файл не предоставлен'}), 400

        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'status': 'error', 'message': 'Файл не выбран'}), 400

        # Получаем оригинальный формат файла
        original_format = audio_file.filename.split('.')[-1].lower()
        supported_formats = ['mp3', 'wav', 'ogg', 'oga', 'flac', 'aac', 'm4a', 'wma', 'aiff', 'aif', 'mpeg']
        
        if original_format not in supported_formats:
            return jsonify({'status': 'error', 'message': f'Неподдерживаемый формат аудио. Поддерживаемые: {", ".join(supported_formats)}'}), 400

        # Читаем данные файла
        audio_data = audio_file.read()
        
        # Конвертируем в WAV если нужно
        if original_format != 'wav':
            success, converted_data = convert_audio_format(audio_data, original_format)
            if not success:
                return jsonify({'status': 'error', 'message': converted_data}), 400
            audio_data = converted_data

        # Преобразуем речь в текст
        success, recognized_text = speech_to_text(audio_data)
        if not success:
            return jsonify({'status': 'error', 'message': recognized_text}), 400

        logger.info(f"Recognized text from audio: {recognized_text}")

        # Переводим на английский и генерируем изображение
        english_prompt = translate_to_english(recognized_text)
        success, image_url = generate_image_with_g4f(english_prompt)
        
        if success:
            image_id = str(uuid.uuid4())[:12]
            filename = f"{image_id}.jpg"
            filepath = download_image(image_url, filename)

            if filepath:
                server_url = f"{DOMAIN}/image/{image_id}"

                return jsonify({
                    'status': 'success',
                    'recognized_text': recognized_text,
                    'english_prompt': english_prompt,
                    'image_id': image_id,
                    'image_url': server_url,
                    'processing_time': f"{time.time() - start_time:.2f}s"
                })
            else:
                return jsonify({'status': 'error', 'message': 'Ошибка загрузки изображения'}), 500
        else:
            return jsonify({
                'status': 'error',
                'recognized_text': recognized_text,
                'message': image_url,
                'processing_time': f"{time.time() - start_time:.2f}s"
            }), 500

    except Exception as e:
        logger.error(f"Error in audio_to_image_generation: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/v1/code/<path:prompt>')
def generate_code(prompt):
    """Генерация кода"""
    start_time = time.time()
    
    try:
        decoded_prompt = urllib.parse.unquote(prompt)
        code_prompt = f"{decoded_prompt}. Provide ONLY the code without explanations. If libraries are used, include a requirements.txt file with those libraries."
        
        success, result = generate_text_with_pollinations(code_prompt)

        if success:
            return jsonify({
                'status': 'success',
                'code': result,
                'processing_time': f"{time.time() - start_time:.2f}s"
            })
        else:
            return jsonify({
                'status': 'error',
                'message': result,
                'processing_time': f"{time.time() - start_time:.2f}s"
            }), 500

    except Exception as e:
        logger.error(f"Unexpected error in generate_code: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/v1/status/')
def server_status():
    """Статус сервера"""
    image_count = len([f for f in os.listdir(IMAGES_DIR) if f.endswith('.jpg')])
    return jsonify({
        'status': 'running',
        'service': 'DHA AI',
        'version': 'v8.6',
        'domain': DOMAIN,
        'g4f_available': g4f_available,
        'images_stored': image_count,
        'unique_numbers_generated': len(unique_generator.used_numbers)
    })

@app.route('/')
def home():
    """Главная страница с веб-интерфейсом"""
    return '''
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DHA AI - Генератор текста и изображений</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
                color: #e2e2e2;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 800px;
                margin: 0 auto;
            }
            
            .header {
                text-align: center;
                margin-bottom: 40px;
                padding: 30px 0;
            }
            
            .header h1 {
                font-size: 2.5rem;
                background: linear-gradient(45deg, #8a2be2, #9d4edd, #00ffff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: 10px;
            }
            
            .header p {
                color: #cccccc;
                font-size: 1.1rem;
            }
            
            .card {
                background: rgba(26, 26, 46, 0.8);
                border-radius: 15px;
                padding: 30px;
                margin-bottom: 30px;
                border: 1px solid rgba(138, 43, 226, 0.3);
            }
            
            .card h2 {
                color: #ffffff;
                margin-bottom: 20px;
                font-size: 1.5rem;
            }
            
            .form-group {
                margin-bottom: 20px;
            }
            
            label {
                display: block;
                margin-bottom: 8px;
                color: #cccccc;
                font-weight: 500;
            }
            
            textarea, input[type="text"], input[type="file"] {
                width: 100%;
                padding: 12px;
                background: rgba(42, 42, 62, 0.9);
                border: 1px solid rgba(138, 43, 226, 0.3);
                border-radius: 8px;
                color: #ffffff;
                font-size: 1rem;
                resize: vertical;
            }
            
            textarea {
                min-height: 100px;
            }
            
            .radio-group {
                display: flex;
                gap: 20px;
                margin: 15px 0;
            }
            
            .radio-label {
                display: flex;
                align-items: center;
                gap: 8px;
                cursor: pointer;
            }
            
            .btn {
                background: linear-gradient(45deg, #8a2be2, #4a00e0);
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 1rem;
                font-weight: 500;
                transition: all 0.3s ease;
            }
            
            .btn:hover {
                box-shadow: 0 0 15px rgba(138, 43, 226, 0.5);
                transform: translateY(-2px);
            }
            
            .btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }
            
            .result {
                margin-top: 20px;
                padding: 20px;
                background: rgba(15, 15, 26, 0.9);
                border-radius: 8px;
                border: 1px solid rgba(138, 43, 226, 0.2);
                display: none;
            }
            
            .result.success {
                border-color: #4CAF50;
                display: block;
            }
            
            .result.error {
                border-color: #f44336;
                display: block;
            }
            
            .loading {
                display: none;
                text-align: center;
                margin: 20px 0;
                color: #9d4edd;
            }
            
            .image-result {
                max-width: 100%;
                border-radius: 8px;
                margin-top: 15px;
            }
            
            .footer {
                text-align: center;
                margin-top: 40px;
                padding: 20px 0;
                color: #888;
                border-top: 1px solid rgba(138, 43, 226, 0.3);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>DHA AI</h1>
                <p>Генератор текста и изображений</p>
            </div>
            
            <!-- Текстовая генерация -->
            <div class="card">
                <h2>Текстовая генерация</h2>
                <form id="textForm">
                    <div class="form-group">
                        <label for="prompt">Введите промпт:</label>
                        <textarea id="prompt" name="prompt" placeholder="Напишите что-нибудь..." required></textarea>
                    </div>
                    <div class="radio-group">
                        <label class="radio-label">
                            <input type="radio" name="type" value="text" checked>
                            <span>Генерация текста</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="type" value="image">
                            <span>Генерация изображения</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="type" value="code">
                            <span>Генерация кода</span>
                        </label>
                    </div>
                    <button type="submit" class="btn" id="textSubmit">Сгенерировать</button>
                </form>
                <div class="loading" id="textLoading">Генерация...</div>
                <div class="result" id="textResult"></div>
            </div>
            
            <!-- Аудио генерация -->
            <div class="card">
                <h2>Аудио генерация</h2>
                <form id="audioForm">
                    <div class="form-group">
                        <label for="audioFile">Загрузите аудио файл:</label>
                        <input type="file" id="audioFile" name="audio" accept=".mp3,.wav,.ogg,.oga,.flac,.aac,.m4a,.wma,.aiff,.aif,.mpeg" required>
                        <small style="color: #888; display: block; margin-top: 5px;">
                            Поддерживаемые форматы: MP3, WAV, OGG, OGA, FLAC, AAC, M4A, WMA, AIFF, AIF, MPEG
                        </small>
                    </div>
                    <div class="radio-group">
                        <label class="radio-label">
                            <input type="radio" name="audioType" value="text" checked>
                            <span>Генерация текста</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="audioType" value="image">
                            <span>Генерация изображения</span>
                        </label>
                    </div>
                    <button type="submit" class="btn" id="audioSubmit">Обработать аудио</button>
                </form>
                <div class="loading" id="audioLoading">Обработка аудио...</div>
                <div class="result" id="audioResult"></div>
            </div>
            
            <div class="footer">
                <p>© 2025 Dark Heavens Corporate. Все права защищены.</p>
                <p>by haker_one</p>
            </div>
        </div>
        
        <script>
            // Текстовая форма
            document.getElementById('textForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const prompt = document.getElementById('prompt').value;
                const type = document.querySelector('input[name="type"]:checked').value;
                const submitBtn = document.getElementById('textSubmit');
                const loading = document.getElementById('textLoading');
                const resultDiv = document.getElementById('textResult');
                
                if (!prompt.trim()) return;
                
                submitBtn.disabled = true;
                loading.style.display = 'block';
                resultDiv.style.display = 'none';
                
                try {
                    const encodedPrompt = encodeURIComponent(prompt);
                    let url;
                    
                    if (type === 'text') {
                        url = `/v1/text/${encodedPrompt}`;
                    } else if (type === 'image') {
                        url = `/v1/image/${encodedPrompt}`;
                    } else if (type === 'code') {
                        url = `/v1/code/${encodedPrompt}`;
                    }
                    
                    const response = await fetch(url);
                    const data = await response.json();
                    
                    if (data.status === 'success') {
                        let content = '';
                        if (type === 'text' || type === 'code') {
                            content = `<h3>Результат:</h3><pre style="white-space: pre-wrap; background: rgba(0,0,0,0.3); padding: 15px; border-radius: 5px;">${data.response || data.code}</pre>`;
                        } else if (type === 'image') {
                            content = `
                                <h3>Изображение сгенерировано!</h3>
                                <p>ID: ${data.image_id}</p>
                                <img src="${data.image_url}" alt="Generated image" class="image-result" onerror="this.style.display='none'">
                                <p><a href="${data.image_url}" target="_blank">Открыть изображение</a></p>
                            `;
                        }
                        
                        resultDiv.innerHTML = content;
                        resultDiv.className = 'result success';
                    } else {
                        resultDiv.innerHTML = `<h3>Ошибка:</h3><p>${data.message}</p>`;
                        resultDiv.className = 'result error';
                    }
                } catch (error) {
                    resultDiv.innerHTML = `<h3>Ошибка:</h3><p>${error.message}</p>`;
                    resultDiv.className = 'result error';
                } finally {
                    submitBtn.disabled = false;
                    loading.style.display = 'none';
                }
            });
            
            // Аудио форма
            document.getElementById('audioForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const audioFile = document.getElementById('audioFile').files[0];
                const type = document.querySelector('input[name="audioType"]:checked').value;
                const submitBtn = document.getElementById('audioSubmit');
                const loading = document.getElementById('audioLoading');
                const resultDiv = document.getElementById('audioResult');
                
                if (!audioFile) return;
                
                submitBtn.disabled = true;
                loading.style.display = 'block';
                resultDiv.style.display = 'none';
                
                try {
                    const formData = new FormData();
                    formData.append('audio', audioFile);
                    
                    let url = type === 'text' ? '/v1/aud_promt/text/' : '/v1/aud_promt/image/';
                    
                    const response = await fetch(url, {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    
                    if (data.status === 'success') {
                        let content = '';
                        if (type === 'text') {
                            content = `
                                <h3>Распознанный текст:</h3>
                                <p><em>"${data.recognized_text}"</em></p>
                                <h3>Сгенерированный текст:</h3>
                                <pre style="white-space: pre-wrap; background: rgba(0,0,0,0.3); padding: 15px; border-radius: 5px;">${data.generated_text}</pre>
                            `;
                        } else {
                            content = `
                                <h3>Распознанный текст:</h3>
                                <p><em>"${data.recognized_text}"</em></p>
                                <h3>Изображение сгенерировано!</h3>
                                <p>ID: ${data.image_id}</p>
                                <img src="${data.image_url}" alt="Generated image" class="image-result" onerror="this.style.display='none'">
                                <p><a href="${data.image_url}" target="_blank">Открыть изображение</a></p>
                            `;
                        }
                        
                        resultDiv.innerHTML = content;
                        resultDiv.className = 'result success';
                    } else {
                        resultDiv.innerHTML = `<h3>Ошибка:</h3><p>${data.message}</p>`;
                        resultDiv.className = 'result error';
                    }
                } catch (error) {
                    resultDiv.innerHTML = `<h3>Ошибка:</h3><p>${error.message}</p>`;
                    resultDiv.className = 'result error';
                } finally {
                    submitBtn.disabled = false;
                    loading.style.display = 'none';
                }
            });
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    logger.info(f"Starting DHA AI Server v8.6 on {SERVER_HOST}:{SERVER_PORT}")
    logger.info(f"Domain: {DOMAIN}")
    logger.info(f"Debug mode: {DEBUG_MODE}")
    logger.info(f"g4f available: {g4f_available}")
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=DEBUG_MODE, threaded=True)
