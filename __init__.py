#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding=utf8
import importlib
import json
import os
import sys

bot_path = os.path.dirname(os.path.abspath(__file__))
"""We use patched pytelegrambotapi here with sendAnimation and video previews"""
if os.path.isdir(bot_path + '/../pyTelegramBotAPI'):
    sys.path.insert(0, bot_path + '/../pyTelegramBotAPI')
import telebot as telebot


with open(bot_path + '/config.json') as json_file:
    config = json.loads(json_file.read())


if __name__ != "__main__":
    raise Exception("This file should be executed, not imported.")

bot = telebot.TeleBot(config['telegram_token'])

sys.path.append(bot_path + '/plugins')
loaded = {}
if len(config['plugins']):
    for plugin, plugin_config in config['plugins'].iteritems():
        try:
            loaded[plugin] = importlib.import_module(plugin)
            loaded[plugin].register(bot=bot, config=plugin_config, debug=config['debug'])
        except Exception as e:
            print("Cannot load plugin {}".format(plugin), e)


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
                    print("Inline error:", e)
            else:
                return


bot.polling()
