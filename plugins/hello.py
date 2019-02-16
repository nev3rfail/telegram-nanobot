#encoding: UTF-8

__plugin_name__ = "Dummy hello"

def register(bot, listen=True, config={}, ** kwargs):
    if listen:
        @bot.channel_post_handler(regexp="^!hello$")
        @bot.message_handler(regexp="^!hello$")
        @bot.message_handler(commands=['hello'])
        @bot.channel_post_handler(commands=['hello'])
        def send_welcome(message):
            if "text" in config:
                bot.reply_to(message, config["text"])
            else:
                bot.reply_to(message, "Hello, world!")


def helpmsg():
    return "`/hello` for hello message"


