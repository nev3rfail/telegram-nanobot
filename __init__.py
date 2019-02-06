#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# encoding=utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import os
import importlib
import json

bot_path = os.path.dirname(os.path.abspath(__file__))
"""We use patched pytelegrambotapi here with sendAnimation and video previews"""
if os.path.isdir(bot_path + '/../pyTelegramBotAPI'):
    sys.path.insert(0, bot_path + '/../pyTelegramBotAPI')
import telebot as telebot


with open(bot_path + '/config.json') as json_file:
    settings = json.loads(json_file.read())


if __name__ != "__main__":
    raise Exception("This file should be executed, not imported.")

bot = telebot.TeleBot(settings['telegram_token'])

sys.path.append(bot_path + '/plugins')
loaded = {}
if len(settings['plugins']):
    for plugin in settings['plugins']:
        loaded[plugin] = importlib.import_module(plugin)
        loaded[plugin].register(bot)



"""Fallback inline handler loops through plugins and tries to get result to reply"""
@bot.inline_handler(lambda query: True)
def query_text(inline_query):
    if len(inline_query.query):
        msgs = inline_query.query.split(" ")
        message = " ".join(msgs)
        if len(message):
            choices = []
            for name, plugin in loaded.iteritems():
                if hasattr(plugin, "handle_inline"):
                    result = plugin.handle_inline(message)
                    if result:
                        choices.append(result)
            if len(choices):
                try:
                    bot.answer_inline_query(inline_query.id, choices)
                except Exception as e:
                    print "Inline error:", e
            else:
                return


bot.polling()
