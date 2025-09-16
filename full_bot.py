#!/usr/bin/env python3
"""
Полнофункциональный бот с сохранением в БД
"""

import os
import sys
import asyncio
from pathlib import Path
from loguru import logger

# Добавляем корневую директорию в PYTHONPATH
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Загружаем переменные окружения
from dotenv import load_dotenv
load_dotenv(".env")

# Настраиваем логирование
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

async def full_bot():
    """Полнофункциональный бот с БД"""
    try:
        logger.info("🚀 Starting Full Virtual Try-On Bot...")
        
        # Проверяем токен
        bot_token = os.getenv("BOT_TOKEN")
        if not bot_token or bot_token == "your_telegram_bot_token_here":
            logger.error("❌ BOT_TOKEN not set!")
            return False
        
        logger.info(f"✅ BOT_TOKEN found: {bot_token[:10]}...")
        
        # Импортируем aiogram
        from aiogram import Bot, Dispatcher
        from aiogram.types import Message, PhotoSize
        from aiogram.filters import Command
        from aiogram.enums import ParseMode
        from aiogram.fsm.context import FSMContext
        from aiogram.fsm.storage.memory import MemoryStorage
        
        # Импортируем наши модули
        from app.database.connection import engine, Base
        from app.models.user import User, SubscriptionType
        from app.models.photo import UserPhoto, PhotoType
        from sqlalchemy import select, insert
        from sqlalchemy.ext.asyncio import AsyncSession
        
        # Создаем таблицы если их нет
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables created/verified")
        
        # Создаем бота
        bot = Bot(token=bot_token, parse_mode=ParseMode.HTML)
        dp = Dispatcher(storage=MemoryStorage())
        
        # Состояния для FSM
        class UserStates:
            waiting_for_selfie = "waiting_for_selfie"
            waiting_for_full_body = "waiting_for_full_body"
            waiting_for_clothing = "waiting_for_clothing"
        
        # Функция для сохранения пользователя
        async def save_user(telegram_user):
            async with AsyncSession(engine) as session:
                # Проверяем, есть ли пользователь
                result = await session.execute(
                    select(User).where(User.telegram_id == telegram_user.id)
                )
                user = result.scalar_one_or_none()
                
                if not user:
                    # Создаем нового пользователя
                    user = User(
                        telegram_id=telegram_user.id,
                        username=telegram_user.username,
                        first_name=telegram_user.first_name,
                        last_name=telegram_user.last_name,
                        subscription_type=SubscriptionType.FREE
                    )
                    session.add(user)
                    await session.commit()
                    await session.refresh(user)
                    logger.info(f"✅ Created new user: {telegram_user.id}")
                else:
                    logger.info(f"✅ User already exists: {telegram_user.id}")
                
                return user
        
        # Функция для сохранения фото
        async def save_photo(user_id, photo_url, photo_type):
            async with AsyncSession(engine) as session:
                # Получаем URL фото
                file = await bot.get_file(photo_url)
                photo_url = f"https://api.telegram.org/file/bot{bot.token}/{file.file_path}"
                
                # Сохраняем фото
                photo = UserPhoto(
                    user_id=user_id,
                    photo_url=photo_url,
                    photo_type=photo_type
                )
                session.add(photo)
                await session.commit()
                await session.refresh(photo)
                logger.info(f"✅ Saved {photo_type} photo for user {user_id}")
                return photo
        
        # Обработчик команды /start
        @dp.message(Command("start"))
        async def start_handler(message: Message, state: FSMContext):
            # Сохраняем пользователя
            user = await save_user(message.from_user)
            
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
            # Получаем информацию о пользователе
            async with AsyncSession(engine) as session:
                result = await session.execute(
                    select(User).where(User.telegram_id == message.from_user.id)
                )
                user = result.scalar_one_or_none()
                
                if not user:
                    await message.answer("❌ Пользователь не найден. Используйте /start")
                    return
                
                # Получаем фото пользователя
                photos_result = await session.execute(
                    select(UserPhoto).where(UserPhoto.user_id == user.id)
                )
                photos = photos_result.scalars().all()
                
                photo_info = []
                for photo in photos:
                    photo_info.append(f"• {photo.photo_type.value}: ✅")
                
                if not photo_info:
                    photo_info = ["• Нет загруженных фото"]
                
                await message.answer(
                    f"👤 <b>Ваш профиль</b>\n\n"
                    f"🆔 ID: {user.id}\n"
                    f"📱 Telegram ID: {user.telegram_id}\n"
                    f"👤 Имя: {user.first_name} {user.last_name or ''}\n"
                    f"💎 Подписка: {user.subscription_type.value}\n"
                    f"🎨 Генераций: {user.generation_count}\n\n"
                    f"📸 <b>Фото:</b>\n" + "\n".join(photo_info)
                )
        
        # Обработчик фото
        @dp.message(lambda m: m.photo is not None)
        async def photo_handler(message: Message, state: FSMContext):
            current_state = await state.get_state()
            user = await save_user(message.from_user)
            
            # Получаем фото с лучшим качеством
            photo = max(message.photo, key=lambda p: p.file_size)
            
            if current_state == UserStates.waiting_for_selfie:
                # Сохраняем селфи
                await save_photo(user.id, photo.file_id, PhotoType.SELFIE)
                await message.answer("✅ Селфи сохранено!")
                
                # Переходим к следующему шагу
                await state.set_state(UserStates.waiting_for_full_body)
                await message.answer(
                    "📸 <b>Шаг 2:</b> Теперь загрузи фото в полный рост"
                )
                
            elif current_state == UserStates.waiting_for_full_body:
                # Сохраняем фото в полный рост
                await save_photo(user.id, photo.file_id, PhotoType.FULL_BODY)
                await message.answer("✅ Фото в полный рост сохранено!")
                
                # Профиль создан
                await state.clear()
                await message.answer(
                    "🎉 <b>Профиль создан!</b>\n\n"
                    "Теперь ты можешь создавать try-on изображения!\n\n"
                    "👕 <b>Шаг 3:</b> Загрузи фото одежды для примерки"
                )
                await state.set_state(UserStates.waiting_for_clothing)
                
            elif current_state == UserStates.waiting_for_clothing:
                # Сохраняем фото одежды
                await save_photo(user.id, photo.file_id, PhotoType.CLOTHING)
                await message.answer("✅ Фото одежды сохранено!")
                
                # Генерируем try-on (пока заглушка)
                await state.clear()
                await message.answer(
                    "⚡ <b>Генерирую try-on изображение...</b>\n"
                    "Это может занять 30-60 секунд\n\n"
                    "🎉 <b>Try-on готов!</b>\n\n"
                    "(Пока это заглушка - AI интеграция будет в следующей фазе)"
                )
            
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
    success = await full_bot()
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
