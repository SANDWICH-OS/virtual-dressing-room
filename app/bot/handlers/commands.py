from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from app.bot.states import UserStates
from app.bot.keyboards import MainKeyboard
from app.services.ai_logging_service import ai_logging_service
from loguru import logger
import asyncio
from datetime import datetime


async def start_command(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    user = message.from_user
    
    # Очищаем состояние
    await state.clear()
    
    # Приветственное сообщение
    welcome_text = f"""
👋 <b>Добро пожаловать в Virtual Try-On Bot!</b>

Привет, {user.first_name}! Я помогу тебе примерить одежду виртуально с помощью ИИ.

🎯 <b>Что я умею:</b>
• Создавать твой виртуальный профиль
• Генерировать фото в новой одежде
• Сохранять результаты примерки

🚀 <b>Начнем?</b>
Сначала нужно создать твой профиль - загрузи свои фото!
    """
    
    await message.answer(
        welcome_text,
        reply_markup=MainKeyboard.get_main_menu()
    )
    
    # Переводим в состояние ожидания селфи
    await state.set_state(UserStates.waiting_for_selfie)
    
    await message.answer(
        "📷 <b>Шаг 1:</b> Загрузи свое селфи для создания профиля",
        reply_markup=MainKeyboard.get_cancel_keyboard()
    )
    
    logger.info(f"User {user.id} started bot")


async def help_command(message: Message, state: FSMContext):
    """Обработчик команды /help"""
    
    help_text = """
❓ <b>Помощь по использованию бота</b>

🎯 <b>Основные команды:</b>
/start - Начать работу с ботом
/help - Показать эту справку
/profile - Управление профилем

🤖 <b>Тестирование ИИ сервисов:</b>
/test_vmodel - Тест VModel API
/test_fashn - Тест Fashn API
/test_pixelcut - Тест Pixelcut API

📸 <b>Как создать try-on:</b>
1. Загрузи свое селфи
2. Загрузи фото в полный рост
3. Загрузи фото одежды
4. Выбери ИИ сервис для генерации
5. Получи результат!

💡 <b>Советы для лучшего результата:</b>
• Используй качественные фото
• Селфи делай анфас с хорошим освещением
• Фото в полный рост - в нейтральной позе
• Одежду фотографируй на белом фоне

❓ <b>Проблемы?</b>
Если что-то не работает, напиши @support
    """
    
    await message.answer(help_text)
    logger.info(f"User {message.from_user.id} requested help")


async def profile_command(message: Message, state: FSMContext):
    """Обработчик команды /profile"""
    from app.database.async_session import get_async_session
    from app.models.user import User
    from app.models.photo import UserPhoto, PhotoType
    from sqlalchemy import select, func
    
    # Очищаем состояние
    await state.clear()
    
    user = message.from_user
    
    try:
        # Получаем информацию о пользователе из БД
        async with get_async_session() as session:
            # Получаем пользователя
            result = await session.execute(
                select(User).where(User.telegram_id == user.id)
            )
            db_user = result.scalar_one_or_none()
            
            # Получаем количество загруженных фото
            selfie_count = await session.scalar(
                select(func.count(UserPhoto.id)).where(
                    UserPhoto.user_id == user.id,
                    UserPhoto.photo_type == PhotoType.SELFIE
                )
            ) or 0
            
            fullbody_count = await session.scalar(
                select(func.count(UserPhoto.id)).where(
                    UserPhoto.user_id == user.id,
                    UserPhoto.photo_type == PhotoType.FULL_BODY
                )
            ) or 0
            
            clothing_count = await session.scalar(
                select(func.count(UserPhoto.id)).where(
                    UserPhoto.user_id == user.id,
                    UserPhoto.photo_type == PhotoType.CLOTHING
                )
            ) or 0
            
            # Формируем информацию о профиле
            if db_user:
                subscription_info = "🆓 Бесплатная" if db_user.subscription_type == "free" else f"💎 {db_user.subscription_type.title()}"
                generation_count = db_user.generation_count or 0
                created_at = db_user.created_at.strftime("%d.%m.%Y") if db_user.created_at else "Неизвестно"
            else:
                subscription_info = "🆓 Бесплатная"
                generation_count = 0
                created_at = "Неизвестно"
            
            profile_text = f"""
👤 <b>Мой профиль</b>

🆔 <b>ID:</b> {user.id}
👤 <b>Имя:</b> {user.first_name or 'Не указано'}
📧 <b>Username:</b> @{user.username or 'Не указан'}
💳 <b>Подписка:</b> {subscription_info}
🎨 <b>Генераций использовано:</b> {generation_count}
📅 <b>Дата регистрации:</b> {created_at}

📸 <b>Загруженные фото:</b>
• Селфи: {selfie_count}
• В полный рост: {fullbody_count}
• Одежда: {clothing_count}

{'✅ Профиль готов к использованию!' if selfie_count > 0 and fullbody_count > 0 else '⚠️ Загрузи фото для создания профиля'}
            """
            
            await message.answer(
                profile_text,
                reply_markup=MainKeyboard.get_main_menu()
            )
            
    except Exception as e:
        logger.error(f"Error getting profile info for user {user.id}: {e}")
        # Fallback информация без БД
        profile_text = f"""
👤 <b>Мой профиль</b>

🆔 <b>ID:</b> {user.id}
👤 <b>Имя:</b> {user.first_name or 'Не указано'}
📧 <b>Username:</b> @{user.username or 'Не указан'}
💳 <b>Подписка:</b> 🆓 Бесплатная
🎨 <b>Генераций использовано:</b> 0
📅 <b>Дата регистрации:</b> Неизвестно

📸 <b>Загруженные фото:</b>
• Селфи: 0
• В полный рост: 0
• Одежда: 0

⚠️ Загрузи фото для создания профиля
        """
        
        await message.answer(
            profile_text,
            reply_markup=MainKeyboard.get_main_menu()
        )
    
    logger.info(f"User {message.from_user.id} viewed profile")


async def test_vmodel_command(message: Message, state: FSMContext):
    """Обработчик команды /test_vmodel"""
    user = message.from_user
    current_state = await state.get_state()
    
    if current_state != UserStates.photos_uploaded:
        await message.answer(
            "❌ Сначала загрузи свои фото для создания профиля!",
            reply_markup=MainKeyboard.get_main_menu()
        )
        return
    
    start_time = datetime.now()
    
    # Логируем запрос
    await ai_logging_service.log_ai_request(
        user_id=user.id,
        service_name="VModel",
        request_data={"type": "try_on_generation", "user_photos": "loaded", "command": "/test_vmodel"},
        start_time=start_time
    )
    
    await state.set_state(UserStates.waiting_ai_response)
    await message.answer(
        "🤖 <b>Тестируем VModel...</b>\n\nОтправляю твои фото в VModel API для генерации try-on изображения.\nЭто может занять 30-60 секунд.",
        reply_markup=MainKeyboard.get_cancel_keyboard()
    )
    
    # Заглушка для VModel
    await asyncio.sleep(3)
    processing_time = (datetime.now() - start_time).total_seconds()
    
    # Логируем ответ
    await ai_logging_service.log_ai_response(
        user_id=user.id,
        service_name="VModel",
        response_data={"status": "success", "result_type": "try_on_image"},
        processing_time=processing_time,
        success=True
    )
    
    # Логируем метрики качества
    await ai_logging_service.log_ai_quality_metrics(
        user_id=user.id,
        service_name="VModel",
        quality_score=4,
        processing_time=processing_time
    )
    
    await message.answer(
        "🎉 <b>VModel результат готов!</b>\n\n(Это заглушка - реальная интеграция будет в Фазе 4.2)\n\nКачество: ⭐⭐⭐⭐\nВремя обработки: 2.3 сек",
        reply_markup=MainKeyboard.get_ai_testing_keyboard()
    )
    await state.set_state(UserStates.photos_uploaded)
    
    logger.info(f"User {user.id} tested VModel service")


async def test_fashn_command(message: Message, state: FSMContext):
    """Обработчик команды /test_fashn"""
    user = message.from_user
    current_state = await state.get_state()
    
    if current_state != UserStates.photos_uploaded:
        await message.answer(
            "❌ Сначала загрузи свои фото для создания профиля!",
            reply_markup=MainKeyboard.get_main_menu()
        )
        return
    
    start_time = datetime.now()
    
    # Логируем запрос
    await ai_logging_service.log_ai_request(
        user_id=user.id,
        service_name="Fashn",
        request_data={"type": "try_on_generation", "user_photos": "loaded", "command": "/test_fashn"},
        start_time=start_time
    )
    
    await state.set_state(UserStates.waiting_ai_response)
    await message.answer(
        "👗 <b>Тестируем Fashn...</b>\n\nОтправляю твои фото в Fashn API для генерации try-on изображения.\nЭто может занять 30-60 секунд.",
        reply_markup=MainKeyboard.get_cancel_keyboard()
    )
    
    # Заглушка для Fashn
    await asyncio.sleep(3)
    processing_time = (datetime.now() - start_time).total_seconds()
    
    # Логируем ответ
    await ai_logging_service.log_ai_response(
        user_id=user.id,
        service_name="Fashn",
        response_data={"status": "success", "result_type": "try_on_image"},
        processing_time=processing_time,
        success=True
    )
    
    # Логируем метрики качества
    await ai_logging_service.log_ai_quality_metrics(
        user_id=user.id,
        service_name="Fashn",
        quality_score=5,
        processing_time=processing_time
    )
    
    await message.answer(
        "🎉 <b>Fashn результат готов!</b>\n\n(Это заглушка - реальная интеграция будет в Фазе 4.3)\n\nКачество: ⭐⭐⭐⭐⭐\nВремя обработки: 1.8 сек",
        reply_markup=MainKeyboard.get_ai_testing_keyboard()
    )
    await state.set_state(UserStates.photos_uploaded)
    
    logger.info(f"User {user.id} tested Fashn service")


async def test_pixelcut_command(message: Message, state: FSMContext):
    """Обработчик команды /test_pixelcut"""
    user = message.from_user
    current_state = await state.get_state()
    
    if current_state != UserStates.photos_uploaded:
        await message.answer(
            "❌ Сначала загрузи свои фото для создания профиля!",
            reply_markup=MainKeyboard.get_main_menu()
        )
        return
    
    start_time = datetime.now()
    
    # Логируем запрос
    await ai_logging_service.log_ai_request(
        user_id=user.id,
        service_name="Pixelcut",
        request_data={"type": "try_on_generation", "user_photos": "loaded", "command": "/test_pixelcut"},
        start_time=start_time
    )
    
    await state.set_state(UserStates.waiting_ai_response)
    await message.answer(
        "✂️ <b>Тестируем Pixelcut...</b>\n\nОтправляю твои фото в Pixelcut API для генерации try-on изображения.\nЭто может занять 30-60 секунд.",
        reply_markup=MainKeyboard.get_cancel_keyboard()
    )
    
    # Заглушка для Pixelcut
    await asyncio.sleep(3)
    processing_time = (datetime.now() - start_time).total_seconds()
    
    # Логируем ответ
    await ai_logging_service.log_ai_response(
        user_id=user.id,
        service_name="Pixelcut",
        response_data={"status": "success", "result_type": "try_on_image"},
        processing_time=processing_time,
        success=True
    )
    
    # Логируем метрики качества
    await ai_logging_service.log_ai_quality_metrics(
        user_id=user.id,
        service_name="Pixelcut",
        quality_score=3,
        processing_time=processing_time
    )
    
    await message.answer(
        "🎉 <b>Pixelcut результат готов!</b>\n\n(Это заглушка - реальная интеграция будет в Фазе 4.4)\n\nКачество: ⭐⭐⭐\nВремя обработки: 3.1 сек",
        reply_markup=MainKeyboard.get_ai_testing_keyboard()
    )
    await state.set_state(UserStates.photos_uploaded)
    
    logger.info(f"User {user.id} tested Pixelcut service")


async def clear_command(message: Message, state: FSMContext):
    """Обработчик команды /clear"""
    await state.clear()
    await message.answer(
        "🧹 <b>Данные очищены!</b>\n\nВсе загруженные фото и состояния сброшены.\nИспользуй /start для начала работы.",
        reply_markup=MainKeyboard.get_main_menu()
    )
    logger.info(f"User {message.from_user.id} cleared data")


async def cancel_handler(message: Message, state: FSMContext):
    """Обработчик отмены"""
    await state.clear()
    await message.answer(
        "❌ Операция отменена",
        reply_markup=MainKeyboard.get_main_menu()
    )
    logger.info(f"User {message.from_user.id} cancelled operation")


def register_command_handlers(dp: Dispatcher):
    """Регистрация обработчиков команд"""
    dp.message.register(start_command, Command("start"))
    dp.message.register(help_command, Command("help"))
    dp.message.register(profile_command, Command("profile"))
    dp.message.register(clear_command, Command("clear"))
    dp.message.register(test_vmodel_command, Command("test_vmodel"))
    dp.message.register(test_fashn_command, Command("test_fashn"))
    dp.message.register(test_pixelcut_command, Command("test_pixelcut"))
    dp.message.register(cancel_handler, lambda m: m.text == "❌ Отмена")
