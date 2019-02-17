#encoding: UTF-8

__plugin_name__ = "Currency converter"

import helpers.bot
import json
from libs.caching import Pool
from telebot import types
import urllib.request

_debug = False
def register(debug=False, listen=True, ** kwargs):
    _debug = debug
    if listen:
        bot = helpers.bot.instance()
        @bot.channel_post_handler(regexp="^!convert |^!conv |^!curr ")
        @bot.message_handler(regexp="^!convert |^!conv |^!curr ")
        @bot.message_handler(commands=['convert', 'curr', 'conv'])
        @bot.channel_post_handler(commands=['convert', 'curr', 'conv'])
        def do_convert(msg):
            error = None
            args = None
            try:
                args = parse_args(msg.text)
            except Exception as e:
                error = e
            if args:
                try:
                    args['result'] = str(round(currency_convert(args['amount'], args['from'], args['to']), 2))
                except Exception as e:
                    error = e
            if not error:
                bot.reply_to(msg, "{amount} {from} = `{result}` {to}".format(** args), parse_mode="Markdown")
            else:
                bot.reply_to(msg, "{}".format(error), parse_mode="Markdown")


def parse_args(text, inline=False):
    text = text.replace(" to ", " ")
    segs = text.split(" ")
    if not inline:
        segs.pop(0)
    try:
        amount = float(segs[0])
    except Exception as e:
        raise ValueError("Syntax error: cannot get amount")

    try:
        _from = segs[1].upper()
    except:
        _from = "USD"

    try:
        _to = segs[2].upper()
    except:
        _to = "RUB"

    return {"amount":amount, "from":_from, "to":_to}

def _request_currencies():
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent', 'telegram:nanobot:0.6 (https://github.com/nev3rfail/telegram-nanobot)')]
    try:
        response = opener.open("https://www.cbr-xml-daily.ru/daily_json.js", timeout=5)
        if _debug:
            print(response.info())
        rmsg = response.read()
        stack = json.loads(rmsg)
    except Exception as e:
        print("Cannot retrieve currencies:", e)
        return False

    _currencies = stack['Valute']
    currencies = {}
    for currency in _currencies:
        currencies[currency] = str(round(float(_currencies[currency]["Nominal"]) / float(_currencies[currency]["Value"]), 4))
    currencies["RUB"] = 1
    return currencies


currency_cache = Pool(update_function=_request_currencies)


def get_currencies():
    return currency_cache.get_data()


def currency_convert(amount, _from="USD", _to="RUB"):
    currencies = get_currencies()
    if _from in currencies.keys() and _to in currencies.keys():
        return float(currencies[_to]) / float(currencies[_from]) * float(amount)
    else:
        raise ValueError(("Cannot extract " + _from if _from not in currencies.keys() else "Cannot extract " + _to) + " from currency list. Currency list: " + ' '.join(currencies.keys()))
        print("cannot extract currency " + _from + " or currency " + _to + " from currency list")
        return 0


def helpmsg():
    return """`!convert <amount> <source currency> to <target currency>` to convert `amount` of `source` to `dest`
    Example: `!convert 100 uah to usd`
    Short variant is `!conv`;
    Supported as bot private message;
    Supports `inline` mode."""


def handle_inline(msg):
    args = parse_args(msg, True)
    if args:
        args['result'] = str(round(currency_convert(args['amount'], args['from'], args['to']), 2))
        return types.InlineQueryResultArticle('12', '!convert', types.InputTextMessageContent("{amount} {from} = `{result}` {to}".format(** args), parse_mode="Markdown"))




