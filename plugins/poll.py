#encoding: UTF-8

__plugin_name__ = "Polls"

import csv
import helpers.bot
import helpers.db
from helpers.sanitize import sanitize_md
from io import StringIO
import json
from telebot import types
import time
db = helpers.db.instance()

def register(listen=True, ** kwargs):
    db.query("""
CREATE TABLE IF NOT EXISTS `polls` (
    `id`	INTEGER PRIMARY KEY AUTOINCREMENT,
    `chat_id`	INTEGER,
    `message_id`	INTEGER,
    `text` TEXT,
    `answers`	TEXT,
    `date_started`	INTEGER DEFAULT CURRENT_TIMESTAMP,
    `ttl` INTEGER,
    `is_multi` INTEGER DEFAULT 0
);
""")
    db.query("""
CREATE TABLE IF NOT EXISTS `poll_votes` (
    `id`	INTEGER PRIMARY KEY AUTOINCREMENT,
    `poll_id`	INTEGER,
    `user_id`	INTEGER,
    `username`	TEXT,
    `answer_id`	INTEGER
);
""")
    if listen:
        bot = helpers.bot.instance()
        @bot.channel_post_handler(regexp="^!vote |^!poll ")
        @bot.message_handler(regexp="^!vote |^!poll ")
        @bot.message_handler(commands=['vote', 'poll'])
        @bot.channel_post_handler(commands=['vote', 'poll'])
        def start_vote(msg):
            is_multipoll = False
            _ = msg.text.split(' ')
            _.pop(0)
            if len(_):
                if _[0] == "end":
                    #stop_vote
                    pass
                else:
                    txt = ' '.join(_)
                    if '"' in txt:
                        _test = StringIO(txt)
                        """Documentation:
                        `Note The reader is hard-coded to recognise either '\r' or '\n' as end-of-line, and ignores lineterminator. This behavior may change in the future.`
                        Well, shit.
                        """
                        _params = csv.reader(_test, delimiter="\n", quotechar='"', lineterminator="�")
                        params = []
                        for pew in _params:
                            params.append(list(filter(None, pew))[0])
                    else:
                        params = txt.split("\n")
                    voting_text = params.pop(0)
                    try_ttl = params.pop(-1)
                    try:
                        ttl = int(try_ttl)
                    except:
                        params.append(try_ttl)
                        ttl = 5 #minutes)
                    if not create_poll(msg.chat.id, voting_text, params, ttl, is_multipoll):
                        bot.send_message(msg.chat.id, "Cant start vote: not enough parameters.")

        @bot.callback_query_handler(func=lambda call: True)
        def callback_query(call):
            try:
                bot.answer_callback_query(call.id, "")
            except Exception as e:
                print(e)

            data = call.data
            poll_id = None
            answer_id = None
            if data:
                try:
                    data = json.loads(data)
                    poll_id = data['poll_id']
                    answer_id = data['answer_id']
                except:
                    print("This is not poll:", call.json)
            if poll_id and answer_id is not None:
                poll = get_poll(poll_id)
                if not poll:
                    print("No such poll:", poll_id)
                    return
                write_vote(poll_id, answer_id, call.from_user.id, call.from_user.username, poll['is_multi'])
                _p = update_poll(poll_id)
                #return -256


def create_poll(chat_id, poll_text, answers, ttl, is_multipoll=False):
    if not len(answers):
        return
    bot = helpers.bot.instance()
    poll_id = db.query("insert into polls(chat_id, text, answers, ttl, is_multi) VALUES (:chat_id, :text, :answers, :ttl, :is_multi)", {'chat_id':chat_id, 'text':poll_text, 'answers':json.dumps(answers), 'ttl':ttl * 60, 'is_multi':is_multipoll}, get_id=True)
    sent = bot.send_message(chat_id, compose_body(poll_text, answers), reply_markup=generate_markup(poll_id, answers), parse_mode="Markdown")
    db.query("update polls set message_id = ? where id = ?", [sent.message_id, poll_id])
    return poll_id

def generate_markup(poll_id, lines, width=1):
    markup = types.InlineKeyboardMarkup(row_width=width)
    res = []
    for i, param in enumerate(lines):
        res.append(types.InlineKeyboardButton(param, callback_data=json.dumps({'poll_id':poll_id, 'answer_id':i})))
    markup.add(*res)
    return markup

def update_poll(poll_id):
    poll = get_poll(poll_id, full=True)
    if poll:
        new_body = compose_body(poll['text'], poll['answers'])
        if round(time.time()) > poll['date_started_unix'] + poll['ttl']:
            markup = None
        else:
            markup = generate_markup(poll_id, poll['_answers'])
        try:
            bot = helpers.bot.instance()
            bot.edit_message_text(chat_id=poll['chat_id'], message_id=poll['message_id'], text=new_body, reply_markup=markup, parse_mode="Markdown")
        except Exception as e:
            print(e)
        #return {"chat_id":poll['chat_id'], "message_id":poll['message_id'], "text":new_body, "reply_markup":m, "parse_mode":"Markdown"}
    else:
        return None


def compose_body(vote_text, vote_params):
    return vote_text + "\n" + "\n".join(fancy_lines(vote_params));

def fancy_lines(lines):
    fancy_lines = []
    try:
        total_votes = sum(v['votes'] for v in lines)
    except:
        total_votes = 0
    progressbar_len = 25
    for line in lines:
        if "votes" in line:
            _line = line['text']
        else:
            _line = line

        percent = line['votes'] * 100 / total_votes if total_votes else 0
        numchars = round(percent * progressbar_len / 100)
        progressbar = ''.join(["=" for n in range(0, numchars)]).ljust(progressbar_len, '-')
        fancy_lines.append("\n{line}\n\[`{progressbar}`] {percent}%".format(line=sanitize_md(_line), percent=int(percent), progressbar=progressbar))

    return fancy_lines



def get_poll(poll_id, full=False):
    poll = db.query("select *, cast(strftime('%s', date_started) as integer) as date_started_unix from polls where id = ?", [poll_id])
    if len(poll):
        poll = dict(poll[0])
        if not full:
            return poll
        poll['_answers'] = json.loads(poll['answers'])
        poll['answers'] = [{"text":a, "votes":0, "voters":[]} for a in json.loads(poll['answers'])]
    else:
        return
    votes = db.query("select * from poll_votes where poll_id = ?", [poll_id])
    for v in votes:
        v = dict(v)
        poll['answers'][v['answer_id']]['votes'] += 1
        poll['answers'][v['answer_id']]['voters'].append(v['username'])
    return poll

def write_vote(poll_id, answer_id, user_id, username, is_multipoll=False):
    sql = "select id from poll_votes where poll_id = ? and user_id = ?"
    data = [poll_id, user_id]
    if is_multipoll:
        sql += " and answer_id = ?"
        data.append(answer_id)
    v = db.query(sql, data)
    updated = False
    if len(v):
        for item in v:
            item = dict(item)
            db.query("update poll_votes set answer_id = ? where id = ?", [answer_id, item['id']])
            updated = True
    if not updated:
        db.query("insert into poll_votes(poll_id, answer_id, user_id, username) values (?,?,?,?)", [poll_id, answer_id, user_id, username])


def helpmsg():
    return """Poll plugin. Use the following syntax:```
  !poll "Here goes poll text. It can be as long as you
    like but should not contain newlines.
    If poll text or any answer(s) should contain
    newlines - quote it"
    Here goes answer 1
    "Here goes answer 2
    And it is multilined"
    Here goes answer ...
    Here goes answer N
    10```
  Last line can contain poll lifetime in _minutes_. If it's not -- poll will be active for 5 minutes.
"""


