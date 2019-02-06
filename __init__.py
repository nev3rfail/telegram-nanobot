#!/usr/bin/env python
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


bot.polling()