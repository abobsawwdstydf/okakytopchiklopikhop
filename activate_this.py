from flask import Flask, jsonify, request
from g4f.client import Client
import urllib.parse
import requests
import time
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
client = Client()

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

        logger.info(f"Text request processed in {time.time() - start_time:.2f}s")

        return jsonify({
            'status': 'success',
            'response': answer,
            'processing_time': f"{time.time() - start_time:.2f}s"
        })

    except Exception as e:
        logger.error(f"Error in generate_text: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Генерация изображения
@app.route('/v1/image/<path:prompt>')
def generate_image(prompt):
    start_time = time.time()

    try:
        decoded = urllib.parse.unquote(prompt)
        english_prompt = translate_to_english(decoded)

        response = client.images.generate(
            model="flux",
            prompt=english_prompt,
            response_format="url"
        )
        image_url = response.data[0].url

        logger.info(f"Image request processed in {time.time() - start_time:.2f}s")

        return jsonify({
            'status': 'success',
            'image_url': image_url,
            'original_prompt': decoded,
            'english_prompt': english_prompt,
            'processing_time': f"{time.time() - start_time:.2f}s"
        })

    except Exception as e:
        logger.error(f"Error in generate_image: {e}")
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

        logger.info(f"Image analysis processed in {time.time() - start_time:.2f}s")

        return jsonify({
            'status': 'success',
            'description': description,
            'processing_time': f"{time.time() - start_time:.2f}s"
        })

    except Exception as e:
        logger.error(f"Error in analyze_image: {e}")
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

        logger.info(f"Code generation processed in {time.time() - start_time:.2f}s")

        return jsonify({
            'status': 'success',
            'code': code,
            'processing_time': f"{time.time() - start_time:.2f}s"
        })

    except Exception as e:
        logger.error(f"Error in generate_code: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Статус сервера
@app.route('/v1/status/')
def server_status():
    return jsonify({'status': 'running', 'performance': 'high'})

@app.route('/')
def home():
    return """
    <h1>AI API Server</h1>
    <h3>Доступные endpoints:</h3>
    <ul>
        <li><b>Текст:</b> GET /v1/text/твой запрос</li>
        <li><b>Изображение:</b> GET /v1/image/описание картинки</li>
        <li><b>Анализ изображения:</b> POST /v1/uimg/ с file или url</li>
        <li><b>Код:</b> GET /v1/code/описание кода</li>
        <li><b>Статус:</b> GET /v1/status/</li>
    </ul>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=71203, debug=True, threaded=True)