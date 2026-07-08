"""
🦎 Chameleon Game Bot for Telegram
"""

import logging
import random
import json
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ─── НАСТРОЙКИ ────────────────────────────────────────────────
import os
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
USERS_FILE = Path("/data/users.json") if Path("/data").exists() else Path("users.json")
SCORES_FILE = Path("/data/scores.json") if Path("/data").exists() else Path("scores.json")
GAMES_FILE = Path("/data/games.json") if Path("/data").exists() else Path("games.json")

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


# ─── УПРАВЛЕНИЕ ОЧКАМИ ────────────────────────────────────────
def load_scores():
    """Загружает очки из файла"""
    if SCORES_FILE.exists():
        with open(SCORES_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_scores(scores):
    """Сохраняет очки в файл"""
    with open(SCORES_FILE, 'w') as f:
        json.dump(scores, f)

def add_score(user_id, points):
    """Добавляет очки пользователю"""
    scores = load_scores()
    user_id_str = str(user_id)
    scores[user_id_str] = scores.get(user_id_str, 0) + points
    save_scores(scores)

def get_score(user_id):
    """Возвращает очки пользователя"""
    scores = load_scores()
    return scores.get(str(user_id), 0)


# ─── УПРАВЛЕНИЕ ИГРАМИ ─────────────────────────────────────────
def load_games():
    """Загружает активные игры из файла"""
    if GAMES_FILE.exists():
        with open(GAMES_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_games(games):
    """Сохраняет активные игры в файл"""
    with open(GAMES_FILE, 'w') as f:
        json.dump(games, f)

def save_game(chat_id, chameleon_id, word, members):
    """Сохраняет информацию об активной игре"""
    games = load_games()
    games[str(chat_id)] = {
        "chameleon_id": chameleon_id,
        "word": word,
        "members": [m.id for m in members],
        "votes": {}
    }
    save_games(games)

def get_game(chat_id):
    """Возвращает информацию об активной игре"""
    games = load_games()
    return games.get(str(chat_id))

def delete_game(chat_id):
    """Удаляет активную игру"""
    games = load_games()
    if str(chat_id) in games:
        del games[str(chat_id)]
        save_games(games)


def get_vote_winner(votes, members):
    vote_counts = {}
    for voted_for_id in votes.values():
        vote_counts[voted_for_id] = vote_counts.get(voted_for_id, 0) + 1

    if not vote_counts:
        return None, vote_counts

    max_votes = max(vote_counts.values())
    leaders = [member_id for member_id, count in vote_counts.items() if count == max_votes]

    if len(leaders) != 1:
        return None, vote_counts

    if max_votes <= len(members) / 2:
        return None, vote_counts

    return leaders[0], vote_counts


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветственное сообщение и регистрация пользователя"""
    user = update.effective_user
    add_user(user.id, user.username, user.first_name)
    
    await update.message.reply_text(
        "🦎 *Chameleon Game Bot*\n\n"
        "Ты зарегистрирован! Теперь добавь меня в группу и используй команду /newgame чтобы начать игру.",
        parse_mode="Markdown"
    )


async def scores(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает таблицу лидеров"""
    scores = load_scores()
    users = load_users()
    
    if not scores:
        await update.message.reply_text("🏆 Пока нет очков! Начните игру с /newgame")
        return
    
    # Сортируем по очкам
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    lines = ["🏆 *Таблица лидеров*\n"]
    for i, (user_id_str, score) in enumerate(sorted_scores[:10]):
        user_data = users.get(user_id_str, {})
        name = user_data.get("first_name", f"User {user_id_str}")
        username = user_data.get("username")
        if username:
            name = f"@{username}"
        medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i + 1}."
        lines.append(f"{medal} {name} — *{score}* очков")
    
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def remove_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удаляет пользователя из системы"""
    if not context.args:
        await update.message.reply_text("Использование: /remove @username или /remove user_id")
        return
    
    target = context.args[0]
    users = load_users()
    scores = load_scores()
    
    # Если указан username
    if target.startswith("@"):
        target = target[1:]
        user_id_to_remove = None
        for user_id_str, user_data in users.items():
            if user_data.get("username") == target:
                user_id_to_remove = user_id_str
                break
        
        if not user_id_to_remove:
            await update.message.reply_text(f"❌ Пользователь @{target} не найден")
            return
    else:
        # Если указан user_id
        user_id_to_remove = target
        if user_id_to_remove not in users:
            await update.message.reply_text(f"❌ Пользователь с ID {target} не найден")
            return
    
    # Удаляем пользователя
    user_name = users[user_id_to_remove].get("first_name", users[user_id_to_remove].get("username", f"User {user_id_to_remove}"))
    del users[user_id_to_remove]
    save_users(users)
    
    # Удаляем очки
    if user_id_to_remove in scores:
        del scores[user_id_to_remove]
        save_scores(scores)
    
    await update.message.reply_text(f"✅ Пользователь {user_name} удален из системы")


async def newgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает новую игру в группе"""
    if not update.effective_chat:
        return
    
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("Эта команда работает только в группах!")
        return
    
    chat_id = update.effective_chat.id
    
    # Проверяем, нет ли уже активной игры
    if get_game(chat_id):
        await update.message.reply_text("❌ Игра уже идет! Сначала закончите текущую.")
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
        
        # Сохраняем игру
        save_game(chat_id, chameleon.id, word, members)
        
        # Отправляем сообщения каждому участнику
        sent_count = 0
        for member in members:
            try:
                if member.id == chameleon.id:
                    # Хамелеон получает особое сообщение
                    await context.bot.send_message(
                        chat_id=member.id,
                        text=" *Ты хамелеон!* 🦎\n\n👀 Шифруйся. Не дай себя раскусить!",
                        parse_mode="Markdown"
                    )
                else:
                    # Остальные получают слово
                    await context.bot.send_message(
                        chat_id=member.id,
                        text=f"Секретное слово: {word} 🤫\n\n🕵️ Найди хамелеона!",
                        parse_mode="Markdown"
                    )
                sent_count += 1
            except Exception as e:
                logger.warning(f"Не удалось отправить сообщение пользователю {member.id}: {e}")
        
        # Сообщение в группе с кнопкой голосования
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🗳️ Голосовать", callback_data=f"vote:{chat_id}")]
        ])
        await update.message.reply_text(
            f"🎮 *Игра началась!*\n\n"
            f"Отправил слова {sent_count} зарегистрированным игрокам.\n"
            f"Проверьте личные сообщения!\n"
            f"Один из вас - хамелеон! Найдите его!",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Ошибка при запуске игры: {e}")
        await update.message.reply_text(
            "❌ Произошла ошибка. Убедитесь, что пользователи написали мне в личку /start"
        )


async def vote_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатия на кнопку голосования"""
    query = update.callback_query
    logger.info(f"Vote callback received: {query.data}")
    
    try:
        await query.answer()
        
        chat_id = int(query.data.split(":")[1])
        game = get_game(chat_id)
        
        if not game:
            await query.edit_message_text("❌ Игра не найдена или уже закончена")
            return
        
        users = load_users()
        members = game["members"]
        votes = game.get("votes", {})
        
        # Создаем клавиатуру с кандидатами и количеством голосов
        keyboard = []
        for member_id in members:
            user_data = users.get(str(member_id), {})
            name = user_data.get("first_name", f"User {member_id}")
            username = user_data.get("username")
            if username:
                name = f"@{username}"
            
            # Подсчитываем голоса за этого кандидата
            vote_count = sum(1 for v in votes.values() if v == member_id)
            button_text = f"{name} ({vote_count})" if vote_count > 0 else name
            
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"vote_for:{chat_id}:{member_id}")])
        
        keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data=f"cancel_vote:{chat_id}")])
        
        await query.edit_message_text(
            "🗳️ *Кто хамелеон?*\n\nГолосуйте за подозреваемого:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        logger.error(f"Error in vote_callback: {e}")
        await query.answer("❌ Произошла ошибка", show_alert=True)


async def vote_for_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка голоса за конкретного игрока"""
    query = update.callback_query
    await query.answer()
    
    data = query.data.split(":")
    chat_id = int(data[1])
    voted_for_id = int(data[2])
    
    game = get_game(chat_id)
    if not game:
        await query.edit_message_text("❌ Игра не найдена или уже закончена")
        return
    
    user_id = query.from_user.id
    
    # Проверяем, что пользователь участвует в игре
    if user_id not in game["members"]:
        await query.answer("❌ Вы не участвуете в этой игре", show_alert=True)
        return
    
    # Записываем голос
    if "votes" not in game:
        game["votes"] = {}
    game["votes"][str(user_id)] = voted_for_id
    
    # Сохраняем обновленные голоса
    games = load_games()
    games[str(chat_id)] = game
    save_games(games)
    
    # Обновляем клавиатуру с количеством голосов
    users = load_users()
    members = game["members"]
    votes = game["votes"]
    
    keyboard = []
    for member_id in members:
        user_data = users.get(str(member_id), {})
        name = user_data.get("first_name", f"User {member_id}")
        username = user_data.get("username")
        if username:
            name = f"@{username}"
        
        # Подсчитываем голоса за этого кандидата
        vote_count = sum(1 for v in votes.values() if v == member_id)
        button_text = f"{name} ({vote_count})" if vote_count > 0 else name
        
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"vote_for:{chat_id}:{member_id}")])
    
    keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data=f"cancel_vote:{chat_id}")])
    
    await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))
    
    # Если один кандидат набрал большинство, подводим итоги
    suspected_id, vote_counts = get_vote_winner(game["votes"], game["members"])
    if suspected_id is not None:
        await finish_game(update, context, chat_id, game)
    elif len(game["votes"]) == len(game["members"]) and vote_counts:
        await context.bot.send_message(
            chat_id=chat_id,
            text="🗳️ Ничья в голосовании. Переголосуйте: нужен один кандидат с большинством голосов."
        )


async def cancel_vote_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена голосования"""
    query = update.callback_query
    await query.answer()
    
    chat_id = int(query.data.split(":")[1])
    
    await query.edit_message_text(
        "🗳️ Голосование отменено. Нажмите кнопку снова, когда будете готовы.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🗳️ Голосовать", callback_data=f"vote:{chat_id}")]
        ])
    )


async def finish_game(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int, game: dict):
    """Завершение игры и подсчет очков"""
    votes = game["votes"]
    chameleon_id = game["chameleon_id"]
    members = game["members"]
    users = load_users()
    
    # Находим кого подозревают больше всего
    suspected_id, vote_counts = get_vote_winner(votes, members)
    if suspected_id is None:
        await context.bot.send_message(
            chat_id=chat_id,
            text="🗳️ Ничья в голосовании. Переголосуйте: нужен один кандидат с большинством голосов."
        )
        return
    
    # Определяем результат
    chameleon_caught = (suspected_id == chameleon_id)
    
    # Начисляем очки
    if chameleon_caught:
        # Хамелеона поймали - все кроме него получают +2
        for member_id in members:
            if member_id != chameleon_id:
                add_score(member_id, 2)
        result_text = "🎉 *Хамелеона поймали!*\n\n"
        result_text += f"Все игроки кроме хамелеона получают +2 очка!"
    else:
        # Хамелеон не пойман - он получает +3
        add_score(chameleon_id, 3)
        result_text = "🦎 *Хамелеон ушел!*\n\n"
        result_text += f"Хамелеон получает +3 очка!"
    
    # Показываем кто был хамелеоном
    chameleon_data = users.get(str(chameleon_id), {})
    chameleon_name = chameleon_data.get("first_name", f"User {chameleon_id}")
    chameleon_username = chameleon_data.get("username")
    if chameleon_username:
        chameleon_name = f"@{chameleon_username}"
    
    result_text += f"\n\n🦎 Хамелеон был: {chameleon_name}"
    result_text += f"\n🎯 Секретное слово: {game['word']}"
    
    # Удаляем игру
    delete_game(chat_id)
    
    # Отправляем результат в группу
    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=result_text,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке результата: {e}")


def main():
    if not BOT_TOKEN:
        raise RuntimeError("Не задан BOT_TOKEN. Установи переменную окружения BOT_TOKEN и перезапусти бота.")
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("scores", scores))
    app.add_handler(CommandHandler("remove", remove_user))
    app.add_handler(CommandHandler("newgame", newgame))
    app.add_handler(CommandHandler("cnewgame", newgame))
    
    # Callback handlers for voting (поддержка отрицательных chat_id для групп)
    app.add_handler(CallbackQueryHandler(vote_callback, pattern=r"^vote:-?\d+$"))
    app.add_handler(CallbackQueryHandler(vote_for_callback, pattern=r"^vote_for:-?\d+:\d+$"))
    app.add_handler(CallbackQueryHandler(cancel_vote_callback, pattern=r"^cancel_vote:-?\d+$"))
    
    print("🦎 Chameleon Game Bot запущен! Ctrl+C для остановки.")
    app.run_polling()


if __name__ == "__main__":
    main()
