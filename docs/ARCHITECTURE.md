# Архитектура проекта

## Обзор

Virtual Try-On Bot построен на основе микросервисной архитектуры с использованием современных технологий для обеспечения масштабируемости и надежности.

## 🏗️ Общая архитектура

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Telegram      │    │   Railway       │    │   External      │
│   Users         │◄──►│   Bot Service   │◄──►│   Services      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   PostgreSQL    │
                       │   Database      │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │     Redis       │
                       │   (FSM Store)   │
                       └─────────────────┘
```

## 📁 Структура компонентов

### 1. Bot Layer (Слой бота)

**Назначение**: Обработка сообщений от пользователей Telegram

**Компоненты**:
- `app/bot/bot.py` - Основная логика создания и запуска бота
- `app/bot/handlers/` - Обработчики команд и сообщений
- `app/bot/keyboards/` - Клавиатуры для пользовательского интерфейса
- `app/bot/middleware/` - Middleware для обработки запросов
- `app/bot/states.py` - FSM состояния пользователей

**Технологии**: aiogram 3.x, FSM (Finite State Machine)

### 2. Service Layer (Слой сервисов)

**Назначение**: Бизнес-логика и интеграция с внешними сервисами

**Компоненты**:
- `app/services/file_service.py` - Обработка и загрузка файлов
- `app/services/redis_service.py` - Работа с Redis
- `app/services/ai_logging_service.py` - Логирование ИИ запросов

**Технологии**: httpx, cloudinary, redis

### 3. Data Layer (Слой данных)

**Назначение**: Управление данными и персистентность

**Компоненты**:
- `app/database/` - Настройки подключения к БД
- `app/models/` - SQLAlchemy модели
- `migrations/` - Alembic миграции

**Технологии**: SQLAlchemy, PostgreSQL, Alembic

### 4. Utils Layer (Слой утилит)

**Назначение**: Вспомогательные функции и валидация

**Компоненты**:
- `app/utils/validators.py` - Валидация изображений

**Технологии**: PIL, httpx

## 🔄 Поток данных

### 1. Обработка сообщения пользователя

```
User Message → Middleware → Handler → Service → Database
     ↓              ↓          ↓         ↓         ↓
  Telegram      Logging    Command   Business   Storage
     API        Middleware  Logic     Logic     Layer
```

### 2. Загрузка фото

```
Photo Upload → Validation → Cloudinary → Database → Response
     ↓             ↓           ↓           ↓          ↓
  Telegram     Image Check   File Upload  Save URL   Success
     API       (PIL/httpx)   (Cloudinary) (SQLAlchemy) Message
```

### 3. FSM Управление состояниями

```
User Action → State Check → Handler → State Update → Response
     ↓            ↓           ↓           ↓            ↓
  Message     Current     Process     New State    Keyboard
  Received    State       Action      Set         Update
```

## 🗄️ Модель данных

### User (Пользователь)

```python
class User:
    id: int                    # Первичный ключ
    telegram_id: int           # ID в Telegram (уникальный)
    username: str              # Имя пользователя
    first_name: str            # Имя
    last_name: str             # Фамилия
    subscription_type: Enum    # Тип подписки (free/premium)
    generation_count: int      # Количество генераций
    created_at: datetime       # Дата создания
    updated_at: datetime       # Дата обновления
```

### UserPhoto (Фото пользователя)

```python
class UserPhoto:
    id: int                    # Первичный ключ
    user_id: int               # Внешний ключ на User
    photo_url: str             # URL фото
    photo_type: Enum           # Тип фото (user_photo/clothing)
    cloudinary_public_id: str  # ID в Cloudinary
    created_at: datetime       # Дата создания
    updated_at: datetime       # Дата обновления
```

## 🔧 Конфигурация

### Environment Variables

```env
# Обязательные
BOT_TOKEN=your_telegram_bot_token
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port

# Опциональные
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
RAILWAY_ENVIRONMENT=production
```

### Конфигурационные классы

- `app/config.py` - Локальная конфигурация
- `app/config_prod.py` - Продакшн конфигурация

## 🔄 FSM Состояния

### UserStates

1. **`unauthorized`** - Пользователь не авторизован
2. **`authorized`** - Пользователь авторизован
3. **`waiting_user_photo`** - Ожидание фото пользователя
4. **`waiting_clothing_photo`** - Ожидание фото одежды
5. **`subscription_management`** - Управление подпиской
6. **`waiting_ai_response`** - Ожидание ответа ИИ

### Переходы состояний

```
unauthorized → authorized (при /start)
authorized → waiting_user_photo (при загрузке фото пользователя)
authorized → waiting_clothing_photo (при загрузке фото одежды)
authorized → subscription_management (при /subscription)
waiting_* → authorized (после завершения операции)
```

## 🚀 Деплой

### Railway (Продакшн)

- Автоматический деплой при push в main
- Переменные окружения в Railway dashboard
- Автоматическое масштабирование

### Локальная разработка

- Запуск через `python railway_bot_new.py`
- Локальная база данных SQLite/PostgreSQL
- Локальный Redis или MemoryStorage

## 📊 Мониторинг и логирование

### Логирование

- **Structured logging** с помощью loguru
- Логи всех команд и сообщений
- Логи ошибок и исключений
- Логи ИИ запросов

### Метрики

- Количество активных пользователей
- Количество загруженных фото
- Время отклика команд
- Использование ресурсов

## 🔒 Безопасность

### Аутентификация

- Токен бота для аутентификации
- Middleware для проверки пользователей

### Валидация данных

- Валидация изображений (размер, формат)
- Санитизация пользовательского ввода
- Проверка типов файлов

### Хранение данных

- Шифрование чувствительных данных
- Безопасное хранение токенов
- Регулярные бэкапы базы данных

## 🔄 Интеграции

### Внешние сервисы

- **Telegram Bot API** - Основной интерфейс
- **Cloudinary** - Хранение изображений
- **PostgreSQL** - Основная база данных
- **Redis** - Кэширование и FSM

### Планируемые интеграции

- **VModel API** - Генерация try-on
- **Fashn API** - Альтернативная генерация
- **Pixelcut API** - Дополнительная генерация
- **YooMoney** - Платежи
- **SberPay** - Альтернативные платежи

## 📈 Масштабирование

### Горизонтальное масштабирование

- Stateless архитектура
- Внешнее хранение состояния (Redis)
- Load balancing через Railway

### Вертикальное масштабирование

- Увеличение ресурсов в Railway
- Оптимизация запросов к БД
- Кэширование часто используемых данных

## 🧪 Тестирование

### Типы тестов

- **Unit tests** - Тестирование отдельных функций
- **Integration tests** - Тестирование интеграций
- **E2E tests** - Тестирование полного потока

### Инструменты

- pytest для unit тестов
- httpx для тестирования API
- aiogram test framework для тестирования бота

## 📚 Документация

### Техническая документация

- README.md - Основная документация
- API.md - Документация API
- DEPLOYMENT.md - Руководство по развертыванию
- ARCHITECTURE.md - Архитектура проекта

### Код документация

- Docstrings для всех функций
- Type hints для типизации
- Комментарии для сложной логики
