#!/usr/bin/env python3
"""
Railway production bot - упрощенная версия
"""

import os
import sys
import asyncio
import sqlite3
from pathlib import Path
from loguru import logger

# Добавляем корневую директорию в PYTHONPATH
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Загружаем переменные окружения
from dotenv import load_dotenv
load_dotenv()

# Настраиваем логирование для production
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

# Состояния для FSM
class UserStates:
    waiting_for_selfie = "waiting_for_selfie"
    waiting_for_full_body = "waiting_for_full_body"
    waiting_for_clothing = "waiting_for_clothing"

def get_db_connection():
    """Получить соединение с БД"""
    db_url = os.getenv("DATABASE_URL", "sqlite:///./virtual_tryon.db")
    
    if db_url.startswith("postgres://") or db_url.startswith("postgresql://"):
        # PostgreSQL для production
        import psycopg2
        import urllib.parse as urlparse
        
        url = urlparse.urlparse(db_url)
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        return conn
    else:
        # SQLite для development
        return sqlite3.connect('virtual_tryon.db')

def init_database():
    """Инициализация базы данных"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Создаем таблицы если их нет
        if os.getenv("DATABASE_URL", "").startswith("postgres"):
            # PostgreSQL
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    telegram_id BIGINT UNIQUE NOT NULL,
                    username VARCHAR(255),
                    first_name VARCHAR(255),
                    last_name VARCHAR(255),
                    subscription_type VARCHAR(50) DEFAULT 'free',
                    generation_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_photos (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    photo_url TEXT NOT NULL,
                    photo_type VARCHAR(50) NOT NULL,
                    cloudinary_public_id VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
        else:
            # SQLite
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE NOT NULL,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    subscription_type TEXT DEFAULT 'free',
                    generation_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_photos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    photo_url TEXT NOT NULL,
                    photo_type TEXT NOT NULL,
                    cloudinary_public_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
        
        conn.commit()
        logger.info("✅ Database tables initialized")
        
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        conn.rollback()
    finally:
        conn.close()

def save_user(telegram_user):
    """Сохранить пользователя в БД"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Проверяем, есть ли пользователь
        if os.getenv("DATABASE_URL", "").startswith("postgres"):
            cursor.execute("SELECT id FROM users WHERE telegram_id = %s", (telegram_user.id,))
        else:
            cursor.execute("SELECT id FROM users WHERE telegram_id = ?", (telegram_user.id,))
        user = cursor.fetchone()
        
        if not user:
            # Создаем нового пользователя
            if os.getenv("DATABASE_URL", "").startswith("postgres"):
                cursor.execute("""
                    INSERT INTO users (telegram_id, username, first_name, last_name, subscription_type)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    telegram_user.id,
                    telegram_user.username,
                    telegram_user.first_name,
                    telegram_user.last_name,
                    'free'
                ))
            else:
                cursor.execute("""
                    INSERT INTO users (telegram_id, username, first_name, last_name, subscription_type)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    telegram_user.id,
                    telegram_user.username,
                    telegram_user.first_name,
                    telegram_user.last_name,
                    'free'
                ))
            conn.commit()
            user_id = cursor.lastrowid
            logger.info(f"✅ Created new user: {telegram_user.id} (ID: {user_id})")
        else:
            user_id = user[0]
            logger.info(f"✅ User already exists: {telegram_user.id} (ID: {user_id})")
        
        return user_id
        
    except Exception as e:
        logger.error(f"❌ Error saving user: {e}")
        return None
    finally:
        conn.close()

def save_photo(user_id, photo_url, photo_type):
    """Сохранить фото в БД"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if os.getenv("DATABASE_URL", "").startswith("postgres"):
            cursor.execute("""
                INSERT INTO user_photos (user_id, photo_url, photo_type)
                VALUES (%s, %s, %s)
            """, (user_id, photo_url, photo_type))
        else:
            cursor.execute("""
                INSERT INTO user_photos (user_id, photo_url, photo_type)
                VALUES (?, ?, ?)
            """, (user_id, photo_url, photo_type))
        conn.commit()
        photo_id = cursor.lastrowid
        logger.info(f"✅ Saved {photo_type} photo for user {user_id} (Photo ID: {photo_id})")
        return photo_id
        
    except Exception as e:
        logger.error(f"❌ Error saving photo: {e}")
        return None
    finally:
        conn.close()

async def railway_bot():
    """Railway бот"""
    try:
        logger.info("🚀 Starting Railway Virtual Try-On Bot...")
        
        # Проверяем токен
        bot_token = os.getenv("BOT_TOKEN")
        if not bot_token:
            logger.error("❌ BOT_TOKEN not set!")
            return False
        
        logger.info(f"✅ BOT_TOKEN found: {bot_token[:10]}...")
        
        # Инициализируем базу данных
        logger.info("🗄️ Initializing database...")
        init_database()
        
        # Импортируем aiogram
        from aiogram import Bot, Dispatcher
        from aiogram.types import Message
        from aiogram.filters import Command
        from aiogram.enums import ParseMode
        from aiogram.fsm.context import FSMContext
        from aiogram.fsm.storage.memory import MemoryStorage
        
        # Создаем бота
        bot = Bot(token=bot_token, parse_mode=ParseMode.HTML)
        dp = Dispatcher(storage=MemoryStorage())
        
        # Обработчик команды /start
        @dp.message(Command("start"))
        async def start_handler(message: Message, state: FSMContext):
            # Сохраняем пользователя
            user_id = save_user(message.from_user)
            
            if user_id:
                await message.answer(
                    f"👋 <b>Добро пожаловать в Virtual Try-On Bot!</b>\n\n"
                    f"Привет, {message.from_user.first_name}! Я помогу тебе примерить одежду виртуально с помощью ИИ.\n\n"
                    "🎯 <b>Что я умею:</b>\n"
                    "• Создавать твой виртуальный профиль\n"
                    "• Генерировать фото в новой одежде\n"
                    "• Сохранять результаты примерки\n\n"
                    "🚀 <b>Начнем?</b>\n"
                    "Сначала нужно создать твой профиль - загрузи свои фото!\n\n"
                    "📷 <b>Шаг 1:</b> Загрузи свое селфи для создания профиля"
                )
                
                await state.set_state(UserStates.waiting_for_selfie)
            else:
                await message.answer("❌ Ошибка создания профиля. Попробуйте позже.")
        
        # Обработчик команды /help
        @dp.message(Command("help"))
        async def help_handler(message: Message):
            await message.answer(
                "❓ <b>Помощь по использованию бота</b>\n\n"
                "🎯 <b>Основные команды:</b>\n"
                "/start - Начать работу с ботом\n"
                "/help - Показать эту справку\n"
                "/profile - Управление профилем\n\n"
                "📸 <b>Как создать try-on:</b>\n"
                "1. Загрузи свое селфи\n"
                "2. Загрузи фото в полный рост\n"
                "3. Загрузи фото одежды\n"
                "4. Получи результат!\n\n"
                "💡 <b>Советы для лучшего результата:</b>\n"
                "• Используй качественные фото\n"
                "• Селфи делай анфас с хорошим освещением\n"
                "• Фото в полный рост - в нейтральной позе\n"
                "• Одежду фотографируй на белом фоне"
            )
        
        # Обработчик команды /profile
        @dp.message(Command("profile"))
        async def profile_handler(message: Message):
            conn = get_db_connection()
            cursor = conn.cursor()
            
            try:
                if os.getenv("DATABASE_URL", "").startswith("postgres"):
                    cursor.execute("""
                        SELECT id, telegram_id, username, first_name, last_name, 
                               subscription_type, generation_count, created_at
                        FROM users 
                        WHERE telegram_id = %s
                    """, (message.from_user.id,))
                else:
                    cursor.execute("""
                        SELECT id, telegram_id, username, first_name, last_name, 
                               subscription_type, generation_count, created_at
                        FROM users 
                        WHERE telegram_id = ?
                    """, (message.from_user.id,))
                user = cursor.fetchone()
                
                if not user:
                    await message.answer("❌ Пользователь не найден. Используйте /start")
                    return
                
                await message.answer(
                    f"👤 <b>Ваш профиль</b>\n\n"
                    f"🆔 ID: {user[0]}\n"
                    f"📱 Telegram ID: {user[1]}\n"
                    f"👤 Имя: {user[3]} {user[4] or ''}\n"
                    f"💎 Подписка: {user[5]}\n"
                    f"🎨 Генераций: {user[6]}\n\n"
                    f"📸 <b>Фото:</b> Загружено"
                )
                
            except Exception as e:
                logger.error(f"❌ Error getting profile: {e}")
                await message.answer("❌ Ошибка получения профиля")
            finally:
                conn.close()
        
        # Обработчик фото
        @dp.message(lambda m: m.photo is not None)
        async def photo_handler(message: Message, state: FSMContext):
            current_state = await state.get_state()
            user_id = save_user(message.from_user)
            
            if not user_id:
                await message.answer("❌ Ошибка сохранения пользователя")
                return
            
            # Получаем фото с лучшим качеством
            photo = max(message.photo, key=lambda p: p.file_size)
            
            # Получаем URL фото
            file = await bot.get_file(photo.file_id)
            photo_url = f"https://api.telegram.org/file/bot{bot.token}/{file.file_path}"
            
            if current_state == UserStates.waiting_for_selfie:
                # Сохраняем селфи
                photo_id = save_photo(user_id, photo_url, "selfie")
                if photo_id:
                    await message.answer("✅ Селфи сохранено!")
                    
                    # Переходим к следующему шагу
                    await state.set_state(UserStates.waiting_for_full_body)
                    await message.answer(
                        "📸 <b>Шаг 2:</b> Теперь загрузи фото в полный рост"
                    )
                else:
                    await message.answer("❌ Ошибка сохранения селфи")
                
            elif current_state == UserStates.waiting_for_full_body:
                # Сохраняем фото в полный рост
                photo_id = save_photo(user_id, photo_url, "full_body")
                if photo_id:
                    await message.answer("✅ Фото в полный рост сохранено!")
                    
                    # Профиль создан
                    await state.clear()
                    await message.answer(
                        "🎉 <b>Профиль создан!</b>\n\n"
                        "Теперь ты можешь создавать try-on изображения!\n\n"
                        "👕 <b>Шаг 3:</b> Загрузи фото одежды для примерки"
                    )
                    await state.set_state(UserStates.waiting_for_clothing)
                else:
                    await message.answer("❌ Ошибка сохранения фото")
                
            elif current_state == UserStates.waiting_for_clothing:
                # Сохраняем фото одежды
                photo_id = save_photo(user_id, photo_url, "clothing")
                if photo_id:
                    await message.answer("✅ Фото одежды сохранено!")
                    
                    # Генерируем try-on (пока заглушка)
                    await state.clear()
                    await message.answer(
                        "⚡ <b>Генерирую try-on изображение...</b>\n"
                        "Это может занять 30-60 секунд\n\n"
                        "🎉 <b>Try-on готов!</b>\n\n"
                        "(Пока это заглушка - AI интеграция будет в следующей фазе)\n\n"
                        "Используй /profile чтобы посмотреть сохраненные фото"
                    )
                else:
                    await message.answer("❌ Ошибка сохранения фото одежды")
            
            else:
                await message.answer(
                    "❌ Неожиданное фото. Используй команду /start для начала работы."
                )
        
        # Обработчик всех остальных сообщений
        @dp.message()
        async def echo_handler(message: Message):
            await message.answer(
                "🤖 <b>Бот работает!</b>\n\n"
                "Используй команды:\n"
                "/start - Начать работу\n"
                "/help - Помощь\n"
                "/profile - Профиль\n\n"
                "Или отправь фото для тестирования!"
            )
        
        logger.info("✅ Bot handlers registered")
        logger.info("🚀 Starting bot polling...")
        
        # Запускаем бота
        await dp.start_polling(bot)
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'bot' in locals():
            await bot.session.close()
    
    return True

async def main():
    """Главная функция"""
    success = await railway_bot()
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
