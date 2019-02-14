# -*- coding: utf-8 -*-
# encoding=utf8

try:
    # Python 2.6-2.7
    from HTMLParser import HTMLParser
except ImportError:
    # Python 3
    from html.parser import HTMLParser

html_parser = HTMLParser()

def sanitize_html(string):
    sanitized = re.sub("<!--(.+?)-->", "", html_parser.unescape(string))
    sanitized = replace_multiple({"<strong>":"<b>", "</strong>":"</b>", "<p>":"", "</p>":"\n", "<br>":"\n", "<br/>":"\n", "<h2>":"<b>", "</h2>":"</b>"}, sanitized)
    sanitized = re.sub("(?!<b|<\/b|<i|<\/i|<a|<\/a>|<code|<\/code>|<pre|<\/pre)<(.+?)?>", "", sanitized)
    sanitized = sanitized.replace("\n\n\n\n", "\n")
    sanitized = sanitized.replace("\n\n\n", "\n")
    sanitized = sanitized.replace("\n\n", "\n")
    return sanitized

def sanitize_md(txt):
    to_sanitize = ["_", "*", "`"]
    for char in to_sanitize:
        if txt.count(char) % 2:
            pos = txt.rfind(char)
            if pos > -1:
                txt = txt[:pos] + txt[pos:].replace(char, "\\" + char)
    return txt