from aiogram.fsm.state import State, StatesGroup


class UserStates(StatesGroup):
    """Состояния пользователя для FSM"""
    
    # Создание профиля
    waiting_for_selfie = State()           # Ждем селфи пользователя
    waiting_for_full_body = State()        # Ждем фото в полный рост
    
    # Try-on процесс
    waiting_for_clothing = State()         # Ждем фото одежды
    processing_tryon = State()             # Обрабатываем генерацию
    
    # Дополнительные состояния
    waiting_for_clothing_url = State()     # Ждем ссылку на одежду
    viewing_results = State()              # Просматриваем результаты
    settings = State()                     # Настройки профиля


class AdminStates(StatesGroup):
    """Состояния администратора"""
    
    waiting_for_broadcast = State()        # Ждем текст для рассылки
    waiting_for_photo = State()            # Ждем фото для рассылки
