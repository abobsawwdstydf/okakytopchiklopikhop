from flask import Flask, request, Response, render_template_string
import requests
from urllib.parse import unquote
import threading
import gzip
import brotli
import json

app = Flask(__name__)

request_count = 0
count_lock = threading.Lock()

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DH PROXY</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: #000000;
            color: #ffffff;
            font-family: 'Arial', sans-serif;
            min-height: 100vh;
            overflow-x: hidden;
        }

        .particles {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -1;
        }

        .particle {
            position: absolute;
            background: #8b00ff;
            border-radius: 50%;
            animation: float 20s infinite linear;
        }

        @keyframes float {
            0% {
                transform: translateY(100vh) translateX(0) scale(0);
                opacity: 0;
            }
            10% {
                opacity: 1;
            }
            90% {
                opacity: 1;
            }
            100% {
                transform: translateY(-100px) translateX(100px) scale(1);
                opacity: 0;
            }
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            position: relative;
            z-index: 1;
        }

        .header {
            text-align: center;
            padding: 120px 20px 100px;
            position: relative;
        }

        .dh-proxy-3d {
            font-size: 7em;
            font-weight: 900;
            background: linear-gradient(45deg, #8b00ff, #ff00ff, #00ffff, #8b00ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            background-size: 300% 300%;
            text-shadow: 
                0 0 30px #8b00ff,
                0 0 60px #ff00ff,
                0 0 90px #00ffff;
            margin-bottom: 30px;
            transform: perspective(500px) rotateX(20deg);
            animation: glow 4s ease-in-out infinite, gradientShift 8s ease-in-out infinite;
        }

        @keyframes glow {
            0%, 100% {
                text-shadow: 
                    0 0 20px #8b00ff,
                    0 0 40px #ff00ff,
                    0 0 60px #00ffff;
            }
            50% {
                text-shadow: 
                    0 0 30px #8b00ff,
                    0 0 60px #ff00ff,
                    0 0 90px #00ffff,
                    0 0 120px #00ffff;
            }
        }

        @keyframes gradientShift {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }

        .subtitle {
            font-size: 1.6em;
            color: #cccccc;
            margin-bottom: 60px;
            line-height: 1.6;
            animation: fadeInUp 2s ease-out;
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin: 80px 0;
        }

        .feature {
            background: rgba(17, 17, 17, 0.8);
            border: 1px solid #333333;
            border-radius: 20px;
            padding: 40px 30px;
            text-align: center;
            transition: all 0.4s ease;
            backdrop-filter: blur(10px);
            animation: slideIn 1s ease-out;
            animation-fill-mode: both;
        }

        .feature:nth-child(1) { animation-delay: 0.2s; }
        .feature:nth-child(2) { animation-delay: 0.4s; }
        .feature:nth-child(3) { animation-delay: 0.6s; }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(-50px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }

        .feature:hover {
            transform: translateY(-15px) scale(1.05);
            border-color: #8b00ff;
            box-shadow: 
                0 20px 50px rgba(139, 0, 255, 0.3),
                0 0 100px rgba(139, 0, 255, 0.1) inset;
        }

        .feature-icon {
            font-size: 4em;
            margin-bottom: 25px;
            background: linear-gradient(45deg, #8b00ff, #00ffff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: bounce 2s infinite;
        }

        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }

        .feature-title {
            color: #8b00ff;
            font-size: 1.5em;
            margin-bottom: 20px;
            font-weight: bold;
        }

        .feature-text {
            color: #999999;
            line-height: 1.6;
            font-size: 1.1em;
        }

        .usage-section {
            background: rgba(17, 17, 17, 0.8);
            border: 1px solid #333333;
            border-radius: 25px;
            padding: 60px;
            margin: 80px 0;
            backdrop-filter: blur(10px);
            animation: fadeInUp 1.5s ease-out;
        }

        .section-title {
            color: #8b00ff;
            font-size: 2.5em;
            text-align: center;
            margin-bottom: 50px;
            text-shadow: 0 0 30px rgba(139, 0, 255, 0.5);
            animation: pulse 3s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.8; }
        }

        .language-tabs {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 50px;
            flex-wrap: wrap;
        }

        .tab {
            background: rgba(26, 26, 26, 0.8);
            border: 2px solid #8b00ff;
            border-radius: 30px;
            padding: 15px 35px;
            color: #ffffff;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 1.1em;
            backdrop-filter: blur(5px);
        }

        .tab.active {
            background: linear-gradient(45deg, #8b00ff, #ff00ff);
            transform: scale(1.1);
            box-shadow: 0 0 30px rgba(139, 0, 255, 0.5);
        }

        .tab:hover {
            background: #8b00ff;
            transform: scale(1.1);
            box-shadow: 0 0 25px rgba(139, 0, 255, 0.7);
        }

        .code-block {
            background: rgba(0, 0, 0, 0.9);
            border: 2px solid #8b00ff;
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
            position: relative;
            overflow: hidden;
            animation: codeGlow 3s infinite alternate;
        }

        @keyframes codeGlow {
            from {
                box-shadow: 0 0 20px rgba(139, 0, 255, 0.3);
            }
            to {
                box-shadow: 0 0 40px rgba(139, 0, 255, 0.6);
            }
        }

        .code-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
        }

        .language {
            color: #00ffff;
            font-weight: bold;
            font-size: 1.3em;
            text-shadow: 0 0 10px #00ffff;
        }

        .copy-btn {
            background: linear-gradient(45deg, #8b00ff, #ff00ff);
            border: none;
            border-radius: 15px;
            color: white;
            padding: 12px 25px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 1em;
            position: relative;
            overflow: hidden;
        }

        .copy-btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            transition: left 0.5s;
        }

        .copy-btn:hover::before {
            left: 100%;
        }

        .copy-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(139, 0, 255, 0.5);
        }

        .copy-btn.copied {
            background: linear-gradient(45deg, #00ff00, #00cc00);
            transform: scale(0.95);
        }

        .code {
            background: #050505;
            border: 1px solid #333333;
            border-radius: 15px;
            padding: 30px;
            font-family: 'Courier New', monospace;
            color: #00ffff;
            overflow-x: auto;
            white-space: pre;
            line-height: 1.5;
            font-size: 1em;
            text-shadow: 0 0 5px #00ffff;
        }

        .demo {
            background: rgba(17, 17, 17, 0.8);
            border: 1px solid #333333;
            border-radius: 20px;
            padding: 40px;
            margin: 50px 0;
            text-align: center;
            backdrop-filter: blur(10px);
            animation: fadeInUp 2s ease-out;
        }

        .demo-url {
            background: #000000;
            border: 2px solid #8b00ff;
            border-radius: 15px;
            padding: 25px;
            margin: 25px 0;
            font-family: 'Courier New', monospace;
            color: #00ffff;
            font-size: 1.2em;
            word-break: break-all;
            animation: urlGlow 2s infinite alternate;
        }

        @keyframes urlGlow {
            from {
                box-shadow: 0 0 10px rgba(139, 0, 255, 0.3);
            }
            to {
                box-shadow: 0 0 20px rgba(139, 0, 255, 0.6);
            }
        }

        .comparison {
            background: rgba(17, 17, 17, 0.8);
            border: 1px solid #333333;
            border-radius: 25px;
            padding: 60px;
            margin: 80px 0;
            text-align: center;
            backdrop-filter: blur(10px);
            animation: fadeInUp 2s ease-out;
        }

        .comparison-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
            margin-top: 50px;
        }

        .other-proxies, .dh-proxy {
            background: rgba(26, 26, 26, 0.8);
            border-radius: 20px;
            padding: 40px;
            transition: all 0.4s ease;
            backdrop-filter: blur(5px);
        }

        .other-proxies {
            border: 2px solid #ff4444;
            animation: shake 0.5s ease-in-out;
        }

        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-5px); }
            75% { transform: translateX(5px); }
        }

        .dh-proxy {
            border: 2px solid #00ff00;
            animation: pulseGreen 2s infinite;
        }

        @keyframes pulseGreen {
            0%, 100% { box-shadow: 0 0 20px rgba(0, 255, 0, 0.3); }
            50% { box-shadow: 0 0 40px rgba(0, 255, 0, 0.6); }
        }

        .bad {
            color: #ff4444;
            font-size: 1.3em;
            margin: 15px 0;
            text-shadow: 0 0 10px #ff4444;
        }

        .good {
            color: #00ff00;
            font-size: 1.3em;
            margin: 15px 0;
            text-shadow: 0 0 10px #00ff00;
        }

        .footer {
            text-align: center;
            padding: 80px 20px 40px;
            border-top: 1px solid #333333;
            margin-top: 80px;
            color: #666666;
            animation: fadeInUp 2s ease-out;
        }

        .copyright {
            font-size: 1.2em;
            margin-top: 25px;
        }

        @media (max-width: 768px) {
            .dh-proxy-3d { font-size: 4em; }
            .container { padding: 10px; }
            .header { padding: 80px 20px 60px; }
            .usage-section { padding: 30px; }
            .comparison-grid { grid-template-columns: 1fr; }
            .code { font-size: 0.9em; padding: 20px; }
            .features { grid-template-columns: 1fr; }
        }

        .floating {
            animation: floating 6s ease-in-out infinite;
        }

        @keyframes floating {
            0%, 100% { 
                transform: perspective(500px) rotateX(20deg) translateY(0px) rotate(0deg); 
            }
            33% { 
                transform: perspective(500px) rotateX(20deg) translateY(-20px) rotate(1deg); 
            }
            66% { 
                transform: perspective(500px) rotateX(20deg) translateY(-10px) rotate(-1deg); 
            }
        }
    </style>
</head>
<body>
    <div class="particles" id="particles"></div>
    
    <div class="container">
        <div class="header">
            <div class="dh-proxy-3d floating">DH PROXY</div>
            <div class="subtitle">
                Самый быстрый бесплатный прокси в мире.<br>
                Обрабатывает 500+ запросов в секунду. Без лимитов. Навсегда бесплатно.
            </div>
        </div>

        <div class="features">
            <div class="feature">
                <div class="feature-icon">⚡</div>
                <div class="feature-title">Молниеносная скорость</div>
                <div class="feature-text">500+ запросов в секунду. Самое быстрое прокси-решение на рынке</div>
            </div>
            <div class="feature">
                <div class="feature-icon">💰</div>
                <div class="feature-title">Навсегда бесплатно</div>
                <div class="feature-text">Никаких скрытых платежей. Никаких ограничений. Бесплатно навсегда</div>
            </div>
            <div class="feature">
                <div class="feature-icon">🔒</div>
                <div class="feature-title">Полная анонимность</div>
                <div class="feature-text">Ваш IP полностью скрыт. Без логов. Без отслеживания</div>
            </div>
        </div>

        <div class="usage-section">
            <div class="section-title">Начало работы за 30 секунд</div>
            
            <div class="language-tabs">
                <button class="tab active" onclick="showCode('python')">Python</button>
                <button class="tab" onclick="showCode('node')">Node.js</button>
                <button class="tab" onclick="showCode('php')">PHP</button>
                <button class="tab" onclick="showCode('curl')">cURL</button>
            </div>

            <div id="python-code" class="code-block">
                <div class="code-header">
                    <div class="language">Python</div>
                    <button class="copy-btn" onclick="copyCode('python')">Копировать код</button>
                </div>
                <div class="code">import requests

url = "https://api.example.com/data"
proxy_url = f"https://proxy.darkheavens.ru/url={url}"

response = requests.get(proxy_url)
print(response.text)</div>
            </div>

            <div id="node-code" class="code-block" style="display:none">
                <div class="code-header">
                    <div class="language">Node.js</div>
                    <button class="copy-btn" onclick="copyCode('node')">Копировать код</button>
                </div>
                <div class="code">const https = require('https');

const url = "https://api.example.com/data";
const proxy_url = `https://proxy.darkheavens.ru/url=${url}`;

https.get(proxy_url, (response) => {
    let data = '';
    response.on('data', (chunk) => data += chunk);
    response.on('end', () => console.log(data));
});</div>
            </div>

            <div id="php-code" class="code-block" style="display:none">
                <div class="code-header">
                    <div class="language">PHP</div>
                    <button class="copy-btn" onclick="copyCode('php')">Копировать код</button>
                </div>
                <div class="code">$url = "https://api.example.com/data";
$proxy_url = "https://proxy.darkheavens.ru/url=" . $url;

$response = file_get_contents($proxy_url);
echo $response;</div>
            </div>

            <div id="curl-code" class="code-block" style="display:none">
                <div class="code-header">
                    <div class="language">cURL</div>
                    <button class="copy-btn" onclick="copyCode('curl')">Копировать код</button>
                </div>
                <div class="code">curl "https://proxy.darkheavens.ru/url=https://api.example.com/data"</div>
            </div>
        </div>

        <div class="demo">
            <div class="section-title">Попробуйте прямо сейчас</div>
            <div class="demo-url">https://proxy.darkheavens.ru/url=https://jsonplaceholder.typicode.com/posts/1</div>
            <div style="color: #999; margin-top: 20px; font-size: 1.1em;">Откройте эту ссылку в браузере и увидите мгновенный результат</div>
        </div>

        <div class="comparison">
            <div class="section-title">Почему DH PROXY лучше других</div>
            <div class="comparison-grid">
                <div class="other-proxies">
                    <div style="color: #ff4444; font-size: 1.8em; margin-bottom: 30px; text-shadow: 0 0 15px #ff4444;">Обычные прокси</div>
                    <div class="bad">❌ Медленные</div>
                    <div class="bad">❌ Платные</div>
                    <div class="bad">❌ Ограничения</div>
                    <div class="bad">❌ Сложная настройка</div>
                    <div class="bad">❌ Отслеживание</div>
                </div>
                <div class="dh-proxy">
                    <div style="color: #00ff00; font-size: 1.8em; margin-bottom: 30px; text-shadow: 0 0 15px #00ff00;">DH PROXY</div>
                    <div class="good">✅ Молниеносные</div>
                    <div class="good">✅ Бесплатные</div>
                    <div class="good">✅ Без лимитов</div>
                    <div class="good">✅ Простые</div>
                    <div class="good">✅ Анонимные</div>
                </div>
            </div>
        </div>
    </div>

    <div class="footer">
        <div style="font-size: 1.5em; margin-bottom: 20px; color: #8b00ff; text-shadow: 0 0 20px #8b00ff;">DH PROXY</div>
        <div style="color: #999; margin-bottom: 15px; font-size: 1.1em;">Самый быстрый бесплатный прокси в мире</div>
        <div class="copyright">© 2025 Dark Heavens Corporate. Все права защищены.</div>
    </div>

    <script>
        // Создание частиц
        function createParticles() {
            const particles = document.getElementById('particles');
            const particleCount = 50;
            
            for (let i = 0; i < particleCount; i++) {
                const particle = document.createElement('div');
                particle.className = 'particle';
                
                // Случайные свойства
                const size = Math.random() * 5 + 1;
                const left = Math.random() * 100;
                const animationDuration = Math.random() * 20 + 10;
                const animationDelay = Math.random() * 5;
                const color = `hsl(${Math.random() * 60 + 270}, 100%, 50%)`;
                
                particle.style.width = `${size}px`;
                particle.style.height = `${size}px`;
                particle.style.left = `${left}%`;
                particle.style.background = color;
                particle.style.animationDuration = `${animationDuration}s`;
                particle.style.animationDelay = `${animationDelay}s`;
                
                particles.appendChild(particle);
            }
        }

        function showCode(lang) {
            document.querySelectorAll('.code-block').forEach(block => {
                block.style.display = 'none';
            });
            document.getElementById(lang + '-code').style.display = 'block';
            
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            event.target.classList.add('active');
        }

        function copyCode(lang) {
            const codeElement = document.getElementById(lang + '-code').querySelector('.code');
            const text = codeElement.textContent;
            const btn = event.target;
            
            navigator.clipboard.writeText(text).then(() => {
                btn.textContent = 'Скопировано!';
                btn.classList.add('copied');
                
                setTimeout(() => {
                    btn.textContent = 'Копировать код';
                    btn.classList.remove('copied');
                }, 2000);
            });
        }

        // Инициализация при загрузке
        document.addEventListener('DOMContentLoaded', function() {
            createParticles();
            
            // Анимация появления при скролле
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.style.animationPlayState = 'running';
                    }
                });
            });
            
            document.querySelectorAll('.feature, .usage-section, .comparison').forEach(el => {
                observer.observe(el);
            });
        });
    </script>
</body>
</html>
'''

def decode_response_content(response):
    """Правильно декодирует содержимое ответа с учетом кодировки и сжатия"""
    content = response.content

    # Проверяем кодировку и распаковываем если нужно
    if response.headers.get('Content-Encoding') == 'gzip':
        try:
            content = gzip.decompress(content)
        except:
            pass
    elif response.headers.get('Content-Encoding') == 'br':
        try:
            content = brotli.decompress(content)
        except:
            pass

    # Пытаемся определить кодировку текста
    if response.encoding:
        try:
            return content.decode(response.encoding)
        except:
            pass

    # Пробуем распространенные кодировки
    encodings = ['utf-8', 'latin-1', 'cp1251', 'iso-8859-1']
    for encoding in encodings:
        try:
            return content.decode(encoding)
        except:
            continue

    # Если ничего не помогло, возвращаем как есть
    return content

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/url=<path:target_url>')
def proxy_get(target_url):
    global request_count
    with count_lock:
        request_count += 1

    try:
        if not target_url.startswith(('http://', 'https://')):
            url = 'https://' + target_url
        else:
            url = target_url

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br'
        }

        # Копируем заголовки от клиента, кроме проблемных
        for key, value in request.headers:
            if key.lower() not in ['host', 'connection', 'content-length']:
                headers[key] = value

        response = requests.get(
            url=url,
            headers=headers,
            timeout=30,
            allow_redirects=True,
            stream=True
        )

        # Декодируем контент
        content = decode_response_content(response)

        # Создаем правильные заголовки для ответа
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        response_headers = []

        for key, value in response.headers.items():
            if key.lower() not in excluded_headers:
                response_headers.append((key, value))

        # Добавляем CORS заголовки
        response_headers.append(('Access-Control-Allow-Origin', '*'))
        response_headers.append(('Access-Control-Allow-Methods', '*'))
        response_headers.append(('Access-Control-Allow-Headers', '*'))
        response_headers.append(('X-Proxy-Server', 'DH-PROXY/2.0'))

        return Response(
            content,
            status=response.status_code,
            headers=response_headers
        )

    except requests.exceptions.Timeout:
        return Response('Proxy Error: Request timeout', 504)
    except requests.exceptions.ConnectionError:
        return Response('Proxy Error: Connection failed', 502)
    except Exception as e:
        return Response(f'Proxy Error: {str(e)}', 500)

@app.route('/url=<path:target_url>', methods=['POST', 'PUT', 'DELETE', 'PATCH'])
def proxy_with_body(target_url):
    global request_count
    with count_lock:
        request_count += 1

    try:
        if not target_url.startswith(('http://', 'https://')):
            url = 'https://' + target_url
        else:
            url = target_url

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br'
        }

        for key, value in request.headers:
            if key.lower() not in ['host', 'connection', 'content-length']:
                headers[key] = value

        response = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            data=request.get_data(),
            timeout=30,
            allow_redirects=True,
            stream=True
        )

        content = decode_response_content(response)

        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        response_headers = []

        for key, value in response.headers.items():
            if key.lower() not in excluded_headers:
                response_headers.append((key, value))

        response_headers.append(('Access-Control-Allow-Origin', '*'))
        response_headers.append(('Access-Control-Allow-Methods', '*'))
        response_headers.append(('Access-Control-Allow-Headers', '*'))
        response_headers.append(('X-Proxy-Server', 'DH-PROXY/2.0'))

        return Response(
            content,
            status=response.status_code,
            headers=response_headers
        )

    except requests.exceptions.Timeout:
        return Response('Proxy Error: Request timeout', 504)
    except requests.exceptions.ConnectionError:
        return Response('Proxy Error: Connection failed', 502)
    except Exception as e:
        return Response(f'Proxy Error: {str(e)}', 500)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, threaded=True)
