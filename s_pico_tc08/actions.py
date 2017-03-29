#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
actions
Created by otger on 23/03/17.
All rights reserved.
"""

from entropyfw import Action


class StartTempLoop(Action):
    name = 'start_temp_loop'
    arguments = [('interval', float)]
    description = "Starts to publish temperatures of specified channels"
    version = "0.1"

    def functionality(self):
        interval = int(self.get_arg('interval'))
        self.module.start_timer(interval)


class StopTempLoop(Action):
    name = 'stop_temp_loop'
    arguments = []
    description = "Stops publishing temperatures"
    version = "0.1"

    def functionality(self):
        self.module.stop_timer()


class EnableChannel(Action):
    name = 'enable_channel'
    arguments = [('channel', int)]
    description = "Enables a channel of TC08"
    version = "0.1"

    def functionality(self):
        channel = int(self.get_arg('channel'))
        self.module.enable(channel)
