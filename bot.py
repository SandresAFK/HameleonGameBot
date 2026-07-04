"""
🦎 Chameleon Game Bot for Telegram
"""

import logging
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ─── НАСТРОЙКИ ────────────────────────────────────────────────
import os
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветственное сообщение"""
    await update.message.reply_text(
        "🦎 *Chameleon Game Bot*\n\n"
        "Добавь меня в группу и используй команду /newgame чтобы начать игру!",
        parse_mode="Markdown"
    )


async def newgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает новую игру в группе"""
    if not update.effective_chat:
        return
    
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("Эта команда работает только в группах!")
        return
    
    # Получаем список участников группы
    try:
        chat_id = update.effective_chat.id
        members = []
        
        # Получаем администраторов
        admins = await context.bot.get_chat_administrators(chat_id)
        for admin in admins:
            if admin.user.id != context.bot.id:
                members.append(admin.user)
        
        # Если участников меньше 3, игра не имеет смысла
        if len(members) < 3:
            await update.message.reply_text(
                "❌ Нужно минимум 3 участника для игры!"
            )
            return
        
        # Выбираем случайное слово
        word = random.choice(WORDS)
        
        # Выбираем хамелеона
        chameleon = random.choice(members)
        
        # Отправляем сообщения каждому участнику
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
                        text=f"🎯 *Твое слово: {word}*\n\n"
                             "Найди хамелеона среди участников!",
                        parse_mode="Markdown"
                    )
            except Exception as e:
                logger.warning(f"Не удалось отправить сообщение пользователю {member.id}: {e}")
        
        # Сообщение в группе
        await update.message.reply_text(
            f"🎮 *Игра началась!*\n\n"
            f"Проверьте личные сообщения - я отправил каждому слово.\n"
            f"Один из вас - хамелеон! Найдите его!",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Ошибка при запуске игры: {e}")
        await update.message.reply_text(
            "❌ Произошла ошибка. Убедитесь, что я могу писать личные сообщения участникам."
        )


def main():
    if not BOT_TOKEN:
        raise RuntimeError("Не задан BOT_TOKEN. Установи переменную окружения BOT_TOKEN и перезапусти бота.")
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("newgame", newgame))
    
    print("🦎 Chameleon Game Bot запущен! Ctrl+C для остановки.")
    app.run_polling()


if __name__ == "__main__":
    main()
