#encoding: UTF-8

import helpers.bot
from helpers.common import replace_multiple
import helpers.db
import json
from plugins.gatekeeper import get_setting
from plugins.gatekeeper import set_setting
from plugins.google_cloud import json as google_json
from plugins.google_cloud import languages as google_languages
from plugins.google_cloud import tts_languages as google_tts_languages
import re
from telebot import types
__plugin_name__ = "Google translate"

from google.cloud import translate
try:
    translate_client = translate.Client.from_service_account_json(google_json)
except Exception as e:
    print(__plugin_name__, ' unloaded:', e)


commands = "^!translate$|^!tr$|^!translate |^!tr "

db = helpers.db.instance()


def register(listen=True, config={}, ** kwargs):
    db.query("""
    CREATE TABLE IF NOT EXISTS `translation_history` (
        `id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`chat_id`	INTEGER,
	`query`	TEXT DEFAULT '',
	`result`	TEXT DEFAULT '',
        `src_lang` TEXT DEFAULT 'auto',
        `target_lang` TEXT DEFAULT 'auto'
);
    """)
    if listen:
        bot = helpers.bot.instance()
        @bot.channel_post_handler(regexp=commands)
        @bot.message_handler(func=lambda msg: not (msg.text or msg.caption or '').startswith('!tts') and not (msg.text or msg.caption or '').startswith('!history')) #any message in direct chat should trigger translation
        def ev_translate(msg):
            text = msg.text or msg.caption
            text = re.sub(commands, '', text)

            if text == '' and msg.reply_to_message:
                text = msg.reply_to_message.text or msg.reply_to_message.caption

            splitted = text.split(' ')

            dest = get_setting(msg.chat.id, 'default_to') or config['default_to']

            #if user is trying to set target lang by hands
            if len(splitted[0]) == 2:
                #replacing commonly mistaken language codes
                _dest = replace_multiple({"ua":"uk", "by":"be", "br":"be", "jp":"ja"}, splitted[0])
                print(_dest)
                if _dest in google_languages:
                    dest = _dest
                    #deleting language code from text
                    splitted.pop(0)
                    text = ' '.join(splitted)

            local_detected = detect_lang(text)

            if local_detected == dest:
                dest = get_setting(msg.chat.id, 'default_to_if_from_is_to') or config['default_to_if_from_is_to']

            try:
                translated = translate(text, dest, True)
                translated_text = translated['translatedText']
                translated_src = translated['detectedSourceLanguage']

            except Exception as e:
                print(msg.chat.id, 'Translation error:', e)
                bot.send_message(msg.chat.id, "Error: {}".format(e))
                return

            hist_id = db.query("insert into translation_history (chat_id, query, result, src_lang, target_lang) values (:chat_id, :query, :result, :src_lang, :target_lang)", {'chat_id':msg.chat.id, 'query':text, 'result':translated_text, 'src_lang':translated_src, 'target_lang':dest}, get_id=True)

            markup = False
            if 'tts' in config and config['tts']:

                btns = []
                if translated_src in google_tts_languages:
                    btns.append(types.InlineKeyboardButton('Say [' + translated_src + ']', callback_data=json.dumps({'function':'tts', 'what':'src', 'id':hist_id})))

                if dest in google_tts_languages:
                    btns.append(types.InlineKeyboardButton('Say [' + dest + ']', callback_data=json.dumps({'function':'tts', 'what':'target', 'id':hist_id})))

                if len(btns):
                    markup = types.InlineKeyboardMarkup(row_width=2)
                    markup.add(*btns)


            bot.send_message(msg.chat.id, translated_text, reply_to_message_id=msg.message_id, reply_markup=markup)


        @bot.channel_post_handler(regexp='^!languages')
        @bot.message_handler(regexp='^!languages')
        def langs(msg):
            bot.reply_to(msg, ', '.join(google_languages))

        histregex = '^!history$|^!history '
        @bot.channel_post_handler(regexp=histregex)
        @bot.message_handler(regexp=histregex)
        def history(msg):
            text = msg.text or msg.caption
            text = re.sub(histregex, '', text)
            send = ''
            markup = False
            if len(text):
                item = get_history_item(msg.chat.id, text)
                if not item:
                    send = 'Cannot get item `{text}`. Type `!history` to get full history.'.format({'text':text})
                else:
                    send = '`{query}` {src_lang}<->{target_lang} `{result}`'.format( ** item)
                    btns = []
                    if item['src_lang'] in google_tts_languages:
                        btns.append(types.InlineKeyboardButton('Say [' + item['src_lang'] + ']', callback_data=json.dumps({'function':'tts', 'what':'src', 'id':item['id']})))

                    if item['target_lang'] in google_tts_languages:
                        btns.append(types.InlineKeyboardButton('Say [' + item['target_lang'] + ']', callback_data=json.dumps({'function':'tts', 'what':'target', 'id':item['id']})))

                    if len(btns):
                        markup = types.InlineKeyboardMarkup(row_width=2)
                        markup.add(*btns)
            else:
                full = get_history(msg.chat.id)
                send = ''
                if not len(full):
                    send = "History is empty.";
                for item in full:
                    send += '\n{id} `{query}` {src_lang}<->{target_lang} `{result}`'.format( ** item)
            bot.reply_to(msg, send, reply_markup=markup, parse_mode="Markdown")


def get_history_item(chat_id, item_id):
    r = db.query("select * from translation_history where id = ? and chat_id = ?", [int(item_id), chat_id])
    if len(r):
        return r[0]
    else:
        return False

def get_history(chat_id):
    return db.query("select * from translation_history where chat_id = ?", [chat_id])



def detect_lang(string):
    tests = {
        'ru':u'[а-я]',
        'en':u'[a-z]',
        'tr':u'[a-zğüşöçİĞÜŞÖÇ]'
    }
    tests_results = {k:0 for k in tests.keys()}

    for lang in tests:
        tests_results[lang] = len(re.findall(tests[lang], string, re.IGNORECASE))

    _max = 0
    result = "en"
    for lang in tests_results:
        if tests_results[lang] > _max:
            _max = tests_results[lang]
            result = lang

    return result


def translate(text, target_language, full=False):
    result = translate_client.translate(text, target_language=target_language)
    if full:
        return result
    else:
        return result['translatedText']


def helpmsg():
    return """Translator bot.
    Any message in private chat to translate message contents.
    `!translate text` in group chat to translate text.
    You can set target language with language code before text.
    For example `!translate ja test` to translate "test" to japaneese.
    Or `ja test` to translate "test" to japaneese in private chat.
    `!languages` to list supported language codes.
"""


