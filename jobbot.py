#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: set et ts=4 sw=4:
import os
import pickle
import random
import re
import sys
from irc import RateLimitedDispatcher, IRCBot
import listjobs

class JobsDispatcher(RateLimitedDispatcher):
    def __init__(self, *args, **kwargs):
        super(JobsDispatcher, self).__init__(*args, **kwargs)

    def reply_to(self, message, nick):
        self.send(message, nick=nick)

    def listlatest(self, sender, message, channel, is_ping, reply):
        jobs = listjobs.get_latest()
        if not len(jobs):
            self.reply_to("Sorry, there are no jobs available right now", sender)
            return
        for job in jobs:
            self.reply_to(job, sender)

    def listjobs(self, sender, message, channel, is_ping, reply):
        jobs = listjobs.get_all()
        if not len(jobs):
            self.reply_to("Sorry, there are no jobs available right now", sender)
            return
        for job in jobs:
            self.reply_to(job, sender)

    def listsearch(self, sender, message, channel, is_ping, reply):
        search = message.replace('!listsearch', '').strip().lower()
        jobs = listjobs.get_by_term(search)
        if not len(jobs):
            self.reply_to("Sorry, no matches", sender)
            return
        for job in jobs:
            self.reply_to(job, sender)
 
    def get_patterns(self):
        return (
            ('^!listsearch \S+', self.listsearch),
            ('^!listlatest', self.listlatest),
            ('^!listjobs', self.listjobs),
        )


host = "irc.gulle.se"
port = 6667
nick = "spotifyjobs"
password = ""
channels = ["#test"]

bot = JobsDispatcher()
bot = IRCBot(host, port, nick, password, channels, [bot])
bot.run_forever()

