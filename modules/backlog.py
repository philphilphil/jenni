#!/usr/bin/env python
"""
backlog.py - jenni backlog utilities

Usage:
jenni.backlog(filter_channel, max_lines)
"""

import os, re
import threading
from modules import unicode as uc


# Backlog utils
def update_backlog(self, input):
    """Write every received line to a backlog file"""
    channel = uc.encode(uc.decode(input.sender))
    nick = (input.nick).encode("utf-8")
    line = input.group()
    if type(line) != type(str()):
        line = uc.encode(line)

    # Rules for lines that should be excluded
    if not channel.startswith("#"):
        return
    elif line.startswith("."):
        return
    elif line.startswith("s/"):
        return

    self.backlog_lock.acquire()
    try:
        backlog_file = open(self.backlog_filename, "a")
        backlog_file.write("{},{},{}\n".format(channel, nick, line))
        backlog_file.close()
        #TODO: Check backlog size and clear oldest entries if needed
    finally:
        self.backlog_lock.release()
update_backlog.rule = r".*"
update_backlog.priority = "medium"


def read_backlog(self, filter_channel=None, max_lines=100):
    """Read backlog file and return all entries from a specific channel"""
    channel_log = list()

    self.backlog_lock.acquire()
    try:
        backlog_file = open(self.backlog_filename, "r")
        backlog_lines = backlog_file.readlines()

        for line in backlog_lines:
            elements = line.split(",", 2)
            if len(elements) < 3: continue
            (channel, nick, log) = elements

            if filter_channel and channel != filter_channel:
                continue
            channel_log.append(log)

        backlog_file.close()
    finally:
        self.backlog_lock.release()
    return channel_log[-max_lines:]


def setup(self):
    fn = self.nick + "-" + self.config.host + ".backlog.db"
    self.backlog_filename = os.path.join(os.path.expanduser("~/.jenni"), fn)
    if not os.path.exists(self.backlog_filename):
        try: f = open(self.backlog_filename, "w")
        except OSError: pass
        else:
            f.write("")
            f.close()
    self.backlog_lock = threading.Lock()
    self.backlog = read_backlog
