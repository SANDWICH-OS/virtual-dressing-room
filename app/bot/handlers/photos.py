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
    
    if current_state == UserStates.waiting_user_photo:
        await handle_user_photo(message, photo, state)
    elif current_state == UserStates.waiting_clothing_photo:
        await handle_clothing_photo(message, photo, state)
    else:
        # Если фото загружено не в ожидаемом состоянии
        await message.answer(
            "❌ <b>Бот не готов загрузить фотографию</b>\n\nСначала выбери команду для загрузки фото:\n• /upload_user_photo - для фото пользователя\n• /upload_clothing_photo - для фото одежды",
            reply_markup=MainKeyboard.get_main_menu()
        )


async def handle_user_photo(message: Message, photo: PhotoSize, state: FSMContext):
    """Обработка фото пользователя"""
    user = message.from_user
    
    try:
        # Обрабатываем фото через сервис
        cloudinary_url, public_id, error = await file_service.process_telegram_photo(
            message.bot, photo, user.id, PhotoType.USER_PHOTO
        )
        
        if error:
            await message.answer(f"❌ {error}\n\nПопробуй загрузить другое фото:")
            return
        
        # Сохраняем в БД
        async with get_async_session() as session:
            await file_service.save_photo_to_database(
                session, user.id, cloudinary_url, PhotoType.USER_PHOTO, public_id
            )
        
        await message.answer("✅ Фото пользователя сохранено!")
        
        # Переходим в состояние авторизован
        await state.set_state(UserStates.authorized)
        await message.answer(
            "🎉 <b>Фото загружено!</b>\n\nТеперь ты можешь загрузить фото одежды или тестировать ИИ сервисы!",
            reply_markup=MainKeyboard.get_main_menu()
        )
        
        logger.info(f"User {user.id} uploaded user photo successfully")
        
    except Exception as e:
        logger.error(f"Error handling user photo for user {user.id}: {e}")
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
        
        # Переходим в состояние авторизован
        await state.set_state(UserStates.authorized)
        await message.answer(
            "🎉 <b>Фото одежды загружено!</b>\n\nТеперь ты можешь тестировать ИИ сервисы для генерации try-on изображений!",
            reply_markup=MainKeyboard.get_main_menu()
        )
        
        logger.info(f"User {user.id} uploaded clothing photo successfully")
        
    except Exception as e:
        logger.error(f"Error handling clothing photo for user {user.id}: {e}")
        await message.answer("❌ Произошла ошибка. Попробуй еще раз.")


def register_photo_handlers(dp: Dispatcher):
    """Регистрация обработчиков фото"""
    dp.message.register(handle_photo, lambda m: m.photo is not None)
