<!-- b9fcb0d7-d8f7-4139-aac0-0b2cabc58e52 b07a66c9-1902-4104-aea6-61ccedcf8c2d -->
# План: Хранение данных пользователей в Redis

## Проблема

При каждом деплое на Railway все данные пользователей стираются, потому что данные хранятся в SQLite внутри контейнера приложения.

## Упрощенная архитектура (ТОЛЬКО Redis)

```
┌─────────────────────────────────┐
│  Railway Bot Container          │
│  - MemoryStorage (FSM)          │ ← Сбрасывается при деплое
│  - SQLite (минимум, для логов)  │
└─────────────────────────────────┘
           ↓
┌─────────────────────────────────┐
│  Railway Redis (persistent)     │
│  - Базовые данные пользователей │ ← НЕ сбрасывается
│  - URL фото                     │
│  - Будущие: credits, подписки   │
└─────────────────────────────────┘
```

### Философия:

- **FSM в MemoryStorage** → при изменении логики флоу пользователи просто начинают заново (безопасно)
- **Данные в Redis** → основная информация о пользователе, URL фото сохраняются всегда
- **PostgreSQL** → добавим позже для истории операций
- **generation_count, credits, subscription** → проработаем отдельно в рамках фичи подписок

---

## Часть 1: Настройка Railway

### Шаг 1: Проверить/создать Redis сервис

В Railway dashboard:

1. Откройте ваш проект
2. Проверьте, есть ли сервис **Redis**

   - Если НЕТ: New → Database → Add Redis

3. Откройте Redis сервис → вкладка **Variables**
4. Найдите переменную `REDIS_URL` (формат: `redis://default:password@host:port`)

### Шаг 2: Настроить переменные окружения для бота

1. Откройте ваш **Bot сервис** (приложение Python)
2. Перейдите на вкладку **Variables**
3. Добавьте/обновите переменную `REDIS_URL`:

**Рекомендуемый способ (Reference Variable):**

- Нажмите "New Variable"
- Variable name: `REDIS_URL`
- Выберите тип "Reference" 
- Service: выберите ваш Redis сервис
- Variable: выберите `REDIS_URL`

**Альтернативный способ (копирование вручную):**

- Скопируйте значение `REDIS_URL` из Redis сервиса
- Вставьте в переменную `REDIS_URL` Bot сервиса

### Шаг 3: Проверка связи

После настройки бот автоматически передеплоится. Проверьте логи:

- Должна быть строка: `✅ Redis connected for user data: redis://...`
- НЕ должно быть: `⚠️ Using MemoryStorage as fallback`

---

## Часть 2: Изменения в коде

### 1. Убрать использование RedisStorage для FSM (`app/bot/bot.py`)

**Текущая проблема:** FSM использует Redis → старые состояния конфликтуют при изменении логики.

**Решение:** FSM в MemoryStorage, но Redis подключен для данных.

Изменить метод `create_bot` в файле `app/bot/bot.py`:

```python
async def create_bot():
    """Создание и настройка бота"""
    current_settings = get_settings()
    
    # Инициализируем базу данных
    await init_database()
    
    # Подключаем Redis ДЛЯ ДАННЫХ (не для FSM)
    redis_url = os.getenv("REDIS_URL", current_settings.redis_url)
    
    if redis_url and "localhost" not in redis_url and "127.0.0.1" not in redis_url:
        try:
            await redis_service.connect()
            logger.info(f"✅ Redis connected for user data: {redis_url}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            logger.warning("⚠️ Bot will work without Redis persistence")
    else:
        logger.warning("⚠️ Redis URL not configured, data will not persist")
    
    # FSM использует MemoryStorage (сбрасывается при деплое)
    from aiogram.fsm.storage.memory import MemoryStorage
    storage = MemoryStorage()
    logger.info("✅ Using MemoryStorage for FSM (states will reset on deploy)")
    
    # Создаем бота
    bot = Bot(token=current_settings.bot_token, parse_mode=ParseMode.HTML)
    
    # Создаем диспетчер
    dp = Dispatcher(storage=storage)
    
    # ... остальной код без изменений
```

### 2. Расширить RedisService (`app/services/redis_service.py`)

Добавить методы для работы с данными пользователя:

```python
# Добавить в класс RedisService:

async def get_user_data(self, user_id: int) -> Optional[dict]:
    """Получить все данные пользователя из Redis"""
    key = f"user:{user_id}:data"
    return await self.get_json(key)

async def set_user_data(self, user_id: int, data: dict, expire: Optional[int] = None) -> bool:
    """Сохранить данные пользователя в Redis (без expire = постоянно)"""
    key = f"user:{user_id}:data"
    return await self.set_json(key, data, expire=expire)

async def update_user_field(self, user_id: int, field: str, value: Any) -> bool:
    """Обновить конкретное поле пользователя"""
    user_data = await self.get_user_data(user_id) or {}
    user_data[field] = value
    return await self.set_user_data(user_id, user_data)

async def get_user_field(self, user_id: int, field: str, default: Any = None) -> Any:
    """Получить конкретное поле пользователя"""
    user_data = await self.get_user_data(user_id)
    if user_data:
        return user_data.get(field, default)
    return default

async def clear_user_data(self, user_id: int) -> bool:
    """Полная очистка всех данных пользователя из Redis"""
    keys_to_delete = [
        f"user:{user_id}:data",
        f"user:{user_id}:generations",  # старый ключ, если был
    ]
    
    deleted_count = 0
    for key in keys_to_delete:
        if await self.exists(key):
            await self.delete(key)
            deleted_count += 1
    
    logger.info(f"Cleared {deleted_count} Redis keys for user {user_id}")
    return deleted_count > 0
```

### 3. Обновить middleware регистрации (`app/bot/middleware/user_registration.py`)

При регистрации/обновлении пользователя сохраняем базовые данные в Redis.

Добавить в конец метода `get_or_create_user` (после `session.commit()`):

```python
from app.services.redis_service import redis_service

# Сохраняем/обновляем базовые данные в Redis
try:
    user_data = {
        "telegram_id": user.telegram_id,
        "username": user.username,
        "first_name": user.first_name,
        "subscription_type": user.subscription_type.value if user.subscription_type else "free",
    }
    await redis_service.set_user_data(telegram_user.id, user_data)
    logger.info(f"User {telegram_user.id} data saved to Redis")
except Exception as e:
    logger.error(f"Failed to save user {telegram_user.id} to Redis: {e}")
    # Не прерываем работу, если Redis недоступен
```

### 4. Обновить команду `/clear` (`app/bot/handlers/commands.py`)

Добавить очистку данных из Redis:

```python
async def clear_command(message: Message, state: FSMContext):
    """Обработчик команды /clear - очищает фото из БД и данные из Redis"""
    from app.database.async_session import get_async_session
    from app.models.user import User
    from app.models.photo import UserPhoto
    from app.services.redis_service import redis_service
    from sqlalchemy import select, delete
    
    user = message.from_user
    
    try:
        # Удаляем фото из БД
        async with get_async_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == user.id)
            )
            db_user = result.scalar_one_or_none()
            
            if db_user:
                await session.execute(
                    delete(UserPhoto).where(UserPhoto.user_id == db_user.id)
                )
                await session.commit()
                logger.info(f"User {user.id} cleared photos from database")
        
        # Очищаем данные из Redis
        await redis_service.clear_user_data(user.id)
        
        # Очищаем FSM состояние
        await state.clear()
        
        await message.answer(
            "🧹 <b>Данные очищены!</b>\n\nВсе загруженные фото, кеш и состояния сброшены.\nИспользуй /start для начала работы.",
            reply_markup=MainKeyboard.get_main_menu()
        )
        await state.set_state(UserStates.authorized)
        
    except Exception as e:
        logger.error(f"Error clearing data for user {user.id}: {e}")
        await state.clear()
        await message.answer(
            "⚠️ Произошла ошибка при очистке. Попробуй еще раз.",
            reply_markup=MainKeyboard.get_main_menu()
        )
        await state.set_state(UserStates.authorized)
```

### 5. Опционально: Сохранение URL фото в Redis

При сохранении фото в БД также можно сохранять URL в Redis для быстрого доступа.

В обработчике загрузки фото (файл `app/bot/handlers/photos.py`), после сохранения в БД:

```python
from app.services.redis_service import redis_service

# После успешного сохранения фото в БД
if photo_type == PhotoType.USER_PHOTO:
    await redis_service.update_user_field(user.id, "user_photo_url", photo_url)
elif photo_type == PhotoType.CLOTHING:
    await redis_service.update_user_field(user.id, "clothing_photo_url", photo_url)
```

---

## Часть 3: Структура данных в Redis

### Ключи Redis:

```
user:123456789:data → JSON с данными пользователя
```

### Базовая структура JSON:

```json
{
  "telegram_id": 123456789,
  "username": "username",
  "first_name": "Name",
  "subscription_type": "free",
  "user_photo_url": "https://cloudinary.com/...",
  "clothing_photo_url": "https://cloudinary.com/..."
}
```

### Добавление новых полей в будущем (для фичи подписок):

```python
# Пример: добавить кредиты
await redis_service.update_user_field(user_id, "credits", 100)

# Пример: проверить подписку
subscription = await redis_service.get_user_field(user_id, "subscription_type", "free")

# Пример: добавить счетчик генераций
await redis_service.update_user_field(user_id, "generation_count", 5)
```

---

## Тестирование

### 1. Тест базового сохранения данных:

1. Отправь `/start` боту
2. Проверь логи Railway - должна быть строка: `✅ Redis connected for user data`
3. Проверь логи - должна быть строка: `User <id> data saved to Redis`
4. Сделай **деплой** (push в main на GitHub)
5. После перезапуска отправь `/start` снова
6. ✅ Данные пользователя должны остаться в Redis

### 2. Тест очистки:

1. `/clear`
2. Проверь логи - должна быть строка: `Cleared N Redis keys for user <id>`
3. ✅ Данные из Redis удалены

### 3. Тест FSM сброса:

1. Начни загрузку фото `/upload_user_photo`
2. **НЕ** загружай фото, просто останови
3. Сделай деплой
4. После деплоя FSM состояние сброшено → пользователь вернется в начало флоу
5. Но базовые данные (имя, username) в Redis остались

### 4. Тест сохранения URL фото (опционально):

1. Загрузи фото пользователя
2. Загрузи фото одежды
3. Деплой
4. После перезапуска URL фото должны быть в Redis
5. Можно проверить через `/profile` или используя Redis CLI

---

## Будущие расширения

После этой фичи легко добавить (в рамках других задач):

- ✅ **Кредиты на балансе** (фича подписок)
- ✅ **Счетчик генераций** (фича подписок)
- ✅ **Дата окончания подписки** (фича подписок)
- ✅ **Лимиты генераций** (фича подписок)
- ✅ **История последних генераций** (отдельная фича)
- ✅ **Настройки пользователя** (отдельная фича)

PostgreSQL добавим позже для:

- История всех операций
- Платежи и транзакции  
- Аналитика и отчеты
- Долгосрочный backup

### To-dos

- [ ] Настроить  Redis сервисы в Railway и связать переменные окружения
- [ ] Исправить app/database/connection.py для использования production БД
- [ ] Расширить RedisService методами для работы с данными пользователя
- [ ] Создать новый UserDataService для синхронизации PostgreSQL ↔ Redis
- [ ] Обновить UserRegistrationMiddleware для загрузки данных в Redis
- [ ] Обновить команду /clear для очистки данных из Redis
- [ ] Заменить обращения к generation_count на использование UserDataService
- [ ] Протестировать сохранение данных после деплоя