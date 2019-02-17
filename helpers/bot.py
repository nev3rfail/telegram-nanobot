import telebot

telebot.util.TELEBOT_DEFAULT_BREAK = True
_bot = None

def instance(token=None, ** kwargs):
    global _bot
    if not _bot:
        if token:
            _bot = telebot.TeleBot(token, ** kwargs)
            print("Bot instance created.")
        else:
            raise ValueError("No bot instance.")
    return _bot