from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from app.bot.states import UserStates
from app.bot.keyboards import MainKeyboard
from app.services.ai_logging_service import ai_logging_service
from loguru import logger
import asyncio
from datetime import datetime


async def start_command(message: Message, state: FSMContext):
    """
    Обработчик команды /start
    
    Приветствует пользователя, показывает доступные команды
    и переводит в состояние 'authorized'.
    
    Args:
        message: Сообщение от пользователя
        state: FSM контекст для управления состояниями
    """
    user = message.from_user
    
    # Очищаем состояние
    await state.clear()
    
    # Приветственное сообщение
    welcome_text = f"""
👋 <b>Добро пожаловать в Virtual Try-On Bot!</b>

Привет, {user.first_name}! Я помогу тебе примерить одежду виртуально с помощью ИИ.

🎯 <b>Доступные команды:</b>
/help - Список команд
/profile - Информация о профиле
/clear - Очистить данные
/upload_user_photo - Загрузить фото пользователя
/upload_clothing_photo - Загрузить фото одежды
/test_vmodel - Тест VModel API
/test_fashn - Тест Fashn API
/test_pixelcut - Тест Pixelcut API
/subscription - Управление подпиской
/back - Вернуться в главное меню

🚀 <b>Начнем работу!</b>
    """
    
    await message.answer(
        welcome_text,
        reply_markup=MainKeyboard.get_main_menu()
    )
    
    # Переводим в состояние авторизован
    await state.set_state(UserStates.authorized)
    
    logger.info(f"User {user.id} started bot")


async def help_command(message: Message, state: FSMContext):
    """Обработчик команды /help"""
    
    help_text = """
❓ <b>Помощь по использованию бота</b>

🎯 <b>Основные команды:</b>
/start - Начать работу с ботом
/help - Показать эту справку
/profile - Управление профилем

🤖 <b>Тестирование ИИ сервисов:</b>
/test_vmodel - Тест VModel API
/test_fashn - Тест Fashn API
/test_pixelcut - Тест Pixelcut API

📸 <b>Как создать try-on:</b>
1. Загрузи свое селфи
2. Загрузи фото в полный рост
3. Загрузи фото одежды
4. Выбери ИИ сервис для генерации
5. Получи результат!

💡 <b>Советы для лучшего результата:</b>
• Используй качественные фото
• Селфи делай анфас с хорошим освещением
• Фото в полный рост - в нейтральной позе
• Одежду фотографируй на белом фоне

❓ <b>Проблемы?</b>
Если что-то не работает, напиши @support
    """
    
    await message.answer(help_text)
    logger.info(f"User {message.from_user.id} requested help")


async def profile_command(message: Message, state: FSMContext):
    """
    Обработчик команды /profile
    
    Показывает информацию о профиле пользователя:
    - ID пользователя, имя, подписка
    - Количество загруженных фото (пользователь/одежда)
    - Дата регистрации и количество генераций
    
    Args:
        message: Сообщение от пользователя
        state: FSM контекст для управления состояниями
    """
    from app.database.async_session import get_async_session
    from app.models.user import User
    from app.models.photo import UserPhoto, PhotoType
    from sqlalchemy import select, func, delete
    
    # Очищаем состояние
    await state.clear()
    
    user = message.from_user
    
    try:
        # Получаем информацию о пользователе из БД
        async with get_async_session() as session:
            # Получаем пользователя
            result = await session.execute(
                select(User).where(User.telegram_id == user.id)
            )
            db_user = result.scalar_one_or_none()
            
            # Получаем количество загруженных фото
            if db_user:
                logger.info(f"Profile: Looking for photos with user_id = {db_user.id}")
                user_photo_count = await session.scalar(
                    select(func.count(UserPhoto.id)).where(
                        UserPhoto.user_id == db_user.id,
                        UserPhoto.photo_type == PhotoType.USER_PHOTO
                    )
                ) or 0
                
                clothing_count = await session.scalar(
                    select(func.count(UserPhoto.id)).where(
                        UserPhoto.user_id == db_user.id,
                        UserPhoto.photo_type == PhotoType.CLOTHING
                    )
                ) or 0
                
                logger.info(f"Profile: Found {user_photo_count} user photos, {clothing_count} clothing photos")
            else:
                user_photo_count = 0
                clothing_count = 0
                logger.info("Profile: No user found in database")
            
            # Формируем информацию о профиле
            if db_user:
                subscription_info = "🆓 Бесплатная" if db_user.subscription_type == "free" else f"💎 {db_user.subscription_type.title()}"
                generation_count = db_user.generation_count or 0
                created_at = db_user.created_at.strftime("%d.%m.%Y") if db_user.created_at else "Неизвестно"
            else:
                subscription_info = "🆓 Бесплатная"
                generation_count = 0
                created_at = "Неизвестно"
            
            profile_text = f"""
👤 <b>Мой профиль</b>

🆔 <b>ID:</b> {user.id}
👤 <b>Имя:</b> {user.first_name or 'Не указано'}
📧 <b>Username:</b> @{user.username or 'Не указан'}
💳 <b>Подписка:</b> {subscription_info}
🎨 <b>Генераций использовано:</b> {generation_count}
📅 <b>Дата регистрации:</b> {created_at}

📸 <b>Загруженные фото:</b>
• Пользователь: {'✅ Да' if user_photo_count > 0 else '❌ Нет'}
• Одежда: {'✅ Да' if clothing_count > 0 else '❌ Нет'}

{'✅ Профиль готов к использованию!' if user_photo_count > 0 and clothing_count > 0 else '⚠️ Загрузи фото для создания профиля'}
            """
            
            await message.answer(
                profile_text,
                reply_markup=MainKeyboard.get_main_menu()
            )
            # Остаемся в состоянии authorized
            await state.set_state(UserStates.authorized)
            
    except Exception as e:
        logger.error(f"Error getting profile info for user {user.id}: {e}")
        # Fallback информация без БД
        profile_text = f"""
👤 <b>Мой профиль</b>

🆔 <b>ID:</b> {user.id}
👤 <b>Имя:</b> {user.first_name or 'Не указано'}
📧 <b>Username:</b> @{user.username or 'Не указан'}
💳 <b>Подписка:</b> 🆓 Бесплатная
🎨 <b>Генераций использовано:</b> 0
📅 <b>Дата регистрации:</b> Неизвестно

📸 <b>Загруженные фото:</b>
• Пользователь: ❌ Нет
• Одежда: ❌ Нет

⚠️ Загрузи фото для создания профиля
        """
        
        await message.answer(
            profile_text,
            reply_markup=MainKeyboard.get_main_menu()
        )
        # Остаемся в состоянии authorized
        await state.set_state(UserStates.authorized)
    
    logger.info(f"User {message.from_user.id} viewed profile")


async def test_fashn_command(message: Message, state: FSMContext):
    """Обработчик команды /test_fashn"""
    user = message.from_user
    
    # Проверяем наличие фото пользователя и одежды
    try:
        from app.database.async_session import get_async_session
        from app.models.user import User
        from app.models.photo import UserPhoto, PhotoType
        from sqlalchemy import select, and_
        
        async with get_async_session() as session:
            # Сначала получаем пользователя из БД
            user_result = await session.execute(
                select(User).where(User.telegram_id == user.id)
            )
            db_user = user_result.scalar_one_or_none()
            
            if not db_user:
                await message.answer(
                    "❌ Пользователь не найден в базе данных. Используй /start для регистрации.",
                    reply_markup=MainKeyboard.get_main_menu()
                )
                return
            
            # Проверяем фото пользователя
            user_photo_result = await session.execute(
                select(UserPhoto).where(
                    and_(UserPhoto.user_id == db_user.id, UserPhoto.photo_type == PhotoType.USER_PHOTO)
                )
            )
            user_photo = user_photo_result.scalar_one_or_none()
            
            # Проверяем фото одежды
            clothing_photo_result = await session.execute(
                select(UserPhoto).where(
                    and_(UserPhoto.user_id == db_user.id, UserPhoto.photo_type == PhotoType.CLOTHING)
                )
            )
            clothing_photo = clothing_photo_result.scalar_one_or_none()
            
            if not user_photo or not clothing_photo:
                missing_photos = []
                if not user_photo:
                    missing_photos.append("фото пользователя")
                if not clothing_photo:
                    missing_photos.append("фото одежды")
                
                await message.answer(
                    f"❌ Сначала загрузи {', '.join(missing_photos)}!\n\nИспользуй команды:\n/upload_user_photo - загрузить фото пользователя\n/upload_clothing_photo - загрузить фото одежды",
                    reply_markup=MainKeyboard.get_main_menu()
                )
                return
                
    except Exception as e:
        logger.error(f"Error checking photos for user {user.id}: {e}")
        await message.answer(
            "❌ Ошибка при проверке фото. Попробуй еще раз.",
            reply_markup=MainKeyboard.get_main_menu()
        )
        return
    
    # Импортируем FashnService
    from app.services.fashn_service import fashn_service
    from app.services.redis_service import redis_service
    
    start_time = datetime.now()
    
    # Логируем запрос
    await ai_logging_service.log_ai_request(
        user_id=user.id,
        service_name="Fashn",
        request_data={"type": "try_on_generation", "user_photos": "loaded", "command": "/test_fashn"},
        start_time=start_time
    )
    
    await state.set_state(UserStates.waiting_ai_response)
    await message.answer(
        "👗 <b>Тестируем Fashn...</b>\n\nОтправляю твои фото в Fashn API для генерации try-on изображения.\nЭто может занять 30-60 секунд.",
        reply_markup=MainKeyboard.get_main_menu()
    )
    
    # Отправляем запрос в Fashn AI
    success, response_message, prediction_id = await fashn_service.submit_tryon_request(
        user_photo_url=user_photo.photo_url,
        clothing_photo_url=clothing_photo.photo_url,
        user_id=user.id
    )
    
    if success and prediction_id:
        # Сохраняем контекст для webhook обработки
        await redis_service.set_json(
            f"fashn_prediction:{prediction_id}",
            {
                "user_id": user.id,
                "start_time": start_time.isoformat(),
                "user_photo_url": user_photo.photo_url,
                "clothing_photo_url": clothing_photo.photo_url
            },
            expire=3600  # 1 час
        )
        
        await message.answer(
            f"✅ <b>Запрос отправлен в Fashn AI!</b>\n\n{response_message}\n\nОжидайте результат через webhook...",
            reply_markup=MainKeyboard.get_main_menu()
        )
        
        logger.info(f"User {user.id} submitted Fashn request with prediction ID: {prediction_id}")
    else:
        # Обработка ошибок
        await state.set_state(UserStates.authorized)
        await message.answer(
            f"❌ <b>Ошибка Fashn AI</b>\n\n{response_message}",
            reply_markup=MainKeyboard.get_main_menu()
        )
        
        # Логируем ошибку
        await ai_logging_service.log_ai_response(
            user_id=user.id,
            service_name="Fashn",
            response_data={"error": message},
            processing_time=(datetime.now() - start_time).total_seconds(),
            success=False,
            error_message=message
        )
        
        logger.error(f"Fashn request failed for user {user.id}: {message}")



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


async def upload_user_photo_command(message: Message, state: FSMContext):
    """Обработчик команды /upload_user_photo"""
    await state.set_state(UserStates.waiting_user_photo)
    await message.answer(
        "📷 <b>Загрузка фото пользователя</b>\n\nБот готов принять твое фото. Загрузи селфи для создания профиля.\n\n💡 <b>Советы:</b>\n• Делай фото анфас с хорошим освещением\n• Лицо должно быть хорошо видно\n• Избегай теней и бликов",
        reply_markup=MainKeyboard.get_back_keyboard()
    )
    logger.info(f"User {message.from_user.id} started user photo upload")


async def upload_clothing_photo_command(message: Message, state: FSMContext):
    """Обработчик команды /upload_clothing_photo"""
    await state.set_state(UserStates.waiting_clothing_photo)
    await message.answer(
        "👗 <b>Загрузка фото одежды</b>\n\nБот готов принять фото одежды. Загрузи фото предмета одежды.\n\n💡 <b>Советы:</b>\n• Фотографируй на белом фоне\n• Одежда должна быть хорошо видна\n• Избегай теней и складок",
        reply_markup=MainKeyboard.get_back_keyboard()
    )
    logger.info(f"User {message.from_user.id} started clothing photo upload")


async def subscription_command(message: Message, state: FSMContext):
    """Обработчик команды /subscription"""
    await state.set_state(UserStates.subscription_management)
    await message.answer(
        "💳 <b>Управление подпиской</b>\n\nЗдесь будет информация о подписках и лимитах.\nПока что эта функция в разработке.",
        reply_markup=MainKeyboard.get_back_keyboard()
    )
    logger.info(f"User {message.from_user.id} opened subscription management")


async def back_command(message: Message, state: FSMContext):
    """Обработчик команды /back"""
    await state.set_state(UserStates.authorized)
    await message.answer(
        "🏠 <b>Главное меню</b>\n\nВыбери команду или используй кнопки ниже:",
        reply_markup=MainKeyboard.get_main_menu()
    )
    logger.info(f"User {message.from_user.id} returned to main menu")




def register_command_handlers(dp: Dispatcher):
    """Регистрация обработчиков команд"""
    dp.message.register(start_command, Command("start"))
    dp.message.register(help_command, Command("help"))
    dp.message.register(profile_command, Command("profile"))
    dp.message.register(clear_command, Command("clear"))
    dp.message.register(upload_user_photo_command, Command("upload_user_photo"))
    dp.message.register(upload_clothing_photo_command, Command("upload_clothing_photo"))
    dp.message.register(subscription_command, Command("subscription"))
    dp.message.register(back_command, Command("back"))
    dp.message.register(test_fashn_command, Command("test_fashn"))
    dp.message.register(back_command, lambda m: m.text == "🔙 Назад")
