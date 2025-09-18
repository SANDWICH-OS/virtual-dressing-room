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
            KeyboardButton(text="🤖 Тест VModel"),
            KeyboardButton(text="👗 Тест Fashn"),
            KeyboardButton(text="✂️ Тест Pixelcut"),
            KeyboardButton(text="💳 Подписка"),
            KeyboardButton(text="🧹 Очистить данные"),
            KeyboardButton(text="❓ Помощь")
        )
        builder.adjust(2, 2, 2, 1, 1, 1)
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


class ProfileKeyboard:
    """Клавиатуры для профиля"""
    
    @staticmethod
    def get_photo_upload_keyboard() -> ReplyKeyboardMarkup:
        """Клавиатура для загрузки фото"""
        builder = ReplyKeyboardBuilder()
        builder.add(
            KeyboardButton(text="📷 Загрузить селфи"),
            KeyboardButton(text="📸 Загрузить фото в полный рост"),
            KeyboardButton(text="👀 Посмотреть мои фото")
        )
        builder.adjust(2, 1, 1)
        return builder.as_markup(resize_keyboard=True)
    
    @staticmethod
    def get_photo_management_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура управления фото"""
        builder = InlineKeyboardBuilder()
        builder.add(
            InlineKeyboardButton(text="🗑 Удалить селфи", callback_data="delete_selfie"),
            InlineKeyboardButton(text="🗑 Удалить фото в полный рост", callback_data="delete_fullbody"),
            InlineKeyboardButton(text="📷 Загрузить новое селфи", callback_data="upload_selfie"),
            InlineKeyboardButton(text="📸 Загрузить новое фото в полный рост", callback_data="upload_fullbody")
        )
        builder.adjust(1, 1, 1, 1)
        return builder.as_markup()


class TryOnKeyboard:
    """Клавиатуры для try-on"""
    
    @staticmethod
    def get_clothing_upload_keyboard() -> ReplyKeyboardMarkup:
        """Клавиатура для загрузки одежды"""
        builder = ReplyKeyboardBuilder()
        builder.add(
            KeyboardButton(text="📷 Загрузить фото одежды"),
            KeyboardButton(text="🔗 Отправить ссылку на одежду")
        )
        builder.adjust(1, 1, 1)
        return builder.as_markup(resize_keyboard=True)
    
    @staticmethod
    def get_tryon_result_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура для результата try-on"""
        builder = InlineKeyboardBuilder()
        builder.add(
            InlineKeyboardButton(text="🔄 Сгенерировать еще раз", callback_data="regenerate"),
            InlineKeyboardButton(text="💾 Сохранить результат", callback_data="save_result"),
            InlineKeyboardButton(text="📤 Поделиться", callback_data="share_result")
        )
        builder.adjust(2, 1, 1)
        return builder.as_markup()
    
    @staticmethod
    def get_subscription_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура подписки"""
        builder = InlineKeyboardBuilder()
        builder.add(
            InlineKeyboardButton(text="💎 Premium (5 генераций/месяц)", callback_data="subscribe_premium"),
            InlineKeyboardButton(text="📦 Пакет 10 генераций", callback_data="buy_package_10"),
            InlineKeyboardButton(text="📦 Пакет 25 генераций", callback_data="buy_package_25"),
            InlineKeyboardButton(text="ℹ️ О подписках", callback_data="subscription_info")
        )
        builder.adjust(1, 1, 1, 1)
        return builder.as_markup()
