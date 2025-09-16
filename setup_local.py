#!/usr/bin/env python3
"""
Скрипт для настройки локального окружения
"""

import subprocess
import sys
import os
from pathlib import Path
from loguru import logger

def run_command(command, description):
    """Выполнить команду с логированием"""
    logger.info(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        logger.info(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} failed: {e}")
        logger.error(f"Error output: {e.stderr}")
        return False

def main():
    """Главная функция настройки"""
    logger.info("🚀 Setting up local environment...")
    
    # Проверяем Python версию
    if sys.version_info < (3, 11):
        logger.error("❌ Python 3.11+ required. Current version: {sys.version}")
        return False
    
    logger.info(f"✅ Python version: {sys.version}")
    
    # Устанавливаем зависимости
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        return False
    
    # Устанавливаем python-dotenv если не установлен
    if not run_command("pip install python-dotenv", "Installing python-dotenv"):
        return False
    
    # Создаем .env файл если не существует
    env_file = Path(".env")
    if not env_file.exists():
        logger.info("📝 Creating .env file...")
        try:
            with open("env.local", "r") as src:
                content = src.read()
            with open(".env", "w") as dst:
                dst.write(content)
            logger.info("✅ .env file created from env.local")
        except Exception as e:
            logger.error(f"❌ Error creating .env file: {e}")
            return False
    else:
        logger.info("✅ .env file already exists")
    
    # Инициализируем базу данных
    logger.info("🗄️ Initializing database...")
    try:
        result = subprocess.run([sys.executable, "init_db.py"], check=True, capture_output=True, text=True)
        logger.info("✅ Database initialized")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Database initialization failed: {e}")
        logger.error(f"Error output: {e.stderr}")
        return False
    
    logger.info("🎉 Local environment setup completed!")
    logger.info("")
    logger.info("📋 Next steps:")
    logger.info("1. Get bot token from @BotFather")
    logger.info("2. Update BOT_TOKEN in .env file")
    logger.info("3. Run: python start_local.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

