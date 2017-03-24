#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
actions
Created by otger on 23/03/17.
All rights reserved.
"""

from entropyfw import Action


class StartTimer(Action):
    name = 'starttimer'
    arguments = [('interval', int)]
    description = "Starts to publish temperatures of specified channels"
    version = "0.1"

    def functionality(self):
        interval = int(self.get_arg('interval'))
        self.module.start_timer(interval)


class StopTimer(Action):
    name = 'stoptimer'
    arguments = []
    description = "Stops publishing temperatures"
    version = "0.1"

    def functionality(self):
        self.module.stop_timer()


class EnableChannel(Action):
    name = 'enablechannel'
    arguments = [('channel', int)]
    description = "Enables a channel of TC08"
    version = "0.1"

    def functionality(self):
        channel = int(self.get_arg('channel'))
        self.module.enable(channel)
