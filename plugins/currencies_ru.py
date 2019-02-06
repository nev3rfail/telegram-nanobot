#encoding: UTF-8
import json
from telebot import types
import urllib2
from util import Stupidcache


def register(bot):
    print("Loading through-rub currency converter plugin...")
    @bot.channel_post_handler(func=lambda m: m.text.startswith("!convert ") or m.text.startswith('!curr '))
    @bot.message_handler(func=lambda m: m.text.startswith("!convert ") or m.text.startswith('!curr '))
    @bot.message_handler(commands=['convert', 'curr'])
    @bot.channel_post_handler(commands=['convert', 'curr'])
    def do_convert(msg):
        args = parse_args(msg.text)
        if args:
            args['result'] = str(round(currency_convert(args['amount'], args['from'], args['to']), 2))
            bot.reply_to(msg, "{amount} {from} = `{result}` {to}".format(** args), parse_mode="Markdown")


def parse_args(text, inline=False):
    text = text.replace(" to ", " ")
    segs = text.split(" ")
    if not inline:
        segs.pop(0)
    try:
        amount = float(segs[0])
    except Exception as e:
        print("Cannot get amount:", e)
        return False
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
    opener = urllib2.build_opener()
    opener.addheaders = [('User-Agent', 'telegram:nanobot:0.6 (https://github.com/nev3rfail/telegram-nanobot)')]
    try:
        response = opener.open("https://www.cbr-xml-daily.ru/daily_json.js", timeout=5)
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


currency_cache = Stupidcache(update_function=_request_currencies)


def get_currencies():
    return currency_cache.get_data()


def currency_convert(amount, _from="USD", _to="RUB"):
    currencies = get_currencies()
    if _from in currencies.keys() and _to in currencies.keys():
        return float(currencies[_to]) / float(currencies[_from]) * float(amount)
    else:
        print("cannot extract currency " + _from + " or currency " + _to + " from currency list")
        return 0


def handle_inline(msg):
    args = parse_args(msg, True)
    if args:
        args['result'] = str(round(currency_convert(args['amount'], args['from'], args['to']), 2))
        return types.InlineQueryResultArticle('12', '!convert', types.InputTextMessageContent("{amount} {from} = `{result}` {to}".format(** args), parse_mode="Markdown"))




