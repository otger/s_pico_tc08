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
from .web.blueprints import get_blueprint
from .logger import log
"""
module
Created by otger on 23/03/17.
All rights reserved.
"""


class EntropyPicoTc08(Module):
    name = 'picotc08'
    description = "Picotech TC08 thermocouples controller entropy module"

    def __init__(self, name=None, channels=list(range(9))):
        Module.__init__(self, name=name)
        self.tc = ThermoCouples(channels=channels)
        self._timer = None
        self.interval = None
        self._l = threading.Lock()
        self.register_action(StartTempLoop)
        self.register_action(StopTempLoop)
        self.register_action(EnableChannel)
        self.register_blueprint(get_blueprint(self.name))
        for r in get_api_resources():
            self.register_api_resource(r)

    def exit(self):
        self.stop_timer()
        self.tc.close()

    def enable(self, channel, tc_type=None, units=None):
        self.tc.enable(channel, tc_type, units)

    def disable(self, channel):
        self.tc.disable(channel)

    def disconnect(self):
        self.stop_timer()
        self.tc.disconnect()

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

    def pub_status(self):
        values = self.tc.get_status()
        self.pub_event('status', values)


class ThermoCouples(object):

    MAX_CHANNEL_NUMBER = 8

    def __init__(self, channels=[], units=UNITS.TEMPERATURE.KELVIN,
                 tc_type=THERMOCOUPLES.T):
        self.channels = channels
        self._units = units
        self._tc_type = tc_type
        self._init_ctrlr()

    def _init_ctrlr(self):
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

    def _get_info(self):
        info = self.tc_ctrlr.getInfo()
        tmp = {k: info[k].decode('utf-8') for k in info}
        return tmp
    info = property(_get_info)

    def connect(self):
        if self.tc_ctrlr.isConnected():
            raise Exception("Controller is already connected")
        self.tc_ctrlr.connect()

    def disconnect(self):
        self.tc_ctrlr.close()

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

    def get_single_status(self, channel):
        tc = self.tc_factory.getModule(channel)
        return {'ts_utc': get_utc_ts(),
                'value': tc.getSingleValue(),
                'units': tc.getUnitsStr(),
                'tc_type': tc.getTypeStr(),
                'poll interval': tc.getProperties().pollinterval}

    def get_value(self, channel):
        tc = self.tc_factory.getModule(channel)
        return tc.getSingleValue()

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

    def get_status(self):
        values = {}
        for x in self.channels:
            values['channel_{0}'.format(x)] = self.get_single_status(x)
        return values

