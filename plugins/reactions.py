#encoding: UTF-8

__plugin_name__ = "Message reactions"

from helpers.db import connection
import re
import shlex
db = connection()

def register(bot, listen=True, ** kwargs):
    db.query("""
CREATE TABLE IF NOT EXISTS `reactions` (
    `id`	INTEGER PRIMARY KEY AUTOINCREMENT,
    `chat_id`	INTEGER,
    `trigger`	TEXT,
    `reaction`	TEXT,
    `added_by`	INTEGER
);
""")

    if listen:
        @bot.message_handler(func=lambda m: True)
        @bot.channel_post_handler(func=lambda m: True)
        def react(msg):
            reactions = get_reactions(msg.chat.id, msg.text)
            reaction = ', '.join(reactions)
            if reaction:
                sent = bot.send_message(msg.chat.id, reaction)

        @bot.message_handler(regexp="^!reaction |^!react ")
        @bot.channel_post_handler(regexp="^!reaction |^!react ")
        @bot.message_handler(commands=['reaction', 'react'])
        @bot.channel_post_handler(commands=['reaction', 'react'])
        def handle_command(msg):
            segs = shlex.split(msg.text)
            segs.pop(0)
            if len(segs) >= 1:
                action = segs[0]
                reaction = None
                trigger = None
                if len(segs) >= 2:
                    trigger = segs[1]
                if len(segs) >= 3:
                    reaction = segs[2]

                if action == "add" and trigger and reaction:
                    add_reaction(msg.chat.id, trigger, reaction)
                    pass
                elif action == "del" and trigger and reaction:
                    delete_trigger(msg.chat.id, trigger, reaction)
                    pass
                elif action == "del" and trigger:
                    #remove reaction completely
                    reaction = trigger
                    delete_reaction(msg.chat.id, reaction)
                elif action == "list":
                    reactions = get_chat_reactions(msg.chat.id)
                    result = ""
                    if len(reactions):
                        for reaction, trigger in reactions.items():
                            result += reaction + ":\n"
                            for t in trigger.split('|'):
                                result += "  " + t + "\n"
                    else:
                        result = "No reactions for this channel."
                    bot.send_message(msg.chat.id, result)


def get_reactions(chat_id, text):
    rlist = get_chat_reactions(chat_id)
    found = []
    for reaction, trigger in rlist.items():
        f = re.search(trigger, text, re.IGNORECASE)
        if f is not None:
            found.append(reaction)
    return found


def add_reaction(chat_id, trigger, reaction):
    trigger = re.sub('[*./|\\\]', '', trigger)
    if not len(trigger):
        return
    r = db.query("select * from reactions where reaction = ? and chat_id = ?", [reaction, chat_id])
    if len(r):
        r = dict(r[0])
        r['trigger'] = r['trigger'].split("|")
        r['trigger'].append(trigger)
        db.query("update reactions set trigger = ? where chat_id = ? and reaction = ?", ['|'.join(r['trigger']), chat_id, reaction])
    else:
        db.query("insert into reactions(chat_id, trigger, reaction) values(?,?,?)", [chat_id, trigger, reaction])

def delete_trigger(chat_id, trigger, reaction):
    trigger = re.sub('[*./|\\\]', '', trigger)
    if not len(trigger):
        return
    r = db.query("select * from reactions where reaction = ? and chat_id = ?", [reaction, chat_id])
    if len(r):
        r = dict(r[0])
        r['trigger'] = r['trigger'].split("|")
        r['trigger'].remove(trigger)
        print(reaction, trigger)
        if len(r['trigger']):
            db.query("update reactions set trigger = ? where chat_id = ? and reaction = ?", ['|'.join(r['trigger']), chat_id, reaction])
        else:
            delete_reaction(chat_id, reaction)

def delete_reaction(chat_id, reaction):
    db.query("delete from reactions where reaction = ? and chat_id = ?", [reaction, chat_id])

def get_chat_reactions(chat_id):
    r = db.query("select * from reactions where chat_id = ?", [chat_id])
    ret = {}
    for item in r:
        item = dict(item)
        ret[item['reaction']] = item['trigger']
    return ret


def helpmsg():
    return """`!reaction add <trigger> <reaction>` to add reaction;
`!reaction del <trigger> <reaction>` to delete trigger from reaction;
`!reaction del <reaction>` to delete reaction completely"""



