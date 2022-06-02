#encoding: UTF-8

__plugin_name__ = "Vertical fancy text"
import helpers.bot
from telebot import types

def register(listen=True, ** kwargs):
    if listen:
        bot = helpers.bot.instance()
        @bot.channel_post_handler(regexp="^!vertical2 |^!vert2 ")
        @bot.message_handler(regexp="^!vertical2 |^!vert2 ")
        @bot.message_handler(commands=['vertical2', 'vert2'])
        @bot.channel_post_handler(commands=['vertical2', 'vert2'])
        def vertical(msg):
            msgs = msg.text.split(" ")
            msgs.pop(0)
            message = " ".join(msgs)
            if len(message):
                bot.send_message(msg.chat.id, do_vertical(message), parse_mode="Markdown")


def do_vertical(msg):
    word = msg
    l = len(msg)
    for index, char in enumerate(word):
        if index == 0:
            fst = "."
        else:
            fst = " "
        pad_len = l - index - 1
        msg += "`" + fst + " " * pad_len
        for index2, char2 in enumerate(word):
            if index == index2:
                msg += "`"
            elif index + 1 == index2:
                msg += "`"
            msg += char2
            if index2 == len(word) - 1:
                msg += "`"
        if index == len(word) - 1:
            msg += "`"
        msg += "\n"
    return msg


def helpmsg():
    return """`!vertical2 text` to make fancy text
    Alias: `!vert2`;
    Supported as bot private message;
    Supports `inline` mode."""


def handle_inline(msg):
    return types.InlineQueryResultArticle('1', '!vert2', types.InputTextMessageContent(do_vertical(msg), parse_mode="Markdown"))
