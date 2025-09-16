from aiogram import Dispatcher
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from app.bot.states import UserStates
from app.bot.keyboards import MainKeyboard, ProfileKeyboard, TryOnKeyboard
from loguru import logger


async def handle_yes_callback(callback: CallbackQuery, state: FSMContext):
    """Обработчик кнопки 'Да'"""
    await callback.answer("✅ Подтверждено")
    await callback.message.edit_text("Отлично! Продолжаем...")
    logger.info(f"User {callback.from_user.id} pressed 'Yes'")


async def handle_no_callback(callback: CallbackQuery, state: FSMContext):
    """Обработчик кнопки 'Нет'"""
    await callback.answer("❌ Отменено")
    await callback.message.edit_text("Понятно. Что-то другое?")
    logger.info(f"User {callback.from_user.id} pressed 'No'")


async def handle_upload_selfie_callback(callback: CallbackQuery, state: FSMContext):
    """Обработчик загрузки селфи"""
    await callback.answer()
    await state.set_state(UserStates.waiting_for_selfie)
    await callback.message.edit_text(
        "📷 <b>Загрузи свое селфи</b>\n\nСделай фото анфас с хорошим освещением",
        reply_markup=None
    )
    logger.info(f"User {callback.from_user.id} started selfie upload")


async def handle_upload_fullbody_callback(callback: CallbackQuery, state: FSMContext):
    """Обработчик загрузки фото в полный рост"""
    await callback.answer()
    await state.set_state(UserStates.waiting_for_full_body)
    await callback.message.edit_text(
        "📸 <b>Загрузи фото в полный рост</b>\n\nВстань в нейтральной позе, руки по швам",
        reply_markup=None
    )
    logger.info(f"User {callback.from_user.id} started fullbody upload")


async def handle_delete_selfie_callback(callback: CallbackQuery, state: FSMContext):
    """Обработчик удаления селфи"""
    await callback.answer("🗑 Селфи удалено")
    await callback.message.edit_text("Селфи удалено. Загрузи новое фото:")
    logger.info(f"User {callback.from_user.id} deleted selfie")


async def handle_delete_fullbody_callback(callback: CallbackQuery, state: FSMContext):
    """Обработчик удаления фото в полный рост"""
    await callback.answer("🗑 Фото в полный рост удалено")
    await callback.message.edit_text("Фото в полный рост удалено. Загрузи новое фото:")
    logger.info(f"User {callback.from_user.id} deleted fullbody photo")


async def handle_regenerate_callback(callback: CallbackQuery, state: FSMContext):
    """Обработчик повторной генерации"""
    await callback.answer("🔄 Генерирую заново...")
    await callback.message.edit_text("⚡ Генерирую новое try-on изображение...")
    logger.info(f"User {callback.from_user.id} requested regeneration")


async def handle_save_result_callback(callback: CallbackQuery, state: FSMContext):
    """Обработчик сохранения результата"""
    await callback.answer("💾 Результат сохранен!")
    await callback.message.edit_text("✅ Результат сохранен в твою галерею")
    logger.info(f"User {callback.from_user.id} saved result")


async def handle_share_result_callback(callback: CallbackQuery, state: FSMContext):
    """Обработчик поделиться результатом"""
    await callback.answer("📤 Поделиться результатом")
    await callback.message.edit_text("🔗 Ссылка для sharing будет здесь")
    logger.info(f"User {callback.from_user.id} shared result")


async def handle_subscription_callback(callback: CallbackQuery, state: FSMContext):
    """Обработчик подписки"""
    subscription_type = callback.data.split("_")[-1]
    
    if subscription_type == "premium":
        await callback.answer("💎 Premium подписка")
        await callback.message.edit_text(
            "💎 <b>Premium подписка</b>\n\n5 генераций в месяц\nЦена: 299₽/месяц",
            reply_markup=TryOnKeyboard.get_subscription_keyboard()
        )
    elif subscription_type.startswith("package"):
        count = subscription_type.split("_")[1]
        await callback.answer(f"📦 Пакет {count} генераций")
        await callback.message.edit_text(
            f"📦 <b>Пакет {count} генераций</b>\n\nЦена: {int(count) * 50}₽",
            reply_markup=TryOnKeyboard.get_subscription_keyboard()
        )
    elif subscription_type == "info":
        await callback.answer("ℹ️ Информация о подписках")
        await callback.message.edit_text(
            "ℹ️ <b>Информация о подписках</b>\n\n"
            "💎 Premium: 5 генераций/месяц - 299₽\n"
            "📦 Пакет 10: 10 генераций - 500₽\n"
            "📦 Пакет 25: 25 генераций - 1000₽",
            reply_markup=TryOnKeyboard.get_subscription_keyboard()
        )
    
    logger.info(f"User {callback.from_user.id} viewed subscription: {subscription_type}")


def register_callback_handlers(dp: Dispatcher):
    """Регистрация обработчиков callback'ов"""
    dp.callback_query.register(handle_yes_callback, lambda c: c.data == "yes")
    dp.callback_query.register(handle_no_callback, lambda c: c.data == "no")
    dp.callback_query.register(handle_upload_selfie_callback, lambda c: c.data == "upload_selfie")
    dp.callback_query.register(handle_upload_fullbody_callback, lambda c: c.data == "upload_fullbody")
    dp.callback_query.register(handle_delete_selfie_callback, lambda c: c.data == "delete_selfie")
    dp.callback_query.register(handle_delete_fullbody_callback, lambda c: c.data == "delete_fullbody")
    dp.callback_query.register(handle_regenerate_callback, lambda c: c.data == "regenerate")
    dp.callback_query.register(handle_save_result_callback, lambda c: c.data == "save_result")
    dp.callback_query.register(handle_share_result_callback, lambda c: c.data == "share_result")
    dp.callback_query.register(handle_subscription_callback, lambda c: c.data.startswith("subscribe_") or c.data.startswith("buy_package_") or c.data == "subscription_info")
