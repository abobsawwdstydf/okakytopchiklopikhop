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
IO_NET_API_BASE = "https://api.intelligence.io.solutions/api/v1"
IO_NET_API_TOKEN = "io-v2-eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lciI6IjIwMzE2MzU5LWZiN2MtNDc4YS04YzczLTU2MmNlZGM4YzRkYSIsImV4cCI6NDkxNTQxNTIwMX0.Tm8o-2RDU49zWs0SxQM3xhthv2nYaqepjHgNjWbuBPIE_mSq4xrA8nOSn2ym4x8pfMd-ezvwny8NM9Mwp7xDFA"

# Gemini API Configuration
GEMINI_API_KEY = "AIzaSyDbIzvvmlN9no8DwkhZAcpyfgDHaEVtlrQ"  # Замените на ваш ключ Gemini
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent"

# ======================
# Model Configuration & Fallback Logic
# ======================

TEXT_MODELS = [
    "meta-llama/Llama-3.3-70B-Instruct",
    "Qwen/QwQ-32B-Preview", 
    "microsoft/WizardLM-2-8x22B",
    "google/gemma-2-27b-it",
    "mistralai/Mixtral-8x22B-Instruct-v0.1"
]

def make_io_net_request(messages, model_index=0):
    """IO.net запрос с fallback моделями"""
    if model_index >= len(TEXT_MODELS):
        return False, "Все модели временно недоступны"

    current_model = TEXT_MODELS[model_index]
    url = f"{IO_NET_API_BASE}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {IO_NET_API_TOKEN}"
    }
    data = {
        "model": current_model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 4096
    }

    try:
        logger.info(f"Attempting request with model: {current_model}")
        response = requests.post(url, headers=headers, json=data, timeout=120)
        response.raise_for_status()
        result = response.json()
        generated_text = result['choices'][0]['message']['content']
        return True, generated_text

    except requests.exceptions.RequestException as e:
        logger.error(f"Error with model '{current_model}': {e}")
        return make_io_net_request(messages, model_index + 1)
    except (KeyError, IndexError) as e:
        logger.error(f"Unexpected response format from model '{current_model}': {e}")
        return make_io_net_request(messages, model_index + 1)

def generate_with_gemini(prompt, image_data=None):
    """Генерация текста или анализ изображений через Gemini"""
    url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
    
    contents = []
    
    if image_data:
        # Анализ изображения
        if isinstance(image_data, bytes):
            image_base64 = base64.b64encode(image_data).decode('utf-8')
        else:
            image_base64 = image_data
            
        contents = [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": image_base64
                        }
                    }
                ]
            }
        ]
    else:
        # Только текст
        contents = [
            {
                "parts": [{"text": prompt}]
            }
        ]
    
    data = {
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 2048,
        }
    }
    
    try:
        response = requests.post(url, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        if 'candidates' in result and result['candidates']:
            return True, result['candidates'][0]['content']['parts'][0]['text']
        else:
            return False, "Сервис временно недоступен"
            
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
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
    """Генерация текста через io.net с fallback на Gemini"""
    start_time = time.time()
    
    try:
        decoded_prompt = urllib.parse.unquote(prompt)
        messages = [{"role": "user", "content": decoded_prompt}]

        # Сначала пробуем io.net
        success, result = make_io_net_request(messages)

        if not success:
            # Если io.net не сработал, пробуем Gemini
            logger.info("Falling back to Gemini for text generation")
            success, result = generate_with_gemini(decoded_prompt)

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
    """Анализ изображения через Gemini"""
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

        # Анализируем через Gemini
        prompt = "Детально опиши что изображено на этой картинке. Опиши цвета, объекты, стиль, настроение и возможный контекст."
        success, description = generate_with_gemini(prompt, image_data)

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

@app.route('/v1/status/')
def server_status():
    """Статус сервера"""
    image_count = len([f for f in os.listdir(IMAGES_DIR) if f.endswith('.jpg')])
    return jsonify({
        'status': 'running',
        'service': 'AI API Server',
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
        <title>AI API Документация</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
                color: #ffffff;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            
            .header {
                text-align: center;
                margin-bottom: 50px;
                padding: 30px 0;
            }
            
            .header h1 {
                font-size: 3rem;
                background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 10px;
            }
            
            .header p {
                font-size: 1.2rem;
                color: #cccccc;
            }
            
            .endpoints {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
                gap: 30px;
                margin-bottom: 50px;
            }
            
            .endpoint-card {
                background: rgba(40, 40, 40, 0.8);
                border-radius: 15px;
                padding: 30px;
                border: 1px solid #444;
                backdrop-filter: blur(10px);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            
            .endpoint-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 30px rgba(0, 0, 0, 0.3);
            }
            
            .endpoint-header {
                display: flex;
                align-items: center;
                margin-bottom: 20px;
            }
            
            .method {
                padding: 5px 15px;
                border-radius: 20px;
                font-weight: bold;
                margin-right: 15px;
                font-size: 0.9rem;
            }
            
            .get { background: #4CAF50; color: white; }
            .post { background: #FF9800; color: white; }
            
            .endpoint-title {
                font-size: 1.4rem;
                color: #ffffff;
            }
            
            .endpoint-description {
                color: #cccccc;
                margin-bottom: 25px;
                font-size: 1rem;
            }
            
            .code-tabs {
                background: #2d2d2d;
                border-radius: 10px;
                overflow: hidden;
                margin-bottom: 15px;
            }
            
            .tab-buttons {
                display: flex;
                background: #3d3d3d;
                padding: 10px;
                gap: 5px;
            }
            
            .tab-button {
                padding: 8px 16px;
                background: transparent;
                border: none;
                color: #cccccc;
                cursor: pointer;
                border-radius: 5px;
                transition: all 0.3s ease;
                font-size: 0.9rem;
            }
            
            .tab-button.active {
                background: #4ecdc4;
                color: white;
            }
            
            .tab-content {
                display: none;
                padding: 20px;
            }
            
            .tab-content.active {
                display: block;
            }
            
            pre {
                background: #1e1e1e;
                padding: 20px;
                border-radius: 8px;
                overflow-x: auto;
                border: 1px solid #444;
                color: #f8f8f2;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 0.9rem;
                line-height: 1.4;
            }
            
            .copy-btn {
                background: #4ecdc4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                cursor: pointer;
                margin-top: 10px;
                transition: background 0.3s ease;
                font-size: 0.9rem;
            }
            
            .copy-btn:hover {
                background: #45b7af;
            }
            
            .footer {
                text-align: center;
                margin-top: 50px;
                padding: 30px 0;
                color: #888;
                border-top: 1px solid #444;
            }
            
            @media (max-width: 768px) {
                .endpoints {
                    grid-template-columns: 1fr;
                }
                
                .header h1 {
                    font-size: 2.2rem;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 AI API Документация</h1>
                <p>Мощный API для генерации текстов, изображений и анализа контента</p>
            </div>
            
            <div class="endpoints">
                <!-- Генерация текста -->
                <div class="endpoint-card">
                    <div class="endpoint-header">
                        <span class="method get">GET</span>
                        <h2 class="endpoint-title">Генерация текста</h2>
                    </div>
                    <p class="endpoint-description">
                        Генерация текстовых ответов на любые запросы с помощью продвинутых AI-моделей.
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
                <p>© 2024 AI API Server | Документация обновлена автоматически</p>
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
