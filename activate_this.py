from flask import Flask, jsonify, request, send_file
import urllib.parse
import requests
import time
import logging
import os
import uuid
import base64
import io

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

# API Configuration
POLLINATIONS_TEXT_URL = "https://text.pollinations.ai/"

# ======================
# AI Service Selection
# ======================

# Choose your image analysis service: "gemini" or "huggingface"
IMAGE_ANALYSIS_SERVICE = "gemini"  # Change to "huggingface" if preferred

# Service Configuration
if IMAGE_ANALYSIS_SERVICE == "gemini":
    # Gemini API Configuration
    GEMINI_API_KEY = "AIzaSyDbIzvvmlN9no8DwkhZAcpyfgDHaEVtlrQ"  # Replace with your actual key
    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent"
elif IMAGE_ANALYSIS_SERVICE == "huggingface":
    # Hugging Face Inference API Configuration
    HF_API_KEY = "YOUR_HUGGING_FACE_API_KEY_HERE"  # Replace with your actual key
    HF_API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"

# ======================
# Image Generation with g4f
# ======================

from g4f.client import Client

def generate_image_with_g4f(prompt):
    """Генерация изображения через g4f с моделью flux"""
    try:
        client = Client()
        response = client.images.generate(
            model="flux",
            prompt=prompt,
            response_format="url"
        )
        return True, response.data[0].url
    except Exception as e:
        logger.error(f"g4f image generation error: {e}")
        return False, str(e)

# ======================
# Text Generation with Pollinations.ai
# ======================

def generate_text_with_pollinations(prompt):
    """Генерация текста через Pollinations.ai"""
    try:
        # URL encode the prompt
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"{POLLINATIONS_TEXT_URL}{encoded_prompt}"
        
        logger.info(f"Making request to Pollinations.ai: {url}")
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        
        # Pollinations.ai returns plain text, not JSON
        generated_text = response.text.strip()
        return True, generated_text
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Pollinations.ai API error: {e}")
        return False, f"Ошибка соединения с сервисом: {e}"
    except Exception as e:
        logger.error(f"Unexpected error in text generation: {e}")
        return False, str(e)

# ======================
# Image Analysis Services
# ======================

def analyze_with_gemini(image_data):
    """Анализ изображения через Gemini"""
    try:
        url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
        
        # Convert image to base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        contents = [
            {
                "parts": [
                    {"text": "Детально опиши что изображено на этой картинке. Опиши цвета, объекты, стиль, настроение и возможный контекст."},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": image_base64
                        }
                    }
                ]
            }
        ]
        
        data = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 2048,
            }
        }
        
        response = requests.post(url, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        if 'candidates' in result and result['candidates']:
            return True, result['candidates'][0]['content']['parts'][0]['text']
        else:
            return False, "Gemini API returned no response"
            
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return False, str(e)

def analyze_with_huggingface(image_data):
    """Анализ изображения через Hugging Face API"""
    try:
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        response = requests.post(HF_API_URL, headers=headers, data=image_data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            # BLIP model returns a list with generated text
            caption = result[0].get('generated_text', 'Не удалось сгенерировать описание')
            return True, caption
        else:
            return False, "Неожиданный формат ответа от Hugging Face API"
            
    except requests.exceptions.RequestException as e:
        if e.response.status_code == 503:
            # Model is loading, need to wait
            return False, "Модель загружается, попробуйте через несколько секунд"
        logger.error(f"Hugging Face API error: {e}")
        return False, str(e)
    except Exception as e:
        logger.error(f"Unexpected error with Hugging Face: {e}")
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
    """Анализ изображения через выбранный сервис"""
    start_time = time.time()

    try:
        # Получаем изображение
        if 'file' in request.files:
            file = request.files['file']
            image_data = file.read()
        elif 'url' in request.json:
            image_url = request.json['url']
            response = requests.get(image_url, timeout=10)
            image_data = response.content
        else:
            return jsonify({'status': 'error', 'message': 'Не предоставлен файл или URL'}), 400

        # Анализируем через выбранный сервис
        if IMAGE_ANALYSIS_SERVICE == "gemini":
            success, description = analyze_with_gemini(image_data)
        else:  # huggingface
            success, description = analyze_with_huggingface(image_data)

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
    """Генерация кода через Pollinations.ai"""
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
        'service': 'AI API Server',
        'images_stored': image_count,
        'image_analysis_service': IMAGE_ANALYSIS_SERVICE
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
        <title>AI API Документация</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');
            
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
                --neon-glow: 0 0 10px var(--primary), 0 0 20px var(--primary), 0 0 30px var(--primary-glow);
            }
            
            body {
                background: linear-gradient(135deg, var(--darker) 0%, var(--dark) 50%, #16213e 100%);
                color: var(--light);
                font-family: 'Rajdhani', sans-serif;
                line-height: 1.6;
                min-height: 100vh;
                padding: 20px;
                overflow-x: hidden;
            }
            
            body::before {
                content: '';
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: 
                    radial-gradient(circle at 20% 80%, rgba(138, 43, 226, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(74, 0, 224, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 40% 40%, rgba(157, 78, 221, 0.05) 0%, transparent 50%);
                pointer-events: none;
                z-index: -1;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                position: relative;
            }
            
            .header {
                text-align: center;
                margin-bottom: 60px;
                padding: 40px 0;
                position: relative;
            }
            
            .header::after {
                content: '';
                position: absolute;
                bottom: 0;
                left: 50%;
                transform: translateX(-50%);
                width: 200px;
                height: 3px;
                background: linear-gradient(90deg, transparent, var(--primary), transparent);
                box-shadow: var(--neon-glow);
            }
            
            .header h1 {
                font-family: 'Orbitron', sans-serif;
                font-size: 4rem;
                font-weight: 900;
                background: linear-gradient(45deg, var(--primary), var(--primary-glow), #00ffff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: 20px;
                text-shadow: 0 0 30px rgba(138, 43, 226, 0.3);
                animation: titleGlow 3s ease-in-out infinite alternate;
            }
            
            @keyframes titleGlow {
                0% { text-shadow: 0 0 30px rgba(138, 43, 226, 0.3); }
                100% { text-shadow: 0 0 40px rgba(138, 43, 226, 0.6), 0 0 60px rgba(74, 0, 224, 0.3); }
            }
            
            .header p {
                font-size: 1.3rem;
                color: #cccccc;
                font-weight: 300;
                letter-spacing: 1px;
            }
            
            .service-badge {
                display: inline-block;
                background: rgba(138, 43, 226, 0.2);
                border: 1px solid var(--primary);
                border-radius: 20px;
                padding: 8px 20px;
                margin-top: 15px;
                font-size: 0.9rem;
                color: var(--primary-glow);
                box-shadow: var(--neon-glow);
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0% { box-shadow: 0 0 10px var(--primary), 0 0 20px var(--primary); }
                50% { box-shadow: 0 0 15px var(--primary), 0 0 30px var(--primary), 0 0 40px var(--primary-glow); }
                100% { box-shadow: 0 0 10px var(--primary), 0 0 20px var(--primary); }
            }
            
            .endpoints {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
                gap: 30px;
                margin-bottom: 60px;
            }
            
            .endpoint-card {
                background: rgba(26, 26, 46, 0.8);
                border-radius: 15px;
                padding: 30px;
                border: 1px solid rgba(138, 43, 226, 0.3);
                backdrop-filter: blur(10px);
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }
            
            .endpoint-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(138, 43, 226, 0.1), transparent);
                transition: left 0.5s ease;
            }
            
            .endpoint-card:hover {
                transform: translateY(-5px);
                border-color: var(--primary);
                box-shadow: var(--neon-glow);
            }
            
            .endpoint-card:hover::before {
                left: 100%;
            }
            
            .endpoint-header {
                display: flex;
                align-items: center;
                margin-bottom: 20px;
            }
            
            .method {
                padding: 6px 16px;
                border-radius: 20px;
                font-weight: 600;
                margin-right: 15px;
                font-size: 0.9rem;
                font-family: 'Orbitron', sans-serif;
                letter-spacing: 1px;
            }
            
            .get { 
                background: linear-gradient(45deg, #4CAF50, #8bc34a); 
                color: white; 
                box-shadow: 0 0 10px rgba(76, 175, 80, 0.3);
            }
            
            .post { 
                background: linear-gradient(45deg, #FF9800, #ffb74d); 
                color: white; 
                box-shadow: 0 0 10px rgba(255, 152, 0, 0.3);
            }
            
            .endpoint-title {
                font-size: 1.4rem;
                color: #ffffff;
                font-family: 'Orbitron', sans-serif;
                font-weight: 600;
            }
            
            .endpoint-description {
                color: #cccccc;
                margin-bottom: 25px;
                font-size: 1rem;
                line-height: 1.6;
            }
            
            .code-tabs {
                background: rgba(42, 42, 62, 0.9);
                border-radius: 12px;
                overflow: hidden;
                margin-bottom: 15px;
                border: 1px solid rgba(138, 43, 226, 0.2);
            }
            
            .tab-buttons {
                display: flex;
                background: rgba(32, 32, 52, 0.9);
                padding: 10px;
                gap: 5px;
                border-bottom: 1px solid rgba(138, 43, 226, 0.2);
            }
            
            .tab-button {
                padding: 8px 16px;
                background: transparent;
                border: 1px solid rgba(138, 43, 226, 0.3);
                color: #888;
                cursor: pointer;
                border-radius: 8px;
                transition: all 0.3s ease;
                font-size: 0.9rem;
                font-family: 'Rajdhani', sans-serif;
                font-weight: 500;
            }
            
            .tab-button.active {
                background: rgba(138, 43, 226, 0.2);
                border-color: var(--primary);
                color: var(--primary-glow);
                box-shadow: 0 0 10px rgba(138, 43, 226, 0.3);
            }
            
            .tab-content {
                display: none;
                padding: 20px;
            }
            
            .tab-content.active {
                display: block;
            }
            
            pre {
                background: rgba(15, 15, 26, 0.9);
                padding: 20px;
                border-radius: 8px;
                overflow-x: auto;
                border: 1px solid rgba(138, 43, 226, 0.2);
                color: #f8f8f2;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 0.9rem;
                line-height: 1.4;
            }
            
            .copy-btn {
                background: linear-gradient(45deg, var(--primary), var(--secondary));
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                cursor: pointer;
                margin-top: 10px;
                transition: all 0.3s ease;
                font-family: 'Rajdhani', sans-serif;
                font-weight: 600;
                font-size: 0.9rem;
                letter-spacing: 1px;
            }
            
            .copy-btn:hover {
                box-shadow: var(--neon-glow);
                transform: translateY(-2px);
            }
            
            .footer {
                text-align: center;
                margin-top: 60px;
                padding: 40px 0;
                color: #888;
                border-top: 1px solid rgba(138, 43, 226, 0.3);
                position: relative;
            }
            
            .footer::before {
                content: '';
                position: absolute;
                top: -1px;
                left: 50%;
                transform: translateX(-50%);
                width: 100px;
                height: 2px;
                background: linear-gradient(90deg, transparent, var(--primary), transparent);
                box-shadow: var(--neon-glow);
            }
            
            .copyright {
                font-size: 1rem;
                margin-bottom: 10px;
                color: #aaa;
            }
            
            .by-line {
                font-size: 0.9rem;
                color: var(--primary-glow);
                font-style: italic;
            }
            
            @media (max-width: 768px) {
                .endpoints {
                    grid-template-columns: 1fr;
                }
                
                .header h1 {
                    font-size: 2.5rem;
                }
                
                .header p {
                    font-size: 1.1rem;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 AI API SERVER</h1>
                <p>Мощный API для генерации текстов, изображений и анализа контента</p>
                <div class="service-badge">
                    Текст: Pollinations.ai | Изображения: G4F | Анализ: ''' + IMAGE_ANALYSIS_SERVICE.upper() + '''
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
                        Генерация текстовых ответов на любые запросы с помощью Pollinations.ai.
                    </p>
                    
                    <div class="code-tabs">
                        <div class="tab-buttons">
                            <button class="tab-button active" onclick="switchTab(this, 'text-python')">Python</button>
                            <button class="tab-button" onclick="switchTab(this, 'text-curl')">cURL</button>
                            <button class="tab-button" onclick="switchTab(this, 'text-node')">Node.js</button>
                        </div>
                        
                        <div id="text-python" class="tab-content active">
                            <pre><code>import requests

prompt = "Расскажи о искусственном интеллекте"
url = f"https://apiai.darkheavens.ru/v1/text/{requests.utils.quote(prompt)}"

response = requests.get(url)
print(response.json()['response'])</code></pre>
                            <button class="copy-btn" onclick="copyCode('text-python')">Копировать код</button>
                        </div>
                        
                        <div id="text-curl" class="tab-content">
                            <pre><code>curl -X GET \\
  "https://apiai.darkheavens.ru/v1/text/Расскажи%20о%20искусственном%20интеллекте" \\
  -H "Content-Type: application/json"</code></pre>
                            <button class="copy-btn" onclick="copyCode('text-curl')">Копировать код</button>
                        </div>
                        
                        <div id="text-node" class="tab-content">
                            <pre><code>const https = require('https');

const prompt = "Расскажи о искусственном интеллекте";
const encodedPrompt = encodeURIComponent(prompt);
const url = `https://apiai.darkheavens.ru/v1/text/${encodedPrompt}`;

https.get(url, (resp) => {
    let data = '';
    resp.on('data', (chunk) => data += chunk);
    resp.on('end', () => console.log(JSON.parse(data).response));
});</code></pre>
                            <button class="copy-btn" onclick="copyCode('text-node')">Копировать код</button>
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
                        Создание уникальных изображений по текстовому описанию с помощью нейросетей.
                    </p>
                    
                    <div class="code-tabs">
                        <div class="tab-buttons">
                            <button class="tab-button active" onclick="switchTab(this, 'image-python')">Python</button>
                            <button class="tab-button" onclick="switchTab(this, 'image-curl')">cURL</button>
                            <button class="tab-button" onclick="switchTab(this, 'image-node')">Node.js</button>
                        </div>
                        
                        <div id="image-python" class="tab-content active">
                            <pre><code>import requests

prompt = "космонавт в стиле поп-арт"
url = f"https://apiai.darkheavens.ru/v1/image/{requests.utils.quote(prompt)}"

response = requests.get(url)
result = response.json()
print(f"ID изображения: {result['image_id']}")
print(f"URL: {result['image_url']}")</code></pre>
                            <button class="copy-btn" onclick="copyCode('image-python')">Копировать код</button>
                        </div>
                        
                        <div id="image-curl" class="tab-content">
                            <pre><code>curl -X GET \\
  "https://apiai.darkheavens.ru/v1/image/космонавт%20в%20стиле%20поп-арт" \\
  -H "Content-Type: application/json"</code></pre>
                            <button class="copy-btn" onclick="copyCode('image-curl')">Копировать код</button>
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
        console.log('ID изображения:', result.image_id);
        console.log('URL:', result.image_url);
    });
});</code></pre>
                            <button class="copy-btn" onclick="copyCode('image-node')">Копировать код</button>
                        </div>
                    </div>
                </div>
                
                <!-- Анализ изображений -->
                <div class="endpoint-card">
                    <div class="endpoint-header">
                        <span class="method post">POST</span>
                        <h2 class="endpoint-title">Анализ изображений</h2>
                    </div>
                    <p class="endpoint-description">
                        Детальный анализ загруженных изображений с описанием содержимого, стиля и контекста.
                    </p>
                    
                    <div class="code-tabs">
                        <div class="tab-buttons">
                            <button class="tab-button active" onclick="switchTab(this, 'analyze-python')">Python</button>
                            <button class="tab-button" onclick="switchTab(this, 'analyze-curl')">cURL</button>
                            <button class="tab-button" onclick="switchTab(this, 'analyze-node')">Node.js</button>
                        </div>
                        
                        <div id="analyze-python" class="tab-content active">
                            <pre><code>import requests

# Вариант 1: Загрузка файла
with open('image.jpg', 'rb') as f:
    files = {'file': f}
    response = requests.post('https://apiai.darkheavens.ru/v1/uimg/', files=files)
    print(response.json()['description'])

# Вариант 2: По URL
data = {'url': 'https://example.com/image.jpg'}
response = requests.post('https://apiai.darkheavens.ru/v1/uimg/', json=data)
print(response.json()['description'])</code></pre>
                            <button class="copy-btn" onclick="copyCode('analyze-python')">Копировать код</button>
                        </div>
                        
                        <div id="analyze-curl" class="tab-content">
                            <pre><code># Загрузка файла
curl -X POST \\
  https://apiai.darkheavens.ru/v1/uimg/ \\
  -F "file=@/path/to/image.jpg"

# Использование URL
curl -X POST \\
  https://apiai.darkheavens.ru/v1/uimg/ \\
  -H "Content-Type: application/json" \\
  -d '{"url": "https://example.com/image.jpg"}'</code></pre>
                            <button class="copy-btn" onclick="copyCode('analyze-curl')">Копировать код</button>
                        </div>
                        
                        <div id="analyze-node" class="tab-content">
                            <pre><code>const https = require('https');
const fs = require('fs');

// Загрузка файла
const data = fs.readFileSync('image.jpg');
const options = {
    hostname: 'apiai.darkheavens.ru',
    path: '/v1/uimg/',
    method: 'POST',
    headers: {
        'Content-Type': 'multipart/form-data'
    }
};

const req = https.request(options, (resp) => {
    let data = '';
    resp.on('data', (chunk) => data += chunk);
    resp.on('end', () => console.log(JSON.parse(data).description));
});
req.write(data);
req.end();</code></pre>
                            <button class="copy-btn" onclick="copyCode('analyze-node')">Копировать код</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <div class="copyright">© 2025 Dark Heavens Corporate. Все права защищены.</div>
                <div class="by-line">by haker_one</div>
            </div>
        </div>
        
        <script>
            function switchTab(button, tabId) {
                // Hide all tab contents
                const tabContents = button.parentElement.parentElement.querySelectorAll('.tab-content');
                tabContents.forEach(tab => tab.classList.remove('active'));
                
                // Remove active class from all buttons
                const buttons = button.parentElement.querySelectorAll('.tab-button');
                buttons.forEach(btn => btn.classList.remove('active'));
                
                // Show selected tab and activate button
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
                const originalText = button.textContent;
                button.textContent = 'Скопировано!';
                setTimeout(() => button.textContent = originalText, 2000);
            }
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=71203, debug=True, threaded=True)
