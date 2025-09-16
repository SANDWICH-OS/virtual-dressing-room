from aiogram import Dispatcher
from aiogram.types import Message, PhotoSize
from aiogram.fsm.context import FSMContext
from app.bot.states import UserStates
from app.bot.keyboards import MainKeyboard, ProfileKeyboard
from app.services.file_service import file_service
from app.models.photo import PhotoType
from app.database.async_session import get_async_session
from loguru import logger
import asyncio


async def handle_photo(message: Message, state: FSMContext):
    """Обработчик загруженных фото"""
    user = message.from_user
    current_state = await state.get_state()
    
    # Получаем фото с лучшим качеством
    photo = max(message.photo, key=lambda p: p.file_size)
    
    logger.info(f"User {user.id} uploaded photo, current state: {current_state}")
    
    if current_state == UserStates.waiting_for_selfie:
        await handle_selfie_photo(message, photo, state)
    elif current_state == UserStates.waiting_for_full_body:
        await handle_fullbody_photo(message, photo, state)
    elif current_state == UserStates.waiting_for_clothing:
        await handle_clothing_photo(message, photo, state)
    else:
        await message.answer(
            "❌ Неожиданное фото. Используй команду /start для начала работы.",
            reply_markup=MainKeyboard.get_main_menu()
        )


async def handle_selfie_photo(message: Message, photo: PhotoSize, state: FSMContext):
    """Обработка селфи пользователя"""
    user = message.from_user
    
    try:
        # Обрабатываем фото через сервис
        cloudinary_url, public_id, error = await file_service.process_telegram_photo(
            message.bot, photo, user.id, PhotoType.SELFIE
        )
        
        if error:
            await message.answer(f"❌ {error}\n\nПопробуй загрузить другое фото:")
            return
        
        # Сохраняем в БД
        async with get_async_session() as session:
            await file_service.save_photo_to_database(
                session, user.id, cloudinary_url, PhotoType.SELFIE, public_id
            )
        
        await message.answer("✅ Селфи сохранено!")
        
        # Переходим к следующему шагу
        await state.set_state(UserStates.waiting_for_full_body)
        await message.answer(
            "📸 <b>Шаг 2:</b> Теперь загрузи фото в полный рост",
            reply_markup=MainKeyboard.get_cancel_keyboard()
        )
        
        logger.info(f"User {user.id} uploaded selfie successfully")
        
    except Exception as e:
        logger.error(f"Error handling selfie for user {user.id}: {e}")
        await message.answer("❌ Произошла ошибка. Попробуй еще раз.")


async def handle_fullbody_photo(message: Message, photo: PhotoSize, state: FSMContext):
    """Обработка фото в полный рост"""
    user = message.from_user
    
    try:
        # Обрабатываем фото через сервис
        cloudinary_url, public_id, error = await file_service.process_telegram_photo(
            message.bot, photo, user.id, PhotoType.FULL_BODY
        )
        
        if error:
            await message.answer(f"❌ {error}\n\nПопробуй загрузить другое фото:")
            return
        
        # Сохраняем в БД
        async with get_async_session() as session:
            await file_service.save_photo_to_database(
                session, user.id, cloudinary_url, PhotoType.FULL_BODY, public_id
            )
        
        await message.answer("✅ Фото в полный рост сохранено!")
        
        # Профиль создан, переходим к главному меню
        await state.clear()
        await message.answer(
            "🎉 <b>Профиль создан!</b>\n\nТеперь ты можешь создавать try-on изображения!",
            reply_markup=MainKeyboard.get_main_menu()
        )
        
        logger.info(f"User {user.id} uploaded fullbody photo successfully")
        
    except Exception as e:
        logger.error(f"Error handling fullbody photo for user {user.id}: {e}")
        await message.answer("❌ Произошла ошибка. Попробуй еще раз.")


async def handle_clothing_photo(message: Message, photo: PhotoSize, state: FSMContext):
    """Обработка фото одежды"""
    user = message.from_user
    
    try:
        # Обрабатываем фото через сервис
        cloudinary_url, public_id, error = await file_service.process_telegram_photo(
            message.bot, photo, user.id, PhotoType.CLOTHING
        )
        
        if error:
            await message.answer(f"❌ {error}\n\nПопробуй загрузить другое фото:")
            return
        
        # Сохраняем в БД
        async with get_async_session() as session:
            await file_service.save_photo_to_database(
                session, user.id, cloudinary_url, PhotoType.CLOTHING, public_id
            )
        
        await message.answer("✅ Фото одежды сохранено!")
        
        # Переходим к генерации
        await state.set_state(UserStates.processing_tryon)
        await message.answer(
            "⚡ <b>Генерирую try-on изображение...</b>\nЭто может занять 30-60 секунд",
            reply_markup=MainKeyboard.get_cancel_keyboard()
        )
        
        # Здесь будет вызов AI сервиса для генерации
        # Пока просто имитируем процесс
        await asyncio.sleep(2)
        await message.answer(
            "🎉 <b>Try-on готов!</b>\n\n(Пока это заглушка - AI интеграция будет в следующей фазе)",
            reply_markup=MainKeyboard.get_main_menu()
        )
        
        await state.clear()
        
        logger.info(f"User {user.id} uploaded clothing photo successfully")
        
    except Exception as e:
        logger.error(f"Error handling clothing photo for user {user.id}: {e}")
        await message.answer("❌ Произошла ошибка. Попробуй еще раз.")


def register_photo_handlers(dp: Dispatcher):
    """Регистрация обработчиков фото"""
    dp.message.register(handle_photo, lambda m: m.photo is not None)
