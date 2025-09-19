# Руководство по развертыванию

## Обзор

Данное руководство описывает процесс развертывания Virtual Try-On Bot на различных платформах.

## 🚀 Railway (Рекомендуется)

### Предварительные требования

1. Аккаунт на [Railway](https://railway.app)
2. GitHub репозиторий с кодом
3. Токен Telegram бота

### Шаги развертывания

#### 1. Подключение репозитория

1. Войдите в Railway dashboard
2. Нажмите "New Project"
3. Выберите "Deploy from GitHub repo"
4. Выберите ваш репозиторий
5. Railway автоматически определит Python проект

#### 2. Настройка переменных окружения

В Railway dashboard перейдите в Settings → Variables и добавьте:

```env
BOT_TOKEN=your_telegram_bot_token
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port
RAILWAY_ENVIRONMENT=production
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

#### 3. Настройка базы данных

Railway автоматически создаст PostgreSQL базу данных. URL будет доступен в переменной `DATABASE_URL`.

#### 4. Настройка Redis

Railway предоставляет Redis как сервис. URL будет доступен в переменной `REDIS_URL`.

#### 5. Настройка Railway.json

Убедитесь, что файл `railway.json` содержит:

```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python3 railway_bot_new.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Автоматическое развертывание

После настройки Railway будет автоматически развертывать бота при каждом push в main ветку.

## 🐳 Docker

### Создание образа

```bash
# Сборка образа
docker build -t virtual-tryon-bot .

# Запуск контейнера
docker run -d \
  --name virtual-tryon-bot \
  -e BOT_TOKEN=your_token \
  -e DATABASE_URL=your_db_url \
  -e REDIS_URL=your_redis_url \
  virtual-tryon-bot
```

### Docker Compose

```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f app

# Остановка
docker-compose down
```

## 🖥️ Локальная разработка

### Установка зависимостей

```bash
# Создание виртуального окружения
python -m venv venv

# Активация окружения
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

### Настройка переменных окружения

```bash
# Копирование примера
cp env.example .env

# Редактирование .env файла
nano .env
```

### Запуск

```bash
# Запуск бота
python railway_bot_new.py
```

## 🔧 Настройка базы данных

### PostgreSQL

1. Установите PostgreSQL
2. Создайте базу данных:
```sql
CREATE DATABASE virtual_tryon;
```

3. Настройте переменную `DATABASE_URL`:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/virtual_tryon
```

### Redis

1. Установите Redis
2. Запустите сервер:
```bash
redis-server
```

3. Настройте переменную `REDIS_URL`:
```env
REDIS_URL=redis://localhost:6379
```

## 📊 Мониторинг

### Логи

Railway предоставляет встроенный просмотр логов в dashboard.

Для локальной разработки логи выводятся в консоль.

### Метрики

- Количество активных пользователей
- Количество загруженных фото
- Время отклика API
- Использование памяти и CPU

## 🔒 Безопасность

### Переменные окружения

- Никогда не коммитьте `.env` файлы
- Используйте сильные пароли для базы данных
- Регулярно обновляйте токены API

### Сетевая безопасность

- Используйте HTTPS для продакшн
- Настройте firewall для базы данных
- Ограничьте доступ к Redis

## 🚨 Устранение неполадок

### Частые проблемы

1. **Ошибка подключения к базе данных**
   - Проверьте правильность `DATABASE_URL`
   - Убедитесь, что база данных запущена

2. **Ошибка подключения к Redis**
   - Проверьте правильность `REDIS_URL`
   - Убедитесь, что Redis запущен

3. **Бот не отвечает**
   - Проверьте правильность `BOT_TOKEN`
   - Убедитесь, что бот запущен

### Логи для отладки

```bash
# Просмотр логов Railway
railway logs

# Просмотр логов Docker
docker logs virtual-tryon-bot

# Локальные логи
tail -f logs/bot.log
```

## 📈 Масштабирование

### Горизонтальное масштабирование

Railway автоматически масштабирует приложение при необходимости.

### Вертикальное масштабирование

В Railway dashboard можно изменить план подписки для увеличения ресурсов.

## 🔄 Обновления

### Автоматические обновления

Railway автоматически развертывает обновления при push в main ветку.

### Ручные обновления

```bash
# Остановка текущей версии
railway down

# Развертывание новой версии
railway up
```

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи приложения
2. Убедитесь в правильности переменных окружения
3. Создайте issue в GitHub репозитории
4. Обратитесь к документации Railway
