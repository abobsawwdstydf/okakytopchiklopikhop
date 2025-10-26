from flask import Flask, jsonify, request, send_file
from g4f.client import Client
import urllib.parse
import requests
import time
import logging
import os
import uuid
import io

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
client = Client()

# Папки для файлов
IMAGES_DIR = "images"
os.makedirs(IMAGES_DIR, exist_ok=True)

def translate_to_english(text):
    """Переводит текст на английский"""
    try:
        url = "https://api.mymemory.translated.net/get"
        params = {'q': text, 'langpair': 'ru|en'}
        response = requests.get(url, params=params, timeout=10)
        translation = response.json()
        return translation['responseData']['translatedText'] if translation['responseStatus'] == 200 else text
    except:
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

# Генерация изображения с сохранением на сервер
@app.route('/v1/image/<path:prompt>')
def generate_image(prompt):
    start_time = time.time()

    try:
        decoded = urllib.parse.unquote(prompt)
        english_prompt = translate_to_english(decoded)

        # Генерируем изображение
        response = client.images.generate(
            model="flux",
            prompt=english_prompt,
            response_format="url"
        )
        image_url = response.data[0].url

        # Скачиваем на сервер
        image_id = str(uuid.uuid4())[:12]
        filename = f"{image_id}.jpg"
        filepath = download_image(image_url, filename)

        if filepath:
            server_url = f"/image/{image_id}"

            logger.info(f"Image saved to server: {filename}")

            return jsonify({
                'status': 'success',
                'image_id': image_id,
                'image_url': f"http://localhost:5000{server_url}",
                'download_url': f"http://localhost:5000/v1/download/{image_id}",
                'original_prompt': decoded,
                'english_prompt': english_prompt,
                'processing_time': f"{time.time() - start_time:.2f}s"
            })
        else:
            return jsonify({'status': 'error', 'message': 'Failed to download image'}), 500

    except Exception as e:
        logger.error(f"Error in generate_image: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Просмотр изображения по ID
@app.route('/image/<image_id>')
def get_image(image_id):
    try:
        filename = f"{image_id}.jpg"
        filepath = os.path.join(IMAGES_DIR, filename)

        if os.path.exists(filepath):
            return send_file(filepath, mimetype='image/jpeg')
        else:
            return jsonify({'status': 'error', 'message': 'Image not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Скачивание изображения как файл
@app.route('/v1/download/<image_id>')
def download_image_file(image_id):
    try:
        filename = f"{image_id}.jpg"
        filepath = os.path.join(IMAGES_DIR, filename)

        if os.path.exists(filepath):
            return send_file(
                filepath,
                as_attachment=True,
                download_name=f"ai_image_{image_id}.jpg"
            )
        else:
            return jsonify({'status': 'error', 'message': 'Image not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Генерация текста
@app.route('/v1/text/<path:prompt>')
def generate_text(prompt):
    start_time = time.time()

    try:
        decoded = urllib.parse.unquote(prompt)

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": decoded}],
        )

        answer = response.choices[0].message.content

        return jsonify({
            'status': 'success',
            'response': answer,
            'processing_time': f"{time.time() - start_time:.2f}s"
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Анализ изображения
@app.route('/v1/uimg/', methods=['POST'])
def analyze_image():
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
            return jsonify({'status': 'error', 'message': 'No file or URL provided'}), 400

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "user",
                "content": "Детально опиши что изображено на этой картинке",
                "images": [image_data]
            }],
        )

        description = response.choices[0].message.content

        return jsonify({
            'status': 'success',
            'description': description,
            'processing_time': f"{time.time() - start_time:.2f}s"
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Генерация кода
@app.route('/v1/code/<path:prompt>')
def generate_code(prompt):
    start_time = time.time()

    try:
        decoded = urllib.parse.unquote(prompt)

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "user",
                "content": f"{decoded}. В ответе должен быть ТОЛЬКО код без пояснений. Если используются библиотеки, добавь файл requirements.txt с этими библиотеками."
            }],
        )

        code = response.choices[0].message.content

        return jsonify({
            'status': 'success',
            'code': code,
            'processing_time': f"{time.time() - start_time:.2f}s"
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Статус сервера
@app.route('/v1/status/')
def server_status():
    image_count = len([f for f in os.listdir(IMAGES_DIR) if f.endswith('.jpg')])
    return jsonify({
        'status': 'running',
        'images_stored': image_count,
        'performance': 'high'
    })

@app.route('/')
def home():
    return """
    <h1>AI API Server</h1>
    <h3>Доступные endpoints:</h3>
    <ul>
        <li><b>Текст:</b> GET /v1/text/твой запрос</li>
        <li><b>Изображение (сохраняет на сервер):</b> GET /v1/image/описание картинки</li>
        <li><b>Просмотр изображения:</b> GET /image/ID_изображения</li>
        <li><b>Скачать изображение:</b> GET /v1/download/ID_изображения</li>
        <li><b>Анализ изображения:</b> POST /v1/uimg/ с file или url</li>
        <li><b>Код:</b> GET /v1/code/описание кода</li>
    </ul>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=71203, debug=True, threaded=True)