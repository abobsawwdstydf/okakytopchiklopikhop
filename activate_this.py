from flask import Flask, jsonify, request, send_file
import urllib.parse
import requests
import time
import logging
import os
import uuid

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

# IO.net API Configuration
IO_NET_API_BASE = "https://api.intelligence.io.solutions/api/v1"
# You must set your IO.net token here
IO_NET_API_TOKEN = "io-v2-eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lciI6IjIwMzE2MzU5LWZiN2MtNDc4YS04YzczLTU2MmNlZGM4YzRkYSIsImV4cCI6NDkxNTQxNTIwMX0.Tm8o-2RDU49zWs0SxQM3xhthv2nYaqepjHgNjWbuBPIE_mSq4xrA8nOSn2ym4x8pfMd-ezvwny8NM9Mwp7xDFA"

# ======================
# Model Configuration & Fallback Logic
# ======================

# List of models for text/code generation, in order of preference.
TEXT_MODELS = [
    "meta-llama/Llama-3.3-70B-Instruct",
    "Qwen/QwQ-32B-Preview",
    "microsoft/WizardLM-2-8x22B",
    "google/gemma-2-27b-it",
    "mistralai/Mixtral-8x22B-Instruct-v0.1"
]

def make_io_net_request(messages, model_index=0):
    """
    Makes a request to the IO.net chat completions API.
    Implements the fallback logic if a model fails.

    Args:
        messages: List of message dictionaries.
        model_index: Index of the model to try from TEXT_MODELS.

    Returns:
        tuple: (success_status, response_text_or_error_message)
    """
    if model_index >= len(TEXT_MODELS):
        return False, "All available models failed to process the request."

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
        "max_tokens": 4096  # Adjust as needed
    }

    try:
        logger.info(f"Attempting request with model: {current_model}")
        response = requests.post(url, headers=headers, json=data, timeout=120)
        response.raise_for_status()  # Raises an HTTPError for bad status codes
        result = response.json()
        generated_text = result['choices'][0]['message']['content']
        return True, generated_text

    except requests.exceptions.RequestException as e:
        logger.error(f"Error with model '{current_model}': {e}")
        # Recursively try the next model
        return make_io_net_request(messages, model_index + 1)
    except (KeyError, IndexError) as e:
        logger.error(f"Unexpected response format from model '{current_model}': {e}")
        return make_io_net_request(messages, model_index + 1)

# ======================
# Helper Functions
# ======================

def translate_to_english(text):
    """Translates text to English using MyMemory Translation API."""
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
    """Downloads an image and saves it to the server."""
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
    """
    NOTE: This endpoint remains as a stub.
    io.net does not provide a native image generation API.
    You would need to integrate a separate service like Stability AI or DALL-E.
    """
    start_time = time.time()
    return jsonify({
        'status': 'error',
        'message': 'Image generation via io.net is not available. Consider integrating a dedicated image generation service (e.g., Stable Diffusion API, DALL-E).',
        'processing_time': f"{time.time() - start_time:.2f}s"
    }), 501  # 501 Not Implemented

@app.route('/image/<image_id>')
def get_image(image_id):
    """Serves a previously generated image by its ID."""
    try:
        filename = f"{image_id}.jpg"
        filepath = os.path.join(IMAGES_DIR, filename)
        if os.path.exists(filepath):
            return send_file(filepath, mimetype='image/jpeg')
        else:
            return jsonify({'status': 'error', 'message': 'Image not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/v1/text/<path:prompt>')
def generate_text(prompt):
    """Generates text using the io.net API with model fallback."""
    start_time = time.time()
    try:
        decoded_prompt = urllib.parse.unquote(prompt)
        messages = [{"role": "user", "content": decoded_prompt}]

        success, result = make_io_net_request(messages)

        if success:
            return jsonify({
                'status': 'success',
                'response': result,
                'processing_time': f"{time.time() - start_time:.2f}s"
            })
        else:
            return jsonify({
                'status': 'error',
                'message': result,  # This contains the final error after all retries
                'processing_time': f"{time.time() - start_time:.2f}s"
            }), 500

    except Exception as e:
        logger.error(f"Unexpected error in generate_text: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/v1/uimg/', methods=['POST'])
def analyze_image():
    """
    NOTE: This endpoint remains as a stub.
    io.net does not provide a native image analysis API.
    You would need to integrate a separate service like Azure Computer Vision or OpenAI's GPT-4V.
    """
    start_time = time.time()
    return jsonify({
        'status': 'error',
        'message': 'Image analysis via io.net is not available. Consider integrating a dedicated computer vision service.',
        'processing_time': f"{time.time() - start_time:.2f}s"
    }), 501  # 501 Not Implemented

@app.route('/v1/code/<path:prompt>')
def generate_code(prompt):
    """Generates code using the io.net API with model fallback."""
    start_time = time.time()
    try:
        decoded_prompt = urllib.parse.unquote(prompt)
        # Specific instruction for code generation
        code_prompt = f"{decoded_prompt}. Provide ONLY the code without explanations. If libraries are used, include a requirements.txt file with those libraries."
        messages = [{"role": "user", "content": code_prompt}]

        success, result = make_io_net_request(messages)

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
    """Checks the status of the server."""
    image_count = len([f for f in os.listdir(IMAGES_DIR) if f.endswith('.jpg')])
    return jsonify({
        'status': 'running',
        'service': 'io.net AI Server',
        'images_stored': image_count
    })

@app.route('/')
def home():
    """Displays a simple homepage with API documentation."""
    return """
    <h1>AI API Server (Powered by io.net)</h1>
    <p><b>Note:</b> Image generation and analysis are not currently available via io.net.</p>
    <h3>Available Endpoints:</h3>
    <ul>
        <li><b>Text Generation:</b> GET /v1/text/your_text_request</li>
        <li><b>Code Generation:</b> GET /v1/code/your_code_request</li>
        <li><b>Server Status:</b> GET /v1/status/</li>
    </ul>
    <h3>Unavailable Endpoints (Require Additional Services):</h3>
    <ul>
        <li><s>Image Generation</s></li>
        <li><s>Image Analysis</s></li>
    </ul>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=71203, debug=True, threaded=True)
