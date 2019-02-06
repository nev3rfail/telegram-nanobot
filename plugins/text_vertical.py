#encoding: UTF-8
from telebot import types


def register(** kwargs):
    print("Loading vertical text plugin...")
    bot = kwargs['bot']
    @bot.channel_post_handler(func=lambda m: m.text.startswith("!vertical ") or m.text.startswith('!vert '))
    @bot.message_handler(func=lambda m: m.text.startswith("!vertical ") or m.text.startswith('!vert '))
    @bot.message_handler(commands=['vertical', 'vert'])
    @bot.channel_post_handler(commands=['vertical', 'vert'])
    def vertical(msg):
        msgs = msg.text.split(" ")
        msgs.pop(0)
        message = " ".join(msgs)
        if len(message):
            bot.send_message(msg.chat.id, "```\n" + do_vertical(message) + "```", parse_mode="Markdown")


def do_vertical(msg):
    s = msg
    sb = ""
    for i in range(len(s)):
        sb += s[i] + " "
    spaces = " "
    sb += '\n'
    for i in range(1, len(s)):
        sb += s[i] + spaces + s[i] + '\n'
        spaces += "  "
    return sb

def handle_inline(msg):
    return types.InlineQueryResultArticle('1', '!vert', types.InputTextMessageContent("```\n" + do_vertical(msg) + "```", parse_mode="Markdown"))
