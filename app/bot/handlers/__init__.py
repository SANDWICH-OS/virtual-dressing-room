from .commands import register_command_handlers
from .photos import register_photo_handlers
from .ai_testing import register_ai_testing_handlers

def register_handlers(dp):
    """Регистрация всех обработчиков"""
    register_command_handlers(dp)
    register_photo_handlers(dp)
    register_ai_testing_handlers(dp)
