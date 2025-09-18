from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from app.bot.states import UserStates
from app.bot.keyboards import MainKeyboard
from app.services.ai_logging_service import ai_logging_service
from loguru import logger
import asyncio
from datetime import datetime


async def handle_ai_testing_buttons(message: Message, state: FSMContext):
    """Обработчик кнопок тестирования ИИ сервисов"""
    user = message.from_user
    current_state = await state.get_state()
    
    if current_state != UserStates.photos_uploaded:
        await message.answer(
            "❌ Сначала загрузи свои фото для создания профиля!",
            reply_markup=MainKeyboard.get_main_menu()
        )
        return
    
    text = message.text
    
    if text == "🤖 Тест VModel":
        await test_vmodel_service(message, state)
    elif text == "👗 Тест Fashn":
        await test_fashn_service(message, state)
    elif text == "✂️ Тест Pixelcut":
        await test_pixelcut_service(message, state)
    elif text == "📸 Загрузить фото одежды":
        await handle_clothing_upload_request(message, state)
    else:
        await message.answer(
            "❌ Неизвестная команда. Используй кнопки ниже:",
            reply_markup=MainKeyboard.get_ai_testing_keyboard()
        )


async def test_vmodel_service(message: Message, state: FSMContext):
    """Тестирование VModel сервиса"""
    user = message.from_user
    start_time = datetime.now()
    
    # Логируем запрос
    await ai_logging_service.log_ai_request(
        user_id=user.id,
        service_name="VModel",
        request_data={"type": "try_on_generation", "user_photos": "loaded"},
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
    
    logger.info(f"User {user.id} tested VModel service via button")


async def test_fashn_service(message: Message, state: FSMContext):
    """Тестирование Fashn сервиса"""
    user = message.from_user
    start_time = datetime.now()
    
    # Логируем запрос
    await ai_logging_service.log_ai_request(
        user_id=user.id,
        service_name="Fashn",
        request_data={"type": "try_on_generation", "user_photos": "loaded"},
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
    
    logger.info(f"User {user.id} tested Fashn service via button")


async def test_pixelcut_service(message: Message, state: FSMContext):
    """Тестирование Pixelcut сервиса"""
    user = message.from_user
    start_time = datetime.now()
    
    # Логируем запрос
    await ai_logging_service.log_ai_request(
        user_id=user.id,
        service_name="Pixelcut",
        request_data={"type": "try_on_generation", "user_photos": "loaded"},
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
    
    logger.info(f"User {user.id} tested Pixelcut service via button")


async def handle_clothing_upload_request(message: Message, state: FSMContext):
    """Обработка запроса на загрузку фото одежды"""
    await state.set_state(UserStates.waiting_for_clothing)
    await message.answer(
        "📸 <b>Загрузи фото одежды</b>\n\nСфотографируй одежду, которую хочешь примерить виртуально.\n\n💡 <b>Советы:</b>\n• Фотографируй на белом фоне\n• Одежда должна быть хорошо видна\n• Избегай теней и складок",
        reply_markup=MainKeyboard.get_cancel_keyboard()
    )
    
    logger.info(f"User {message.from_user.id} requested clothing upload")


def register_ai_testing_handlers(dp: Dispatcher):
    """Регистрация обработчиков тестирования ИИ"""
    # Обработчик кнопок тестирования ИИ
    dp.message.register(
        handle_ai_testing_buttons,
        lambda m: m.text in ["🤖 Тест VModel", "👗 Тест Fashn", "✂️ Тест Pixelcut", "📸 Загрузить фото одежды"]
    )
