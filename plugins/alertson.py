#encoding: UTF-8

__plugin_name__ = "Alerts"

"""Skype-style /alertson and /alertsoff"""
from plugins.reactions import add_reaction
from plugins.reactions import delete_trigger
import shlex
def register(bot, ** kwargs):
    @bot.channel_post_handler(regexp="^!alertson ")
    @bot.message_handler(regexp="^!alertson ")
    def alertson(msg):
        if not msg.from_user:
            bot.send_message(msg.chat.id, "Works only in groups.")
        segs = shlex.split(msg.text)
        segs.pop(0)
        if len(segs):
            for seg in segs:
                add_reaction(msg.chat.id, seg, "@" + msg.from_user.username)

    @bot.channel_post_handler(regexp="^!alertsoff ")
    @bot.message_handler(regexp="^!alertsoff ")
    def alertsoff(msg):
        if not msg.from_user:
            bot.send_message(msg.chat.id, "Works only in groups.")
        segs = shlex.split(msg.text)
        segs.pop(0)
        if len(segs):
            for seg in segs:
                delete_trigger(msg.chat.id, seg, "@" + msg.from_user.username)