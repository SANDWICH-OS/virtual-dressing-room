from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from app.bot.states import UserStates
from app.bot.keyboards import MainKeyboard
from loguru import logger


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

📸 <b>Как создать try-on:</b>
1. Загрузи свое селфи
2. Загрузи фото в полный рост
3. Загрузи фото одежды
4. Получи результат!

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
    from app.bot.keyboards import ProfileKeyboard
    
    # Очищаем состояние
    await state.clear()
    
    profile_text = """
👤 <b>Управление профилем</b>

Здесь ты можешь:
• Загрузить свои фото
• Посмотреть сохраненные фото
• Удалить ненужные фото
    """
    
    await message.answer(
        profile_text,
        reply_markup=ProfileKeyboard.get_photo_upload_keyboard()
    )
    
    logger.info(f"User {message.from_user.id} opened profile")


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
    dp.message.register(cancel_handler, lambda m: m.text == "❌ Отмена")
