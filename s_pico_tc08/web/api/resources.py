#!/usr/bin/python
# -*- coding: utf-8 -*-
from entropyfw.api.rest import ModuleResource, REST_STATUS
from flask import jsonify
from flask_restful import reqparse
from entropyfw.common import get_utc_ts
from PicoController.common.definitions import THERMOCOUPLES, UNITS
from .logger import log
from s_pico_tc08 import T_UNITS, TC_TYPES
"""
resources
Created by otger on 29/03/17.
All rights reserved.
"""


class StartTempLoop(ModuleResource):
    url = 'start_temp_loop'
    description = "Configures tc08 to read and publish enabled channels every 'interval' seconds"

    def __init__(self, module):
        super(StartTempLoop, self).__init__(module)
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('interval', type=float, required=True, location='json')

    def post(self):
        args = self.reqparse.parse_args()
        try:
            self.module.start_timer(args['interval'])
        except Exception as ex:
            log.exception('Exception when starting status publication loop')
            return self.jsonify_return(status=REST_STATUS.Error, result=str(ex), args=args)
        else:
            return self.jsonify_return(status=REST_STATUS.Done, result=None, args=args)


class StopTempLoop(ModuleResource):
    url = 'stop_temp_loop'
    description = "Stop get temperature values loop"

    def __init__(self, module):
        super(StopTempLoop, self).__init__(module)

    def post(self):
        try:
            self.module.stop_timer()
        except Exception as ex:
            log.exception('Exception when stopping status publication loop')
            return self.jsonify_return(status=REST_STATUS.Error, result=str(ex))
        else:
            return self.jsonify_return(status=REST_STATUS.Done, result=None)


class EnableChannel(ModuleResource):
    url = 'enable_channel'
    description = "Enables a channel of TC08 with configured thermocouple type and units"

    def __init__(self, module):
        super(EnableChannel, self).__init__(module)
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('channel', type=int, required=True, location='json')
        self.reqparse.add_argument('tc_type', type=str,
                                   choices=TC_TYPES,
                                   location='json')
        self.reqparse.add_argument('units', type=str,
                                   choices=T_UNITS,
                                   location='json')

    def post(self):
        args = self.reqparse.parse_args()

        tc_type = args.get('tc_type')
        if tc_type:
            tc_type = getattr(THERMOCOUPLES, tc_type.upper())

        units = args.get('units')
        if units:
            units = getattr(UNITS.TEMPERATURE, units.upper())
        try:
            self.module.enable(args['channel'], tc_type=tc_type, units=units)
        except Exception as ex:
            log.exception('Something went wrong when enabling channel with arguments: {0}'.format(args))
            return self.jsonify_return(status=REST_STATUS.Error, result=str(ex), args=args)
        else:
            return self.jsonify_return(status=REST_STATUS.Done, result=None, args=args)


class DisableChannel(ModuleResource):
    url = 'disable_channel'
    description = "Disables a channel of TC08"

    def __init__(self, module):
        super(DisableChannel, self).__init__(module)
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('channel', type=int, required=True, location='json')

    def post(self):
        args = self.reqparse.parse_args()

        try:
            self.module.disable(args['channel'])
        except Exception as ex:
            log.exception('Something went wrong when disabling channel with arguments: {0}'.format(args))
            return self.jsonify_return(status=REST_STATUS.Error, result=str(ex), args=args)
        else:
            return self.jsonify_return(status=REST_STATUS.Done, result=None, args=args)


class ReadChannels(ModuleResource):
    url = 'read_channels'
    description = "Reads all enabled channels and return its read values"

    def get(self):
        try:
            values = self.module.tc.get_status()
        except Exception as ex:
            log.exception('Something went wrong when reading status')
            return self.jsonify_return(status=REST_STATUS.Error, result=str(ex))
        else:
            return self.jsonify_return(status=REST_STATUS.Done, result=values)


def get_api_resources():
    return [StartTempLoop, StopTempLoop, EnableChannel, DisableChannel, ReadChannels]
