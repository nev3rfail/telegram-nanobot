import os
import sys

_bot = None

def instance(token=None, ** kwargs):
    global _bot
    if not _bot:
        if token:
            bot_path = kwargs.pop("bot_path", None)
            if bot_path and os.path.isdir(bot_path + '/../pyTelegramBotAPI_fancy'):
                sys.path.insert(0, bot_path + '/../pyTelegramBotAPI_fancy')
            import telebot
            telebot.util.TELEBOT_DEFAULT_BREAK = True
            _bot = telebot.TeleBot(token, ** kwargs)
            print("Bot instance created.")
        else:
            raise ValueError("No bot instance.")
    return _bot