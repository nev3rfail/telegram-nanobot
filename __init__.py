#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# encoding=utf8
import argparse
import helpers.bot
import helpers.db
import helpers.timer
import importlib
import json
import os
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--config', help='Relative path to bot\'s configuration file. Defaults to config.json inside workdir.', default="config.json")
cmdline = parser.parse_args()

#for arg in vars(args):
#    setattr(config, arg, getattr(args, arg))


bot_path = os.path.dirname(os.path.abspath(__file__))
"""We use patched pytelegrambotapi here
with sendAnimation
and video previews
and fancy user-controller loop
and other things
"""

with open(bot_path + '/' + cmdline.config) as json_file:
    config = json.loads(json_file.read())

"""Initialize database"""
if "database" in config:
    try:
        if 'database_autocommit' in config:
            autocommit = config['database_autocommit']
        else:
            autocommit = False
        helpers.db.instance(config['database'], autocommit)
    except Exception as e:
        print("Cannot initialize database:", e)

timer = helpers.timer.instance(1)


if __name__ != "__main__":
    raise Exception("This file should be executed, not imported.")

bot = helpers.bot.instance(token=config['telegram_token'], threaded=True)

sys.path.append(bot_path + '/plugins')
loaded = {}
if len(config['plugins']):
    for plugin in config['plugins']:
        if plugin in config['plugin_config']:
            plugin_config = config['plugin_config'][plugin]
        else:
            plugin_config = {}
        try:
            loaded[plugin] = importlib.import_module(plugin)
            if hasattr(loaded[plugin], '__plugin_name__'):
                print("Loaded", loaded[plugin].__plugin_name__, "plugin.")
            else:
                print("Loaded", plugin)
            loaded[plugin].register(config=plugin_config, debug=config['debug'])
        except Exception as e:
            print("Cannot load plugin {}:".format(plugin), e)


"""Help handler"""
@bot.channel_post_handler(regexp="^!help$|^!help ")
@bot.message_handler(regexp="^!help$|^!help ")
@bot.message_handler(commands=['help'])
@bot.channel_post_handler(commands=['help'])
def helpmsg(message):
    response = []
    for name, plugin in loaded.items():
        if hasattr(plugin, "helpmsg"):
            result = plugin.helpmsg()
            if result:
                response.append(result)
    bot.send_message(message.chat.id, "\n".join(response), parse_mode="Markdown")


"""Fallback inline handler loops through plugins and tries to get result to reply"""
@bot.inline_handler(lambda query: True)
def query_text(inline_query):
    if len(inline_query.query):
        msgs = inline_query.query.split(" ")
        message = " ".join(msgs)
        if len(message):
            choices = []
            for name, plugin in loaded.items():
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

try:
    bot.polling(interval=3)
    pass
except Exception as e:
    print("Exception", e)
    pass
finally:
    timer.stop()
    exit(0)

