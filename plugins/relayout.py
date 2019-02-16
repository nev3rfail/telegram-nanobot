#encoding: UTF-8

__plugin_name__ = "Layout changing plugin [en<->ru]"
import sys
if sys.version_info[0] < 3:
    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')
from telebot import types

def register(bot, listen=True, ** kwargs):
    if listen:
        @bot.channel_post_handler(regexp="^!relayout|^!fuck")
        @bot.message_handler(regexp="^!relayout|^!fuck")
        @bot.message_handler(commands=['relayout', 'fuck'])
        @bot.channel_post_handler(commands=['relayout', 'fuck'])
        def relayout(msg):
            if msg.reply_to_message:
                r = do_relayout(msg.reply_to_message.text)
                bot.reply_to(msg.reply_to_message, r)

def do_relayout(text):
    _from = list(u",.бю?;ж:ЖЭ\"ё1234567890-=йцукенгшщзхъфывапролджэ\ячсмитьбю.Ё!\"№;%:?*()_+ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭ/ЯЧСМИТЬБЮ,`1234567890-=qwertyuiop[]asdfghjkl;'\zxcvbnm,./~!@#$%^&*()_+QWERTYUIOP{}ASDFGHJKL:\"|ZXCVBNM<>?")
    _to   = list(u"бю,.,ж;Ж:\"Э`1234567890-=qwertyuiop[]asdfghjkl;'\zxcvbnm,./~!@#$%^&*()_+QWERTYUIOP{}ASDFGHJKL:\"|ZXCVBNM<>?ё1234567890-=йцукенгшщзхъфывапролджэ\ячсмитьбю.Ё!\"№;%:?*()_+ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭ/ЯЧСМИТЬБЮ,")
    result = ""
    for char in text:
        if char in _from:
            result += _to[_from.index(char)]
        else:
            result += char
    return result


def helpmsg():
    return """`!relayout` or `/relayout` as reply to any message in chat to change layout ru<->en
    Example: `!relayout >kz хеуыеъ` will return `Юля [test]`
    Supported as bot private message;
    Supports `inline` mode."""


def handle_inline(msg):
    return types.InlineQueryResultArticle('112', '!relayout', types.InputTextMessageContent("{}".format(do_relayout(msg))))

