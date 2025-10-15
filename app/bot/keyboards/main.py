from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


class MainKeyboard:
    """Основные клавиатуры бота"""
    
    @staticmethod
    def get_main_menu() -> ReplyKeyboardMarkup:
        """Главное меню - состояние Авторизован"""
        builder = ReplyKeyboardBuilder()
        builder.add(
            KeyboardButton(text="👤 Мой профиль"),
            KeyboardButton(text="📷 Загрузить фото пользователя"),
            KeyboardButton(text="👗 Загрузить фото одежды"),
            KeyboardButton(text="👗 Тест Fashn"),
            KeyboardButton(text="💳 Подписка"),
            KeyboardButton(text="🧹 Очистить данные"),
            KeyboardButton(text="❓ Помощь")
        )
        builder.adjust(2, 2, 1, 1, 1)
        return builder.as_markup(resize_keyboard=True)
    
    @staticmethod
    def get_cancel_keyboard() -> ReplyKeyboardMarkup:
        """Клавиатура с кнопкой отмены (удалена)"""
        builder = ReplyKeyboardBuilder()
        return builder.as_markup(resize_keyboard=True)
    
    @staticmethod
    def get_back_keyboard() -> ReplyKeyboardMarkup:
        """Клавиатура с кнопкой назад"""
        builder = ReplyKeyboardBuilder()
        builder.add(KeyboardButton(text="🔙 Назад"))
        return builder.as_markup(resize_keyboard=True)
    
    @staticmethod
    def get_yes_no_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура Да/Нет"""
        builder = InlineKeyboardBuilder()
        builder.add(
            InlineKeyboardButton(text="✅ Да", callback_data="yes"),
            InlineKeyboardButton(text="❌ Нет", callback_data="no")
        )
        return builder.as_markup()
    
    @staticmethod
    def get_ai_testing_keyboard() -> ReplyKeyboardMarkup:
        """Клавиатура для тестирования ИИ сервисов (удалена)"""
        builder = ReplyKeyboardBuilder()
        return builder.as_markup(resize_keyboard=True)


