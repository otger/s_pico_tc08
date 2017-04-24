#!/usr/bin/python
# -*- coding: utf-8 -*-
from .logger import log
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
    arguments = [('channel', int), ('tc_type', str), ('units', str)]
    description = "Enables a channel of TC08"
    version = "0.1"

    def functionality(self):
        try:
            channel = int(self.get_arg('channel'))
            tc_type = self.get_arg('tc_type')
            units = self.get_arg('units')

            self.module.enable(channel, tc_type, units)
        except:
            log.exception('Exception when enabling channel. Request: {}'.format(self.request.get_as_dict()))
