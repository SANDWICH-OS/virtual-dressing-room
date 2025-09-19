from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from app.bot.states import UserStates
from app.bot.keyboards import MainKeyboard
from loguru import logger












async def handle_general_text_messages(message: Message, state: FSMContext):
    """Обработчик общих текстовых сообщений"""
    from .commands import (
        profile_command, help_command, upload_user_photo_command, 
        upload_clothing_photo_command,
        test_vmodel_command, test_fashn_command, test_pixelcut_command,
        clear_command
    )
    
    user = message.from_user
    text = message.text
    current_state = await state.get_state()
    
    # Обработка состояния "Неавторизован"
    if current_state == UserStates.unauthorized or current_state is None:
        await message.answer(
            "👋 <b>Добро пожаловать в Virtual Try-On Bot!</b>\n\nДля начала работы нажми /start",
            reply_markup=None
        )
        return
    
    # Обработка кнопок главного меню (только в состоянии authorized)
    if current_state == UserStates.authorized:
        if text == "👤 Мой профиль":
            await profile_command(message, state)
        elif text == "📷 Загрузить фото пользователя":
            await upload_user_photo_command(message, state)
        elif text == "👗 Загрузить фото одежды":
            await upload_clothing_photo_command(message, state)
        elif text == "🤖 Тест VModel":
            await test_vmodel_command(message, state)
        elif text == "👗 Тест Fashn":
            await test_fashn_command(message, state)
        elif text == "✂️ Тест Pixelcut":
            await test_pixelcut_command(message, state)
        elif text == "💳 Подписка":
            await message.answer(
                "💳 <b>Управление подпиской</b>\n\nЭта функция будет доступна в следующих версиях бота.",
                reply_markup=MainKeyboard.get_main_menu()
            )
        elif text == "🧹 Очистить данные":
            await clear_command(message, state)
        elif text == "❓ Помощь":
            await help_command(message, state)
        else:
            # Неизвестное сообщение
            await message.answer(
                "❓ <b>Не понимаю эту команду</b>\n\nИспользуй кнопки меню или команды:\n/start - Начать работу\n/help - Помощь\n/clear - Очистить данные",
                reply_markup=MainKeyboard.get_main_menu()
            )
    elif current_state in [UserStates.waiting_user_photo, UserStates.waiting_clothing_photo, UserStates.subscription_management]:
        # В состояниях загрузки фото и управления подпиской - переходим в authorized и выполняем команду
        await state.set_state(UserStates.authorized)
        
        if text == "👤 Мой профиль":
            await profile_command(message, state)
        elif text == "📷 Загрузить фото пользователя":
            await upload_user_photo_command(message, state)
        elif text == "👗 Загрузить фото одежды":
            await upload_clothing_photo_command(message, state)
        elif text == "🤖 Тест VModel":
            await test_vmodel_command(message, state)
        elif text == "👗 Тест Fashn":
            await test_fashn_command(message, state)
        elif text == "✂️ Тест Pixelcut":
            await test_pixelcut_command(message, state)
        elif text == "💳 Подписка":
            await message.answer(
                "💳 <b>Управление подпиской</b>\n\nЭта функция будет доступна в следующих версиях бота.",
                reply_markup=MainKeyboard.get_main_menu()
            )
        elif text == "🧹 Очистить данные":
            await clear_command(message, state)
        elif text == "❓ Помощь":
            await help_command(message, state)
        else:
            # Неизвестное сообщение
            await message.answer(
                "❓ <b>Не понимаю эту команду</b>\n\nИспользуй кнопки меню или команды:\n/start - Начать работу\n/help - Помощь\n/clear - Очистить данные",
                reply_markup=MainKeyboard.get_main_menu()
            )
    else:
        # В других состояниях - обрабатываем команды
        if text == "👤 Мой профиль":
            await profile_command(message, state)
        elif text == "📷 Загрузить фото пользователя":
            await upload_user_photo_command(message, state)
        elif text == "👗 Загрузить фото одежды":
            await upload_clothing_photo_command(message, state)
        elif text == "🤖 Тест VModel":
            await test_vmodel_command(message, state)
        elif text == "👗 Тест Fashn":
            await test_fashn_command(message, state)
        elif text == "✂️ Тест Pixelcut":
            await test_pixelcut_command(message, state)
        elif text == "💳 Подписка":
            await message.answer(
                "💳 <b>Управление подпиской</b>\n\nЭта функция будет доступна в следующих версиях бота.",
                reply_markup=MainKeyboard.get_main_menu()
            )
        elif text == "🧹 Очистить данные":
            await clear_command(message, state)
        elif text == "❓ Помощь":
            await help_command(message, state)
        else:
            # Неизвестное сообщение
            await message.answer(
                "❓ <b>Не понимаю эту команду</b>\n\nИспользуй кнопки меню или команды:\n/start - Начать работу\n/help - Помощь\n/clear - Очистить данные",
                reply_markup=MainKeyboard.get_main_menu()
            )
    
    logger.info(f"User {user.id} sent text message: {text}")


def register_ai_testing_handlers(dp: Dispatcher):
    """Регистрация обработчиков тестирования ИИ"""
    # Обработчик всех текстовых сообщений (кроме команд и отмены)
    dp.message.register(
        handle_general_text_messages,
        lambda m: m.text is not None and m.text not in ["🔙 Назад"]
    )