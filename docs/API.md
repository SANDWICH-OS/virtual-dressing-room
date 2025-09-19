# API Документация

## Обзор

Virtual Try-On Bot предоставляет REST API для управления пользователями, фото и тестирования ИИ сервисов.

## Базовый URL

- **Локальная разработка**: `http://localhost:8000`
- **Продакшн**: `https://your-railway-app.railway.app`

## Аутентификация

API использует токен бота для аутентификации. Токен передается в заголовке:

```
Authorization: Bearer YOUR_BOT_TOKEN
```

## Endpoints

### 1. Проверка здоровья

```http
GET /health
```

**Описание**: Проверяет состояние сервиса и подключения к внешним сервисам.

**Ответ**:
```json
{
  "status": "healthy",
  "redis": "connected",
  "debug": false
}
```

### 2. Главная страница

```http
GET /
```

**Описание**: Возвращает информацию о сервисе.

**Ответ**:
```json
{
  "message": "Virtual Try-On Bot API",
  "status": "running"
}
```

## Модели данных

### User

```json
{
  "id": 1,
  "telegram_id": 123456789,
  "username": "username",
  "first_name": "Имя",
  "last_name": "Фамилия",
  "subscription_type": "free",
  "generation_count": 0,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### UserPhoto

```json
{
  "id": 1,
  "user_id": 1,
  "photo_url": "https://example.com/photo.jpg",
  "photo_type": "user_photo",
  "cloudinary_public_id": "photo_123",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

## Коды ошибок

- `200` - Успешный запрос
- `400` - Неверный запрос
- `401` - Не авторизован
- `404` - Не найдено
- `500` - Внутренняя ошибка сервера

## Примеры использования

### Проверка состояния сервиса

```bash
curl -X GET "https://your-app.railway.app/health" \
  -H "Authorization: Bearer YOUR_BOT_TOKEN"
```

### Получение информации о сервисе

```bash
curl -X GET "https://your-app.railway.app/" \
  -H "Authorization: Bearer YOUR_BOT_TOKEN"
```

## Ограничения

- API доступен только для авторизованных пользователей
- Лимит запросов: 100 запросов в минуту на пользователя
- Максимальный размер загружаемого файла: 20MB
- Поддерживаемые форматы изображений: JPEG, PNG, WEBP

## Поддержка

Для получения поддержки обратитесь к разработчикам или создайте issue в репозитории проекта.
