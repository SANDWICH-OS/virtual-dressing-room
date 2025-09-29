# Настройка интеграции с Fashn AI

## Описание

Интеграция с Fashn AI для генерации виртуальной примерки одежды с использованием webhook'ов для быстрой доставки результатов.

## Настройка API ключей

### 1. Получение API ключа Fashn AI

1. Зарегистрируйтесь на [app.fashn.ai](https://app.fashn.ai)
2. Перейдите в Developer API Dashboard
3. Создайте новый API ключ
4. **Важно**: Сохраните ключ сразу, так как его нельзя будет посмотреть повторно

### 2. Настройка переменных окружения

#### Локальная разработка (.env файл):
```bash
# Fashn AI API
FASHN_API_KEY=your_fashn_api_key_here
FASHN_WEBHOOK_URL=http://localhost:8001/webhook/fashn
```

#### Продакшн (Railway):
```bash
# Fashn AI API
FASHN_API_KEY=your_fashn_api_key_here
FASHN_WEBHOOK_URL=https://your-app.railway.app/webhook/fashn
```

### 3. Запуск webhook сервера

Для обработки webhook'ов от Fashn AI нужно запустить отдельный FastAPI сервер:

```bash
# Локально
python app/webhook_server.py

# Или через uvicorn
uvicorn app.webhook_server:app --host 0.0.0.0 --port 8001
```

## Архитектура интеграции

### 1. Основной бот (aiogram)
- Обрабатывает команды пользователей
- Отправляет запросы в Fashn AI
- Сохраняет контекст в Redis

### 2. Webhook сервер (FastAPI)
- Принимает webhook'и от Fashn AI
- Обрабатывает результаты генерации
- Отправляет результаты пользователям через Telegram

## Поток обработки

1. **Пользователь** вызывает `/test_fashn`
2. **Бот** проверяет наличие фото пользователя и одежды
3. **FashnService** отправляет запрос в Fashn AI с webhook URL
4. **Fashn AI** обрабатывает запрос и отправляет webhook
5. **Webhook сервер** получает результат и отправляет пользователю

## Тестирование

### 1. Локальное тестирование

1. Запустите основной бот:
```bash
python railway_bot_new.py
```

2. Запустите webhook сервер:
```bash
python app/webhook_server.py
```

3. Используйте ngrok для публичного URL:
```bash
ngrok http 8001
```

4. Обновите FASHN_WEBHOOK_URL в .env:
```bash
FASHN_WEBHOOK_URL=https://your-ngrok-url.ngrok.io/webhook/fashn
```

### 2. Продакшн тестирование

1. Убедитесь, что FASHN_API_KEY настроен в Railway
2. Убедитесь, что FASHN_WEBHOOK_URL указывает на ваш Railway домен
3. Запустите webhook сервер на Railway (добавьте в Procfile)

## Мониторинг

### Логи
- Все запросы к Fashn AI логируются через AILoggingService
- Webhook'и логируются в webhook_server
- Ошибки обрабатываются и логируются

### Health checks
- `/health` - основной бот
- `/webhook/fashn/health` - webhook сервер

## Обработка ошибок

### API-level ошибки:
- `400` - Неверный запрос
- `401` - Неверный API ключ
- `429` - Превышен лимит запросов или недостаточно кредитов
- `500` - Внутренняя ошибка сервера

### Runtime ошибки:
- `ImageLoadError` - Ошибка загрузки изображения
- `ContentModerationError` - Контент не прошел модерацию
- `PoseError` - Не удалось определить позу
- `PipelineError` - Ошибка обработки
- `ThirdPartyError` - Временная ошибка сервиса

## Настройка Railway

### 1. Добавьте в Railway переменные окружения:
```
FASHN_API_KEY=your_key_here
FASHN_WEBHOOK_URL=https://your-app.railway.app/webhook/fashn
```

### 2. Обновите Procfile для запуска webhook сервера:
```
web: python app/webhook_server.py
```

### 3. Убедитесь, что порт 8001 доступен в Railway

## Troubleshooting

### Проблема: Webhook не приходят
- Проверьте, что FASHN_WEBHOOK_URL доступен публично
- Убедитесь, что webhook сервер запущен
- Проверьте логи webhook сервера

### Проблема: Ошибка "API ключ не настроен"
- Убедитесь, что FASHN_API_KEY установлен
- Проверьте, что переменная окружения загружается правильно

### Проблема: Ошибка "Webhook URL не настроен"
- Убедитесь, что FASHN_WEBHOOK_URL установлен
- Проверьте, что URL доступен публично

## Безопасность

- Webhook'и не требуют аутентификации (Fashn AI не поддерживает подпись)
- Используйте HTTPS в продакшне
- Ограничьте доступ к webhook endpoint'ам
- Регулярно ротируйте API ключи
