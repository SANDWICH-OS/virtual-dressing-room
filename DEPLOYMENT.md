# 🚀 Railway Deployment Guide

## 📋 Подготовка к деплою

### 1. Создание аккаунта на Railway
1. Перейдите на [railway.app](https://railway.app)
2. Войдите через GitHub
3. Подключите ваш репозиторий

### 2. Настройка переменных окружения

В Railway Dashboard добавьте следующие переменные:

#### Обязательные:
```
BOT_TOKEN=your_telegram_bot_token_here
```

#### База данных (автоматически создается Railway):
```
DATABASE_URL=postgresql://... (автоматически)
```

#### Redis (автоматически создается Railway):
```
REDIS_URL=redis://... (автоматически)
```

#### AI/ML APIs (опционально):
```
OPENAI_API_KEY=your_openai_key
REPLICATE_API_TOKEN=your_replicate_token
```

#### Платежные системы (опционально):
```
YOOMONEY_SHOP_ID=your_shop_id
YOOMONEY_SECRET_KEY=your_secret_key
SBERPAY_MERCHANT_ID=your_merchant_id
SBERPAY_SECRET_KEY=your_secret_key
```

#### Файловое хранилище (опционально):
```
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

### 3. Автоматический деплой

Railway автоматически деплоит при каждом push в main ветку.

## 🔧 Локальная настройка

### Запуск production бота локально:
```bash
# Установите переменные окружения
export BOT_TOKEN="your_bot_token"
export DATABASE_URL="postgresql://..."

# Запустите бота
python3 production_bot.py
```

## 📊 Мониторинг

### Логи:
- Railway Dashboard → Logs
- Или через Railway CLI: `railway logs`

### Метрики:
- Railway Dashboard → Metrics
- CPU, Memory, Network usage

## 🐛 Отладка

### Проверка статуса:
```bash
railway status
```

### Просмотр логов:
```bash
railway logs
```

### Подключение к БД:
```bash
railway connect
```

## 🔄 Обновление

1. Внесите изменения в код
2. Закоммитьте и запушьте в main
3. Railway автоматически перезапустит бота

## 📝 Примечания

- Бот использует PostgreSQL в production
- Redis для кэширования и очередей
- Все файлы конфигурации готовы
- Автоматический рестарт при ошибках
