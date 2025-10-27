# app.py на Render.com
from flask import Flask, request, Response, render_template_string
from flask_cors import CORS
import base64
import cv2
import numpy as np
from datetime import datetime
import time
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # ✅ Включаем CORS для всех доменов

# Хранилище для кадра камеры
latest_frame = None
last_timestamp = None
frame_counter = 0

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
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 0 30px rgba(255,0,0,0.5);
        }
        .camera-title {
            font-size: 28px;
            margin-bottom: 20px;
            color: #ff4444;
        }
        .video-container {
            position: relative;
            display: inline-block;
        }
        img {
            border-radius: 10px;
            border: 4px solid #ff4444;
            max-width: 85vw;
            max-height: 75vh;
            background: #000;
        }
        .status {
            margin-top: 20px;
            font-size: 18px;
            padding: 10px;
            border-radius: 5px;
        }
        .online {
            color: #00ff00;
            background: rgba(0,255,0,0.1);
        }
        .offline {
            color: #ff4444;
            background: rgba(255,0,0,0.1);
        }
        .loading {
            color: #ffff00;
            background: rgba(255,255,0,0.1);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="camera-title">📹 LIVE CAMERA STREAM</div>
        <div class="video-container">
            <img id="cameraFeed" src="/video_feed" width="800" height="600" alt="Live Camera" 
                 onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iODAwIiBoZWlnaHQ9IjYwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjMzMzIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtc2l6ZT0iMjQiIGZpbGw9IiM2NjYiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj7QotC+0LvRjNC60L4g0YLRg9GA0L3QsDwvdGV4dD48L3N2Zz4='">
        </div>
        <div class="status loading" id="status">🟡 Connecting to camera...</div>
        <div class="status" id="timestamp">-</div>
        <div class="status" id="stats">Frames received: 0</div>
    </div>

    <script>
        let receivedFrames = 0;
        
        function updateStatus() {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    const statusElement = document.getElementById('status');
                    const timestampElement = document.getElementById('timestamp');
                    const statsElement = document.getElementById('stats');
                    
                    statsElement.textContent = `Frames received: ${data.frame_counter}`;
                    receivedFrames = data.frame_counter;
                    
                    if (data.is_online) {
                        statusElement.className = 'status online';
                        statusElement.innerHTML = '🟢 LIVE STREAMING - Camera is online';
                        const date = new Date(data.timestamp * 1000);
                        timestampElement.textContent = 'Last frame: ' + date.toLocaleTimeString();
                    } else {
                        statusElement.className = 'status offline';
                        statusElement.innerHTML = '🔴 OFFLINE - No signal from camera';
                        timestampElement.textContent = 'Waiting for camera connection...';
                    }
                })
                .catch(error => {
                    document.getElementById('status').className = 'status offline';
                    document.getElementById('status').innerHTML = '🔴 SERVER ERROR - Cannot connect';
                });
        }
        
        // Обновляем статус каждые 2 секунды
        setInterval(updateStatus, 2000);
        
        // Обновляем видео поток каждые 100ms
        setInterval(() => {
            const cameraFeed = document.getElementById('cameraFeed');
            const currentSrc = cameraFeed.src.split('?')[0];
            cameraFeed.src = currentSrc + '?t=' + new Date().getTime();
        }, 100);
        
        // Первоначальное обновление
        updateStatus();
        
        // Показываем сообщение если изображение не загружается
        document.getElementById('cameraFeed').onerror = function() {
            console.log('Image load error, retrying...');
        };
        
        document.getElementById('cameraFeed').onload = function() {
            console.log('Image loaded successfully');
        };
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

# Эндпоинт для приема видео с камеры
@app.route('/upload', methods=['POST', 'OPTIONS'])
def upload_camera():
    global latest_frame, last_timestamp, frame_counter
    
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        logger.info(f"Received upload request: {data.keys() if data else 'No data'}")
        
        if data and 'image' in data:
            # Декодируем base64 изображение
            image_data = base64.b64decode(data['image'])
            np_arr = np.frombuffer(image_data, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            
            if frame is not None:
                # Кодируем обратно в JPEG для streaming
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                latest_frame = buffer.tobytes()
                last_timestamp = int(datetime.now().timestamp())
                frame_counter += 1
                
                logger.info(f"Frame {frame_counter} processed successfully")
                
                return {
                    'status': 'success', 
                    'message': f'Frame {frame_counter} received',
                    'timestamp': last_timestamp,
                    'frame_size': len(latest_frame)
                }
            else:
                logger.error("Failed to decode frame")
        else:
            logger.error("No image data in request")
    
    except Exception as e:
        logger.error(f"Error processing frame: {e}")
    
    return {'status': 'error'}, 400

# Video streaming эндпоинт
@app.route('/video_feed')
def video_feed():
    def generate():
        frame_count = 0
        while True:
            if latest_frame is not None:
                frame_count += 1
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + 
                       latest_frame + b'\r\n')
            else:
                # Создаем пустой черный кадр
                empty_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                _, buffer = cv2.imencode('.jpg', empty_frame)
                empty_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + 
                       empty_bytes + b'\r\n')
            time.sleep(0.033)  # ~30 FPS
    
    return Response(generate(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Статус камеры
@app.route('/status')
def status():
    current_time = int(datetime.now().timestamp())
    is_online = last_timestamp and (current_time - last_timestamp) < 10  # 10 секунд таймаут
    
    return {
        'is_online': is_online,
        'timestamp': last_timestamp,
        'server_time': current_time,
        'frame_counter': frame_counter,
        'has_frame': latest_frame is not None
    }

# Простой тестовый эндпоинт
@app.route('/test')
def test():
    return {
        'message': 'Server is running!', 
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'frame_count': frame_counter
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
