# -*- coding: utf-8 -*-
#
# This file is part of Linux Show Player
#
# Copyright 2012-2016 Francesco Ceruti <ceppofrancy@gmail.com>
#
# Linux Show Player is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Linux Show Player is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Linux Show Player.  If not, see <http://www.gnu.org/licenses/>.

import math
from collections import UserDict
from enum import Enum
import mido

from lisp.core.util import time_tuple
from lisp.modules.midi.midi_utils import str_msg_to_dict, dict_msg_to_str
from lisp.ui import elogging


class MscArgument(Enum):
    Q_NUMBER = 'Q_Number'
    Q_LIST = 'Q_List'
    Q_PATH = 'Q_Path'
    MACRO_NUM = 'Macro Number'
    CTRL_NUM = 'Generic Control Number'
    CTRL_VALUE = 'Generic Control Value'
    TIMECODE = 'Timecode'
    TIME_TYPE = 'Time Type'

    def __str__(self):
        return self.value


class MscCommandFormat(Enum):
    LIGHTING_GENERAL = 'Lighting (General Category)'
    MOVING_LIGHTS = 'Moving Lights'
    COLOR_CHANGERS = 'Colour Changers'
    STROBES = 'Strobes'
    LASERS = 'Lasers'
    CHASERS = 'Chasers'
    SOUND_GENERAL = 'Sound (General Category)'
    MUSIC = 'Music'
    CD_PLAYERS = 'CD Players'
    EPROM_PLAYBACK = 'EPROM Playback'
    AUDIO_TAPE_MACHINES = 'Audio Tape Machines'
    INTERCOMS = 'Intercoms'
    AMPLIFIERS = 'Amplifiers'
    AUDIO_EFFECT_DEVICES = 'Audio Effects Devices'
    EQUALISERS = 'Equalisers'
    # 'Machinery (General Category)'
    # 'Rigging'
    # 'Flys'
    # 'Lifts'
    # 'Turntables'
    # 'Trusses'
    # 'Robots'
    # 'Animation'
    # 'Floats'
    # 'Breakaways'
    # 'Barges'
    VIDEO_GENERAL = 'Video (General Category)'
    VIDEO_TAPE_MACHINES = 'Video Tape Machines'
    VIDEO_CASSETTE_MACHINE = 'Video Cassette Machines'
    VIDEO_DISC_PLAYERS = 'Video Disc Players'
    VIDEO_SWITCHERS = 'Video Switchers'
    VIDEO_EFFECTS = 'Video Effects'
    VIDEO_CHARACTER_GENERATORS = 'Video Character Generators'
    VIDEO_STILL_SCORES = 'Video Still Stores'
    VIDEO_MONITORS = 'Video Monitors'
    PROJECTION_GENERAL = 'Projection (General Category)'
    FILM_PROJECTORS = 'Film Projectors'
    SLIDE_PROJECTORS = 'Slide Projectors'
    VIDEO_PROJECTORS = 'Video Projectors'
    DISSOLVERS = 'Dissolvers'
    SHUTTER_CONTROL = 'Shutter Controls'
    # 'Process Control (General Category)'
    # 'Hydraulic Oil'
    # 'H20'
    # 'CO2'
    # 'Compressed Air'
    # 'Natural Gas'
    # 'Fog'
    # 'Smoke'
    # 'Cracked Haze'
    # 'Pyro  (General Category)'
    # 'Fireworks'
    # 'Explosions'
    # 'Flame'
    # 'Smoke pots'
    ALL_TYPES = 'All-types'

    def __str__(self):
        return self.value


class MscCommand(Enum):
    GO = 'Go'
    STOP = 'Stop'
    RESUME = 'Resume'
    TIMED_GO = 'Timed Go'
    LOAD = 'Load'
    SET = 'Set'
    FIRE = 'Fire'
    ALL_OFF = 'All Off'
    RESTORE = 'Restore'
    RESET = 'Reset'
    GO_OFF = 'Go Off'
    GO_JAM_CLOCK = 'Go/Jam Clock'
    STANDBY_PLUS = 'Standby +'
    STANDBY_MINUS = 'Standby -'
    SEQUENCE_PLUS = 'Sequence +'
    SEQUENCE_MINUS = 'Sequence -'
    START_CLOCK = 'Start Clock'
    STOP_CLOCK = 'Stop Clock'
    ZERO_CLOCK = 'Zero Clock'
    SET_CLOCK = 'Set Clock'
    MTC_CHASE_ON = 'MTC Chase On'
    MTC_CHASE_OFF = 'MTC Chase Off'
    OPEN_CUE_LIST = 'Open Cuelist'
    CLOSE_CUE_LIST = 'Close Cuelist'
    OPEN_CUE_PATH = 'Open Cue Path'
    CLOSE_CUE_PATH = 'Close Cue Path'

    def __str__(self):
        return self.value


class MscTimeType(Enum):
    FILM = 'Film 24 frame'
    EBU = 'EBU 25 frame'
    SMPTE = 'SMPTE 30 frame'

    def __str__(self):
        return self.value


class _MscLookupTable:
    CMD_FMT = {
        MscCommandFormat.LIGHTING_GENERAL: 0x1,
        MscCommandFormat.MOVING_LIGHTS: 0x2,
        MscCommandFormat.COLOR_CHANGERS: 0x3,
        MscCommandFormat.STROBES: 0x4,
        MscCommandFormat.LASERS: 0x5,
        MscCommandFormat.CHASERS: 0x6,
        MscCommandFormat.SOUND_GENERAL: 0x10,
        MscCommandFormat.MUSIC: 0x11,
        MscCommandFormat.CD_PLAYERS: 0x12,
        MscCommandFormat.EPROM_PLAYBACK: 0x13,
        MscCommandFormat.AUDIO_TAPE_MACHINES: 0x14,
        MscCommandFormat.INTERCOMS: 0x15,
        MscCommandFormat.AMPLIFIERS: 0x16,
        MscCommandFormat.AUDIO_EFFECT_DEVICES: 0x17,
        MscCommandFormat.EQUALISERS: 0x18,
        MscCommandFormat.VIDEO_GENERAL: 0x30,
        MscCommandFormat.VIDEO_TAPE_MACHINES: 0x31,
        MscCommandFormat.VIDEO_CASSETTE_MACHINE: 0x32,
        MscCommandFormat.VIDEO_DISC_PLAYERS: 0x33,
        MscCommandFormat.VIDEO_SWITCHERS: 0x34,
        MscCommandFormat.VIDEO_EFFECTS: 0x35,
        MscCommandFormat.VIDEO_CHARACTER_GENERATORS: 0x36,
        MscCommandFormat.VIDEO_STILL_SCORES: 0x37,
        MscCommandFormat.VIDEO_MONITORS: 0x38,
        MscCommandFormat.PROJECTION_GENERAL: 0x40,
        MscCommandFormat.FILM_PROJECTORS: 0x41,
        MscCommandFormat.SLIDE_PROJECTORS: 0x42,
        MscCommandFormat.VIDEO_PROJECTORS: 0x43,
        MscCommandFormat.DISSOLVERS: 0x44,
        MscCommandFormat.SHUTTER_CONTROL: 0x45,
        MscCommandFormat.ALL_TYPES: 0x7F
    }

    REV_CMD_FMT = {value: key for key, value in CMD_FMT.items()}

    CMD = {
        MscCommand.GO: 0x1,
        MscCommand.STOP: 0x2,
        MscCommand.RESUME: 0x03,
        MscCommand.TIMED_GO: 0x04,
        MscCommand.LOAD: 0x05,
        MscCommand.SET: 0x06,
        MscCommand.FIRE: 0x07,
        MscCommand.ALL_OFF: 0x08,
        MscCommand.RESTORE: 0x09,
        MscCommand.RESET: 0x0A,
        MscCommand.GO_OFF: 0x0B,
        MscCommand.GO_JAM_CLOCK: 0x10,
        MscCommand.STANDBY_PLUS: 0x11,
        MscCommand.STANDBY_MINUS: 0x12,
        MscCommand.SEQUENCE_PLUS: 0x13,
        MscCommand.SEQUENCE_MINUS: 0x14,
        MscCommand.START_CLOCK: 0x15,
        MscCommand.STOP_CLOCK: 0x16,
        MscCommand.ZERO_CLOCK: 0x17,
        MscCommand.SET_CLOCK: 0x18,
        MscCommand.MTC_CHASE_ON: 0x19,
        MscCommand.MTC_CHASE_OFF: 0x1A,
        MscCommand.OPEN_CUE_LIST: 0x1B,
        MscCommand.CLOSE_CUE_LIST: 0x1C,
        MscCommand.OPEN_CUE_PATH: 0x1D,
        MscCommand.CLOSE_CUE_PATH: 0x1E
    }

    REV_CMD = {value: key for key, value in CMD.items()}

    CMD_ARGS_TYPES = {
        MscArgument.Q_NUMBER: {'type': float, 'min': 0, 'default': 0},
        MscArgument.Q_PATH: {'type': float, 'min': 0, 'default': 0},
        MscArgument.Q_LIST: {'type': float, 'min': 0, 'default': 0},
        MscArgument.MACRO_NUM: {'type': int, 'min': 0, 'max': 127, 'default': 0},
        MscArgument.CTRL_NUM: {'type': int, 'min': 0, 'max': 1023, 'default': 0},
        MscArgument.CTRL_VALUE: {'type': int, 'min': 0, 'max': 1023, 'default': 0},
        MscArgument.TIMECODE: {'type': int, 'min': 0, 'default': 0},
        MscArgument.TIME_TYPE: {'type': MscTimeType, 'default': MscTimeType.SMPTE}
    }

    # dict holds MscArguments for certain MscCommands: { MsgArgument: [ required by: MscCommand | MscArgument | None ] }
    CMD_ARGS = {
        MscCommand.GO: {MscArgument.Q_NUMBER: None,
                        MscArgument.Q_LIST: MscArgument.Q_PATH,
                        MscArgument.Q_PATH: None},

        MscCommand.STOP: {MscArgument.Q_NUMBER: None,
                          MscArgument.Q_LIST: MscArgument.Q_PATH,
                          MscArgument.Q_PATH: None},

        MscCommand.RESUME: {MscArgument.Q_NUMBER: None,
                            MscArgument.Q_LIST: MscArgument.Q_PATH,
                            MscArgument.Q_PATH: None},

        MscCommand.TIMED_GO: {MscArgument.TIMECODE: MscCommand.TIMED_GO,
                              MscArgument.TIME_TYPE: MscCommand.TIMED_GO,
                              MscArgument.Q_NUMBER: None,
                              MscArgument.Q_LIST: MscArgument.Q_PATH,
                              MscArgument.Q_PATH: None},

        MscCommand.LOAD: {MscArgument.Q_NUMBER: None,
                          MscArgument.Q_LIST: MscArgument.Q_PATH,
                          MscArgument.Q_PATH: None},

        MscCommand.SET: {MscArgument.CTRL_NUM: MscCommand.SET,
                         MscArgument.CTRL_VALUE: MscCommand.SET,
                         MscArgument.TIMECODE: None,
                         MscArgument.TIME_TYPE: MscArgument.TIMECODE},

        MscCommand.FIRE: {MscArgument.MACRO_NUM: MscCommand.FIRE},

        MscCommand.ALL_OFF: {},

        MscCommand.RESTORE: {},

        MscCommand.RESET: {},

        MscCommand.GO_OFF: {MscArgument.Q_NUMBER: None,
                            MscArgument.Q_LIST: MscArgument.Q_PATH,
                            MscArgument.Q_PATH: None},

        MscCommand.GO_JAM_CLOCK: {MscArgument.Q_NUMBER: None,
                                  MscArgument.Q_LIST: MscArgument.Q_PATH,
                                  MscArgument.Q_PATH: None},

        MscCommand.STANDBY_PLUS: {MscArgument.Q_LIST: None},

        MscCommand.STANDBY_MINUS: {MscArgument.Q_LIST: None},

        MscCommand.SEQUENCE_PLUS: {MscArgument.Q_LIST: None},

        MscCommand.SEQUENCE_MINUS: {MscArgument.Q_LIST: None},

        MscCommand.START_CLOCK: {MscArgument.Q_LIST: None},

        MscCommand.STOP_CLOCK: {MscArgument.Q_LIST: None},

        MscCommand.ZERO_CLOCK: {MscArgument.Q_LIST: None},

        MscCommand.SET_CLOCK: {MscArgument.TIMECODE: MscCommand.SET_CLOCK,
                               MscArgument.TIME_TYPE: MscCommand.SET_CLOCK,
                               MscArgument.Q_LIST: None},

        MscCommand.MTC_CHASE_ON: {MscArgument.Q_LIST: None},

        MscCommand.MTC_CHASE_OFF: {MscArgument.Q_LIST: None},

        MscCommand.OPEN_CUE_LIST: {MscArgument.Q_LIST: MscCommand.OPEN_CUE_LIST},

        MscCommand.CLOSE_CUE_LIST: {MscArgument.Q_LIST: MscCommand.CLOSE_CUE_LIST},

        MscCommand.OPEN_CUE_PATH: {MscArgument.Q_LIST: MscCommand.CLOSE_CUE_LIST},

        MscCommand.CLOSE_CUE_PATH: {MscArgument.Q_LIST: MscCommand.CLOSE_CUE_PATH}
    }

    TIME_TYPE = {
        MscTimeType.FILM: 0x0,
        MscTimeType.EBU: 0x1,
        MscTimeType.SMPTE: 0x3
    }

    REV_TIME_TYPE = {value: key for key, value in TIME_TYPE.items()}

    TIME_TYPE_FRAME = {
        MscTimeType.FILM: 1000 / 24,
        MscTimeType.EBU: 1000 / 25,
        MscTimeType.SMPTE: 1000 / 30
    }

    @staticmethod
    def pack_float(value):
        """
        pack float values for McArguments: Q_NUMBER, Q_LIST, Q_PATH
        digits from the float encoded as [0 - 9] -> 0x30 - 0x39
        0x2E used as sep for .
        12.6 -> 0x31 0x32 0x2E 0x36
        :param value:
        :type float:
        :return: list of int
        :rtype: list
        """
        l = []
        for i in "%g" % value:
            if i.isdigit():
                l.append(int(i) + 0x30)
            else:
                l.append(0x2E)
        return l

    @staticmethod
    def unpack_float(digit_list):
        """
        unpacks float values for McArguments: Q_NUMBER, Q_LIST, Q_PATH in a MSC Message
        :param digit_list: list of int
        :type digit_list: list
        :return: float
        :rtype: float
        """
        if 0x2e in digit_list:
            point = digit_list.index(0x2e)
            digit_list.pop(point)
        else:
            point = len(digit_list)
        index = 0
        val = 0
        for i in reversed(range(-(len(digit_list[point:])), point)):
            digit = ~0x30 & digit_list[index]
            val += 10 ** i * digit
            index += 1
        return val

    @staticmethod
    def pack_millis(msec, time_type):
        """
        returns timecode hex list for MscArgument.TIMECODE
        :param msec: milliseconds
        :type msec: int
        :param time_type: MscTimeType
        :type time_type: MscTimeType
        :return: list of int
        :rtype: list
        """
        tt = time_tuple(msec)
        hh = (_MscLookupTable.TIME_TYPE[time_type] << 5) + tt[0]
        mm = tt[1]  # we use non colour frame (7th bit stays 0)
        ss = tt[2]  # subframes, standard
        frame = _MscLookupTable.TIME_TYPE_FRAME[time_type]
        ff, fr = math.modf(tt[3] / frame)
        return [hh, mm, ss, int(fr), int(ff * 100)]

    @staticmethod
    def unpack_time_type(data):
        """
        unpacks and returns MscTimeType from a MSC Message chunk which holds TIMECODE
        as first elements (5 bytes)
        :param data: list of int
        :type data: list
        :return: MscTimeType
        :rtype: MscTimeType
        """
        if len(data) > 4:
            time_type_bits = (data[0] & int('1100000', 2)) >> 5
            time_type = _MscLookupTable.REV_TIME_TYPE[time_type_bits]
            return time_type
        else:
            return None

    @staticmethod
    def unpack_millis(data):
        """
        unpacks and returns TIME_CODE in milliseconds
        from a MSC Message chunk which holds timecode as first elements (5 bytes)
        :param data: list of int
        :type data: list
        :return: milliseconds
        :rtype: int
        """
        time_type = _MscLookupTable.unpack_time_type(data)

        frame_millis = _MscLookupTable.TIME_TYPE_FRAME[time_type]

        hour = (data[0] & int('11111', 2)) * 3600000
        minute = (data[1] & int('111111', 2)) * 60000
        sec = (data[2] & int('111111', 2)) * 1000

        fr = data[3] & int('11111', 2)

        # test on subframes (bit 6 : 0)
        sub_frame = data[3] & int('00100000', 2)
        if not sub_frame:
            ff = data[4] & int('1111111', 2)
            fr += ff / 100

        msec = int(fr * frame_millis)

        return hour + minute + sec + msec

    @staticmethod
    def pack_int16(value):
        """
        packs int into two int (bytes) for MscArgument.CTRL_NUM or MscArgument.CTRL_VALUE
        :param value: int16 between (0 - 1023)
        :type value: int
        :return: lsb, msb
        :rtype: int, int
        """
        if isinstance(value, int) and (0 <= value <= 1023):
            return value & 0x7F, value >> 7
        else:
            return None

    @staticmethod
    def unpack_int16(data):
        """
        unpacks data MscArgument.CTRL_NUM or MscArgument.CTRL_VALUE
        :param data: list of int
        :type data: list
        :return: int (between 0 - 1023)
        :rtype: int
        """
        if len(data) > 1:
            return data[0] + (data[1] << 7)
        else:
            return None


class MscObject(UserDict):
    def __init__(self):
        super().__init__(self)

        self._device_id = None
        self._command_format = None
        self._command = None

    def __str__(self):
        return ', '.join([
            'DeviceID = {0}'.format(self._device_id),
            'CommandFormat = {0}'.format(self._command_format),
            'Command = {0}'.format(self._command),
            *('{0} = {1}'.format(k, v) for k, v in self.items())
        ])

    @property
    def device_id(self):
        """

        :rtype: int
        """
        return self._device_id

    @device_id.setter
    def device_id(self, device_id):
        """

        :param device_id: Msc Device ID
        :type device_id: int
        """
        self._device_id = device_id

    @property
    def command_format(self):
        """

        :rtype: MscCommandFormat
        """
        return self._command_format

    @command_format.setter
    def command_format(self, command_format):
        """

        :param command_format: Msc Command Format
        :type command_format: MscCommandFormat
        """
        self._command_format = command_format

    @property
    def command(self):
        """

        :rtype: MscCommand
        """
        return self._command

    @command.setter
    def command(self, command):
        """

        :param command: Msc Command
        :type command: MscCommand
        """
        self._command = command
        self.data.clear()

    def required(self, key):
        """
        checks if the requested key is required for the message or optional
        :param key: MSC message argument
        :type key: MscArgument
        :return: True if required for message
        :rtype: bool
        """
        if not isinstance(key, MscArgument):
            raise TypeError("key is not type MscArgument")

        if key in _MscLookupTable.CMD_ARGS[self._command]:
            required = _MscLookupTable.CMD_ARGS[self._command].get(key, None)
            if required is self._command:
                return True
            elif isinstance(required, MscArgument) and required in self:
                return True
            else:
                return False

    def _get_required(self):
        for key, req in _MscLookupTable.CMD_ARGS[self._command].items():
            if self.required(key):
                yield key

    @staticmethod
    def message_is_msc(message):
        """
        minimum check, only sysex and min length, manufacturer id and Msc Sub ID
        use this method to check if parsing would make sense
        :param message: Midi Message
        :type message: mido.Message
        :return: returns True if message is a MSC message
        :rtype: bool
        """
        return isinstance(message, mido.Message) \
               and message.type == 'sysex' \
               and len(message.data) > 4 \
               and message.data[0] == 0x7F \
               and message.data[2] == 0x02


    @staticmethod
    def str_is_msc(message_str):
        """
        minimum check, only sysex and min length, manufacturer id and Msc Sub ID
        use this method to check if parsing would make sense
        :param message: Midi Message string
        :type message: str
        :return: returns True if message is a MSC message
        :rtype: bool
        """
        if not isinstance(message_str, str):
            return False
        try:
            message = str_msg_to_dict(message_str)
            return message.get('type', '') == 'sysex' \
                   and message.get('data', None) \
                   and len(message['data']) > 4 \
                   and message.data[0] == 0x7F \
                   and message.data[2] == 0x02
        except ValueError:
            return False

    @staticmethod
    def get_arguments(command):
        return _MscLookupTable.CMD_ARGS.get(command)


class MscMessage(MscObject):
    def __init__(self, device_id, command_format, command):
        """
        MscMessage: creates Midi MSC Message
        :param device_id: Device ID
        :type device_id: int
        :param command_format: MSC Command Format (LIGHTING_GENERAL, ...)
        :type command_format: MscCommandFormat
        :param command: MSC Command (GO, STOP, ...)
        :type command: MscCommand
        """
        super().__init__()
        if not isinstance(device_id, int):
            raise TypeError("device_id is not type int")

        if not isinstance(command_format, MscCommandFormat):
            raise TypeError("device_id is not type MscCommandFormat")

        if not isinstance(command, MscCommand):
            raise TypeError("device_id is not type MscCommand")

        self._device_id = device_id
        self._command_format = command_format
        self._command = command

    def __setitem__(self, key, value):
        if isinstance(key, MscArgument) and key in _MscLookupTable.CMD_ARGS[self._command]:
            type_descr = _MscLookupTable.CMD_ARGS_TYPES[key]
            if 'max' in type_descr:
                value = min(value, type_descr['max'])
            if 'min' in type_descr:
                value = max(type_descr['min'], value)
            self.data[key] = type_descr['type'](value)
        else:
            elogging.error(
                "MscMessage: could not add argument: '{0}' to Command: '{1}'".format(str(key), str(self._command)))

    @property
    def message_str(self):
        """
        returns a MSC mido sysex message string
        :rtype: str
        """
        data = self.__create_msg()
        if data:
            return dict_msg_to_str({'type': 'sysex', 'data': data})
        else:
            return ''

    @property
    def message(self):
        return mido.parse_string(self.message_str)

    def __create_msg(self):
        for key in self._get_required():
            if key in self:
                continue
            else:
                self[key] = _MscLookupTable.CMD_ARGS_TYPES[key]['default']
                elogging.debug("MscMessage: missing argument: {0}, adding default".format(key), dialog=False)

        data = [
            0x7F,
            self._device_id,
            0x02,
            _MscLookupTable.CMD_FMT[self._command_format],
            _MscLookupTable.CMD[self._command]
        ]

        for key in self:
            if key is MscArgument.Q_NUMBER:
                data.extend(_MscLookupTable.pack_float(self.get(key)))

            elif key is MscArgument.Q_LIST:
                if MscArgument.Q_NUMBER in _MscLookupTable.CMD_ARGS[self._command]:
                    data.append(0x0)
                data.extend(_MscLookupTable.pack_float(self.get(key)))

            elif key is MscArgument.Q_PATH:
                if MscArgument.Q_LIST in self:
                    data.append(0x0)
                    data.extend(_MscLookupTable.pack_float(self.get(key)))

            elif key is MscArgument.MACRO_NUM:
                data.append(self.get(key))

            elif key is MscArgument.CTRL_NUM or key is MscArgument.CTRL_VALUE:
                values = _MscLookupTable.pack_int16(self.get(key))
                data.extend(values)

            elif key is MscArgument.TIMECODE:
                time_type = self[MscArgument.TIME_TYPE]
                timecode = _MscLookupTable.pack_millis(self.get(key), time_type)
                data.extend(timecode)
        return data

    def to_hex_str(self):
        """
        Message in  hex strings: 7F Device_ID 02 <Command Format> <Command> <Data> <F7>
        :return: hex string of the MSC message
        :rtype: str
        """
        msg_list = [0xF0]
        data = self.__create_msg()
        if data:
            msg_list.extend(data)
            msg_list.append(0xF7)
            return ' '.join(['{0:02x}'.format(i).upper() for i in msg_list])
        else:
            return ''


class MscParser(MscObject):
    def __init__(self, message):
        """
        midi msc message parses the arguments
        :param message: midi msc sysex message
        :type message: mido.Message
        """
        super().__init__()

        if not MscParser.message_is_msc(message):
            raise ValueError('message is not an msc midi message')

        self.__message = message
        self.__valid = True
        self._device_id = message.data[1]

        try:
            self._command_format = _MscLookupTable.REV_CMD_FMT[message.data[3]]
            self._command = _MscLookupTable.REV_CMD[message.data[4]]
        except KeyError:
            self._command = None
            self._command_format = None
            self.__valid = False
            return

        data = list(message.data)[5:]

        for msc_arg in _MscLookupTable.CMD_ARGS[self._command]:
            if not len(data):
                return

            if msc_arg is MscArgument.Q_NUMBER:
                if 0x0 in data:
                    index = data.index(0x0)
                    if index == 0:
                        data.pop(0)
                        continue
                    value = _MscLookupTable.unpack_float(data[:index])
                    data = data[index + 1:]
                else:
                    value = _MscLookupTable.unpack_float(data)
                    data.clear()

                self.data[msc_arg] = value

            if msc_arg is msc_arg is MscArgument.Q_LIST \
                    or msc_arg is MscArgument.Q_PATH:

                if 0x0 in data:
                    index = data.index(0x0)
                    value = _MscLookupTable.unpack_float(data[:index])
                    data = data[index + 1:]
                else:
                    value = _MscLookupTable.unpack_float(data)
                    data.clear()

                self.data[msc_arg] = value

            elif msc_arg is MscArgument.MACRO_NUM:
                self.data[msc_arg] = data[0]
                data.pop(0)

            elif msc_arg is MscArgument.CTRL_NUM \
                    or msc_arg is MscArgument.CTRL_VALUE:

                value = _MscLookupTable.unpack_int16(data)
                self.data[msc_arg] = value
                data = data[2:]

            elif msc_arg is MscArgument.TIME_TYPE:
                pass

            elif msc_arg is MscArgument.TIMECODE or msc_arg is MscArgument.TIME_TYPE:
                self.data[MscArgument.TIME_TYPE] = _MscLookupTable.unpack_time_type(data)
                self.data[MscArgument.TIMECODE] = _MscLookupTable.unpack_millis(data)
                data = data[5:]

        for key in self._get_required():
            if key in self:
                continue
            else:
                elogging.error("MscMessage: not a valid msc message missing argument: {0}".format(key), dialog=False)
                self.__valid = False

    def __setitem__(self, key, value):
        raise RuntimeError("writing to Parser not possible")

    @property
    def valid(self):
        return self.__valid


class MscStringParser(MscParser):
    def __init__(self, message_str):
        """
        midi msc message string and parses the arguments
        :param message: midi msc sysex as string
        :type message: str
        """
        super().__init__(mido.parse_string(message_str))