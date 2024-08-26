# encoding: UTF-8

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

from google.cloud import translate_v2 as translate

try:
    translate_client = translate.Client.from_service_account_json(google_json)
except Exception as e:
    print(__plugin_name__, ' unloaded:', e)

commands = "^!translate$|^!tr$|^!translate |^!tr "

db = helpers.db.instance()

config_keys = ["default_to", "default_to_if_from_is_to", "chat_mode"]

def register(listen=True, config={}, **kwargs):
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

        @bot.channel_post_handler(regexp='^!set ')
        @bot.message_handler(regexp='^!set ')
        def setting(message):
            # chat = get_chat(message.chat.id)
            # if not chat and message.chat.id != settings['god_id']:
            #    bot.send_message(message.chat.id, unset())
            #    return
            segs = message.text.split(" ")
            if len(segs) >= 2:
                action = segs[1]
                if len(segs) >= 3:
                    param = segs[2]
                else:
                    param = ""
                if action == "default_to":
                    if param in google_languages:
                        set_setting(message.chat.id, "default_to", param)
                        bot.send_message(message.chat.id, "New default target language is {} now.".format(param))
                    else:
                        # set_setting(message.chat.id, "nsfw", False)
                        bot.send_message(message.chat.id,
                                         param + " is not supported. Supported languages are:\n" + ', '.join(
                                             google_languages))

                elif action == "default_to_if_from_is_to":
                    if param in google_languages:
                        set_setting(message.chat.id, "default_to_if_from_is_to", param)
                        bot.send_message(message.chat.id, "New default fallback language is {} now.".format(param))
                    else:
                        # set_setting(message.chat.id, "nsfw", False)
                        bot.send_message(message.chat.id,
                                         param + " is not supported. Supported languages are:\n" + ', '.join(
                                             google_languages))
                elif action == "mode":
                    set_setting(message.chat.id, "chat_mode", param)
                    bot.send_message(message.chat.id, f"Chat mode set to {param}")
                elif action == "pair":
                    pair = param.split(" ")
                    if pair[0] in google_languages and pair[1] in google_languages:
                        set_setting(message.chat.id, "default_to", pair[1])
                        set_setting(message.chat.id, "default_to_if_from_is_to", pair[0])
                        bot.send_message(message.chat.id, f"Language pair set to {pair[0]}<->{pair[1]}")
                    else:
                        bot.send_message(message.chat.id, f"Invalid pair")
                elif action == "dump":
                    msg = ""
                    for item in config_keys:
                        msg += f"{item}={get_setting(message.chat.id, item)}\n"
                    bot.send_message(message.chat.id, f"Config: \n{msg}")

        @bot.channel_post_handler(regexp='^!languages')
        @bot.message_handler(regexp='^!languages')
        def langs(msg):
            bot.reply_to(msg, ', '.join(google_languages))

        histregex = '^!history$|^!history '

        @bot.channel_post_handler(regexp=histregex, blocking=True)
        @bot.message_handler(regexp=histregex, blocking=True)
        def history(msg):
            text = msg.text or msg.caption
            text = re.sub(histregex, '', text)
            send = ''
            markup = False
            if len(text):
                send, markup = render_history_item(msg.chat.id, text)
            else:
                send, markup = history_message(msg.chat.id)

            bot.reply_to(msg, send, reply_markup=markup, parse_mode="Markdown")
            from telebot.util import TELEBOT_EAT_ALL
            return TELEBOT_EAT_ALL

        @bot.callback_query_handler(func=lambda call: True)
        def callback_query(call):
            data = call.data
            data = json.loads(data)
            if data["what"] == "prev":
                text, markup = history_message(call.message.chat.id, before=data["id"])
            elif data["what"] == "next":
                text, markup = history_message(call.message.chat.id, after=data["id"])
            elif data["what"] == "show":
                text, markup = render_history_item(call.message.chat.id, data["id"])
                bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
                text = None
                markup = False
            else:
                text = None
                markup = False
            try:
                bot.answer_callback_query(call.id, "")
            except Exception as e:
                print(e)
            if text is not None:
                bot.edit_message_text(text, reply_markup=markup, message_id=call.message.message_id, chat_id=call.message.chat.id, parse_mode="Markdown")

        @bot.channel_post_handler(regexp=commands)
        @bot.message_handler(
            func=lambda msg: check_if_i_needed(msg))  # any message in direct chat should trigger translation
        def ev_translate(msg):

            text = msg.text or msg.caption
            text = re.sub(commands, '', text)

            if text == '' and msg.reply_to_message:
                text = msg.reply_to_message.text or msg.reply_to_message.caption

            splitted = text.split(' ')

            dest = get_setting(msg.chat.id, 'default_to') or config['default_to']

            # if user is trying to set target lang by hands
            if len(splitted[0]) == 2:
                # replacing commonly mistaken language codes
                _dest = replace_multiple({"ua": "uk", "by": "be", "br": "be", "jp": "ja"}, splitted[0])
                if _dest in google_languages:
                    dest = _dest
                    # deleting language code from text
                    splitted.pop(0)
                    text = ' '.join(splitted)

            local_detected = detect_lang(text)
            if local_detected == dest:
                dest = get_setting(msg.chat.id, 'default_to_if_from_is_to') or config['default_to_if_from_is_to']
            print(dest)
            try:
                translated = translate(text, dest, True)
                translated_text = translated['translatedText']
                translated_src = translated['detectedSourceLanguage']
                print(translated)

            except Exception as e:
                print(msg.chat.id, 'Translation error:', e)
                bot.send_message(msg.chat.id, "Error: {}".format(e))
                return

            hist_id = db.query(
                "insert into translation_history (chat_id, query, result, src_lang, target_lang) values (:chat_id, :query, :result, :src_lang, :target_lang)",
                {'chat_id': msg.chat.id, 'query': text, 'result': translated_text, 'src_lang': translated_src,
                 'target_lang': dest}, get_id=True)

            markup = False
            if 'tts' in config and config['tts']:

                btns = []
                if translated_src in google_tts_languages:
                    btns.append(types.InlineKeyboardButton('Say [' + translated_src + ']', callback_data=json.dumps(
                        {'function': 'tts', 'what': 'src', 'id': hist_id})))

                if dest in google_tts_languages:
                    btns.append(types.InlineKeyboardButton('Say [' + dest + ']', callback_data=json.dumps(
                        {'function': 'tts', 'what': 'target', 'id': hist_id})))

                if len(btns):
                    markup = types.InlineKeyboardMarkup(row_width=2)
                    markup.add(*btns)

            bot.send_message(msg.chat.id, translated_text, reply_to_message_id=msg.message_id, reply_markup=markup)


def check_if_i_needed(msg):
    if msg.chat.type in ['group', 'supergroup', 'channel'] and (
            (msg.text or msg.caption or '').startswith('!translate ') or (msg.text or msg.caption or '').startswith(
            '!tr ') or get_setting(msg.chat.id, "chat_mode") == "monopoly"):
        # trigger only with commands
        return True
    elif msg.chat.type == 'private' and not (msg.text or msg.caption or '').startswith('!help') and not (
            msg.text or msg.caption or '').startswith('/help'):
        # trigger on any message except help request
        return True
    else:
        return False


def get_history_item(chat_id, item_id):
    r = db.query("select * from translation_history where id = ? and chat_id = ?", [int(item_id), chat_id])
    if len(r):
        return r[0]
    else:
        return False

def render_history_item(chat_id, text):
    item = get_history_item(chat_id, text)
    markup = False
    if not item:
        send = 'Cannot get item `{text}`. Type `!history` to get full history.'.format({'text': text})
    else:
        send = '`{query}` {src_lang}<->{target_lang} `{result}`'.format(**item)
        btns = []
        if item['src_lang'] in google_tts_languages:
            btns.append(types.InlineKeyboardButton('Say [' + item['src_lang'] + ']',
                                                   callback_data=json.dumps(
                                                       {'function': 'tts', 'what': 'src',
                                                        'id': item['id']})))

        if item['target_lang'] in google_tts_languages:
            btns.append(types.InlineKeyboardButton('Say [' + item['target_lang'] + ']',
                                                   callback_data=json.dumps(
                                                       {'function': 'tts', 'what': 'target',
                                                        'id': item['id']})))

        if len(btns):
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(*btns)
    return send, markup

def get_history(chat_id):
    return db.query("select * from translation_history where chat_id = ? order by id desc", [chat_id])


def detect_lang(string):
    tests = {
        'ru': u'[а-я]',
        'en': u'[a-z]',
        'tr': u'[a-zğüşöçİĞÜŞÖÇ]'
    }
    tests_results = {k: 0 for k in tests.keys()}

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

def render_history(items, ltr=False):
    send = ""
    for item in items:
        send += '\n{id} `{query}` {src_lang}<->{target_lang} `{result}`'.format(**item)
    if len(send) > 4096:
        if ltr:
            sliced = items[1:]
        else:
            sliced = items[:-1]
        send, items = render_history(sliced, ltr)

    return send, items


def history_message(chat_id, before=None, after=None):
    full = get_history(chat_id)
    if before is not None:
        # Filter elements whose id is less than 'before'
        filtered_list = [elem for elem in full if elem['id'] < before]
    elif after is not None:
        # Filter elements whose id is greater than 'after'
        filtered_list = [elem for elem in full if elem['id'] > after]
    else:
        # If neither 'before' nor 'after' is provided, return the original list
        filtered_list = full

    if not len(filtered_list):
        return "History is empty.", False
    else:
        send, items = render_history(filtered_list, before is not None)
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(*[
            types.InlineKeyboardButton('< Prev',
                                       callback_data=json.dumps(
                                           {'function': 'history', 'what': 'prev',
                                            'id': items[0]["id"]})),
            types.InlineKeyboardButton('Next >',
                                       callback_data=json.dumps(
                                           {'function': 'history', 'what': 'next',
                                            'id': items[len(items) - 1]["id"]}))
        ])
        for one in items:
            markup.add(types.InlineKeyboardButton(str(one['id']),
                                       callback_data=json.dumps(
                                           {'function': 'history', 'what': 'show',
                                            'id': one['id']})))
        return send, markup


def helpmsg():
    return """Translator bot.
    Send me any message in private chat to translate message contents.
    `!translate text` in group chat to translate text.
    You can set target language with language code before text.
    For example `!translate ja test` to translate "test" to japaneese.
    Or `ja test` to translate "test" to japaneese in private chat.
    `!languages` to list supported language codes.
    
    `!set mode monopoly` to react to all messages in group chat or channel
    
    `!set pair lang1 lang2` to change default language pair.
     Second param is target language, first param is fallback target language. 
     For example, to translate all input to english and translate all input to czech if input text language is english use 
     `!set pair cs en`
     
     `!history` to view translation history
"""


