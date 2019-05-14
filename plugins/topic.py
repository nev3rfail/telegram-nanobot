#encoding: UTF-8

import helpers.bot

__plugin_name__ = "Change group or channel title"
from plugins.gatekeeper import set_setting, get_setting
def register(listen=True, ** kwargs):
    if listen:
        bot = helpers.bot.instance()
        @bot.channel_post_handler(regexp="^!topic|^!topic |^!title|^!title ")
        @bot.message_handler(regexp="^!topic|^!topic |^!title|^!title ")
        @bot.message_handler(commands=['topic', 'title'])
        @bot.channel_post_handler(commands=['topic', 'title'])
        def send_welcome(message):
            print(message.chat.type)
            if message.chat.type in ['group', 'channel', 'supergroup']:
                args = message.text.split(' ')
                args.pop(0)
                if len(args):
                    if args[0] == 'alter':
                        args.pop(0)
                        alter_topic(message.chat.id, ' '.join(args))
                    elif args[0] == 'rollback':
                        rollback_topic(message.chat.id)
                    else:
                        set_topic(message.chat.id, ' '.join(args))
                else:
                    bot.reply_to(message, "Topic is: {}".format(message.chat.title))

def set_topic(chat_id, topic):
    bot = helpers.bot.instance()
    set_setting(chat_id, 'old_topic', get_setting(chat_id, 'topic'))
    set_setting(chat_id, 'topic', topic)
    try:
        bot.set_chat_title(chat_id, topic)
    except Exception as e:
        if "rights to change" in str(e):
            bot.send_message(chat_id, "Promote me to change the topic.");
        print(e)
    pass

def alter_topic(chat_id, alter):
    topic = get_setting(chat_id, 'topic')
    bot = helpers.bot.instance()
    if not topic:
        try:
            topic = bot.get_chat(chat_id).title
        except Exception as e:
            print("Cant get chat:", e)

    if topic:
        set_topic(chat_id, topic + ' ' + alter)
    else:
        set_topic(chat_id, alter)

def rollback_topic(chat_id):
    topic = get_setting(chat_id, 'old_topic')
    if topic:
        set_topic(chat_id, topic)
    else:
        helpers.bot.instance().send_message(chat_id, "I don't remember the old topic.")

def helpmsg():
    return """`/topic <newtopic>` to set topic;
`/topic alter <altering_text>` to alter topic;
/topic rollback to set previous topic (if known);
Aliases: /topic, !topic, /title, !title
"""


