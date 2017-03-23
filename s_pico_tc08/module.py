#!/usr/bin/python
# -*- coding: utf-8 -*-

from entropyfw import Module
from PicoController import ControllerTC08
from PicoController.common.tools import ThermoCoupleModifier, UnitsModifier
from PicoController.common.definitions import THERMOCOUPLES, UNITS
from PicoController.common.definitions import MODULES_AVAILABLE


"""
module
Created by otger on 23/03/17.
All rights reserved.
"""


class EntropyPicoTc08(Module):
    name = 'picotc08'

    def __init__(self, dealer, name=None, channels=list(range(8))):
        Module.__init__(self, name=name, dealer=dealer)
        self.tc = ThermoCouples(channels=channels)

    def enable(self, channel):
        self.tc.enable(channel)


class ThermoCouples(object):
    def __init__(self, channels=list(range(8)), units=UNITS.TEMPERATURE.KELVIN,
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
        if channel not in self.channels:
            self.channels.append(channel)
            self.channels.sort()
        self.enable(channel, tc_type, units)

    def disable(self, channel):
        if channel in self.channels:
            self.channels.pop(self.channels.index(channel))

    def get_value(self,channel):
        tc = self.tc_factory.getModule(channel)
        return tc.getSingleValue()

    def close(self):
        self.tc_ctrlr.close()

    def get_poll_interval(self, channel):
        ch = self.tc_factory.getModule(channel)
        return ch.getProperties().pollinterval

    def get_channels_values(self):
        values = []
        for x in self.channels:
           values.append(self.get_value(x))
        return values

