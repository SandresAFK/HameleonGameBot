# 🦎 Chameleon Game Bot

Простой Telegram бот для игры в "Хамелеон".

## Как это работает

1. Добавьте бота в группу
2. Любой участник пишет команду `/newgame`
3. Бот выбирает случайное слово и одного хамелеона
4. Всем участникам в личку отправляется сообщение:
   - Хамелеону: "Ты хамелеон! Шифруйся. Не дай себя раскусить!"
   - Остальным: случайное слово (одинаковое для всех)
5. Игра начинается!

## Установка

### Локально

```bash
# Создайте .env файл с токеном бота
echo "BOT_TOKEN=your_token_here" > .env

# Установите зависимости
pip install -r requirements.txt

# Запустите бота
python bot.py
```

### Docker

```bash
# Соберите образ
docker build -t chameleon-bot .

# Запустите контейнер
docker run -d -e BOT_TOKEN=your_token_here chameleon-bot
```

### AWS EC2

Развертывание аналогично другим ботам (StickerCapsBot, PoopTrackerBot, MistressBot).

## Требования

- Python 3.11+
- python-telegram-bot 22.7
- Telegram Bot Token (получить у @BotFather)
