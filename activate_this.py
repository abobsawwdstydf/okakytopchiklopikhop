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
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GOOGLE_VISION_API_KEY = os.getenv('GOOGLE_VISION_API_KEY')  # Новый ключ для Vision API
SERVER_PORT = int(os.getenv('SERVER_PORT', 10000))
SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
DOMAIN = os.getenv('DOMAIN', 'https://apiai.darkheavens.ru')
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'

# API Configuration
GOOGLE_VISION_API_URL = f"https://vision.googleapis.com/v1/images:annotate?key={GOOGLE_VISION_API_KEY}"

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
        
        logger.info(f"Making request to text service")
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        
        generated_text = response.text.strip()
        return True, generated_text
        
    except Exception as e:
        logger.error(f"Text API error: {e}")
        return False, f"Ошибка соединения с сервисом: {e}"

# ======================
# Image Analysis with Google Cloud Vision API
# ======================

def analyze_with_vision_api(image_data):
    """Анализ изображения через Google Cloud Vision API"""
    try:
        # Кодируем изображение в base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Формируем запрос к Vision API
        payload = {
            "requests": [
                {
                    "image": {
                        "content": image_base64
                    },
                    "features": [
                        {
                            "type": "LABEL_DETECTION",
                            "maxResults": 10
                        },
                        {
                            "type": "TEXT_DETECTION",
                            "maxResults": 5
                        },
                        {
                            "type": "IMAGE_PROPERTIES",
                            "maxResults": 5
                        }
                    ]
                }
            ]
        }
        
        response = requests.post(GOOGLE_VISION_API_URL, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        # Форматируем ответ в читаемый вид
        description_parts = []
        
        if 'responses' in result and result['responses']:
            response_data = result['responses'][0]
            
            # Анализ объектов (лейблы)
            if 'labelAnnotations' in response_data:
                labels = [label['description'] for label in response_data['labelAnnotations']]
                description_parts.append(f"📷 На изображении обнаружены объекты: {', '.join(labels)}.")
            
            # Анализ текста
            if 'textAnnotations' in response_data and response_data['textAnnotations']:
                detected_text = response_data['textAnnotations'][0]['description']
                description_parts.append(f"📝 Обнаружен текст: \"{detected_text[:100]}{'...' if len(detected_text) > 100 else ''}\".")
            
            # Анализ цветов
            if 'imagePropertiesAnnotation' in response_data:
                colors = response_data['imagePropertiesAnnotation']['dominantColors']['colors']
                top_colors = sorted(colors, key=lambda x: x['score'], reverse=True)[:3]
                color_descs = []
                for color in top_colors:
                    rgb = color['color']
                    color_descs.append(f"RGB({rgb.get('red', 0)}, {rgb.get('green', 0)}, {rgb.get('blue', 0)})")
                if color_descs:
                    description_parts.append(f"🎨 Основные цвета: {', '.join(color_descs)}.")
        
        if description_parts:
            final_description = " ".join(description_parts)
            return True, final_description
        else:
            return False, "Не удалось проанализировать изображение"
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Vision API request error: {e}")
        return False, f"Ошибка соединения с сервисом анализа изображений: {e}"
    except Exception as e:
        logger.error(f"Vision API processing error: {e}")
        return False, str(e)

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

@app.route('/v1/uimg/', methods=['POST'])
def analyze_image():
    """Анализ изображения через Google Cloud Vision API"""
    start_time = time.time()

    try:
        if 'file' in request.files:
            file = request.files['file']
            image_data = file.read()
        elif 'url' in request.json:
            image_url = request.json['url']
            response = requests.get(image_url, timeout=10)
            image_data = response.content
        else:
            return jsonify({'status': 'error', 'message': 'Не предоставлен файл или URL'}), 400

        success, description = analyze_with_vision_api(image_data)

        if success:
            return jsonify({
                'status': 'success',
                'description': description,
                'processing_time': f"{time.time() - start_time:.2f}s"
            })
        else:
            return jsonify({
                'status': 'error',
                'message': description,
                'processing_time': f"{time.time() - start_time:.2f}s"
            }), 500

    except Exception as e:
        logger.error(f"Error in analyze_image: {e}")
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
        'image_analysis_service': 'Google Cloud Vision API',
        'g4f_available': g4f_available,
        'images_stored': image_count,
        'unique_numbers_generated': len(unique_generator.used_numbers)
    })

if __name__ == '__main__':
    logger.info(f"Starting DHA AI Server v8.6 on {SERVER_HOST}:{SERVER_PORT}")
    logger.info(f"Domain: {DOMAIN}")
    logger.info(f"Debug mode: {DEBUG_MODE}")
    logger.info(f"g4f available: {g4f_available}")
    logger.info(f"Image analysis service: Google Cloud Vision API")
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=DEBUG_MODE, threaded=True)
