"""
🦎 Chameleon Game Bot for Telegram
"""

import logging
import random
import json
from pathlib import Path
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ─── НАСТРОЙКИ ────────────────────────────────────────────────
import os
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
USERS_FILE = Path("/data/users.json") if Path("/data").exists() else Path("users.json")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Список слов для игры
WORDS = [
    "поцелуй", "любовь", "форма", "дневник", "учительская", "столовая",
    "спортзал", "аквариум", "хомяк", "кошка", "собака", "бабушка",
    "дедушка", "подъезд", "лифт", "чердак", "подвал", "гараж", "дача",
    "палатка", "костёр", "гитара", "плеер", "наушники", "телефон",
    "ноутбук", "планшет", "камера", "скейт", "ролики", "велосипед",
    "самокат", "мороженое", "пицца", "бургер", "суши", "шаурма",
    "пельмени", "борщ", "компот", "чай", "кофе", "лимонад", "кола",
    "кино", "театр", "концерт", "дискотека", "библиотека", "парк",
    "пляж", "бассейн", "сауна", "баня"
]


# ─── УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ ─────────────────────────────────
def load_users():
    """Загружает список пользователей из файла"""
    if USERS_FILE.exists():
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Сохраняет список пользователей в файл"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def add_user(user_id, username, first_name):
    """Добавляет пользователя в список"""
    users = load_users()
    users[str(user_id)] = {
        "username": username,
        "first_name": first_name
    }
    save_users(users)

def get_all_users():
    """Возвращает всех пользователей"""
    return load_users()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветственное сообщение и регистрация пользователя"""
    user = update.effective_user
    add_user(user.id, user.username, user.first_name)
    
    await update.message.reply_text(
        "🦎 *Chameleon Game Bot*\n\n"
        "Ты зарегистрирован! Теперь добавь меня в группу и используй команду /newgame чтобы начать игру.",
        parse_mode="Markdown"
    )


async def newgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает новую игру в группе"""
    if not update.effective_chat:
        return
    
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("Эта команда работает только в группах!")
        return
    
    # Получаем список зарегистрированных пользователей
    try:
        users_dict = get_all_users()
        
        if not users_dict:
            await update.message.reply_text(
                "❌ Никто еще не зарегистрировался! Напишите мне в личку /start"
            )
            return
        
        # Преобразуем в список объектов пользователей
        from types import SimpleNamespace
        members = []
        for user_id, user_data in users_dict.items():
            user = SimpleNamespace()
            user.id = int(user_id)
            user.username = user_data.get("username")
            user.first_name = user_data.get("first_name")
            members.append(user)
        
        # Если участников меньше 3, игра не имеет смысла
        if len(members) < 3:
            await update.message.reply_text(
                "❌ Нужно минимум 3 зарегистрированных участника для игры! Напишите мне в личку /start"
            )
            return
        
        # Выбираем случайное слово
        word = random.choice(WORDS)
        
        # Выбираем хамелеона
        chameleon = random.choice(members)
        
        # Отправляем сообщения каждому участнику
        sent_count = 0
        for member in members:
            try:
                if member.id == chameleon.id:
                    # Хамелеон получает особое сообщение
                    await context.bot.send_message(
                        chat_id=member.id,
                        text="🦎 *Ты хамелеон!*\n\nШифруйся. Не дай себя раскусить!",
                        parse_mode="Markdown"
                    )
                else:
                    # Остальные получают слово
                    await context.bot.send_message(
                        chat_id=member.id,
                        text=f"Секретное слово: {word}. Найди хамелеона!",
                        parse_mode="Markdown"
                    )
                sent_count += 1
            except Exception as e:
                logger.warning(f"Не удалось отправить сообщение пользователю {member.id}: {e}")
        
        # Сообщение в группе
        await update.message.reply_text(
            f"🎮 *Игра началась!*\n\n"
            f"Отправил слова {sent_count} зарегистрированным игрокам.\n"
            f"Проверьте личные сообщения!\n"
            f"Один из вас - хамелеон! Найдите его!",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Ошибка при запуске игры: {e}")
        await update.message.reply_text(
            "❌ Произошла ошибка. Убедитесь, что пользователи написали мне в личку /start"
        )


def main():
    if not BOT_TOKEN:
        raise RuntimeError("Не задан BOT_TOKEN. Установи переменную окружения BOT_TOKEN и перезапусти бота.")
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("newgame", newgame))
    app.add_handler(CommandHandler("cnewgame", newgame))
    
    print("🦎 Chameleon Game Bot запущен! Ctrl+C для остановки.")
    app.run_polling()


if __name__ == "__main__":
    main()
