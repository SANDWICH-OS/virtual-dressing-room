# Virtual Try-On Telegram Bot

Телеграм бот для виртуальной примерки одежды с использованием генеративных ИИ моделей.

## 🚀 Быстрый старт

### 1. Клонирование и установка зависимостей

```bash
# Установка зависимостей
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

```bash
# Скопируйте файл с примером переменных
cp env.example .env

# Отредактируйте .env файл, добавив ваши API ключи
nano .env
```

### 3. Настройка базы данных

```bash
# Запуск PostgreSQL и Redis через Docker
docker-compose up -d db redis

# Создание миграций
alembic revision --autogenerate -m "Initial migration"

# Применение миграций
alembic upgrade head
```

### 4. Запуск приложения

```bash
# Запуск в режиме разработки
python -m app.main

# Или через uvicorn
uvicorn app.main:app --reload
```

## 🏗 Структура проекта

```
app/
├── bot/              # Телеграм бот
├── database/         # Настройки БД и миграции
├── models/           # SQLAlchemy модели
├── services/         # Бизнес-логика
├── utils/            # Утилиты
└── main.py          # Точка входа FastAPI

migrations/           # Alembic миграции
requirements.txt      # Python зависимости
docker-compose.yml    # Docker конфигурация
```

## 🔧 Конфигурация

### Обязательные переменные окружения:

- `BOT_TOKEN` - токен телеграм бота
- `DATABASE_URL` - URL базы данных PostgreSQL
- `REDIS_URL` - URL Redis сервера

### Опциональные переменные:

- `REPLICATE_API_TOKEN` - токен Replicate API для генерации
- `OPENAI_API_KEY` - ключ OpenAI API
- `YOOMONEY_SHOP_ID` - ID магазина YooMoney
- `YOOMONEY_SECRET_KEY` - секретный ключ YooMoney
- `CLOUDINARY_CLOUD_NAME` - имя облака Cloudinary
- `CLOUDINARY_API_KEY` - API ключ Cloudinary
- `CLOUDINARY_API_SECRET` - секретный ключ Cloudinary

## 📊 API Endpoints

- `GET /` - Главная страница
- `GET /health` - Проверка здоровья сервиса

## 🐳 Docker

```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f app

# Остановка
docker-compose down
```

## 🗄 База данных

### Модели:

- **User** - пользователи бота
- **UserPhoto** - загруженные фото пользователей
- **TryOnRequest** - запросы на генерацию try-on
- **Payment** - платежи и подписки

### Миграции:

```bash
# Создание новой миграции
alembic revision --autogenerate -m "Description"

# Применение миграций
alembic upgrade head

# Откат миграции
alembic downgrade -1
```

## 🔄 Разработка

1. Создайте ветку для новой функции
2. Внесите изменения в код
3. Создайте миграцию БД (если нужно)
4. Протестируйте изменения
5. Создайте Pull Request

## 📝 TODO

- [ ] Реализация телеграм бота
- [ ] Интеграция с AI API
- [ ] Система платежей
- [ ] Тесты
- [ ] Документация API
