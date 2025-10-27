# app.py на Render.com
from flask import Flask, request, Response, render_template_string
import base64
import cv2
import numpy as np
from datetime import datetime
import time

app = Flask(__name__)

# Хранилище для кадра камеры
latest_frame = None
last_timestamp = None

# HTML страница для просмотра
HTML_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Live Camera Stream</title>
    <style>
        body { 
            margin: 0; 
            padding: 0; 
            background: #000;
            color: white;
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .container {
            text-align: center;
            background: #1a1a1a;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 0 20px rgba(0,255,0,0.3);
        }
        .camera-title {
            font-size: 24px;
            margin-bottom: 15px;
            color: #00ff00;
        }
        img {
            border-radius: 10px;
            border: 3px solid #00ff00;
            max-width: 90vw;
            max-height: 80vh;
        }
        .status {
            margin-top: 15px;
            font-size: 16px;
        }
        .online {
            color: #00ff00;
        }
        .offline {
            color: #ff0000;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="camera-title">📹 LIVE CAMERA STREAM</div>
        <img id="cameraFeed" src="/video_feed" width="800" height="600" alt="Live Camera">
        <div class="status" id="status">Checking connection...</div>
        <div class="status" id="timestamp">-</div>
    </div>

    <script>
        function updateStatus() {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    const statusElement = document.getElementById('status');
                    const timestampElement = document.getElementById('timestamp');
                    
                    if (data.is_online) {
                        statusElement.innerHTML = '<span class="online">🟢 LIVE STREAMING</span>';
                        const date = new Date(data.timestamp * 1000);
                        timestampElement.textContent = 'Last update: ' + date.toLocaleTimeString();
                    } else {
                        statusElement.innerHTML = '<span class="offline">🔴 OFFLINE - No signal</span>';
                        timestampElement.textContent = 'Waiting for camera connection...';
                    }
                })
                .catch(error => {
                    document.getElementById('status').innerHTML = '<span class="offline">🔴 CONNECTION ERROR</span>';
                });
        }
        
        // Обновляем статус каждые 2 секунды
        setInterval(updateStatus, 2000);
        
        // Обновляем видео поток (обход кеширования)
        setInterval(() => {
            const cameraFeed = document.getElementById('cameraFeed');
            cameraFeed.src = '/video_feed?t=' + new Date().getTime();
        }, 100);
        
        // Первоначальное обновление
        updateStatus();
        
        // Авто-обновление при ошибке загрузки изображения
        document.getElementById('cameraFeed').onerror = function() {
            this.src = '/video_feed?t=' + new Date().getTime();
        };
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

# Эндпоинт для приема видео с камеры
@app.route('/upload', methods=['POST'])
def upload_camera():
    global latest_frame, last_timestamp
    
    try:
        data = request.get_json()
        
        if data and 'image' in data:
            # Декодируем base64 изображение
            image_data = base64.b64decode(data['image'])
            np_arr = np.frombuffer(image_data, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            
            if frame is not None:
                # Кодируем обратно в JPEG для streaming
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                latest_frame = buffer.tobytes()
                last_timestamp = int(datetime.now().timestamp())
                
                return {
                    'status': 'success', 
                    'message': 'Frame received',
                    'timestamp': last_timestamp
                }
    
    except Exception as e:
        print(f"Error processing frame: {e}")
    
    return {'status': 'error'}, 400

# Video streaming эндпоинт
@app.route('/video_feed')
def video_feed():
    def generate():
        while True:
            if latest_frame is not None:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + 
                       latest_frame + b'\r\n')
            else:
                # Пустой кадр если нет данных
                time.sleep(0.1)
    
    return Response(generate(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Статус камеры
@app.route('/status')
def status():
    current_time = int(datetime.now().timestamp())
    is_online = last_timestamp and (current_time - last_timestamp) < 5
    
    return {
        'is_online': is_online,
        'timestamp': last_timestamp,
        'server_time': current_time
    }

# Простой тестовый эндпоинт
@app.route('/test')
def test():
    return {'message': 'Server is running!', 'status': 'ok'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5931)
