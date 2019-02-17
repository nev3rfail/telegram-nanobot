#encoding: UTF-8
from helpers.db import connection
import json
db = connection()
"""
Note: this plugin should be loaded before any other.
It stops bot from executing any further command if chat is unknown;
It alters telebot's message.chat if chat is known.
Force mode works only with patched telebot.
"""
__plugin_name__ = "Bot gatekeeper"
def register(bot, config={}, ** kwargs):
    db.query("""
    CREATE TABLE IF NOT EXISTS `chats` (
	`chat_id`	INTEGER,
	`settings`	TEXT DEFAULT '{}',
	`date_added`	TEXT DEFAULT CURRENT_TIMESTAMP,
	`deleted`	INTEGER DEFAULT 0,
	PRIMARY KEY(`chat_id`)
);
    """)
    if "mode" in config and config["mode"] in ["force", "auto"]:
        _mode = config["mode"]
    else:
        _mode = "force"

    print("Gatekeeper is in", _mode, "mode.")
    @bot.channel_post_handler(func=lambda m: True, blocking=True, final=False)
    @bot.message_handler(func=lambda m: True, blocking=True, final=False)
    def whoru(msg):
        if _mode == "force":
            t = msg.text.split('@')[0]
            if t in ['!start', '/start']:
                #do registration
                try:
                    chat = register_chat(msg.chat.id)
                    print("New chat:", msg.chat.id)
                except:
                    bot.send_message(msg.chat.id, "Already registered. Use `!help` or /help for help.")
            else:
                chat = (get_chat(msg.chat.id))
                if not chat:
                    print("Unknown chat", msg.chat.id, "-- eating all.")
                else:
                    msg.chat.nanobot_chat_data = chat
                    return
            return -256

        elif _mode == "auto":
            chat = get_chat(msg.chat.id)
            if not chat:
                print("Unknown chat", msg.chat.id, "-- registering chat.")
                chat = register_chat(msg.chat.id)
            msg.chat.nanobot_chat_data = chat


def get_chat(chat_id):
    byid = db.query("select * from chats where chat_id = ?", [chat_id])
    if len(byid):
        chat = dict(byid[0])
        chat['id'] = chat['chat_id']
        chat['settings'] = json.loads(chat['settings'])
        return chat
    else:
        return False

def set_chat(chat_id, settings):
    return db.query("update chats set settings = ? where chat_id = ?", [json.dumps(settings), chat_id])

def set_setting(chat_id, k, v):
    chat = get_chat(chat_id)
    if chat:
        chat['settings'][k] = v
        return set_chat(chat_id, chat['settings'])

def register_chat(chat_id):
    db.query("insert into chats(chat_id) VALUES (?)", [chat_id])
    #db.commit()
    return get_chat(chat_id)


