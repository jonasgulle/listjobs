#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: set et ts=4 sw=4:
from irc import RateLimitedDispatcher, IRCBot
from datetime import datetime
from listjobs import scrape_jobs

class JobsDispatcher(RateLimitedDispatcher):
    def __init__(self, *args, **kwargs):
        super(JobsDispatcher, self).__init__(*args, **kwargs)

    def reply_to(self, message, nick):
        self.send(message, nick=nick)

    def log(self, log):
        print "%s | %s" % (datetime.now(), log)

    def listlatest(self, sender, message, channel, is_ping, reply):
        self.log("%s asked for latest jobs" % sender)
        for job in scrape_jobs(limit=10):
            self.reply_to(job, sender)

    def listjobs(self, sender, message, channel, is_ping, reply):
        self.log("%s asked for all jobs" % sender)
        for job in scrape_jobs():
            self.reply_to(job, sender)

    def listsearch(self, sender, message, channel, is_ping, reply):
        search = message.replace('!listsearch', '').strip().lower()
        self.log("%s searched for \"%s\"" % (sender, search))
        for job in scrape_jobs(search=search):
            self.reply_to(job, sender)
 
    def get_patterns(self):
        return (
            ('^!listsearch \S+', self.listsearch),
            ('^!listlatest', self.listlatest),
            ('^!listjobs', self.listjobs),
        )

import threading
import config

class StoppableThread(threading.Thread):
    def __init__(self, **kwargs):
        super(StoppableThread, self).__init__(**kwargs)
        self._stop = threading.Event()

    def stop(self):
        print "Stopping..."
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

def bot_thread(arg):
    bot = JobsDispatcher()
    bot = IRCBot(arg["host"], arg["port"], arg["nick"], arg["password"], arg["channels"], [bot])
    bot.run_forever()

threads = [StoppableThread(target=bot_thread, args=[s]).start() for s in config.servers]

try:
    print "%d bots currently running" % len(threads)
    print "Press Ctrl+C to abort"
except KeyboardInterrupt:
    print "Aborting..."
    map(lambda t: t.stop(), threads)

