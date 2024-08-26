#encoding: UTF-8

import helpers.bot
import helpers.db
from io import BytesIO
import json
from plugins.google_cloud import json as google_json
from plugins.google_cloud import tts_languages as google_tts_languages
import re
__plugin_name__ = "Google TTS"

from plugins.google_translate import translate_client

from google.cloud import texttospeech_v1 as texttospeech

from telebot.apihelper import ApiException

try:
    tts_client = texttospeech.TextToSpeechClient.from_service_account_json(google_json)
except Exception as e:
    print(__plugin_name__, ' unloaded:', e)


commands = "^!tts$|^!tts "


def register(listen=True, config={}, ** kwargs):
    if listen:
        bot = helpers.bot.instance()
        @bot.channel_post_handler(regexp=commands, final=True)
        @bot.message_handler(regexp=commands, final=True)
        def ev_tts(msg):
            text = msg.text or msg.caption
            text = re.sub(commands, '', text)

            if len(text):
                if translate_client and tts_client:
                    lang = google_detect_lang(text)
                    if lang and lang in google_tts_languages:
                        audio = tts(text, lang)
                        if audio:
                            bot.send_voice(msg.chat.id, voice=BytesIO(audio), caption=text)#, reply_to_message_id=msg.message_id)
                        else:
                            bot.reply_to(msg, "Функционал недоступен или нет синтезатора для {lang}".format(lang=lang))
                    elif lang not in google_tts_languages:
                        bot.reply_to(msg, "Нет синтезатора для {lang}".format(lang=lang))
                    else:
                        bot.reply_to(msg, "Не удалось распознать язык.")
                else:
                    bot.reply_to(msg, "Функционал недоступен.")

        @bot.callback_query_handler(func=lambda call: True)
        def callback_query(call):
            try:
                bot.answer_callback_query(call.id, "")
            except Exception as e:
                print(e)

            data = call.data
            print(data)
            hist_id = None
            what = None
            if data:
                try:
                    data = json.loads(data)
                    function = data['function']
                    if(function == 'tts'):
                        hist_id = data['id']
                        what = data['what']

                except Exception as e:
                    print("This is not tts:", call.data, e)
            if hist_id is not None and what:
                from plugins.google_translate import get_history_item
                translated = get_history_item(call.message.chat.id, hist_id)
                if not translated:
                    print("No such item in translation history:", hist_id)
                    return
                if what == "src":
                    lang = translated['src_lang']
                    text = translated['query']
                elif what == "target":
                    lang = translated['target_lang']
                    text = translated['result']
                else:
                    print("Cannot get `what` from callback. full callback:", call.data)

                #print(call.message.chat.id)

                audio = tts(text, lang)
                if audio:
                    try:
                        bot.send_voice(call.message.chat.id, voice=BytesIO(audio), caption=text)#, reply_to_message_id=msg.message_id)
                    except ApiException as e:
                        bot.reply_to(call.message, e.result)
                else:
                    bot.reply_to(call.message, "Функционал недоступен или нет синтезатора для {lang}".format(lang=lang))
                #write_vote(poll_id, answer_id, call.from_user.id, call.from_user.username, poll['is_multi'])

                #_p = update_poll(poll_id)
                #return -256


        @bot.channel_post_handler(regexp='^!tts_languages')
        @bot.message_handler(regexp='^!tts_languages')
        def langs(msg):
            bot.reply_to(msg, ', '.join(google_tts_languages))



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

def google_detect_lang(string):
    try:
        return translate_client.detect_language(string)['language']
    except Exception as e:
        print("Language detection error:", e)
        return False



def tts(text, lang):
    if lang == "zh-TW":
        lang = "ja-JP"
    if lang == "zh-CN":
        lang = "zh"
    no_tts = ["be"]
    if lang in no_tts:
        return False
    try:
        if tts_client:
            synthesis_input = texttospeech.types.SynthesisInput(text=text)
            voice = texttospeech.types.VoiceSelectionParams(language_code=lang, ssml_gender=texttospeech.types.SsmlVoiceGender.FEMALE)
            audio_config = texttospeech.types.AudioConfig(audio_encoding=texttospeech.AudioEncoding.OGG_OPUS)

            response = tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
            return response.audio_content
        else:
            return False
    except Exception as e:
        print("TTS exception:", e)
        return False



def helpmsg():
    return """TTS bot.
    `!tts text` in any chat to text-to-speech `text`.
    `!tts_languages` to list supported text-to-speech language codes.
"""


