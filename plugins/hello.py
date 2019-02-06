#encoding: UTF-8

def register(bot):
    @bot.message_handler(commands=['hello'])
    @bot.channel_post_handler(commands=['hello'])
    def send_welcome(message):
	bot.reply_to(message, "Hello, world!")


