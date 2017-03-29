#!/usr/bin/python
# -*- coding: utf-8 -*-
import threading
from entropyfw import Module
from entropyfw.common import get_utc_ts
from PicoController import ControllerTC08
from PicoController.common.tools import ThermoCoupleModifier, UnitsModifier
from PicoController.common.definitions import THERMOCOUPLES, UNITS
from PicoController.common.definitions import MODULES_AVAILABLE

from .actions import StartTempLoop, EnableChannel, StopTempLoop
from .web.api.resources import get_api_resources

"""
module
Created by otger on 23/03/17.
All rights reserved.
"""


class EntropyPicoTc08(Module):
    name = 'picotc08'

    def __init__(self, name=None, channels=list(range(9))):
        Module.__init__(self, name=name)
        self.tc = ThermoCouples(channels=channels)
        self._timer = None
        self.interval = None
        self._l = threading.Lock()
        self.register_action(StartTempLoop)
        self.register_action(StopTempLoop)
        self.register_action(EnableChannel)
        for r in get_api_resources():
            self.register_api_resource(r)

    def exit(self):
        self.tc.close()

    def enable(self, channel, tc_type=None, units=None):
        self.tc.enable(channel, tc_type, units)

    def disable(self, channel):
        self.tc.disable(channel)

    def _timer_func(self):
        values = self.tc.get_channels_values()
        self.pub_event('temperatures', values)
        self._timer = threading.Timer(self.interval, self._timer_func)
        self._timer.start()

    def start_timer(self, interval):
        with self._l:
            self.interval = interval
            if self._timer is None:
                self._timer_func()

    def stop_timer(self):
        with self._l:
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None


class ThermoCouples(object):

    MAX_CHANNEL_NUMBER = 8

    def __init__(self, channels=list(range(9)), units=UNITS.TEMPERATURE.KELVIN,
                 tc_type=THERMOCOUPLES.T):
        self.channels = channels
        self._units = units
        self._tc_type = tc_type
        self.tc_ctrlr = ControllerTC08()
        self.tc_ctrlr.connect()
        self.tc_factory = self.tc_ctrlr.getModuleFactory(MODULES_AVAILABLE.ANALOG_INPUT)
        self._config_channels()

    def _config_channels(self):
        for channel in self.channels:
            self._config(channel)

    def _config(self, channel, tc_type=None, units=None):
        ch = self.tc_factory.getModule(channel)
        ch.addAnalogModifier(ThermoCoupleModifier(tc_type or self._tc_type))
        ch.addAnalogModifier(UnitsModifier(units or self._units))

    def enable(self, channel, tc_type=None, units=None):
        if channel > self.MAX_CHANNEL_NUMBER:
            raise Exception("Allowed channels are 0-{0}".format(self.MAX_CHANNEL_NUMBER))

        if channel not in self.channels:
            self.channels.append(channel)
            self.channels.sort()
        self._config(channel, tc_type, units)

    def disable(self, channel):
        if channel in self.channels:
            self.channels.pop(self.channels.index(channel))

    def get_value(self, channel):
        tc = self.tc_factory.getModule(channel)
        return {'ts_utc': get_utc_ts(),
                'value': tc.getSingleValue(),
                'units': tc.getUnitsStr(),
                'tc_type': tc.getTypeStr()}

    def close(self):
        self.tc_ctrlr.close()

    def get_poll_interval(self, channel):
        ch = self.tc_factory.getModule(channel)
        return ch.getProperties().pollinterval

    def get_channels_values(self):
        values = {}
        for x in self.channels:
            values['channel_{0}'.format(x)] = self.get_value(x)
        return values

