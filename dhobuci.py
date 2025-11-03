from flask import Flask, render_template_string
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils import executor
import threading
import os
import json
from datetime import datetime, timedelta

# ========== FLASK SITE ==========
app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 DH Learning - Прокачка в Питоне и Node.js</title>
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

        /* Header Styles */
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

        /* Hero Section */
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

        /* Cards Section */
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

        /* Tables Section */
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

        /* Footer */
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

        /* Animations */
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-20px); }
        }

        .floating {
            animation: float 3s ease-in-out infinite;
        }

        /* Responsive */
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
    
    <!-- Header -->
    <header>
        <div class="container">
            <div class="nav-container">
                <div class="logo floating">🚀 DH Learning</div>
                <nav class="nav-links">
                    <a href="#python">🐍 Python</a>
                    <a href="#nodejs">💚 Node.js</a>
                    <a href="#comparison">🔥 Сравнение</a>
                    <a href="#tables">📊 Планы</a>
                    <a href="#telegram">🤖 Бот</a>
                </nav>
            </div>
        </div>
    </header>

    <!-- Hero Section -->
    <section class="hero">
        <div class="container">
            <h1>🚀 ПРОКАЧАЙСЯ В ПРОГРАММИРОВАНИИ</h1>
            <p>💥 Полное руководство по изучению Python и Node.js. От полного нуля до профессионального уровня за 6 месяцев. ЕБАШЬ КОД КАК БОГ! ⚡</p>
            <a href="#courses" class="cta-button">🎯 НАЧАТЬ ЕБАШИТЬ КОД</a>
        </div>
    </section>

    <!-- Telegram Section -->
    <section id="telegram" class="telegram-section">
        <div class="container">
            <h2 class="section-title">🤖 ТЕЛЕГРАМ БОТ</h2>
            <p style="font-size: 1.3rem; color: var(--text-gray); margin-bottom: 2rem;">
                💫 Присоединяйся к нашему боту! Он будет каждый день ЕБАШИТЬ тебя заданиями<br>
                ⚡ Без компромиссов! Без отсрочек! Только ХАРДКОР! 🚀
            </p>
            <a href="https://t.me/dh_learning_bot" class="telegram-button" target="_blank">
                🚀 ПРИСОЕДИНИТЬСЯ К БОТУ
            </a>
        </div>
    </section>

    <!-- Overview Cards -->
    <section id="courses" class="cards-section">
        <div class="container">
            <h2 class="section-title">🎯 ВЫБЕРИ СВОЙ ПЛАН АТАКИ</h2>
            <div class="cards-grid">
                <!-- Python Cards -->
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

                <!-- Node.js Cards -->
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

    <!-- Comparison Table -->
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

    <!-- Python Learning Tables -->
    <section id="python" class="tables-section">
        <div class="container">
            <h2 class="section-title">🐍 ПОЛНЫЙ ПЛАН АТАКИ PYTHON</h2>
            
            <!-- Python 7 дней -->
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
        </div>
    </section>

    <!-- Footer -->
    <footer>
        <div class="container">
            <div class="footer-content">
                <div class="footer-section">
                    <h3>🚀 DH Learning</h3>
                    <p>Современная платформа для обучения программированию. От начинающего до ПРОФЕССИОНАЛА. 💥</p>
                </div>
                <div class="footer-section">
                    <h3>🛠️ Технологии</h3>
                    <p>Python 🐍 • Node.js 💚 • JavaScript • Flask • Express • Django • React ⚡</p>
                </div>
                <div class="footer-section">
                    <h3>📞 Контакты</h3>
                    <p>👨‍💻 Разработчик: @haker_one</p>
                    <p>🛠️ Техподдержка: @dark_heavens_support_bot</p>
                </div>
            </div>
            <div class="copyright">
                <p>© 2025-2026 Dark Heavens Corporate. Все права защищены. 🚀</p>
            </div>
        </div>
    </footer>

    <script>
        // Smooth scrolling for navigation links
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

        // Add animation to cards on scroll
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

        // Observe all cards and tables
        document.querySelectorAll('.card, .table-container').forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(30px)';
            el.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
            observer.observe(el);
        });

        // Add glow effect to header on scroll
        window.addEventListener('scroll', () => {
            const header = document.querySelector('header');
            if (window.scrollY > 100) {
                header.style.boxShadow = '0 5px 30px rgba(188, 19, 254, 0.4)';
            } else {
                header.style.boxShadow = 'none';
            }
        });

        // Cyber effects
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

# ========== TELEGRAM BOT ==========
# Конфигурация бота
BOT_TOKEN = "8524355119:AAExHf5r0GZQxXiB58S95nOaqdS9DfyfYWI"  # Замени на свой токен
ADMIN_ID = 7215210750  # Замени на свой ID

# Хранилище данных пользователей
user_data = {}

# Планы обучения с ежедневными заданиями
learning_plans = {
    "python_7": {
        "name": "🐍 Python за 7 дней",
        "days": {
            1: "🚀 ДЕНЬ 1: Установи Python и напиши первый скрипт! 💥\n\nЗадание:\n1. Установи Python с python.org\n2. Напиши скрипт который выводит твое имя и возраст\n3. Запусти его через терминал\n\n⚡ ДЕЛАЙ СЕЙЧАС! Не откладывай!",
            2: "🔥 ДЕНЬ 2: Условия и логика! 🧠\n\nЗадание:\n1. Напиши скрипт который проверяет твой возраст\n2. Если больше 18 - 'Доступ разрешен', иначе - 'Доступ запрещен'\n3. Добавь проверку на пустой ввод\n\n🎯 ВПЕРЕД КОДИТЬ!",
            3: "⚡ ДЕНЬ 3: Циклы и списки! 🔄\n\nЗадание:\n1. Создай список из 5 чисел\n2. Напиши цикл который выводит каждый элемент\n3. Сделай сумму всех чисел в списке\n\n💥 РАБОТАЙ БЕЗ ОСТАНОВКИ!",
            4: "💫 ДЕНЬ 4: Функции - твой новый суперсила! 🦸\n\nЗадание:\n1. Создай функцию для расчета площади круга\n2. Функцию для проверки четности числа\n3. Вызови их с разными параметрами\n\n🚀 КОДИМ ДАЛЬШЕ!",
            5: "🎯 ДЕНЬ 5: Работа с файлами! 📁\n\nЗадание:\n1. Создай текстовый файл\n2. Запиши в него несколько строк\n3. Прочитай и выведи содержимое\n\n⚡ НЕ ОСТАНАВЛИВАЙСЯ!",
            6: "🚀 ДЕНЬ 6: Библиотеки и API! 🌐\n\nЗадание:\n1. Установи библиотеку requests через pip\n2. Сделай запрос к какому-нибудь публичному API\n3. Обработай и выведи результат\n\n💥 ТЫ УЖЕ ПРОГРАММИСТ!",
            7: "🎉 ДЕНЬ 7: ФИНАЛ! Завершающий проект! 🏆\n\nЗадание:\n1. Создай простой телеграм бот\n2. Или напиши парсер сайта\n3. Или сделай автоматизацию для себя\n\n🔥 ТЫ СДЕЛАЛ ЭТО! МОЛОДЕЦ!"
        }
    },
    "nodejs_7": {
        "name": "💚 Node.js за 7 дней",
        "days": {
            1: "🚀 ДЕНЬ 1: Установка и первый сервер! 💥\n\nЗадание:\n1. Установи Node.js с nodejs.org\n2. Создай файл server.js\n3. Запусти простой HTTP сервер\n\n⚡ ВПЕРЕД К СЕРВЕРАМ!",
            2: "🔥 ДЕНЬ 2: Модули и NPM! 📦\n\nЗадание:\n1. Изучи модульную систему\n2. Установи через npm библиотеку express\n3. Создай простой роут\n\n🎯 КОДИ СЕРВЕРА!",
            3: "⚡ ДЕНЬ 3: Express.js - твой фреймворк! 🛠️\n\nЗадание:\n1. Настрой базовое Express приложение\n2. Создай несколько GET роутов\n3. Добавь простой HTML шаблон\n\n💥 СЕРВЕРА ЖДУТ!",
            4: "💫 ДЕНЬ 4: Middleware и POST запросы! 📨\n\nЗадание:\n1. Добавь middleware для логирования\n2. Создай форму и обрабатывай POST\n3. Научись работать с body парсером\n\n🚀 ДАЛЬШЕ В БЭКЕНД!",
            5: "🎯 ДЕНЬ 5: Базы данных! 🗄️\n\nЗадание:\n1. Подключи MongoDB или SQLite\n2. Создай простую модель\n3. Реализуй CRUD операции\n\n⚡ БД ТЕБЯ ЖДУТ!",
            6: "🚀 ДЕНЬ 6: API и аутентификация! 🔐\n\nЗадание:\n1. Создай REST API\n2. Добавь JWT аутентификацию\n3. Сделай защищенные роуты\n\n💥 СТАНЬ ФУЛЛСТЕК!",
            7: "🎉 ДЕНЬ 7: ДЕПЛОЙ И ФИНАЛ! ☁️\n\nЗадание:\n1. Задеплой приложение на Heroku\n2. Настрой домен и SSL\n3. Протестируй все endpoints\n\n🔥 ТЫ СТАЛ NODE.js РАЗРАБОТЧИКОМ!"
        }
    }
}

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Клавиатуры
def get_main_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🐍 Python курсы", callback_data="python_courses"),
        InlineKeyboardButton("💚 Node.js курсы", callback_data="nodejs_courses")
    )
    keyboard.add(
        InlineKeyboardButton("👨‍💻 Разработчик", url="https://t.me/haker_one"),
        InlineKeyboardButton("🛠️ Техподдержка", url="https://t.me/dark_heavens_support_bot")
    )
    keyboard.add(
        InlineKeyboardButton("🎯 Мой прогресс", callback_data="my_progress"),
        InlineKeyboardButton("🚀 Сегодняшнее задание", callback_data="todays_task")
    )
    return keyboard

def get_python_courses_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🐍 Python за 7 дней", callback_data="start_python_7"))
    keyboard.add(InlineKeyboardButton("🐍 Python за 1 месяц", callback_data="start_python_30"))
    keyboard.add(InlineKeyboardButton("🐍 Python за 6 месяцев", callback_data="start_python_180"))
    keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_main"))
    return keyboard

def get_nodejs_courses_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("💚 Node.js за 7 дней", callback_data="start_nodejs_7"))
    keyboard.add(InlineKeyboardButton("💚 Node.js за 1 месяц", callback_data="start_nodejs_30"))
    keyboard.add(InlineKeyboardButton("💚 Node.js за 6 месяцев", callback_data="start_nodejs_180"))
    keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_main"))
    return keyboard

def get_day_navigation_keyboard(user_id, course_type):
    user = user_data.get(user_id, {})
    current_day = user.get('current_day', 1)
    total_days = 7  # Для демо используем 7 дней

    keyboard = InlineKeyboardMarkup()
    if current_day > 1:
        keyboard.add(InlineKeyboardButton("⬅️ Предыдущий день", callback_data=f"prev_day_{course_type}"))

    if current_day < total_days:
        keyboard.add(InlineKeyboardButton("➡️ Следующий день", callback_data=f"next_day_{course_type}"))
    else:
        keyboard.add(InlineKeyboardButton("🎉 Завершить курс!", callback_data="finish_course"))

    keyboard.add(InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main"))
    return keyboard

# Обработчики сообщений
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {
            'current_course': None,
            'current_day': 1,
            'start_date': datetime.now().strftime("%Y-%m-%d"),
            'completed_days': []
        }

    welcome_text = """
🚀 ДОБРО ПОЖАЛОВАТЬ В DH LEARNING! 💥

Я твой личный тренер по программированию! 
Каждый день я буду ЕБАШИТЬ тебя новыми заданиями! ⚡

🎯 Выбери курс и начинай ЕБАШИТЬ код прямо сейчас!
💥 Никаких отсрочек! Только ХАРДКОР! 🚀
    """

    await message.answer(welcome_text, reply_markup=get_main_keyboard())

@dp.message_handler(commands=['today'])
async def send_todays_task(message: types.Message):
    user_id = message.from_user.id
    user = user_data.get(user_id, {})

    if not user.get('current_course'):
        await message.answer("⚠️ Сначала выбери курс в главном меню! 🎯")
        return

    course_type = user['current_course']
    current_day = user['current_day']

    if course_type in learning_plans and current_day in learning_plans[course_type]['days']:
        task = learning_plans[course_type]['days'][current_day]
        await message.answer(f"🎯 ЗАДАНИЕ НА СЕГОДНЯ:\n\n{task}",
                             reply_markup=get_day_navigation_keyboard(user_id, course_type))
    else:
        await message.answer("🎉 Ты завершил все задания курса! МОЛОДЕЦ! 🏆")

@dp.callback_query_handler(lambda c: c.data == 'python_courses')
async def python_courses(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id,
                           "🐍 ВЫБЕРИ СВОЙ PYTHON КУРС:\n\n"
                           "⚡ 7 дней - экспресс прокачка\n"
                           "🔥 1 месяц - базовая подготовка\n"
                           "🎯 6 месяцев - профессиональный уровень",
                           reply_markup=get_python_courses_keyboard())

@dp.callback_query_handler(lambda c: c.data == 'nodejs_courses')
async def nodejs_courses(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id,
                           "💚 ВЫБЕРИ СВОЙ NODE.JS КУРС:\n\n"
                           "⚡ 7 дней - экспресс прокачка\n"
                           "🔥 1 месяц - базовая подготовка\n"
                           "🎯 6 месяцев - профессиональный уровень",
                           reply_markup=get_nodejs_courses_keyboard())

@dp.callback_query_handler(lambda c: c.data.startswith('start_'))
async def start_course(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user_id = callback_query.from_user.id
    course_type = callback_query.data.replace('start_', '')

    user_data[user_id]['current_course'] = course_type
    user_data[user_id]['current_day'] = 1
    user_data[user_id]['start_date'] = datetime.now().strftime("%Y-%m-%d")

    course_name = learning_plans.get(course_type, {}).get('name', 'курс')

    await bot.send_message(user_id,
                           f"🚀 ОТЛИЧНЫЙ ВЫБОР! НАЧИНАЕМ {course_name.upper()}! 💥\n\n"
                           f"⚡ С сегодняшнего дня я буду ЕБАШИТЬ тебя заданиями!\n"
                           f"🔥 Никаких поблажек! Работаем на результат! 🎯\n\n"
                           f"ПЕРВОЕ ЗАДАНИЕ ЖДЕТ ТЕБЯ НИЖЕ! ⬇️")

    # Отправляем первое задание
    if course_type in learning_plans:
        first_task = learning_plans[course_type]['days'][1]
        await bot.send_message(user_id, first_task,
                               reply_markup=get_day_navigation_keyboard(user_id, course_type))

@dp.callback_query_handler(lambda c: c.data.startswith('next_day_'))
async def next_day(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user_id = callback_query.from_user.id
    course_type = callback_query.data.replace('next_day_', '')

    user = user_data.get(user_id, {})
    current_day = user.get('current_day', 1)

    if current_day < 7:  # Максимум 7 дней для демо
        user_data[user_id]['current_day'] = current_day + 1
        user_data[user_id]['completed_days'] = user.get('completed_days', []) + [current_day]

        next_task = learning_plans[course_type]['days'][current_day + 1]

        motivation_texts = [
            "🚀 ОТЛИЧНО ПРОДВИГАЕШЬСЯ! ДАВАЙ ДАЛЬШЕ! 💥",
            "🔥 ТЫ НЕОСТАНОВИМ! ПРОДОЛЖАЕМ ЕБАШИТЬ! ⚡",
            "🎯 ВПЕРЕД К ПОБЕДЕ! СЛЕДУЮЩЕЕ ЗАДАНИЕ! 🚀",
            "💫 ТЫ РВЕШЬ! НЕ СБАВЛЯЙ ТЕМП! 🔥"
        ]

        import random
        motivation = random.choice(motivation_texts)

        await bot.send_message(user_id, f"{motivation}\n\n{next_task}",
                               reply_markup=get_day_navigation_keyboard(user_id, course_type))

@dp.callback_query_handler(lambda c: c.data.startswith('prev_day_'))
async def prev_day(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user_id = callback_query.from_user.id
    course_type = callback_query.data.replace('prev_day_', '')

    user = user_data.get(user_id, {})
    current_day = user.get('current_day', 1)

    if current_day > 1:
        user_data[user_id]['current_day'] = current_day - 1
        prev_task = learning_plans[course_type]['days'][current_day - 1]

        await bot.send_message(user_id, f"🔄 ПОВТОРЕНИЕ - МАТЬ УЧЕНИЯ! 🔄\n\n{prev_task}",
                               reply_markup=get_day_navigation_keyboard(user_id, course_type))

@dp.callback_query_handler(lambda c: c.data == 'todays_task')
async def todays_task(callback_query: types.CallbackQuery):
    await send_todays_task(callback_query.message)

@dp.callback_query_handler(lambda c: c.data == 'my_progress')
async def my_progress(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user_id = callback_query.from_user.id
    user = user_data.get(user_id, {})

    if not user.get('current_course'):
        await bot.send_message(user_id, "⚠️ Ты еще не начал ни одного курса! Выбери курс в главном меню! 🎯")
        return

    course_type = user['current_course']
    current_day = user.get('current_day', 1)
    completed_days = user.get('completed_days', [])
    total_days = 7  # Для демо

    progress = len(completed_days)
    percentage = (progress / total_days) * 100

    progress_bar = "🟢" * progress + "⚪" * (total_days - progress)

    course_name = learning_plans.get(course_type, {}).get('name', 'курс')

    progress_text = f"""
📊 ТВОЙ ПРОГРЕСС В {course_name.upper()}:

{progress_bar}
🎯 Пройдено дней: {progress}/{total_days}
📈 Прогресс: {percentage:.1f}%
🚀 Текущий день: {current_day}
💪 Начал: {user.get('start_date', 'Неизвестно')}

⚡ ПРОДОЛЖАЕМ ЕБАШИТЬ! НИКАКИХ ПОБЛАЖЕК! 🔥
    """

    await bot.send_message(user_id, progress_text)

@dp.callback_query_handler(lambda c: c.data == 'finish_course')
async def finish_course(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user_id = callback_query.from_user.id
    user = user_data.get(user_id, {})

    course_type = user.get('current_course')
    course_name = learning_plans.get(course_type, {}).get('name', 'курс')

    await bot.send_message(user_id,
                           f"🎉 БЛЯДЬ, ТЫ СДЕЛАЛ ЭТО! 🏆\n\n"
                           f"Ты завершил {course_name}! Это офигенно! 💥\n"
                           f"Ты доказал что можешь ЕБАШИТЬ код как настоящий программист! 🚀\n\n"
                           f"⚡ Что дальше?\n"
                           f"• Начни новый курс\n"
                           f"• Создай свой проект\n"
                           f"• Ищи работу или заказы\n\n"
                           f"Гордимся тобой! Ты крут! 🔥",
                           reply_markup=get_main_keyboard())

    # Сбрасываем курс
    user_data[user_id]['current_course'] = None
    user_data[user_id]['current_day'] = 1

@dp.callback_query_handler(lambda c: c.data == 'back_to_main')
async def back_to_main(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await send_welcome(callback_query.message)

# Функция для отправки ежедневных напоминаний
async def send_daily_reminders():
    while True:
        now = datetime.now()
        if now.hour == 9 and now.minute == 0:  # 9:00 утра
            for user_id, user_data in user_data.items():
                if user_data.get('current_course'):
                    try:
                        await bot.send_message(
                            user_id,
                            "🚀 ДОБРОЕ УТРО! ВРЕМЯ ЕБАШИТЬ КОД! 💥\n\n"
                            "⚡ Не проебывай день! Задание ждет тебя!\n"
                            "🎯 Используй /today чтобы получить задание\n\n"
                            "ДАВАЙ НАХУЙ, РАБОТАЙ! 🔥"
                        )
                    except Exception as e:
                        print(f"Не удалось отправить напоминание пользователю {user_id}: {e}")

            # Ждем 24 часа до следующей проверки
            await asyncio.sleep(60 * 60 * 24)
        else:
            await asyncio.sleep(60)  # Проверяем каждую минуту

# Запуск бота в отдельном потоке
def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Запускаем напоминания в фоне
    loop.create_task(send_daily_reminders())

    # Запускаем бота
    executor.start_polling(dp, skip_updates=True)

# Запуск Flask и бота
if __name__ == '__main__':
    print("🚀 Запускаю DH Learning...")
    print("💥 Сайт: http://localhost:5000")
    print("🤖 Бот: запускается...")

    # Запускаем бота в отдельном потоке
    import threading
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

    # Запускаем Flask
    app.run(host='0.0.0.0', port=5000, debug=False)
