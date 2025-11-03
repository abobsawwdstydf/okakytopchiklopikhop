from flask import Flask, render_template_string
import os

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 DH Learning - Прокачка в Питоне и Node.js</title>
    <link rel="icon" type="image/x-icon" href="https://storage.googleapis.com/gpt-engineer-file-uploads/Mmp7STHj41hgutFG4xqKbKlwJ2s1/uploads/1760284886820-19d83c0f-a26a-44ff-9019-ea102827f795-13129162.png">
    <style>
        :root {
            --neon-purple: #bc13fe;
            --neon-blue: #00ffff;
            --neon-pink: #ff00ff;
            --dark-bg: #0a0a0a;
            --darker-bg: #050505;
            --dark-gray: #1a1a1a;
            --text-light: #ffffff;
            --text-gray: #b0b0b0;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: linear-gradient(135deg, var(--darker-bg) 0%, var(--dark-bg) 50%, #2d1b69 100%);
            color: var(--text-light);
            font-family: 'JetBrains Mono', 'SF Mono', Monaco, monospace;
            line-height: 1.6;
            min-height: 100vh;
            overflow-x: hidden;
        }

        .cyber-grid {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                linear-gradient(rgba(188, 19, 254, 0.1) 1px, transparent 1px),
                linear-gradient(90deg, rgba(188, 19, 254, 0.1) 1px, transparent 1px);
            background-size: 50px 50px;
            pointer-events: none;
            z-index: -1;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }

        header {
            background: rgba(10, 10, 10, 0.95);
            backdrop-filter: blur(20px);
            border-bottom: 3px solid transparent;
            border-image: linear-gradient(45deg, var(--neon-purple), var(--neon-blue)) 1;
            position: fixed;
            width: 100%;
            top: 0;
            z-index: 1000;
        }

        .nav-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1.5rem 0;
        }

        .logo {
            font-size: 2.5rem;
            font-weight: 900;
            background: linear-gradient(45deg, var(--neon-purple), var(--neon-blue), var(--neon-pink));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 0 0 30px rgba(188, 19, 254, 0.5);
            animation: hue-rotate 3s linear infinite;
        }

        @keyframes hue-rotate {
            from { filter: hue-rotate(0deg); }
            to { filter: hue-rotate(360deg); }
        }

        .nav-links {
            display: flex;
            gap: 3rem;
        }

        .nav-links a {
            color: var(--text-light);
            text-decoration: none;
            font-weight: 600;
            padding: 0.5rem 1rem;
            border: 2px solid transparent;
            border-radius: 8px;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .nav-links a::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(188, 19, 254, 0.4), transparent);
            transition: left 0.5s ease;
        }

        .nav-links a:hover::before {
            left: 100%;
        }

        .nav-links a:hover {
            border-color: var(--neon-purple);
            box-shadow: 0 0 20px rgba(188, 19, 254, 0.3);
            color: var(--neon-blue);
        }

        .hero {
            margin-top: 120px;
            text-align: center;
            padding: 6rem 0;
            position: relative;
        }

        .hero::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 600px;
            height: 600px;
            background: radial-gradient(circle, rgba(188, 19, 254, 0.15) 0%, transparent 70%);
            z-index: -1;
        }

        .hero h1 {
            font-size: 4.5rem;
            margin-bottom: 2rem;
            background: linear-gradient(45deg, var(--neon-purple), var(--neon-blue), var(--neon-pink));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 0 0 50px rgba(188, 19, 254, 0.5);
            animation: text-glow 2s ease-in-out infinite alternate;
        }

        @keyframes text-glow {
            from { text-shadow: 0 0 20px rgba(188, 19, 254, 0.5), 0 0 30px rgba(0, 255, 255, 0.3); }
            to { text-shadow: 0 0 30px rgba(188, 19, 254, 0.8), 0 0 40px rgba(0, 255, 255, 0.5), 0 0 50px rgba(255, 0, 255, 0.3); }
        }

        .hero p {
            font-size: 1.4rem;
            color: var(--text-gray);
            max-width: 700px;
            margin: 0 auto 3rem;
            line-height: 1.8;
        }

        .cta-button {
            display: inline-block;
            padding: 1.2rem 3rem;
            font-size: 1.2rem;
            font-weight: 700;
            text-decoration: none;
            color: var(--text-light);
            background: linear-gradient(45deg, var(--neon-purple), var(--neon-blue));
            border: none;
            border-radius: 12px;
            box-shadow: 0 0 30px rgba(188, 19, 254, 0.4);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .cta-button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: left 0.5s ease;
        }

        .cta-button:hover::before {
            left: 100%;
        }

        .cta-button:hover {
            transform: translateY(-3px);
            box-shadow: 0 0 40px rgba(188, 19, 254, 0.6);
        }

        .cards-section {
            padding: 6rem 0;
        }

        .section-title {
            text-align: center;
            font-size: 3rem;
            margin-bottom: 4rem;
            background: linear-gradient(45deg, var(--neon-blue), var(--neon-pink));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .cards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 3rem;
            margin-bottom: 6rem;
        }

        .card {
            background: rgba(26, 26, 26, 0.7);
            backdrop-filter: blur(10px);
            border: 2px solid;
            border-image: linear-gradient(45deg, var(--neon-purple), transparent, var(--neon-blue)) 1;
            border-radius: 20px;
            padding: 3rem;
            transition: all 0.4s ease;
            position: relative;
            overflow: hidden;
        }

        .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(45deg, var(--neon-purple), var(--neon-blue), var(--neon-pink));
        }

        .card:hover {
            transform: translateY(-15px) scale(1.02);
            box-shadow: 0 20px 60px rgba(188, 19, 254, 0.3);
            border-image: linear-gradient(45deg, var(--neon-purple), var(--neon-blue), var(--neon-pink)) 1;
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
        }

        .card-title {
            font-size: 1.8rem;
            font-weight: 700;
            background: linear-gradient(45deg, var(--neon-blue), var(--neon-pink));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .card-duration {
            background: linear-gradient(45deg, var(--neon-purple), var(--neon-blue));
            color: var(--dark-bg);
            padding: 0.5rem 1.2rem;
            border-radius: 25px;
            font-size: 1rem;
            font-weight: 800;
            box-shadow: 0 0 15px rgba(188, 19, 254, 0.3);
        }

        .features-list {
            list-style: none;
        }

        .features-list li {
            padding: 1rem 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            position: relative;
            padding-left: 2.5rem;
            font-size: 1.1rem;
        }

        .features-list li::before {
            content: '⚡';
            position: absolute;
            left: 0;
            color: var(--neon-blue);
            font-size: 1.2rem;
        }

        .tables-section {
            padding: 4rem 0;
        }

        .table-container {
            background: rgba(26, 26, 26, 0.7);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 3rem;
            margin-bottom: 4rem;
            border: 2px solid;
            border-image: linear-gradient(45deg, var(--neon-purple), transparent, var(--neon-blue)) 1;
            position: relative;
            overflow: hidden;
        }

        .table-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(45deg, var(--neon-purple), var(--neon-blue));
        }

        .table-title {
            color: var(--neon-blue);
            font-size: 2.2rem;
            margin-bottom: 2rem;
            text-align: center;
            font-weight: 700;
        }

        .comparison-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 2rem;
        }

        .comparison-table th {
            background: linear-gradient(45deg, rgba(188, 19, 254, 0.3), rgba(0, 255, 255, 0.3));
            color: var(--light-neon);
            padding: 1.5rem;
            text-align: left;
            border: 2px solid rgba(188, 19, 254, 0.3);
            font-size: 1.1rem;
            font-weight: 700;
        }

        .comparison-table td {
            padding: 1.5rem;
            border: 2px solid rgba(188, 19, 254, 0.2);
            color: var(--text-gray);
            font-size: 1rem;
            line-height: 1.6;
        }

        .comparison-table tr:hover {
            background: rgba(188, 19, 254, 0.1);
        }

        .learning-table {
            width: 100%;
            border-collapse: collapse;
        }

        .learning-table th {
            background: linear-gradient(45deg, rgba(188, 19, 254, 0.4), rgba(0, 255, 255, 0.4));
            color: var(--light-neon);
            padding: 1.5rem;
            text-align: left;
            border: 2px solid rgba(188, 19, 254, 0.4);
            font-weight: 700;
            font-size: 1.1rem;
        }

        .learning-table td {
            padding: 1.5rem;
            border: 2px solid rgba(188, 19, 254, 0.3);
            color: var(--text-gray);
            font-size: 1rem;
        }

        .learning-table tr:nth-child(even) {
            background: rgba(188, 19, 254, 0.08);
        }

        .learning-table tr:hover {
            background: rgba(188, 19, 254, 0.15);
        }

        footer {
            background: var(--darker-bg);
            border-top: 3px solid transparent;
            border-image: linear-gradient(45deg, var(--neon-purple), var(--neon-blue)) 1;
            padding: 4rem 0 2rem;
            margin-top: 6rem;
        }

        .footer-content {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 3rem;
            margin-bottom: 3rem;
        }

        .footer-section h3 {
            color: var(--neon-blue);
            margin-bottom: 1.5rem;
            font-size: 1.4rem;
            font-weight: 700;
        }

        .footer-section p, .footer-section a {
            color: var(--text-gray);
            text-decoration: none;
            transition: all 0.3s ease;
            line-height: 1.8;
        }

        .footer-section a:hover {
            color: var(--neon-blue);
            text-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
        }

        .copyright {
            text-align: center;
            padding-top: 3rem;
            border-top: 2px solid rgba(188, 19, 254, 0.3);
            color: var(--text-gray);
            font-size: 1rem;
        }

        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-20px); }
        }

        .floating {
            animation: float 3s ease-in-out infinite;
        }

        @media (max-width: 768px) {
            .nav-container {
                flex-direction: column;
                gap: 1.5rem;
            }

            .hero h1 {
                font-size: 3rem;
            }

            .cards-grid {
                grid-template-columns: 1fr;
            }

            .table-container {
                padding: 2rem 1rem;
                overflow-x: auto;
            }
        }

        .telegram-section {
            text-align: center;
            padding: 4rem 0;
            background: rgba(188, 19, 254, 0.05);
            border-radius: 30px;
            margin: 4rem 0;
            border: 2px solid transparent;
            border-image: linear-gradient(45deg, var(--neon-purple), var(--neon-blue)) 1;
        }

        .telegram-button {
            display: inline-block;
            padding: 1.5rem 3rem;
            font-size: 1.3rem;
            font-weight: 700;
            text-decoration: none;
            color: white;
            background: linear-gradient(45deg, #0088cc, #00aced);
            border-radius: 15px;
            box-shadow: 0 0 30px rgba(0, 136, 204, 0.4);
            transition: all 0.3s ease;
            margin-top: 2rem;
        }

        .telegram-button:hover {
            transform: translateY(-3px);
            box-shadow: 0 0 40px rgba(0, 136, 204, 0.6);
        }
    </style>
</head>
<body>
    <div class="cyber-grid"></div>
    
    <header>
        <div class="container">
            <div class="nav-container">
                <div class="logo floating">🚀 DH Learning</div>
                <nav class="nav-links">
                    <a href="#python">🐍 Python</a>
                    <a href="#nodejs">💚 Node.js</a>
                    <a href="#comparison">🔥 Сравнение</a>
                    <a href="#telegram">🤖 Бот</a>
                </nav>
            </div>
        </div>
    </header>

    <section class="hero">
        <div class="container">
            <h1>🚀 ПРОКАЧАЙСЯ В ПРОГРАММИРОВАНИИ</h1>
            <p>💥 Полное руководство по изучению Python и Node.js. От полного нуля до профессионального уровня за 6 месяцев. ПИСАТЬ КОД КАК БОГ! ⚡</p>
            <a href="#courses" class="cta-button">🎯 НАЧАТЬ ПИСАТЬ КОД</a>
        </div>
    </section>

    <section id="telegram" class="telegram-section">
        <div class="container">
            <h2 class="section-title">🤖 ТЕЛЕГРАМ БОТ</h2>
            <p style="font-size: 1.3rem; color: var(--text-gray); margin-bottom: 2rem;">
                💫 Присоединяйся к нашему боту! Он будет каждый день ЕБАШИТЬ тебя заданиями<br>
                ⚡ Без компромиссов! Без отсрочек! Только ХАРДКОР! 🚀
            </p>
            <a href="https://t.me/DH_Learningbot" class="telegram-button" target="_blank">
                🚀 ПРИСОЕДИНИТЬСЯ К БОТУ
            </a>
        </div>
    </section>

    <section id="courses" class="cards-section">
        <div class="container">
            <h2 class="section-title">🎯 ВЫБЕРИ СВОЙ ПЛАН АТАКИ</h2>
            <div class="cards-grid">
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">🐍 Python - 7 дней</h3>
                        <span class="card-duration">⚡ ЭКСПРЕСС</span>
                    </div>
                    <ul class="features-list">
                        <li>🚀 Базовый синтаксис и типы данных</li>
                        <li>💥 Простые скрипты и автоматизация</li>
                        <li>🔥 Работа с файлами и библиотеками</li>
                        <li>⚡ Основы отладки и обработки ошибок</li>
                    </ul>
                </div>

                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">🐍 Python - 1 месяц</h3>
                        <span class="card-duration">🔥 БАЗОВЫЙ</span>
                    </div>
                    <ul class="features-list">
                        <li>🚀 Углубленное изучение конструкций</li>
                        <li>💥 Объектно-ориентированное программирование</li>
                        <li>⚡ Работа с API и базами данных</li>
                        <li>🔥 Создание веб-приложений на Flask</li>
                    </ul>
                </div>

                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">🐍 Python - 6 месяцев</h3>
                        <span class="card-duration">🎯 ПРОДВИНУТЫЙ</span>
                    </div>
                    <ul class="features-list">
                        <li>🚀 Продвинутые темы и фреймворки</li>
                        <li>💥 Django, FastAPI, Data Science</li>
                        <li>⚡ Архитектура и паттерны проектирования</li>
                        <li>🔥 Подготовка к коммерческой разработке</li>
                    </ul>
                </div>

                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">💚 Node.js - 7 дней</h3>
                        <span class="card-duration">⚡ ЭКСПРЕСС</span>
                    </div>
                    <ul class="features-list">
                        <li>🚀 Основы Node.js и npm</li>
                        <li>💥 Создание первого сервера</li>
                        <li>⚡ Работа с Express.js</li>
                        <li>🔥 Простое REST API</li>
                    </ul>
                </div>

                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">💚 Node.js - 1 месяц</h3>
                        <span class="card-duration">🔥 БАЗОВЫЙ</span>
                    </div>
                    <ul class="features-list">
                        <li>🚀 Асинхронное программирование</li>
                        <li>💥 Работа с базами данных</li>
                        <li>⚡ Аутентификация и безопасность</li>
                        <li>🔥 Создание полноценных API</li>
                    </ul>
                </div>

                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">💚 Node.js - 6 месяцев</h3>
                        <span class="card-duration">🎯 ПРОДВИНУТЫЙ</span>
                    </div>
                    <ul class="features-list">
                        <li>🚀 Архитектура приложений</li>
                        <li>💥 GraphQL, WebSockets, Microservices</li>
                        <li>⚡ Оптимизация и безопасность</li>
                        <li>🔥 DevOps и развертывание</li>
                    </ul>
                </div>
            </div>
        </div>
    </section>

    <section id="comparison" class="tables-section">
        <div class="container">
            <h2 class="section-title">⚡ СРАВНЕНИЕ ПЛАНОВ АТАКИ</h2>
            <div class="table-container">
                <h3 class="table-title">🎯 ЦЕЛИ И РЕЗУЛЬТАТЫ</h3>
                <table class="comparison-table">
                    <thead>
                        <tr>
                            <th>⏱️ Срок обучения</th>
                            <th>🐍 Для Python...</th>
                            <th>💚 Для Node.js...</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>⚡ 7 дней</strong></td>
                            <td>• 🚀 Понять базовый синтаксис<br>• 💥 Написать первые простые скрипты</td>
                            <td>• 🚀 Понять основы и создать первый веб-сервер</td>
                        </tr>
                        <tr>
                            <td><strong>🔥 1 месяц</strong></td>
                            <td>• 🚀 Освоить ключевые конструкции языка<br>• 💥 Автоматизировать задачи с помощью скриптов</td>
                            <td>• 🚀 Научиться создавать REST API с Express.js<br>• 💥 Подключить базу данных</td>
                        </tr>
                        <tr>
                            <td><strong>🎯 6 месяцев</strong></td>
                            <td>• 🚀 Освоить продвинутые темы и фреймворки<br>• 💥 Научиться писать промышленный код</td>
                            <td>• 🚀 Освоить архитектуру, безопасность, GraphQL<br>• 💥 Развертывание и поддержка приложений</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </section>

    <section id="python" class="tables-section">
        <div class="container">
            <h2 class="section-title">🐍 ПОЛНЫЙ ПЛАН АТАКИ PYTHON</h2>
            
            <div class="table-container">
                <h3 class="table-title">🐍 Python за 7 дней (ХАРДКОР МОДЕ)</h3>
                <table class="learning-table">
                    <thead>
                        <tr>
                            <th>📅 День</th>
                            <th>🎯 Основные темы</th>
                            <th>💥 Практический проект</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>🚀 День 1</td>
                            <td>Установка Python, переменные, типы данных, вывод данных</td>
                            <td>Скрипт с выводом информации о пользователе</td>
                        </tr>
                        <tr>
                            <td>⚡ День 2</td>
                            <td>Условные операторы, логические операции</td>
                            <td>Скрипт с реакцией на разные условия</td>
                        </tr>
                        <tr>
                            <td>🔥 День 3</td>
                            <td>Циклы, генераторы списков</td>
                            <td>Обработка списков и фильтрация данных</td>
                        </tr>
                        <tr>
                            <td>💥 День 4</td>
                            <td>Функции, область видимости</td>
                            <td>Рефакторинг кода с использованием функций</td>
                        </tr>
                        <tr>
                            <td>🚀 День 5</td>
                            <td>Работа с файлами</td>
                            <td>Простой дневник с записью и чтением заметок</td>
                        </tr>
                        <tr>
                            <td>⚡ День 6</td>
                            <td>Библиотеки, установка pip, requests</td>
                            <td>Скрипт для получения данных с API</td>
                        </tr>
                        <tr>
                            <td>🎯 День 7</td>
                            <td>Отладка, обработка исключений</td>
                            <td>Завершение проекта с обработкой ошибок</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="table-container">
                <h3 class="table-title">🐍 Python за 1 месяц (БАЗОВЫЙ УРОВЕНЬ)</h3>
                <table class="learning-table">
                    <thead>
                        <tr>
                            <th>📅 Неделя</th>
                            <th>🎯 Основные темы</th>
                            <th>💥 Практический проект</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>🚀 Неделя 1</td>
                            <td>Основы языка, структуры данных, функции</td>
                            <td>Телеграм-бот для уведомлений</td>
                        </tr>
                        <tr>
                            <td>⚡ Неделя 2</td>
                            <td>ООП: классы, объекты, наследование</td>
                            <td>Текстовая игра с использованием классов</td>
                        </tr>
                        <tr>
                            <td>🔥 Неделя 3</td>
                            <td>Работа с данными, API, основы SQL</td>
                            <td>Скрипт для сбора данных с веб-сайтов</td>
                        </tr>
                        <tr>
                            <td>💥 Неделя 4</td>
                            <td>Веб-разработка: Flask/FastAPI</td>
                            <td>Простое REST API для списка задач</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="table-container">
                <h3 class="table-title">🐍 Python за 6 месяцев (ПРОДВИНУТЫЙ УРОВЕНЬ)</h3>
                <table class="learning-table">
                    <thead>
                        <tr>
                            <th>📅 Месяц</th>
                            <th>🎯 Основные темы</th>
                            <th>💥 Ключевые проекты</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>🚀 1-2</td>
                            <td>Продвинутые возможности языка, декораторы, генераторы</td>
                            <td>Скрипты с использованием продвинутых возможностей</td>
                        </tr>
                        <tr>
                            <td>⚡ 3</td>
                            <td>ООП, алгоритмы, тестирование (pytest)</td>
                            <td>Реализация алгоритмов, написание тестов</td>
                        </tr>
                        <tr>
                            <td>🔥 4</td>
                            <td>Веб-разработка: Django, ORM, базы данных</td>
                            <td>Новостной портал или блог на Django</td>
                        </tr>
                        <tr>
                            <td>💥 5</td>
                            <td>REST API: DRF, FastAPI, аутентификация</td>
                            <td>REST API для сайта объявлений</td>
                        </tr>
                        <tr>
                            <td>🎯 6</td>
                            <td>Docker, развертывание, CI/CD</td>
                            <td>Завершенный и развернутый проект</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </section>

    <section id="nodejs" class="tables-section">
        <div class="container">
            <h2 class="section-title">💚 ПОЛНЫЙ ПЛАН АТАКИ NODE.JS</h2>
            
            <div class="table-container">
                <h3 class="table-title">💚 Node.js за 7 дней (ХАРДКОР МОДЕ)</h3>
                <table class="learning-table">
                    <thead>
                        <tr>
                            <th>📅 День</th>
                            <th>🎯 Основные темы</th>
                            <th>💥 Практический проект</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>🚀 День 1</td>
                            <td>Установка Node.js, npm, модульная система</td>
                            <td>Скрипт с выводом разных типов данных</td>
                        </tr>
                        <tr>
                            <td>⚡ День 2</td>
                            <td>Асинхронность, работа с файлами</td>
                            <td>Скрипт для чтения и обработки файлов</td>
                        </tr>
                        <tr>
                            <td>🔥 День 3</td>
                            <td>Создание веб-сервера (http модуль)</td>
                            <td>Сервер "Hello World"</td>
                        </tr>
                        <tr>
                            <td>💥 День 4</td>
                            <td>Express.js, маршрутизация</td>
                            <td>Простое приложение с маршрутами</td>
                        </tr>
                        <tr>
                            <td>🚀 День 5</td>
                            <td>Обработка запросов, middleware</td>
                            <td>Форма с обработкой данных</td>
                        </tr>
                        <tr>
                            <td>⚡ День 6</td>
                            <td>Базы данных, подключение SQLite/JSON</td>
                            <td>API для получения данных из БД</td>
                        </tr>
                        <tr>
                            <td>🎯 День 7</td>
                            <td>Объединение знаний, CRUD API</td>
                            <td>Бэкенд для блога или списка дел</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="table-container">
                <h3 class="table-title">💚 Node.js за 1 месяц (БАЗОВЫЙ УРОВЕНЬ)</h3>
                <table class="learning-table">
                    <thead>
                        <tr>
                            <th>📅 Неделя</th>
                            <th>🎯 Основные темы</th>
                            <th>💥 Практический проект</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>🚀 Неделя 1</td>
                            <td>Основы платформы, событийный цикл, npm</td>
                            <td>Консольное приложение для работы с файлами</td>
                        </tr>
                        <tr>
                            <td>⚡ Неделя 2</td>
                            <td>Express.js, REST архитектура, CRUD</td>
                            <td>REST API для управления сущностями</td>
                        </tr>
                        <tr>
                            <td>🔥 Неделя 3</td>
                            <td>Базы данных: MongoDB/PostgreSQL, ORM</td>
                            <td>Интеграция БД в проект</td>
                        </tr>
                        <tr>
                            <td>💥 Неделя 4</td>
                            <td>Аутентификация, безопасность, JWT</td>
                            <td>Регистрация и аутентификация в API</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="table-container">
                <h3 class="table-title">💚 Node.js за 6 месяцев (ПРОДВИНУТЫЙ УРОВЕНЬ)</h3>
                <table class="learning-table">
                    <thead>
                        <tr>
                            <th>📅 Месяц</th>
                            <th>🎯 Основные темы</th>
                            <th>💥 Ключевые проекты</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>🚀 1-2</td>
                            <td>Event Loop, потоки, кэширование, производительность</td>
                            <td>Высокопроизводительный скрипт для обработки данных</td>
                        </tr>
                        <tr>
                            <td>⚡ 3</td>
                            <td>Паттерны проектирования, тестирование (Jest)</td>
                            <td>Написание тестов для API</td>
                        </tr>
                        <tr>
                            <td>🔥 4</td>
                            <td>GraphQL, WebSockets (Socket.io)</td>
                            <td>Чат-приложение в реальном времени</td>
                        </tr>
                        <tr>
                            <td>💥 5</td>
                            <td>Docker, развертывание, облачные платформы</td>
                            <td>Развернутый проект в облаке</td>
                        </tr>
                        <tr>
                            <td>🎯 6</td>
                            <td>Fullstack разработка, безопасность, оптимизация</td>
                            <td>Полноценное fullstack приложение</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </section>

    <footer>
        <div class="container">
            <div class="footer-content">
                <div class="footer-section">
                    <h3></h3>
                    <p></p>
                </div>
                <div class="footer-section">
                    <h3>🚀 DH Learning</h3>
                    <p>Современная платформа для обучения программированию. От начинающего до ПРОФЕССИОНАЛА. 💥</p>
                </div>
                <div class="footer-section">
                    <h3></h3>
                    <p></p>
                    <p></p>
                </div>
            </div>
            <div class="copyright">
                <p>© 2025-2026 Dark Heavens Corporate. Все права защищены.</p>
            </div>
        </div>
    </footer>

    <script>
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, observerOptions);

        document.querySelectorAll('.card, .table-container').forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(30px)';
            el.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
            observer.observe(el);
        });

        window.addEventListener('scroll', () => {
            const header = document.querySelector('header');
            if (window.scrollY > 100) {
                header.style.boxShadow = '0 5px 30px rgba(188, 19, 254, 0.4)';
            } else {
                header.style.boxShadow = 'none';
            }
        });

        document.addEventListener('mousemove', (e) => {
            const grid = document.querySelector('.cyber-grid');
            const x = e.clientX / window.innerWidth;
            const y = e.clientY / window.innerHeight;
            
            grid.style.transform = `translate(${x * 20}px, ${y * 20}px)`;
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    print("🚀 Запускаю DH Learning Website...")
    app.run(host='0.0.0.0', port=5000, debug=False)
