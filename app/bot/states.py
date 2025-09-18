from aiogram.fsm.state import State, StatesGroup


class UserStates(StatesGroup):
    """Состояния пользователя для FSM согласно ТЗ"""
    
    # Основные состояния
    unauthorized = State()                 # 1. Неавторизован (до /start)
    authorized = State()                   # 2. Авторизован (после /start)
    
    # Загрузка фото
    waiting_user_photo = State()           # 3. Загрузка фото пользователя
    waiting_clothing_photo = State()       # 4. Загрузка фото одежды
    
    # Управление подпиской
    subscription_management = State()      # 5. Управление подпиской
    
    # Дополнительные состояния для обработки
    waiting_ai_response = State()          # Ждем ответ от ИИ сервиса


class AdminStates(StatesGroup):
    """Состояния администратора"""
    
    waiting_for_broadcast = State()        # Ждем текст для рассылки
    waiting_for_photo = State()            # Ждем фото для рассылки
