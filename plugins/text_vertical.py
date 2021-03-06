#encoding: UTF-8

__plugin_name__ = "Vertical fancy text"
import helpers.bot
from telebot import types

def register(listen=True, ** kwargs):
    if listen:
        bot = helpers.bot.instance()
        @bot.channel_post_handler(regexp="^!vertical |^!vert ")
        @bot.message_handler(regexp="^!vertical |^!vert ")
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


def helpmsg():
    return """`!vertical text` to make fancy text
    Alias: `!vert`;
    Supported as bot private message;
    Supports `inline` mode."""


def handle_inline(msg):
    return types.InlineQueryResultArticle('1', '!vert', types.InputTextMessageContent("```\n" + do_vertical(msg) + "```", parse_mode="Markdown"))
