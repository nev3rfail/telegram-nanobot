## Telegram Nanobot
**⚠️ This is WIP and not ready to production use or whatever. Use it at your own risk**

telegram-nanobot is a wrapper around pyTelegramBotAPI used to quickly create telegram bots with plugin support.
#### Features:
* Out of the box database access
* Timers (WIP)
* Run multiple different bots from same directory just by changing JSON congifuration file

This was created when I grew tired of writing same code over and over again in different bots. It is not quite production ready, but it works for me.
#### Used in
* nev3rfail/nanobot-reddit_reposter
* nev3rfail/nanobot-transation_tools
* _a lot_ of small bots that don't event have it's own repositories. For examples see /plugins

#### Known issues:
* Code is _bad_
* Little to no documentation
* Timer usage is difficult
* Database is hardcoded in `__init__.py`
* Requires my [fork](https://github.com/nev3rfail/pyTelegramBotAPI) of pyTelegramBotAPI
  * Upstream is not against changes from this fork (https://github.com/eternnoir/pyTelegramBotAPI/pull/622), but it need to be done a little differently and I don't have enough time
